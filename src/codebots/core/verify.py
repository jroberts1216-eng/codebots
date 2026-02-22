from __future__ import annotations

import subprocess
from pathlib import Path

from codebots.core.models import VerifyResult


def run_verify(repo_path: Path, commands: list[str]) -> VerifyResult:
    results: list[dict[str, object]] = []
    combined: list[str] = []
    ok = True

    for cmd in commands:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_path),
            shell=True,
            capture_output=True,
            text=True,
        )
        step = {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
        results.append(step)
        combined.append(f"$ {cmd}\n{proc.stdout}{proc.stderr}")
        if proc.returncode != 0:
            ok = False
            # Continue collecting outputs for better diagnostics.

    return VerifyResult(ok=ok, command_results=results, combined_output="\n\n".join(combined))
