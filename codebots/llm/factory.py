from __future__ import annotations

from codebots.config import LLMConfig
from codebots.llm.mock import MockProvider
from codebots.llm.openai_compat import OpenAICompatProvider
from codebots.llm.provider import LLMProvider


def make_provider(cfg: LLMConfig) -> LLMProvider:
    if cfg.provider == "mock":
        return MockProvider()
    return OpenAICompatProvider(
        base_url=cfg.base_url,
        model=cfg.model,
        api_key_env=cfg.api_key_env,
        timeout_seconds=cfg.timeout_seconds,
    )
