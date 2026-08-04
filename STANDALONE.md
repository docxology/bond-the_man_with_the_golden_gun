# STANDALONE.md

**the_man_with_the_golden_gun** is a PROJECT BOND film package on a
**local-only** working tree. There is **no remote** — it is never pushed.

## What this package is

A self-contained, deterministic mission-software package for the SOLEX
operation (The Man with the Golden Gun, 1974). It depends on `bond-api` (the
frozen protocol, via an editable path dependency) plus `numpy`,
`matplotlib`, and `pyyaml`. The pure domain core is standalone-importable
without `bond-api`.

## Running it standalone

```bash
uv sync --extra dev          # resolves the bond-api path dep
uv run python scripts/00_preflight.py
uv run python scripts/run_mission.py          # all five phases
uv run python scripts/generate_artifacts.py   # outcome JSON + three figures
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Nothing requires network access at runtime; all data is computed
deterministically in-process.

## Publishing posture

Not published. Because the tree has no remote, metadata sidecars
(`.zenodo.json`, `CITATION.cff`, `codemeta.json`) intentionally omit DOI and
repository fields. If this package is ever promoted to a remote, regenerate
those sidecars and the manuscript publication block before any superset
release workflow.
