# AGENTS.md — the_man_with_the_golden_gun (PROJECT BOND · mission SOLEX)

**This is an active PROJECT BOND film package** in the suite under
`projects/working/bond/`. The Man with the Golden Gun (1974) · mission
codename **SOLEX**. This is a **local-only** working tree: there is **no
remote** and it is never pushed. Scope rules are the shared BOND guardrail
preamble: work only inside this package directory, commit path-scoped inside
this repo only, no mock framework, deterministic real-data tests, ≥90%
line+branch coverage on `src/`.

## Identity

| Field | Value |
| --- | --- |
| film | The Man with the Golden Gun (1974) |
| mission codename | SOLEX |
| package slug | `the_man_with_the_golden_gun` |
| protocol | frozen `bond-api` (`MissionProvider`) — implemented in `src/the_man_with_the_golden_gun/mission.py` |
| version | 0.1.0 |

## Layer contract

| Surface | Rule |
| --- | --- |
| `src/the_man_with_the_golden_gun/solar_concentration.py`, `lair_topology.py`, `duel_scheduler.py` | Pure domain core — stdlib + numpy only, **no** `bond_api` and **no** `infrastructure` imports; importable standalone (fallback if the path dep ever fails) |
| `src/the_man_with_the_golden_gun/mission.py` | Thin adapter implementing the frozen `MissionProvider` protocol; the only module that imports `bond_api` |
| `src/the_man_with_the_golden_gun/manuscript_variables.py`, `figures.py`, `mission_cli.py` | Token hydration, deterministic figure generation, CLI output shaping |
| `scripts/` | Thin orchestrators (argv forwarding); may import `src/` and `bond_api` |

The pure domain modules never import `bond_api`; `mission.py` is the single
adapter point, and the orchestrator discovers the provider by slug
(`the_man_with_the_golden_gun.mission.MissionProvider`) via
`bond_api.discovery`. Gadgets (the domain callables/data) are registered into
the shared `bond_api.registry.GadgetRegistry`.

## Domain concepts

* **Solar concentration yield** (`solar_concentration.py`) — mirror-array →
  heat-output model; field optical power, thermal output, concentration
  ratio, and greedy optimal mirror-budget allocation.
* **Funhouse lair escape topology** (`lair_topology.py`) — rooms/mirrors as an
  undirected graph; BFS shortest escape route, reachability, Tarjan cut
  vertices, and exact `entry→exit` bottleneck rooms.
* **Assassin duel / bounty scheduling** (`duel_scheduler.py`) — appointment
  book as half-open intervals; conflict detection, weighted interval
  scheduling (max-bounty DP), earliest-finish greedy, and `active_at`.

## Manuscript variables

Metrics are **injected** from `manuscript/config.yaml` plus the deterministic
domain models via `src/the_man_with_the_golden_gun/manuscript_variables.py::generate_variables()`
— never hand-authored in prose. Run `scripts/z_generate_manuscript_variables.py`
which writes `output/data/manuscript_variables.json` and the resolved tree to
`output/manuscript/`. The live cross-reference gate
(`tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`)
asserts every `{{TOKEN}}` in `manuscript/[0-9]*.md` resolves.

## Usage

```bash
# Full mission lifecycle
uv run python scripts/run_mission.py            # brief..debrief (all phases)
uv run python scripts/00_preflight.py           # protocol discoverability gate

# Per-phase CLIs (thin wrappers)
uv run python scripts/brief.py
uv run python scripts/recon.py
uv run python scripts/plan.py
uv run python scripts/execute.py
uv run python scripts/debrief.py

# Artifacts + figures (output/ is git-ignored, regenerable)
uv run python scripts/generate_artifacts.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Testing & gates

```bash
uv sync --extra dev                       # installs bond-api path dep + dev tools
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format src/ scripts/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**'   # -> zero
```

The suite targets 100% line+branch on `src/` with a zero-mock, real-data test
approach (known-vector assertions on the three domain models, protocol
conformance, deterministic serialization round-trips, live token gate, and
subprocess CLI smoke tests).

## Protocol integration

`[tool.uv.sources] bond-api = { path = "/Users/4d/Documents/GitHub/template/projects/working/bond/bond-api" }`
is declared in `pyproject.toml`. bond-api is **done and frozen** — do not
invent new protocol types; implement the frozen `MissionProvider` surface
(`film`, `brief`, `recon`, `plan`, `execute`, `debrief`) and the 11 frozen
dataclasses.

## Publishing note

Local-only: no remote, never push. Metadata sidecars (`.zenodo.json`,
`CITATION.cff`, `codemeta.json`) drop DOI fields because the tree is not
published.

## Troubleshooting

* Missing `bond_api`: run `uv sync --extra dev` (the path dependency is only
  resolved after sync).
* script `ModuleNotFoundError` for the package: run from this package root so
  `pythonpath = [".", "src"]` applies; scripts self-insert `src/` via
  `scripts/_bootstrap.py`.
* Figure tests hanging: `MPLBACKEND=Agg` is forced in `tests/conftest.py` and
  at import of `figures.py`.

## See also

* BOND suite skill: `bond-suite-package-development` (guardrails + frozen
  protocol reference).
* Frozen protocol record: `references/bond-api-phase1.md` in that skill.
