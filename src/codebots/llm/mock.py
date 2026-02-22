from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from codebots.llm.base import LLMClient


@dataclass
class MockLLMClient(LLMClient):
    """Deterministic mock LLM.

    It returns JSON strings so structured parsing works in CI.
    """

    seed: str = "codebots-mock"

    def complete(self, prompt: str) -> str:
        h = hashlib.sha256((self.seed + "\n" + prompt).encode("utf-8")).hexdigest()[:8]
        # Heuristics: choose a response shape based on prompt markers.
        if "SCHEMA:PRD" in prompt:
            return json.dumps(
                {
                    "title": f"PRD {h}",
                    "problem_statement": "Mock problem statement.",
                    "in_scope": ["Generate a plan", "Create files", "Run verification"],
                    "out_of_scope": ["Production deployment"],
                    "requirements": ["Must be testable", "Must have CI"],
                    "acceptance_criteria": ["CI passes", "Artifacts are produced"],
                    "risks": ["Mock output may not reflect real repo complexity."],
                }
            )
        if "SCHEMA:ARCHITECTURE" in prompt:
            return json.dumps(
                {
                    "summary": "Mock architecture summary.",
                    "components": ["CLI", "Orchestrator", "Agents", "Verifier", "Artifacts"],
                    "key_decisions": ["Typed agent outputs", "Repo verify loop"],
                    "constraints": ["Offline by default"],
                    "tradeoffs": ["Mock provider vs real LLM quality"],
                }
            )
        if "SCHEMA:WORK_DAG" in prompt:
            return json.dumps(
                {
                    "work_items": [
                        {
                            "id": "w1",
                            "title": "Add a placeholder file",
                            "description": "Create a file to demonstrate apply_changes.",
                            "owner": "software_engineer",
                            "depends_on": [],
                            "acceptance_criteria": ["File exists in repo"],
                            "tags": ["demo"],
                        },
                        {
                            "id": "w2",
                            "title": "Add a placeholder test",
                            "description": "Create a trivial pytest to verify CI plumbing.",
                            "owner": "qa_engineer",
                            "depends_on": ["w1"],
                            "acceptance_criteria": ["pytest passes"],
                            "tags": ["demo", "tests"],
                        },
                    ],
                }
            )
        if "SCHEMA:WORK_OUTPUT" in prompt:
            # Very small change for safety
            work_id = "unknown"
            marker = "WORK_ITEM_ID="
            if marker in prompt:
                work_id = prompt.split(marker, 1)[1].splitlines()[0].strip()
            return json.dumps(
                {
                    "work_item_id": work_id,
                    "summary": "Mock work output.",
                    "changes": [],
                    "follow_ups": [],
                    "notes": ["No changes applied (mock)."],
                }
            )
        return json.dumps({"text": f"Mock response {h}"})
