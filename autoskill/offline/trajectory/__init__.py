"""
Offline extraction flow for agentic trajectories and execution records.
"""

from __future__ import annotations

from typing import Any

__all__ = ["extract_from_agentic_trajectory", "main"]


def __getattr__(name: str) -> Any:
    """Run getattr."""
    if name == "extract_from_agentic_trajectory":
        from .extract import extract_from_agentic_trajectory as fn

        return fn
    if name == "main":
        from .extract import main as fn

        return fn
    raise AttributeError(name)
