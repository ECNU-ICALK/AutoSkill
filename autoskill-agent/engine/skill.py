from __future__ import annotations

import json
import math
import os
import re
import shutil
from typing import Any, Dict, List, Optional

from engine.clients import OpenAICompatEmbeddingClient, TeacherRouter
from engine.core import (
    SkillDecision,
    SkillDraft,
    SuccessScore,
    Trajectory,
    bump_patch,
    extract_frontmatter,
    normalize_tool_name,
    now_iso,
    read_json,
    render_skill_md,
    sha1_obj,
    sha1_text,
    slugify,
    write_json,
)


class SuccessEvaluator:
    """
    Trajectory success and usability filter.

    LLM judgment is primary when a judge is configured.
    Heuristic scoring is used as fallback to keep the pipeline available.
    """

    POSITIVE_MARKERS = {
        "thanks",
        "thank you",
        "great",
        "done",
        "resolved",
        "works",
        "got it",
        "谢谢",
        "搞定",
        "可以了",
        "已解决",
        "完成了",
    }
    NEGATIVE_MARKERS = {
        "error",
        "failed",
        "doesn't work",
        "not working",
        "still wrong",
        "报错",
        "失败",
        "不行",
        "不对",
        "没解决",
    }

    def __init__(self, *, threshold: float = 0.65, judge: TeacherRouter | None = None) -> None:
        self.threshold = float(threshold)
        self.judge = judge

    def evaluate(self, trajectory: Trajectory) -> SuccessScore:
        llm_score = self._evaluate_by_llm(trajectory)
        if llm_score is not None:
            return llm_score
        return self._evaluate_by_heuristic(trajectory)

    def _evaluate_by_llm(self, trajectory: Trajectory) -> SuccessScore | None:
        if self.judge is None or not self.judge.available():
            return None
        system = (
            "You are AutoSkill-Agent's trajectory evaluator.\n"
            "Judge whether one trajectory is suitable for skill extraction.\n"
            "Prioritize reliability and reusable value.\n"
            "Output strict JSON only:\n"
            "{\"usable\": true|false, \"score\": 0.0-1.0, \"reason\": \"...\"}\n"
            "Guidelines:\n"
            "- usable=true only when the trajectory likely solved the user's goal with enough evidence.\n"
            "- Require reusable process signals (stable steps/tool-use), not one-off noise.\n"
            "- If uncertain, set usable=false.\n"
            "- Keep reason short and concrete."
        )
        snapshot = {
            "trajectory_id": trajectory.trajectory_id,
            "user_instruction": trajectory.user_instruction,
            "environment": trajectory.environment,
            "messages": trajectory.messages[-16:],
            "tool_calls": trajectory.tool_calls[-24:],
            "raw_signals": {
                "status": trajectory.raw.get("status"),
                "success": trajectory.raw.get("success"),
                "completed": trajectory.raw.get("completed"),
            },
        }
        user = "Trajectory snapshot (JSON):\n" + json.dumps(snapshot, ensure_ascii=False)
        parsed = self.judge.complete_json(system=system, user=user, temperature=0.0, task="trajectory_evaluation")
        if not isinstance(parsed, dict):
            return None
        usable = bool(parsed.get("usable"))
        try:
            score = float(parsed.get("score"))
        except Exception:
            score = 0.0
        score = min(1.0, max(0.0, score))
        reason = str(parsed.get("reason") or "llm_judged").strip() or "llm_judged"
        ok = usable and score >= self.threshold
        return SuccessScore(ok=ok, score=score, reason=reason)

    def _evaluate_by_heuristic(self, trajectory: Trajectory) -> SuccessScore:
        raw = trajectory.raw
        score = 0.0
        reasons: List[str] = []
        if self._has_explicit_failure(raw):
            score -= 0.9
            reasons.append("explicit_failure")
        if self._has_explicit_success(raw):
            score += 0.55
            reasons.append("explicit_success")
        feedback = self._latest_user_feedback(trajectory.messages)
        if feedback:
            text = feedback.lower()
            if any(k in text for k in self.POSITIVE_MARKERS):
                score += 0.25
                reasons.append("positive_user_feedback")
            if any(k in text for k in self.NEGATIVE_MARKERS):
                score -= 0.45
                reasons.append("negative_user_feedback")
        if trajectory.tool_calls:
            error_tools = [t for t in trajectory.tool_calls if str(t.get("status") or "").lower() in {"error", "failed"}]
            if error_tools:
                score -= 0.25
                reasons.append("tool_errors")
            else:
                score += 0.20
                reasons.append("tool_chain_completed")
        if trajectory.messages:
            score += 0.10
            reasons.append("has_conversation_context")
        ok = score >= self.threshold
        return SuccessScore(ok=ok, score=score, reason=",".join(reasons) if reasons else "no_signal")

    def _has_explicit_success(self, raw: Dict[str, Any]) -> bool:
        for key in ("success", "completed"):
            if raw.get(key) is True:
                return True
        status = str(raw.get("status") or "").strip().lower()
        return status in {"ok", "success", "completed", "done"}

    def _has_explicit_failure(self, raw: Dict[str, Any]) -> bool:
        for key in ("success", "completed"):
            if raw.get(key) is False:
                return True
        status = str(raw.get("status") or "").strip().lower()
        return status in {"error", "failed", "failure", "aborted"}

    def _latest_user_feedback(self, messages: List[Dict[str, Any]]) -> str:
        for m in reversed(messages or []):
            if str(m.get("role") or "").lower() != "user":
                continue
            content = str(m.get("content") or "").strip()
            if content:
                return content
        return ""


class SkillSynthesizer:
    """
    Convert successful trajectories into reusable agentic SKILL.md drafts.
    """

    def __init__(self, *, teacher: Optional[TeacherRouter]) -> None:
        self.teacher = teacher

    def synthesize(self, trajectory: Trajectory) -> Optional[SkillDraft]:
        draft = self._synthesize_by_teacher(trajectory) if self.teacher is not None else None
        if draft is None:
            draft = self._fallback_synthesize(trajectory)
        if draft is None:
            return None
        cleaned = self._post_clean(draft)
        cleaned.fingerprint = sha1_obj(
            {
                "name": cleaned.name.lower(),
                "description": cleaned.description.lower(),
                "tools": [x.lower() for x in cleaned.tools],
                "steps": [x.lower() for x in cleaned.steps],
            }
        )
        return cleaned

    def _synthesize_by_teacher(self, trajectory: Trajectory) -> Optional[SkillDraft]:
        system = (
            "You are AutoSkill-Agent's teacher. Convert successful agent trajectories into a reusable OpenClaw skill.\n"
            "Output strict JSON only:\n"
            "{"
            "\"name\":\"...\","
            "\"description\":\"...\","
            "\"version\":\"1.0.0\","
            "\"tools\":[\"tool_a\",\"tool_b\"],"
            "\"steps\":[\"step1\",\"step2\"]"
            "}\n"
            "Rules:\n"
            "- Keep reusable process knowledge; remove task-specific payload.\n"
            "- Replace specific file names, dates, ids, URLs, exact numbers with placeholders such as <FILE>, <DATE>, <ID>, <URL>, <VALUE>.\n"
            "- Focus on successful tool-use patterns and execution order.\n"
            "- name should be concise, capability-oriented, and searchable.\n"
            "- description should explain when to use this skill.\n"
            "- tools should be normalized tool identifiers.\n"
            "- steps should be actionable and generic.\n"
            "- Do not output markdown."
        )
        snapshot = {
            "trajectory_id": trajectory.trajectory_id,
            "user_instruction": trajectory.user_instruction,
            "environment": trajectory.environment,
            "messages": trajectory.messages[-12:],
            "tool_calls": trajectory.tool_calls[-20:],
        }
        user = "Trajectory snapshot (JSON):\n" + json.dumps(snapshot, ensure_ascii=False) + "\n\nGenerate skill JSON:"
        parsed = (
            self.teacher.complete_json(system=system, user=user, temperature=0.0, task="skill_synthesis")
            if self.teacher
            else None
        )
        if not isinstance(parsed, dict):
            return None
        return self._from_json(parsed, trajectory_id=trajectory.trajectory_id)

    def _fallback_synthesize(self, trajectory: Trajectory) -> Optional[SkillDraft]:
        tools = [t.get("name", "") for t in trajectory.tool_calls if str(t.get("name") or "").strip()]
        uniq_tools: List[str] = []
        for t in tools:
            n = normalize_tool_name(str(t))
            if n not in uniq_tools:
                uniq_tools.append(n)
        if not uniq_tools:
            uniq_tools = ["terminal"]

        name_seed = trajectory.user_instruction or "agent-workflow"
        name = slugify(name_seed)
        desc = "Use when a similar multi-step agent workflow needs to be executed reliably."
        steps = self._derive_steps_from_tools(trajectory.tool_calls)
        if not steps:
            steps = [
                "Identify the target objective and required inputs.",
                "Execute tools in a validated order and keep outputs structured.",
                "Validate final output against user constraints before returning.",
            ]
        return SkillDraft(
            name=name,
            description=desc,
            version="1.0.0",
            tools=uniq_tools[:10],
            steps=steps[:12],
            source_trajectory_id=trajectory.trajectory_id,
        )

    def _derive_steps_from_tools(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        out: List[str] = []
        for t in tool_calls:
            name = normalize_tool_name(str(t.get("name") or "tool"))
            out.append(f"Use `{name}` to complete the next required sub-task and capture outputs.")
        uniq: List[str] = []
        for s in out:
            if s not in uniq:
                uniq.append(s)
        return uniq

    def _from_json(self, obj: Dict[str, Any], *, trajectory_id: str) -> Optional[SkillDraft]:
        name = slugify(str(obj.get("name") or "agent-workflow"))
        description = str(obj.get("description") or "").strip()
        version = str(obj.get("version") or "1.0.0").strip() or "1.0.0"
        tools_raw = obj.get("tools")
        steps_raw = obj.get("steps")
        if not isinstance(tools_raw, list) or not isinstance(steps_raw, list):
            return None
        tools = [normalize_tool_name(str(x)) for x in tools_raw if str(x).strip()]
        steps = [str(x).strip() for x in steps_raw if str(x).strip()]
        if not description or not tools or not steps:
            return None
        return SkillDraft(
            name=name,
            description=description,
            version=version,
            tools=tools[:12],
            steps=steps[:16],
            source_trajectory_id=trajectory_id,
        )

    def _post_clean(self, draft: SkillDraft) -> SkillDraft:
        uniq_tools: List[str] = []
        for t in draft.tools:
            n = normalize_tool_name(t)
            if n and n not in uniq_tools:
                uniq_tools.append(n)

        uniq_steps: List[str] = []
        for s in draft.steps:
            text = str(s).strip()
            if text and text not in uniq_steps:
                uniq_steps.append(text)

        version = str(draft.version or "").strip()
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            version = "1.0.0"

        return SkillDraft(
            name=slugify(draft.name),
            description=str(draft.description).strip(),
            version=version,
            tools=uniq_tools[:12] or ["terminal"],
            steps=uniq_steps[:16] or ["Execute the workflow with validated tool outputs."],
            source_trajectory_id=draft.source_trajectory_id,
            fingerprint=draft.fingerprint,
        )


class SkillSetManager:
    """
    Decide how to integrate a new skill draft into an existing skill set.
    """

    def __init__(self, *, teacher: Optional[TeacherRouter]) -> None:
        self.teacher = teacher

    def decide(
        self,
        *,
        candidate: SkillDraft,
        existing_skills: List[Dict[str, Any]],
        similar_skills: Optional[List[Dict[str, Any]]] = None,
    ) -> SkillDecision:
        if not existing_skills:
            return SkillDecision(action="add", target_slug="", reason="no_existing_skill")

        scoped = list(similar_skills or [])
        if not scoped:
            scoped = self._top_similar(candidate=candidate, existing_skills=existing_skills, limit=8)
        if self.teacher is not None and self.teacher.available():
            decision = self._decide_by_llm(candidate=candidate, similar=scoped)
            if decision is not None:
                return decision

        return self._fallback_decide(candidate=candidate, similar=scoped)

    def merge(self, *, candidate: SkillDraft, target: Dict[str, Any]) -> SkillDraft:
        if self.teacher is not None and self.teacher.available():
            merged = self._merge_by_llm(candidate=candidate, target=target)
            if merged is not None:
                return merged
        return self._fallback_merge(candidate=candidate, target=target)

    def _decide_by_llm(self, *, candidate: SkillDraft, similar: List[Dict[str, Any]]) -> Optional[SkillDecision]:
        system = (
            "You are AutoSkill-Agent's skill-set manager.\n"
            "Given a candidate skill and similar existing skills, choose exactly one action.\n"
            "Output strict JSON only:\n"
            "{\"action\":\"add|merge|discard|delete_existing\",\"target_slug\":\"...|\",\"reason\":\"...\"}\n"
            "Rules:\n"
            "- Prioritize quality and non-redundancy.\n"
            "- Choose merge when job-to-be-done is the same and candidate is an improvement.\n"
            "- Choose add only for clearly distinct reusable capability.\n"
            "- Choose discard if candidate is generic, noisy, or low confidence.\n"
            "- Choose delete_existing only if one existing skill is clearly obsolete/duplicate and candidate is better.\n"
            "- If uncertain, choose discard.\n"
            "- For merge/delete_existing, target_slug must be one slug from the provided list.\n"
            "- Keep reason short."
        )
        payload = {
            "candidate": self._compact_skill(candidate),
            "similar_existing_skills": [
                {
                    "slug": str(s.get("slug") or ""),
                    "name": str(s.get("name") or ""),
                    "description": str(s.get("description") or ""),
                    "tools": list(s.get("tools") or []),
                    "steps_preview": list(s.get("steps") or [])[:6],
                    "version": str(s.get("version") or ""),
                    "similarity": float(s.get("_similarity") or 0.0),
                }
                for s in similar
            ],
        }
        user = "Evaluate candidate skill against existing skills:\n" + json.dumps(payload, ensure_ascii=False)
        parsed = self.teacher.complete_json(system=system, user=user, temperature=0.0, task="skill_set_decision")
        if not isinstance(parsed, dict):
            return None
        action = str(parsed.get("action") or "").strip().lower()
        target = str(parsed.get("target_slug") or "").strip()
        reason = str(parsed.get("reason") or "").strip() or "llm_decision"
        allowed = {"add", "merge", "discard", "delete_existing"}
        if action not in allowed:
            return None
        allowed_targets = {str(s.get("slug") or "") for s in similar}
        if action in {"merge", "delete_existing"} and target not in allowed_targets:
            return None
        if action in {"add", "discard"}:
            target = ""
        return SkillDecision(action=action, target_slug=target, reason=reason)

    def _merge_by_llm(self, *, candidate: SkillDraft, target: Dict[str, Any]) -> Optional[SkillDraft]:
        system = (
            "You are AutoSkill-Agent's skill merge editor.\n"
            "Merge candidate skill into one target skill and output strict JSON only:\n"
            "{\"name\":\"...\",\"description\":\"...\",\"tools\":[...],\"steps\":[...]}\n"
            "Rules:\n"
            "- Keep one clean, reusable skill with no duplicated or contradictory instructions.\n"
            "- Preserve stable constraints and high-signal workflow steps from both sides.\n"
            "- Remove one-off details, environment-specific noise, and duplicate wording.\n"
            "- Keep the intent focused on one capability.\n"
            "- tools should be normalized and deduplicated.\n"
            "- steps should be concise, actionable, and deduplicated."
        )
        payload = {
            "target_skill": {
                "name": str(target.get("name") or ""),
                "description": str(target.get("description") or ""),
                "tools": list(target.get("tools") or []),
                "steps": list(target.get("steps") or []),
                "version": str(target.get("version") or ""),
            },
            "candidate_skill": self._compact_skill(candidate),
        }
        user = "Merge target and candidate into one final skill JSON:\n" + json.dumps(payload, ensure_ascii=False)
        parsed = self.teacher.complete_json(system=system, user=user, temperature=0.0, task="skill_merge")
        if not isinstance(parsed, dict):
            return None
        name = slugify(str(parsed.get("name") or target.get("name") or candidate.name))
        description = str(parsed.get("description") or "").strip()
        tools_raw = parsed.get("tools")
        steps_raw = parsed.get("steps")
        if not description or not isinstance(tools_raw, list) or not isinstance(steps_raw, list):
            return None
        tools = [normalize_tool_name(str(x)) for x in tools_raw if str(x).strip()]
        steps = [str(x).strip() for x in steps_raw if str(x).strip()]
        if not tools or not steps:
            return None
        return SkillDraft(
            name=name,
            description=description,
            version=str(target.get("version") or candidate.version or "1.0.0"),
            tools=self._dedupe_keep_order(tools)[:12],
            steps=self._dedupe_keep_order(steps)[:16],
            source_trajectory_id=candidate.source_trajectory_id,
            fingerprint=candidate.fingerprint,
        )

    def _fallback_decide(self, *, candidate: SkillDraft, similar: List[Dict[str, Any]]) -> SkillDecision:
        if len(candidate.steps) < 2 or len(candidate.description.strip()) < 12:
            return SkillDecision(action="discard", target_slug="", reason="low_signal_candidate")
        if not similar:
            return SkillDecision(action="add", target_slug="", reason="no_similar_existing")
        best = similar[0]
        best_score = float(best.get("_similarity") or 0.0)
        if best_score >= 0.72:
            return SkillDecision(action="merge", target_slug=str(best.get("slug") or ""), reason="high_similarity")
        if best_score <= 0.35:
            return SkillDecision(action="add", target_slug="", reason="distinct_capability")
        return SkillDecision(action="discard", target_slug="", reason="ambiguous_similarity")

    def _fallback_merge(self, *, candidate: SkillDraft, target: Dict[str, Any]) -> SkillDraft:
        target_name = slugify(str(target.get("name") or "agent-skill"))
        target_desc = str(target.get("description") or "").strip()
        merged_name = candidate.name if len(candidate.name) > len(target_name) + 6 else target_name
        merged_desc = candidate.description if len(candidate.description) > len(target_desc) else target_desc
        if not merged_desc:
            merged_desc = candidate.description or "Reusable multi-step agent workflow skill."
        tools = [normalize_tool_name(str(x)) for x in list(target.get("tools") or []) + list(candidate.tools)]
        steps = [str(x).strip() for x in list(target.get("steps") or []) + list(candidate.steps)]
        return SkillDraft(
            name=slugify(merged_name),
            description=merged_desc,
            version=str(target.get("version") or candidate.version or "1.0.0"),
            tools=self._dedupe_keep_order([x for x in tools if x])[:12] or ["terminal"],
            steps=self._dedupe_keep_order([x for x in steps if x])[:16]
            or ["Execute the workflow with validated tool outputs."],
            source_trajectory_id=candidate.source_trajectory_id,
            fingerprint=candidate.fingerprint,
        )

    def _compact_skill(self, draft: SkillDraft) -> Dict[str, Any]:
        return {
            "name": draft.name,
            "description": draft.description,
            "tools": list(draft.tools)[:12],
            "steps": list(draft.steps)[:16],
        }

    def _top_similar(
        self,
        *,
        candidate: SkillDraft,
        existing_skills: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        scored: List[Dict[str, Any]] = []
        for item in existing_skills:
            score = self._similarity(candidate, item)
            row = dict(item)
            row["_similarity"] = score
            scored.append(row)
        scored.sort(key=lambda x: float(x.get("_similarity") or 0.0), reverse=True)
        return scored[: max(1, int(limit))]

    def _similarity(self, candidate: SkillDraft, existing: Dict[str, Any]) -> float:
        c_name = self._tokenize(candidate.name)
        c_desc = self._tokenize(candidate.description)
        c_tools = {normalize_tool_name(x) for x in candidate.tools}
        c_steps = self._tokenize(" ".join(candidate.steps))
        e_name = self._tokenize(str(existing.get("name") or ""))
        e_desc = self._tokenize(str(existing.get("description") or ""))
        e_tools = {normalize_tool_name(str(x)) for x in list(existing.get("tools") or [])}
        e_steps = self._tokenize(" ".join([str(x) for x in list(existing.get("steps") or [])]))
        name_sim = self._jaccard(c_name, e_name)
        desc_sim = self._jaccard(c_desc, e_desc)
        tool_sim = self._jaccard(c_tools, e_tools)
        step_sim = self._jaccard(c_steps, e_steps)
        return 0.35 * name_sim + 0.35 * desc_sim + 0.15 * tool_sim + 0.15 * step_sim

    def _tokenize(self, text: str) -> set[str]:
        parts = re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", str(text or "").lower())
        return {x for x in parts if x}

    def _jaccard(self, a: set[str], b: set[str]) -> float:
        if not a or not b:
            return 0.0
        inter = len(a.intersection(b))
        union = len(a.union(b))
        return float(inter) / float(union) if union else 0.0

    def _dedupe_keep_order(self, values: List[str]) -> List[str]:
        out: List[str] = []
        seen = set()
        for v in values:
            key = str(v).strip()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(key)
        return out


class SkillEmbeddingRetriever:
    def __init__(
        self,
        *,
        state_dir: str,
        client: Optional[OpenAICompatEmbeddingClient],
        top_k: int = 8,
    ) -> None:
        self.client = client
        self.top_k = max(1, int(top_k))
        self.state_dir = os.path.abspath(os.path.expanduser(str(state_dir)))
        os.makedirs(self.state_dir, exist_ok=True)
        self.cache_path = os.path.join(self.state_dir, "skill_embedding_cache.json")
        self.cache = read_json(self.cache_path)

    def find_similar(
        self,
        *,
        candidate: SkillDraft,
        existing_skills: List[Dict[str, Any]],
        top_k: int = 0,
    ) -> List[Dict[str, Any]]:
        if self.client is None or not self.client.available():
            return []
        if not existing_skills:
            return []
        use_top_k = self.top_k if int(top_k) <= 0 else max(1, int(top_k))
        candidate_text = self._skill_to_text_from_draft(candidate)
        candidate_vectors = self.client.embed([candidate_text])
        if not candidate_vectors:
            return []
        candidate_vec = candidate_vectors[0]
        model_key = f"{self.client.base_url}|{self.client.model}"
        if str(self.cache.get("model_key") or "") != model_key:
            self.cache = {"model_key": model_key, "items": {}}
        items = self.cache.get("items")
        if not isinstance(items, dict):
            items = {}
            self.cache["items"] = items
        missing_slugs: List[str] = []
        missing_texts: List[str] = []
        scored: List[Dict[str, Any]] = []
        for skill in existing_skills:
            slug = str(skill.get("slug") or "").strip()
            if not slug:
                continue
            text = self._skill_to_text_from_existing(skill)
            text_hash = sha1_text(text)
            cached = items.get(slug)
            vector: Optional[List[float]] = None
            if isinstance(cached, dict) and str(cached.get("text_hash") or "") == text_hash:
                raw_vec = cached.get("vector")
                if isinstance(raw_vec, list):
                    try:
                        vector = [float(x) for x in raw_vec]
                    except Exception:
                        vector = None
            if vector is None:
                missing_slugs.append(slug)
                missing_texts.append(text)
            else:
                row = dict(skill)
                row["_similarity"] = self._cosine(candidate_vec, vector)
                row["_retrieval"] = "embedding"
                scored.append(row)
        if missing_texts:
            vectors = self._embed_in_batches(missing_texts, batch_size=16)
            for slug, text, vec in zip(missing_slugs, missing_texts, vectors):
                if not vec:
                    continue
                items[slug] = {"text_hash": sha1_text(text), "vector": vec}
                src = self._find_by_slug(existing_skills, slug)
                if src is None:
                    continue
                row = dict(src)
                row["_similarity"] = self._cosine(candidate_vec, vec)
                row["_retrieval"] = "embedding"
                scored.append(row)
            write_json(self.cache_path, self.cache)
        scored.sort(key=lambda x: float(x.get("_similarity") or 0.0), reverse=True)
        return scored[:use_top_k]

    def _embed_in_batches(self, texts: List[str], batch_size: int) -> List[List[float]]:
        out: List[List[float]] = []
        idx = 0
        while idx < len(texts):
            chunk = texts[idx : idx + batch_size]
            vectors = self.client.embed(chunk) if self.client else None
            if not vectors or len(vectors) != len(chunk):
                out.extend([[] for _ in chunk])
            else:
                out.extend(vectors)
            idx += batch_size
        return out

    def _skill_to_text_from_draft(self, draft: SkillDraft) -> str:
        return self._render_skill_text(
            name=draft.name,
            description=draft.description,
            tools=list(draft.tools),
            steps=list(draft.steps),
        )

    def _skill_to_text_from_existing(self, skill: Dict[str, Any]) -> str:
        return self._render_skill_text(
            name=str(skill.get("name") or ""),
            description=str(skill.get("description") or ""),
            tools=[str(x) for x in list(skill.get("tools") or [])],
            steps=[str(x) for x in list(skill.get("steps") or [])],
        )

    def _render_skill_text(self, *, name: str, description: str, tools: List[str], steps: List[str]) -> str:
        lines = [
            f"name: {str(name).strip()}",
            f"description: {str(description).strip()}",
            "tools: " + ", ".join([str(x).strip() for x in tools if str(x).strip()][:12]),
            "steps:",
        ]
        for s in [str(x).strip() for x in steps if str(x).strip()][:16]:
            lines.append("- " + s)
        return "\n".join(lines).strip()

    def _find_by_slug(self, rows: List[Dict[str, Any]], slug: str) -> Optional[Dict[str, Any]]:
        for row in rows:
            if str(row.get("slug") or "") == slug:
                return row
        return None

    def _cosine(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        n = min(len(a), len(b))
        if n <= 0:
            return 0.0
        dot = 0.0
        na = 0.0
        nb = 0.0
        for i in range(n):
            x = float(a[i])
            y = float(b[i])
            dot += x * y
            na += x * x
            nb += y * y
        if na <= 0.0 or nb <= 0.0:
            return 0.0
        return dot / (math.sqrt(na) * math.sqrt(nb))


class SkillDeployer:
    """
    Deploy generated skills to OpenClaw external skills directory.
    """

    def __init__(self, *, skills_dir: str, state_dir: str) -> None:
        self.skills_dir = os.path.abspath(os.path.expanduser(str(skills_dir)))
        self.state_dir = os.path.abspath(os.path.expanduser(str(state_dir)))
        self.index_path = os.path.join(self.state_dir, "skill_index.json")
        self.reload_flag = os.path.join(self.skills_dir, ".autoskill_reload")
        os.makedirs(self.skills_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        self._index = read_json(self.index_path)

    def list_skills(self) -> list[Dict[str, Any]]:
        out: list[Dict[str, Any]] = []
        by_slug = self._index.get("skills")
        if isinstance(by_slug, dict):
            for slug, meta in by_slug.items():
                item = self._read_skill_snapshot(str(slug), dict(meta) if isinstance(meta, dict) else {})
                if item is not None:
                    out.append(item)
        known = {str(x.get("slug") or "") for x in out}
        try:
            entries = sorted(os.listdir(self.skills_dir))
        except Exception:
            entries = []
        for entry in entries:
            if entry.startswith(".") or entry in known:
                continue
            path = os.path.join(self.skills_dir, entry)
            if not os.path.isdir(path):
                continue
            item = self._read_skill_snapshot(entry, {})
            if item is not None:
                out.append(item)
        return out

    def deploy(self, draft: SkillDraft, *, force_slug: str = "") -> Dict[str, Any]:
        fingerprints = self._index.get("fingerprints")
        if not isinstance(fingerprints, dict):
            fingerprints = {}
            self._index["fingerprints"] = fingerprints
        by_slug = self._index.get("skills")
        if not isinstance(by_slug, dict):
            by_slug = {}
            self._index["skills"] = by_slug
        slug = slugify(force_slug or draft.name)
        fp = str(draft.fingerprint or "").strip()
        existing_slug = ""
        if not force_slug and fp:
            existing_slug = str(fingerprints.get(fp) or "").strip()
        if existing_slug:
            slug = existing_slug
        skill_dir = os.path.join(self.skills_dir, slug)
        os.makedirs(skill_dir, exist_ok=True)
        md_path = os.path.join(skill_dir, "SKILL.md")
        old_md = ""
        old_meta: Dict[str, Any] = {}
        if os.path.isfile(md_path):
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    old_md = f.read()
                old_meta, _ = extract_frontmatter(old_md)
            except Exception:
                old_md = ""
                old_meta = {}
        version = draft.version
        if old_md:
            if old_md.strip() == render_skill_md(draft).strip():
                version = str(old_meta.get("version") or version or "1.0.0")
            else:
                version = bump_patch(str(old_meta.get("version") or "1.0.0"))
        final = SkillDraft(
            name=draft.name,
            description=draft.description,
            version=version,
            tools=draft.tools,
            steps=draft.steps,
            source_trajectory_id=draft.source_trajectory_id,
            fingerprint=draft.fingerprint,
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(render_skill_md(final))
        meta = {
            "name": final.name,
            "description": final.description,
            "version": final.version,
            "tools": list(final.tools),
            "fingerprint": final.fingerprint,
            "updated_at": now_iso(),
            "source_trajectory_id": final.source_trajectory_id,
        }
        with open(os.path.join(skill_dir, "autoskill_agent.meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        by_slug[slug] = meta
        if fp:
            fingerprints[fp] = slug
        write_json(self.index_path, self._index)
        try:
            with open(self.reload_flag, "w", encoding="utf-8") as f:
                f.write(now_iso())
        except Exception:
            pass
        return {"slug": slug, "path": skill_dir, "version": final.version}

    def delete_skill(self, slug: str) -> bool:
        target = slugify(slug)
        if not target:
            return False
        skill_dir = os.path.join(self.skills_dir, target)
        existed = os.path.isdir(skill_dir)
        if existed:
            try:
                shutil.rmtree(skill_dir)
            except Exception:
                return False
        by_slug = self._index.get("skills")
        if isinstance(by_slug, dict):
            by_slug.pop(target, None)
        fps = self._index.get("fingerprints")
        if isinstance(fps, dict):
            to_remove = [k for k, v in fps.items() if str(v) == target]
            for k in to_remove:
                fps.pop(k, None)
        write_json(self.index_path, self._index)
        try:
            with open(self.reload_flag, "w", encoding="utf-8") as f:
                f.write(now_iso())
        except Exception:
            pass
        return existed

    def _read_skill_snapshot(self, slug: str, meta: Dict[str, Any]) -> Dict[str, Any] | None:
        skill_dir = os.path.join(self.skills_dir, slug)
        md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(md_path):
            return None
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md = f.read()
        except Exception:
            return None
        front, body = extract_frontmatter(md)
        name = str(front.get("name") or meta.get("name") or slug).strip()
        description = str(front.get("description") or meta.get("description") or "").strip()
        version = str(front.get("version") or meta.get("version") or "1.0.0").strip() or "1.0.0"
        tools_raw = front.get("tools")
        tools = list(tools_raw) if isinstance(tools_raw, list) else list(meta.get("tools") or [])
        steps = self._parse_steps_from_body(body)
        return {
            "slug": slug,
            "name": name,
            "description": description,
            "version": version,
            "tools": tools,
            "steps": steps,
        }

    def _parse_steps_from_body(self, body: str) -> list[str]:
        out: list[str] = []
        for line in (body or "").splitlines():
            text = str(line).strip()
            if not text:
                continue
            if re.match(r"^\d+\.\s+", text):
                out.append(re.sub(r"^\d+\.\s+", "", text).strip())
        return out
