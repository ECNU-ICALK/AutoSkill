"""
Command parsing for the interactive chat loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Command:
    name: str
    arg: str = ""


def parse_command(line: str) -> Optional[Command]:
    s = (line or "").strip()
    if not s.startswith("/"):
        return None
    parts = s.split(" ", 1)
    name = parts[0].strip().lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    return Command(name=name, arg=arg)

