from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar
from pydantic import BaseModel

from .provider import LLMResponse

SchemaT = TypeVar("SchemaT", bound=BaseModel)


@dataclass(frozen=True)
class MockProvider:
    name: str = "mock"

    def chat(self, system: str, user: str) -> LLMResponse:
        # Deterministic placeholder; useful for tests.
        return LLMResponse(text=f"[mock] {user[:200]}")

    def chat_json(self, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        # Return minimal valid objects for known schemas.
        name = schema.__name__
        if name == "PRD":
            return schema.model_validate(
                {
                    "problem": "mock problem",
                    "scope": ["mock scope"],
                    "non_goals": ["mock non-goal"],
                    "acceptance_criteria": ["mock acceptance"],
                }
            )
        if name == "Architecture":
            return schema.model_validate(
                {
                    "overview": "mock overview",
                    "components": ["mock component"],
                    "risks": ["mock risk"],
                    "decisions": ["mock decision"],
                }
            )
        if name == "Plan":
            return schema.model_validate(
                {
                    "goal": "mock goal",
                    "tasks": [
                        {
                            "id": "T1",
                            "title": "mock task",
                            "owner": "software_engineer",
                            "deps": [],
                            "acceptance": ["mock"],
                        }
                    ],
                }
            )
        return schema.model_validate({})
