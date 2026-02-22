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

## GCP DIM_CASE Pipeline Scaffold

This repo now includes a config-driven scaffold for a daily incremental CDC pipeline on GCP:

- Source: CDC Avro files in GCS (dev/prod buckets).
- Landing/query: BigLake external tables in BigQuery.
- Current-state logic: `vw_cases_current_<env>` views.
- Consolidation: Type 1 MERGE into native `dim_case`.
- Orchestration: Cloud Run Job (per-tenant MERGE) + Cloud Scheduler (daily).

### Layout

- Terraform: `terraform/`
- SQL:
  - `sql/tables/ops_stream_config.sql`
  - `sql/tables/ops_pipeline_state.sql`
  - `sql/tables/dim_case.sql`
  - `sql/external_tables/ext_cases_avro_dev.sql`
  - `sql/external_tables/ext_cases_avro_prod.sql`
  - `sql/views/vw_cases_current_dev.sql`
  - `sql/views/vw_cases_current_prod.sql`
  - `sql/merges/merge_dim_case.sql`
- Cloud Run job:
  - `jobs/dim_case_updater/main.py`
  - `jobs/dim_case_updater/Dockerfile`
  - `jobs/dim_case_updater/requirements.txt`

### Placeholder Variables

Use these placeholders in SQL/Terraform and replace for each environment:

- `<PROJECT_ID>`
- `<DATASET_ANALYTICS>`
- `<DATASET_OPS>`
- `<REGION>`
- `<CONNECTION_ID>`

### Notes

- `stream_config` is the single control plane for dev/prod tenant activation.
- The merge script computes deterministic `case_key` as `ABS(FARM_FINGERPRINT(CONCAT(tenant_id,'|',case_id)))`.
- TODO markers are included where source field names or bucket/path conventions may differ.
- Docker build should be run from repo root so `sql/merges/merge_dim_case.sql` is copied into the image.
