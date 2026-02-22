from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


class LLMClient(ABC):
    """Abstract LLM client.

    Implementations should:
    - take a prompt string
    - return a raw string response
    """

    @abstractmethod
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class StructuredLLM:
    """Helper that enforces structured output parsing."""

    def __init__(self, client: LLMClient):
        self._client = client

    def complete_model(self, model_type: type[T], prompt: str) -> T:
        raw = self._client.complete(prompt)
        try:
            return model_type.model_validate_json(raw)
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"Failed to parse model {model_type.__name__} from LLM output. Raw:\n{raw}") from e
