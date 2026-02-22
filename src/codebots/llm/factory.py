from __future__ import annotations

from codebots.config import CodebotsConfig
from codebots.llm.base import StructuredLLM
from codebots.llm.mock import MockLLMClient
from codebots.llm.openai_compat import OpenAICompatClient


class ProviderNotConfigured(RuntimeError):
    pass


def create_llm(config: CodebotsConfig) -> StructuredLLM:
    """Create an LLM client from config.

    Only `mock` is implemented in this scaffold to keep CI deterministic.
    Add providers by implementing `LLMClient` and extending this function.
    """
    if config.llm.provider == "mock":
        return StructuredLLM(MockLLMClient())

    if config.llm.provider == "openai_compat":
        if not config.llm.base_url:
            raise ProviderNotConfigured("llm.base_url must be set for provider openai_compat")
        return StructuredLLM(
            OpenAICompatClient(
                base_url=config.llm.base_url,
                model=config.llm.model,
                api_key_env=config.llm.api_key_env,
            )
        )

    raise ProviderNotConfigured(
        f"Provider {config.llm.provider!r} not implemented in this scaffold. "
        "Implement a provider and extend codebots.llm.factory.create_llm()."
    )
