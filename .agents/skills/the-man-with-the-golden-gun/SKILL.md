---
name: the-man-with-the-golden-gun
description: PROJECT BOND film package (SOLEX) — solar concentration yield, funhouse lair escape topology, duel/bounty scheduling, frozen bond-api MissionProvider.
version: 0.1.0
author: Daniel Ari Friedman
license: MIT
tags: [bond, film-package, solex, deterministic, mission-provider]
---

# the-man-with-the-golden-gun

Project-scoped skill for the PROJECT BOND film package at
`projects/working/bond/the_man_with_the_golden_gun/`. Mission codename SOLEX
(The Man with the Golden Gun, 1974). Load when working inside the package.

## When to Use

- Working inside the SOLEX package: running scripts, editing the domain core,
  regenerating artifacts, or driving the mission lifecycle.
- Modifying the frozen protocol adapter (`src/the_man_with_the_golden_gun/mission.py`).
- Verifying the package's contracts: layer boundaries (pure domain core vs
  single `bond_api` adapter), deterministic tests, ≥90% coverage, local-only.

## Quick Reference

```bash
cd projects/working/bond/the_man_with_the_golden_gun
uv sync --extra dev                     # resolves the bond-api path dep
uv run python scripts/00_preflight.py   # protocol discoverability gate
uv run python scripts/run_mission.py    # brief..debrief (all phases)
uv run python scripts/generate_artifacts.py
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Domain

- `solar_concentration.py` — mirror array → heat yield, optimal allocation.
- `solar_tracking.py` — solar position + daily clear-sky insolation.
- `lair_topology.py` — funhouse rooms/mirrors as graph; escape + bottlenecks.
- `lair_flows.py` — max-flow / min-cut + cost-aware escape (Dijkstra).
- `duel_scheduler.py` — bounty appointment book, weighted interval scheduling.
- `deadline_scheduler.py` — unit-time deadline bounty scheduling (union-find).

## Pitfalls

- **Frozen protocol.** implement the frozen `bond-api` `MissionProvider`; do
  not invent new types. `mission.py` is the only module importing `bond_api`.
- **Pure domain core stays standalone.** Do not import `bond_api` (or
  `infrastructure`) inside the three concept modules.
- **No mocks.** Real data + computation only; deterministic known vectors.
- **Local-only.** No remote; never push; metadata sidecars drop DOI fields.
- **Lineage gate.** Keep `template[_]code_project` strings out of your own
  docs (bracket-split any self-referential `rg`/prose so they don't self-trip).

## Cross-refs

- Package contract: [`AGENTS.md`](../../../AGENTS.md)
- Overview: [`README.md`](../../../README.md)
- Build history: [`TODO.md`](../../../TODO.md)
- BOND suite skill: `bond-suite-package-development` (guardrails + frozen
  protocol reference).
