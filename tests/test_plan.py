from __future__ import annotations

from pathlib import Path

from codebots.workflows.plan import run_plan


def test_run_plan_writes_artifacts(tmp_path: Path) -> None:
    # Minimal repo structure
    (tmp_path / "README.md").write_text("demo", encoding="utf-8")
    plan, run_paths = run_plan(repo_path=tmp_path, goal="demo goal")
    assert plan.goal == "demo goal"
    assert plan.work_items
    assert run_paths.plan_path.exists()
    assert run_paths.events_path.exists()
