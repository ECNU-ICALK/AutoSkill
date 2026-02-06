"""
Skill maintenance (Maintainer): merge SkillCandidates into the user's “skill set”.

Key goals:
- dedupe similar skills (vector search + similarity threshold)
- merge fields (heuristic merge or LLM-assisted merge)
- bump version
- always generate/update the Agent Skill artifact (SKILL.md) while preserving custom scripts/resources
"""

from __future__ import annotations

import json
import re
import threading
import uuid
from dataclasses import replace
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple

from ..config import AutoSkillConfig
from .extraction import SkillCandidate, SkillExtractor
from .formats.agent_skill import build_agent_skill_files
from ..llm.factory import build_llm
from ..models import Skill, SkillExample
from .stores.base import SkillStore
from ..utils.json import json_from_llm_text
from ..utils.time import now_iso

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def _json_from_llm_decision(text: str) -> Dict:
    """
    Parses a small JSON decision object from an LLM output.

    Unlike `json_from_llm_text`, this parser prefers objects containing an `action` key.
    """

    cleaned = _FENCE_RE.sub("", (text or "").strip())
    if not cleaned:
        raise ValueError("empty LLM output")
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    candidates = [i for i, ch in enumerate(cleaned) if ch == "{"]
    best_obj = None
    best_score = -1
    for idx in reversed(candidates):
        try:
            obj, _end = decoder.raw_decode(cleaned, idx)
        except json.JSONDecodeError:
            continue
        score = 0
        if isinstance(obj, dict):
            if "action" in obj:
                score += 10
            if "target_skill_id" in obj or "target" in obj:
                score += 3
            if "reason" in obj or "rationale" in obj:
                score += 1
        if score > best_score:
            best_score = score
            best_obj = obj
            if best_score >= 12:
                break
    if isinstance(best_obj, dict):
        return best_obj
    raise ValueError("failed to parse decision JSON from LLM output")


def _is_library_skill(skill: Skill) -> bool:
    owner = str(getattr(skill, "user_id", "") or "").strip().lower()
    return owner.startswith("library:")


def _normalize_action(action: str) -> str:
    a = str(action or "").strip().lower()
    if a in {"delete", "drop", "ignore", "skip"}:
        return "discard"
    if a in {"discard", "reject"}:
        return "discard"
    if a in {"merge", "update", "upsert"}:
        return "merge"
    if a in {"add", "create", "new"}:
        return "add"
    return ""


def _hit_for_llm(hit) -> Dict:
    skill = getattr(hit, "skill", None)
    score = float(getattr(hit, "score", 0.0) or 0.0)
    if skill is None:
        return {"score": score}

    return {
        "id": str(skill.id),
        "owner": str(skill.user_id),
        "scope": ("library" if _is_library_skill(skill) else "user"),
        "score": score,
        "name": str(skill.name),
        "description": str(skill.description),
        "prompt": str(skill.instructions),
        "triggers": list(skill.triggers or []),
        "tags": list(skill.tags or []),
        "version": str(skill.version),
    }


def _ensure_skill_in_hits(hits: List, skill: Optional[Skill], score: float = 0.0) -> List:
    if skill is None:
        return list(hits or [])
    for h in hits or []:
        s = getattr(h, "skill", None)
        if s is not None and str(getattr(s, "id", "")) == str(skill.id):
            return list(hits or [])
    injected = SimpleNamespace(skill=skill, score=float(score or 0.0))
    return [injected] + list(hits or [])


class SkillMaintainer:
    def __init__(
        self, config: AutoSkillConfig, store: SkillStore, extractor: SkillExtractor
    ) -> None:
        self._config = config
        self._store = store
        self._extractor = extractor
        self._llm = (
            build_llm(config.llm)
            if (config.maintenance_strategy or "").lower() == "llm"
            else None
        )
        self._last_lock = threading.Lock()
        self._last_upserted_skill_id_by_user: Dict[str, str] = {}

    def _pop_previous_skill_id(self, metadata: Optional[Dict]) -> Tuple[Optional[str], Dict]:
        md = dict(metadata or {})
        prev = None
        for k in ("previous_skill_id", "prev_skill_id", "last_skill_id"):
            v = md.pop(k, None)
            if v is None:
                continue
            s = str(v).strip()
            if s:
                prev = s
                break
        return prev, md

    def _get_last_upserted_skill_id(self, *, user_id: str) -> Optional[str]:
        uid = str(user_id or "").strip()
        if not uid:
            return None
        with self._last_lock:
            sid = self._last_upserted_skill_id_by_user.get(uid)
        return str(sid).strip() if sid and str(sid).strip() else None

    def _record_last_upserted_skill_id(self, *, user_id: str, skill_id: str) -> None:
        uid = str(user_id or "").strip()
        sid = str(skill_id or "").strip()
        if not uid or not sid:
            return
        with self._last_lock:
            self._last_upserted_skill_id_by_user[uid] = sid

    def apply(
        self,
        candidates: List[SkillCandidate],
        *,
        user_id: str,
        metadata: Optional[Dict] = None,
    ) -> List[Skill]:
        out: List[Skill] = []
        for cand in candidates:
            skill = self._upsert_candidate(cand, user_id=user_id, metadata=metadata)
            if skill is not None:
                out.append(skill)
        return out

    def _upsert_candidate(
        self, cand: SkillCandidate, *, user_id: str, metadata: Optional[Dict]
    ) -> Optional[Skill]:
        previous_id, metadata_clean = self._pop_previous_skill_id(metadata)
        previous_id = previous_id or self._get_last_upserted_skill_id(user_id=user_id)

        previous_skill = None
        if previous_id:
            try:
                s = self._store.get(str(previous_id))
            except Exception:
                s = None
            if s is not None and not _is_library_skill(s) and str(getattr(s, "user_id", "")) == str(user_id):
                previous_skill = s

        prev_threshold = float(
            (self._config.extra or {}).get(
                "previous_skill_similarity_threshold", self._config.dedupe_similarity_threshold
            )
        )
        prev_hits: List = []
        prev_score = 0.0
        if previous_skill is not None and prev_threshold > 0:
            prev_hits = self._store.search(
                user_id=user_id,
                query=_candidate_to_query(cand),
                limit=1,
                filters={"scope": "user", "ids": [previous_skill.id]},
            )
            prev_score = float(prev_hits[0].score) if prev_hits else 0.0
            if prev_score >= prev_threshold and self._llm is None:
                merged = (
                    _merge_with_llm(self._llm, previous_skill, cand)
                    if self._llm is not None
                    else _merge(previous_skill, cand)
                )
                merged.updated_at = now_iso()
                merged.metadata = _merge_metadata(previous_skill.metadata, metadata_clean, cand)
                if self._config.store_sources and cand.source:
                    merged.source = cand.source
                merged.files = _merge_files(previous_skill.files, build_agent_skill_files(merged))
                self._store.upsert(merged, raw=_skill_to_raw(merged))
                self._record_last_upserted_skill_id(user_id=user_id, skill_id=merged.id)
                return merged

        # Search for similar skills using the candidate text to avoid duplicates.
        # Include both user skills and shared library skills as references.
        similar = self._store.search(
            user_id=user_id,
            query=_candidate_to_query(cand),
            limit=self._config.max_similar_skills_to_consider,
            filters={"scope": "all"},
        )
        similar_for_llm = (
            _ensure_skill_in_hits(similar, previous_skill, prev_score)
            if self._llm is not None
            else similar
        )

        best_any = similar[0] if similar else None
        best_user = next((h for h in similar if not _is_library_skill(h.skill)), None)
        best_library = next((h for h in similar if _is_library_skill(h.skill)), None)
        best_user_for_llm = (
            next((h for h in similar_for_llm if not _is_library_skill(h.skill)), None)
            if self._llm is not None
            else best_user
        )

        def _create_new() -> Skill:
            created = Skill(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=cand.name.strip(),
                description=cand.description.strip() or cand.name.strip(),
                instructions=cand.instructions.strip(),
                triggers=[t.strip() for t in cand.triggers if t and t.strip()],
                tags=[t.strip() for t in cand.tags if t and t.strip()],
                examples=list(cand.examples or []),
                version="0.1.0",
                metadata=_merge_metadata({}, metadata_clean, cand),
                source=cand.source if self._config.store_sources else None,
                created_at=now_iso(),
                updated_at=now_iso(),
            )
            created.files = build_agent_skill_files(created)
            self._store.upsert(created, raw=_skill_to_raw(created))
            self._record_last_upserted_skill_id(user_id=user_id, skill_id=created.id)
            return created

        if self._llm is not None:
            try:
                action, target_skill_id, _reason = _decide_candidate_action_with_llm(
                    self._llm,
                    cand,
                    similar_for_llm,
                    user_id=user_id,
                    dedupe_threshold=float(self._config.dedupe_similarity_threshold),
                )
            except Exception:
                action, target_skill_id = "", None

            if action == "discard":
                return None
            if action == "add":
                return _create_new()

            if action == "merge":
                target = None
                if target_skill_id:
                    target_id = str(target_skill_id).strip()
                    allowed_user_ids = {
                        str(h.skill.id)
                        for h in (similar_for_llm or [])
                        if getattr(h, "skill", None) is not None and not _is_library_skill(h.skill)
                    }
                    if target_id and target_id in allowed_user_ids:
                        target = self._store.get(target_id)
                        if target is not None and _is_library_skill(target):
                            target = None
                if target is None and best_user_for_llm is not None:
                    target = best_user_for_llm.skill
                if target is not None:
                    merged = _merge_with_llm(self._llm, target, cand)
                    merged.updated_at = now_iso()
                    merged.metadata = _merge_metadata(target.metadata, metadata_clean, cand)
                    if self._config.store_sources and cand.source:
                        merged.source = cand.source
                    merged.files = _merge_files(target.files, build_agent_skill_files(merged))
                    self._store.upsert(merged, raw=_skill_to_raw(merged))
                    self._record_last_upserted_skill_id(user_id=user_id, skill_id=merged.id)
                    return merged

                return _create_new()

        # Fallback / heuristic maintenance:
        # - merge into the best user-owned skill when clearly similar
        # - otherwise, if a shared library skill is clearly similar, discard the candidate to avoid duplication
        # - otherwise, add a new user skill
        if best_user and best_user.score >= self._config.dedupe_similarity_threshold:
            merged = _merge(best_user.skill, cand)
            merged.updated_at = now_iso()
            merged.metadata = _merge_metadata(best_user.skill.metadata, metadata_clean, cand)
            if self._config.store_sources and cand.source:
                merged.source = cand.source
            merged.files = _merge_files(best_user.skill.files, build_agent_skill_files(merged))
            self._store.upsert(merged, raw=_skill_to_raw(merged))
            self._record_last_upserted_skill_id(user_id=user_id, skill_id=merged.id)
            return merged

        if best_any and best_library and best_library.score >= self._config.dedupe_similarity_threshold:
            return None

        return _create_new()


def _decide_candidate_action_with_llm(
    llm,
    cand: SkillCandidate,
    similar_hits: List,
    *,
    user_id: str,
    dedupe_threshold: float,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Uses an LLM to decide whether to add/merge/discard a candidate skill.

    Returns:
    - action: add|merge|discard
    - target_skill_id: only for merge
    - reason: optional, best-effort string
    """

    system = (
        "You are AutoSkill's Skill Set Manager.\n"
        "Task: decide how to handle a newly extracted candidate skill given similar existing skills.\n"
        "Output ONLY strict JSON; no Markdown, no commentary, no extra text.\n"
        "\n"
        "Context:\n"
        "- Skills are modular capability packages (SKILL.md + optional resources) that onboard another assistant instance.\n"
        "- Maintain a high-signal, non-redundant skill set.\n"
        "- Favor progressive disclosure: store concise metadata + an executable prompt; avoid storing long reference dumps.\n"
        "\n"
        "You must choose one action:\n"
        "- add: store the candidate as a new user skill\n"
        "- merge: merge the candidate into ONE existing USER skill (pick target_skill_id)\n"
        "- discard: do not store the candidate\n"
        "\n"
        "Quality rules (be conservative):\n"
        "- Prefer discard if the candidate is generic/obvious, low-signal, or not clearly reusable.\n"
        "- Prefer discard if a shared library skill already covers the capability and the candidate adds no stable, user-specific value.\n"
        "- Prefer merge if the candidate is an incremental improvement to an existing user skill (same intent, clearer prompt, better checks, better metadata).\n"
        "- Prefer add if the candidate changes the core content type, channel, or audience (e.g., 'government report' vs 'public account article'), even if the structure is similar.\n"
        "- Prefer add only if the candidate is a distinct reusable capability not covered by existing skills.\n"
        "- Use similarity scores as hints, not absolute truth.\n"
        "\n"
        "Constraints:\n"
        "- If action is merge, target_skill_id MUST refer to a skill with scope == 'user' in the provided similar list.\n"
        "- Do not propose deleting any existing skills.\n"
        "\n"
        "Return schema:\n"
        "{\n"
        '  \"action\": \"add\"|\"merge\"|\"discard\",\n'
        '  \"target_skill_id\": string|null,\n'
        '  \"reason\": string\n'
        "}\n"
    )
    data = {
        "user_id": str(user_id),
        "dedupe_threshold": float(dedupe_threshold),
        "candidate": _candidate_to_raw(cand),
        "similar": [_hit_for_llm(h) for h in (similar_hits or [])][:8],
    }
    user = json.dumps(data, ensure_ascii=False)
    text = llm.complete(system=system, user=user, temperature=0.0)
    obj = _json_from_llm_decision(text)
    action = _normalize_action(obj.get("action"))
    target = str(obj.get("target_skill_id") or obj.get("target") or "").strip() or None
    reason = str(obj.get("reason") or obj.get("rationale") or "").strip() or None
    if action not in {"add", "merge", "discard"}:
        action = ""
    return action, target, reason


def _candidate_to_query(cand: SkillCandidate) -> str:
    return f"{cand.name}\n{cand.description}\n{cand.instructions}"


def _merge(existing: Skill, cand: SkillCandidate) -> Skill:
    def _instruction_quality_score(text: str) -> int:
        s = str(text or "").strip()
        if not s:
            return 0
        low = s.lower()
        score = 0
        if re.search(r"(?m)^\s*\d+[\.\)]\s+", s):
            score += 4
        if "output format" in low:
            score += 2
        if "validation" in low or "check" in low:
            score += 2
        if "assumption" in low:
            score += 1
        if "rollback" in low or "fallback" in low:
            score += 1
        if "bundled resources" in low:
            score += 1
        if "<" in s and ">" in s:
            score += 1
        score += min(len(s) // 500, 3)
        return int(score)

    existing_instr = str(existing.instructions or "").strip()
    cand_instr = str(cand.instructions or "").strip()
    instructions = existing_instr or cand_instr
    if existing_instr and cand_instr:
        s_old = _instruction_quality_score(existing_instr)
        s_new = _instruction_quality_score(cand_instr)
        if s_new > s_old + 1:
            instructions = cand_instr
        elif s_new == s_old and len(cand_instr) > len(existing_instr) * 1.1:
            instructions = cand_instr

    description = existing.description
    if len(cand.description.strip()) > len(existing.description.strip()) * 1.1:
        description = cand.description.strip()

    merged = replace(
        existing,
        name=_prefer_name(existing.name, cand.name),
        description=description,
        instructions=instructions,
        triggers=_dedupe(existing.triggers + list(cand.triggers or [])),
        tags=_dedupe(existing.tags + list(cand.tags or [])),
        examples=_merge_examples(existing.examples, cand.examples),
        version=_bump_patch(existing.version),
    )
    return merged


def _merge_with_llm(llm, existing: Skill, cand: SkillCandidate) -> Skill:
    try:
        system = (
            "You are AutoSkill's Skill Maintainer.\n"
            "Task: Update the `existing_skill` using new insights from `candidate_skill`.\n"
            "Output ONLY strict JSON (parsable by json.loads); no Markdown, no commentary.\n"
            "\n"
            "### CRITICAL STRATEGY: INCREMENTAL PATCHING\n"
            "Treat `existing_skill` as the **Master Copy** and `candidate_skill` as a **Patch/Update**.\n"
            "Your goal is to **INJECT** new rules into the Master Copy without rewriting the parts that work.\n"
            "\n"
            "1. **Anchor on Existing:** Start with the structure and content of `existing_skill`.\n"
            "2. **Identify Deltas:** Look for NEW constraints, NEW triggers, or NEW style requirements in `candidate_skill` that are missing from `existing_skill`.\n"
            "3. **Append (Don't Invent):** Add these new items to the existing lists. Do not rewrite valid existing rules.\n"
            "4. **No Phantom Workflows:** \n"
            "   - If `existing_skill` has no workflow AND `candidate_skill` has no workflow -> **KEEP IT EMPTY.**\n"
            "   - Do NOT synthesize a workflow from constraints. (e.g., 'Don't use passive voice' is a Constraint, NOT a Workflow step).\n"
            "\n"
            "### MERGE RULES\n"
            "- **Name:** Keep `existing_skill.name` (unless it was empty/generic and candidate is specific).\n"
            "- **Language:** CRITICAL. The output MUST use the **dominant language of the `existing_skill`**. If `candidate` is in a different language, translate the *new logic* to match the `existing` language before merging.\n"
            "- **Prompt Composition (Markdown):**\n"
            "  - **# Goal:** Use `existing` goal. Refine only if `candidate` makes it clearer.\n"
            "  - **# Constraints & Style:** **(This is where 90% of updates happen)**. Combine lists from both. Deduplicate. Keep negative constraints (e.g., 'No hallucinations').\n"
            "  - **# Workflow:** \n"
            "    * If `existing` has one, keep it. Update steps only if `candidate` explicitly corrects a step.\n"
            "    * If `existing` is empty, ADOPT `candidate`'s workflow ONLY IF it is explicitly defined.\n"
            "    * **OTHERWISE: OMIT THIS SECTION.**\n"
            "- **Triggers/Tags:** Union of both lists. Deduplicate.\n"
            "\n"
            "### OUTPUT FORMAT\n"
            "Return JSON fields: {name, description, prompt, triggers, tags, examples}\n"
            "JSON validity: Escape newlines inside strings as \\n."
        )
        user = (
            "existing_skill:\n"
            f"{_skill_for_llm(existing)}\n\n"
            "candidate_skill:\n"
            f"{_candidate_to_raw(cand)}\n"
        )
        print(user)
        text = llm.complete(system=system, user=user, temperature=0.0)
        obj = json_from_llm_text(text)
        if not isinstance(obj, dict):
            return _merge(existing, cand)
        merged = _merge(existing, cand)
        merged.name = str(obj.get("name") or merged.name).strip() or merged.name
        merged.description = (
            str(obj.get("description") or merged.description).strip() or merged.description
        )
        merged.instructions = str(
            obj.get("prompt") or obj.get("instructions") or merged.instructions
        ).strip() or merged.instructions
        merged.triggers = _dedupe(
            [str(t).strip() for t in (obj.get("triggers") or []) if str(t).strip()]
        ) or merged.triggers
        merged.tags = _dedupe(
            [str(t).strip() for t in (obj.get("tags") or []) if str(t).strip()]
        ) or merged.tags
        merged.examples = _merge_examples(
            merged.examples,
            _examples_from_obj(obj.get("examples")),
        )
        return merged
    except Exception:
        return _merge(existing, cand)


def _examples_from_obj(obj) -> List[SkillExample]:
    if not isinstance(obj, list):
        return []
    out: List[SkillExample] = []
    for e in obj[:8]:
        if not isinstance(e, dict):
            continue
        inp = str(e.get("input") or "").strip()
        if not inp:
            continue
        out.append(
            SkillExample(
                input=inp,
                output=(str(e.get("output")).strip() if e.get("output") else None),
                notes=(str(e.get("notes")).strip() if e.get("notes") else None),
            )
        )
    return out


def _prefer_name(old: str, new: str) -> str:
    old_s = (old or "").strip()
    new_s = (new or "").strip()
    if not old_s:
        return new_s
    if not new_s:
        return old_s
    return new_s if len(new_s) < len(old_s) else old_s


def _dedupe(items: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for it in items:
        s = str(it).strip()
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def _merge_examples(old: List[SkillExample], new: List[SkillExample]) -> List[SkillExample]:
    out: List[SkillExample] = []
    seen = set()
    for e in (old or []) + (new or []):
        key = (e.input or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out[:8]


def _bump_patch(version: str) -> str:
    parts = [p for p in str(version or "").split(".") if p.strip().isdigit()]
    if len(parts) != 3:
        return "0.1.1"
    major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
    patch += 1
    return f"{major}.{minor}.{patch}"


def _merge_metadata(old: Dict, extra: Optional[Dict], cand: SkillCandidate) -> Dict:
    out = dict(old or {})
    if extra:
        out.update(extra)
    prev_conf = out.get("confidence")
    try:
        prev_conf_f = float(prev_conf) if prev_conf is not None else 0.0
    except (TypeError, ValueError):
        prev_conf_f = 0.0
    out["confidence"] = max(prev_conf_f, float(cand.confidence))
    return out


def _candidate_to_raw(cand: SkillCandidate) -> Dict:
    return {
        "name": cand.name,
        "description": cand.description,
        "instructions": cand.instructions,
        "triggers": list(cand.triggers or []),
        "tags": list(cand.tags or []),
        "examples": [
            {"input": e.input, "output": e.output, "notes": e.notes}
            for e in (cand.examples or [])
        ],
        "confidence": cand.confidence,
    }


def _skill_to_raw(skill: Skill) -> Dict:
    return {
        "id": skill.id,
        "user_id": skill.user_id,
        "name": skill.name,
        "description": skill.description,
        "instructions": skill.instructions,
        "files": dict(skill.files or {}),
        "triggers": list(skill.triggers or []),
        "tags": list(skill.tags or []),
        "examples": [
            {"input": e.input, "output": e.output, "notes": e.notes}
            for e in (skill.examples or [])
        ],
        "version": skill.version,
        "status": skill.status.value,
        "metadata": dict(skill.metadata or {}),
        "source": skill.source,
        "created_at": skill.created_at,
        "updated_at": skill.updated_at,
    }


def _skill_for_llm(skill: Skill) -> Dict:
    return {
        "name": skill.name,
        "description": skill.description,
        "prompt": skill.instructions,
        "triggers": list(skill.triggers or []),
        "tags": list(skill.tags or []),
        "examples": [
            {"input": e.input, "output": e.output, "notes": e.notes}
            for e in (skill.examples or [])
        ],
        "version": skill.version,
    }


def _merge_files(existing: Dict[str, str], updates: Dict[str, str]) -> Dict[str, str]:
    merged = dict(existing or {})
    for path, content in (updates or {}).items():
        if path and content is not None:
            merged[str(path)] = str(content)
    return merged
