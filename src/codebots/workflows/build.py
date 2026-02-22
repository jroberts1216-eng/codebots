from __future__ import annotations

from pathlib import Path

from codebots.agents.base import AgentContext
from codebots.agents.registry import AgentPack, DEFAULT_AGENT_PACK
from codebots.config import load_config
from codebots.core.artifacts import (
    RunPaths,
    dump_json,
    dump_model,
    new_run_id,
    persist_config,
    work_item_dir,
)
from codebots.core.dag import topo_sort
from codebots.core.events import Event, EventLogger
from codebots.core.models import Plan, Role, VerifyResult, WorkItem, WorkOutput
from codebots.core.repo import apply_changes
from codebots.core.verify import run_verify
from codebots.llm.factory import create_llm


def _execute_item(ctx: AgentContext, pack: AgentPack, item: WorkItem) -> WorkOutput:
    # Planning roles do not "execute" code changes.
    if item.owner in {Role.product_manager, Role.architect, Role.program_manager}:
        return WorkOutput(
            work_item_id=item.id, summary="No-op (planning role).", notes=["Skipped execution."]
        )

    # Execution roles use role-specific execute methods.
    if item.owner == Role.platform_engineer:
        return pack.platform_engineer.execute(ctx, item)
    if item.owner == Role.software_engineer:
        return pack.software_engineer.execute(ctx, item)
    if item.owner == Role.qa_engineer:
        return pack.qa_engineer.execute(ctx, item)
    if item.owner == Role.security_engineer:
        return pack.security_engineer.execute(ctx, item)
    if item.owner == Role.reviewer:
        return pack.reviewer.execute(ctx, item)

    # Fallback (should not happen due to enum)
    return WorkOutput(
        work_item_id=item.id, summary="No-op (unknown role).", notes=["Skipped execution."]
    )


def run_build(
    repo_path: Path,
    goal: str,
    agent_pack: AgentPack | None = None,
    apply: bool = False,
) -> tuple[Plan, VerifyResult, RunPaths]:
    repo_path = repo_path.resolve()
    config = load_config(repo_path)
    run_paths = RunPaths.create(repo_path, new_run_id())
    persist_config(run_paths, config)

    events = EventLogger(run_paths.events_path)
    events.emit(
        Event.now("run.start", goal=goal, repo=str(repo_path), workflow="build", apply=apply)
    )

    llm = create_llm(config)
    ctx = AgentContext(repo_path=repo_path, config=config, llm=llm, events=events)
    pack = agent_pack or DEFAULT_AGENT_PACK

    # --- plan ---
    prd = pack.product_manager.create_prd(ctx, goal=goal)
    architecture = pack.architect.create_architecture(ctx, prd=prd)
    work_dag = pack.program_manager.create_work_dag(
        ctx, goal=goal, prd=prd, architecture=architecture
    )
    plan = Plan(goal=goal, prd=prd, architecture=architecture, work_items=work_dag.work_items)
    dump_model(run_paths.plan_path, plan)
    events.emit(Event.now("plan.complete", work_items=len(plan.work_items)))

    # --- execute ---
    ordered = topo_sort(plan.work_items)
    follow_ups: list[WorkItem] = []

    for item in ordered:
        item_dir = work_item_dir(run_paths, item.id)
        dump_model(item_dir / "input.json", item)

        events.emit(
            Event.now(
                "work_item.start", work_item_id=item.id, owner=item.owner.value, title=item.title
            )
        )
        out = _execute_item(ctx, pack, item)
        dump_model(item_dir / "output.json", out)

        applied_paths: list[str] = []
        if apply and out.changes:
            written = apply_changes(repo_path, out.changes)
            applied_paths = [str(p.relative_to(repo_path)) for p in written]
            dump_json(item_dir / "applied_changes.json", {"paths": applied_paths})
        else:
            dump_json(item_dir / "applied_changes.json", {"paths": [], "dry_run": True})

        follow_ups.extend(out.follow_ups)
        events.emit(
            Event.now(
                "work_item.end",
                work_item_id=item.id,
                owner=item.owner.value,
                applied=len(applied_paths),
                follow_ups=len(out.follow_ups),
            )
        )

    # --- verify ---
    verify = run_verify(repo_path, config.verify.commands)
    (run_paths.run_dir / "verify.log").write_text(verify.combined_output, encoding="utf-8")
    events.emit(Event.now("verify.complete", ok=verify.ok))

    # --- bounded fix loop (optional) ---
    cycles = 0
    while (not verify.ok) and cycles < config.workflows.max_fix_cycles:
        cycles += 1
        fix_item = WorkItem(
            id=f"fix{cycles}",
            title=f"Fix verification failures (cycle {cycles})",
            description=f"Verification output:\n\n{verify.combined_output}",
            owner=Role.software_engineer,
            depends_on=[],
            acceptance_criteria=["verify passes"],
            tags=["fix"],
        )
        item_dir = work_item_dir(run_paths, fix_item.id)
        dump_model(item_dir / "input.json", fix_item)

        out = pack.software_engineer.execute(ctx, fix_item)
        dump_model(item_dir / "output.json", out)
        if apply and out.changes:
            written = apply_changes(repo_path, out.changes)
            dump_json(
                item_dir / "applied_changes.json",
                {"paths": [str(p.relative_to(repo_path)) for p in written]},
            )
        else:
            dump_json(item_dir / "applied_changes.json", {"paths": [], "dry_run": True})

        verify = run_verify(repo_path, config.verify.commands)
        (run_paths.run_dir / f"verify_fix{cycles}.log").write_text(
            verify.combined_output, encoding="utf-8"
        )
        events.emit(Event.now("verify.complete", ok=verify.ok, cycle=cycles))

    events.emit(Event.now("run.end", workflow="build", ok=verify.ok))
    return plan, verify, run_paths
