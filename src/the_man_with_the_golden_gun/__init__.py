"""the_man_with_the_golden_gun — SOLEX mission software.

PROJECT BOND film package for *The Man with the Golden Gun* (1974), mission
codename **SOLEX**. Pure, deterministic domain core:

* :mod:`~the_man_with_the_golden_gun.solar_concentration` — mirror-array to
  heat-output yield model;
* :mod:`~the_man_with_the_golden_gun.lair_topology` — funhouse lair
  escape-topology graph solver;
* :mod:`~the_man_with_the_golden_gun.duel_scheduler` — assassin duel / bounty
  appointment-book scheduling and conflict resolution.

:mod:`~the_man_with_the_golden_gun.mission` adapts this domain core to the
frozen BOND-API :class:`~bond_api.protocol.MissionProvider` contract via
``src/the_man_with_the_golden_gun/mission.py`` (top-level ``MissionProvider``).
"""

from __future__ import annotations

from .duel_scheduler import (
    Appointment,
    CANONICAL_DUELS,
    active_at,
    earliest_finish_schedule,
    find_conflicts,
    max_bounty_schedule,
    overlaps,
)
from .lair_topology import (
    articulation_points,
    build_lair_graph,
    canonical_lair,
    escape_distance,
    find_escape_path,
    mirror_gated_bottlenecks,
    reachable_rooms,
)
from .solar_concentration import (
    Mirror,
    SOLEX_DNI,
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
    field_optical_power,
    mirror_optical_power,
    optimal_mirror_allocation,
    solex_heat_output_kw,
    solex_yield,
    thermal_output_kw,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # solar_concentration
    "Mirror",
    "SOLEX_DNI",
    "SOLEX_FIELD",
    "SOLEX_RECEIVER_AREA_M2",
    "concentration_ratio",
    "field_optical_power",
    "mirror_optical_power",
    "optimal_mirror_allocation",
    "solex_heat_output_kw",
    "solex_yield",
    "thermal_output_kw",
    # lair_topology
    "articulation_points",
    "build_lair_graph",
    "canonical_lair",
    "escape_distance",
    "find_escape_path",
    "mirror_gated_bottlenecks",
    "reachable_rooms",
    # duel_scheduler
    "Appointment",
    "CANONICAL_DUELS",
    "active_at",
    "earliest_finish_schedule",
    "find_conflicts",
    "max_bounty_schedule",
    "overlaps",
]
