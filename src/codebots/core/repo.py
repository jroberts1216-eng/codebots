from __future__ import annotations

import os
from pathlib import Path

from codebots.core.models import FileChange


class RepoError(RuntimeError):
    pass


def _safe_join(repo_root: Path, relative_path: str) -> Path:
    # Avoid path traversal outside repo_root
    rel = Path(relative_path)
    if rel.is_absolute():
        raise RepoError(f"Refusing to write absolute path: {relative_path}")
    out = (repo_root / rel).resolve()
    root = repo_root.resolve()
    if root not in out.parents and out != root:
        raise RepoError(f"Refusing to write outside repo: {relative_path}")
    return out


def apply_changes(repo_root: Path, changes: list[FileChange]) -> list[Path]:
    written: list[Path] = []
    for ch in changes:
        p = _safe_join(repo_root, ch.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(ch.content, encoding="utf-8")
        written.append(p)
    return written


def summarize_tree(repo_root: Path, max_files: int = 200) -> str:
    """Lightweight tree summary for prompts.

    Avoids dumping the entire repo into prompts.
    """
    lines: list[str] = []
    count = 0
    for root, dirs, files in os.walk(repo_root):
        # Skip common noise
        parts = Path(root).parts
        if any(p in {".git", ".codebots", ".venv", "__pycache__", "dist", "build"} for p in parts):
            continue
        rel_root = str(Path(root).relative_to(repo_root))
        for name in sorted(files):
            if count >= max_files:
                lines.append("... (truncated)")
                return "\n".join(lines)
            rel = (Path(rel_root) / name) if rel_root != "." else Path(name)
            lines.append(str(rel))
            count += 1
    return "\n".join(lines)
