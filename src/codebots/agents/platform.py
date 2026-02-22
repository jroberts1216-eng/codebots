from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import Role, WorkItem, WorkOutput


class PlatformEngineerAgent(Agent[WorkOutput]):
    role = Role.platform_engineer.value
    name = "platform_engineer"

    def execute(self, ctx: AgentContext, item: WorkItem) -> WorkOutput:
        prompt = f"""You are a platform engineer. Implement the work item by proposing file changes.

SCHEMA:WORK_OUTPUT
WORK_ITEM_ID={item.id}
Return ONLY valid JSON that matches the WorkOutput schema.

Work item (JSON):
{item.model_dump_json(indent=2)}

Repository file tree:
{ctx.repo_tree()}

Rules:
- Prefer minimal changes.
- If you propose file changes, include full file contents.
- If you cannot safely implement, leave changes empty and add notes.
"""
        return self.run(ctx, prompt, WorkOutput)
