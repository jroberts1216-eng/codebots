from __future__ import annotations

from codebots.agents.base import Agent, AgentContext
from codebots.core.models import Architecture, PRD, Role, WorkDAG


class ProgramManagerAgent(Agent[WorkDAG]):
    role = Role.program_manager.value
    name = "program_manager"

    def create_work_dag(
        self, ctx: AgentContext, goal: str, prd: PRD, architecture: Architecture
    ) -> WorkDAG:
        prompt = f"""You are a program manager. Break work into an executable dependency graph.

SCHEMA:WORK_DAG
Return ONLY valid JSON that matches the WorkDAG schema.

Goal:
{goal}

PRD (JSON):
{prd.model_dump_json(indent=2)}

Architecture (JSON):
{architecture.model_dump_json(indent=2)}

Repository file tree:
{ctx.repo_tree()}

Constraints:
- Work items must be small enough for a single PR.
- Use stable IDs like w1, w2, w3...
- Set `owner` to one of:
  - product_manager, architect, program_manager, platform_engineer, software_engineer, qa_engineer, security_engineer, reviewer
"""
        return self.run(ctx, prompt, WorkDAG)
