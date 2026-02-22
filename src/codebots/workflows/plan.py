from __future__ import annotations

from pathlib import Path

from codebots.agents.base import AgentContext
from codebots.agents.registry import AgentPack, DEFAULT_AGENT_PACK
from codebots.config import load_config
from codebots.core.artifacts import RunPaths, dump_model, new_run_id, persist_config
from codebots.core.events import Event, EventLogger
from codebots.core.models import Plan
from codebots.llm.factory import create_llm


def run_plan(repo_path: Path, goal: str, agent_pack: AgentPack | None = None) -> tuple[Plan, RunPaths]:
    repo_path = repo_path.resolve()
    config = load_config(repo_path)
    run_paths = RunPaths.create(repo_path, new_run_id())
    persist_config(run_paths, config)

    events = EventLogger(run_paths.events_path)
    events.emit(Event.now("run.start", goal=goal, repo=str(repo_path), workflow="plan"))

    llm = create_llm(config)
    ctx = AgentContext(repo_path=repo_path, config=config, llm=llm, events=events)

    pack = agent_pack or DEFAULT_AGENT_PACK
    prd = pack.product_manager.create_prd(ctx, goal=goal)
    architecture = pack.architect.create_architecture(ctx, prd=prd)
    work_dag = pack.program_manager.create_work_dag(ctx, goal=goal, prd=prd, architecture=architecture)

    plan = Plan(goal=goal, prd=prd, architecture=architecture, work_items=work_dag.work_items)
    dump_model(run_paths.plan_path, plan)

    events.emit(Event.now("run.end", workflow="plan", ok=True))
    return plan, run_paths
