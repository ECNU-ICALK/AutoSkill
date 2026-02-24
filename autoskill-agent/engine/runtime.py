from __future__ import annotations

import os
from typing import Any, Dict

from engine.clients import OpenAICompatEmbeddingClient, OpenAICompatTeacher, TeacherRouter
from engine.core import append_jsonl, now_iso, read_json, write_json
from engine.monitor import ObservationMonitor
from engine.skill import SkillDeployer, SkillEmbeddingRetriever, SkillSetManager, SkillSynthesizer, SuccessEvaluator


class AutoSkillAgentRuntime:
    def __init__(
        self,
        *,
        workspace_dir: str,
        skills_dir: str,
        state_dir: str,
        trajectory_log_path: str,
        official_llm_url: str,
        official_llm_api_key: str,
        official_llm_model: str,
        extra_llm_url: str,
        extra_llm_api_key: str,
        extra_llm_model: str,
        llm_url: str,
        llm_api_key: str,
        llm_model: str,
        embedding_url: str,
        embedding_api_key: str,
        embedding_model: str,
        embedding_top_k: int = 8,
        min_success_score: float = 0.65,
    ) -> None:
        self.state_dir = os.path.abspath(os.path.expanduser(str(state_dir)))
        os.makedirs(self.state_dir, exist_ok=True)
        self.state_path = os.path.join(self.state_dir, "runtime_state.json")
        self.state = read_json(self.state_path)
        processed = self.state.get("processed_trajectory_ids")
        self.processed_trajectory_ids = set(processed if isinstance(processed, list) else [])

        monitor_state = self.state.get("monitor_state") if isinstance(self.state.get("monitor_state"), dict) else {}
        self.monitor = ObservationMonitor(workspace_dir=workspace_dir, state=monitor_state)
        teachers = self._build_teachers(
            official_llm_url=official_llm_url,
            official_llm_api_key=official_llm_api_key,
            official_llm_model=official_llm_model,
            extra_llm_url=extra_llm_url,
            extra_llm_api_key=extra_llm_api_key,
            extra_llm_model=extra_llm_model,
            llm_url=llm_url,
            llm_api_key=llm_api_key,
            llm_model=llm_model,
        )
        self.teacher_router = TeacherRouter(teachers)
        judge = self.teacher_router if self.teacher_router.available() else None
        self.evaluator = SuccessEvaluator(threshold=min_success_score, judge=judge)
        self.synthesizer = SkillSynthesizer(teacher=judge)
        self.manager = SkillSetManager(teacher=judge)
        self.deployer = SkillDeployer(skills_dir=skills_dir, state_dir=self.state_dir)
        embedding_client = self._build_embedding_client(
            embedding_url=embedding_url,
            embedding_api_key=embedding_api_key,
            embedding_model=embedding_model,
        )
        self.retriever = SkillEmbeddingRetriever(
            state_dir=self.state_dir,
            client=embedding_client,
            top_k=max(1, int(embedding_top_k)),
        )
        self.trajectory_log_path = os.path.abspath(os.path.expanduser(str(trajectory_log_path)))

    def run_once(self) -> Dict[str, Any]:
        captured = self.monitor.collect_new_trajectories()
        if not captured:
            self._save_state()
            return {"captured": 0, "successful": 0, "deployed": 0, "discarded": 0, "merged": 0, "deleted": 0}

        successful = 0
        deployed = 0
        discarded = 0
        merged = 0
        deleted = 0
        for traj in captured:
            if traj.trajectory_id in self.processed_trajectory_ids:
                continue

            score = self.evaluator.evaluate(traj)
            if not score.ok:
                self._mark_processed(traj.trajectory_id)
                continue
            successful += 1

            append_jsonl(
                self.trajectory_log_path,
                {
                    "captured_at": now_iso(),
                    "trajectory_id": traj.trajectory_id,
                    "source_file": traj.source_file,
                    "source_mtime": traj.source_mtime,
                    "success_score": score.score,
                    "success_reason": score.reason,
                    "user_instruction": traj.user_instruction,
                    "environment": traj.environment,
                    "messages": traj.messages,
                    "tool_calls": traj.tool_calls,
                },
            )

            draft = self.synthesizer.synthesize(traj)
            if draft is None:
                self._mark_processed(traj.trajectory_id)
                continue

            existing = self.deployer.list_skills()
            similar = self.retriever.find_similar(candidate=draft, existing_skills=existing, top_k=self.retriever.top_k)
            if similar:
                top = similar[0]
                print(
                    "[autoskill-agent] retrieved top skill:",
                    str(top.get("slug") or ""),
                    "score=" + f"{float(top.get('_similarity') or 0.0):.4f}",
                )
            decision = self.manager.decide(candidate=draft, existing_skills=existing, similar_skills=similar)
            action = str(decision.action or "discard")
            target_slug = str(decision.target_slug or "")

            if action == "discard":
                discarded += 1
                print(
                    "[autoskill-agent] discarded candidate:",
                    draft.name,
                    "reason=" + str(decision.reason or ""),
                    "from=" + traj.trajectory_id,
                )
                self._mark_processed(traj.trajectory_id)
                continue

            if action == "merge":
                target = self._find_target(existing, target_slug)
                if target is None:
                    discarded += 1
                    print(
                        "[autoskill-agent] discarded candidate due missing merge target:",
                        draft.name,
                        "target=" + target_slug,
                        "from=" + traj.trajectory_id,
                    )
                    self._mark_processed(traj.trajectory_id)
                    continue
                draft = self.manager.merge(candidate=draft, target=target)
                deploy_result = self.deployer.deploy(draft, force_slug=target_slug)
                merged += 1
            elif action == "delete_existing":
                if target_slug:
                    if self.deployer.delete_skill(target_slug):
                        deleted += 1
                deploy_result = self.deployer.deploy(draft)
            else:
                deploy_result = self.deployer.deploy(draft)
            deployed += 1
            print(
                "[autoskill-agent] deployed:",
                deploy_result.get("slug"),
                "version=" + str(deploy_result.get("version")),
                "action=" + action,
                "from=" + traj.trajectory_id,
            )
            self._mark_processed(traj.trajectory_id)

        self._save_state()
        return {
            "captured": len(captured),
            "successful": successful,
            "deployed": deployed,
            "discarded": discarded,
            "merged": merged,
            "deleted": deleted,
        }

    def _mark_processed(self, trajectory_id: str) -> None:
        self.processed_trajectory_ids.add(str(trajectory_id))

    def _save_state(self) -> None:
        self.state["processed_trajectory_ids"] = sorted(self.processed_trajectory_ids)
        self.state["monitor_state"] = self.monitor.export_state()
        write_json(self.state_path, self.state)

    def _build_teachers(
        self,
        *,
        official_llm_url: str,
        official_llm_api_key: str,
        official_llm_model: str,
        extra_llm_url: str,
        extra_llm_api_key: str,
        extra_llm_model: str,
        llm_url: str,
        llm_api_key: str,
        llm_model: str,
    ) -> list[OpenAICompatTeacher]:
        teachers: list[OpenAICompatTeacher] = []
        seen = set()

        def add_one(name: str, url: str, api_key: str, model: str) -> None:
            raw_url = str(url or "").strip().rstrip("/")
            raw_model = str(model or "").strip()
            if not raw_url or not raw_model:
                return
            if not raw_url.lower().endswith("/v1"):
                raw_url = raw_url + "/v1"
            dedup_key = (raw_url, raw_model)
            if dedup_key in seen:
                return
            seen.add(dedup_key)
            teachers.append(
                OpenAICompatTeacher(
                    base_url=raw_url,
                    api_key=str(api_key or ""),
                    model=raw_model,
                    name=name,
                )
            )

        add_one("official", official_llm_url, official_llm_api_key, official_llm_model)
        add_one("extra", extra_llm_url, extra_llm_api_key, extra_llm_model)
        add_one("legacy", llm_url, llm_api_key, llm_model)
        return teachers

    def _build_embedding_client(
        self,
        *,
        embedding_url: str,
        embedding_api_key: str,
        embedding_model: str,
    ) -> OpenAICompatEmbeddingClient | None:
        raw_url = str(embedding_url or "").strip().rstrip("/")
        raw_model = str(embedding_model or "").strip()
        if not raw_url or not raw_model:
            return None
        if not raw_url.lower().endswith("/v1"):
            raw_url = raw_url + "/v1"
        return OpenAICompatEmbeddingClient(
            base_url=raw_url,
            api_key=str(embedding_api_key or ""),
            model=raw_model,
            name="embedding",
        )

    def _find_target(self, existing: list[Dict[str, Any]], slug: str) -> Dict[str, Any] | None:
        target = str(slug or "").strip()
        for item in existing:
            if str(item.get("slug") or "").strip() == target:
                return item
        return None
