"""
LLM interface.

AutoSkill only needs one minimal capability: given (system + user), return completion text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, Optional


class LLM(ABC):
    @abstractmethod
    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        """Run complete."""
        raise NotImplementedError

    def stream_complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> Iterator[str]:
        """
        Streams completion text chunks.

        Default behavior falls back to `complete(...)` and yields one chunk.
        Provider implementations can override this to support true token/chunk streaming.
        """

        out = self.complete(system=system, user=user, temperature=temperature)
        if out:
            yield str(out)


# Backward-compatible semantic alias used by plugin-style factory APIs.
LLMConnector = LLM
