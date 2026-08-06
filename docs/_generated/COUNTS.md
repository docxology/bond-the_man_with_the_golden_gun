# Live counts — the_man_with_the_golden_gun (SOLEX)

Measured test and coverage numbers for this film package, copied from a real
gate run. Do not hand-edit the measured values, and do not restate them in any
other document — every other file describes the *gate*, which is stable, rather
than the measurement, which moves.

Measured on Python 3.14.6 (darwin) with
`uv run pytest tests/ --cov=src --cov-fail-under=90`.

| Metric | Value |
| --- | --- |
| Test count | 206 |
| Failures / errors / skips | 0 / 0 / 0 |
| Statements (`src/`) | 1070 |
| Branches (`src/`) | 338 |
| Line coverage (`src/`) | 100.00% |
| Branch coverage (`src/`) | 100.00% |
| Gate | `--cov-fail-under=90` (passing) |
| Mock-framework uses | 0 |
| Test modules | 12 |

Per-module coverage is 100.00% for all eleven measured source modules
(`deadline_scheduler`, `declarations`, `duel_scheduler`, `figures`,
`lair_flows`, `lair_topology`, `manuscript_variables`, `mission`,
`mission_cli`, `solar_concentration`, `solar_tracking`). `__init__.py` is
excluded by the `omit` list in `pyproject.toml` because it contains only
re-exports.

Regenerate: `uv run pytest tests/ --cov=src --cov-fail-under=90`, then update
the table above from what the run actually printed.
