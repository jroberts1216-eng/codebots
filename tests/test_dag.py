from __future__ import annotations

from pathlib import Path

from codebots.llm.mock import MockProvider
from codebots.orchestration.context import build_repo_context
from codebots.orchestration.plan import Planner


def test_plan_output_contains_dependency_fields(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("demo", encoding="utf-8")
    ctx = build_repo_context(tmp_path)
    planner = Planner(
        llm=MockProvider(), enabled_agents=["product_manager", "architect", "program_manager"]
    )
    out = planner.run(repo_context=ctx, goal="demo goal")
    assert out["goal"] == "demo goal"
    assert out["plan"] is not None
    tasks = out["plan"]["tasks"]
    assert tasks
    assert "deps" in tasks[0]
