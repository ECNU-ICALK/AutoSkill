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
import uuid
from dataclasses import replace
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
        # Search for similar skills using the candidate text to avoid duplicates.
        # Include both user skills and shared library skills as references.
        similar = self._store.search(
            user_id=user_id,
            query=_candidate_to_query(cand),
            limit=self._config.max_similar_skills_to_consider,
            filters={"scope": "all"},
        )

        best_any = similar[0] if similar else None
        best_user = next((h for h in similar if not _is_library_skill(h.skill)), None)
        best_library = next((h for h in similar if _is_library_skill(h.skill)), None)

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
                metadata=_merge_metadata({}, metadata, cand),
                source=cand.source if self._config.store_sources else None,
                created_at=now_iso(),
                updated_at=now_iso(),
            )
            created.files = build_agent_skill_files(created)
            self._store.upsert(created, raw=_skill_to_raw(created))
            return created

        if self._llm is not None:
            try:
                action, target_skill_id, _reason = _decide_candidate_action_with_llm(
                    self._llm,
                    cand,
                    similar,
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
                        for h in (similar or [])
                        if getattr(h, "skill", None) is not None and not _is_library_skill(h.skill)
                    }
                    if target_id and target_id in allowed_user_ids:
                        target = self._store.get(target_id)
                        if target is not None and _is_library_skill(target):
                            target = None
                if target is None and best_user is not None:
                    target = best_user.skill
                if target is not None:
                    merged = _merge_with_llm(self._llm, target, cand)
                    merged.updated_at = now_iso()
                    merged.metadata = _merge_metadata(target.metadata, metadata, cand)
                    if self._config.store_sources and cand.source:
                        merged.source = cand.source
                    merged.files = _merge_files(target.files, build_agent_skill_files(merged))
                    self._store.upsert(merged, raw=_skill_to_raw(merged))
                    return merged

                return _create_new()

        # Fallback / heuristic maintenance:
        # - merge into the best user-owned skill when clearly similar
        # - otherwise, if a shared library skill is clearly similar, discard the candidate to avoid duplication
        # - otherwise, add a new user skill
        if best_user and best_user.score >= self._config.dedupe_similarity_threshold:
            merged = _merge(best_user.skill, cand)
            merged.updated_at = now_iso()
            merged.metadata = _merge_metadata(best_user.skill.metadata, metadata, cand)
            if self._config.store_sources and cand.source:
                merged.source = cand.source
            merged.files = _merge_files(best_user.skill.files, build_agent_skill_files(merged))
            self._store.upsert(merged, raw=_skill_to_raw(merged))
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
    instructions = existing.instructions
    if len(cand.instructions.strip()) > len(existing.instructions.strip()) * 1.1:
        instructions = cand.instructions.strip()

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
            "Task: merge existing_skill and candidate_skill into a better single Skill.\n"
            "Output ONLY strict JSON (parsable by json.loads); no Markdown, no commentary, no extra text.\n"
            "\n"
            "Skills are modular capability packages (SKILL.md + optional resources) used to onboard another assistant instance.\n"
            "Keep the merged skill high-signal, reusable, and easy to retrieve.\n"
            "Rules:\n"
            "1) Keep only reusable capabilities and generalize/de-identify: remove names, orgs, project IDs, accounts, URLs, secrets, exact dates/amounts; use placeholders like <PROJECT>, <ENV>, <TOOL>, <DATE>, <VERSION>.\n"
            "2) Keep existing_skill.name stable; only replace it if the new name is clearly more specific and improves retrieval.\n"
            "3) description: 1-2 sentences in third person; include WHEN the skill should be used.\n"
            "4) prompt: ALWAYS English; imperative/infinitive form; must be executable (numbered steps + per-step checks + output format); do not reference 'this conversation/above'.\n"
            "5) prompt may include a short \"Bundled resources (optional)\" section suggesting scripts/references/assets; do not paste large content.\n"
            "6) Deduplicate triggers/tags/examples; keep 0-3 representative examples.\n"
            "7) JSON validity: escape newlines inside strings as \\n.\n"
            "Return JSON fields: {name, description, prompt, triggers, tags, examples}\n"
        )
        user = (
            "existing_skill:\n"
            f"{_skill_for_llm(existing)}\n\n"
            "candidate_skill:\n"
            f"{_candidate_to_raw(cand)}\n"
        )
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
