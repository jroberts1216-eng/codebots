from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RepoFS:
    root: Path

    def abspath(self, rel: str | Path) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (self.root / p)

    def exists(self, rel: str | Path) -> bool:
        return self.abspath(rel).exists()

    def read_text(self, rel: str | Path, *, encoding: str = "utf-8") -> str:
        return self.abspath(rel).read_text(encoding=encoding)

    def write_text(self, rel: str | Path, text: str, *, encoding: str = "utf-8") -> None:
        p = self.abspath(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding=encoding)

    def list_files(self, rel: str | Path = ".", *, max_files: int = 2000) -> list[str]:
        out: list[str] = []
        base = self.abspath(rel)
        if not base.exists():
            return out
        for dirpath, dirnames, filenames in os.walk(base):
            # skip heavy / irrelevant dirs
            dn = [
                d
                for d in dirnames
                if d
                not in {
                    ".git",
                    ".venv",
                    "node_modules",
                    "__pycache__",
                    ".mypy_cache",
                    ".pytest_cache",
                }
            ]
            dirnames[:] = dn
            for fn in filenames:
                p = Path(dirpath) / fn
                out.append(str(p.relative_to(self.root)))
                if len(out) >= max_files:
                    return sorted(out)
        return sorted(out)

    def walk(self, rel: str | Path = ".") -> Iterable[Path]:
        base = self.abspath(rel)
        if not base.exists():
            return
        for dirpath, dirnames, filenames in os.walk(base):
            dn = [
                d
                for d in dirnames
                if d
                not in {
                    ".git",
                    ".venv",
                    "node_modules",
                    "__pycache__",
                    ".mypy_cache",
                    ".pytest_cache",
                }
            ]
            dirnames[:] = dn
            for fn in filenames:
                yield Path(dirpath) / fn
