from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: dict[str, Any] | None = None


class LLMProvider(Protocol):
    @property
    def name(self) -> str: ...

    def chat(self, system: str, user: str) -> LLMResponse: ...
    def chat_json(self, system: str, user: str, schema: type[SchemaT]) -> SchemaT: ...
