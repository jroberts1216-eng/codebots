from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta


@dataclass(frozen=True)
class ReviewerAgent:
    meta: AgentMeta = AgentMeta(
        id="reviewer",
        kind="execution",
        specialties=["code review", "risk spotting", "acceptance check"],
        can_write=False,
        can_run_commands=False,
    )

    def run(self, *, repo_context: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
        return {
            "task_id": task.get("id"),
            "status": "ok",
            "notes": "reviewer stub: no-op (summarize diffs in future).",
        }
