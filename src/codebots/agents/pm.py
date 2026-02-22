from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import PRD, Role


class ProductManagerAgent(Agent[PRD]):
    role = Role.product_manager.value
    name = "product_manager"

    def create_prd(self, ctx: AgentContext, goal: str) -> PRD:
        prompt = f"""You are a pragmatic product manager.

SCHEMA:PRD
Return ONLY valid JSON that matches the PRD schema.

Goal:
{goal}

Repository file tree (for context):
{ctx.repo_tree()}

Guidelines:
- Keep it implementable.
- Include explicit acceptance criteria.
"""
        return self.run(ctx, prompt, PRD)
