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
_NAME_TOKEN_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+")
_HISTORY_KEY = "_autoskill_version_history"
_HISTORY_LIMIT = 30


def _name_similarity(a: str, b: str) -> float:
    a_tokens = {m.group(0) for m in _NAME_TOKEN_RE.finditer(str(a or "").lower())}
    b_tokens = {m.group(0) for m in _NAME_TOKEN_RE.finditer(str(b or "").lower())}
    if not a_tokens or not b_tokens:
        return 0.0
    inter = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)
    if union <= 0:
        return 0.0
    return float(inter) / float(union)


def _token_set(text: str) -> set[str]:
    return {m.group(0) for m in _NAME_TOKEN_RE.finditer(str(text or "").lower())}


def _overlap_ratio(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    if union <= 0:
        return 0.0
    return float(inter) / float(union)


def _signal_overlap(existing: Skill, candidate: SkillCandidate) -> float:
    existing_signal = "\n".join(
        [
            str(existing.name or ""),
            str(existing.description or ""),
            " ".join([str(t or "") for t in (existing.tags or [])]),
            "\n".join([str(t or "") for t in (existing.triggers or [])]),
        ]
    )
    candidate_signal = "\n".join(
        [
            str(candidate.name or ""),
            str(candidate.description or ""),
            " ".join([str(t or "") for t in (candidate.tags or [])]),
            "\n".join([str(t or "") for t in (candidate.triggers or [])]),
        ]
    )
    return _overlap_ratio(_token_set(existing_signal), _token_set(candidate_signal))


def _clip01(x: float) -> float:
    v = float(x)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _merge_confidence_by_code(
    *,
    existing: Skill,
    candidate: SkillCandidate,
    similarity: float,
    threshold: float,
) -> float:
    """
    Generic, provider-agnostic merge confidence from semantic + lexical signals.

    This intentionally avoids domain/channel keyword rules and only uses:
    - vector similarity from retrieval
    - name overlap
    - intent-signal overlap (name/description/tags/triggers)
    """

    similarity_f = _clip01(float(similarity or 0.0))
    threshold_f = _clip01(float(threshold or 0.0))
    # Normalize semantic confidence around threshold; allow a margin for noisy embeddings.
    semantic_floor = max(0.0, threshold_f - 0.15)
    semantic_norm = _clip01((similarity_f - semantic_floor) / max(1e-6, 1.0 - semantic_floor))

    name_sim = _name_similarity(existing.name, candidate.name)
    signal_sim = _signal_overlap(existing, candidate)
    # Weighted blend: semantic signal dominates, lexical signal stabilizes near threshold.
    return _clip01(0.70 * semantic_norm + 0.18 * signal_sim + 0.12 * name_sim)


def _judge_merge_with_llm(
    llm,
    *,
    existing: Skill,
    candidate: SkillCandidate,
    similarity: float,
    threshold: float,
) -> Tuple[bool, float, str]:
    """
    LLM semantic judge for same-capability check.

    Returns:
    - same_capability: bool
    - confidence: [0,1]
    - reason: short text
    """

    if llm is None:
        return False, 0.0, "no_llm"
    system = (
        "You are AutoSkill's capability identity judge.\n"
        "Task: decide whether candidate_skill should UPDATE/MERGE an existing_skill or be a NEW skill.\n"
        "Output ONLY strict JSON, no markdown, no extra text.\n"
        "\n"
        "### Decision Principles\n"
        "- same_capability=true only when both skills solve the same job-to-be-done and candidate is mainly an iteration/refinement.\n"
        "- same_capability=false when deliverable objective, target audience, or evaluation criteria differ materially.\n"
        "- Hard split: if primary deliverable class changes (artifact/form/channel), treat as different capability.\n"
        "- Hard split: if intended audience or acceptance criteria change materially, treat as different capability.\n"
        "- Do NOT treat renaming, wording changes, or different examples as a new capability.\n"
        "- Treat durable implementation/output policy upgrades (language/runtime/tool constraints, output contract strictness, explanation depth, comment policy) as same-capability refinement when job-to-be-done is unchanged.\n"
        "\n"
        "### Recency and Continuity Rules\n"
        "- Treat candidate_skill as recent interaction intent; existing_skill as historical memory.\n"
        "- Use history only to judge continuity vs topic switch.\n"
        "- Detect whether recent turns contain a boundary turn (a new objective/deliverable/channel/task).\n"
        "- First test ongoing work item continuity: objective + deliverable type + operation class must stay aligned.\n"
        "- If boundary turn exists, evaluate capability identity mainly by post-boundary intent rather than earlier topic context.\n"
        "- If ongoing work item shifts, return same_capability=false even when style/domain overlap exists.\n"
        "- If recent intent indicates topic switch (new objective/deliverable/audience), return same_capability=false.\n"
        "- If continuity is unclear, default to same_capability=false.\n"
        "\n"
        "### De-identification and Portability Rules\n"
        "- Evaluate capability identity AFTER removing instance details (org/team/person names, addresses, project/product/repo names, IDs, URLs, exact dates/budgets).\n"
        "- If differences are mainly instance/topic entities, treat as same capability.\n"
        "- If candidate contains only one-off case details and no portable constraints, treat as not a meaningful new capability.\n"
        "- A single explicit user policy constraint can be sufficient signal if it is portable and reusable.\n"
        "\n"
        "Return schema:\n"
        "{\n"
        '  "same_capability": true|false,\n'
        '  "confidence": 0.0-1.0,\n'
        '  "reason": "short reason"\n'
        "}\n"
    )
    data = {
        "similarity": float(similarity or 0.0),
        "dedupe_threshold": float(threshold or 0.0),
        "existing_skill": _skill_for_llm(existing),
        "candidate_skill": _candidate_to_raw(candidate),
    }
    user = json.dumps(data, ensure_ascii=False)
    try:
        out = llm.complete(system=system, user=user, temperature=0.0)
        obj = json_from_llm_text(out)
        same = bool(obj.get("same_capability"))
        conf = _clip01(float(obj.get("confidence", 0.0) or 0.0))
        reason = str(obj.get("reason") or "").strip()
        return same, conf, reason
    except Exception as e:
        return False, 0.0, f"judge_error:{e}"


def _should_merge(
    *,
    llm,
    existing: Skill,
    candidate: SkillCandidate,
    similarity: float,
    threshold: float,
) -> bool:
    """
    Unified merge gate.

    Priority:
    1) LLM semantic judge when available (primary decision source)
    2) deterministic score only as fallback/safety net
    """

    score = _merge_confidence_by_code(
        existing=existing,
        candidate=candidate,
        similarity=similarity,
        threshold=threshold,
    )

    if llm is not None:
        same, conf, _reason = _judge_merge_with_llm(
            llm,
            existing=existing,
            candidate=candidate,
            similarity=similarity,
            threshold=threshold,
        )
        if conf >= 0.55:
            return bool(same)
        # Low-confidence LLM output: rely on deterministic score as a conservative backup.
        if score >= 0.82:
            return True
        if score <= 0.20:
            return False
        return bool(score >= 0.52)

    # LLM unavailable: deterministic fallback.
    if score >= 0.80:
        return True
    if score <= 0.22:
        return False
    return bool(score >= 0.50)


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
        """
        Maintainer owns add/merge/discard decisions after extraction.

        It can run in:
        - heuristic mode
        - llm mode (decision + merge synthesis)
        """

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
        """Extracts and removes previous-skill hints from metadata."""

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
        """Returns in-memory last upserted skill id for a user in this process."""

        uid = str(user_id or "").strip()
        if not uid:
            return None
        with self._last_lock:
            sid = self._last_upserted_skill_id_by_user.get(uid)
        return str(sid).strip() if sid and str(sid).strip() else None

    def _record_last_upserted_skill_id(self, *, user_id: str, skill_id: str) -> None:
        """Records last upserted skill id for follow-up merge preference."""

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
        """
        Applies maintenance for each candidate and returns upserted skills.

        Candidates that resolve to `discard` are omitted from the returned list.
        """

        out: List[Skill] = []
        for cand in candidates:
            skill = self._upsert_candidate(cand, user_id=user_id, metadata=metadata)
            if skill is not None:
                out.append(skill)
        return out

    def _upsert_candidate(
        self, cand: SkillCandidate, *, user_id: str, metadata: Optional[Dict]
    ) -> Optional[Skill]:
        """
        Core maintenance decision pipeline for one candidate.

        Priority:
        1) build candidate context (previous skill hint + similar skill retrieval)
        2) llm decision (add/merge/discard) when available
        3) heuristic fallback when llm is unavailable
        """

        previous_id, metadata_clean = self._pop_previous_skill_id(metadata)
        previous_id = previous_id or self._get_last_upserted_skill_id(user_id=user_id)
        merge_gate_cache: Dict[str, bool] = {}

        def _persist_merged(target: Skill) -> Skill:
            merged = (
                _merge_with_llm(self._llm, target, cand)
                if self._llm is not None
                else _merge(target, cand)
            )
            merged.updated_at = now_iso()
            merged.metadata = _append_version_snapshot(
                _merge_metadata(target.metadata, metadata_clean, cand),
                target,
            )
            if self._config.store_sources and cand.source:
                merged.source = cand.source
            merged.files = _merge_files(target.files, build_agent_skill_files(merged))
            self._store.upsert(merged, raw=_skill_to_raw(merged))
            self._record_last_upserted_skill_id(user_id=user_id, skill_id=merged.id)
            return merged

        def _can_merge_to(target: Skill, score: float, *, threshold: float) -> bool:
            sid = str(getattr(target, "id", "") or "")
            cache_key = f"{sid}|{round(float(score or 0.0), 6)}|{round(float(threshold or 0.0), 6)}"
            cached = merge_gate_cache.get(cache_key)
            if cached is not None:
                return bool(cached)
            decision = _should_merge(
                llm=self._llm,
                existing=target,
                candidate=cand,
                similarity=float(score or 0.0),
                threshold=float(threshold or 0.0),
            )
            merge_gate_cache[cache_key] = bool(decision)
            return bool(decision)

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
            if self._llm is None:
                prev_force_merge_threshold = float(
                    (self._config.extra or {}).get(
                        "previous_skill_force_merge_threshold",
                        max(prev_threshold + 0.18, 0.72),
                    )
                )
                if prev_score >= prev_force_merge_threshold:
                    if _can_merge_to(previous_skill, prev_score, threshold=prev_threshold):
                        return _persist_merged(previous_skill)
                if prev_score >= prev_threshold:
                    if _can_merge_to(previous_skill, prev_score, threshold=prev_threshold):
                        return _persist_merged(previous_skill)

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
                    if target_id:
                        target = self._store.get(target_id)
                        if target is not None:
                            owner = str(getattr(target, "user_id", "") or "").strip()
                            if _is_library_skill(target) or owner != str(user_id):
                                target = None
                if target is not None:
                    return _persist_merged(target)

                if best_user and best_user.score >= self._config.dedupe_similarity_threshold and _can_merge_to(
                    best_user.skill,
                    float(best_user.score),
                    threshold=float(self._config.dedupe_similarity_threshold),
                ):
                    return _persist_merged(best_user.skill)
                return _create_new()

            # If LLM action is missing/invalid, fall back to deterministic maintenance.
            if best_user and best_user.score >= self._config.dedupe_similarity_threshold and _can_merge_to(
                best_user.skill,
                float(best_user.score),
                threshold=float(self._config.dedupe_similarity_threshold),
            ):
                return _persist_merged(best_user.skill)
            if (
                best_any
                and best_library
                and best_library.score >= self._config.dedupe_similarity_threshold
                and _can_merge_to(
                best_library.skill,
                float(best_library.score),
                threshold=float(self._config.dedupe_similarity_threshold),
                )
            ):
                return None
            return _create_new()

        # Fallback / heuristic maintenance:
        # - merge into the best user-owned skill when clearly similar
        # - otherwise, if a shared library skill is clearly similar, discard the candidate to avoid duplication
        # - otherwise, add a new user skill
        if best_user and best_user.score >= self._config.dedupe_similarity_threshold:
            if _can_merge_to(
                best_user.skill,
                float(best_user.score),
                threshold=float(self._config.dedupe_similarity_threshold),
            ):
                return _persist_merged(best_user.skill)

        if best_any and best_library and best_library.score >= self._config.dedupe_similarity_threshold:
            # Discard only when the shared skill is safely considered the same capability.
            if _can_merge_to(
                best_library.skill,
                float(best_library.score),
                threshold=float(self._config.dedupe_similarity_threshold),
            ):
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
        "Quality-first: if merge-vs-add is unclear you may discard, but do not discard clearly reusable candidates.\n"
        "\n"
        "### Context\n"
        "- Skills are modular capability packages (SKILL.md + optional resources) that onboard another assistant instance.\n"
        "- Maintain a high-signal, non-redundant skill set.\n"
        "- Favor progressive disclosure: store concise metadata + an executable prompt; avoid storing long reference dumps.\n"
        "- Decision objective: maximize long-term capability quality while minimizing skill fragmentation.\n"
        "- Evaluate candidate portability after removing instance-specific details.\n"
        "- Candidate is derived from recent conversation rounds; existing skills reflect older accumulated memory.\n"
        "- Historical context should mainly help determine whether the topic continues or switches.\n"
        "\n"
        "### Output Action (choose one)\n"
        "- add: store the candidate as a new user skill\n"
        "- merge: merge the candidate into ONE existing USER skill (pick target_skill_id)\n"
        "- discard: do not store the candidate\n"
        "\n"
        "### Decision Procedure (follow in order)\n"
        "0) Topic continuity and family check\n"
        "- Compare candidate with existing USER skills to determine whether recent intent continues the same topic.\n"
        "- First locate a boundary turn in recent conversation (where user starts a new objective/deliverable/channel/task).\n"
        "- If boundary exists, prefer post-boundary intent as the active work item; treat pre-boundary context as background.\n"
        "- First determine whether they represent the same ongoing work item (objective + deliverable type + operation class).\n"
        "- If same domain/style but different ongoing work item, treat as topic switch.\n"
        "- Do not merge only because style constraints overlap across boundary; overlap without work-item continuity is insufficient.\n"
        "- If recent intent clearly switches objective/deliverable/audience, do NOT force merge just because style/domain looks similar.\n"
        "- Infer capability family first (for example: writing/editing, coding/debugging, analysis/modeling, planning/operations).\n"
        "- If candidate and target skill are in different capability families, choose add.\n"
        "- Treat family switch as stronger evidence than embedding similarity.\n"
        "1) Discard gate\n"
        "- Choose discard if candidate is generic, low-signal, not clearly reusable, or adds no durable user-specific value.\n"
        "- Choose discard if a shared library skill already covers it and candidate has no stable improvement.\n"
        "- Choose discard if candidate mainly contains one-off case entities (orgs, names, addresses, project IDs, URLs, exact dates/budgets) and cannot survive de-identification.\n"
        "- Do NOT discard when candidate contributes durable user-level implementation/output policy constraints that can guide future similar tasks.\n"
        "2) Capability identity test against USER skills\n"
        "- Compare candidate vs each user skill on four axes:\n"
        "  a) core job-to-be-done,\n"
        "  b) output contract/deliverable type,\n"
        "  c) hard constraints and success criteria,\n"
        "  d) required context/tools/workflow.\n"
        "- Hard non-merge: if deliverable class/channel or target audience/evaluation rubric materially differs, treat as different capability.\n"
        "- Hard non-merge: if task verbs indicate different primary work (for example, compose/rewrite vs implement/debug vs analyze/forecast), treat as different capability.\n"
        "- Ignore instance-specific entities when comparing capability identity.\n"
        "- Ignore generic quality constraints (for example: be concrete, avoid hallucination, concise style, reliable citations) as identity signals; these alone must not drive merge.\n"
        "- Treat as SAME capability only when the core method and completion criteria substantially match after removing instance details.\n"
        "- If completion criteria differ (even with similar style constraints), treat as different capability.\n"
        "3) Merge vs add\n"
        "- If SAME capability with any user skill: choose merge to the best matching target_skill_id.\n"
        "- If candidate is mostly an iteration (clearer prompt, stronger checks, extra constraints, better metadata), choose merge.\n"
        "- If candidate adds reusable implementation/output policy for the same job-to-be-done, choose merge rather than discard.\n"
        "- If differences are mostly topic/entity substitution but the method and quality bar are the same, choose merge.\n"
        "- Require continuity of ongoing work item before merge; otherwise choose add.\n"
        "- If topic continuity is broken (new objective/deliverable/audience in recent intent), choose add.\n"
        "- Choose add only if candidate introduces a durable non-overlapping capability that remains distinct after removing instance details.\n"
        "4) Tie-breakers\n"
        "- On uncertainty: choose add when topic continuity is weak/unclear; choose merge only when continuity is strong.\n"
        "- Never choose add only due renaming, wording/style change, or example replacement.\n"
        "- Similarity scores are hints, not the sole criterion.\n"
        "\n"
        "### Constraints\n"
        "- If action is merge, target_skill_id MUST refer to a skill with scope == 'user' in the provided similar list.\n"
        "- Do not propose deleting any existing skills.\n"
        "- Keep reason short and concrete (<= 30 words).\n"
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
    """Builds a retrieval query string from candidate fields."""

    return f"{cand.name}\n{cand.description}\n{cand.instructions}"


def _merge(existing: Skill, cand: SkillCandidate) -> Skill:
    """
    Heuristic merge strategy (deterministic, no LLM).

    Keeps existing stable identity and increments patch version.
    """

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

    # Keep stable naming on heuristic merge: update name only when the existing one is missing.
    merged_name = (existing.name or "").strip() or (cand.name or "").strip()

    merged = replace(
        existing,
        name=merged_name,
        description=description,
        instructions=instructions,
        triggers=_dedupe(existing.triggers + list(cand.triggers or [])),
        tags=_dedupe(existing.tags + list(cand.tags or [])),
        examples=_merge_examples(existing.examples, cand.examples),
        version=_bump_patch(existing.version),
    )
    return merged


def _merge_with_llm(llm, existing: Skill, cand: SkillCandidate) -> Skill:
    """
    LLM-assisted merge that preserves extractor schema.

    Falls back to heuristic `_merge` on any parsing/runtime error.
    """

    try:
        system = (
            "You are AutoSkill's Skill Merger.\n"
            "Task: Merge existing_skill and candidate_skill into ONE improved Skill.\n"
            "Output ONLY strict JSON (parsable by json.loads); no Markdown, no commentary, no extra text.\n"
            "Quality-first: keep existing core stable and merge only candidate additions that are clearly reusable.\n"
            "\n"
            "IMPORTANT: Follow the SAME requirements as the Skill Extractor. Do NOT invent a new format.\n"
            "Only output the required fields: {name, description, prompt, triggers, tags, examples}.\n"
            "\n"
            "### 1) Merge Principles\n"
            "- Shared intent: keep the same capability (do not change the skill's purpose).\n"
            "- Diff-aware: merge unique, non-conflicting constraints and improvements from BOTH skills.\n"
            "- Field merge operator: perform semantic union, NOT concatenation.\n"
            "- Recency/topic guard: keep constraints aligned with the candidate's recent-topic intent; do not import stale constraints from unrelated old topics.\n"
            "- Constraints over content: keep reusable rules and constraints; do not expand topic-specific details.\n"
            "- Avoid regressions: do NOT drop important constraints/checks from existing_skill unless they are clearly wrong or overly specific.\n"
            "- If candidate_skill adds no durable value, keep existing_skill largely unchanged.\n"
            "\n"
            "### 2) Anti-Duplication (CRITICAL)\n"
            "- Never duplicate section headers or blocks in any field.\n"
            "- Never copy markdown section labels into list fields (triggers/tags/examples).\n"
            "- For near-duplicate phrases, keep only one clearer canonical phrasing.\n"
            "- Preserve signal density: shorter, cleaner, non-redundant output is preferred.\n"
            "\n"
            "### 3) De-identification and Portability (CRITICAL)\n"
            "- Remove case-specific entities unless they are truly stable reusable constraints.\n"
            "- Exclude organization/team/person names, addresses, project/product/repo names, branch/ticket/account IDs, URLs/emails/phones, exact dates/budgets/contracts.\n"
            "- Keep portable capability rules; do not merge one-off business facts.\n"
            "- If candidate adds only instance-specific details, do not import them.\n"
            "\n"
            "### 4) No-Invention Rules (CRITICAL)\n"
            "- Use ONLY information present in existing_skill and candidate_skill.\n"
            "- Do NOT add generic industry standards or imagined details.\n"
            "\n"
            "### 5) Language Consistency\n"
            "- Keep language consistent with existing_skill unless candidate_skill is clearly a different user language.\n"
            "- If candidate_skill is in a different language, translate ONLY the new logic to match existing_skill.\n"
            "- Do NOT mix languages inside the same field.\n"
            "\n"
            "### 6) Field Definitions (MUST FOLLOW)\n"
            "- name: Concise, specific, kebab-case (for English). Keep existing_skill.name unless the new name is clearly more specific and improves retrieval; include durable topic/domain and platform/channel cues when user-evidenced (for example, WeChat Official Account, Xiaohongshu, Weibo/Sina, Douyin, Twitter/X, or other platforms).\n"
            "- description: 1-2 sentences in third person. Clearly state WHAT the skill does and WHEN to use it, including domain/platform usage scope when relevant.\n"
            "- prompt: Use Markdown. Keep this structure EXACTLY:\n"
            "  1. # Goal (Required)\n"
            "  2. # Constraints & Style (Required: capture concrete user rules and negative constraints)\n"
            "  3. # Workflow (OPTIONAL: include ONLY if either skill explicitly defines a multi-step process of distinct actions).\n"
            "     - If steps are merely document sections, they belong in Constraints & Style, NOT Workflow.\n"
            "  - Content strategy: keep only user-specific requirements; do NOT add new rules.\n"
            "  - Resources: if reusable scripts/references are implied, mention 'Execute script: scripts/...' or 'Read reference: references/...'.\n"
            "  - Forbidden in prompt: '## Prompt', '## Triggers', '## Tags', '## Examples', frontmatter blocks, repeated title blocks.\n"
            "  - Ensure prompt appears exactly once as a single body, not nested/duplicated.\n"
            "- triggers: 3-5 short, concrete phrases representing user intent.\n"
            "  - Build by semantic union from both skills, then dedupe (exact + near-duplicate paraphrases).\n"
            "  - Preserve reusable platform/channel intent signals when user-evidenced; use canonical platform labels and avoid account-specific names.\n"
            "  - Do NOT repeat same intent with wording variants.\n"
            "- tags: 1-6 keywords.\n"
            "  - Build by semantic union, keep canonical tags only, remove synonyms/redundant variants.\n"
            "  - Keep domain/platform tags when they materially affect usage/retrieval; do not duplicate equivalent platform aliases.\n"
            "- examples: 0-3 short, de-identified inputs.\n"
            "  - Keep only distinct examples; merge overlapping ones into one clearer example.\n"
            "\n"
            "### 7) Generalization and Final Self-Checks\n"
            "- De-identify aggressively: remove instance details; only keep stable reusable constraints/procedures.\n"
            "- Placeholders are optional (<PROJECT>, <ENV>, <TOOL>, <DATE>, <VERSION>) and should only be kept when they preserve reusable logic.\n"
            "- Final self-check: output fields must not contain one-off proper nouns or case-specific business facts.\n"
            "- Final self-check: each field must be internally de-duplicated; no repeated bullets or repeated section headers.\n"
            "\n"
            "### 8) JSON Validity\n"
            "- Escape newlines inside strings as \\n.\n"
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
    """Merges metadata and keeps the max observed confidence."""

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


def _skill_snapshot_for_history(skill: Skill) -> Dict[str, Optional[str]]:
    files = dict(getattr(skill, "files", {}) or {})
    return {
        "version": str(getattr(skill, "version", "") or ""),
        "name": str(getattr(skill, "name", "") or ""),
        "description": str(getattr(skill, "description", "") or ""),
        "instructions": str(getattr(skill, "instructions", "") or ""),
        "skill_md": str(files.get("SKILL.md") or ""),
        "updated_at": str(getattr(skill, "updated_at", "") or ""),
    }


def _append_version_snapshot(metadata: Dict, skill: Skill) -> Dict:
    out = dict(metadata or {})
    hist_raw = out.get(_HISTORY_KEY)
    hist: List[Dict] = []
    if isinstance(hist_raw, list):
        for item in hist_raw:
            if isinstance(item, dict):
                hist.append(dict(item))
    hist.append(_skill_snapshot_for_history(skill))
    if len(hist) > int(_HISTORY_LIMIT):
        hist = hist[-int(_HISTORY_LIMIT) :]
    out[_HISTORY_KEY] = hist
    return out


def _candidate_to_raw(cand: SkillCandidate) -> Dict:
    """Serializes a candidate for logging/LLM decision payloads."""

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
    """Serializes a persisted skill record."""

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
    """Serializes only LLM-relevant fields used in merge prompts."""

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
    """Overlay merge for skill artifact files, preserving existing resources by default."""

    merged = dict(existing or {})
    for path, content in (updates or {}).items():
        if path and content is not None:
            merged[str(path)] = str(content)
    return merged
