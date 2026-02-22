# Quickstart

## Running against another repo

1) Install codebots

```bash
pip install -e ".[dev]"
```

2) Create a config (or use defaults)

```bash
mkdir -p /path/to/target/.codebots
cp .codebots/config.example.yaml /path/to/target/.codebots/config.yaml
```

3) Plan

```bash
codebots plan --repo /path/to/target --goal "Add offline verification scripts"
```

4) Build (plan + execute + verify)

```bash
codebots build --repo /path/to/target --goal "Add offline verification scripts"
```

## Notes

- The default LLM provider is `mock` so runs are deterministic.
- For real providers, configure `llm.provider` in `.codebots/config.yaml`.
