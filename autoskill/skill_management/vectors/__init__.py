"""
Vector indexing backends.

By default, AutoSkill uses a dependency-free persistent flat index (exact search).
Optional accelerated backends can be added later without changing the store interface.
"""

from .base import VectorIndex
from .flat import FlatFileVectorIndex

__all__ = ["VectorIndex", "FlatFileVectorIndex"]
