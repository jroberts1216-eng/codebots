from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Literal


class ToolCall(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    name: str
    ok: bool
    output: str
    data: dict[str, Any] = Field(default_factory=dict)


class Severity(str):
    pass


class Finding(BaseModel):
    id: str
    title: str
    severity: Literal["low", "medium", "high"]
    evidence: list[str] = Field(default_factory=list)
    recommendation: str


class ReviewReport(BaseModel):
    agent: str
    summary: str
    findings: list[Finding] = Field(default_factory=list)


class PRD(BaseModel):
    problem: str
    scope: list[str]
    non_goals: list[str]
    acceptance_criteria: list[str]


class Architecture(BaseModel):
    overview: str
    components: list[str]
    risks: list[str]
    decisions: list[str]


class Task(BaseModel):
    id: str
    title: str
    owner: str
    deps: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(default_factory=list)


class Plan(BaseModel):
    goal: str
    tasks: list[Task]
