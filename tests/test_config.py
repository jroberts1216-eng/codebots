from pathlib import Path
from codebots.config import load_config, write_default_config


def test_default_config_written_and_loaded(tmp_path: Path):
    repo = tmp_path
    p = write_default_config(repo)
    assert p.exists()
    cfg = load_config(repo)
    assert cfg.llm.provider in ("mock", "openai_compat")
    assert len(cfg.agents.enabled) > 0
