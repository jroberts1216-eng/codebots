from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError


class LLMConfig(BaseModel):
    provider: Literal["mock", "openai_compat", "custom"] = "mock"
    model: str = "default"
    base_url: str | None = None
    api_key_env: str = "CODEBOTS_API_KEY"


class VerifyConfig(BaseModel):
    commands: list[str] = Field(
        default_factory=lambda: [
            "python -m compileall -q .",
            "ruff check .",
            "ruff format --check .",
            "pytest -q",
        ]
    )


class WorkflowConfig(BaseModel):
    max_fix_cycles: int = 1
    max_retries_per_item: int = 2


class CodebotsConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    verify: VerifyConfig = Field(default_factory=VerifyConfig)
    workflows: WorkflowConfig = Field(default_factory=WorkflowConfig)

    @staticmethod
    def default() -> "CodebotsConfig":
        return CodebotsConfig()


DEFAULT_CONFIG_PATH = Path(".codebots/config.yaml")


def load_config(repo_path: Path) -> CodebotsConfig:
    """Load `.codebots/config.yaml` under `repo_path`, or return defaults."""
    cfg_path = repo_path / DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        return CodebotsConfig.default()

    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    try:
        return CodebotsConfig.model_validate(raw)
    except ValidationError as e:
        raise ValueError(f"Invalid config at {cfg_path}: {e}") from e


def write_example_config(repo_path: Path) -> Path:
    """Write a starter config file into the repo."""
    cfg_path = repo_path / DEFAULT_CONFIG_PATH
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    example = CodebotsConfig.default().model_dump()
    cfg_path.write_text(yaml.safe_dump(example, sort_keys=False), encoding="utf-8")
    return cfg_path
