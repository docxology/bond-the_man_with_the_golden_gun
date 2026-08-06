"""Gates for the SOLEX package's declared-fact sidecars.

Three YAML files restate facts whose source of truth is code. Each test here
runs the real verifier against the real shipped file (so the declaration cannot
go stale) and then, for every checked declaration, tampers with a copy in
`tmp_path` and asserts the verifier goes red (so the check cannot be
decoration). Real files, real YAML, real recomputation — no mocks.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from the_man_with_the_golden_gun.declarations import (
    CLAIM_RECOMPUTERS,
    DOMAIN_MODULES,
    MISSION_CODENAME,
    PACKAGE_NAME,
    PACKAGE_ROOT,
    expected_script_artifacts,
    verify_claim_ledger,
    verify_domain_profile,
    verify_experiment_plan,
)
from the_man_with_the_golden_gun.figures import FIGURES

LEDGER_PATH = PACKAGE_ROOT / "data" / "claim_ledger.yaml"
PLAN_PATH = PACKAGE_ROOT / "experiment_plan.yaml"
PROFILE_PATH = PACKAGE_ROOT / "domain_profile.yaml"


def _load(path: Path) -> dict[str, Any]:
    return copy.deepcopy(yaml.safe_load(path.read_text(encoding="utf-8")))


def _write(tmp_path: Path, name: str, document: Any) -> Path:
    target = tmp_path / name
    target.write_text(yaml.safe_dump(document), encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# claim ledger
# ---------------------------------------------------------------------------


def test_live_claim_ledger_is_recomputed_and_agrees() -> None:
    """Every claim in the shipped ledger is recomputed from the models."""
    verified = verify_claim_ledger()
    assert set(verified) == set(CLAIM_RECOMPUTERS)
    assert len(verified) == len(CLAIM_RECOMPUTERS) == 16


@pytest.mark.parametrize("claim", sorted(CLAIM_RECOMPUTERS))
def test_every_claim_value_can_fail(tmp_path, claim: str) -> None:  # type: ignore[no-untyped-def]
    """Positive control, one case per claim: a wrong value is caught.

    Perturbing by +1 is safe for every claim because each recorded value is
    recomputed at its recorded precision, so no rounding can absorb the change.
    """
    ledger = _load(LEDGER_PATH)
    ledger["claims"][claim]["value"] = float(ledger["claims"][claim]["value"]) + 1.0
    with pytest.raises(ValueError, match=f"claims.{claim}.value"):
        verify_claim_ledger(_write(tmp_path, "claim_ledger.yaml", ledger))


def test_ledger_must_match_the_recomputation_registry_in_both_directions(tmp_path) -> None:  # type: ignore[no-untyped-def]
    ledger = _load(LEDGER_PATH)
    ledger["claims"]["bond_martinis_shaken"] = {
        "value": 1.0,
        "evidence": "src/the_man_with_the_golden_gun/mission.py::CODENAME",
        "test": "tests/test_mission.py",
    }
    with pytest.raises(ValueError, match="no recomputation: bond_martinis_shaken"):
        verify_claim_ledger(_write(tmp_path, "claim_ledger.yaml", ledger))

    ledger = _load(LEDGER_PATH)
    del ledger["claims"]["deadline_max_profit"]
    with pytest.raises(ValueError, match="missing recomputable claim"):
        verify_claim_ledger(_write(tmp_path, "claim_ledger.yaml", ledger))


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        (lambda entry: entry.pop("evidence"), "missing its 'evidence' field"),
        (lambda entry: entry.pop("test"), "missing its 'test' field"),
        (lambda entry: entry.__setitem__("evidence", "src/the_man_with_the_golden_gun/lair_flows.py"), "::symbol"),
        (lambda entry: entry.__setitem__("evidence", "src/gone.py::thing"), "missing evidence file"),
        (
            lambda entry: entry.__setitem__("evidence", "src/the_man_with_the_golden_gun/lair_flows.py::renamed_away"),
            "does not define",
        ),
        (lambda entry: entry.__setitem__("test", "tests/test_gone.py"), "missing test file"),
    ],
)
def test_claim_evidence_paths_are_checked(tmp_path, mutate, needle: str) -> None:  # type: ignore[no-untyped-def]
    """The evidence column is verified, not decorative."""
    ledger = _load(LEDGER_PATH)
    mutate(ledger["claims"]["lair_min_cut_edges"])
    with pytest.raises(ValueError, match=needle):
        verify_claim_ledger(_write(tmp_path, "claim_ledger.yaml", ledger))


def test_claim_ledger_structural_failures(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(FileNotFoundError, match="not found"):
        verify_claim_ledger(tmp_path / "absent.yaml")

    bad = tmp_path / "claim_ledger.yaml"
    bad.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="top-level mapping"):
        verify_claim_ledger(bad)

    with pytest.raises(ValueError, match="non-empty `claims` mapping"):
        verify_claim_ledger(_write(tmp_path, "claim_ledger.yaml", {"claims": {}}))

    ledger = _load(LEDGER_PATH)
    ledger["claims"]["duel_max_bounty"] = 13.0  # not a mapping
    with pytest.raises(ValueError, match="must be a mapping carrying a `value`"):
        verify_claim_ledger(_write(tmp_path, "claim_ledger.yaml", ledger))


# ---------------------------------------------------------------------------
# experiment_plan.yaml
# ---------------------------------------------------------------------------


def test_live_experiment_plan_matches_the_code() -> None:
    checked = verify_experiment_plan()
    assert "experiment.concepts" in checked and "expected_figures" in checked


def test_experiment_plan_concepts_track_the_module_set(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The drift this file actually suffered: concepts left behind by new modules."""
    plan = _load(PLAN_PATH)
    assert [next(iter(item)) for item in plan["experiment"]["concepts"]] == list(DOMAIN_MODULES)
    plan["experiment"]["concepts"] = plan["experiment"]["concepts"][:3]
    with pytest.raises(ValueError, match="experiment.concepts"):
        verify_experiment_plan(_write(tmp_path, "experiment_plan.yaml", plan))


def test_experiment_plan_figures_track_the_registry(tmp_path) -> None:  # type: ignore[no-untyped-def]
    plan = _load(PLAN_PATH)
    assert plan["expected_figures"] == [f"output/figures/{name}" for _, name in FIGURES]
    plan["expected_figures"] = plan["expected_figures"][:-1]
    with pytest.raises(ValueError, match="expected_figures"):
        verify_experiment_plan(_write(tmp_path, "experiment_plan.yaml", plan))


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        (lambda p: p.__setitem__("rumour_mill", {"note": "unchecked"}), "unverified top-level key"),
        (lambda p: p.__setitem__("experiment", "SOLEX"), "must carry an `experiment` mapping"),
        (lambda p: p["experiment"].__setitem__("codename", "GOLDFINGER"), "experiment.codename"),
        (lambda p: p["experiment"].__setitem__("concepts", "three of them"), "`experiment.concepts` as a list"),
        (lambda p: p["experiment"].__setitem__("concepts", ["solar_concentration"]), "single-key mapping"),
        (lambda p: p.__setitem__("canonical_inputs", [1, 2]), "`canonical_inputs` mapping"),
        (lambda p: p["canonical_inputs"].__setitem__("mirror_count", 5), "uncheckable canonical input"),
        (lambda p: p["canonical_inputs"].__setitem__("receiver_area_m2", 6.0), "receiver_area_m2"),
        (lambda p: p["canonical_inputs"].__setitem__("lair_exit", "Roof"), "lair_exit"),
        (lambda p: p.__setitem__("primary_metrics", []), "non-empty `primary_metrics`"),
        (lambda p: p["primary_metrics"].append("solar.vibes"), "no ledger claim: solar.vibes"),
    ],
)
def test_experiment_plan_rejects_a_stale_declaration(tmp_path, mutate, needle: str) -> None:  # type: ignore[no-untyped-def]
    plan = _load(PLAN_PATH)
    mutate(plan)
    with pytest.raises(ValueError, match=needle):
        verify_experiment_plan(_write(tmp_path, "experiment_plan.yaml", plan))


# ---------------------------------------------------------------------------
# domain_profile.yaml
# ---------------------------------------------------------------------------


def test_src_readme_lists_every_module() -> None:
    """`src/README.md`'s module table is checked against the files on disk.

    Same drift class as the YAML overlays: the table sat at three domain
    modules for three phases after the package had six. Both directions are
    asserted, so a row cannot outlive its file either.
    """
    readme = (PACKAGE_ROOT / "src" / "README.md").read_text(encoding="utf-8")
    package_dir = PACKAGE_ROOT / "src" / PACKAGE_NAME
    on_disk = {path.name for path in package_dir.glob("*.py") if path.name != "__init__.py"}
    documented = set(re.findall(r"^\| `([a-z_]+\.py)` \|", readme, re.MULTILINE))
    assert documented == on_disk


def _coverage_gate() -> int:
    config = yaml.safe_load((PACKAGE_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))
    return int(config["gates"]["coverage_fail_under"])


def test_live_domain_profile_matches_the_code() -> None:
    checked = verify_domain_profile(coverage_gate=_coverage_gate())
    assert "source_policy.modules" in checked
    assert "review_gates.coverage_min_line_branch" in checked
    assert "film" in checked and "protocol.adapter" in checked
    # the coverage gate is optional; omitting it simply checks less
    assert "review_gates.coverage_min_line_branch" not in verify_domain_profile()


def test_domain_profile_lists_every_module_and_artifact() -> None:
    profile = _load(PROFILE_PATH)
    assert profile["source_policy"]["modules"] == list(DOMAIN_MODULES)
    assert profile["artifact_expectations"]["script_artifacts"] == list(expected_script_artifacts())
    assert profile["project"] == PACKAGE_NAME
    assert profile["codename"] == MISSION_CODENAME


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        (lambda p: p.__setitem__("project", "the_spy_who_loved_me"), "project"),
        (lambda p: p.__setitem__("codename", "GOLDFINGER"), "codename"),
        (lambda p: p.__setitem__("source_policy", "real data only"), "`source_policy` mapping"),
        (lambda p: p["source_policy"]["modules"].remove("lair_flows"), "source_policy.modules"),
        (lambda p: p.__setitem__("artifact_expectations", [1]), "`artifact_expectations` mapping"),
        (lambda p: p["artifact_expectations"]["script_artifacts"].pop(), "script_artifacts"),
        (lambda p: p.__setitem__("review_gates", 90), "`review_gates` mapping"),
        (lambda p: p["review_gates"].__setitem__("coverage_min_line_branch", 80), "coverage_min_line_branch"),
        # Round-2 additions: unknown top-level key, film title, protocol adapter.
        (lambda p: p.__setitem__("rumour_mill", {}), "unverified top-level key"),
        (lambda p: p.__setitem__("film", "On Her Majesty's Secret Service"), "film"),
        (lambda p: p.__setitem__("protocol", "nope"), "protocol.adapter"),
        (lambda p: p["protocol"].__setitem__("adapter", "src/the_man_with_the_golden_gun/gone.py"), "does not exist"),
    ],
)
def test_domain_profile_rejects_a_stale_declaration(tmp_path, mutate, needle: str) -> None:  # type: ignore[no-untyped-def]
    profile = _load(PROFILE_PATH)
    mutate(profile)
    with pytest.raises(ValueError, match=needle):
        verify_domain_profile(_write(tmp_path, "domain_profile.yaml", profile), coverage_gate=_coverage_gate())
