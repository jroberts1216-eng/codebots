from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from codebots.agents.registry import DEFAULT_AGENT_PACK
from codebots.config import write_example_config
from codebots.core.models import Role
from codebots.workflows.build import run_build
from codebots.workflows.plan import run_plan

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def init(
    repo: Path = typer.Option(Path("."), "--repo", help="Target repository path"),
) -> None:
    """Create `.codebots/config.yaml` in the target repo."""
    repo = repo.resolve()
    cfg_path = write_example_config(repo)
    console.print(f"Created config: {cfg_path}")


@app.command()
def agents() -> None:
    """List built-in agent roles."""
    table = Table(title="Built-in agents")
    table.add_column("Role")
    table.add_column("Agent class")
    table.add_row(Role.product_manager.value, type(DEFAULT_AGENT_PACK.product_manager).__name__)
    table.add_row(Role.architect.value, type(DEFAULT_AGENT_PACK.architect).__name__)
    table.add_row(Role.program_manager.value, type(DEFAULT_AGENT_PACK.program_manager).__name__)
    table.add_row(Role.platform_engineer.value, type(DEFAULT_AGENT_PACK.platform_engineer).__name__)
    table.add_row(Role.software_engineer.value, type(DEFAULT_AGENT_PACK.software_engineer).__name__)
    table.add_row(Role.qa_engineer.value, type(DEFAULT_AGENT_PACK.qa_engineer).__name__)
    table.add_row(Role.security_engineer.value, type(DEFAULT_AGENT_PACK.security_engineer).__name__)
    table.add_row(Role.reviewer.value, type(DEFAULT_AGENT_PACK.reviewer).__name__)
    console.print(table)


@app.command()
def plan(
    goal: str = typer.Option(..., "--goal", help="What you want to achieve"),
    repo: Path = typer.Option(Path("."), "--repo", help="Target repository path"),
) -> None:
    """Generate PRD + architecture + work DAG and write artifacts."""
    plan_obj, run_paths = run_plan(repo_path=repo, goal=goal)
    console.print(f"Run: {run_paths.run_dir}")
    console.print(f"Work items: {len(plan_obj.work_items)}")
    console.print(f"Plan artifact: {run_paths.plan_path}")


@app.command()
def build(
    goal: str = typer.Option(..., "--goal", help="What you want to achieve"),
    repo: Path = typer.Option(Path("."), "--repo", help="Target repository path"),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="If set, apply file changes to the repo. Otherwise dry-run.",
    ),
) -> None:
    """Plan + execute + verify (bounded fix loop)."""
    plan_obj, verify, run_paths = run_build(repo_path=repo, goal=goal, apply=apply)
    console.print(f"Run: {run_paths.run_dir}")
    console.print(f"Work items: {len(plan_obj.work_items)}")
    console.print(f"Verify ok: {verify.ok}")
    if not verify.ok:
        console.print(f"See verify logs under: {run_paths.run_dir}")


if __name__ == "__main__":
    app()
