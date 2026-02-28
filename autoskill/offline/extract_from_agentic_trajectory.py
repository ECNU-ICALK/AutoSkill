"""
Backward-compatible entrypoint for offline trajectory extraction.

The implementation lives in `autoskill.offline.trajectory.extract`.
"""

from __future__ import annotations

from .trajectory.extract import extract_from_agentic_trajectory, main

__all__ = ["extract_from_agentic_trajectory", "main"]


if __name__ == "__main__":
    main()
