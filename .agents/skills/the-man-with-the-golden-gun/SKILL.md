---
name: the-man-with-the-golden-gun
description: PROJECT BOND film package (SOLEX) — solar concentration yield, funhouse lair escape topology, duel/bounty scheduling, frozen bond-api MissionProvider.
version: 0.1.0
author: Daniel Ari Friedman
license: MIT
tags: [bond, film-package, solex, deterministic, mission-provider]
---

# the-man-with-the-golden-gun

Project-scoped skill for the PROJECT BOND film package — the standalone mirror
of `projects/working/bond/the_man_with_the_golden_gun/`. Mission codename SOLEX
(The Man with the Golden Gun, 1974). Load when working inside the package.

## When to Use

- Working inside the SOLEX package: running scripts, editing the domain core,
  regenerating artifacts, or driving the mission lifecycle.
- Modifying the frozen protocol adapter (`src/the_man_with_the_golden_gun/mission.py`).
- Verifying the package's contracts: layer boundaries (pure domain core vs
  single `bond_api` adapter), deterministic tests, ≥90% coverage, frozen protocol.

## Quick Reference

```bash
cd "$(git rev-parse --show-toplevel)"   # or any path to this package
uv sync --extra dev                     # needs the suite monorepo; else see STANDALONE.md
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
  `infrastructure`) inside any of the six domain modules listed above.
- **Bottlenecks are not articulation points.** `mirror_gated_bottlenecks`
  separates a specific entry from a specific exit; `articulation_points` cuts
  the graph anywhere. Conflating them is the easiest wrong answer here.
- **Config is verified, not decorative.** `manuscript/config.yaml`'s
  `experiment` block is recomputed by `verify_declared_experiment()`; changing
  a canonical fixture without updating the config raises at token generation.
- **No mocks.** Real data + computation only; deterministic known vectors.
- **Published mirror.** The suite copy is local-only; this mirror is pushed, and
  the metadata sidecars drop DOI fields because nothing is archived.
- **Lineage gate.** Keep `template[_]code_project` strings out of your own
  docs (bracket-split any self-referential `rg`/prose so they don't self-trip).

## Cross-refs

- Package contract: [`AGENTS.md`](../../../AGENTS.md)
- Overview: [`README.md`](../../../README.md)
- Open work and integration points: [`TODO.md`](../../../TODO.md)
- Module-by-module structure: [`docs/architecture.md`](../../../docs/architecture.md)
- Test doctrine: [`docs/testing_philosophy.md`](../../../docs/testing_philosophy.md)
- BOND suite skill: `bond-suite-package-development` (guardrails + frozen
  protocol reference).
