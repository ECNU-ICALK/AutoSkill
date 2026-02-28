"""
Backward-compatible entrypoint for offline document extraction.

The implementation lives in `autoskill.offline.document.extract`.
"""

from __future__ import annotations

from .document.extract import extract_from_doc, main

__all__ = ["extract_from_doc", "main"]


if __name__ == "__main__":
    main()
