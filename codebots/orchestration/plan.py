from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.registry import make_agent
from codebots.llm.provider import LLMProvider
from codebots.tools.models import PRD, Architecture, Plan


@dataclass(frozen=True)
class Planner:
    llm: LLMProvider
    enabled_agents: list[str]

    def run(self, *, repo_context: dict[str, Any], goal: str) -> dict[str, Any]:
        # Run in a fixed order to keep artifacts stable.
        prd: PRD | None = None
        arch: Architecture | None = None
        plan: Plan | None = None

        if "product_manager" in self.enabled_agents:
            prd = make_agent("product_manager", llm=self.llm).run(
                repo_context=repo_context, goal=goal
            )
        if "architect" in self.enabled_agents:
            arch = make_agent("architect", llm=self.llm).run(repo_context=repo_context, goal=goal)
        if "program_manager" in self.enabled_agents:
            plan = make_agent("program_manager", llm=self.llm).run(
                repo_context=repo_context, goal=goal
            )

        return {
            "goal": goal,
            "prd": prd.model_dump() if prd else None,
            "architecture": arch.model_dump() if arch else None,
            "plan": plan.model_dump() if plan else None,
        }
