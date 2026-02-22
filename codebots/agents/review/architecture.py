from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport, Finding


@dataclass(frozen=True)
class ArchitectureReviewAgent:
    meta: AgentMeta = AgentMeta(
        id="architecture_review",
        kind="review",
        specialties=["architecture", "modularity", "boundaries"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        scan = repo_context.get("scan", {})
        frameworks = scan.get("signals", {}).get("likely_frameworks", [])
        findings: list[Finding] = []
        if "docker" in frameworks and not scan.get("signals", {}).get("has_github_actions", False):
            findings.append(
                Finding(
                    id="docker_without_ci",
                    title="Docker detected but CI not detected",
                    severity="low",
                    evidence=[],
                    recommendation="Add CI that builds (and optionally runs) containers to catch regressions early.",
                )
            )
        return ReviewReport(
            agent=self.meta.id, summary=f"frameworks={frameworks}", findings=findings
        )
