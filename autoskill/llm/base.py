"""
LLM interface.

AutoSkill only needs one minimal capability: given (system + user), return completion text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class LLM(ABC):
    @abstractmethod
    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        raise NotImplementedError
