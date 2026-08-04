"""Tests for the SOLEX MissionProvider (frozen bond-api protocol, real data)."""

from __future__ import annotations

from bond_api.protocol import (
    MissionProvider as Protocol,
    Provenance,
    run_mission,
)
from bond_api.registry import GadgetRegistry
from bond_api.serialization import from_json, to_json

from the_man_with_the_golden_gun.mission import (
    CODENAME,
    FILM,
    SEED,
    GADGETS,
    MissionProvider,
    _input_hash,
    mission_id,
    register_gadgets,
    run_domain,
)


def test_provider_satisfies_protocol() -> None:
    assert isinstance(MissionProvider(), Protocol)


def test_identity() -> None:
    provider = MissionProvider()
    assert provider.film == FILM == "the_man_with_the_golden_gun"
    assert provider.brief().codename == CODENAME == "SOLEX"
    assert mission_id() == {"film": FILM, "codename": CODENAME, "version": "0.1.0"}


def test_brief_objectives_and_assets() -> None:
    brief = MissionProvider().brief()
    assert len(brief.objectives) == 3
    assert len(brief.assets) == 3
    assert any(c.kind == "determinism" for c in brief.constraints)


def test_run_mission_full_flow() -> None:
    from bond_api.protocol import ReconRequest

    debrief = run_mission(MissionProvider(), ReconRequest(goal="survey the SOLEX domain"))
    assert debrief.outcome.success is True
    assert len(debrief.lessons) == 3
    # integrated results present
    assert debrief.outcome.results["integrated"]["max_duel_bounty"] == 13.0
    assert debrief.outcome.provenance.seed == SEED


def test_execute_deterministic() -> None:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    first = provider.execute(plan)
    second = provider.execute(plan)
    assert first.results == second.results
    assert first.provenance == second.provenance
    assert first.provenance.input_hash == second.provenance.input_hash


def test_input_hash_deterministic() -> None:
    assert _input_hash() == _input_hash()
    assert len(_input_hash()) == 64


def test_provenance_fields() -> None:
    outcome = MissionProvider().execute(MissionProvider().plan(MissionProvider().brief()))
    p: Provenance = outcome.provenance
    assert p.seed == 3
    assert p.wall_time_s == 0.0
    assert p.input_hash != ""


def test_serialization_roundtrip() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    text = to_json(outcome)
    decoded = from_json(text)
    assert decoded == outcome


def test_gadgets_registration() -> None:
    registry = GadgetRegistry()
    register_gadgets(registry)
    assert registry.contains(FILM, "solar_field")
    assert registry.contains(FILM, "duel_max_bounty")
    assert len(registry.gadgets_for(FILM)) == len(GADGETS())


def test_gadget_callable() -> None:
    registry = GadgetRegistry()
    register_gadgets(registry)
    max_bounty = registry.lookup(FILM, "duel_max_bounty")
    total, selected = max_bounty(registry.lookup(FILM, "duels"))
    assert total == 13.0
    assert selected[0] == "B"


def test_run_domain_shape() -> None:
    domain = run_domain()
    assert set(domain) == {"solar", "lair", "duel", "integrated"}
    assert domain["lair"]["escape_distance"] == 4
    assert domain["duel"]["total_bounty"] == 13.0
