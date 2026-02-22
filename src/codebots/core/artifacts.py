from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from codebots.config import CodebotsConfig


def new_run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


@dataclass(frozen=True)
class RunPaths:
    repo_path: Path
    run_dir: Path
    work_dir: Path
    events_path: Path
    plan_path: Path
    config_path: Path

    @staticmethod
    def create(repo_path: Path, run_id: str) -> "RunPaths":
        run_dir = repo_path / ".codebots" / "runs" / run_id
        work_dir = run_dir / "work"
        run_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        return RunPaths(
            repo_path=repo_path,
            run_dir=run_dir,
            work_dir=work_dir,
            events_path=run_dir / "events.jsonl",
            plan_path=run_dir / "plan.json",
            config_path=run_dir / "config.yaml",
        )


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dump_model(path: Path, model: BaseModel) -> None:
    dump_json(path, model.model_dump())


def dump_yaml(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(obj, sort_keys=False), encoding="utf-8")


def persist_config(run_paths: RunPaths, config: CodebotsConfig) -> None:
    dump_yaml(run_paths.config_path, config.model_dump())


def work_item_dir(run_paths: RunPaths, work_item_id: str) -> Path:
    d = run_paths.work_dir / work_item_id
    d.mkdir(parents=True, exist_ok=True)
    return d
