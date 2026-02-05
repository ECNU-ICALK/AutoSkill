"""
Interactive configuration.

The interactive loop is intentionally configurable via a single object so it can be used by:
- CLI scripts (examples)
- external apps embedding AutoSkill
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InteractiveConfig:
    store_dir: str = "Skills"
    user_id: str = "u1"

    # Which Skills to use during retrieval:
    # - "user": only the current user's skills
    # - "library"/"common": only shared/common skills
    # - "all": both
    skill_scope: str = "all"

    # Retrieval query rewriting:
    # - "never": do not rewrite
    # - "auto": rewrite when a rewriter is configured
    # - "always": always rewrite (when a rewriter is configured)
    rewrite_mode: str = "always"  # auto|always|never
    rewrite_history_turns: int = 6
    # "chars" here means sizing units: CJK ideographs count by character; ASCII/English counts by word.
    rewrite_history_chars: int = 2000
    rewrite_max_query_chars: int = 256

    # Minimum similarity threshold for retrieval results (post-search filter).
    # Use a high value to be conservative and avoid injecting irrelevant skills.
    min_score: float = 0.4

    top_k: int = 1
    history_turns: int = 10
    ingest_window: int = 6

    # Extraction timing signals:
    # In "auto" mode, attempt extraction once every N turns (N=extract_turn_limit).
    # Set N=1 to attempt extraction every turn.
    extract_turn_limit: int = 1

    extract_mode: str = "auto"  # auto|always|never

    assistant_temperature: float = 0.2

    def normalize(self) -> "InteractiveConfig":
        self.store_dir = str(self.store_dir or "Skills").strip() or "Skills"

        self.skill_scope = (self.skill_scope or "all").strip().lower()
        if self.skill_scope == "common":
            self.skill_scope = "library"
        if self.skill_scope not in {"all", "user", "library"}:
            self.skill_scope = "all"

        self.rewrite_mode = (self.rewrite_mode or "auto").strip().lower()
        if self.rewrite_mode not in {"auto", "always", "never"}:
            self.rewrite_mode = "always"
        self.rewrite_history_turns = max(0, int(self.rewrite_history_turns))
        self.rewrite_history_chars = max(0, int(self.rewrite_history_chars))
        self.rewrite_max_query_chars = max(32, int(self.rewrite_max_query_chars))

        try:
            self.min_score = float(self.min_score)
        except Exception:
            self.min_score = 0.4

        self.extract_mode = (self.extract_mode or "auto").strip().lower()
        if self.extract_mode not in {"auto", "always", "never"}:
            self.extract_mode = "auto"

        self.top_k = max(0, int(self.top_k))
        self.history_turns = max(0, int(self.history_turns))
        self.ingest_window = max(2, int(self.ingest_window))
        self.extract_turn_limit = max(1, int(self.extract_turn_limit))
        return self
