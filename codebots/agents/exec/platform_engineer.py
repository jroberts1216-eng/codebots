from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta


@dataclass(frozen=True)
class PlatformEngineerAgent:
    meta: AgentMeta = AgentMeta(
        id="platform_engineer",
        kind="execution",
        specialties=["CI/CD", "build pipelines", "tooling"],
        can_write=True,
        can_run_commands=True,
    )

    def run(self, *, repo_context: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
        # Stub: In LLM mode this would propose patches and/or CI templates.
        return {
            "task_id": task.get("id"),
            "status": "skipped",
            "notes": "platform_engineer is stub in v0.2.0 (no changes applied).",
            "patches": [],
        }
