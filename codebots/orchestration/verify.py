from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codebots.tools.commands import CommandRunner, CommandNotAllowed


@dataclass(frozen=True)
class Verifier:
    repo: Path
    allow_prefixes: list[str]

    def run(self, commands: list[str]) -> dict[str, Any]:
        runner = CommandRunner(repo=self.repo, allow_prefixes=self.allow_prefixes)
        results: list[dict[str, Any]] = []
        ok = True
        for cmd in commands:
            try:
                code, out = runner.run(cmd)
            except CommandNotAllowed as e:
                ok = False
                results.append({"cmd": cmd, "code": None, "output": str(e), "allowed": False})
                continue
            if code != 0:
                ok = False
            results.append({"cmd": cmd, "code": code, "output": out, "allowed": True})
        return {"ok": ok, "results": results}
