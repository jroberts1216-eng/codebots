from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport, Finding


@dataclass(frozen=True)
class DependencyReviewAgent:
    meta: AgentMeta = AgentMeta(
        id="dependencies",
        kind="review",
        specialties=["dependency hygiene", "pinning", "lockfiles"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        files = set(repo_context.get("files", []))
        findings: list[Finding] = []
        if "package.json" in files and not any(
            f in files for f in ["package-lock.json", "pnpm-lock.yaml", "yarn.lock"]
        ):
            findings.append(
                Finding(
                    id="node_lock_missing",
                    title="Node lockfile missing",
                    severity="medium",
                    evidence=["package.json present; no lockfile detected"],
                    recommendation="Commit a lockfile (npm/pnpm/yarn) for reproducible installs.",
                )
            )
        if (
            "requirements.txt" in files
            and "requirements.lock" not in files
            and "poetry.lock" not in files
        ):
            findings.append(
                Finding(
                    id="python_lock_missing",
                    title="Python dependency locking not detected",
                    severity="low",
                    evidence=["requirements.txt present; no obvious lockfile detected"],
                    recommendation="Consider a lockfile strategy (poetry/pip-tools/uv) for reproducible builds.",
                )
            )
        return ReviewReport(
            agent=self.meta.id, summary="dependency checks completed", findings=findings
        )
