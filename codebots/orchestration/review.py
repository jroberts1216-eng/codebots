from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, cast

from codebots.agents.registry import make_agent
from codebots.tools.models import ReviewReport


@dataclass(frozen=True)
class ReviewRunner:
    enabled_agents: list[str]
    parallel: bool = True

    def run(self, *, repo_context: dict[str, Any]) -> list[ReviewReport]:
        reports: list[ReviewReport] = []

        def _run_one(agent_id: str) -> ReviewReport:
            agent = make_agent(agent_id)
            return cast(ReviewReport, agent.run(repo_context=repo_context))

        review_ids = [
            a
            for a in self.enabled_agents
            if a.endswith("_review")
            or a
            in {
                "repo_overview",
                "build_system",
                "quality",
                "security",
                "dependencies",
                "docs",
                "architecture_review",
            }
        ]
        if not self.parallel or len(review_ids) <= 1:
            for aid in review_ids:
                reports.append(_run_one(aid))
            return reports

        with ThreadPoolExecutor(max_workers=min(8, len(review_ids))) as ex:
            futs = {ex.submit(_run_one, aid): aid for aid in review_ids}
            for fut in as_completed(futs):
                reports.append(fut.result())
        # stable order
        return sorted(reports, key=lambda r: r.agent)
