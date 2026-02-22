# codebots

`codebots` is a **drop-in**, **local-first** multi-agent CLI that can:

- **Review** any git repository with an arbitrary number of specialized agents
- **Plan** work (PRD + architecture + dependency-aware task graph)
- **Execute** tasks using tool-driven agents (read/search/write/apply patches)
- **Verify** with your repo’s real commands, then run a bounded **fix loop**

It is general-purpose: use it for backend work, frontend work, infra work, data work, or integration work
(e.g., “connect invoice data to QuickBooks”) as long as the work can be represented as repo changes.

## Install (developer mode)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

## Use against any repo

From anywhere:

```bash
codebots agents
codebots review --repo /path/to/repo
codebots plan   --repo /path/to/repo --goal "..."
codebots run    --repo /path/to/repo --goal "..." --apply
```

Artifacts are written under:

- `<repo>/.codebots/artifacts/<run-id>/`

## Configuration

Create `<repo>/.codebots/config.toml`:

```toml
[llm]
provider = "openai_compat"
base_url = "https://api.openai.com"
model = "gpt-4.1-mini"
api_key_env = "CODEBOTS_API_KEY"

[budgets]
max_input_tokens = 200000
max_output_tokens = 80000
max_cost_usd = 25.0

[verify]
commands = [
  "python -m compileall -q .",
  "pytest -q"
]
# Allowlist for commands codebots may execute (recommended)
allow = ["python", "pytest", "ruff", "mypy", "npm", "pnpm", "yarn", "go", "cargo", "make", "terraform", "tofu"]

[agents]
# Enable/disable any built-in agents
enabled = ["repo_overview", "build_system", "quality", "security", "dependencies", "docs",
           "product_manager", "architect", "program_manager",
           "platform_engineer", "software_engineer", "qa_engineer", "reviewer"]
parallel_reviews = true
```

Then:

```bash
export CODEBOTS_API_KEY="..."
codebots run --repo /path/to/repo --goal "..."
```

## Agent model

Agents are grouped into categories:

- **Review** agents: read/search only; produce findings and recommendations.
- **Planning** agents: produce PRD, architecture, and a dependency-aware plan.
- **Execution** agents: propose edits (patches) and apply them; then verify/fix.

Built-ins are rule-based by default; enable the LLM provider to generate richer plans and edits.

## Safety defaults

- Only reads/writes inside `--repo`.
- Patch application is done via unified diffs.
- Command execution is allowlisted (off by default unless configured).
