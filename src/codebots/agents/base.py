from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from codebots.config import CodebotsConfig
from codebots.core.events import Event, EventLogger
from codebots.core.repo import summarize_tree
from codebots.llm.base import StructuredLLM


@dataclass(frozen=True)
class AgentContext:
    repo_path: Path
    config: CodebotsConfig
    llm: StructuredLLM
    events: EventLogger

    def repo_tree(self, max_files: int = 200) -> str:
        return summarize_tree(self.repo_path, max_files=max_files)


T = TypeVar("T", bound=BaseModel)


class Agent(Generic[T]):
    role: str  # Role value as string (for logging)
    name: str

    def run(self, ctx: AgentContext, prompt: str, model_type: type[T]) -> T:
        ctx.events.emit(Event.now("agent.start", role=self.role, name=self.name))
        out = ctx.llm.complete_model(model_type, prompt)
        ctx.events.emit(
            Event.now("agent.end", role=self.role, name=self.name, model=model_type.__name__)
        )
        return out
