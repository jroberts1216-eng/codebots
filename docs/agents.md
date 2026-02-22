# Agents

Agents are role-specific components that:

- read inputs (goal, repo context, previous artifacts),
- produce structured outputs (validated),
- optionally propose file changes and/or follow-up work items.

## Built-in roles

- **ProductManagerAgent**
  - Output: PRD (problem, scope, requirements, acceptance criteria)

- **ArchitectAgent**
  - Output: Architecture (system components, constraints, tradeoffs)

- **ProgramManagerAgent**
  - Output: Work DAG (work items, dependencies, ownership, milestones)

- **PlatformEngineerAgent**
  - Output: infra/CI/platform changes

- **SoftwareEngineerAgent**
  - Output: application/library changes

- **QAEngineerAgent**
  - Output: test plans, failure analysis, fix suggestions

- **SecurityEngineerAgent**
  - Output: security review notes + recommended hardening

- **CodeReviewerAgent**
  - Output: review comments + requested changes

## Adding new agents

1. Implement an `Agent` subclass.
2. Register it in `codebots.agents.registry.DEFAULT_AGENT_PACK`.
3. Optionally add a workflow that uses it.

Agents are intentionally simple; orchestration logic belongs in workflows.
