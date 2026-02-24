#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List

try:
    from .adapter import append_trajectory
except Exception:
    import os
    import sys

    _HERE = os.path.dirname(os.path.abspath(__file__))
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    from adapter import append_trajectory


class _Handler(BaseHTTPRequestHandler):
    workspace_dir: str = "~/.openclaw"

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/v1/trajectories":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except Exception:
            length = 0
        body = self.rfile.read(length) if length > 0 else b""
        try:
            payload = json.loads(body.decode("utf-8", errors="replace"))
        except Exception:
            self._json(400, {"error": "invalid_json"})
            return

        records: List[Dict[str, Any]]
        if isinstance(payload, list):
            records = [x for x in payload if isinstance(x, dict)]
        elif isinstance(payload, dict):
            records = [payload]
        else:
            records = []
        if not records:
            self._json(400, {"error": "empty_payload"})
            return

        out_path = ""
        for rec in records:
            out_path = append_trajectory(self.workspace_dir, rec)
        self._json(200, {"ok": True, "written": len(records), "path": out_path})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _json(self, code: int, obj: Dict[str, Any]) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generic trajectory sink for AutoSkill-Agent.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9011)
    parser.add_argument("--workspace-dir", default="~/.openclaw")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    _Handler.workspace_dir = str(args.workspace_dir)
    server = ThreadingHTTPServer((str(args.host), int(args.port)), _Handler)
    print(f"[autoskill-agent] trajectory-sink listening on http://{args.host}:{args.port}/v1/trajectories")
    server.serve_forever()


if __name__ == "__main__":
    main()
