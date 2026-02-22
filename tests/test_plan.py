from __future__ import annotations

from pathlib import Path

from codebots.llm.mock import MockProvider
from codebots.orchestration.context import build_repo_context
from codebots.orchestration.execute import Executor
from codebots.orchestration.plan import Planner


def test_planner_and_executor_run_with_mock(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("demo", encoding="utf-8")
    ctx = build_repo_context(tmp_path)

    planner = Planner(
        llm=MockProvider(), enabled_agents=["product_manager", "architect", "program_manager"]
    )
    plan = planner.run(repo_context=ctx, goal="demo goal")
    assert plan["goal"] == "demo goal"
    assert plan["plan"] is not None

    executor = Executor(
        repo=tmp_path,
        enabled_agents=["software_engineer", "qa_engineer", "platform_engineer", "reviewer"],
        verify_commands=[],
        allow_prefixes=[],
    )
    result = executor.run(repo_context=ctx, plan=plan, apply=False)
    assert "events" in result
