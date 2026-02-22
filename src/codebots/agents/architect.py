from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import Architecture, PRD, Role


class ArchitectAgent(Agent[Architecture]):
    role = Role.architect.value
    name = "architect"

    def create_architecture(self, ctx: AgentContext, prd: PRD) -> Architecture:
        prompt = f"""You are a software architect focused on repo-based delivery.

SCHEMA:ARCHITECTURE
Return ONLY valid JSON that matches the Architecture schema.

PRD (JSON):
{prd.model_dump_json(indent=2)}

Repository file tree (for context):
{ctx.repo_tree()}

Guidelines:
- Prefer decisions that make verification and CI reliable.
- List key components and constraints.
"""
        return self.run(ctx, prompt, Architecture)
