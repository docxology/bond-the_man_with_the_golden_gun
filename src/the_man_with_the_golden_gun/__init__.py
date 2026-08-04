"""the_man_with_the_golden_gun — SOLEX mission software.

PROJECT BOND film package for *The Man with the Golden Gun* (1974), mission
codename **SOLEX**. Pure, deterministic domain core:

* :mod:`~the_man_with_the_golden_gun.solar_concentration` — mirror-array to
  heat-output yield model;
* :mod:`~the_man_with_the_golden_gun.solar_tracking` — solar position and
  daily (clear-sky) insolation model;
* :mod:`~the_man_with_the_golden_gun.lair_topology` — funhouse lair
  escape-topology graph solver;
* :mod:`~the_man_with_the_golden_gun.lair_flows` — lair max-flow / min-cut /
  cost-aware escape analysis;
* :mod:`~the_man_with_the_golden_gun.duel_scheduler` — assassin duel / bounty
  appointment-book scheduling and conflict resolution;
* :mod:`~the_man_with_the_golden_gun.deadline_scheduler` — unit-time deadline
  bounty scheduling (max profit with deadlines).

:mod:`~the_man_with_the_golden_gun.mission` adapts this domain core to the
frozen BOND-API :class:`~bond_api.protocol.MissionProvider` contract via
``src/the_man_with_the_golden_gun/mission.py`` (top-level ``MissionProvider``).
"""

from __future__ import annotations

from .deadline_scheduler import (
    SOLEX_DEADLINE_JOBS,
    DeadlineJob,
    assign_slots,
    canonical_deadline_book,
    max_profit_with_deadlines,
)
from .duel_scheduler import (
    Appointment,
    CANONICAL_DUELS,
    active_at,
    earliest_finish_schedule,
    find_conflicts,
    max_bounty_schedule,
    overlaps,
)
from .lair_flows import (
    EXTENDED_ENTRY,
    EXTENDED_EXIT,
    build_extended_lair,
    cost_aware_escape,
    edge_connectivity,
    edge_disjoint_escape_routes,
    edmonds_karp,
    min_cut_edges,
    unit_traversal_costs,
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
from .solar_tracking import (
    SOLEX_CLEARNESS,
    SOLEX_DAY_OF_YEAR,
    SOLEX_DNI_PEAK,
    SOLEX_LATITUDE_DEG,
    SOLEX_SOLAR_CONSTANT_W_M2,
    beam_flux_kw_m2,
    daily_clear_sky_insolation_kwh_m2,
    daily_extraterrestrial_insolation_kwh_m2,
    daylight_hours,
    equation_of_time_min,
    field_daily_energy_kwh,
    solar_azimuth_deg,
    solar_declination_deg,
    solar_elevation_deg,
    solar_hour_angle_deg,
    solex_daily_profile,
    sun_position,
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
    # solar_tracking
    "SOLEX_CLEARNESS",
    "SOLEX_DAY_OF_YEAR",
    "SOLEX_DNI_PEAK",
    "SOLEX_LATITUDE_DEG",
    "SOLEX_SOLAR_CONSTANT_W_M2",
    "beam_flux_kw_m2",
    "daily_clear_sky_insolation_kwh_m2",
    "daily_extraterrestrial_insolation_kwh_m2",
    "daylight_hours",
    "equation_of_time_min",
    "field_daily_energy_kwh",
    "solar_azimuth_deg",
    "solar_declination_deg",
    "solar_elevation_deg",
    "solar_hour_angle_deg",
    "solex_daily_profile",
    "sun_position",
    # lair_topology
    "articulation_points",
    "build_lair_graph",
    "canonical_lair",
    "escape_distance",
    "find_escape_path",
    "mirror_gated_bottlenecks",
    "reachable_rooms",
    # lair_flows
    "EXTENDED_ENTRY",
    "EXTENDED_EXIT",
    "build_extended_lair",
    "cost_aware_escape",
    "edge_connectivity",
    "edge_disjoint_escape_routes",
    "edmonds_karp",
    "min_cut_edges",
    "unit_traversal_costs",
    # duel_scheduler
    "Appointment",
    "CANONICAL_DUELS",
    "active_at",
    "earliest_finish_schedule",
    "find_conflicts",
    "max_bounty_schedule",
    "overlaps",
    # deadline_scheduler
    "SOLEX_DEADLINE_JOBS",
    "DeadlineJob",
    "assign_slots",
    "canonical_deadline_book",
    "max_profit_with_deadlines",
]
