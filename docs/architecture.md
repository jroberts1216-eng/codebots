# Architecture

## Goals

- Provide a **repeatable** plan → execute → verify loop for repository changes.
- Support **multiple roles** (PM/PGM/Platform/SWE/QA/Security/Reviewer).
- Make the system **testable without credentials** (mock LLM provider).
- Keep the core small and easy to extend.

## High-level flow

1. **Plan**
   - Product Manager produces a PRD (requirements + acceptance criteria).
   - Architect produces architecture decisions and constraints.
   - Program Manager produces a *Work DAG* (work items + dependencies + owners).

2. **Execute**
   - Work items are run in topological order.
   - Each work item is executed by its owner role (SWE, Platform, etc.).
   - Outputs are applied as file changes to the repo.

3. **Verify**
   - Runs a configured list of repo commands (e.g., `ruff`, `pytest`, `tofu validate`).
   - If verification fails, QA + SWE can propose fix work items (bounded loop).

## What this architecture improves

- **Strict schemas**: every agent output is validated (Pydantic). Fail-fast vs. downstream confusion.
- **First-class verification**: verify commands are required in config and run consistently.
- **Deterministic tests**: mock provider gives stable outputs so CI can run without secrets.
- **Extensible agent packs**: add/override roles by registering new agent classes.

## Artifacts

Each run produces a directory:

```
.codebots/runs/<run-id>/
  config.yaml
  plan.json
  events.jsonl
  work/
    <work-item-id>/
      input.json
      output.json
      applied_changes.json
      verify.log
```

This is intended to make debugging, auditing, and human review easier.
