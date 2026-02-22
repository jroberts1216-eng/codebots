from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta


@dataclass(frozen=True)
class SoftwareEngineerAgent:
    meta: AgentMeta = AgentMeta(
        id="software_engineer",
        kind="execution",
        specialties=["implementation", "refactoring", "integration"],
        can_write=True,
        can_run_commands=False,
    )

    def run(self, *, repo_context: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
        return {
            "task_id": task.get("id"),
            "status": "skipped",
            "notes": "software_engineer is stub in v0.2.0 (no changes applied).",
            "patches": [],
        }
