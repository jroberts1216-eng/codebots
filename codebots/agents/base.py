from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Literal, Any

from codebots.tools.models import ReviewReport

AgentKind = Literal["review", "planning", "execution"]


@dataclass(frozen=True)
class AgentMeta:
    id: str
    kind: AgentKind
    specialties: list[str]
    can_write: bool = False
    can_run_commands: bool = False


class ReviewAgent(Protocol):
    meta: AgentMeta

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport: ...


class PlanningAgent(Protocol):
    meta: AgentMeta

    def run(self, *, repo_context: dict[str, Any], goal: str) -> Any: ...


class ExecutionAgent(Protocol):
    meta: AgentMeta

    def run(self, *, repo_context: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]: ...
