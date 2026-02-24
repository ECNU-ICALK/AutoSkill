"""
Vector indexing backends.

By default, AutoSkill uses a dependency-free persistent flat index (exact search).
Optional accelerated backends can be added later without changing the store interface.
"""

from .base import VectorIndex, VectorStore
from .factory import (
    build_vector_index,
    list_vector_backends,
    register_vector_backend,
)
from .flat import FlatFileVectorIndex

__all__ = [
    "VectorIndex",
    "VectorStore",
    "FlatFileVectorIndex",
    "build_vector_index",
    "register_vector_backend",
    "list_vector_backends",
]
