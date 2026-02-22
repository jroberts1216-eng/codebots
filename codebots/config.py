from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import tomllib
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: Literal["mock", "openai_compat"] = "mock"
    base_url: str = "https://api.openai.com"
    model: str = "mock"
    api_key_env: str = "CODEBOTS_API_KEY"
    timeout_seconds: float = 60.0


class BudgetsConfig(BaseModel):
    max_input_tokens: int = 200_000
    max_output_tokens: int = 80_000
    max_cost_usd: float | None = None


class VerifyConfig(BaseModel):
    commands: list[str] = Field(default_factory=list)
    allow: list[str] = Field(default_factory=list)


class AgentsConfig(BaseModel):
    enabled: list[str] = Field(default_factory=list)
    parallel_reviews: bool = True


class CodebotsConfig(BaseModel):
    llm: LLMConfig = LLMConfig()
    budgets: BudgetsConfig = BudgetsConfig()
    verify: VerifyConfig = VerifyConfig()
    agents: AgentsConfig = AgentsConfig()


DEFAULT_ENABLED = [
    # Review
    "repo_overview",
    "build_system",
    "quality",
    "security",
    "dependencies",
    "docs",
    "architecture_review",
    # Planning
    "product_manager",
    "architect",
    "program_manager",
    # Execution (stubs, safe)
    "platform_engineer",
    "software_engineer",
    "qa_engineer",
    "reviewer",
]


def load_config(repo: Path) -> CodebotsConfig:
    cfg_path = repo / ".codebots" / "config.toml"
    if not cfg_path.exists():
        cfg = CodebotsConfig()
        cfg.agents.enabled = list(DEFAULT_ENABLED)
        return cfg

    data: dict[str, Any] = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    cfg = CodebotsConfig.model_validate(data)
    if not cfg.agents.enabled:
        cfg.agents.enabled = list(DEFAULT_ENABLED)
    return cfg


def write_default_config(repo: Path) -> Path:
    out = repo / ".codebots" / "config.toml"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return out

    out.write_text(
        """# codebots configuration

[llm]
provider = "mock"
base_url = "https://api.openai.com"
model = "mock"
api_key_env = "CODEBOTS_API_KEY"
timeout_seconds = 60.0

[budgets]
max_input_tokens = 200000
max_output_tokens = 80000
max_cost_usd = 25.0

[verify]
# Add repo-specific verification commands here (recommended).
# Example:
# commands = ["pytest -q"]
commands = []
# Allowlist prefixes for commands that codebots may execute.
allow = []

[agents]
enabled = []
parallel_reviews = true
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return out
