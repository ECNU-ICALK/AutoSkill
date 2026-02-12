"""
Embedding provider layer.

Built-in providers:
- `hashing`: deterministic offline embeddings (for demos/tests)
- `openai`: OpenAI embeddings
- `generic`: OpenAI-compatible custom endpoint (optional API key)
- `dashscope`: Aliyun DashScope Qwen embeddings (OpenAI-compatible mode)
- `glm`: BigModel embedding-3
"""

from .base import EmbeddingModel
from .factory import build_embeddings

__all__ = ["EmbeddingModel", "build_embeddings"]
