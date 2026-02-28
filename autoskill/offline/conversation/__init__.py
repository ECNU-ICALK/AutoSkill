"""
Offline extraction flow for archived OpenAI-format conversations.
"""

from __future__ import annotations

from typing import Any

__all__ = ["extract_from_conversation", "main"]


def __getattr__(name: str) -> Any:
    if name == "extract_from_conversation":
        from .extract import extract_from_conversation as fn

        return fn
    if name == "main":
        from .extract import main as fn

        return fn
    raise AttributeError(name)
