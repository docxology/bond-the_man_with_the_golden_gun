# Agent instructions — the_man_with_the_golden_gun (SOLEX)

Read this before changing anything. Package rules: [`../AGENTS.md`](../AGENTS.md).
Structure: [`architecture.md`](architecture.md). Test doctrine:
[`testing_philosophy.md`](testing_philosophy.md).

This is a PROJECT BOND film package published as a standalone mirror; the suite
copy is the local-only tree.

## Operational constraints

1. **Scope is exactly this directory.** Do not touch sibling BOND packages, the
   bond root files, or the template repo. Commits are path-scoped inside this
   repository only.
2. **No mock framework.** No `unittest.mock`, `MagicMock`, or `mocker.patch`
   anywhere in `tests/`. Real data, real computation, real files, real
   subprocesses.
3. **Deterministic.** Fixed inputs, no random draws, sorted iteration in graph
   traversals, no wall-clock read in a persisted artifact.
4. **Coverage gate.** `--cov-fail-under=90` on `src/`, line **and** branch. The
   current measurement lives in [`_generated/COUNTS.md`](_generated/COUNTS.md) —
   read it there, never quote it from memory.
5. **Thin orchestrators.** `scripts/` forwards argv and does I/O. Business logic
   lives in `src/`. A script that computes something is a defect.
6. **The core stays pure.** The six domain modules import only the standard
   library and never `bond_api`. `mission.py` is the single adapter.
7. **Metrics are injected, never typed.** Any number in `manuscript/` must be a
   token produced by `manuscript_variables.generate_variables()`.

## Before you start

```bash
cd "$(git rev-parse --show-toplevel)"   # run from this package's root
uv sync --extra dev          # resolves the bond-api path dependency
uv run pytest tests/ -q      # confirm you are starting from green
git status --short           # confirm you are starting from clean
```

Starting from a red or dirty tree makes it impossible to attribute what you
break, so establish the baseline first.

## Adding a domain capability

1. Write the test first, with an expected value derived from the algorithm's
   definition or from a structural property — not from running the new code and
   pasting what it printed.
2. Implement in a new or existing module under
   `src/the_man_with_the_golden_gun/`. Full type hints, a docstring naming the
   algorithm, and validation that raises on malformed input.
3. If it is a domain module, add it to `DOMAIN_MODULES` in
   `manuscript_variables.py` — the manuscript's module count is derived from
   that list.
4. Surface it in `mission.py`: extend `run_domain()`'s payload and, where it is
   part of the film's toolkit, add a gadget. **Do not** rename or remove
   anything in the frozen protocol surface (see the table in
   [`architecture.md`](architecture.md)) — `bond-cli`, the coordinator, and the
   orchestrator consume it across packages.
5. Add a token for any result you want to state in the manuscript, then cite the
   token. Never write the number.
6. Update [`architecture.md`](architecture.md) and `../README.md` in the same
   commit.

## Adding a figure

1. Write the generator in `figures.py`.
2. Register it in the `FIGURES` tuple and the `_GENERATORS` map.
3. Declare it in a manuscript section as
   `![caption](../output/figures/<name>.png){#fig:<label>}`.
4. Add it to the figure table in `../manuscript/README.md`.

The test suite binds these in both directions: a registered figure that no
section declares fails, and a section that declares an unregistered figure
fails.

## Editing the manuscript

Numbered sections (`[0-9]*.md`) and `preamble.md` are token-hydrated and
gate-scanned — the writer and the gate share `manuscript_sources()`. The
canonical section set is `00_abstract`, `01_introduction`, `02_methodology`,
`03_results`, `04_conclusion`, `05_experimental_setup`, `06_reproducibility`,
`07_scope_and_related_work`, `08_appendix`, `99_references`, plus
`preamble.md`, `config.yaml`, and `references.bib`.

* A new metric needs a new entry in `generate_variables()` first; the token gate
  fails on any placeholder the generator does not produce.
* Do not write a literal double-brace placeholder as prose in a numbered
  section — the gate will read it as an unresolved token. Describe it instead.
* `references.bib` entries must be real and checkable. If you are not confident
  a citation exists as stated, remove it rather than ship it.
* Anything the config restates about the domain is verified by
  `verify_declared_experiment()`; if you change a canonical fixture, change the
  config too or the build will raise. Adding a key to the `experiment` block
  also means adding its recomputation to `declarations.experiment_expectations()`
  — an unverifiable declaration raises rather than passing.
* The same holds for `data/claim_ledger.yaml`, `experiment_plan.yaml`, and
  `domain_profile.yaml`: they are checked restatements, not notes. A new claim
  needs an entry in `declarations.CLAIM_RECOMPUTERS`; a new module or figure
  must land in the overlays or `tests/test_declarations.py` goes red.

## Gate checklist before "done"

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
uv run python scripts/00_preflight.py                     # protocol discoverability
uv run python scripts/generate_artifacts.py               # outcome + figures
uv run python scripts/z_generate_manuscript_variables.py  # every token resolves
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' --glob '!.venv/**'
git status --short                                        # clean after commit
```

Zero failures, zero skips, coverage at or above the gate, and no lineage
strings. Read the output of each command — an exit code alone does not tell you
whether the suite collected any tests.
