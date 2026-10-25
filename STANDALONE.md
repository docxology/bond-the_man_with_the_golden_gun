# STANDALONE.md

**the_man_with_the_golden_gun** is a PROJECT BOND film package, extracted as a
standalone mirror. It is published at
`github.com/docxology/bond-the_man_with_the_golden_gun` and pushed from this
checkout; the suite copy under `projects/working/bond/` stays local-only.

## What this package is

A self-contained, deterministic mission-software package for the SOLEX
operation (The Man with the Golden Gun, 1974). It depends on `bond-api` (the
frozen protocol, via an editable path dependency) plus `numpy`,
`matplotlib`, and `pyyaml`. The pure domain core is standalone-importable
without `bond-api`.

## Running it standalone

```bash
uv sync --extra dev          # requires the suite monorepo checkout (see below)
uv run python scripts/00_preflight.py
uv run python scripts/run_mission.py          # all five phases
uv run python scripts/generate_artifacts.py   # outcome JSON + three figures
uv run pytest tests/ --cov=src --cov-fail-under=90
```

`[tool.uv.sources]` pins `bond-api` to the suite monorepo path
(`<suite>/projects/working/bond/bond-api`), so `uv sync` and `uv lock` fail in a
clone without that checkout. The pin is suite provenance and is not
repointable: `bond-api` is not on PyPI and there is no canonical GitHub repo
for it. Without the suite tree, verify against an unpacked `bond_api` on a bare
venv:

```bash
uv venv --python 3.12 /tmp/solex-verify/.venv
uv pip install --python /tmp/solex-verify/.venv/bin/python numpy matplotlib pyyaml pytest pytest-cov ruff mypy
# copy an unpacked bond_api (from the suite, or ~/.cache/uv/archive-v0/<hash>/) into /tmp/solex-verify/site
PYTHONPATH="$PWD/src:/tmp/solex-verify/site" /tmp/solex-verify/.venv/bin/python -m pytest \
  tests/ -q --cov=src --cov-fail-under=90
```

`src` must be on `PYTHONPATH` (not only pytest's `pythonpath` ini) because the
suite spawns real subprocesses. `[tool.ruff]` also lives in the suite root, so
without it the portable equivalents are `ruff format --check --line-length 120`
and `ruff check --line-length 120`; `mypy` and `pytest` settings are in this
repo's `pyproject.toml` and travel with it.

Nothing requires network access at runtime; all data is computed
deterministically in-process.

## Publishing posture

Published as a public mirror of the suite package. There is no DOI and no
Zenodo deposit, so the metadata sidecars (`.zenodo.json`, `CITATION.cff`,
`codemeta.json`) omit DOI fields rather than carrying placeholders; they name
the mirror repository and no archived release. The suite copy is never pushed.
