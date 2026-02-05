"""
DashScope Qwen embeddings demo (OpenAI-compatible mode).

Equivalent to:
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-v4","input":"...","dimensions":1024,"encoding_format":"float"}'

Env:
- DASHSCOPE_API_KEY: required
- DASHSCOPE_EMBED_MODEL: optional (default: text-embedding-v4)
- DASHSCOPE_BASE_URL: optional (default: https://dashscope.aliyuncs.com/compatible-mode)
- AUTOSKILL_TIMEOUT_S: optional (default: 120)
"""

from __future__ import annotations

import argparse
import os

from autoskill.embeddings.factory import build_embeddings


def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None and v.strip() else default


def main() -> None:
    parser = argparse.ArgumentParser(description="DashScope Qwen embeddings demo")
    parser.add_argument("--model", default=_env("DASHSCOPE_EMBED_MODEL", "text-embedding-v4"))
    parser.add_argument("--text", default="The quick brown fox jumps over the lazy dog.")
    parser.add_argument("--dimensions", type=int, default=1024)
    parser.add_argument("--encoding-format", default="float")
    args = parser.parse_args()

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key or not api_key.strip():
        raise SystemExit("Missing DASHSCOPE_API_KEY.")

    emb = build_embeddings(
        {
            "provider": "dashscope",
            "model": str(args.model),
            "api_key": api_key,
            "base_url": _env("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode"),
            "timeout_s": int(_env("AUTOSKILL_TIMEOUT_S", "120")),
            "extra_body": {
                "dimensions": int(args.dimensions),
                "encoding_format": str(args.encoding_format),
            },
        }
    )
    vectors = emb.embed([str(args.text)])
    if not vectors:
        print("(empty)")
        return
    vec = vectors[0]
    print("dims:", len(vec))
    print("head:", [float(x) for x in vec[:8]])


if __name__ == "__main__":
    main()

