from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codebots.repo.fs import RepoFS
from codebots.repo.scan import scan_repo


@dataclass(frozen=True)
class RepoContext:
    repo: Path
    fs: RepoFS
    scan: dict[str, Any]


def build_repo_context(
    repo: Path, *, max_files: int = 2000, max_key_bytes: int = 60_000
) -> dict[str, Any]:
    fs = RepoFS(repo)
    files = fs.list_files(".", max_files=max_files)
    scan = scan_repo(repo, max_files=max_files)

    key_snips: dict[str, str] = {}
    for k in scan.get("key_files", []):
        try:
            txt = fs.read_text(k, encoding="utf-8")
            key_snips[k] = txt[:max_key_bytes]
        except Exception:
            pass

    return {
        "repo": str(repo),
        "files": files,
        "scan": scan,
        "key_snippets": key_snips,
    }
