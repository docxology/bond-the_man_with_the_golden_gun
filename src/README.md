# src/ — the_man_with_the_golden_gun (SOLEX)

Importable package logic under `src/the_man_with_the_golden_gun/`.

| Module | Responsibility | Imports |
| --- | --- | --- |
| `solar_concentration.py` | mirror-array → heat yield, optimal allocation | stdlib |
| `solar_tracking.py` | solar geometry, daylight window, clear-sky insolation | stdlib |
| `lair_topology.py` | funhouse graph escape / bottlenecks | stdlib |
| `lair_flows.py` | max flow, min cut, cost-aware escape | stdlib |
| `duel_scheduler.py` | bounty interval scheduling | stdlib |
| `deadline_scheduler.py` | unit-time deadline contracts (max profit) | stdlib |
| `mission.py` | `MissionProvider` adapter + gadget registration | `bond_api` |
| `manuscript_variables.py` | `{{TOKEN}}` hydration + config verification | yaml + domain |
| `declarations.py` | claim-ledger and YAML-overlay verification | yaml + domain |
| `figures.py` | deterministic concept figures | matplotlib + numpy |
| `mission_cli.py` | phase rendering for CLI wrappers | `bond_api` |

Layer contract: the six domain modules are pure and standalone-importable;
`mission.py` is the single `bond_api` adapter; `scripts/` stay thin.

This table is checked, not hand-maintained:
`tests/test_declarations.py::test_src_readme_lists_every_module` fails if a
module file has no row, or if a row names a file that does not exist.

Gates: `pytest --cov=src --cov-fail-under=90`, `ruff check` + `ruff format`,
`mypy src/`. Measured test count and coverage live in
[`../docs/_generated/COUNTS.md`](../docs/_generated/COUNTS.md) — read them
there rather than quoting a number that drifts.
