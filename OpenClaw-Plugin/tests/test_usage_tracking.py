from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "OpenClaw-Plugin"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openclaw_usage_tracking import (  # noqa: E402
    OpenClawSkillUsageTracker,
    OpenClawUsageTrackingConfig,
)


class _FakeStore:
    def __init__(self) -> None:
        self.rows: Dict[str, Dict[str, Dict[str, int]]] = {}
        self.last_prune_min: int = -1
        self.last_prune_max: int = -1

    def record_skill_usage_judgments(
        self,
        *,
        user_id: str,
        judgments: List[Dict[str, Any]],
        prune_min_retrieved: int = 0,
        prune_max_used: int = 0,
    ) -> Dict[str, Any]:
        self.last_prune_min = int(prune_min_retrieved)
        self.last_prune_max = int(prune_max_used)
        bucket = self.rows.setdefault(str(user_id), {})
        updated = 0
        for item in judgments:
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
        bucket = dict(self.rows.get(str(user_id), {}))
        if skill_id:
            row = bucket.get(str(skill_id), None)
            return {"skills": {str(skill_id): row} if isinstance(row, dict) else {}}
        return {"skills": bucket}


class _FakeSDK:
    def __init__(self) -> None:
        self.store = _FakeStore()


class OpenClawUsageTrackingTest(unittest.TestCase):
    def test_remember_then_record_uses_cached_retrieval(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(enabled=True).normalize(),
        )
        remember = tracker.remember_retrieval(
            user_id="u1",
            session_id="s1",
            retrieval={
                "query": "release checklist",
                "hits": [
                    {"id": "skill-a", "name": "A"},
                    {"id": "skill-b", "name": "B"},
                ],
                "selected_for_context_ids": ["skill-a"],
                "selected_for_use_ids": ["skill-a"],
            },
        )
        self.assertEqual(remember["status"], "remembered")

        recorded = tracker.record_agent_end(
            user_id="u1",
            session_id="s1",
            retrieval=None,
            used_skill_ids=["skill-a"],
        )
        self.assertEqual(recorded["status"], "recorded")
        self.assertEqual(recorded["updated"], 2)
        self.assertEqual(recorded["source"], "before_agent_start_cache")
        stats = tracker.get_stats(user_id="u1")
        self.assertEqual(stats["skills"]["skill-a"]["used"], 1)
        self.assertEqual(stats["skills"]["skill-b"]["used"], 0)

    def test_agent_end_payload_retrieval_overrides_cached_snapshot(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(enabled=True).normalize(),
        )
        tracker.remember_retrieval(
            user_id="u1",
            session_id="s2",
            retrieval={
                "query": "old",
                "hits": [{"id": "skill-old"}],
                "selected_for_context_ids": ["skill-old"],
            },
        )
        recorded = tracker.record_agent_end(
            user_id="u1",
            session_id="s2",
            retrieval={
                "query": "new",
                "hits": [{"id": "skill-new"}],
                "selected_for_context_ids": ["skill-new"],
            },
            used_skill_ids=["skill-new"],
        )
        self.assertEqual(recorded["status"], "recorded")
        self.assertEqual(recorded["source"], "agent_end_payload")
        stats = tracker.get_stats(user_id="u1")
        self.assertIn("skill-new", stats["skills"])
        self.assertNotIn("skill-old", stats["skills"])

    def test_disabled_tracker_is_strict_noop(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(enabled=False).normalize(),
        )
        remember = tracker.remember_retrieval(
            user_id="u1",
            session_id="s3",
            retrieval={"hits": [{"id": "skill-a"}]},
        )
        recorded = tracker.record_agent_end(
            user_id="u1",
            session_id="s3",
            retrieval=None,
            used_skill_ids=["skill-a"],
        )
        self.assertEqual(remember["status"], "skipped")
        self.assertEqual(recorded["status"], "skipped")
        self.assertEqual(sdk.store.rows, {})

    def test_prune_requires_explicit_used_signal_by_default(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(
                enabled=True,
                prune_enabled=True,
                prune_min_retrieved=40,
                prune_max_used=0,
            ).normalize(),
        )
        tracker.remember_retrieval(
            user_id="u1",
            session_id="s4",
            retrieval={
                "query": "release checklist",
                "hits": [{"id": "skill-a"}],
                "selected_for_context_ids": ["skill-a"],
            },
        )
        no_used = tracker.record_agent_end(
            user_id="u1",
            session_id="s4",
            retrieval=None,
            used_skill_ids=[],
        )
        self.assertEqual(no_used["status"], "recorded")
        self.assertEqual(no_used["prune_applied"], False)
        self.assertEqual(sdk.store.last_prune_min, 0)
        self.assertEqual(sdk.store.last_prune_max, 0)

        tracker.remember_retrieval(
            user_id="u1",
            session_id="s5",
            retrieval={
                "query": "release checklist",
                "hits": [{"id": "skill-a"}],
                "selected_for_context_ids": ["skill-a"],
            },
        )
        with_used = tracker.record_agent_end(
            user_id="u1",
            session_id="s5",
            retrieval=None,
            used_skill_ids=["skill-a"],
        )
        self.assertEqual(with_used["status"], "recorded")
        self.assertEqual(with_used["prune_applied"], True)
        self.assertEqual(sdk.store.last_prune_min, 40)
        self.assertEqual(sdk.store.last_prune_max, 0)

    def test_records_with_explicit_used_fallback_when_retrieval_missing(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(enabled=True).normalize(),
        )
        recorded = tracker.record_agent_end(
            user_id="u1",
            session_id="s6",
            retrieval=None,
            used_skill_ids=["skill-fallback-1"],
        )
        self.assertEqual(recorded["status"], "recorded")
        self.assertEqual(recorded["source"], "explicit_used_fallback")
        stats = tracker.get_stats(user_id="u1")
        self.assertIn("skill-fallback-1", stats["skills"])
        self.assertEqual(stats["skills"]["skill-fallback-1"]["used"], 1)

    def test_records_inferred_usage_when_explicit_used_is_missing(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(enabled=True).normalize(),
        )
        recorded = tracker.record_agent_end(
            user_id="u1",
            session_id="s7",
            retrieval={
                "query": "rollback steps",
                "hits": [{"id": "skill-rb", "name": "Rollback Steps"}],
                "selected_for_use_ids": ["skill-rb"],
            },
            used_skill_ids=[],
            inferred_used_skill_ids=["skill-rb"],
            messages=[
                {"role": "user", "content": "Need rollback now"},
                {"role": "assistant", "content": "Use rollback steps."},
            ],
        )
        self.assertEqual(recorded["status"], "recorded")
        self.assertEqual(recorded["usage_inference"]["status"], "recorded")
        self.assertIn("skill-rb", recorded["usage_inference"]["stats"])

        stats = tracker.get_stats(user_id="u1")
        self.assertIn("skills_inferred", stats)
        self.assertIn("skill-rb", stats["skills_inferred"])
        self.assertGreaterEqual(stats["skills_inferred"]["skill-rb"]["used"], 1)
        self.assertIn("skills_combined", stats)
        self.assertIn("skill-rb", stats["skills_combined"])

    def test_inference_skips_when_explicit_used_present(self) -> None:
        sdk = _FakeSDK()
        tracker = OpenClawSkillUsageTracker(
            sdk=sdk,
            config=OpenClawUsageTrackingConfig(enabled=True).normalize(),
        )
        recorded = tracker.record_agent_end(
            user_id="u1",
            session_id="s8",
            retrieval={
                "query": "release checklist",
                "hits": [{"id": "skill-a", "name": "A"}],
                "selected_for_use_ids": ["skill-a"],
            },
            used_skill_ids=["skill-a"],
            inferred_used_skill_ids=["skill-a"],
        )
        self.assertEqual(recorded["status"], "recorded")
        self.assertEqual(recorded["usage_inference"]["status"], "skipped")
        self.assertEqual(recorded["usage_inference"]["reason"], "explicit_used_present")


if __name__ == "__main__":
    unittest.main()
