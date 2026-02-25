"""
Embedding provider layer.

Built-in providers:
- `none`: disable embeddings (keyword/BM25 retrieval fallback)
- `hashing`: deterministic offline embeddings (for demos/tests)
- `openai`: OpenAI embeddings
- `generic`: OpenAI-compatible custom endpoint (optional API key)
- `dashscope`: Aliyun DashScope Qwen embeddings (OpenAI-compatible mode)
- `glm`: BigModel embedding-3
"""

from .base import EmbeddingConnector, EmbeddingModel
from .factory import (
    build_embeddings,
    list_embedding_connectors,
    register_embedding_connector,
)

__all__ = [
    "EmbeddingModel",
    "EmbeddingConnector",
    "build_embeddings",
    "register_embedding_connector",
    "list_embedding_connectors",
]
