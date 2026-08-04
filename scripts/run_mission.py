#!/usr/bin/env python
"""SOLEX mission CLI runner — execute any lifecycle phase or the full flow.

Usage:
    python scripts/run_mission.py [brief|recon|plan|execute|debrief|all]
The optional argument defaults to ``all``; each phase prints its protocol
object as deterministic JSON.
"""

from __future__ import annotations

import sys

import _bootstrap  # noqa: E402,F401  (side effect: inserts src/ onto sys.path)

from the_man_with_the_golden_gun.mission_cli import run_phase  # noqa: E402

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    raise SystemExit(run_phase(phase))  # noqa: B904
