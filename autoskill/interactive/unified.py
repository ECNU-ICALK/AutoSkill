"""
Unified runtime composition for interactive + proxy modes.

`AutoSkillRuntime` keeps one SDK/config stack and exposes:
- `new_session(...)` for programmatic interactive chat sessions
- `new_proxy_runtime(...)` / `create_proxy_server(...)` for OpenAI-compatible proxy serving
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from ..client import AutoSkill
from .config import InteractiveConfig
from .rewriting import LLMQueryRewriter
from .selection import LLMSkillSelector
from .server import AutoSkillProxyConfig, AutoSkillProxyRuntime
from .session import InteractiveSession
from ..management.bootstrap import run_service_startup_maintenance
from ..llm.factory import build_llm


class AutoSkillRuntime:
    """
    Unified composition root for interactive and proxy modes.

    This class does not replace existing entrypoints; it centralizes shared wiring.
    """

    def __init__(
        self,
        *,
        sdk: AutoSkill,
        llm_config: Dict[str, Any],
        embeddings_config: Dict[str, Any],
        interactive_config: Optional[InteractiveConfig] = None,
        proxy_config: Optional[AutoSkillProxyConfig] = None,
        query_rewriter: Optional[LLMQueryRewriter] = None,
        skill_selector: Optional[LLMSkillSelector] = None,
    ) -> None:
        """Run init."""
        self.sdk = sdk
        self.llm_config = dict(llm_config or {})
        self.embeddings_config = dict(embeddings_config or {})
        self.interactive_config = (interactive_config or InteractiveConfig()).normalize()
        self.proxy_config = (proxy_config or AutoSkillProxyConfig()).normalize()
        self.startup_maintenance = run_service_startup_maintenance(
            sdk=self.sdk,
            default_user_id=str(self.interactive_config.user_id or "u1"),
            log_prefix="[runtime]",
        )

        if query_rewriter is not None:
            self.query_rewriter = query_rewriter
        else:
            provider = str(self.llm_config.get("provider") or "mock").lower()
            if provider == "mock" or str(self.interactive_config.rewrite_mode).lower() == "never":
                self.query_rewriter = None
            else:
                self.query_rewriter = LLMQueryRewriter(build_llm(dict(self.llm_config)))
        self.skill_selector = skill_selector

    def new_session(
        self,
        *,
        config_override: Optional[InteractiveConfig] = None,
    ) -> InteractiveSession:
        """Run new session."""
        cfg = (config_override or InteractiveConfig(**asdict(self.interactive_config))).normalize()
        provider = str(self.llm_config.get("provider") or "mock").lower()
        chat_llm = None if provider == "mock" else build_llm(dict(self.llm_config))
        return InteractiveSession(
            sdk=self.sdk,
            config=cfg,
            chat_llm=chat_llm,
            query_rewriter=self.query_rewriter,
            skill_selector=self.skill_selector,
        )

    def new_proxy_runtime(
        self,
        *,
        config_override: Optional[AutoSkillProxyConfig] = None,
    ) -> AutoSkillProxyRuntime:
        """Run new proxy runtime."""
        cfg = (config_override or AutoSkillProxyConfig(**asdict(self.proxy_config))).normalize()
        return AutoSkillProxyRuntime(
            sdk=self.sdk,
            llm_config=dict(self.llm_config),
            embeddings_config=dict(self.embeddings_config),
            config=cfg,
            query_rewriter=self.query_rewriter,
            skill_selector=self.skill_selector,
        )

    def create_proxy_server(
        self,
        *,
        host: str,
        port: int,
        config_override: Optional[AutoSkillProxyConfig] = None,
    ):
        """Run create proxy server."""
        runtime = self.new_proxy_runtime(config_override=config_override)
        return runtime.create_server(host=host, port=port)
