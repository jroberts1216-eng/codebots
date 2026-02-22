from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.llm.provider import LLMProvider
from codebots.tools.models import PRD

SYSTEM = "You are a product manager. Produce a concise PRD as JSON."


@dataclass(frozen=True)
class ProductManagerAgent:
    llm: LLMProvider
    meta: AgentMeta = AgentMeta(
        id="product_manager",
        kind="planning",
        specialties=["requirements", "acceptance criteria", "scope"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any], goal: str) -> PRD:
        user = {
            "goal": goal,
            "repo_signals": repo_context.get("scan", {}).get("signals", {}),
            "key_files": repo_context.get("scan", {}).get("key_files", []),
        }
        return self.llm.chat_json(SYSTEM, json_dumps(user), PRD)


def json_dumps(x: Any) -> str:
    import json

    return json.dumps(x, indent=2, sort_keys=True)
