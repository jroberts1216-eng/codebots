from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.llm.provider import LLMProvider
from codebots.tools.models import Architecture

SYSTEM = "You are a software architect. Produce a concise architecture proposal as JSON."


@dataclass(frozen=True)
class ArchitectAgent:
    llm: LLMProvider
    meta: AgentMeta = AgentMeta(
        id="architect",
        kind="planning",
        specialties=["architecture", "risk analysis", "system design"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any], goal: str) -> Architecture:
        user = {
            "goal": goal,
            "repo_signals": repo_context.get("scan", {}).get("signals", {}),
            "top_level": repo_context.get("scan", {}).get("top_level", []),
            "key_files": repo_context.get("scan", {}).get("key_files", []),
        }
        return self.llm.chat_json(SYSTEM, json_dumps(user), Architecture)


def json_dumps(x: Any) -> str:
    import json

    return json.dumps(x, indent=2, sort_keys=True)
