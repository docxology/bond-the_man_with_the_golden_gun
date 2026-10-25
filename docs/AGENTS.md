# AGENTS.md — working inside `docs/` (the_man_with_the_golden_gun · SOLEX)

Rules for agents editing **this documentation directory**. Package-wide rules
live in [`../AGENTS.md`](../AGENTS.md); the operational read-first checklist is
[`agent_instructions.md`](agent_instructions.md).

## What lives here, and what does not

| File | Owns |
| --- | --- |
| [`README.md`](README.md) | The index of this directory |
| [`AGENTS.md`](AGENTS.md) | This file — how to edit the docs |
| [`agent_instructions.md`](agent_instructions.md) | Operational constraints and the gate checklist |
| [`architecture.md`](architecture.md) | Module-by-module structure of `src/`, the layer contract, the frozen protocol surface |
| [`testing_philosophy.md`](testing_philosophy.md) | Why the suite is zero-mock, real-data, and deterministic |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | Measured test count and coverage — regenerated, never estimated |

Deliberately **not** here:

* Scientific results and their numbers — those belong in `manuscript/`, where
  every metric arrives through the token pipeline.
* Package overview and quick start — `../README.md`.
* Remaining work — `../TODO.md`.

Duplicating any of those here creates a second copy that will drift. Link
instead.

## The one rule that matters: describe what exists

Every statement in this directory must be checkable against the tree as it
stands. In practice that means:

* **Name real modules.** If `architecture.md` describes `lair_flows.py`, that
  file must exist and must do what the description says. Deleting or renaming a
  module means editing this directory in the same commit.
* **Never carry a measured number in prose.** Test counts and coverage
  percentages go in `_generated/COUNTS.md` and are copied from a run you
  actually performed. Elsewhere, describe the *gate*
  ("`--cov-fail-under=90` on `src/`"), which is a stable configured threshold,
  rather than the current measurement, which drifts every commit.
* **No exemplar boilerplate.** This package was forked from the
  `template_code_project` exemplar; that lineage may be mentioned as history,
  but no sentence may describe the exemplar's contents as though they were this
  package's. Text that would read identically in another BOND package is a
  defect here.
* **No aspirational tense.** Documentation describes the current tree. Planned
  work goes in `../TODO.md`.

## When code changes, what to update

| Change | Update |
| --- | --- |
| New or renamed module in `src/` | `architecture.md` module section; `../README.md` layout block; `DOMAIN_MODULES` in `manuscript_variables.py` if it is a domain module |
| New gate, or a gate's threshold changed | `testing_philosophy.md`; `agent_instructions.md` checklist; `gates` block in `manuscript/config.yaml` |
| Change to `mission.py`'s public surface | `architecture.md` protocol table — and reconsider, because that surface is frozen and consumed across packages |
| New figure | `figures.FIGURES` registry, `manuscript/README.md` figure table, and a `{#fig:...}` declaration in a section (the test suite enforces both directions) |
| Test count or coverage moved | `_generated/COUNTS.md`, from a real run |

## Verify before claiming done

```bash
cd "$(git rev-parse --show-toplevel)"   # run from this package's root
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' --glob '!.venv/**'
git status --short
```

`uv run` needs the suite monorepo — the `bond-api` path dependency. On a clone
without that checkout, run the same commands as `python -m pytest …` against a
venv; the recipe is in [`../STANDALONE.md`](../STANDALONE.md).

A documentation change that describes behaviour the suite does not exercise is
a claim without evidence: add the test in the same commit, or write the weaker
sentence that is actually true.
