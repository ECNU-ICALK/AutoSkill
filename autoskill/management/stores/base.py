"""
Store interface.

Minimal capabilities for the SDK:
- upsert/get/list/delete: manage skills
- search: similarity search powered by embeddings
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ...models import Skill, SkillHit


class SkillStore(ABC):
    @abstractmethod
    def upsert(self, skill: Skill, *, raw: Optional[Dict[str, Any]] = None) -> None:
        """Run upsert."""
        raise NotImplementedError

    @abstractmethod
    def get(self, skill_id: str) -> Optional[Skill]:
        """Run get."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, skill_id: str) -> bool:
        """Run delete."""
        raise NotImplementedError

    @abstractmethod
    def list(self, *, user_id: str) -> List[Skill]:
        """Run list."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        *,
        user_id: str,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SkillHit]:
        """Run search."""
        raise NotImplementedError
