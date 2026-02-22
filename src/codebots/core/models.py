from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    product_manager = "product_manager"
    architect = "architect"
    program_manager = "program_manager"
    platform_engineer = "platform_engineer"
    software_engineer = "software_engineer"
    qa_engineer = "qa_engineer"
    security_engineer = "security_engineer"
    reviewer = "reviewer"


class PRD(BaseModel):
    title: str
    problem_statement: str
    in_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class Architecture(BaseModel):
    summary: str
    components: list[str] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)


class WorkItem(BaseModel):
    id: str
    title: str
    description: str
    owner: Role
    depends_on: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class WorkDAG(BaseModel):
    work_items: list[WorkItem]


class Plan(BaseModel):
    goal: str
    prd: PRD
    architecture: Architecture
    work_items: list[WorkItem]


class FileChange(BaseModel):
    path: str
    content: str
    mode: str = "text"  # reserved for future (binary, etc.)


class WorkOutput(BaseModel):
    work_item_id: str
    summary: str
    changes: list[FileChange] = Field(default_factory=list)
    follow_ups: list[WorkItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class VerifyResult(BaseModel):
    ok: bool
    command_results: list[dict[str, Any]] = Field(default_factory=list)
    combined_output: str = ""
