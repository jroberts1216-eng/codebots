from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport


@dataclass(frozen=True)
class RepoOverviewAgent:
    meta: AgentMeta = AgentMeta(
        id="repo_overview",
        kind="review",
        specialties=["repo inventory", "tech stack detection", "risk surfacing"],
        can_write=False,
        can_run_commands=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        signals = repo_context.get("scan", {}).get("signals", {})
        langs = signals.get("languages", [])
        frameworks = signals.get("likely_frameworks", [])
        key_files = repo_context.get("scan", {}).get("key_files", [])
        return ReviewReport(
            agent=self.meta.id,
            summary=f"Detected languages={langs}, frameworks={frameworks}, key_files={key_files}",
            findings=[],
        )
