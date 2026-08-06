"""Manuscript variable hydration for the SOLEX film package.

Every ``{{TOKEN}}`` in the manuscript sources — the numbered sections and
``preamble.md`` — resolves through :func:`generate_variables`, which reads
``manuscript/config.yaml`` and the deterministic domain models. Metrics are
never hand-authored in prose; they flow through this module so the manuscript
cannot drift from the code.

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
from .declarations import (
    DOMAIN_MODULES,
    MISSION_CODENAME,
    compare_declaration,
    experiment_expectations,
    verify_claim_ledger,
)
from .duel_scheduler import (
    CANONICAL_DUELS,
    earliest_finish_schedule,
    find_conflicts,
    max_bounty_schedule,
)
from .figures import FIGURES
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
    optimal_mirror_allocation,
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

__all__ = [
    "DEFAULT_TIMESTAMP",
    "DOMAIN_MODULES",
    "generate_variables",
    "load_manuscript_config",
    "manuscript_sources",
    "verify_declared_experiment",
]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

#: Manuscript files hydrated by :func:`write_resolved_tree` and scanned by the
#: live token gate: the numbered sections plus the Pandoc preamble, which also
#: carries a ``{{TOKEN}}`` in its front matter.
MANUSCRIPT_SOURCE_GLOBS: tuple[str, ...] = ("[0-9]*.md", "preamble.md")
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

#: Fixed build timestamp for byte-deterministic outputs (no wall-clock).
DEFAULT_TIMESTAMP = "2026-08-04T00:00:00Z"

#: Mirror-area budget (m^2) used for the reported greedy-allocation example.
#: Smaller than the 300 m^2 field so the allocation actually has to choose.
MIRROR_BUDGET_M2 = 200.0

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


def _markdown_rows(rows: list[tuple[str, ...]]) -> str:
    """Render table-body rows as a single markdown string for token injection.

    Fixture tables in the manuscript are generated from the live constants
    rather than transcribed, so a change to a canonical fixture cannot leave a
    stale table behind in the setup section.
    """
    return "\n".join("| " + " | ".join(cells) + " |" for cells in rows)


def _mismatch(label: str, declared: object, computed: object) -> str:
    return f"manuscript config declares {label}={declared!r} but the domain model computes {computed!r}"


def _declared_leaf_paths(experiment: dict[str, Any]) -> set[str]:
    """Dotted paths of every leaf declaration in the ``experiment`` block.

    A nested mapping contributes one path per sub-key; anything else (scalar or
    list) is itself a leaf. This is what makes the completeness gate below
    exhaustive rather than a hand-maintained list that can fall behind.
    """
    paths: set[str] = set()
    for key, value in experiment.items():
        if isinstance(value, dict):
            paths.update(f"{key}.{sub}" for sub in value)
        else:
            paths.add(key)
    return paths


def _leaf_value(experiment: dict[str, Any], path: str) -> Any:
    value: Any = experiment
    for part in path.split("."):
        value = value[part]
    return value


def verify_declared_experiment(config: dict[str, Any]) -> tuple[str, ...]:
    """Cross-check *every* ``experiment`` declaration in the config.

    ``manuscript/config.yaml`` restates canonical facts that live in code (the
    mission codename, the DNI, the receiver aperture, the solar-site geometry,
    the lair entry/exit rooms, the maximum duel bounty, the extended lair, the
    deadline book, and the claim-ledger path). Those restatements are only
    worth carrying if they are *load-bearing*, so this function:

    1. recomputes each declared value from the domain models and raises on
       disagreement — including the whole claim ledger, via
       :func:`declarations.verify_claim_ledger`; and
    2. refuses to pass when the block declares a key it does not know how to
       verify, which is what makes "every key in this block is checked" an
       enforced invariant instead of a comment.

    Args:
        config: A parsed ``manuscript/config.yaml`` mapping.

    Returns:
        The dotted paths that were present and verified. An empty tuple means
        the config has no ``experiment`` mapping at all (the fallback path used
        by the minimal configs in the test-suite).

    Raises:
        ValueError: on the first declaration that disagrees with the models, or
            if any declared key has no verification.
    """
    experiment = config.get("experiment")
    if not isinstance(experiment, dict):
        return ()

    expectations = experiment_expectations()
    declared = _declared_leaf_paths(experiment)
    verifiable = set(expectations) | {"deadline_jobs", "data_ledger"}
    unverified = sorted(declared - verifiable)
    if unverified:
        raise ValueError("manuscript config declares experiment key(s) with no verification: " + ", ".join(unverified))

    checked: list[str] = []
    for path in sorted(declared & set(expectations)):
        compare_declaration(
            "manuscript config", f"experiment.{path}", _leaf_value(experiment, path), expectations[path]
        )
        checked.append(path)

    if "deadline_jobs" in declared:
        declared_jobs = experiment["deadline_jobs"]
        if not isinstance(declared_jobs, list):
            raise ValueError(_mismatch("experiment.deadline_jobs", declared_jobs, "a list of job mappings"))
        declared_book = tuple(
            (str(job["id"]), int(job["deadline"]), float(job["profit"]))
            for job in declared_jobs
            if isinstance(job, dict)
        )
        computed_book = tuple((job.id, job.deadline, job.profit) for job in SOLEX_DEADLINE_JOBS)
        if declared_book != computed_book:
            raise ValueError(_mismatch("experiment.deadline_jobs", declared_book, computed_book))
        checked.append("deadline_jobs")

    if "data_ledger" in declared:
        verify_claim_ledger(PACKAGE_ROOT / str(experiment["data_ledger"]))
        checked.append("data_ledger")

    return tuple(checked)


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
    verify_declared_experiment(config)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        paper = {}
    mission = config.get("mission", {})
    if not isinstance(mission, dict):
        mission = {}
    gates = config.get("gates", {})
    if not isinstance(gates, dict):
        gates = {}

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

    # --- derived surface descriptors (never hand-counted in prose) ---
    budget_selection = optimal_mirror_allocation(SOLEX_FIELD, MIRROR_BUDGET_M2, dni=dni_peak)
    earliest_finish = earliest_finish_schedule(CANONICAL_DUELS)
    earliest_finish_bounty = sum(a.bounty for a in CANONICAL_DUELS if a.id in set(earliest_finish))

    # --- sensitivity sweeps (live model calls over a parameter grid) ---
    # Clearness-factor sensitivity: how much of the extraterrestrial resource
    # the clear-sky model retains, and what that means for the daily yield.
    clearness_sweep_rows: list[tuple[str, ...]] = []
    for kappa in (0.60, 0.75, 0.90):
        _cs = daily_clear_sky_insolation_kwh_m2(latitude, day_of_year, solar_constant, clearness=kappa)
        _fe = field_daily_energy_kwh(
            SOLEX_FIELD, latitude, day_of_year, solar_constant_w_m2=solar_constant, clearness=kappa
        )
        clearness_sweep_rows.append((f"{kappa:.2f}", f"{_cs:.2f}", f"{_fe:.1f}"))
    # Site-latitude sensitivity: moving the canonical field equatorward raises
    # the overhead sun at the solstice and with it the concentrated daily energy.
    latitude_sweep_rows: list[tuple[str, ...]] = []
    for _lat in (0.0, SOLEX_LATITUDE_DEG, 23.44):
        _fe = field_daily_energy_kwh(
            SOLEX_FIELD, _lat, day_of_year, solar_constant_w_m2=solar_constant, clearness=clearness
        )
        latitude_sweep_rows.append((f"{_lat:g}", f"{_fe:.1f}"))

    return {
        "BOND_TITLE": str(paper.get("title", "The Man with the Golden Gun: SOLEX")),
        "BOND_CODENAME": MISSION_CODENAME,
        "SOLEX_FIELD_AREA": f"{sum(m.area_m2 for m in SOLEX_FIELD):.1f}",
        "SOLEX_DNI": f"{dni_peak:.0f}",
        "SOLEX_OPTICAL_POWER_KW": f"{optical_kw:.1f}",
        "SOLEX_HEAT_KW": f"{solex_heat_output_kw():.4f}",
        "SOLEX_CONCENTRATION": f"{concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2):.2f}",
        "SOLEX_RECEIVER_AREA_M2": f"{SOLEX_RECEIVER_AREA_M2:.1f}",
        "SOLEX_NUM_MIRRORS": str(len(SOLEX_FIELD)),
        "SOLEX_BUDGET_M2": f"{MIRROR_BUDGET_M2:.0f}",
        "SOLEX_BUDGET_SELECTION": ", ".join(budget_selection) if budget_selection else "NONE",
        "SOLEX_MIRROR_ROWS": _markdown_rows(
            [(f"`{m.id}`", f"{m.area_m2:.1f}", f"{m.reflectivity:.2f}") for m in SOLEX_FIELD]
        ),
        # solar tracking
        "SOLAR_LATITUDE": f"{latitude:.1f}",
        "SOLAR_DAY_OF_YEAR": str(day_of_year),
        "SOLAR_DECLINATION": f"{declination:.2f}",
        "SOLAR_NOON_ELEVATION": f"{noon_elevation:.2f}",
        "SOLAR_DAYLIGHT_HOURS": f"{daylight:.2f}",
        "SOLAR_EXTRATERRESTRIAL_KWH_M2": f"{extraterrestrial:.2f}",
        "SOLAR_CLEAR_SKY_KWH_M2": f"{clear_sky:.2f}",
        "SOLAR_FIELD_DAILY_KWH": f"{daily_energy:.1f}",
        "SOLAR_CLEARNESS_SWEEP_ROWS": _markdown_rows(clearness_sweep_rows),
        "SOLAR_LATITUDE_SWEEP_ROWS": _markdown_rows(latitude_sweep_rows),
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
        "LAIR_EXT_MIN_CUT_WALLS": ", ".join(f"{u}-{v}" for u, v in cut) if cut else "NONE",
        # duels
        "DUEL_NUM_DUELS": str(len(CANONICAL_DUELS)),
        "DUEL_BOOK_ROWS": _markdown_rows(
            [
                (f"`{a.id}`", f"[{a.start:g}, {a.end:g})", f"{a.bounty:g}", a.target or "—")
                for a in sorted(CANONICAL_DUELS, key=lambda a: (a.start, a.id))
            ]
        ),
        "DUEL_TOTAL_BOUNTY": f"{bounty:.1f}",
        "DUEL_SELECTED": ", ".join(selected) if selected else "NONE",
        "DUEL_NUM_SELECTED": str(len(selected)),
        "DUEL_NUM_CONFLICTS": str(len(conflicts)),
        "DUEL_EARLIEST_FINISH": ", ".join(earliest_finish) if earliest_finish else "NONE",
        "DUEL_NUM_EARLIEST_FINISH": str(len(earliest_finish)),
        "DUEL_EARLIEST_FINISH_BOUNTY": f"{earliest_finish_bounty:.1f}",
        # deadline scheduling
        "DUEL_DEADLINE_NUM_JOBS": str(len(SOLEX_DEADLINE_JOBS)),
        "DUEL_DEADLINE_BOOK_ROWS": _markdown_rows(
            [(f"`{j.id}`", str(j.deadline), f"{j.profit:g}") for j in SOLEX_DEADLINE_JOBS]
        ),
        "DUEL_DEADLINE_NUM_SLOTS": str(max((j.deadline for j in SOLEX_DEADLINE_JOBS), default=0)),
        "DUEL_DEADLINE_MAX_PROFIT": f"{deadline_total:.1f}",
        "DUEL_DEADLINE_SELECTED": ", ".join(deadline_selected) if deadline_selected else "NONE",
        "DUEL_DEADLINE_SLOTS": slot_text if slot_text else "NONE",
        # package / reproducibility surface
        "PACKAGE_VERSION": str(paper.get("version", "0.0.0")),
        "MISSION_SEED": str(mission.get("seed", 0)),
        "NUM_DOMAIN_MODULES": str(len(DOMAIN_MODULES)),
        "DOMAIN_MODULE_LIST": ", ".join(f"{name}.py" for name in DOMAIN_MODULES),
        "NUM_FIGURES": str(len(FIGURES)),
        "COVERAGE_GATE_PCT": str(gates.get("coverage_fail_under", 90)),
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


def manuscript_sources(source_dir: str | Path | None = None) -> list[Path]:
    """Every manuscript file that carries ``{{TOKEN}}`` placeholders.

    One function serves both the writer (:func:`write_resolved_tree`) and the
    live token gate in the test-suite, so the set that gets hydrated and the
    set that gets scanned cannot diverge — which is exactly how
    ``preamble.md``'s ``{{BOND_TITLE}}`` survived unhydrated and ungated until
    an audit found it.
    """
    src = Path(source_dir) if source_dir is not None else PACKAGE_ROOT / "manuscript"
    found: dict[str, Path] = {}
    for pattern in MANUSCRIPT_SOURCE_GLOBS:
        for candidate in src.glob(pattern):
            found[candidate.name] = candidate
    return [found[name] for name in sorted(found)]


def write_resolved_tree(
    variables: dict[str, str],
    source_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
) -> list[Path]:
    """Substitute tokens across every manuscript source file.

    Copies each file returned by :func:`manuscript_sources` (the numbered
    sections plus ``preamble.md``) into ``out_dir`` (default
    ``output/manuscript/``) with every ``{{TOKEN}}`` replaced, and returns the
    written paths. Unresolved tokens are left verbatim so the live
    cross-reference test can detect drift.
    """
    out = Path(out_dir) if out_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for section in manuscript_sources(source_dir):
        target = out / section.name
        target.write_text(resolve_text(section.read_text(encoding="utf-8"), variables), encoding="utf-8")
        written.append(target)
    return written
