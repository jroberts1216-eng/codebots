from pathlib import Path
from codebots.repo.scan import scan_repo


def test_scan_detects_actions(tmp_path: Path):
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/ci.yml").write_text("name: ci\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    out = scan_repo(tmp_path)
    assert out["signals"]["has_github_actions"] is True
    assert "pyproject.toml" in out["signals"]["build_files"]
