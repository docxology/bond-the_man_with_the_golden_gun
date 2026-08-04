# Agent instructions — the_man_with_the_golden_gun (SOLEX)

Read this before changing the package. Full package rules: [`../AGENTS.md`](../AGENTS.md).
This is a **local-only** PROJECT BOND film package (no remote, never push).

## Operational constraints

1. Scope = exactly this package directory. Do not touch sibling packages,
   bond root files, or the template repo.
2. No mock framework in tests — real data + computation only.
3. Deterministic: fixed seeds, no untracked random reliance, no wall-clock in
   persisted artifacts.
4. ≥90% line+branch coverage on `src/` (suite currently at 100%).
5. Thin orchestrators in `scripts/`; business logic in `src/`.
6. Pure domain modules must stay importable without `bond_api`; only
   `mission.py` imports the protocol.
7. Commit path-scoped inside this repo only.

## Before modifying tests

Follow `tests/README.md` and the zero-mock, real-data approach. New domain
behaviour = new known-vector test asserting real computed values.

## Before altering module boundaries

`src/the_man_with_the_golden_gun/` has a strict layer contract: the domain
core (solar/lair/duel) is infrastructure-free; `mission.py` is the single
`bond_api` adapter; `manuscript_variables.py`/`figures.py`/`mission_cli.py`
are the hydration/figure/output layers. Keep script surfaces thin.

## Gate checklist (before "done")

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format src/ scripts/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**'   # zero
git status --short   # clean after commit
```
