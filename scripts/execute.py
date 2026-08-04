#!/usr/bin/env python
"""SOLEX mission phase: execute. Runs the domain solvers and prints the outcome."""

from __future__ import annotations


import _bootstrap  # noqa: E402,F401

from the_man_with_the_golden_gun.mission_cli import run_phase  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(run_phase("execute"))  # noqa: B904
