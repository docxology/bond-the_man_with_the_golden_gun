"""SOLEX MissionProvider — the thin adapter from domain core to the frozen BOND-API protocol.

This module is the discovery contract for the orchestrator: it is importable as
``the_man_with_the_golden_gun.mission`` (the package slug, which is also the
top-level module name) and exposes ``MissionProvider`` at module top level.

The provider declares film ``the_man_with_the_golden_gun`` / codename ``SOLEX``
and drives the three pure domain modules — solar concentration, lair escape
topology, and duel/bounty scheduling — through the five lifecycle stages:

* brief   — declare the mission, its assets (canonical mirrors, lair, duels)
  and its determinism constraints;
* recon   — survey what the mission needs to learn;
* plan    — plan the three domain steps plus a provenance record;
* execute — run the domain solvers and return a deterministic outcome carrying
  full provenance;
* debrief — reflect on the outcome with the standing lessons.

The domain core is dependency-free and never imports ``bond_api``; only this
adapter touches the protocol. Gadgets (the domain callables/data) are
registered into the shared :class:`~bond_api.registry.GadgetRegistry`.
"""

from __future__ import annotations

import hashlib
import json

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from . import __version__
from .duel_scheduler import (
    CANONICAL_DUELS,
    active_at,
    earliest_finish_schedule,
    find_conflicts,
    max_bounty_schedule,
)
from .lair_topology import (
    CANONICAL_ENTRY,
    CANONICAL_EXIT,
    articulation_points,
    escape_distance,
    find_escape_path,
    mirror_gated_bottlenecks,
)
from .solar_concentration import (
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
    optimal_mirror_allocation,
    solex_yield,
)

__all__ = [
    "FILM",
    "CODENAME",
    "PACKAGE_VERSION",
    "SEED",
    "GADGETS",
    "Gadgets",
    "MissionProvider",
    "mission_id",
    "register_gadgets",
    "run_domain",
]

#: The film slug this provider answers to (must equal the package slug).
FILM = "the_man_with_the_golden_gun"
CODENAME = "SOLEX"
PACKAGE_VERSION = __version__
#: Fixed deterministic seed (0 disables randomness; we use 3 for provenance).
SEED = 3


# ---------------------------------------------------------------------------
# Gadgets — register the domain surface with the bond-api GadgetRegistry.
# ---------------------------------------------------------------------------

#: Domain surface exposed as gadgets (opaque payloads the registry stores).
Gadgets = dict[str, object]


def GADGETS() -> dict[str, object]:  # noqa: N802 — PascalCase-like callable kept simple
    """Build the film's gadget map (deterministic, no shared mutable state)."""
    return {
        "solar_field": SOLEX_FIELD,
        "solar_receiver_area_m2": SOLEX_RECEIVER_AREA_M2,
        "solar_concentration_ratio": concentration_ratio,
        "solar_optimal_allocation": optimal_mirror_allocation,
        "lair_entry": CANONICAL_ENTRY,
        "lair_exit": CANONICAL_EXIT,
        "lair_articulation_points": articulation_points,
        "lair_bottlenecks": mirror_gated_bottlenecks,
        "duels": CANONICAL_DUELS,
        "duel_max_bounty": max_bounty_schedule,
        "duel_earliest_finish": earliest_finish_schedule,
        "duel_active_at": active_at,
    }


_registry = GadgetRegistry()
_registry.register(FILM, GADGETS())


def register_gadgets(registry: GadgetRegistry) -> None:
    """Register the SOLEX gadgets into an arbitrary (e.g. film-owned) registry."""
    registry.register(FILM, GADGETS())


def _input_hash() -> str:
    """Deterministic sha256 fingerprint of the canonical mission inputs."""
    payload = {
        "film": FILM,
        "codename": CODENAME,
        "mirrors": [(m.id, m.area_m2, m.reflectivity) for m in SOLEX_FIELD],
        "receiver_area_m2": SOLEX_RECEIVER_AREA_M2,
        "duels": [(a.id, a.start, a.end, a.bounty, a.target) for a in CANONICAL_DUELS],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def run_domain() -> dict[str, object]:
    """Run the three SOLEX domain solvers and collect a serialisable outcome.

    Returns a flat mapping whose values are JSON-serialisable (primitives,
    lists, and tuples) so the result can be handed to the protocol's outcome
    and round-tripped by ``bond_api.serialization``.
    """
    from .lair_topology import adjacency as _adj

    solar = solex_yield()
    graph = _adj()
    path = find_escape_path(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    bottlenecks = mirror_gated_bottlenecks(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    duels = max_bounty_schedule(CANONICAL_DUELS)
    conflicts = find_conflicts(CANONICAL_DUELS)
    return {
        "solar": solar,
        "lair": {
            "entry": CANONICAL_ENTRY,
            "exit": CANONICAL_EXIT,
            "escape_path": list(path) if path else None,
            "escape_distance": escape_distance(graph, CANONICAL_ENTRY, CANONICAL_EXIT),
            "bottleneck_rooms": list(bottlenecks),
            "num_rooms": len(graph),
            "articulation_points": sorted(articulation_points(graph)),
        },
        "duel": {
            "total_bounty": duels[0],
            "selected_duels": list(duels[1]),
            "num_conflicts": len(conflicts),
            "conflicts": list(conflicts),
        },
        "integrated": {
            "escape_path": list(path) if path else None,
            "escape_distance": escape_distance(graph, CANONICAL_ENTRY, CANONICAL_EXIT),
            "max_duel_bounty": duels[0],
            "heat_output_kw": solar["heat_output_kw"],
        },
    }


# ---------------------------------------------------------------------------
# MissionProvider — the frozen protocol contract.
# ---------------------------------------------------------------------------


class MissionProvider:  # noqa: N801 — class name fixed by the discovery contract
    """Deterministic SOLEX implementation of the BOND-API mission protocol."""

    film = FILM

    def brief(self) -> MissionBrief:
        """Declare the SOLEX mission: three objectives, canonical assets."""
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=(
                "model solar concentration yield (mirror array to heat)",
                "solve the funhouse lair escape topology (rooms/mirrors as graph)",
                "schedule the assassin duel/bounty appointment book",
            ),
            assets=(
                Asset(kind="mirror_field", name="solex_field", payload={"dni_w_per_m2": 1000.0}),
                Asset(kind="lair", name="funhouse_lair", payload=None),
                Asset(kind="duel_book", name="bounty_schedule", payload=None),
            ),
            constraints=(
                Constraint(kind="determinism", detail="fixed seed, no random draws, no wall-clock in artifacts"),
                Constraint(kind="real_data", detail="all results computed from the real domain models"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the domain, assets, and determinism constraint."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(label="solar", detail="mirror field modelled by area and reflectivity"),
                Finding(label="lair", detail="funhouse rooms and mirror passages form an undirected graph"),
                Finding(label="duel", detail="appointment book solved as weighted interval scheduling"),
                Finding(label="constraints", detail="deterministic, real-data-only execution"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the three domain steps plus a provenance check."""
        return MissionPlan(
            steps=(
                Step(name="solar", action="compute_field_yield", params={"objective": brief.objectives[0]}),
                Step(name="lair", action="solve_escape_topology", params={"objective": brief.objectives[1]}),
                Step(name="duel", action="schedule_appointments", params={"objective": brief.objectives[2]}),
                Step(name="record", action="attach_provenance", params={"seed": SEED, "package": PACKAGE_VERSION}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the domain solvers and return a deterministic, provenanced outcome."""
        domain = run_domain()
        return MissionOutcome(
            success=True,
            results=domain,
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=SEED,
                input_hash=_input_hash(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Reflect on the mission; record the standing SOLEX lessons."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "concentrated heat scales with field reflectivity, not raw area",
                "bottleneck rooms are single points of failure in the funhouse",
                "weighted interval scheduling maximises bounty without double-booking",
            ),
        )


def mission_id() -> dict[str, str]:
    """Package identity record (slug, codename, version) for preflight use."""
    return {"film": FILM, "codename": CODENAME, "version": PACKAGE_VERSION}
