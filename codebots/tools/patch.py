from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatchApplier:
    repo: Path

    def apply_unified_diff(self, diff_text: str) -> tuple[bool, str]:
        # Uses `git apply` to preserve correctness and handle offsets.
        try:
            cp = subprocess.run(
                ["git", "apply", "--whitespace=fix", "--verbose"],
                cwd=self.repo,
                input=diff_text,
                text=True,
                capture_output=True,
                check=True,
            )
            return True, cp.stdout.strip() or "applied"
        except subprocess.CalledProcessError as e:
            out = (e.stdout or "") + "\n" + (e.stderr or "")
            return False, out.strip()
