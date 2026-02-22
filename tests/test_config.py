from __future__ import annotations

from pathlib import Path

from codebots.config import load_config, write_example_config


def test_load_config_defaults_when_missing(tmp_path: Path) -> None:
    cfg = load_config(tmp_path)
    assert cfg.llm.provider == "mock"
    assert cfg.verify.commands


def test_write_example_config_round_trip(tmp_path: Path) -> None:
    path = write_example_config(tmp_path)
    assert path.exists()
    cfg = load_config(tmp_path)
    assert cfg.llm.provider == "mock"
