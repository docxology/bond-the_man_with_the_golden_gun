# The Man with the Golden Gun — SOLEX (Special-Agent Mission Software)

PROJECT BOND film package for **The Man with the Golden Gun** (1974), mission
codename **SOLEX**. Pure, deterministic mission software over three concepts:
solar concentration yield, funhouse lair escape topology, and assassin
duel/bounty scheduling — adapted to the frozen `bond-api` `MissionProvider`
protocol.

Local-only working tree: **no remote, never push.**

## Mission codename: SOLEX

- **Solar concentration yield** — a mirror-array → heat-output model. The
  canonical SOLEX mirror field (300 m²) under a canonical DNI converts optical
  power into a thermal output of **191.6325 kW** at a concentration ratio of
  **50.1×**, and a greedy allocation optimally spends a mirror-area budget on
  the highest-reflectivity mirrors.
- **Funhouse lair escape topology** — the villain's mirror-line lair modelled
  as an undirected graph; a BFS shortest escape route and the exact bottleneck
  rooms that guard the vault (every escape route must pass through them).
- **Assassin duel / bounty scheduling** — an appointment book of half-open
  duels solved by **weighted interval scheduling**: a non-overlapping set that
  maximises total bounty (`13.0` from the canonical 4 contracts), full conflict
  detection, and a count-maximising earliest-finish greedy.

## Protocol integration

`src/the_man_with_the_golden_gun/mission.py` implements the **frozen** bond-api
`MissionProvider` (film, brief, recon, plan, execute, debrief) and registers
its domain functions/data with the `bond_api.registry.GadgetRegistry`. The
pure domain modules (`solar_concentration.py`, `lair_topology.py`,
`duel_scheduler.py`) never import `bond_api` — `mission.py` is the single
adapter, so the core stays standalone if the path dependency ever fails.

## Layout

```
src/the_man_with_the_golden_gun/
  solar_concentration.py   mirror array -> heat yield + optimal allocation
  lair_topology.py         funhouse rooms/mirrors as graph, escape + bottlenecks
  duel_scheduler.py        bounty appointment book, weighted interval scheduling
  mission.py               MissionProvider adapter (frozen bond-api protocol)
  manuscript_variables.py  {{TOKEN}} hydration from config.yaml + domain
  figures.py               deterministic matplotlib concept figures
  mission_cli.py           phase-rendering for the CLI wrappers
scripts/                   thin per-phase CLIs + artifact/manuscript/preflight
manuscript/                config.yaml + numbered {{TOKEN}} sections
tests/                     zero-mock real-data suite (100% line+branch on src/)
```

## Quick start

```bash
uv sync --extra dev
uv run python scripts/00_preflight.py         # protocol discoverability
uv run python scripts/run_mission.py          # brief..debrief (all phases)
uv run python scripts/generate_artifacts.py   # output/data/solex_outcome.json + figures
uv run python scripts/z_generate_manuscript_variables.py  # resolve {{TOKEN}}s
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Gates

100% line+branch coverage on `src/` (≥90% required), zero-mock real-data
tests, `ruff check` + `ruff format` + `mypy` clean on `src/` and `scripts/`,
and zero `template[_]code_project` lineage strings. Git status clean after each
path-scoped commit.

## License

MIT — Daniel Ari Friedman, Active Inference Institute.
