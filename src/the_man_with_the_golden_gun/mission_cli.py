"""Thin output-shaping for the SOLEX mission CLIs.

One function, :func:`run_phase`, renders a single mission lifecycle stage (or
``all`` for the full five-stage flow) as deterministic JSON via the frozen
``bond_api.serialization`` wire format. The ``scripts/`` wrappers are just
argv forwarding to this module. Business logic stays in the domain core;
everything here is presentation.

Exit convention: ``0`` on success, ``2`` for an unknown phase (mirrors the
project's argparse exit-code contract).
"""

from __future__ import annotations

import sys

from bond_api.protocol import ReconRequest
from bond_api.serialization import to_json

from .mission import MissionProvider

__all__ = ["PHASES", "run_phase"]

PHASES = ("brief", "recon", "plan", "execute", "debrief")


def run_phase(phase: str) -> int:
    """Render and print one mission stage (or ``all``) as deterministic JSON."""
    provider = MissionProvider()
    brief = provider.brief()

    if phase == "brief":
        print(to_json(brief))
        return 0
    if phase == "recon":
        print(to_json(provider.recon(ReconRequest(goal="assess the SOLEX domain"))))
        return 0
    if phase == "plan":
        print(to_json(provider.plan(brief)))
        return 0
    if phase == "execute":
        outcome = provider.execute(provider.plan(brief))
        print(to_json(outcome))
        return 0
    if phase == "debrief":
        plan = provider.plan(brief)
        outcome = provider.execute(plan)
        print(to_json(provider.debrief(outcome)))
        return 0
    if phase == "all":
        for label in PHASES:
            print(f"== {label} ==")
            run_phase(label)
        return 0

    print(f"unknown phase {phase!r}; expected {'|'.join(PHASES)} or all", file=sys.stderr)
    return 2
