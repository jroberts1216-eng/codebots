from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import Role, WorkItem, WorkOutput


class SecurityEngineerAgent(Agent[WorkOutput]):
    role = Role.security_engineer.value
    name = "security_engineer"

    def execute(self, ctx: AgentContext, item: WorkItem) -> WorkOutput:
        prompt = f"""You are a security engineer. Review the work item for security concerns and propose hardening changes if needed.

SCHEMA:WORK_OUTPUT
WORK_ITEM_ID={item.id}
Return ONLY valid JSON that matches the WorkOutput schema.

Work item (JSON):
{item.model_dump_json(indent=2)}

Repository file tree:
{ctx.repo_tree()}

Rules:
- Only propose changes that are relevant and low-risk.
- Prefer defense-in-depth: CI checks, dependency pinning, safer defaults.
"""
        return self.run(ctx, prompt, WorkOutput)
