from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .fs import RepoFS


@dataclass(frozen=True)
class RepoSignals:
    languages: list[str]
    build_files: list[str]
    has_github_actions: bool
    has_docker: bool
    has_terraform_like: bool
    has_tests: bool
    likely_frameworks: list[str]


def _detect_languages(files: list[str]) -> list[str]:
    exts = {Path(f).suffix for f in files}
    langs = []
    if ".py" in exts:
        langs.append("python")
    if ".ts" in exts or ".tsx" in exts:
        langs.append("typescript")
    if ".js" in exts or ".jsx" in exts:
        langs.append("javascript")
    if ".go" in exts:
        langs.append("go")
    if ".rs" in exts:
        langs.append("rust")
    if ".java" in exts or "pom.xml" in files:
        langs.append("java")
    if ".kt" in exts or "build.gradle" in files:
        langs.append("kotlin/gradle")
    if ".cs" in exts:
        langs.append("dotnet")
    if ".rb" in exts:
        langs.append("ruby")
    if ".php" in exts:
        langs.append("php")
    if ".sql" in exts:
        langs.append("sql")
    if ".tf" in exts:
        langs.append("terraform/tofu")
    return langs


def _detect_frameworks(files: list[str]) -> list[str]:
    fset = set(files)
    out = []
    if "pyproject.toml" in fset or "requirements.txt" in fset:
        out.append("python")
    if "package.json" in fset:
        out.append("node")
    if "go.mod" in fset:
        out.append("go")
    if "Cargo.toml" in fset:
        out.append("rust")
    if "Dockerfile" in fset or any(p.endswith("docker-compose.yml") for p in files):
        out.append("docker")
    if any(p.endswith(".tf") for p in files):
        out.append("terraform/tofu")
    return out


def scan_repo(repo: Path, *, max_files: int = 2000) -> dict[str, Any]:
    fs = RepoFS(repo)
    files = fs.list_files(".", max_files=max_files)
    fset = set(files)

    build_files = [
        p
        for p in [
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "go.mod",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            "Makefile",
        ]
        if p in fset
    ]

    has_actions = any(p.startswith(".github/workflows/") for p in files)
    has_docker = (
        "Dockerfile" in fset
        or any(p.endswith("docker-compose.yml") for p in files)
        or any(p.endswith("docker-compose.yaml") for p in files)
    )
    has_tf = (
        any(p.endswith(".tf") for p in files)
        or any(p.endswith(".tfvars") for p in files)
        or "versions.tf" in fset
    )
    has_tests = any(p.startswith("tests/") for p in files) or any("/test/" in p for p in files)

    signals = RepoSignals(
        languages=_detect_languages(files),
        build_files=build_files,
        has_github_actions=has_actions,
        has_docker=has_docker,
        has_terraform_like=has_tf,
        has_tests=has_tests,
        likely_frameworks=_detect_frameworks(files),
    )

    # Provide a small "context pack" for LLM prompts (top-level + key files)
    key_files = []
    for cand in [
        "README.md",
        "pyproject.toml",
        "package.json",
        "Makefile",
        ".github/workflows/ci.yml",
        ".github/workflows/main.yml",
        ".pre-commit-config.yaml",
    ]:
        if cand in fset:
            key_files.append(cand)

    return {
        "files_count": len(files),
        "top_level": sorted({Path(p).parts[0] for p in files if p}),
        "signals": signals.__dict__,
        "key_files": key_files,
    }
