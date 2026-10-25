# Reproducibility

Every number in this dossier is regenerable from a clean checkout by running
the commands below. There is no hidden state, no network call, no wall-clock
read in a persisted artifact, and no random draw.

## Regeneration procedure

```bash
uv sync --extra dev                                       # resolve deps + bond-api path dep
uv run python scripts/00_preflight.py                     # protocol discoverability
uv run python scripts/generate_artifacts.py               # outcome JSON + all figures
uv run python scripts/z_generate_manuscript_variables.py  # token map + resolved sections
uv run pytest tests/ --cov=src --cov-fail-under={{COVERAGE_GATE_PCT}}
```

`scripts/generate_artifacts.py` writes `output/data/solex_outcome.json` and the
{{NUM_FIGURES}} figures under `output/figures/`.
`scripts/z_generate_manuscript_variables.py` writes
`output/data/manuscript_variables.json` and the fully resolved manuscript tree
under `output/manuscript/`, and exits non-zero if any placeholder survives
substitution.

## Sources of determinism

The package has three potential nondeterminism surfaces, and each is closed:

1. **Randomness.** There is none. The declared seed ({{MISSION_SEED}}) is
   recorded in the mission provenance for protocol conformance, not consumed by
   a generator — no module imports `random` or `numpy.random`. The correct
   reading of the seed is "this mission asserts it needs no entropy".
2. **Iteration order.** Graph algorithms iterate neighbours through `sorted()`
   rather than set order, so the BFS escape route, the flow decomposition, and
   the minimum cut are stable across runs and interpreter hash seeds.
   Schedulers break ties on `(end, id)` and `(-profit, id)` respectively.
3. **Wall clock.** Persisted artifacts carry the fixed
   `DEFAULT_TIMESTAMP` ({{GENERATION_TIMESTAMP}}), and the mission outcome
   records `wall_time_s = 0.0` rather than a measured duration, so two runs
   produce byte-identical files. Figure PNGs are likewise byte-identical
   between runs; `tests/test_figures.py` asserts this by rendering each figure
   twice into separate directories and comparing bytes.

## Metric injection

No metric in this manuscript is typed by hand. Each is a double-brace
placeholder resolved by
`src/the_man_with_the_golden_gun/manuscript_variables.py::generate_variables()`
from `manuscript/config.yaml` plus a live call into the domain models. Four
gates hold that discipline in place:

* `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
  scans every file the hydrator writes — the numbered sections and the Pandoc
  preamble, both drawn from `manuscript_variables.manuscript_sources()` — and
  fails if one cites a token the generator does not produce.
* `scripts/z_generate_manuscript_variables.py` fails if a resolved file still
  contains an unsubstituted token.
* `manuscript_variables.verify_declared_experiment()` recomputes every value
  the config's `experiment` block declares — the codename, the irradiance, the
  receiver aperture, the solar-site geometry, the lair entry and exit, the
  maximum duel bounty, the extended lair, and the whole deadline book — and
  raises if the config and the code disagree. It also raises on a declared key
  it has no recomputation for, so the checked surface cannot quietly shrink
  below the block. A stale config therefore fails the build rather than
  narrating a wrong number.
* `declarations.verify_claim_ledger()` recomputes every value in
  `data/claim_ledger.yaml` at its recorded precision and checks that each
  claim's cited evidence symbol and test file exist. It runs during token
  generation because the config declares the ledger path, so the ledger is a
  checked restatement of the code rather than a parallel copy of the numbers.

## Test and gate discipline

The suite is zero-mock: no `unittest.mock`, no `MagicMock`, no `mocker.patch`
anywhere in `tests/`. Assertions are made against genuinely computed values
(known vectors derived from the algorithms' definitions), real rendered PNGs,
and real subprocess executions of the `scripts/` entry points. Line **and**
branch coverage on `src/` is gated at {{COVERAGE_GATE_PCT}}% by
`pytest --cov-fail-under`; `ruff check`, `ruff format --check`, and `mypy` must
be clean on `src/` and `scripts/`. The rationale for each of these choices is
recorded in `docs/testing_philosophy.md`.

## What is not reproducible here

The code is public as a standalone mirror, but there is no archived release: no
DOI, no Zenodo deposit, and no versioned artifact beyond the git history. The
metadata sidecars (`.zenodo.json`, `CITATION.cff`, `codemeta.json`) deliberately
omit DOI fields rather than carrying a placeholder. Reproduction therefore means
re-running the commands above inside this checkout, not fetching a release.
