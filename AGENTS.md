# AGENTS.md — the_man_with_the_golden_gun (PROJECT BOND · mission SOLEX)

**This is an active PROJECT BOND film package** in the suite under
`projects/working/bond/`. The Man with the Golden Gun (1974) · mission codename
**SOLEX**. This checkout is the package's standalone mirror, pushed to GitHub as
`docxology/bond-the_man_with_the_golden_gun`; only the suite tree is local-only.
Scope rules are the shared BOND guardrail preamble — work only inside this
package directory, commit path-scoped inside this repository only, no mock
framework, deterministic real-data tests, and a ≥90% line+branch
coverage gate on `src/`.

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
| `solar_concentration.py`, `solar_tracking.py`, `lair_topology.py`, `lair_flows.py`, `duel_scheduler.py`, `deadline_scheduler.py` | Pure domain core — standard library only, **no** `bond_api` and **no** `infrastructure` imports; importable standalone if the path dependency ever fails |
| `mission.py` | The single adapter implementing the frozen `MissionProvider`; the only module in `src/` that imports `bond_api` |
| `manuscript_variables.py`, `declarations.py`, `figures.py`, `mission_cli.py` | Presentation: token hydration, declared-fact verification (config, claim ledger, YAML overlays), deterministic figures, CLI output shaping |
| `scripts/` | Thin orchestrators — argv forwarding and I/O only; may import `src/` and `bond_api` |

The orchestrator discovers the provider by slug
(`the_man_with_the_golden_gun.mission.MissionProvider`) via
`bond_api.discovery`. Gadgets are registered into the shared
`bond_api.registry.GadgetRegistry`.

## Domain concepts

* **Solar concentration yield** (`solar_concentration.py`) — field optical
  power, thermal output, receiver concentration ratio, and greedy mirror-budget
  allocation (whole mirrors, descending reflectivity).
* **Solar tracking and daily insolation** (`solar_tracking.py`) — Spencer
  declination and equation of time, elevation/azimuth, daylight window,
  Duffie–Beckman daily extraterrestrial and clear-sky insolation, field daily
  energy, and the daily beam-flux profile.
* **Funhouse lair escape topology** (`lair_topology.py`) — BFS shortest escape
  route, reachability, Hopcroft–Tarjan cut vertices, and the exact entry→exit
  bottleneck rooms. Bottlenecks and articulation points answer *different*
  questions; do not conflate them.
* **Lair flow analysis** (`lair_flows.py`) — Edmonds–Karp max flow, the minimum
  cut of mirror walls, edge-disjoint route decomposition, and Dijkstra
  cost-aware escape over a 10-room extended fixture.
* **Duel / bounty scheduling** (`duel_scheduler.py`) — conflict detection,
  weighted interval scheduling (maximum bounty), earliest-finish greedy
  (maximum count), and `active_at`. Both objectives are reported because they
  disagree on the canonical book.
* **Deadline bounty scheduling** (`deadline_scheduler.py`) — unit-time
  contracts solved by one matroid greedy with a union–find slot lookup; the
  profit and the slot assignment are two views of a single run.

## Manuscript variables

Metrics are **injected**, never hand-authored: `manuscript/config.yaml` plus
live calls into the domain models, through
`manuscript_variables.generate_variables()`. Run
`scripts/z_generate_manuscript_variables.py`, which writes
`output/data/manuscript_variables.json` and the resolved tree to
`output/manuscript/`, and exits non-zero if any placeholder survives.

Five gates hold this in place:

* `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
  — every placeholder in a hydrated file must be a key the generator produces.
  The scanned set comes from `manuscript_sources()`, the same function
  `write_resolved_tree()` writes from (numbered sections **plus**
  `preamble.md`), and is asserted non-empty, so the gate can neither pass
  vacuously nor miss a file that is hydrated.
* `manuscript_variables.verify_declared_experiment()` — every leaf key the
  config's `experiment` block declares is recomputed from the models and raises
  on disagreement, and a declared key with no recomputation raises too, so the
  check cannot silently cover less than the block.
* `declarations.verify_claim_ledger()` — every value in `data/claim_ledger.yaml`
  is recomputed at its recorded precision, its cited evidence symbol and test
  file must exist, and the ledger's claim set must equal the recomputation
  registry in both directions. Runs during token generation, because the config
  declares the ledger path.
* `tests/test_declarations.py` — `experiment_plan.yaml` and
  `domain_profile.yaml` are checked against `DOMAIN_MODULES`, the `FIGURES`
  registry, the canonical inputs, the ledger claim ids, and the coverage gate.
* `tests/test_mission.py::test_manuscript_config_objectives_match_the_brief` —
  the config's mission objectives must equal the provider's brief verbatim
  (and `test_codename_constant_is_bound_to_the_pure_layer` binds
  `declarations.MISSION_CODENAME` to `mission.CODENAME`).

Each of those gates ships with a positive control: a test that tampers with one
declaration in a temporary copy and asserts the verifier goes red.

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

# Artifacts + figures (output/ is git-ignored and regenerable)
uv run python scripts/generate_artifacts.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Testing and gates

```bash
uv sync --extra dev                       # installs the bond-api path dep + dev tools
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' --glob '!.venv/**'   # -> the two permitted lineage mentions only (`README.md`, `docs/AGENTS.md`); any third hit is a defect
```

Required: zero failures, zero skips, coverage at or above the gate, clean lint
and types, and no lineage strings. The measured test count and coverage from the
latest run are recorded in `docs/_generated/COUNTS.md` — read them there rather
than quoting a figure into prose that will drift.

The suite is zero-mock and real-data: known-vector assertions on every domain
model, structural-property assertions (pairwise edge-disjointness, cut value
equal to flow value, reported profit equal to the summed profit of the assigned
slots), protocol conformance, serialization round-trips, byte-identity checks on
the rendered figures, the live token gate, and real subprocess runs of the CLI
scripts. The reasoning behind each choice is in `docs/testing_philosophy.md`.

## Protocol integration

`[tool.uv.sources]` declares `bond-api = { path = "../bond-api" }` in
`pyproject.toml` — the sibling `bond-api` directory, which inside a BOND suite
tree is `projects/working/bond/bond-api`, the same directory the relative path
resolves to. bond-api is **done and frozen** — do not invent
protocol types. Implement the frozen `MissionProvider` surface (`film`,
`brief`, `recon`, `plan`, `execute`, `debrief`) and the frozen dataclasses.
`GADGETS()` and `register_gadgets()` keep their current shape; deepen *inside*
the package by adding modules and enriching `run_domain()`'s payload. The full
frozen surface is tabulated in `docs/architecture.md`.

## Publishing note

Published as a standalone mirror (the suite copy is the local-only tree). The
metadata sidecars (`.zenodo.json`, `CITATION.cff`, `codemeta.json`) omit DOI
fields because there is no Zenodo deposit and no archived release.

## Troubleshooting

* Missing `bond_api`: run `uv sync --extra dev` — the path dependency is only
  resolved after a sync.
* `ModuleNotFoundError` for the package in a script: run from this package root
  so `pythonpath = [".", "src"]` applies. Scripts also self-insert `src/` via
  `scripts/_bootstrap.py`.
* Figure tests hanging: `MPLBACKEND=Agg` is forced in `tests/conftest.py` and at
  import of `figures.py`.
* Token generation raising a config mismatch: that is
  `verify_declared_experiment()` doing its job — a canonical fixture changed
  without `manuscript/config.yaml` being updated to match.

## See also

* [`docs/architecture.md`](docs/architecture.md) — module-by-module structure
  and the frozen protocol surface.
* [`docs/testing_philosophy.md`](docs/testing_philosophy.md) — test doctrine.
* [`docs/agent_instructions.md`](docs/agent_instructions.md) — read-first
  constraints and the gate checklist.
* BOND suite skill: `bond-suite-package-development` (guardrails plus the frozen
  protocol reference at `references/bond-api-phase1.md`).
