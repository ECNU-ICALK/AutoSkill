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
    """Run parse command."""
    s = (line or "").strip()
    if not s:
        return None

    # Accept both ASCII "/" and fullwidth "／" as the command prefix. Some IMEs may output the
    # fullwidth variant in punctuation modes.
    if s.startswith(("/", "／")):
        s2 = s[1:].strip()
        if not s2:
            return None
        parts = s2.split(" ", 1)
        name = "/" + parts[0].strip().lower()
        arg = parts[1].strip() if len(parts) > 1 else ""
        return Command(name=name, arg=arg)

    # Backward-compatible alias: allow "extract_now" without a leading slash.
    # This avoids surprising behavior for common words like "help" or "write".
    low = s.lower()
    if low == "extract_now" or low.startswith("extract_now "):
        parts = s.split(" ", 1)
        arg = parts[1].strip() if len(parts) > 1 else ""
        return Command(name="/extract_now", arg=arg)

    # Safe bare aliases for no-argument commands (only when the line is exactly the command).
    if low in {"help", "exit", "quit", "skills", "clear"}:
        return Command(name="/" + low, arg="")

    return None
