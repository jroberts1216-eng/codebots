from pathlib import Path
from codebots.orchestration.context import build_repo_context
from codebots.orchestration.review import ReviewRunner


def test_review_runs(tmp_path: Path):
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")
    ctx = build_repo_context(tmp_path)
    rr = ReviewRunner(enabled_agents=["repo_overview", "docs"], parallel=False)
    reports = rr.run(repo_context=ctx)
    assert {r.agent for r in reports} == {"repo_overview", "docs"}
