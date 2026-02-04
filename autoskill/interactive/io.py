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
    def input(self, prompt: str) -> str: ...

    def print(self, *args, **kwargs) -> None: ...


@dataclass
class ConsoleIO:
    def input(self, prompt: str) -> str:
        return input(prompt)

    def print(self, *args, **kwargs) -> None:
        print(*args, **kwargs)

