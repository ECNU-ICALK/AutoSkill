from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from autoskill.offline.provider_config import build_llm_config


class OfflineProviderConfigTest(unittest.TestCase):
    def test_dashscope_defaults_max_tokens_to_supported_range(self) -> None:
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test-key"}, clear=False):
            cfg = build_llm_config("dashscope", model="qwen-turbo")

        self.assertEqual(cfg["provider"], "dashscope")
        self.assertEqual(cfg["model"], "qwen-turbo")
        self.assertEqual(cfg["max_tokens"], 16384)

    def test_dashscope_max_tokens_can_be_overridden(self) -> None:
        with patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "test-key", "DASHSCOPE_MAX_TOKENS": "8192"},
            clear=False,
        ):
            cfg = build_llm_config("dashscope", model="qwen-plus")

        self.assertEqual(cfg["max_tokens"], 8192)


if __name__ == "__main__":
    unittest.main()
