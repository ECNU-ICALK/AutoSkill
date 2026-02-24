from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Trajectory:
    trajectory_id: str
    source_file: str
    source_mtime: float
    user_instruction: str
    environment: Dict[str, Any]
    messages: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    raw: Dict[str, Any]


@dataclass
class SuccessScore:
    ok: bool
    score: float
    reason: str


@dataclass
class SkillDraft:
    name: str
    description: str
    version: str
    tools: List[str]
    steps: List[str]
    source_trajectory_id: str
    fingerprint: str = field(default="")


@dataclass
class SkillDecision:
    action: str
    target_slug: str
    reason: str


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def read_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def write_json(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def sha1_obj(obj: Any) -> str:
    return sha1_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


def slugify(text: str, *, max_len: int = 72) -> str:
    s = str(text or "").strip().lower()
    s = s.replace("/", "-").replace("\\", "-")
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff_-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-_")
    if not s:
        s = "agent-skill"
    return s[:max_len]


def normalize_tool_name(name: str) -> str:
    s = str(name or "").strip().lower()
    s = s.replace(" ", "_").replace("-", "_")
    s = re.sub(r"[^a-z0-9_]+", "", s)
    return s or "tool"


def parse_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    raw = str(text or "").strip()
    if not raw:
        return None
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(raw[start : end + 1])
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None
    return None


def bump_patch(version: str) -> str:
    s = str(version or "").strip()
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", s)
    if not m:
        return "1.0.1"
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{major}.{minor}.{patch + 1}"


def extract_frontmatter(md: str) -> Tuple[Dict[str, Any], str]:
    lines = (md or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, md
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, md

    meta: Dict[str, Any] = {}
    body = "\n".join(lines[end + 1 :]).strip()
    for ln in lines[1:end]:
        if ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        key = k.strip().lower()
        val = v.strip()
        if key == "tools":
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                parts = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
                meta[key] = parts
            else:
                meta[key] = [x.strip() for x in val.split(",") if x.strip()]
        else:
            meta[key] = val.strip('"').strip("'")
    return meta, body


def render_skill_md(skill: SkillDraft) -> str:
    tools = ", ".join(json.dumps(str(t), ensure_ascii=False) for t in skill.tools)
    lines: List[str] = [
        "---",
        f"name: {json.dumps(skill.name, ensure_ascii=False)}",
        f"description: {json.dumps(skill.description, ensure_ascii=False)}",
        f"version: {json.dumps(skill.version, ensure_ascii=False)}",
        f"tools: [{tools}]",
        "---",
        "",
        "# 技能执行步骤",
    ]
    for idx, step in enumerate(skill.steps, start=1):
        lines.append(f"{idx}. {step}")
    lines.append("")
    return "\n".join(lines)


def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if v is not None and v.strip() else default
