from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport, Finding


@dataclass(frozen=True)
class DocsReviewAgent:
    meta: AgentMeta = AgentMeta(
        id="docs",
        kind="review",
        specialties=["documentation", "onboarding", "runbooks"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        files = set(repo_context.get("files", []))
        findings: list[Finding] = []
        if "README.md" not in files:
            findings.append(
                Finding(
                    id="readme_missing",
                    title="README.md missing",
                    severity="medium",
                    evidence=[],
                    recommendation="Add a README with setup, run, test, and deploy instructions.",
                )
            )
        if not any(p.startswith("docs/") for p in files):
            findings.append(
                Finding(
                    id="docs_dir_missing",
                    title="No docs/ directory detected",
                    severity="low",
                    evidence=[],
                    recommendation="Consider docs/ for architecture notes, runbooks, and ADRs.",
                )
            )
        return ReviewReport(
            agent=self.meta.id, summary="documentation checks completed", findings=findings
        )
