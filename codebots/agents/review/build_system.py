from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport, Finding


@dataclass(frozen=True)
class BuildSystemReviewAgent:
    meta: AgentMeta = AgentMeta(
        id="build_system",
        kind="review",
        specialties=["build systems", "CI signals", "test entrypoints"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        scan = repo_context.get("scan", {})
        build_files = scan.get("signals", {}).get("build_files", [])
        has_actions = scan.get("signals", {}).get("has_github_actions", False)
        findings: list[Finding] = []
        if not build_files:
            findings.append(
                Finding(
                    id="build_files_missing",
                    title="No common build manifest detected",
                    severity="medium",
                    evidence=[],
                    recommendation="Add a build manifest (pyproject.toml/package.json/go.mod/etc.) and document the build/test commands in README.",
                )
            )
        if not has_actions:
            findings.append(
                Finding(
                    id="ci_missing",
                    title="No GitHub Actions workflows detected",
                    severity="medium",
                    evidence=[],
                    recommendation="Add CI workflow that runs formatter/linter/tests and a security scan (optional).",
                )
            )
        return ReviewReport(
            agent=self.meta.id,
            summary=f"build_files={build_files}, github_actions={has_actions}",
            findings=findings,
        )
