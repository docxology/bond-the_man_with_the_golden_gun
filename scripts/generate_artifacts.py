#!/usr/bin/env python
"""SOLEX artifact generation: run the domain solvers and render the figures.

Writes ``output/data/solex_outcome.json`` (deterministic mission outcome) and
the three concept figures under ``output/figures/``. ``output/`` is
git-ignored because every artifact here is regenerable.
"""

from __future__ import annotations

import json
from pathlib import Path

import _bootstrap  # noqa: E402,F401

from the_man_with_the_golden_gun.figures import generate_all_figures  # noqa: E402
from the_man_with_the_golden_gun.mission import run_domain  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    outcome = run_domain()
    outcome_path = data_dir / "solex_outcome.json"
    outcome_path.write_text(json.dumps(outcome, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    figures = generate_all_figures(PROJECT_ROOT / "output" / "figures")

    print(f"wrote {outcome_path}")
    for figure in figures:
        print(f"wrote {figure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())  # noqa: B904
