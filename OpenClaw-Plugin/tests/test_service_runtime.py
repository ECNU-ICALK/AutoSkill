from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "OpenClaw-Plugin"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from autoskill.interactive.server import AutoSkillProxyConfig  # noqa: E402
from openclaw_conversation_archive import OpenClawConversationArchiveConfig  # noqa: E402
from openclaw_main_turn_proxy import OpenClawMainTurnProxyConfig  # noqa: E402
from openclaw_skill_mirror import OpenClawSkillInstallConfig  # noqa: E402
from service_runtime import OpenClawSkillRuntime  # noqa: E402


class _FakeSDK:
    class _Store:
        def __init__(self) -> None:
            self.rows: Dict[str, Dict[str, Dict[str, int]]] = {}

        def record_skill_usage_judgments(
            self,
            *,
            user_id: str,
            judgments: List[Dict[str, Any]],
            prune_min_retrieved: int = 0,
            prune_max_used: int = 0,
        ) -> Dict[str, Any]:
            _ = prune_min_retrieved
            _ = prune_max_used
            uid = str(user_id or "").strip()
            bucket = self.rows.setdefault(uid, {})
            updated = 0
            for item in list(judgments or []):
                sid = str(item.get("id") or "").strip()
                if not sid:
                    continue
                row = bucket.setdefault(sid, {"retrieved": 0, "relevant": 0, "used": 0})
                row["retrieved"] += 1
                if bool(item.get("relevant", False)):
                    row["relevant"] += 1
                if bool(item.get("used", False)):
                    row["used"] += 1
                updated += 1
            return {"updated": updated, "deleted_skill_ids": [], "stats": dict(bucket)}

        def get_skill_usage_stats(self, *, user_id: str, skill_id: str = "") -> Dict[str, Any]:
            uid = str(user_id or "").strip()
            sid = str(skill_id or "").strip()
            bucket = dict(self.rows.get(uid) or {})
            if sid:
                row = bucket.get(sid)
                return {"skills": ({sid: row} if isinstance(row, dict) else {})}
            return {"skills": bucket}

    def __init__(self) -> None:
        self.store = self._Store()

    def ingest(self, *, user_id: str, messages: List[Dict[str, Any]], metadata: Dict[str, Any], hint: str | None = None) -> List[Any]:
        return []


class OpenClawServiceRuntimeTest(unittest.TestCase):
    def _make_runtime(
        self,
        *,
        archive_dir: str,
        main_turn_enabled: bool = False,
        target_base_url: str = "",
        session_idle_timeout_s: int = 0,
    ) -> OpenClawSkillRuntime:
        return OpenClawSkillRuntime(
            sdk=_FakeSDK(),
            llm_config={"provider": "mock", "response": ""},
            embeddings_config={"provider": "hashing", "dims": 32},
            config=AutoSkillProxyConfig(
                user_id="u-test",
                extract_enabled=True,
                ingest_window=6,
                top_k=1,
            ).normalize(),
            main_turn_proxy_config=OpenClawMainTurnProxyConfig(
                enabled=main_turn_enabled,
                target_base_url=target_base_url,
                ingest_window=6,
                agent_end_extract_enabled=True,
            ).normalize(),
            skill_install_config=OpenClawSkillInstallConfig(mode="store_only").normalize(),
            conversation_archive_config=OpenClawConversationArchiveConfig(
                enabled=True,
                archive_dir=archive_dir,
                session_idle_timeout_seconds=int(session_idle_timeout_s),
            ).normalize(),
        )

    def _read_archive_lines(self, archive_dir: str) -> List[Dict[str, Any]]:
        files = [
            p
            for p in Path(archive_dir).rglob("*.jsonl")
            if "sessions" not in p.parts
        ]
        self.assertEqual(len(files), 1)
        lines = [line for line in files[0].read_text(encoding="utf-8").splitlines() if line.strip()]
        return [json.loads(line) for line in lines]

    def test_agent_end_archives_and_skips_non_main_turn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: (_ for _ in ()).throw(AssertionError("retrieve should not run"))  # type: ignore[attr-defined]
            runtime._schedule_extraction_job = lambda **_: (_ for _ in ()).throw(AssertionError("schedule should not run"))  # type: ignore[attr-defined]

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-side",
                    "turn_type": "side",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "Need a tool call."},
                        {"role": "assistant", "content": "Calling tool."},
                    ],
                },
                headers={},
            )

            self.assertEqual(payload["extraction"]["status"], "skipped")
            self.assertEqual(payload["extraction"]["reason"], "session_not_finished")
            archived = self._read_archive_lines(tmp)
            self.assertEqual(archived[0]["metadata"]["turn_type"], "side")
            self.assertEqual(archived[0]["metadata"]["session_id"], "sess-side")

    def test_agent_end_first_main_turn_only_stages_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: (_ for _ in ()).throw(AssertionError("retrieve should not run"))  # type: ignore[attr-defined]
            scheduled: List[Dict[str, Any]] = []

            def _schedule(**kwargs: Any) -> str:
                scheduled.append(dict(kwargs))
                return "job-1"

            runtime._schedule_extraction_job = _schedule  # type: ignore[assignment]

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-main",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "Write a report."},
                        {"role": "assistant", "content": "Draft report."},
                    ],
                },
                headers={},
            )

            self.assertEqual(payload["extraction"]["status"], "skipped")
            self.assertEqual(payload["extraction"]["reason"], "session_not_finished")
            self.assertEqual(len(scheduled), 0)
            archived = self._read_archive_lines(tmp)
            self.assertEqual(archived[0]["metadata"]["turn_type"], "main")

    def test_agent_end_schedules_when_session_id_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: {"hits": []}  # type: ignore[attr-defined]
            scheduled: List[Dict[str, Any]] = []

            def _schedule(**kwargs: Any) -> str:
                scheduled.append(dict(kwargs))
                return "job-fallback"

            runtime._schedule_extraction_job = _schedule  # type: ignore[assignment]

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-main-a",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "Write a report."},
                        {"role": "assistant", "content": "Draft report."},
                    ],
                },
                headers={},
            )
            self.assertEqual(payload["extraction"]["status"], "skipped")
            self.assertEqual(payload["extraction"]["reason"], "session_not_finished")
            self.assertEqual(len(scheduled), 0)

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-main-b",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "Start a new topic."},
                        {"role": "assistant", "content": "Working on it."},
                    ],
                },
                headers={},
            )

            self.assertEqual(payload["extraction"]["status"], "scheduled")
            self.assertEqual(len(scheduled), 1)
            self.assertEqual(scheduled[0]["trigger"], "openclaw_agent_end_session_end")
            self.assertEqual(scheduled[0]["metadata"]["session_id"], "sess-main-a")

    def test_agent_end_skips_session_end_extraction_when_main_turn_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: (_ for _ in ()).throw(AssertionError("retrieve should not run"))  # type: ignore[attr-defined]
            runtime._schedule_extraction_job = lambda **_: (_ for _ in ()).throw(AssertionError("schedule should not run"))  # type: ignore[attr-defined]

            runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-dedupe-a",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "task A"},
                        {"role": "assistant", "content": "done A"},
                    ],
                },
                headers={},
            )
            runtime._record_extraction_event(
                user_id="u-test",
                event={
                    "job_id": "job-main-turn-1",
                    "trigger": "openclaw_main_turn_proxy",
                    "status": "completed",
                    "session_id": "sess-dedupe-a",
                },
            )
            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-dedupe-b",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "task B"},
                        {"role": "assistant", "content": "done B"},
                    ],
                },
                headers={},
            )
            self.assertEqual(payload["extraction"]["status"], "skipped")
            self.assertIn("dedupe_main_turn_already_extracted", payload["extraction"]["reason"])

    def test_agent_end_schedules_when_previous_session_is_closed_by_idle_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(
                archive_dir=tmp,
                session_idle_timeout_s=1,
            )
            runtime._retrieve_context = lambda **_: {"hits": []}  # type: ignore[attr-defined]
            scheduled: List[Dict[str, Any]] = []

            def _schedule(**kwargs: Any) -> str:
                scheduled.append(dict(kwargs))
                return f"job-timeout-{len(scheduled)}"

            runtime._schedule_extraction_job = _schedule  # type: ignore[assignment]

            first = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-timeout-a",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "old task"},
                        {"role": "assistant", "content": "old answer"},
                    ],
                },
                headers={},
            )
            self.assertEqual(first["extraction"]["status"], "skipped")
            self.assertEqual(first["extraction"]["reason"], "session_not_finished")
            self.assertEqual(len(scheduled), 0)

            runtime._conversation_archive._active_session_touch_ms["u-test"] = 1  # type: ignore[attr-defined]
            second = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-timeout-a",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "follow-up task"},
                        {"role": "assistant", "content": "follow-up answer"},
                    ],
                },
                headers={},
            )
            self.assertEqual(second["extraction"]["status"], "scheduled")
            self.assertEqual(len(scheduled), 1)
            self.assertEqual(scheduled[0]["metadata"]["session_id"], "sess-timeout-a")
            self.assertEqual(scheduled[0]["metadata"]["source"], "openclaw_agent_end_session_end")

    def test_agent_end_falls_back_to_session_end_extraction_when_main_turn_enabled_but_target_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(
                archive_dir=tmp,
                main_turn_enabled=True,
                target_base_url="",
            )
            runtime._retrieve_context = lambda **_: {"hits": []}  # type: ignore[attr-defined]
            scheduled: List[Dict[str, Any]] = []

            def _schedule(**kwargs: Any) -> str:
                scheduled.append(dict(kwargs))
                return "job-fallback"

            runtime._schedule_extraction_job = _schedule  # type: ignore[assignment]

            runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-fallback-a",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "Write a report."},
                        {"role": "assistant", "content": "Draft report."},
                    ],
                },
                headers={},
            )
            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-fallback-b",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "new session"},
                        {"role": "assistant", "content": "ok"},
                    ],
                },
                headers={},
            )
            self.assertEqual(payload["extraction"]["status"], "scheduled")
            self.assertEqual(len(scheduled), 1)

    def test_agent_end_schedules_when_session_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: {"hits": []}  # type: ignore[attr-defined]
            scheduled: List[Dict[str, Any]] = []

            def _schedule(**kwargs: Any) -> str:
                scheduled.append(dict(kwargs))
                return "job-done"

            runtime._schedule_extraction_job = _schedule  # type: ignore[assignment]

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-done",
                    "turn_type": "main",
                    "session_done": True,
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "finish task"},
                        {"role": "assistant", "content": "done"},
                    ],
                },
                headers={},
            )
            self.assertEqual(payload["extraction"]["status"], "scheduled")
            self.assertEqual(len(scheduled), 1)

    def test_agent_end_still_waits_for_session_end_when_main_turn_proxy_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(
                archive_dir=tmp,
                main_turn_enabled=True,
                target_base_url="http://127.0.0.1:8000/v1",
            )
            runtime._retrieve_context = lambda **_: (_ for _ in ()).throw(AssertionError("retrieve should not run"))  # type: ignore[attr-defined]
            runtime._schedule_extraction_job = lambda **_: (_ for _ in ()).throw(AssertionError("schedule should not run"))  # type: ignore[attr-defined]

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-proxy",
                    "turn_type": "main",
                    "success": True,
                    "messages": [
                        {"role": "user", "content": "Do the task."},
                        {"role": "assistant", "content": "Done."},
                    ],
                },
                headers={},
            )

            self.assertEqual(payload["extraction"]["status"], "skipped")
            self.assertEqual(payload["extraction"]["reason"], "session_not_finished")
            archived = self._read_archive_lines(tmp)
            self.assertEqual(archived[0]["metadata"]["source"], "openclaw_agent_end")

    def test_usage_tracking_stats_endpoint_and_agent_end_accounting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: {"hits": []}  # type: ignore[attr-defined]
            runtime._schedule_extraction_job = lambda **_: "job-x"  # type: ignore[assignment]

            runtime.openclaw_before_agent_start_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-usage",
                    "scope": "user",
                    "messages": [{"role": "user", "content": "Need release checklist"}],
                },
                headers={},
            )
            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-usage",
                    "session_done": True,
                    "turn_type": "main",
                    "success": True,
                    "used_skill_ids": ["skill-1"],
                    "retrieval": {
                        "query": "release checklist",
                        "hits": [{"id": "skill-1", "name": "Release Checklist", "score": 0.9}],
                        "selected_for_context_ids": ["skill-1"],
                        "selected_for_use_ids": ["skill-1"],
                    },
                    "messages": [
                        {"role": "user", "content": "Need release checklist"},
                        {"role": "assistant", "content": "Using checklist"},
                    ],
                },
                headers={},
            )
            self.assertEqual(payload["usage"]["status"], "recorded")
            self.assertIn("usage_inference", payload["usage"])
            stats = runtime.openclaw_usage_stats_api(
                body={"user": "u-test"},
                headers={},
            )
            self.assertTrue(stats["data"]["enabled"])
            self.assertIn("skill-1", stats["data"]["skills"])
            self.assertIn("skills_explicit", stats["data"])
            self.assertIn("skills_inferred", stats["data"])
            self.assertIn("skills_combined", stats["data"])

    def test_usage_tracking_inferred_fallback_without_retrieval_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            runtime._retrieve_context = lambda **_: {"hits": []}  # type: ignore[attr-defined]
            runtime._schedule_extraction_job = lambda **_: "job-infer"  # type: ignore[assignment]

            payload = runtime.openclaw_agent_end_api(
                body={
                    "user": "u-test",
                    "session_id": "sess-infer-only",
                    "session_done": True,
                    "turn_type": "main",
                    "success": True,
                    "inferred_used_skill_ids": ["skill-infer-1"],
                    "messages": [
                        {"role": "user", "content": "Need rollback plan"},
                        {"role": "assistant", "content": "I will follow rollback plan"},
                    ],
                },
                headers={},
            )
            self.assertEqual(payload["usage"]["status"], "recorded")
            self.assertEqual(payload["usage"]["source"], "inferred_used_fallback")
            self.assertEqual(payload["usage"]["usage_inference"]["status"], "recorded")

            stats = runtime.openclaw_usage_stats_api(body={"user": "u-test"}, headers={})
            inferred = dict(stats["data"].get("skills_inferred") or {})
            combined = dict(stats["data"].get("skills_combined") or {})
            self.assertIn("skill-infer-1", inferred)
            self.assertGreaterEqual(int(inferred["skill-infer-1"]["used"]), 1)
            self.assertIn("skill-infer-1", combined)
            self.assertGreaterEqual(int(combined["skill-infer-1"]["used"]), 1)

    def test_openclaw_schedule_dedupe_skips_duplicate_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = self._make_runtime(archive_dir=tmp)
            window = [
                {"role": "user", "content": "do release"},
                {"role": "assistant", "content": "release steps"},
            ]
            metadata = {
                "source": "openclaw_agent_end_session_end",
                "session_id": "sess-dedupe-window",
            }

            job1 = runtime._schedule_extraction_job(  # type: ignore[attr-defined]
                user_id="u-test",
                messages=window,
                trigger="openclaw_agent_end_session_end",
                metadata=metadata,
            )
            event1 = runtime._get_extraction_event_by_job(job_id=job1)
            self.assertIn(str((event1 or {}).get("status") or ""), {"scheduled", "running", "completed"})

            job2 = runtime._schedule_extraction_job(  # type: ignore[attr-defined]
                user_id="u-test",
                messages=window,
                trigger="openclaw_agent_end_session_end",
                metadata=metadata,
            )
            event2 = runtime._get_extraction_event_by_job(job_id=job2)
            self.assertEqual(str((event2 or {}).get("status") or ""), "skipped")
            self.assertEqual(str((event2 or {}).get("error") or ""), "dedupe_skipped")


if __name__ == "__main__":
    unittest.main()
