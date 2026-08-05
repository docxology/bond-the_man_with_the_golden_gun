# The Man with the Golden Gun — SOLEX (Special-Agent Mission Software)

PROJECT BOND film package for **The Man with the Golden Gun** (1974), mission
codename **SOLEX**. Deterministic mission software implementing the film's
three technical premises as real algorithms — the Solex solar concentrator, the
mirror-walled funhouse lair, and the assassin's contract book — exposed through
the frozen `bond-api` `MissionProvider` protocol.

Local-only working tree: **no remote, never push.**

## The film as a specification

| Film premise | Software payload |
| --- | --- |
| The Solex agitator: a mirror array that turns sunlight into industrially useful heat | Heliostat field yield model plus the solar geometry that sets its daily energy |
| The funhouse: a mirror-walled maze an agent must escape and a defender wants to seal | Escape routing, bottleneck rooms, edge-disjoint route redundancy, minimum cut, cheapest escape |
| Scaramanga's contract book: one duel at a time, at a price | Weighted interval scheduling, earliest-finish greedy, and unit-time deadline scheduling |

## Modules

Six pure domain modules (standard library only — no `bond_api`, no
`infrastructure`), plus one adapter and four presentation modules.

| Module | What it computes |
| --- | --- |
| `solar_concentration.py` | Mirror-field optical power, thermal output, receiver concentration ratio, and greedy allocation of a mirror-area budget to the highest-reflectivity mirrors |
| `solar_tracking.py` | Spencer declination and equation of time, solar elevation/azimuth, the daylight window, Duffie–Beckman daily extraterrestrial and clear-sky insolation, field daily energy, and the sunrise-to-sunset beam-flux profile |
| `lair_topology.py` | The lair as an undirected graph: BFS shortest escape route, reachability, Hopcroft–Tarjan cut vertices, and the exact entry→exit bottleneck rooms (by removal and re-test) |
| `lair_flows.py` | Edmonds–Karp max flow (edge connectivity), the minimum cut of mirror walls, decomposition into explicit edge-disjoint routes, and Dijkstra cost-aware cheapest escape |
| `duel_scheduler.py` | The appointment book as half-open intervals: conflict detection, weighted-interval-scheduling maximum bounty, earliest-finish maximum count, and `active_at` |
| `deadline_scheduler.py` | Unit-time bounty contracts with deadlines: one matroid greedy with a path-compressed union–find slot lookup, viewed as both a maximum profit and a slot assignment |
| `mission.py` | The **only** module importing `bond_api`: implements the frozen `MissionProvider` and registers the film's gadgets |
| `manuscript_variables.py` | Token hydration from `manuscript/config.yaml` plus live domain calls, and the config-versus-code cross-check that raises on drift (including on a declared key it cannot verify) |
| `declarations.py` | Recomputes every claim in `data/claim_ledger.yaml` and every declaration in `experiment_plan.yaml` / `domain_profile.yaml` from the models, and raises on disagreement |
| `figures.py` | The four deterministic concept figures and the `FIGURES` registry binding them to the manuscript |
| `mission_cli.py` | Renders one lifecycle phase (or all five) as deterministic JSON |

Module-by-module detail: [`docs/architecture.md`](docs/architecture.md).

## Protocol integration

`src/the_man_with_the_golden_gun/mission.py` implements the **frozen** bond-api
`MissionProvider` — `film`, `brief`, `recon`, `plan`, `execute`, `debrief` —
and registers its domain callables and fixtures with
`bond_api.registry.GadgetRegistry` through a module-level `GADGETS()` and
`register_gadgets(registry)`. The orchestrator discovers the provider by slug
via `bond_api.discovery`.

That surface is consumed by `bond-cli`, the coordinator's reconcile step, and
the orchestrator across packages, so it does not change. The domain core never
imports `bond_api`, so it stays importable and testable if the path dependency
ever fails.

## Layout

```
src/the_man_with_the_golden_gun/
  solar_concentration.py   mirror array -> optical/thermal yield + budget allocation
  solar_tracking.py        solar position, daylight window, daily clear-sky energy
  lair_topology.py         rooms/mirrors as a graph: escape route + bottlenecks
  lair_flows.py            max flow / min cut / edge-disjoint routes / Dijkstra
  duel_scheduler.py        bounty appointment book: two exact scheduling objectives
  deadline_scheduler.py    unit-time deadline contracts (matroid greedy, union-find)
  mission.py               MissionProvider adapter (frozen bond-api protocol)
  manuscript_variables.py  token hydration + config-vs-code verification
  figures.py               deterministic matplotlib concept figures + registry
  mission_cli.py           phase rendering for the CLI wrappers
scripts/                   thin per-phase CLIs + preflight/artifacts/manuscript
manuscript/                config.yaml, references.bib, numbered token sections
docs/                      architecture, testing philosophy, agent instructions
tests/                     zero-mock real-data suite
```

## Quick start

```bash
uv sync --extra dev                                       # resolves the bond-api path dep
uv run python scripts/00_preflight.py                     # protocol discoverability
uv run python scripts/run_mission.py                      # brief..debrief (all phases)
uv run python scripts/generate_artifacts.py               # outcome JSON + figures
uv run python scripts/z_generate_manuscript_variables.py  # resolve manuscript tokens
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Everything written under `output/` is git-ignored and regenerable.

## Results

Every quantitative result — field yield, daily energy, escape routes, cut
walls, both duel schedules, deadline profit — is stated in
[`manuscript/03_results.md`](manuscript/03_results.md), and every number there
is a token injected from `manuscript_variables.py` rather than typed by hand.
The complete metric register is
[`manuscript/08_appendix.md`](manuscript/08_appendix.md). No result is
duplicated into this README, deliberately: a second copy would drift.

## Gates

| Gate | Rule |
| --- | --- |
| Tests | Zero failures, zero skips, no mock framework |
| Coverage | `pytest --cov=src --cov-fail-under=90`, line **and** branch |
| Lint / format | `ruff check` and `ruff format --check` clean on `src/` and `scripts/` |
| Types | `mypy` clean on `src/` and `scripts/` |
| Tokens | Every manuscript placeholder resolves; the config's restated facts are recomputed and must agree |
| Figures | Registry and manuscript references agree in both directions; PNGs byte-identical across runs |
| Lineage | Zero `template_code_project` strings outside docs explaining the exemplar lineage |

The measured test count and coverage from the latest gate run are in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md); this README quotes the
gate rather than the measurement so it cannot go stale.

## Documentation map

| Read | For |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Package rules, layer contract, build/test/verify commands |
| [`TODO.md`](TODO.md) | What is actually left to do |
| [`docs/architecture.md`](docs/architecture.md) | Structure of `src/` and the frozen protocol surface |
| [`docs/testing_philosophy.md`](docs/testing_philosophy.md) | Why the suite is zero-mock, real-data, deterministic |
| [`docs/agent_instructions.md`](docs/agent_instructions.md) | Read-first constraints and the gate checklist |
| [`manuscript/`](manuscript/) | The mission dossier: methods, results, setup, reproducibility, scope |
| [`STANDALONE.md`](STANDALONE.md) | The fork/standalone contract inherited from the exemplar |

## License

MIT — Daniel Ari Friedman, Active Inference Institute.
