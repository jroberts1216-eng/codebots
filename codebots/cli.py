from __future__ import annotations

from pathlib import Path
import typer
from rich import print
from rich.table import Table

from codebots.logging import setup_logging
from codebots.config import load_config, write_default_config
from codebots.llm.factory import make_provider
from codebots.agents.registry import list_agents
from codebots.orchestration.context import build_repo_context
from codebots.orchestration.artifacts import ArtifactStore, new_run_id
from codebots.orchestration.review import ReviewRunner
from codebots.orchestration.plan import Planner
from codebots.orchestration.execute import Executor

app = typer.Typer(
    add_completion=False, help="codebots: drop-in multi-agent review/plan/execute for any repo"
)


@app.command()
def init(repo: Path = typer.Option(Path("."), exists=True, file_okay=False, dir_okay=True)) -> None:
    """Create .codebots/config.toml in the target repo (if missing)."""
    setup_logging()
    p = write_default_config(repo)
    print(f"[green]Wrote[/green] {p}")


@app.command()
def agents_cmd() -> None:
    """List built-in agents."""
    setup_logging()
    t = Table(title="Agents")
    t.add_column("id")
    t.add_column("kind")
    t.add_column("specialties")
    t.add_column("writes")
    t.add_column("runs_cmds")
    for m in list_agents():
        t.add_row(m.id, m.kind, ", ".join(m.specialties), str(m.can_write), str(m.can_run_commands))
    print(t)


@app.command("review")
def review_cmd(
    repo: Path = typer.Option(Path("."), exists=True, file_okay=False, dir_okay=True),
    out: str = typer.Option("review.json", help="Artifact filename"),
) -> None:
    """Run any number of review agents over the repo and write a report artifact."""
    setup_logging()
    cfg = load_config(repo)
    ctx = build_repo_context(repo)
    run_id = new_run_id()
    store = ArtifactStore(repo=repo, run_id=run_id)

    rr = ReviewRunner(enabled_agents=cfg.agents.enabled, parallel=cfg.agents.parallel_reviews)
    reports = rr.run(repo_context=ctx)
    store.write_json(out, [r.model_dump() for r in reports])
    print(f"[green]Wrote[/green] {store.root / out}")


@app.command("plan")
def plan_cmd(
    repo: Path = typer.Option(Path("."), exists=True, file_okay=False, dir_okay=True),
    goal: str = typer.Option(..., help="High-level objective"),
    out: str = typer.Option("plan.json", help="Artifact filename"),
) -> None:
    """Generate PRD + architecture + dependency-aware plan."""
    setup_logging()
    cfg = load_config(repo)
    llm = make_provider(cfg.llm)
    ctx = build_repo_context(repo)
    run_id = new_run_id()
    store = ArtifactStore(repo=repo, run_id=run_id)

    planner = Planner(llm=llm, enabled_agents=cfg.agents.enabled)
    artifact = planner.run(repo_context=ctx, goal=goal)
    store.write_json(out, artifact)
    print(f"[green]Wrote[/green] {store.root / out}")


@app.command("run")
def run_cmd(
    repo: Path = typer.Option(Path("."), exists=True, file_okay=False, dir_okay=True),
    goal: str = typer.Option("", help="High-level objective (if omitted, prompts)"),
    apply: bool = typer.Option(False, help="Apply patches (default: dry-run)"),
) -> None:
    """Plan + execute + verify (with bounded fix loop)."""
    setup_logging()
    if not goal:
        goal = typer.prompt("Goal")

    cfg = load_config(repo)
    llm = make_provider(cfg.llm)
    ctx = build_repo_context(repo)
    run_id = new_run_id()
    store = ArtifactStore(repo=repo, run_id=run_id)

    planner = Planner(llm=llm, enabled_agents=cfg.agents.enabled)
    plan_art = planner.run(repo_context=ctx, goal=goal)
    store.write_json("plan.json", plan_art)

    ex = Executor(
        repo=repo,
        enabled_agents=cfg.agents.enabled,
        verify_commands=cfg.verify.commands,
        allow_prefixes=cfg.verify.allow,
        max_fix_cycles=1,
    )
    result = ex.run(repo_context=ctx, plan=plan_art, apply=apply)
    store.write_json("run.json", result)
    print(f"[green]Wrote[/green] {store.root / 'run.json'}")
    if not apply:
        print(
            "[yellow]Dry-run[/yellow]: re-run with --apply to apply patches (when execution agents are enabled for writing)."
        )


if __name__ == "__main__":
    app()
