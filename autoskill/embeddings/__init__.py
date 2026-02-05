"""
Embedding provider layer.

Built-in providers:
- `hashing`: deterministic offline embeddings (for demos/tests)
- `openai`: OpenAI embeddings
- `dashscope`: Aliyun DashScope Qwen embeddings (OpenAI-compatible mode)
- `glm`: BigModel embedding-3
"""

from .base import EmbeddingModel
from .factory import build_embeddings

__all__ = ["EmbeddingModel", "build_embeddings"]
