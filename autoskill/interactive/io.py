"""
Interactive IO abstraction.

This is a small wrapper around input/print to make the interactive loop:
- easier to test (swap IO)
- reusable in non-console environments
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class IO(Protocol):
    def input(self, prompt: str) -> str:
        """Read one input line from the user."""
        ...

    def print(self, *args, **kwargs) -> None:
        """Render output to the current interactive sink."""
        ...


@dataclass
class ConsoleIO:
    def input(self, prompt: str) -> str:
        """Run input."""
        return input(prompt)

    def print(self, *args, **kwargs) -> None:
        """Run print."""
        print(*args, **kwargs)
