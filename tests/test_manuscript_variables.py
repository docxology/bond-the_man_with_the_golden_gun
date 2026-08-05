"""Tests for SOLEX manuscript variable hydration and the live token gate."""

from __future__ import annotations

import copy
import re
from typing import Any

import pytest
import yaml

from the_man_with_the_golden_gun.manuscript_variables import (
    DEFAULT_TIMESTAMP,
    DOMAIN_MODULES,
    PACKAGE_ROOT,
    generate_variables,
    load_manuscript_config,
    resolve_text,
    unresolved_tokens,
    verify_declared_experiment,
    write_resolved_tree,
)


def test_load_config() -> None:
    config = load_manuscript_config()
    assert config["mission"]["codename"] == "SOLEX"
    assert config["paper"]["version"] == "0.1.0"


def test_load_config_missing(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(FileNotFoundError):
        load_manuscript_config(tmp_path / "nope.yaml")


def test_load_config_non_dict(tmp_path) -> None:  # type: ignore[no-untyped-def]
    bad = tmp_path / "bad.yaml"
    bad.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_manuscript_config(bad)


def test_generate_variables_values() -> None:
    variables = generate_variables()
    assert variables["BOND_CODENAME"] == "SOLEX"
    assert variables["SOLEX_HEAT_KW"] == "191.6325"
    assert variables["SOLEX_CONCENTRATION"] == "50.10"
    assert variables["LAIR_ESCAPE_DISTANCE"] == "4"
    assert variables["LAIR_NUM_BOTTLENECKS"] == "3"
    assert variables["DUEL_TOTAL_BOUNTY"] == "13.0"
    assert variables["DUEL_SELECTED"] == "B, C, D"
    assert variables["DUEL_NUM_CONFLICTS"] == "1"


def test_generate_variables_deepened_values() -> None:
    variables = generate_variables()
    # solar tracking
    assert variables["SOLAR_LATITUDE"] == "8.0"
    assert variables["SOLAR_DAY_OF_YEAR"] == "172"
    assert variables["SOLAR_DECLINATION"] == "23.45"
    assert variables["SOLAR_DAYLIGHT_HOURS"] == "12.47"
    assert variables["SOLAR_NOON_ELEVATION"] == "74.55"
    assert variables["SOLAR_CLEAR_SKY_KWH_M2"] == "7.52"
    assert variables["SOLAR_FIELD_DAILY_KWH"] == "1441.7"
    # lair flows
    assert variables["LAIR_EXT_EDGE_CONNECTIVITY"] == "3"
    assert variables["LAIR_EXT_MIN_CUT_EDGES"] == "3"
    assert variables["LAIR_EXT_CHEAPEST_COST"] == "3"
    assert variables["LAIR_EXT_CHEAPEST_PATH"] == "Entry -> Tunnel -> Armory -> Vault"
    # deadline scheduling
    assert variables["DUEL_DEADLINE_NUM_JOBS"] == "5"
    assert variables["DUEL_DEADLINE_MAX_PROFIT"] == "18.0"
    assert variables["DUEL_DEADLINE_SELECTED"] == "E, C, B"
    assert variables["DUEL_DEADLINE_SLOTS"] == "1:B, 2:C, 3:E"


def test_generate_variables_now_override() -> None:
    variables = generate_variables(now="2020-01-01T00:00:00Z")
    assert variables["GENERATION_TIMESTAMP"] == "2020-01-01T00:00:00Z"
    assert generate_variables()["GENERATION_TIMESTAMP"] == DEFAULT_TIMESTAMP


def test_generate_variables_non_dict_paper(tmp_path) -> None:  # type: ignore[no-untyped-def]
    # A malformed config whose `paper` block is not a mapping must not crash;
    # the generator falls back to defaults.
    cfg = tmp_path / "config.yaml"
    cfg.write_text("paper: [1, 2]\nmission: {codename: SOLEX}\n", encoding="utf-8")
    variables = generate_variables(config_path=cfg)
    assert variables["BOND_TITLE"] == "The Man with the Golden Gun: SOLEX"


def test_generate_variables_non_dict_mission_and_gates(tmp_path) -> None:  # type: ignore[no-untyped-def]
    # Malformed `mission` / `gates` blocks fall back to documented defaults
    # rather than raising: a broken config should still render something
    # obviously wrong (seed 0) instead of half a manuscript.
    cfg = tmp_path / "config.yaml"
    cfg.write_text("mission: [1, 2]\ngates: 'nope'\n", encoding="utf-8")
    variables = generate_variables(config_path=cfg)
    assert variables["MISSION_SEED"] == "0"
    assert variables["COVERAGE_GATE_PCT"] == "90"


def test_generate_variables_non_dict_site_fallback(tmp_path) -> None:  # type: ignore[no-untyped-def]
    # Malformed experiment / solar_tracking blocks fall back to site constants.
    cfg = tmp_path / "config.yaml"
    cfg.write_text("experiment: {solar_tracking: [1, 2]}\n", encoding="utf-8")
    variables = generate_variables(config_path=cfg)
    assert variables["SOLAR_LATITUDE"] == "8.0"
    assert variables["SOLAR_DAY_OF_YEAR"] == "172"
    # experiment block itself not a mapping -> same fallback
    cfg.write_text("experiment: [1, 2]\n", encoding="utf-8")
    variables = generate_variables(config_path=cfg)
    assert variables["SOLAR_LATITUDE"] == "8.0"


def test_resolve_text() -> None:
    variables = {"HEAT": "191.6"}
    assert resolve_text("out: {{HEAT}} kW", variables) == "out: 191.6 kW"
    # unresolvable tokens are left verbatim
    assert resolve_text("{{MISSING}}", variables) == "{{MISSING}}"


def test_unresolved_tokens() -> None:
    assert unresolved_tokens("a {{A}} b {{B}}") == ["{{A}}", "{{B}}"]
    assert unresolved_tokens("no tokens") == []


def test_write_resolved_tree(tmp_path) -> None:  # type: ignore[no-untyped-def]
    source = tmp_path / "src"
    source.mkdir()
    (source / "03_results.md").write_text("heat = {{SOLEX_HEAT_KW}} kW", encoding="utf-8")
    out = tmp_path / "out"
    variables = generate_variables()
    written = write_resolved_tree(variables, source_dir=source, out_dir=out)
    assert len(written) == 1
    assert (out / "03_results.md").read_text(encoding="utf-8") == "heat = 191.6325 kW"


_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def test_all_manuscript_tokens_are_generated() -> None:
    """Live cross-reference gate: every {{TOKEN}} in prose sections resolves."""
    variables = generate_variables()
    sections = sorted((PACKAGE_ROOT / "manuscript").glob("[0-9]*.md"))
    assert sections, "no numbered manuscript sections found — the gate would be vacuous"
    for section in sections:
        for token in _TOKEN_RE.findall(section.read_text(encoding="utf-8")):
            key = token[2:-2]
            assert key in variables, f"{section.name}: {token} not generated"


def test_canonical_section_set_is_present() -> None:
    """The dossier carries every canonical section, not just the ones with tokens."""
    manuscript = PACKAGE_ROOT / "manuscript"
    required = {
        "00_abstract.md",
        "01_introduction.md",
        "02_methodology.md",
        "03_results.md",
        "04_conclusion.md",
        "05_experimental_setup.md",
        "06_reproducibility.md",
        "07_scope_and_related_work.md",
        "99_references.md",
        "preamble.md",
        "config.yaml",
        "references.bib",
        "README.md",
        "AGENTS.md",
        "SYNTAX.md",
    }
    missing = sorted(name for name in required if not (manuscript / name).is_file())
    assert not missing, f"missing canonical manuscript files: {missing}"


def test_derived_surface_tokens() -> None:
    """Tokens describing the package's own shape are derived, not hand-set."""
    variables = generate_variables()
    assert variables["NUM_DOMAIN_MODULES"] == str(len(DOMAIN_MODULES))
    assert variables["DOMAIN_MODULE_LIST"].split(", ") == [f"{m}.py" for m in DOMAIN_MODULES]
    assert variables["NUM_FIGURES"] == "4"
    assert variables["COVERAGE_GATE_PCT"] == "90"
    assert variables["PACKAGE_VERSION"] == "0.1.0"
    assert variables["MISSION_SEED"] == "3"
    # every declared domain module really exists on disk
    for module in DOMAIN_MODULES:
        assert (PACKAGE_ROOT / "src" / "the_man_with_the_golden_gun" / f"{module}.py").is_file()


def test_scheduler_comparison_tokens() -> None:
    """The two duel objectives really do disagree on the canonical book."""
    variables = generate_variables()
    assert variables["DUEL_SELECTED"] == "B, C, D"
    assert variables["DUEL_EARLIEST_FINISH"] == "A, C, D"
    assert variables["DUEL_NUM_SELECTED"] == variables["DUEL_NUM_EARLIEST_FINISH"] == "3"
    assert variables["DUEL_TOTAL_BOUNTY"] == "13.0"
    assert variables["DUEL_EARLIEST_FINISH_BOUNTY"] == "11.0"
    # greedy mirror-budget allocation under a budget smaller than the field
    assert variables["SOLEX_BUDGET_M2"] == "200"
    assert variables["SOLEX_BUDGET_SELECTION"] == "alpha, bravo, echo"
    assert variables["SOLEX_NUM_MIRRORS"] == "5"
    assert variables["LAIR_EXT_MIN_CUT_WALLS"] == "Courtyard-Entry, Entry-Hall, Entry-Tunnel"


def test_fixture_table_tokens_are_generated_from_the_constants() -> None:
    """Setup-section tables are rendered from the live fixtures, not transcribed."""
    from the_man_with_the_golden_gun.deadline_scheduler import SOLEX_DEADLINE_JOBS
    from the_man_with_the_golden_gun.duel_scheduler import CANONICAL_DUELS
    from the_man_with_the_golden_gun.solar_concentration import SOLEX_FIELD

    variables = generate_variables()

    mirror_rows = variables["SOLEX_MIRROR_ROWS"].splitlines()
    assert len(mirror_rows) == len(SOLEX_FIELD)
    for row, mirror in zip(mirror_rows, SOLEX_FIELD):
        assert row.startswith(f"| `{mirror.id}` |")
        assert f"{mirror.area_m2:.1f}" in row
        assert f"{mirror.reflectivity:.2f}" in row

    duel_rows = variables["DUEL_BOOK_ROWS"].splitlines()
    assert len(duel_rows) == len(CANONICAL_DUELS)
    assert duel_rows[0] == "| `A` | [0, 2) | 3 | First_Heel |"

    deadline_rows = variables["DUEL_DEADLINE_BOOK_ROWS"].splitlines()
    assert len(deadline_rows) == len(SOLEX_DEADLINE_JOBS)
    assert deadline_rows[0] == "| `A` | 1 | 3 |"
    # slots available = the latest deadline in the book
    assert variables["DUEL_DEADLINE_NUM_SLOTS"] == str(max(j.deadline for j in SOLEX_DEADLINE_JOBS))
    # the book must over-subscribe its slots or the greedy never rejects anything
    assert int(variables["DUEL_DEADLINE_NUM_JOBS"]) > int(variables["DUEL_DEADLINE_NUM_SLOTS"])


def _live_config() -> dict[str, Any]:
    return copy.deepcopy(load_manuscript_config())


def test_declared_experiment_verifies_the_live_config() -> None:
    """The shipped config declares — and the models confirm — every checked key."""
    checked = verify_declared_experiment(_live_config())
    assert set(checked) == {
        "receiver_area_m2",
        "lair_entry",
        "lair_exit",
        "duel_max_bounty",
        "extended_lair.edge_disjoint_routes",
        "deadline_jobs",
    }


def test_declared_experiment_absent_block_checks_nothing() -> None:
    assert verify_declared_experiment({}) == ()
    assert verify_declared_experiment({"experiment": [1, 2]}) == ()
    assert verify_declared_experiment({"experiment": {}}) == ()
    # a non-mapping extended_lair / non-list deadline_jobs is simply not checked
    assert verify_declared_experiment({"experiment": {"extended_lair": "nope", "deadline_jobs": 7}}) == ()


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        (lambda e: e.__setitem__("receiver_area_m2", 6.0), "receiver_area_m2"),
        (lambda e: e.__setitem__("lair_entry", "Foyer"), "lair_entry"),
        (lambda e: e.__setitem__("lair_exit", "Roof"), "lair_exit"),
        (lambda e: e.__setitem__("duel_max_bounty", 99.0), "duel_max_bounty"),
        (lambda e: e["extended_lair"].__setitem__("edge_disjoint_routes", 2), "edge_disjoint_routes"),
        (lambda e: e["deadline_jobs"][0].__setitem__("profit", 42.0), "deadline_jobs"),
        (lambda e: e["deadline_jobs"].pop(), "deadline_jobs"),
    ],
)
def test_declared_experiment_rejects_a_stale_config(mutate, needle: str) -> None:  # type: ignore[no-untyped-def]
    """Positive control for the config gate: every declaration can actually fail.

    A cross-check that cannot fail is decoration. Each case tampers with one
    declared value and asserts the mismatch is raised and named.
    """
    config = _live_config()
    mutate(config["experiment"])
    with pytest.raises(ValueError, match=needle):
        verify_declared_experiment(config)


def test_generate_variables_rejects_a_stale_config(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The gate is wired into the real entry point, not just callable in isolation."""
    config = _live_config()
    config["experiment"]["duel_max_bounty"] = 1.0
    stale = tmp_path / "config.yaml"
    stale.write_text(yaml.safe_dump(config), encoding="utf-8")
    with pytest.raises(ValueError, match="duel_max_bounty"):
        generate_variables(config_path=stale)
