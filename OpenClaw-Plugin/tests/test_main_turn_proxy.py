from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "OpenClaw-Plugin"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openclaw_main_turn_proxy import (  # noqa: E402
    AssistantCapture,
    OpenClawMainTurnProxyConfig,
    OpenClawMainTurnStateManager,
    StreamAssistantAccumulator,
    UpstreamChatProxy,
    _copy_headers_to_client,
    parse_turn_context,
)


class _RecordingScheduler:
    def __init__(self) -> None:
        self.samples: List[Any] = []

    def __call__(self, sample: Any) -> str:
        self.samples.append(sample)
        return f"job-{len(self.samples)}"


class _FakeHandler:
    def __init__(self) -> None:
        self.status = 0
        self.headers: List[tuple[str, str]] = []
        self.wfile = io.BytesIO()

    def send_response(self, status: int) -> None:
        self.status = int(status)

    def send_header(self, key: str, value: str) -> None:
        self.headers.append((str(key), str(value)))

    def end_headers(self) -> None:
        return None


class MainTurnProxyStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.scheduler = _RecordingScheduler()
        self.cfg = OpenClawMainTurnProxyConfig(enabled=True, ingest_window=6).normalize()
        self.manager = OpenClawMainTurnStateManager(config=self.cfg, schedule_extraction=self.scheduler)

    def _ctx(
        self,
        *,
        session_id: str,
        turn_type: str,
        messages: List[Dict[str, Any]],
        session_done: bool = False,
    ) -> Any:
        return parse_turn_context(
            body={
                "session_id": session_id,
                "turn_type": turn_type,
                "session_done": session_done,
                "messages": messages,
            },
            headers={},
            default_user_id="u-test",
            ingest_window=self.cfg.ingest_window,
        )

    def _run_turn(
        self,
        ctx: Any,
        *,
        assistant_text: Optional[str],
        success: bool = True,
        error: str = "",
    ) -> None:
        assistant = None if assistant_text is None else AssistantCapture(role="assistant", content=assistant_text)
        with self.manager.session_guard(ctx.session_id):
            self.manager.prepare_request(ctx)
            self.manager.finalize_request(ctx=ctx, assistant=assistant, success=success, error=error)

    def test_side_turn_does_not_schedule_extraction(self) -> None:
        ctx = self._ctx(
            session_id="s-side",
            turn_type="side",
            messages=[{"role": "user", "content": "hello"}],
        )
        self._run_turn(ctx, assistant_text="side reply")
        self.assertEqual(len(self.scheduler.samples), 0)
        self.assertNotIn("s-side", self.manager._pending_by_session)

    def test_main_turn_first_request_only_caches_pending(self) -> None:
        ctx = self._ctx(
            session_id="s-main",
            turn_type="main",
            messages=[{"role": "user", "content": "write a plan"}],
        )
        self._run_turn(ctx, assistant_text="plan drafted")
        self.assertEqual(len(self.scheduler.samples), 0)
        pending = self.manager._pending_by_session.get("s-main")
        self.assertIsNotNone(pending)
        self.assertEqual(pending.turn_index, 1)
        self.assertEqual(pending.assistant_message["content"], "plan drafted")

    def test_next_user_request_flushes_previous_main_turn(self) -> None:
        first = self._ctx(
            session_id="s-user",
            turn_type="main",
            messages=[{"role": "user", "content": "draft summary"}],
        )
        self._run_turn(first, assistant_text="summary v1")

        second = self._ctx(
            session_id="s-user",
            turn_type="side",
            messages=[
                {"role": "assistant", "content": "summary v1"},
                {"role": "user", "content": "make it shorter"},
            ],
        )
        with self.manager.session_guard(second.session_id):
            flush = self.manager.prepare_request(second)
            self.manager.finalize_request(ctx=second, assistant=None, success=True)

        self.assertEqual(flush.status, "scheduled")
        self.assertEqual(len(self.scheduler.samples), 1)
        sample = self.scheduler.samples[0]
        self.assertEqual(sample.metadata["next_state_role"], "user")
        self.assertEqual(sample.messages[-1]["content"], "make it shorter")
        self.assertNotIn("s-user", self.manager._pending_by_session)

    def test_next_tool_request_flushes_previous_main_turn(self) -> None:
        first = self._ctx(
            session_id="s-tool",
            turn_type="main",
            messages=[{"role": "user", "content": "run a check"}],
        )
        self._run_turn(first, assistant_text="calling tool now")

        second = self._ctx(
            session_id="s-tool",
            turn_type="side",
            messages=[
                {"role": "assistant", "content": "calling tool now"},
                {"role": "tool", "content": "{\"status\":\"ok\"}"},
            ],
        )
        with self.manager.session_guard(second.session_id):
            flush = self.manager.prepare_request(second)
            self.manager.finalize_request(ctx=second, assistant=None, success=True)

        self.assertEqual(flush.status, "scheduled")
        self.assertEqual(len(self.scheduler.samples), 1)
        self.assertEqual(self.scheduler.samples[0].metadata["next_state_role"], "tool")
        self.assertEqual(self.scheduler.samples[0].messages[-1]["role"], "tool")

    def test_session_done_cleans_pending_when_no_next_state(self) -> None:
        first = self._ctx(
            session_id="s-done",
            turn_type="main",
            messages=[{"role": "user", "content": "final answer"}],
        )
        self._run_turn(first, assistant_text="done")
        self.assertIn("s-done", self.manager._pending_by_session)

        second = self._ctx(
            session_id="s-done",
            turn_type="side",
            session_done=True,
            messages=[{"role": "assistant", "content": "done"}],
        )
        with self.manager.session_guard(second.session_id):
            flush = self.manager.prepare_request(second)
            self.manager.finalize_request(ctx=second, assistant=None, success=True)

        self.assertEqual(flush.reason, "session_done_without_next_state")
        self.assertNotIn("s-done", self.manager._pending_by_session)

    def test_sessions_are_isolated(self) -> None:
        a = self._ctx(session_id="s-a", turn_type="main", messages=[{"role": "user", "content": "task a"}])
        b = self._ctx(session_id="s-b", turn_type="main", messages=[{"role": "user", "content": "task b"}])
        self._run_turn(a, assistant_text="answer a")
        self._run_turn(b, assistant_text="answer b")

        flush_a = self._ctx(
            session_id="s-a",
            turn_type="side",
            messages=[
                {"role": "assistant", "content": "answer a"},
                {"role": "user", "content": "revise a"},
            ],
        )
        with self.manager.session_guard(flush_a.session_id):
            self.manager.prepare_request(flush_a)
            self.manager.finalize_request(ctx=flush_a, assistant=None, success=True)

        self.assertEqual(len(self.scheduler.samples), 1)
        self.assertNotIn("s-a", self.manager._pending_by_session)
        self.assertIn("s-b", self.manager._pending_by_session)

    def test_dedupe_skips_repeated_flush(self) -> None:
        first = self._ctx(
            session_id="s-dedupe",
            turn_type="main",
            messages=[{"role": "user", "content": "prepare checklist"}],
        )
        self._run_turn(first, assistant_text="checklist v1")
        pending = self.manager._pending_by_session.get("s-dedupe")
        self.assertIsNotNone(pending)

        second = self._ctx(
            session_id="s-dedupe",
            turn_type="side",
            messages=[
                {"role": "assistant", "content": "checklist v1"},
                {"role": "user", "content": "add rollback checks"},
            ],
        )
        with self.manager.session_guard(second.session_id):
            first_flush = self.manager.prepare_request(second)
            self.manager.finalize_request(ctx=second, assistant=None, success=True)
        self.assertEqual(first_flush.status, "scheduled")
        self.assertEqual(len(self.scheduler.samples), 1)

        self.manager._pending_by_session["s-dedupe"] = pending
        with self.manager.session_guard(second.session_id):
            second_flush = self.manager.prepare_request(second)
            self.manager.finalize_request(ctx=second, assistant=None, success=True)
        self.assertEqual(second_flush.reason, "dedupe_skipped")
        self.assertEqual(len(self.scheduler.samples), 1)

    def test_forward_failure_does_not_cache_current_main_turn(self) -> None:
        proxy = UpstreamChatProxy(
            config=OpenClawMainTurnProxyConfig(
                enabled=True,
                target_base_url="http://127.0.0.1:9",
                ingest_window=6,
            ).normalize()
        )
        handler = _FakeHandler()
        success, response_sent, assistant, error = proxy.forward(
            handler,
            body={
                "model": "test-model",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": False,
            },
            headers={},
        )
        self.assertFalse(success)
        self.assertFalse(response_sent)
        self.assertIsNone(assistant)
        self.assertTrue(str(error))

        ctx = self._ctx(
            session_id="s-fail",
            turn_type="main",
            messages=[{"role": "user", "content": "hello"}],
        )
        with self.manager.session_guard(ctx.session_id):
            self.manager.prepare_request(ctx)
            self.manager.finalize_request(ctx=ctx, assistant=None, success=False, error=error)
        self.assertNotIn("s-fail", self.manager._pending_by_session)


class StreamAccumulatorTest(unittest.TestCase):
    def test_copy_headers_does_not_force_zero_content_length_for_stream(self) -> None:
        handler = _FakeHandler()
        _copy_headers_to_client(
            handler,
            headers=[
                ("Content-Type", "text/event-stream"),
                ("Content-Length", "123"),
                ("X-Trace-Id", "trace-1"),
            ],
            content_length=None,
        )
        headers = {k.lower(): v for k, v in handler.headers}
        self.assertEqual(headers.get("content-type"), "text/event-stream")
        self.assertEqual(headers.get("x-trace-id"), "trace-1")
        self.assertNotIn("content-length", headers)

    def test_stream_accumulator_collects_sse_content(self) -> None:
        acc = StreamAssistantAccumulator()
        acc.feed(b'data: {"choices":[{"delta":{"role":"assistant","content":"Hello"}}]}\n\n')
        acc.feed(b'data: {"choices":[{"delta":{"content":" world"}}]}\n\n')
        acc.feed(b"data: [DONE]\n\n")
        assistant = acc.finish()
        self.assertIsNotNone(assistant)
        self.assertEqual(assistant.content, "Hello world")


if __name__ == "__main__":
    unittest.main()
