"""
Generic offline file loader.

Loads either a single file or all files under a directory, and returns each file
as one text unit so offline extraction can process heterogeneous sources without
strict schema assumptions.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any, Dict, List, Tuple


def load_file_units(path: str) -> Tuple[List[Dict[str, str]], str]:
    """
    Returns (units, abs_input_path), where each unit has:
    - title: display name (relative path if directory)
    - text: file content as text
    - source_file: absolute file path
    """

    abs_path = os.path.abspath(os.path.expanduser(str(path or "").strip()))
    if not abs_path:
        return [], ""
    if os.path.isfile(abs_path):
        text = _read_any_file_as_text(abs_path)
        if not text.strip():
            return [], abs_path
        return (
            [
                {
                    "title": os.path.basename(abs_path),
                    "text": text,
                    "source_file": abs_path,
                }
            ],
            abs_path,
        )
    if not os.path.isdir(abs_path):
        raise ValueError(f"path not found: {abs_path}")

    files: List[str] = []
    for root, _, names in os.walk(abs_path):
        for name in names:
            p = os.path.join(root, name)
            if os.path.isfile(p):
                files.append(p)
    files.sort()

    out: List[Dict[str, str]] = []
    for p in files:
        text = _read_any_file_as_text(p)
        if not text.strip():
            continue
        rel = os.path.relpath(p, abs_path)
        out.append(
            {
                "title": rel,
                "text": text,
                "source_file": p,
            }
        )
    return out, abs_path


def data_to_text_unit(data: Any, *, title: str = "inline_data") -> Dict[str, str]:
    """
    Converts arbitrary in-memory data into one text unit.
    """

    txt = _to_text(data).strip()
    return {
        "title": str(title or "inline_data"),
        "text": txt,
        "source_file": "",
    }


def _read_any_file_as_text(path: str, *, max_bytes: int = 8_000_000) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".doc", ".docx"}:
        txt = _read_word_document(path)
        if txt.strip():
            return txt

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        pass

    try:
        with open(path, "rb") as f:
            raw = f.read(max_bytes)
    except Exception:
        return ""

    text = raw.decode("utf-8", errors="ignore").replace("\x00", "").strip()
    if text:
        return text
    text2 = raw.decode("latin-1", errors="ignore").replace("\x00", "").strip()
    if text2:
        return text2
    return f"[Binary file content not decoded] {os.path.basename(path)}"


def _read_word_document(path: str) -> str:
    # macOS built-in converter.
    out = _run_text_command(["textutil", "-convert", "txt", "-stdout", path], timeout_s=20)
    if out.strip():
        return out
    # Common Linux tools.
    out = _run_text_command(["antiword", path], timeout_s=20)
    if out.strip():
        return out
    out = _run_text_command(["catdoc", path], timeout_s=20)
    if out.strip():
        return out
    return ""


def _run_text_command(argv: List[str], *, timeout_s: int) -> str:
    if not argv:
        return ""
    bin_name = str(argv[0] or "").strip()
    if not bin_name:
        return ""
    if shutil.which(bin_name) is None:
        return ""
    try:
        cp = subprocess.run(
            argv,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=int(timeout_s),
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if cp.returncode != 0:
            return ""
        return str(cp.stdout or "").strip()
    except Exception:
        return ""


def _to_text(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float, bool)):
        return str(obj)
    if isinstance(obj, list):
        return "\n".join(_to_text(x) for x in obj)
    if isinstance(obj, dict):
        parts: List[str] = []
        for k, v in obj.items():
            parts.append(f"{k}: {_to_text(v)}")
        return "\n".join(parts)
    return str(obj)
