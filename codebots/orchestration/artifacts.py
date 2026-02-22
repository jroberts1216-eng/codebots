from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import datetime
from typing import Any


@dataclass(frozen=True)
class ArtifactStore:
    repo: Path
    run_id: str

    @property
    def root(self) -> Path:
        return self.repo / ".codebots" / "artifacts" / self.run_id

    def write_json(self, name: str, data: Any) -> Path:
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return p

    def write_text(self, name: str, text: str) -> Path:
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p


def new_run_id() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
