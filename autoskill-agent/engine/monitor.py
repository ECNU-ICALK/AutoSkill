from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Iterable, List, Optional

from engine.core import Trajectory, normalize_tool_name, sha1_obj


class ObservationMonitor:
    """
    Poll-based monitor for OpenClaw workspace trajectory files.

    It scans common subfolders and keeps only changed files since the previous state.
    """

    def __init__(
        self,
        *,
        workspace_dir: str,
        state: Dict[str, Any],
        max_scan_depth: int = 6,
    ) -> None:
        self.workspace_dir = os.path.abspath(os.path.expanduser(str(workspace_dir)))
        self.max_scan_depth = max(1, int(max_scan_depth))
        self._file_state = dict(state.get("file_state") or {})

    def export_state(self) -> Dict[str, Any]:
        return {"file_state": dict(self._file_state)}

    def collect_new_trajectories(self) -> List[Trajectory]:
        trajectories: List[Trajectory] = []
        for path in self._iter_candidate_files():
            stat_key = self._stat_key(path)
            old = str(self._file_state.get(path) or "")
            if old == stat_key:
                continue
            self._file_state[path] = stat_key
            trajectories.extend(self._parse_file_to_trajectories(path))
        return trajectories

    def _iter_candidate_files(self) -> Iterable[str]:
        preferred = {"memory", "memories", "runs", "run", "history", "trace", "traces", "sessions"}
        base = self.workspace_dir
        base_sep = base.rstrip(os.sep) + os.sep
        for current, dirs, files in os.walk(base):
            rel = current[len(base_sep) :] if current.startswith(base_sep) else ""
            depth = 0 if not rel else rel.count(os.sep) + 1
            if depth > self.max_scan_depth:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "__pycache__"}]
            if depth == 0:
                dirs[:] = [d for d in dirs if d.lower() in preferred or d.lower().startswith("run")]

            for fn in files:
                if fn.startswith("."):
                    continue
                if not (fn.endswith(".json") or fn.endswith(".jsonl")):
                    continue
                yield os.path.join(current, fn)

    def _stat_key(self, path: str) -> str:
        try:
            st = os.stat(path)
            return f"{int(st.st_mtime)}:{int(st.st_size)}"
        except Exception:
            return "missing"

    def _parse_file_to_trajectories(self, path: str) -> List[Trajectory]:
        out: List[Trajectory] = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception:
            return out
        if not raw.strip():
            return out

        src_mtime = 0.0
        try:
            src_mtime = os.path.getmtime(path)
        except Exception:
            src_mtime = time.time()

        if path.endswith(".jsonl"):
            for line in raw.splitlines():
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                except Exception:
                    continue
                t = self._to_trajectory(obj=obj, source_file=path, source_mtime=src_mtime)
                if t is not None:
                    out.append(t)
            return out

        try:
            obj = json.loads(raw)
        except Exception:
            return out
        if isinstance(obj, list):
            for item in obj:
                t = self._to_trajectory(obj=item, source_file=path, source_mtime=src_mtime)
                if t is not None:
                    out.append(t)
            return out
        if isinstance(obj, dict):
            if isinstance(obj.get("trajectories"), list):
                for item in obj.get("trajectories", []):
                    t = self._to_trajectory(obj=item, source_file=path, source_mtime=src_mtime)
                    if t is not None:
                        out.append(t)
            else:
                t = self._to_trajectory(obj=obj, source_file=path, source_mtime=src_mtime)
                if t is not None:
                    out.append(t)
        return out

    def _to_trajectory(self, *, obj: Any, source_file: str, source_mtime: float) -> Optional[Trajectory]:
        if not isinstance(obj, dict):
            return None

        messages = self._extract_messages(obj)
        tool_calls = self._extract_tool_calls(obj)
        user_instruction = self._extract_user_instruction(obj, messages)
        if not user_instruction and not messages and not tool_calls:
            return None

        env = obj.get("environment")
        if not isinstance(env, dict):
            env = {}

        explicit_id = (
            str(obj.get("trajectory_id") or obj.get("id") or obj.get("run_id") or obj.get("task_id") or "").strip()
        )
        fingerprint = sha1_obj(
            {
                "source_file": source_file,
                "user_instruction": user_instruction,
                "messages": messages[-20:],
                "tool_calls": tool_calls[-20:],
            }
        )
        trajectory_id = explicit_id or fingerprint

        return Trajectory(
            trajectory_id=trajectory_id,
            source_file=source_file,
            source_mtime=float(source_mtime),
            user_instruction=user_instruction,
            environment=env,
            messages=messages,
            tool_calls=tool_calls,
            raw=obj,
        )

    def _extract_messages(self, obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        candidates = obj.get("messages")
        if not isinstance(candidates, list):
            for key in ("conversation", "chat_history", "history", "dialogue"):
                v = obj.get(key)
                if isinstance(v, list):
                    candidates = v
                    break
        out: List[Dict[str, Any]] = []
        if not isinstance(candidates, list):
            return out
        for m in candidates:
            if not isinstance(m, dict):
                continue
            role = str(m.get("role") or m.get("speaker") or "").strip().lower()
            content = str(m.get("content") or m.get("text") or "").strip()
            if not role and not content:
                continue
            out.append({"role": role or "unknown", "content": content})
        return out

    def _extract_tool_calls(self, obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        tool_data = obj.get("tool_calls")
        if not isinstance(tool_data, list):
            for key in ("tools", "actions", "tool_use", "tool_events"):
                v = obj.get(key)
                if isinstance(v, list):
                    tool_data = v
                    break
        out: List[Dict[str, Any]] = []
        if not isinstance(tool_data, list):
            return out
        for t in tool_data:
            if not isinstance(t, dict):
                continue
            name = str(t.get("name") or t.get("tool") or t.get("tool_name") or "").strip()
            if not name:
                continue
            status = str(t.get("status") or "").strip().lower()
            out.append(
                {
                    "name": normalize_tool_name(name),
                    "status": status,
                    "input": t.get("input"),
                    "output": t.get("output"),
                }
            )
        return out

    def _extract_user_instruction(self, obj: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
        for key in ("user_instruction", "instruction", "query", "prompt", "goal", "task"):
            v = obj.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
        for m in messages:
            if str(m.get("role") or "").lower() == "user" and str(m.get("content") or "").strip():
                return str(m.get("content") or "").strip()
        return ""
