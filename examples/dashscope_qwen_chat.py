"""
DashScope Qwen chat completion demo (OpenAI-compatible mode).

Equivalent to:
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[...]}'

Env:
- DASHSCOPE_API_KEY: required
- DASHSCOPE_MODEL: optional (default: qwen-plus)
- DASHSCOPE_BASE_URL: optional (default: https://dashscope.aliyuncs.com/compatible-mode)
- AUTOSKILL_TIMEOUT_S: optional (default: 120)
"""

from __future__ import annotations

import argparse
import os

from autoskill.llm.factory import build_llm


def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None and v.strip() else default


def main() -> None:
    parser = argparse.ArgumentParser(description="DashScope Qwen chat completions demo")
    parser.add_argument("--model", default=_env("DASHSCOPE_MODEL", "qwen-plus"))
    parser.add_argument("--system", default="You are a helpful assistant.")
    parser.add_argument("--user", default="Who are you?")
    args = parser.parse_args()

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key or not api_key.strip():
        raise SystemExit("Missing DASHSCOPE_API_KEY.")

    llm = build_llm(
        {
            "provider": "dashscope",
            "model": str(args.model),
            "api_key": api_key,
            "base_url": _env("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode"),
            "timeout_s": int(_env("AUTOSKILL_TIMEOUT_S", "120")),
        }
    )

    out = llm.complete(system=str(args.system), user=str(args.user), temperature=0.0)
    print(out)


if __name__ == "__main__":
    main()
