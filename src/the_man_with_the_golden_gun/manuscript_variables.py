"""Manuscript variable hydration for the SOLEX film package.

Every ``{{TOKEN}}`` in ``manuscript/[0-9]*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` and the
deterministic domain models. Metrics are never hand-authored in prose — they
flow through this module so the manuscript cannot drift from the code.

Consumed by ``scripts/z_generate_manuscript_variables.py`` (thin wrapper); the
live cross-reference gate lives in ``tests/test_manuscript_variables.py``.
"""

from __future__ import annotations

import platform
import re
from pathlib import Path
from typing import Any

import yaml

from .deadline_scheduler import SOLEX_DEADLINE_JOBS, assign_slots, max_profit_with_deadlines
from .duel_scheduler import CANONICAL_DUELS, find_conflicts, max_bounty_schedule
from .lair_flows import (
    build_extended_lair,
    cost_aware_escape,
    edge_connectivity,
    min_cut_edges,
    unit_traversal_costs,
)
from .lair_topology import (
    CANONICAL_ENTRY,
    CANONICAL_EXIT,
    articulation_points,
    canonical_lair,
    escape_distance,
    find_escape_path,
    mirror_gated_bottlenecks,
)
from .solar_concentration import (
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
    field_optical_power,
    solex_heat_output_kw,
)
from .solar_tracking import (
    SOLEX_CLEARNESS,
    SOLEX_DAY_OF_YEAR,
    SOLEX_DNI_PEAK,
    SOLEX_LATITUDE_DEG,
    SOLEX_SOLAR_CONSTANT_W_M2,
    daily_clear_sky_insolation_kwh_m2,
    daylight_hours,
    field_daily_energy_kwh,
    solar_declination_deg,
    solar_elevation_deg,
)

__all__ = ["DEFAULT_TIMESTAMP", "generate_variables", "load_manuscript_config"]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

#: Fixed build timestamp for byte-deterministic outputs (no wall-clock).
DEFAULT_TIMESTAMP = "2026-08-04T00:00:00Z"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def _config_site(config: dict[str, Any]) -> tuple[float, int, float, float, float]:
    """Read solar-site inputs from the config ``experiment`` block (fallbacks)."""
    experiment = config.get("experiment", {})
    if not isinstance(experiment, dict):
        experiment = {}
    solar = experiment.get("solar_tracking", {})
    if not isinstance(solar, dict):
        solar = {}
    latitude = float(solar.get("latitude_deg", SOLEX_LATITUDE_DEG))
    day_of_year = int(solar.get("day_of_year", SOLEX_DAY_OF_YEAR))
    dni_peak = float(solar.get("dni_peak_w_m2", SOLEX_DNI_PEAK))
    solar_constant = float(solar.get("solar_constant_w_m2", SOLEX_SOLAR_CONSTANT_W_M2))
    clearness = float(solar.get("clearness", SOLEX_CLEARNESS))
    return latitude, day_of_year, dni_peak, solar_constant, clearness


def generate_variables(
    *,
    config_path: str | Path | None = None,
    now: str = DEFAULT_TIMESTAMP,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` → value mapping for the SOLEX manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        now: Fixed timestamp injected into the token map (defaults to the
            deterministic :data:`DEFAULT_TIMESTAMP` so outputs are byte-stable).
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        paper = {}

    latitude, day_of_year, dni_peak, solar_constant, clearness = _config_site(config)

    # --- canonical lair (phase-2 fixture) ---
    graph = canonical_lair()[0]
    path = find_escape_path(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    distance = escape_distance(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    bottlenecks = mirror_gated_bottlenecks(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    arts = articulation_points(graph)
    bounty, selected = max_bounty_schedule(CANONICAL_DUELS)
    conflicts = find_conflicts(CANONICAL_DUELS)

    # --- solar tracking ---
    declination = solar_declination_deg(day_of_year)
    noon_elevation = solar_elevation_deg(latitude, declination, 0.0)
    daylight = daylight_hours(latitude, declination)
    extraterrestrial = daily_clear_sky_insolation_kwh_m2(latitude, day_of_year, solar_constant, clearness=1.0)
    clear_sky = daily_clear_sky_insolation_kwh_m2(latitude, day_of_year, solar_constant, clearness)
    daily_energy = field_daily_energy_kwh(
        SOLEX_FIELD, latitude, day_of_year, solar_constant_w_m2=solar_constant, clearness=clearness
    )

    # --- lair flows (extended lair) ---
    ext_graph, ext_entry, ext_exit = build_extended_lair()
    connectivity = edge_connectivity(ext_graph, ext_entry, ext_exit)
    cut = min_cut_edges(ext_graph, ext_entry, ext_exit)
    cost_result = cost_aware_escape(ext_graph, unit_traversal_costs(ext_graph), ext_entry, ext_exit)

    # --- deadline scheduling ---
    deadline_total, deadline_selected = max_profit_with_deadlines(SOLEX_DEADLINE_JOBS)
    slots = assign_slots(SOLEX_DEADLINE_JOBS)
    slot_text = ", ".join(f"{slot}:{job}" for slot, job in slots)

    optical_kw = field_optical_power(SOLEX_FIELD, dni_peak) / 1000.0

    return {
        "BOND_TITLE": str(paper.get("title", "The Man with the Golden Gun: SOLEX")),
        "BOND_CODENAME": "SOLEX",
        "SOLEX_FIELD_AREA": f"{sum(m.area_m2 for m in SOLEX_FIELD):.1f}",
        "SOLEX_DNI": f"{dni_peak:.0f}",
        "SOLEX_OPTICAL_POWER_KW": f"{optical_kw:.1f}",
        "SOLEX_HEAT_KW": f"{solex_heat_output_kw():.4f}",
        "SOLEX_CONCENTRATION": f"{concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2):.2f}",
        "SOLEX_RECEIVER_AREA_M2": f"{SOLEX_RECEIVER_AREA_M2:.1f}",
        # solar tracking
        "SOLAR_LATITUDE": f"{latitude:.1f}",
        "SOLAR_DAY_OF_YEAR": str(day_of_year),
        "SOLAR_DECLINATION": f"{declination:.2f}",
        "SOLAR_NOON_ELEVATION": f"{noon_elevation:.2f}",
        "SOLAR_DAYLIGHT_HOURS": f"{daylight:.2f}",
        "SOLAR_EXTRATERRESTRIAL_KWH_M2": f"{extraterrestrial:.2f}",
        "SOLAR_CLEAR_SKY_KWH_M2": f"{clear_sky:.2f}",
        "SOLAR_FIELD_DAILY_KWH": f"{daily_energy:.1f}",
        # canonical lair
        "LAIR_NUM_ROOMS": str(len(graph)),
        "LAIR_ESCAPE_DISTANCE": str(distance) if distance is not None else "INF",
        "LAIR_ESCAPE_PATH": " -> ".join(path) if path else "NONE",
        "LAIR_NUM_BOTTLENECKS": str(len(bottlenecks)),
        "LAIR_BOTTLENECKS": ", ".join(bottlenecks) if bottlenecks else "NONE",
        "LAIR_NUM_ARTICULATION": str(len(arts)),
        # extended lair flows
        "LAIR_EXT_NUM_ROOMS": str(len(ext_graph)),
        "LAIR_EXT_EDGE_CONNECTIVITY": f"{connectivity:.0f}",
        "LAIR_EXT_MIN_CUT_EDGES": str(len(cut)),
        "LAIR_EXT_CHEAPEST_COST": f"{cost_result[0]:.0f}" if cost_result is not None else "INF",
        "LAIR_EXT_CHEAPEST_PATH": " -> ".join(cost_result[1]) if cost_result is not None else "NONE",
        # duels
        "DUEL_NUM_DUELS": str(len(CANONICAL_DUELS)),
        "DUEL_TOTAL_BOUNTY": f"{bounty:.1f}",
        "DUEL_SELECTED": ", ".join(selected) if selected else "NONE",
        "DUEL_NUM_CONFLICTS": str(len(conflicts)),
        # deadline scheduling
        "DUEL_DEADLINE_NUM_JOBS": str(len(SOLEX_DEADLINE_JOBS)),
        "DUEL_DEADLINE_MAX_PROFIT": f"{deadline_total:.1f}",
        "DUEL_DEADLINE_SELECTED": ", ".join(deadline_selected) if deadline_selected else "NONE",
        "DUEL_DEADLINE_SLOTS": slot_text if slot_text else "NONE",
        # environment
        "PYTHON_VERSION": platform.python_version(),
        "GENERATION_TIMESTAMP": now,
    }


def unresolved_tokens(text: str) -> list[str]:
    """Return any ``{{TOKEN}}`` placeholders still present in ``text``."""
    return _TOKEN_RE.findall(text)


def resolve_text(text: str, variables: dict[str, str]) -> str:
    """Substitute every ``{{TOKEN}}`` in ``text`` using ``variables``."""

    def _sub(match: re.Match[str]) -> str:
        return variables.get(match.group(0)[2:-2], match.group(0))

    return _TOKEN_RE.sub(_sub, text)


def write_resolved_tree(
    variables: dict[str, str],
    source_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
) -> list[Path]:
    """Substitute tokens across the numbered manuscript sections.

    Copies each ``manuscript/[0-9]*.md`` into ``out_dir`` (default
    ``output/manuscript/``) with every ``{{TOKEN}}`` replaced, and returns the
    written paths. Unresolved tokens are left verbatim so the live
    cross-reference test can detect drift.
    """
    src = Path(source_dir) if source_dir is not None else PACKAGE_ROOT / "manuscript"
    out = Path(out_dir) if out_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for section in sorted(src.glob("[0-9]*.md")):
        target = out / section.name
        target.write_text(resolve_text(section.read_text(encoding="utf-8"), variables), encoding="utf-8")
        written.append(target)
    return written
