# codebots

A multi-agent codebase planning + execution framework for building and evolving real repositories.

`codebots` is designed to improve on SWE-AF-style pipelines by being:

- **Repo-verifiable by default**: every workflow has a configurable, deterministic `verify` step.
- **Strongly typed**: agents produce structured outputs (Pydantic models) so downstream steps are reliable.
- **Role-based**: Product Manager, Program Manager, Platform Engineer, SWE, QA, Security, Reviewer.
- **Testable**: includes a mock LLM provider so unit tests run without external credentials.
- **Pluggable**: swap LLM providers and agent packs without rewriting orchestration.

The repository you linked is currently empty. This scaffold is intended to be committed into that repository as the initial project. citeturn1view0

## Quickstart

### 1) Install (local development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) Run the unit tests

```bash
pytest -q
```

### 3) Create a plan

```bash
codebots plan --repo . --goal "Scaffold a CLI tool with CI and basic docs"
```

Artifacts will be written under `.codebots/runs/<run-id>/`.

### 4) Run a full build

```bash
codebots build --repo . --goal "Add a new workflow: plan -> execute -> verify"
```

By default, builds use the **mock** LLM provider (safe + deterministic).  
To use a real provider, configure `.codebots/config.yaml` (see below).

## Configuration

Create `.codebots/config.yaml`:

```yaml
llm:
  provider: mock  # mock | openai_compat | custom
  model: default
  base_url: https://api.openai.com  # only used for openai_compat
verify:
  commands:
    - python -m compileall -q .
    - ruff check .
    - ruff format --check .
    - pytest -q
workflows:
  max_fix_cycles: 1
  max_retries_per_item: 2
```

## Concepts

- **Plan**: PRD + Architecture + Work DAG (work items with dependencies)
- **Execute**: run work items in topological order using role-specific agents
- **Verify**: run repo commands; if they fail, QA + SWE propose fixes (optional loop)

See `docs/architecture.md` and `docs/agents.md`.
