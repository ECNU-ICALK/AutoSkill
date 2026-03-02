"""
Minimal Agent Skill directory artifact implementation (anthropics/skills style).

One Skill maps to one directory, which contains at least:
- `SKILL.md`: entry + documentation (YAML frontmatter + Markdown body)

This module can:
- render a structured Skill into a files mapping (path -> content)
- parse/import an existing Agent Skill directory (SKILL.md + optional files) into a Skill object
"""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Dict, List, Optional

from ...models import Skill, SkillExample

_SLUG_RE = re.compile(r"[^\w-]+", re.UNICODE)
_WS_RE = re.compile(r"\s+", re.UNICODE)
_DASH_RE = re.compile(r"-{2,}")


def skill_dir_name(skill: Skill) -> str:
    """
    Returns a directory name similar to the anthropics/skills repo style, e.g. "skill-creator".
    """

    slug = _slugify(skill.name)
    if not slug:
        slug = _slugify(skill.description) or "skill"
    return slug


def build_agent_skill_files(skill: Skill) -> Dict[str, str]:
    """
    Minimal Agent Skill artifact:
    - SKILL.md (required)
    - Optional scripts/resources can be added later in `Skill.files`.
    """

    return {"SKILL.md": render_skill_md(skill)}


def render_skill_md(skill: Skill) -> str:
    """Run render skill md."""
    frontmatter = _render_frontmatter(
        skill_id=skill.id,
        name=skill.name,
        description=skill.description,
        version=skill.version,
        tags=list(skill.tags or []),
        triggers=list(skill.triggers or []),
        examples=list(skill.examples or []),
    )
    body = _render_body(skill)
    return f"---\n{frontmatter}\n---\n\n{body}\n"


def upsert_skill_md_id(md: str, *, skill_id: str) -> str:
    """
    Inserts or updates the `id:` field in SKILL.md YAML frontmatter.

    This is used when importing external skills so they get a stable AutoSkill-assigned ID, while
    preserving the rest of the artifact.
    """

    return _upsert_frontmatter_scalar(md, key="id", value=str(skill_id))


def upsert_skill_md_metadata(
    md: str,
    *,
    skill_id: str,
    name: str,
    description: str,
    version: str,
) -> str:
    """
    Ensures SKILL.md YAML frontmatter contains required metadata fields.

    This function preserves the original markdown body while enforcing a stable `id` and keeping
    `name`, `description`, and `version` synchronized with the structured Skill fields.
    """

    # Insert in reverse order because the underlying helper inserts new keys at the top.
    md2 = _upsert_frontmatter_scalar(md, key="version", value=str(version or "0.1.0"))
    md2 = _upsert_frontmatter_scalar(md2, key="description", value=str(description))
    md2 = _upsert_frontmatter_scalar(md2, key="name", value=str(name))
    md2 = _upsert_frontmatter_scalar(md2, key="id", value=str(skill_id))
    return md2


def _upsert_frontmatter_scalar(md: str, *, key: str, value: str) -> str:
    """Run upsert frontmatter scalar."""
    import re

    key_s = str(key or "").strip()
    if not key_s:
        return md
    value_s = str(value or "").strip()
    q = json.dumps(value_s, ensure_ascii=False)

    lines = (md or "").splitlines()
    if lines and lines[0].strip() == "---":
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is not None:
            fm = list(lines[1:end])
            key_re = re.compile(rf"^\s*{re.escape(key_s)}\s*:\s*.*$", re.IGNORECASE)
            out: List[str] = []
            found = False
            for ln in fm:
                if key_re.match(ln):
                    out.append(f"{key_s}: {q}")
                    found = True
                else:
                    out.append(ln)
            if not found:
                out.insert(0, f"{key_s}: {q}")
            new_lines = ["---"] + out + ["---"] + lines[end + 1 :]
            return "\n".join(new_lines).rstrip() + "\n"

    # No frontmatter: create one.
    body = (md or "").strip()
    if body:
        return f"---\n{key_s}: {q}\n---\n\n{body}\n"
    return f"---\n{key_s}: {q}\n---\n"


def _render_body(skill: Skill) -> str:
    """Run render body."""
    lines: List[str] = []
    lines.append(f"# {skill.name}".strip())
    lines.append("")
    if skill.description:
        lines.append(skill.description.strip())
        lines.append("")

    lines.append("## Prompt")
    lines.append("")
    lines.append((skill.instructions or "").strip())
    lines.append("")

    extra_files = sorted([p for p in (skill.files or {}).keys() if p and p != "SKILL.md"])
    if extra_files:
        lines.append("## Files")
        lines.append("")
        for p in extra_files[:50]:
            lines.append(f"- `{p}`")
        lines.append("")

    if skill.triggers:
        lines.append("## Triggers")
        lines.append("")
        for t in (skill.triggers or [])[:10]:
            s = str(t).strip()
            if s:
                lines.append(f"- {s}")
        lines.append("")

    if skill.examples:
        lines.append("## Examples")
        lines.append("")
        for i, ex in enumerate((skill.examples or [])[:3], start=1):
            lines.append(f"### Example {i}")
            lines.append("")
            lines.append("Input:")
            lines.append("")
            lines.append(_indent(ex.input))
            if ex.output:
                lines.append("")
                lines.append("Output:")
                lines.append("")
                lines.append(_indent(str(ex.output)))
            if ex.notes:
                lines.append("")
                lines.append("Notes:")
                lines.append("")
                lines.append(_indent(str(ex.notes)))
            lines.append("")

    return "\n".join(lines).strip()


def _render_frontmatter(
    *,
    skill_id: str,
    name: str,
    description: str,
    version: str,
    tags: List[str],
    triggers: List[str],
    examples: List[SkillExample],
) -> str:
    """Run render frontmatter."""
    lines: List[str] = []
    lines.append(f"id: {_q(skill_id.strip())}")
    lines.append(f"name: {_q(name.strip())}")
    lines.append(f"description: {_q(description.strip())}")
    lines.append(f"version: {_q((version or '0.1.0').strip())}")

    if tags:
        lines.append("tags:")
        for t in tags:
            s = str(t).strip()
            if s:
                lines.append(f"  - {_q(s)}")

    if triggers:
        lines.append("triggers:")
        for tr in triggers:
            s = str(tr).strip()
            if s:
                lines.append(f"  - {_q(s)}")

    if examples:
        lines.append("examples:")
        for ex in examples[:8]:
            lines.append(f"  - input: {_q((ex.input or '').strip())}")
            if ex.output:
                lines.append(f"    output: {_q(str(ex.output).strip())}")
            if ex.notes:
                lines.append(f"    notes: {_q(str(ex.notes).strip())}")

    return "\n".join(lines).strip()


def _q(value: str) -> str:
    """Run q."""
    return json.dumps(value, ensure_ascii=False)


def _slugify(text: str) -> str:
    """Run slugify."""
    s = (text or "").strip().lower()
    s = s.replace("/", "-").replace("\\", "-")
    s = _WS_RE.sub("-", s)
    s = _SLUG_RE.sub("-", s)
    s = _DASH_RE.sub("-", s).strip("-_")
    return s[:64]


def _indent(text: str, spaces: int = 2) -> str:
    """Run indent."""
    prefix = " " * spaces
    lines = (text or "").splitlines() or [""]
    return "\n".join(prefix + ln for ln in lines)


def load_agent_skill_dir(
    dir_path: str,
    *,
    user_id: str,
    default_version: str = "0.1.0",
    include_files: bool = True,
    max_file_bytes: int = 1_000_000,
    deterministic_id_salt: str = "autoskill-agent-skill-import-v1",
    deterministic_id_key: Optional[str] = None,
    ignore_frontmatter_id: bool = False,
) -> Skill:
    """
    Loads an existing Agent Skill directory (anthropics/skills style) into a Skill object.

    Requirements:
    - `dir_path/SKILL.md` must exist.

    Behavior:
    - Parses YAML frontmatter if present.
    - Extracts instructions from the "## Prompt" section (fallbacks are applied).
    - Optionally loads other text files in the directory into `Skill.files`.
    """

    abs_dir = os.path.abspath(os.path.expanduser(str(dir_path)))
    skill_md_path = os.path.join(abs_dir, "SKILL.md")
    if not os.path.isfile(skill_md_path):
        raise FileNotFoundError(f"Missing SKILL.md: {skill_md_path}")

    raw_skill_md = _read_text_file(skill_md_path, max_bytes=max_file_bytes)
    meta, body = _parse_skill_md(raw_skill_md)
    frontmatter, _ = _split_frontmatter(raw_skill_md)

    name = str(meta.get("name") or "").strip() or _infer_name_from_body(body) or os.path.basename(abs_dir)
    description = (
        str(meta.get("description") or "").strip()
        or _infer_description_from_body(body)
        or name
    )

    instructions = str(meta.get("prompt") or meta.get("instructions") or "").strip()
    if not instructions:
        instructions = _extract_markdown_section(body, "Prompt")
    if not instructions:
        instructions = _extract_markdown_section(body, "Instructions")
    instructions = (instructions or "").strip()
    if not instructions:
        # Fall back to the whole body when Prompt is missing; keep it predictable for users who have
        # non-standard Skill markdown layouts.
        instructions = body.strip()

    frontmatter_id = ""
    if not ignore_frontmatter_id:
        frontmatter_id = _extract_frontmatter_scalar(frontmatter, key="id") or _extract_frontmatter_scalar(
            frontmatter, key="skill_id"
        )
    skill_id = frontmatter_id or ("" if ignore_frontmatter_id else str(meta.get("id") or meta.get("skill_id") or "").strip())
    if not skill_id:
        rel_key = str(deterministic_id_key or os.path.basename(abs_dir) or "").strip()
        if not rel_key:
            rel_key = os.path.basename(abs_dir) or "skill"
        # Intentionally avoid using parsed fields (like `name`) in the ID derivation so the ID
        # remains stable even if the markdown content changes or YAML parsing is imperfect.
        base = f"{deterministic_id_salt}:{user_id}:{rel_key}"
        skill_id = str(uuid.uuid5(uuid.NAMESPACE_URL, base))

    version = str(meta.get("version") or default_version or "0.1.0").strip() or "0.1.0"

    tags = _coerce_str_list(meta.get("tags") or meta.get("tag") or [])
    triggers = _coerce_str_list(meta.get("triggers") or meta.get("trigger") or [])
    examples = _coerce_examples(meta.get("examples") or [])

    skill_md = upsert_skill_md_id(raw_skill_md, skill_id=skill_id)
    files: Dict[str, str] = {"SKILL.md": skill_md}
    if include_files:
        for rel_path, content in _read_dir_text_files(
            abs_dir,
            max_bytes=max_file_bytes,
            skip_paths={"SKILL.md"},
        ).items():
            files[rel_path] = content

    skill = Skill(
        id=skill_id,
        user_id=str(user_id),
        name=name,
        description=description,
        instructions=instructions,
        triggers=triggers,
        tags=tags,
        examples=examples,
        version=version,
        files=files,
    )
    return skill


def parse_agent_skill_md(md: str) -> Dict[str, object]:
    """
    Parses `SKILL.md` into a dict containing the extracted core fields.

    Returns:
      {
        "id": str|None,
        "name": str|None,
        "description": str|None,
        "version": str|None,
        "tags": list[str],
        "triggers": list[str],
        "examples": list[dict],
        "prompt": str|None,
      }
    """

    meta, body = _parse_skill_md(md)
    prompt = str(meta.get("prompt") or meta.get("instructions") or "").strip()
    if not prompt:
        prompt = _extract_markdown_section(body, "Prompt")
    if not prompt:
        prompt = _extract_markdown_section(body, "Instructions")
    out: Dict[str, object] = dict(meta)
    out["prompt"] = (prompt or "").strip() or None
    out.setdefault("tags", _coerce_str_list(out.get("tags") or []))
    out.setdefault("triggers", _coerce_str_list(out.get("triggers") or []))
    return out


def _parse_skill_md(md: str) -> tuple[Dict[str, object], str]:
    """Run parse skill md."""
    frontmatter, body = _split_frontmatter(md)
    meta: Dict[str, object] = {}
    if frontmatter is not None:
        meta = _parse_frontmatter(frontmatter)
    return meta, body


def _extract_frontmatter_scalar(frontmatter: Optional[str], *, key: str) -> str:
    """
    Extracts a scalar value from YAML frontmatter without requiring full YAML parsing.

    This is intentionally conservative and only supports one-line scalars like:
      id: "..."
      id: ...
    """

    fm = str(frontmatter or "").strip("\n")
    key_s = str(key or "").strip()
    if not fm or not key_s:
        return ""

    key_re = re.compile(rf"^\s*{re.escape(key_s)}\s*:\s*(.*)\s*$", re.IGNORECASE)
    for line in fm.splitlines():
        m = key_re.match(line)
        if not m:
            continue
        raw = str(m.group(1) or "").strip()
        if raw in {">", ">-", "|", "|-"}:
            return ""
        return _parse_scalar(raw)
    return ""


def _split_frontmatter(md: str) -> tuple[Optional[str], str]:
    """Run split frontmatter."""
    lines = (md or "").splitlines()
    if not lines:
        return None, ""
    if lines[0].strip() != "---":
        return None, md
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            return fm, body
    return None, md


def _parse_frontmatter(frontmatter: str) -> Dict[str, object]:
    # Prefer PyYAML when available but keep a fallback parser to avoid adding mandatory dependencies.
    """Run parse frontmatter."""
    try:
        import yaml  # type: ignore

        obj = yaml.safe_load(frontmatter)  # type: ignore[attr-defined]
        if isinstance(obj, dict):
            return {str(k): v for k, v in obj.items()}
    except Exception:
        pass
    return _parse_frontmatter_fallback(frontmatter)


def _parse_frontmatter_fallback(frontmatter: str) -> Dict[str, object]:
    """
    Minimal YAML subset parser for the frontmatter produced by this SDK.

    Supports:
    - scalar values: `key: value` (quoted/unquoted)
    - string lists: `tags:` + indented `- item`
    - examples: list of dicts with keys input/output/notes
    """

    out: Dict[str, object] = {}
    lines = (frontmatter or "").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if not line.strip():
            i += 1
            continue

        if line.startswith(" "):
            i += 1
            continue

        if ":" not in line:
            i += 1
            continue

        key, rest = line.split(":", 1)
        key = key.strip()
        rest_s = rest.strip()
        if not key:
            i += 1
            continue

        if rest_s:
            out[key] = _parse_scalar(rest_s)
            i += 1
            continue

        # Block/list value.
        if key in {"tags", "triggers"}:
            items: List[str] = []
            i += 1
            while i < len(lines):
                ln = lines[i].rstrip("\n")
                if not ln.strip():
                    i += 1
                    continue
                if not ln.startswith(" "):
                    break
                s = ln.lstrip()
                if s.startswith("- "):
                    items.append(str(_parse_scalar(s[2:].strip())))
                i += 1
            out[key] = [x for x in items if str(x).strip()]
            continue

        if key == "examples":
            examples: List[Dict[str, object]] = []
            i += 1
            while i < len(lines):
                ln = lines[i].rstrip("\n")
                if not ln.strip():
                    i += 1
                    continue
                if not ln.startswith(" "):
                    break
                s = ln.lstrip()
                if not s.startswith("- "):
                    i += 1
                    continue

                ex: Dict[str, object] = {}
                first = s[2:].strip()
                if first:
                    if ":" in first:
                        k2, v2 = first.split(":", 1)
                        ex[k2.strip()] = _parse_scalar(v2.strip())
                i += 1
                while i < len(lines):
                    ln2 = lines[i].rstrip("\n")
                    if not ln2.strip():
                        i += 1
                        continue
                    if not ln2.startswith(" "):
                        break
                    s2 = ln2.lstrip()
                    if s2.startswith("- "):
                        break
                    if ":" in s2:
                        k3, v3 = s2.split(":", 1)
                        ex[k3.strip()] = _parse_scalar(v3.strip())
                    i += 1

                if ex:
                    examples.append(ex)
                continue

            out[key] = examples
            continue

        out[key] = []
        i += 1

    return out


def _parse_scalar(value: str) -> str:
    """Run parse scalar."""
    s = (value or "").strip()
    if not s:
        return ""
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        try:
            return str(json.loads(s))
        except Exception:
            return s.strip('"')
    if s.startswith("'") and s.endswith("'") and len(s) >= 2:
        return s.strip("'")
    return s


def _extract_markdown_section(body: str, title: str) -> str:
    """Run extract markdown section."""
    target = f"## {title}".strip().lower()
    lines = (body or "").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower() != target:
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        out: List[str] = []
        while j < len(lines):
            ln2 = lines[j]
            if ln2.startswith("## ") or ln2.startswith("# "):
                break
            out.append(ln2)
            j += 1
        return "\n".join(out).strip()
    return ""


def _infer_name_from_body(body: str) -> str:
    """Run infer name from body."""
    for ln in (body or "").splitlines():
        s = ln.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return ""


def _infer_description_from_body(body: str) -> str:
    """Run infer description from body."""
    lines = (body or "").splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("# "):
            start = i + 1
            break
    if start is None:
        return ""
    out: List[str] = []
    for ln in lines[start:]:
        if ln.startswith("## ") or ln.startswith("# "):
            break
        if ln.strip() == "" and out:
            break
        if ln.strip():
            out.append(ln.strip())
    return " ".join(out).strip()


def _coerce_str_list(obj: object) -> List[str]:
    """Run coerce str list."""
    if obj is None:
        return []
    if isinstance(obj, list):
        out = []
        seen = set()
        for v in obj:
            s = str(v).strip()
            if not s:
                continue
            key = s.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
        return out
    s = str(obj).strip()
    return [s] if s else []


def _coerce_examples(obj: object) -> List[SkillExample]:
    """Run coerce examples."""
    if not isinstance(obj, list):
        return []
    out: List[SkillExample] = []
    for item in obj[:20]:
        if isinstance(item, SkillExample):
            out.append(item)
            continue
        if not isinstance(item, dict):
            continue
        inp = str(item.get("input") or "").strip()
        if not inp:
            continue
        out.append(
            SkillExample(
                input=inp,
                output=(str(item.get("output")).strip() if item.get("output") else None),
                notes=(str(item.get("notes")).strip() if item.get("notes") else None),
            )
        )
    return out


def _read_text_file(path: str, *, max_bytes: int) -> str:
    """Run read text file."""
    with open(path, "rb") as f:
        data = f.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"File too large (>{max_bytes} bytes): {path}")
    if b"\x00" in data:
        raise ValueError(f"Binary file not supported: {path}")
    return data.decode("utf-8", errors="replace")


def _read_dir_text_files(
    abs_dir: str,
    *,
    max_bytes: int,
    skip_paths: set[str],
) -> Dict[str, str]:
    """Run read dir text files."""
    out: Dict[str, str] = {}
    for root, _dirs, files in os.walk(abs_dir):
        for fn in files:
            if fn in {".DS_Store"}:
                continue
            abs_path = os.path.join(root, fn)
            rel_path = os.path.relpath(abs_path, abs_dir).replace(os.sep, "/")
            if rel_path in skip_paths:
                continue
            try:
                content = _read_text_file(abs_path, max_bytes=max_bytes)
            except Exception:
                continue
            out[rel_path] = content
    return out
