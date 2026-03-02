"""
Time utilities: generate ISO-8601 (UTC) timestamp strings.
"""

from __future__ import annotations

from datetime import datetime, timezone


def now_iso() -> str:
    """Run now iso."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
