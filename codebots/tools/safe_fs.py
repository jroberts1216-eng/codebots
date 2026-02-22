from __future__ import annotations

import re
from dataclasses import dataclass

from codebots.repo.fs import RepoFS


class ToolError(Exception):
    pass


@dataclass(frozen=True)
class SafeFS:
    fs: RepoFS

    def _safe_rel(self, rel: str) -> str:
        # Disallow escaping repo root.
        p = (self.fs.root / rel).resolve()
        if not str(p).startswith(str(self.fs.root.resolve())):
            raise ToolError(f"path escapes repo root: {rel}")
        return str(p.relative_to(self.fs.root))

    def list_files(self, rel: str = ".", max_files: int = 2000) -> list[str]:
        self._safe_rel(rel)
        return self.fs.list_files(rel, max_files=max_files)

    def read_file(self, rel: str, max_bytes: int = 200_000) -> str:
        rel2 = self._safe_rel(rel)
        p = self.fs.abspath(rel2)
        data = p.read_bytes()
        if len(data) > max_bytes:
            raise ToolError(f"file too large: {rel} ({len(data)} bytes > {max_bytes})")
        return data.decode("utf-8", errors="replace")

    def write_file(self, rel: str, text: str) -> None:
        rel2 = self._safe_rel(rel)
        self.fs.write_text(rel2, text)

    def search_text(self, pattern: str, *, max_hits: int = 50) -> list[str]:
        rx = re.compile(pattern)
        hits: list[str] = []
        for p in self.fs.walk("."):
            rel = str(p.relative_to(self.fs.root))
            if rel.startswith(".git/"):
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(txt.splitlines(), start=1):
                if rx.search(line):
                    hits.append(f"{rel}:{i}:{line[:200]}")
                    if len(hits) >= max_hits:
                        return hits
        return hits
