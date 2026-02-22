from __future__ import annotations

from typing import Any

from codebots.agents.base import AgentMeta

# Built-ins are registered manually to keep discovery explicit.
from codebots.agents.review.repo_overview import RepoOverviewAgent
from codebots.agents.review.build_system import BuildSystemReviewAgent
from codebots.agents.review.quality import QualityReviewAgent
from codebots.agents.review.security import SecurityReviewAgent
from codebots.agents.review.dependencies import DependencyReviewAgent
from codebots.agents.review.docs import DocsReviewAgent
from codebots.agents.review.architecture import ArchitectureReviewAgent

from codebots.agents.plan.product_manager import ProductManagerAgent
from codebots.agents.plan.architect import ArchitectAgent
from codebots.agents.plan.program_manager import ProgramManagerAgent

from codebots.agents.exec.platform_engineer import PlatformEngineerAgent
from codebots.agents.exec.software_engineer import SoftwareEngineerAgent
from codebots.agents.exec.qa_engineer import QAEngineerAgent
from codebots.agents.exec.reviewer import ReviewerAgent

BUILTINS: dict[str, Any] = {
    # Review
    "repo_overview": RepoOverviewAgent,
    "build_system": BuildSystemReviewAgent,
    "quality": QualityReviewAgent,
    "security": SecurityReviewAgent,
    "dependencies": DependencyReviewAgent,
    "docs": DocsReviewAgent,
    "architecture_review": ArchitectureReviewAgent,
    # Planning
    "product_manager": ProductManagerAgent,
    "architect": ArchitectAgent,
    "program_manager": ProgramManagerAgent,
    # Execution
    "platform_engineer": PlatformEngineerAgent,
    "software_engineer": SoftwareEngineerAgent,
    "qa_engineer": QAEngineerAgent,
    "reviewer": ReviewerAgent,
}


def list_agents() -> list[AgentMeta]:
    out: list[AgentMeta] = []
    for _id, cls in BUILTINS.items():
        out.append(cls.meta)
    return sorted(out, key=lambda m: (m.kind, m.id))


def make_agent(agent_id: str, **kwargs: Any) -> Any:
    if agent_id not in BUILTINS:
        raise KeyError(f"unknown agent: {agent_id}")
    return BUILTINS[agent_id](**kwargs)
