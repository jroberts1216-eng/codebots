from __future__ import annotations

from dataclasses import dataclass

from codebots.agents.architect import ArchitectAgent
from codebots.agents.pgm import ProgramManagerAgent
from codebots.agents.platform import PlatformEngineerAgent
from codebots.agents.pm import ProductManagerAgent
from codebots.agents.qa import QAEngineerAgent
from codebots.agents.reviewer import CodeReviewerAgent
from codebots.agents.security import SecurityEngineerAgent
from codebots.agents.swe import SoftwareEngineerAgent
from codebots.core.models import Role


@dataclass(frozen=True)
class AgentPack:
    product_manager: ProductManagerAgent
    architect: ArchitectAgent
    program_manager: ProgramManagerAgent
    platform_engineer: PlatformEngineerAgent
    software_engineer: SoftwareEngineerAgent
    qa_engineer: QAEngineerAgent
    security_engineer: SecurityEngineerAgent
    reviewer: CodeReviewerAgent

    def for_role(self, role: Role):
        if role == Role.product_manager:
            return self.product_manager
        if role == Role.architect:
            return self.architect
        if role == Role.program_manager:
            return self.program_manager
        if role == Role.platform_engineer:
            return self.platform_engineer
        if role == Role.software_engineer:
            return self.software_engineer
        if role == Role.qa_engineer:
            return self.qa_engineer
        if role == Role.security_engineer:
            return self.security_engineer
        if role == Role.reviewer:
            return self.reviewer
        raise ValueError(f"Unknown role: {role}")


DEFAULT_AGENT_PACK = AgentPack(
    product_manager=ProductManagerAgent(),
    architect=ArchitectAgent(),
    program_manager=ProgramManagerAgent(),
    platform_engineer=PlatformEngineerAgent(),
    software_engineer=SoftwareEngineerAgent(),
    qa_engineer=QAEngineerAgent(),
    security_engineer=SecurityEngineerAgent(),
    reviewer=CodeReviewerAgent(),
)
