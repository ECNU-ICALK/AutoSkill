"""
Offline Mock LLM (for testing/debugging the extraction pipeline).

Note:
- The default extractor uses a heuristic extractor for provider=mock, so it won't call this LLM.
- To test the “LLM extraction + repair/fallback” path, explicitly construct LLMSkillExtractor and inject MockLLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional

from .base import LLM


@dataclass
class MockLLM(LLM):
    """
    A deterministic offline stub.

    Note: The default extractor uses a heuristic extractor for provider=mock, so
    this LLM is mainly for testing/mocking higher layers.
    """

    response: Any = '{"skills": []}'
    _cursor: int = field(default=0, init=False, repr=False)
    _cursor_by_mode: Dict[str, int] = field(default_factory=dict, init=False, repr=False)

    def _mode(self, system: Optional[str]) -> str:
        """Classifies a mock request into a stable mode label."""

        text = str(system or "")
        lower = text.lower()
        if (
            ("expert knowledge extractor" in lower and "document excerpts" in lower)
            or "offline document skill extractor" in lower
        ):
            return "document_extract"
        if (
            "json output fixer for offline document skill extraction" in lower
            or "json fixer for offline document skill extraction" in lower
        ):
            return "document_extract_repair"
        if "document skill compiler" in lower:
            return "document_compile"
        if "document skill version manager" in lower:
            return "document_version"
        if "document conflict judge" in lower:
            return "document_conflict"
        if "skill set manager" in lower:
            return "manage_decide"
        if "capability identity judge" in lower:
            return "merge_gate"
        if "skill merger" in lower:
            return "merge"
        return "default"

    def _consume(self, value: Any, *, mode: str) -> str:
        """Returns one mock response item."""

        if isinstance(value, list):
            idx = int(self._cursor_by_mode.get(mode, 0))
            if not value:
                return '{"skills": []}'
            chosen = value[min(idx, len(value) - 1)]
            self._cursor_by_mode[mode] = idx + 1
            return json.dumps(chosen, ensure_ascii=False) if isinstance(chosen, dict) else str(chosen)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        """Run complete."""
        mode = self._mode(system)
        if callable(self.response):
            return str(self.response(system=system, user=user, temperature=temperature, mode=mode))
        if isinstance(self.response, dict):
            selected = self.response.get(mode)
            if selected is None:
                selected = self.response.get("default", '{"skills": []}')
            return self._consume(selected, mode=mode)
        if isinstance(self.response, list):
            if not self.response:
                return '{"skills": []}'
            chosen = self.response[min(self._cursor, len(self.response) - 1)]
            self._cursor += 1
            return str(chosen)
        return str(self.response)
