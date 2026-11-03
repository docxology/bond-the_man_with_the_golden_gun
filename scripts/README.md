# scripts/ — the entry points into the package

Every script here is a thin orchestrator: it shapes `argv`, calls into `src/`, and prints or writes the
result. The mathematics lives in `src/the_man_with_the_golden_gun/`, which is also where the tests
point. Nothing outside this directory imports from here, `src/` never does, and the one shared helper
(`_bootstrap.py`) exists for these scripts alone.

| Script | What it does |
| --- | --- |
| `00_preflight.py` | The discoverability gate: the package is found by slug and satisfies the frozen `MissionProvider` surface. Run this first after a change to the protocol surface |
| `run_mission.py` | The runner: `[brief\|recon\|plan\|execute\|debrief\|all]`, defaulting to the full flow, each phase printed as deterministic JSON |
| `brief.py`, `recon.py`, `plan.py`, `execute.py`, `debrief.py` | One lifecycle phase each — the same output as the corresponding `run_mission.py` argument |
| `generate_artifacts.py` | Runs the domain solvers and renders the figures into the ignored `output/` |
| `z_generate_manuscript_variables.py` | Hydrates the manuscript `{{TOKEN}}`s, writing `output/data/manuscript_variables.json` and the resolved tree under `output/manuscript/`, and exiting non-zero if any placeholder survives |
| `_bootstrap.py` | Not an entry point: the shared `sys.path` helper that the others import, so a bare `python scripts/<name>.py` import of the package works without an install |

## How to run them

From the repository root, which is what makes `pythonpath = [".", "src"]` in `pyproject.toml` apply:

```bash
uv run python scripts/00_preflight.py
uv run python scripts/run_mission.py
uv run python scripts/z_generate_manuscript_variables.py
```

Run on 2026-11-03 at `026d766`: the preflight reports the film slug and codename and exits 0; the
lifecycle runner prints protocol objects tagged with their `__bond_type__`; the manuscript generator
resolves the whole tree and reports that every token resolved, exit 0. None of them writes outside the
ignored `output/`.

## What is not here

No logic to edit when a model changes — that lives in `src/`. No console-script entry points: the
commands above are the supported route, and nothing else invokes these files. No `output/`: it is
generated, ignored, and safe to delete.
