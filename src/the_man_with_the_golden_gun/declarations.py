"""Verification of the SOLEX package's declared-fact sidecars.

Four YAML files in this package restate, in prose-adjacent form, facts whose
source of truth is code:

* ``manuscript/config.yaml`` (``experiment:`` block) — canonical model inputs;
* ``data/claim_ledger.yaml`` — the registered numeric claims and their evidence;
* ``experiment_plan.yaml`` and ``domain_profile.yaml`` — declarative overlays
  naming the package's concepts, metrics and expected artifacts.

A restatement nobody checks is a second source of truth, and a second source of
truth rots. An adversarial audit of this package found exactly that: both
overlays still described a three-module package four modules after the fact,
and the claim ledger was read by nothing at all. This module makes every one of
those declarations load-bearing — each is recomputed from the domain models and
compared, and a disagreement raises.

:func:`verify_claim_ledger` runs during token generation (through
``manuscript_variables.verify_declared_experiment``, because
``config.yaml`` declares the ledger path). :func:`verify_experiment_plan` and
:func:`verify_domain_profile` are gated by ``tests/test_declarations.py``.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import yaml

from .deadline_scheduler import SOLEX_DEADLINE_JOBS, max_profit_with_deadlines
from .duel_scheduler import CANONICAL_DUELS, find_conflicts, max_bounty_schedule
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
    canonical_lair,
    escape_distance,
    mirror_gated_bottlenecks,
)
from .solar_concentration import (
    SOLEX_DNI,
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
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
)

__all__ = [
    "CLAIM_RECOMPUTERS",
    "DATA_ARTIFACTS",
    "DOMAIN_MODULES",
    "FILM_TITLE",
    "MISSION_CODENAME",
    "PACKAGE_NAME",
    "PACKAGE_ROOT",
    "experiment_expectations",
    "expected_script_artifacts",
    "verify_claim_ledger",
    "verify_domain_profile",
    "verify_experiment_plan",
]

PACKAGE_NAME = __name__.split(".")[0]
PACKAGE_ROOT = Path(__file__).resolve().parents[2]

#: Mission codename, in the pure layer so token generation never needs the
#: ``bond_api`` adapter. ``tests/test_mission.py`` binds it to
#: ``mission.CODENAME`` so the adapter and this constant cannot diverge.
MISSION_CODENAME = "SOLEX"

#: Human-readable film title for the source film, in the pure layer so it can
#: be compared against ``domain_profile.yaml``'s ``film`` field without the
#: ``bond_api`` adapter. Note this is the *title*, distinct from the package
#: slug ``PACKAGE_NAME`` and the provider's ``mission.FILM`` slug.
FILM_TITLE = "The Man with the Golden Gun (1974)"

#: The pure domain modules of the SOLEX core, in dependency order. Single
#: source of truth for "which concepts this package implements": the
#: ``{{NUM_DOMAIN_MODULES}}`` token, ``experiment_plan.yaml`` and
#: ``domain_profile.yaml`` are all checked against it.
DOMAIN_MODULES: tuple[str, ...] = (
    "solar_concentration",
    "solar_tracking",
    "lair_topology",
    "lair_flows",
    "duel_scheduler",
    "deadline_scheduler",
)

#: Non-figure artifacts the ``scripts/`` orchestrators write under ``output/``.
DATA_ARTIFACTS: tuple[str, ...] = (
    "output/data/solex_outcome.json",
    "output/data/manuscript_variables.json",
)

DEFAULT_CLAIM_LEDGER_PATH = PACKAGE_ROOT / "data" / "claim_ledger.yaml"
DEFAULT_EXPERIMENT_PLAN_PATH = PACKAGE_ROOT / "experiment_plan.yaml"
DEFAULT_DOMAIN_PROFILE_PATH = PACKAGE_ROOT / "domain_profile.yaml"

_SYMBOL_DEFINITION = "^(?:def\\s+|class\\s+)?{symbol}\\b"


def expected_script_artifacts() -> tuple[str, ...]:
    """Every artifact path the scripts produce, derived from the registries."""
    return DATA_ARTIFACTS + tuple(f"output/figures/{filename}" for _, filename in FIGURES)


def _load_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML file that must parse to a top-level mapping."""
    if not path.is_file():
        raise FileNotFoundError(f"declared-fact file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be a top-level mapping, got {type(data).__name__}")
    return data


def _disagreement(source: str, label: str, declared: object, computed: object) -> ValueError:
    return ValueError(f"{source} declares {label}={declared!r} but the domain model computes {computed!r}")


def _escape_distance_value() -> float:
    graph, entry, exit_ = canonical_lair()
    distance = escape_distance(graph, entry, exit_)
    if distance is None:  # pragma: no cover - the canonical lair is always escapable
        raise ValueError("canonical lair has no escape route; the claim ledger cannot be verified")
    return float(distance)


def _bottleneck_count() -> float:
    graph, entry, exit_ = canonical_lair()
    return float(len(mirror_gated_bottlenecks(graph, entry, exit_)))


def _extended_min_cut_size() -> float:
    graph, entry, exit_ = build_extended_lair()
    return float(len(min_cut_edges(graph, entry, exit_)))


def _extended_edge_connectivity() -> float:
    graph, entry, exit_ = build_extended_lair()
    return float(edge_connectivity(graph, entry, exit_))


def _cheapest_escape_cost() -> float:
    graph, entry, exit_ = build_extended_lair()
    result = cost_aware_escape(graph, unit_traversal_costs(graph), entry, exit_)
    if result is None:  # pragma: no cover - the extended lair is always escapable
        raise ValueError("extended lair has no escape route; the claim ledger cannot be verified")
    return float(result[0])


def _clear_sky_insolation() -> float:
    return daily_clear_sky_insolation_kwh_m2(
        SOLEX_LATITUDE_DEG, SOLEX_DAY_OF_YEAR, SOLEX_SOLAR_CONSTANT_W_M2, SOLEX_CLEARNESS
    )


def _field_daily_energy() -> float:
    return field_daily_energy_kwh(
        SOLEX_FIELD,
        SOLEX_LATITUDE_DEG,
        SOLEX_DAY_OF_YEAR,
        solar_constant_w_m2=SOLEX_SOLAR_CONSTANT_W_M2,
        clearness=SOLEX_CLEARNESS,
    )


#: ``claim name -> (recompute, decimal places)`` for every entry the ledger may
#: carry. The verifier requires this registry and the ledger to have exactly the
#: same key set, so a claim cannot be added to the ledger without a
#: recomputation, nor silently dropped from the ledger while code still backs it.
CLAIM_RECOMPUTERS: dict[str, tuple[Callable[[], float], int]] = {
    "solar_field_area_m2": (lambda: sum(m.area_m2 for m in SOLEX_FIELD), 1),
    "solar_dni_w_per_m2": (lambda: SOLEX_DNI, 1),
    "solar_heat_output_kw": (solex_heat_output_kw, 4),
    "solar_concentration_ratio": (lambda: concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2), 2),
    "lair_escape_distance_passages": (_escape_distance_value, 0),
    "lair_num_bottleneck_rooms": (_bottleneck_count, 0),
    "duel_max_bounty": (lambda: max_bounty_schedule(CANONICAL_DUELS)[0], 1),
    "duel_num_conflicts": (lambda: float(len(find_conflicts(CANONICAL_DUELS))), 0),
    "solar_declination_deg": (lambda: solar_declination_deg(SOLEX_DAY_OF_YEAR), 2),
    "solar_daylight_hours": (
        lambda: daylight_hours(SOLEX_LATITUDE_DEG, solar_declination_deg(SOLEX_DAY_OF_YEAR)),
        2,
    ),
    "solar_clear_sky_insolation_kwh_m2": (_clear_sky_insolation, 2),
    "solar_field_daily_energy_kwh": (_field_daily_energy, 1),
    "lair_edge_connectivity": (_extended_edge_connectivity, 0),
    "lair_min_cut_edges": (_extended_min_cut_size, 0),
    "lair_cheapest_escape_cost": (_cheapest_escape_cost, 1),
    "deadline_max_profit": (lambda: max_profit_with_deadlines(SOLEX_DEADLINE_JOBS)[0], 1),
}


def experiment_expectations() -> dict[str, object]:
    """Recompute every canonical input the YAML sidecars are allowed to restate.

    Keys are dotted leaf paths matching the ``experiment`` block of
    ``manuscript/config.yaml`` (and, for the shared subset, the
    ``canonical_inputs`` block of ``experiment_plan.yaml``). Values come from
    the domain models, never from a config file — that is what makes comparing
    against them a check rather than a tautology.
    """
    graph, entry, exit_ = build_extended_lair()
    return {
        "codename": MISSION_CODENAME,
        "daily_dni_w_per_m2": SOLEX_DNI,
        "receiver_area_m2": SOLEX_RECEIVER_AREA_M2,
        "lair_entry": CANONICAL_ENTRY,
        "lair_exit": CANONICAL_EXIT,
        "duel_max_bounty": max_bounty_schedule(CANONICAL_DUELS)[0],
        "solar_tracking.latitude_deg": SOLEX_LATITUDE_DEG,
        "solar_tracking.day_of_year": SOLEX_DAY_OF_YEAR,
        "solar_tracking.dni_peak_w_m2": SOLEX_DNI_PEAK,
        "solar_tracking.solar_constant_w_m2": SOLEX_SOLAR_CONSTANT_W_M2,
        "solar_tracking.clearness": SOLEX_CLEARNESS,
        "extended_lair.entry": entry,
        "extended_lair.exit": exit_,
        "extended_lair.edge_disjoint_routes": edge_connectivity(graph, entry, exit_),
    }


def compare_declaration(source: str, label: str, declared: object, expected: object) -> None:
    """Raise unless ``declared`` equals ``expected`` (numerically or as text)."""
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        agrees = float(declared) == float(expected)  # type: ignore[arg-type]
    else:
        agrees = str(declared) == str(expected)
    if not agrees:
        raise _disagreement(source, label, declared, expected)


def _verify_evidence(claim: str, entry: Mapping[str, Any]) -> None:
    """Check that a ledger entry's ``evidence`` and ``test`` really exist.

    ``evidence`` is ``<path>::<symbol>``; both the file and a top-level
    definition of the symbol must be present, so the ledger cannot cite a code
    path that was renamed or deleted.
    """
    for field in ("evidence", "test"):
        if field not in entry:
            raise ValueError(f"claim ledger entry {claim!r} is missing its {field!r} field")
    evidence = str(entry["evidence"])
    module_ref, _, symbol = evidence.partition("::")
    if not symbol:
        raise ValueError(f"claim ledger entry {claim!r} has evidence {evidence!r} without a ::symbol")
    module_path = PACKAGE_ROOT / module_ref
    if not module_path.is_file():
        raise ValueError(f"claim ledger entry {claim!r} cites missing evidence file {module_ref}")
    pattern = re.compile(_SYMBOL_DEFINITION.format(symbol=re.escape(symbol)), re.MULTILINE)
    if not pattern.search(module_path.read_text(encoding="utf-8")):
        raise ValueError(f"claim ledger entry {claim!r} cites {symbol!r}, which {module_ref} does not define")
    test_path = PACKAGE_ROOT / str(entry["test"])
    if not test_path.is_file():
        raise ValueError(f"claim ledger entry {claim!r} cites missing test file {entry['test']}")


def verify_claim_ledger(path: str | Path | None = None) -> tuple[str, ...]:
    """Recompute every claim in ``data/claim_ledger.yaml`` from the models.

    Args:
        path: Override for the ledger location.

    Returns:
        The verified claim names, in ledger order.

    Raises:
        ValueError: if the ledger's claim set differs from
            :data:`CLAIM_RECOMPUTERS`, if a recorded value disagrees with the
            recomputed one at the recorded precision, or if an entry's evidence
            or test path does not exist.
    """
    ledger_path = Path(path) if path is not None else DEFAULT_CLAIM_LEDGER_PATH
    document = _load_mapping(ledger_path)
    claims = document.get("claims")
    if not isinstance(claims, dict) or not claims:
        raise ValueError(f"{ledger_path.name} must carry a non-empty `claims` mapping")

    unknown = sorted(set(claims) - set(CLAIM_RECOMPUTERS))
    if unknown:
        raise ValueError(f"{ledger_path.name} registers claim(s) with no recomputation: {', '.join(unknown)}")
    missing = sorted(set(CLAIM_RECOMPUTERS) - set(claims))
    if missing:
        raise ValueError(f"{ledger_path.name} is missing recomputable claim(s): {', '.join(missing)}")

    verified: list[str] = []
    for claim, entry in claims.items():
        if not isinstance(entry, dict) or "value" not in entry:
            raise ValueError(f"claim ledger entry {claim!r} must be a mapping carrying a `value`")
        recompute, places = CLAIM_RECOMPUTERS[claim]
        computed = round(recompute(), places)
        if float(entry["value"]) != computed:
            raise _disagreement(ledger_path.name, f"claims.{claim}.value", entry["value"], computed)
        _verify_evidence(claim, entry)
        verified.append(claim)
    return tuple(verified)


_EXPERIMENT_PLAN_KEYS = frozenset(
    {"experiment", "canonical_inputs", "primary_metrics", "expected_figures", "baseline", "ablation"}
)

#: Allowed top-level keys of ``domain_profile.yaml``. The verifier raises on any
#: key outside this set, so a new, unchecked section cannot be added to the
#: profile silently — the sibling guard ``_EXPERIMENT_PLAN_KEYS`` provides for
#: ``experiment_plan.yaml``.
_DOMAIN_PROFILE_KEYS = frozenset(
    {"project", "codename", "film", "review_gates", "source_policy", "artifact_expectations", "protocol"}
)


def verify_experiment_plan(path: str | Path | None = None) -> tuple[str, ...]:
    """Check ``experiment_plan.yaml`` against the live code.

    Verified: the codename, the concept list (must equal
    :data:`DOMAIN_MODULES` in order), every canonical input, every primary
    metric (must be a registered ledger claim), and the expected figure paths
    (must equal the ``figures.FIGURES`` registry in order).

    The ``baseline`` and ``ablation`` blocks are free prose and are deliberately
    *not* checked; an unknown top-level key raises rather than passing silently,
    so a new unchecked section cannot be added without a decision.
    """
    plan_path = Path(path) if path is not None else DEFAULT_EXPERIMENT_PLAN_PATH
    document = _load_mapping(plan_path)
    source = plan_path.name

    unknown = sorted(set(document) - _EXPERIMENT_PLAN_KEYS)
    if unknown:
        raise ValueError(f"{source} carries unverified top-level key(s): {', '.join(unknown)}")

    experiment = document.get("experiment")
    if not isinstance(experiment, dict):
        raise ValueError(f"{source} must carry an `experiment` mapping")
    compare_declaration(source, "experiment.codename", experiment.get("codename"), MISSION_CODENAME)

    concepts = experiment.get("concepts")
    if not isinstance(concepts, list):
        raise ValueError(f"{source} must carry `experiment.concepts` as a list")
    declared_concepts: list[str] = []
    for item in concepts:
        if not isinstance(item, dict) or len(item) != 1:
            raise ValueError(f"{source}: every `experiment.concepts` entry must be a single-key mapping")
        declared_concepts.append(next(iter(item)))
    if tuple(declared_concepts) != DOMAIN_MODULES:
        raise _disagreement(source, "experiment.concepts", tuple(declared_concepts), DOMAIN_MODULES)

    inputs = document.get("canonical_inputs")
    if not isinstance(inputs, dict):
        raise ValueError(f"{source} must carry a `canonical_inputs` mapping")
    expectations = experiment_expectations()
    unverifiable = sorted(set(inputs) - set(expectations))
    if unverifiable:
        raise ValueError(f"{source} declares uncheckable canonical input(s): {', '.join(unverifiable)}")
    for key, declared in inputs.items():
        compare_declaration(source, f"canonical_inputs.{key}", declared, expectations[key])

    metrics = document.get("primary_metrics")
    if not isinstance(metrics, list) or not metrics:
        raise ValueError(f"{source} must carry a non-empty `primary_metrics` list")
    unregistered = sorted({str(m) for m in metrics} - set(CLAIM_RECOMPUTERS))
    if unregistered:
        raise ValueError(f"{source} lists primary metric(s) with no ledger claim: {', '.join(unregistered)}")

    expected_figures = [f"output/figures/{filename}" for _, filename in FIGURES]
    declared_figures = document.get("expected_figures")
    if declared_figures != expected_figures:
        raise _disagreement(source, "expected_figures", declared_figures, expected_figures)

    return ("experiment.codename", "experiment.concepts", "canonical_inputs", "primary_metrics", "expected_figures")


def verify_domain_profile(
    path: str | Path | None = None,
    *,
    coverage_gate: int | None = None,
) -> tuple[str, ...]:
    """Check ``domain_profile.yaml`` against the live code.

    Verified: the project slug (equals the installed package name), the
    codename, the film title (equals :data:`FILM_TITLE`), the module list
    (equals :data:`DOMAIN_MODULES`), the expected script artifacts (equal the
    data artifacts plus the figure registry), the adapter path named by
    ``protocol.adapter`` (must be an existing file), and — when
    ``coverage_gate`` is supplied — the declared coverage floor. An unknown
    top-level key raises rather than passing silently.
    """
    profile_path = Path(path) if path is not None else DEFAULT_DOMAIN_PROFILE_PATH
    document = _load_mapping(profile_path)
    source = profile_path.name

    unknown = sorted(set(document) - _DOMAIN_PROFILE_KEYS)
    if unknown:
        raise ValueError(f"{source} carries unverified top-level key(s): {', '.join(unknown)}")

    compare_declaration(source, "project", document.get("project"), PACKAGE_NAME)
    compare_declaration(source, "codename", document.get("codename"), MISSION_CODENAME)
    compare_declaration(source, "film", document.get("film"), FILM_TITLE)

    protocol = document.get("protocol")
    if not isinstance(protocol, dict) or "adapter" not in protocol:
        raise ValueError(f"{source} must carry a `protocol.adapter` mapping entry")
    adapter = PACKAGE_ROOT / str(protocol["adapter"])
    if not adapter.is_file():
        raise ValueError(
            f"{source} declares protocol.adapter {protocol['adapter']!r} but the adapter file does not exist"
        )

    policy = document.get("source_policy")
    if not isinstance(policy, dict):
        raise ValueError(f"{source} must carry a `source_policy` mapping")
    modules = policy.get("modules")
    if modules != list(DOMAIN_MODULES):
        raise _disagreement(source, "source_policy.modules", modules, list(DOMAIN_MODULES))

    expectations = document.get("artifact_expectations")
    if not isinstance(expectations, dict):
        raise ValueError(f"{source} must carry an `artifact_expectations` mapping")
    declared_artifacts = expectations.get("script_artifacts")
    expected_artifacts = list(expected_script_artifacts())
    if declared_artifacts != expected_artifacts:
        raise _disagreement(source, "artifact_expectations.script_artifacts", declared_artifacts, expected_artifacts)

    checked = [
        "project",
        "codename",
        "film",
        "protocol.adapter",
        "source_policy.modules",
        "artifact_expectations.script_artifacts",
    ]
    if coverage_gate is not None:
        gates = document.get("review_gates")
        if not isinstance(gates, dict):
            raise ValueError(f"{source} must carry a `review_gates` mapping")
        compare_declaration(
            source, "review_gates.coverage_min_line_branch", gates.get("coverage_min_line_branch"), coverage_gate
        )
        checked.append("review_gates.coverage_min_line_branch")
    return tuple(checked)
