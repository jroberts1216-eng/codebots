from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codebots.agents.base import AgentMeta
from codebots.tools.models import ReviewReport, Finding

SECRET_HINTS = ["AKIA", "BEGIN PRIVATE KEY", "xoxb-", "-----BEGIN", "sk-", "AIza"]


@dataclass(frozen=True)
class SecurityReviewAgent:
    meta: AgentMeta = AgentMeta(
        id="security",
        kind="review",
        specialties=["secrets hygiene", "basic hardening", "security posture"],
        can_write=False,
    )

    def run(self, *, repo_context: dict[str, Any]) -> ReviewReport:
        findings: list[Finding] = []
        # heuristic: look for common secret markers in a small set of key files
        key_snips: dict[str, str] = repo_context.get("key_snippets", {})
        hits = []
        for path, txt in key_snips.items():
            for hint in SECRET_HINTS:
                if hint in txt:
                    hits.append(f"{path}: contains '{hint}'")
        if hits:
            findings.append(
                Finding(
                    id="possible_secrets",
                    title="Possible secret material detected in key files",
                    severity="high",
                    evidence=hits[:10],
                    recommendation="Rotate exposed credentials if any are real secrets, remove from git history, and use env/secret manager.",
                )
            )
        return ReviewReport(
            agent=self.meta.id, summary=f"secret_markers_hits={len(hits)}", findings=findings
        )
