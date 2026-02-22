from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import Role, WorkItem, WorkOutput


class QAEngineerAgent(Agent[WorkOutput]):
    role = Role.qa_engineer.value
    name = "qa_engineer"

    def execute(self, ctx: AgentContext, item: WorkItem) -> WorkOutput:
        prompt = f"""You are a QA engineer. Add or adjust tests and verification steps.

SCHEMA:WORK_OUTPUT
WORK_ITEM_ID={item.id}
Return ONLY valid JSON that matches the WorkOutput schema.

Work item (JSON):
{item.model_dump_json(indent=2)}

Repository file tree:
{ctx.repo_tree()}

Rules:
- Prefer adding tests over changing production code unless required.
- Keep tests deterministic.
"""
        return self.run(ctx, prompt, WorkOutput)
