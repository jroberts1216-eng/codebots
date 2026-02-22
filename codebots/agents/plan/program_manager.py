from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.llm.provider import LLMProvider
from codebots.tools.models import Plan

SYSTEM = "You are a program manager. Produce a dependency-aware task plan as JSON."


@dataclass(frozen=True)
class ProgramManagerAgent:
    llm: LLMProvider
    meta: AgentMeta = AgentMeta(
        id="program_manager",
        kind="planning",
        specialties=["work breakdown", "dependencies", "sequencing"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any], goal: str) -> Plan:
        user = {
            "goal": goal,
            "repo_signals": repo_context.get("scan", {}).get("signals", {}),
            "key_files": repo_context.get("scan", {}).get("key_files", []),
            "available_execution_roles": [
                "platform_engineer",
                "software_engineer",
                "qa_engineer",
                "reviewer",
            ],
        }
        return self.llm.chat_json(SYSTEM, json_dumps(user), Plan)


def json_dumps(x: Any) -> str:
    import json

    return json.dumps(x, indent=2, sort_keys=True)
