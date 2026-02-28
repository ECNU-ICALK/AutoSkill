"""
Backward-compatible entrypoint for offline conversation extraction.

The implementation lives in `autoskill.offline.conversation.extract`.
"""

from __future__ import annotations

from .conversation.extract import extract_from_conversation, main

__all__ = ["extract_from_conversation", "main"]


if __name__ == "__main__":
    main()
