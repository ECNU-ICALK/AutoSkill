from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class TrajectoryRecord:
    trajectory_id: str
    user_instruction: str
    messages: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    environment: Dict[str, Any]
    status: str = "completed"
    success: bool = True
    completed: bool = True
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        obj = asdict(self)
        if not obj.get("created_at"):
            obj["created_at"] = _now_iso()
        return obj


def build_trajectory(
    *,
    trajectory_id: str,
    user_instruction: str,
    messages: List[Dict[str, Any]],
    tool_calls: List[Dict[str, Any]],
    environment: Dict[str, Any] | None = None,
    success: bool = True,
    status: str = "completed",
) -> Dict[str, Any]:
    record = TrajectoryRecord(
        trajectory_id=str(trajectory_id),
        user_instruction=str(user_instruction),
        messages=list(messages or []),
        tool_calls=list(tool_calls or []),
        environment=dict(environment or {}),
        success=bool(success),
        completed=bool(success),
        status=str(status),
    )
    return record.to_dict()


def append_trajectory(workspace_dir: str, trajectory: Dict[str, Any], filename: str = "external_trajectories.jsonl") -> str:
    base = os.path.abspath(os.path.expanduser(str(workspace_dir)))
    runs_dir = os.path.join(base, "runs")
    os.makedirs(runs_dir, exist_ok=True)
    path = os.path.join(runs_dir, filename)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(trajectory, ensure_ascii=False) + "\n")
    return path
