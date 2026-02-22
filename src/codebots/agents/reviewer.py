from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import Role, WorkItem, WorkOutput


class CodeReviewerAgent(Agent[WorkOutput]):
    role = Role.reviewer.value
    name = "reviewer"

    def execute(self, ctx: AgentContext, item: WorkItem) -> WorkOutput:
        prompt = f"""You are a strict code reviewer. Suggest improvements or request changes.

SCHEMA:WORK_OUTPUT
WORK_ITEM_ID={item.id}
Return ONLY valid JSON that matches the WorkOutput schema.

Work item (JSON):
{item.model_dump_json(indent=2)}

Repository file tree:
{ctx.repo_tree()}

Rules:
- If no changes are required, leave `changes` empty and add notes.
- Focus on correctness, maintainability, and test coverage.
"""
        return self.run(ctx, prompt, WorkOutput)
