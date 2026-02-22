from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport, Finding


@dataclass(frozen=True)
class QualityReviewAgent:
    meta: AgentMeta = AgentMeta(
        id="quality",
        kind="review",
        specialties=["code quality", "testing", "lint/format"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        scan = repo_context.get("scan", {})
        has_tests = scan.get("signals", {}).get("has_tests", False)
        files = repo_context.get("files", [])
        has_precommit = ".pre-commit-config.yaml" in set(files)
        findings: list[Finding] = []
        if not has_tests:
            findings.append(
                Finding(
                    id="tests_missing",
                    title="No tests directory detected",
                    severity="medium",
                    evidence=[],
                    recommendation="Add at least smoke/unit tests and wire them into CI.",
                )
            )
        if not has_precommit:
            findings.append(
                Finding(
                    id="precommit_missing",
                    title="pre-commit configuration not found",
                    severity="low",
                    evidence=[],
                    recommendation="Consider adding pre-commit to standardize formatting/lint checks across developers.",
                )
            )
        return ReviewReport(
            agent=self.meta.id,
            summary=f"has_tests={has_tests}, precommit={has_precommit}",
            findings=findings,
        )
