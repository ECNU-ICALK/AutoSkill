"""
Offline Mock LLM (for testing/debugging the extraction pipeline).

Note:
- The default extractor uses a heuristic extractor for provider=mock, so it won't call this LLM.
- To test the “LLM extraction + repair/fallback” path, explicitly construct LLMSkillExtractor and inject MockLLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import LLM


@dataclass
class MockLLM(LLM):
    """
    A deterministic offline stub.

    Note: The default extractor uses a heuristic extractor for provider=mock, so
    this LLM is mainly for testing/mocking higher layers.
    """

    response: str = '{"skills": []}'

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        """Run complete."""
        return self.response
