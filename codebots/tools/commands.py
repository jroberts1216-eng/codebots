from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


class CommandNotAllowed(Exception):
    pass


@dataclass(frozen=True)
class CommandRunner:
    repo: Path
    allow_prefixes: list[str]

    def run(self, cmd: str, *, timeout_seconds: int = 1200) -> tuple[int, str]:
        parts = shlex.split(cmd)
        if not parts:
            raise CommandNotAllowed("empty command")
        prefix = parts[0]
        if self.allow_prefixes and prefix not in self.allow_prefixes:
            raise CommandNotAllowed(f"command prefix not allowlisted: {prefix}")

        cp = subprocess.run(
            parts,
            cwd=self.repo,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        out = (cp.stdout or "") + ("\n" + cp.stderr if cp.stderr else "")
        return cp.returncode, out.strip()
