"""
Offline extraction flow for document/text corpora.
"""

from __future__ import annotations

from typing import Any

__all__ = ["extract_from_doc", "main"]


def __getattr__(name: str) -> Any:
    """Run getattr."""
    if name == "extract_from_doc":
        from .extract import extract_from_doc as fn

        return fn
    if name == "main":
        from .extract import main as fn

        return fn
    raise AttributeError(name)
