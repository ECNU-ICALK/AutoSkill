from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "AutoSkill4OpenClaw"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openclaw_conversation_archive import (  # noqa: E402
    OpenClawConversationArchive,
    OpenClawConversationArchiveConfig,
)


class OpenClawConversationArchiveTest(unittest.TestCase):
    def test_sweep_is_noop_when_idle_timeout_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = OpenClawConversationArchive(
                config=OpenClawConversationArchiveConfig(
                    enabled=True,
                    archive_dir=tmp,
                    session_idle_timeout_seconds=0,
                ).normalize()
            )
            archive.append_session_record(
                user_id="u1",
                session_id="s1",
                turn_type="main",
                messages=[
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "world"},
                ],
                session_done=False,
                success=True,
            )
            swept = archive.sweep_inactive_sessions(user_id="u1")
            self.assertTrue(swept["skipped"])
            self.assertEqual(swept["reason"], "idle_timeout_disabled")
            self.assertEqual(len(list(swept.get("ended_sessions") or [])), 0)

    def test_sweep_closes_expired_active_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = OpenClawConversationArchive(
                config=OpenClawConversationArchiveConfig(
                    enabled=True,
                    archive_dir=tmp,
                    session_idle_timeout_seconds=1,
                ).normalize()
            )
            archive.append_session_record(
                user_id="u1",
                session_id="s-timeout",
                turn_type="main",
                messages=[
                    {"role": "user", "content": "task"},
                    {"role": "assistant", "content": "done"},
                ],
                session_done=False,
                success=True,
            )
            archive._active_session_touch_ms["u1"] = 1  # type: ignore[attr-defined]
            swept = archive.sweep_inactive_sessions(user_id="u1")
            ended = list(swept.get("ended_sessions") or [])
            self.assertFalse(swept["skipped"])
            self.assertEqual(len(ended), 1)
            self.assertEqual(str(ended[0].get("session_id") or ""), "s-timeout")
            self.assertEqual(str(ended[0].get("reason") or ""), "session_idle_timeout")
            ended_path = Path(str(ended[0].get("path") or ""))
            self.assertTrue(ended_path.exists())


if __name__ == "__main__":
    unittest.main()
