from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codebots.agents.registry import make_agent
from codebots.tools.patch import PatchApplier
from codebots.orchestration.verify import Verifier


@dataclass(frozen=True)
class Executor:
    repo: Path
    enabled_agents: list[str]
    verify_commands: list[str]
    allow_prefixes: list[str]
    max_fix_cycles: int = 1

    def run(
        self, *, repo_context: dict[str, Any], plan: dict[str, Any], apply: bool
    ) -> dict[str, Any]:
        # MVP: Execution agents are stubs; pipeline wiring is real.
        patches_applied = []
        events = []

        verifier = Verifier(repo=self.repo, allow_prefixes=self.allow_prefixes)

        tasks = (plan.get("plan") or {}).get("tasks") or []
        for t in tasks:
            owner = t.get("owner", "software_engineer")
            if owner not in self.enabled_agents:
                events.append(
                    {"task": t.get("id"), "status": "skipped", "reason": f"agent disabled: {owner}"}
                )
                continue

            agent = make_agent(owner)
            out = agent.run(repo_context=repo_context, task=t)
            events.append({"task": t.get("id"), "agent": owner, "output": out})

            for diff in out.get("patches", []):
                if not apply:
                    continue
                ok, msg = PatchApplier(self.repo).apply_unified_diff(diff)
                patches_applied.append({"task": t.get("id"), "ok": ok, "msg": msg})

            if self.verify_commands:
                v = verifier.run(self.verify_commands)
                events.append({"task": t.get("id"), "verify": v})
                if not v["ok"]:
                    # Fix loop stub: in future invoke qa_engineer/fixer agent to generate patch based on logs
                    events.append({"task": t.get("id"), "fix": {"status": "not_implemented"}})

        return {"events": events, "patches_applied": patches_applied}
