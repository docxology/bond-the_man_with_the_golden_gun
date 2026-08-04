# src/ — the_man_with_the_golden_gun (SOLEX)

Importable package logic under `src/the_man_with_the_golden_gun/`.

| Module | Responsibility | Imports |
| --- | --- | --- |
| `solar_concentration.py` | mirror-array → heat yield, optimal allocation | stdlib + numpy |
| `lair_topology.py` | funhouse graph escape / bottlenecks | stdlib |
| `duel_scheduler.py` | bounty interval scheduling | stdlib |
| `mission.py` | `MissionProvider` adapter + gadget registration | `bond_api` |
| `manuscript_variables.py` | `{{TOKEN}}` hydration | yaml + domain |
| `figures.py` | deterministic concept figures | matplotlib + numpy |
| `mission_cli.py` | phase rendering for CLI wrappers | `bond_api` |

Layer contract: the three domain modules are pure and standalone-importable;
`mission.py` is the single `bond_api` adapter; `scripts/` stay thin.

Gates (all green): `pytest --cov=src --cov-fail-under=90` (100%), `ruff check`
+ `ruff format`, `mypy src/ scripts/`.
