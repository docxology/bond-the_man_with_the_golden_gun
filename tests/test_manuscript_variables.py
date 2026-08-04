"""Tests for SOLEX manuscript variable hydration and the live token gate."""

from __future__ import annotations

import re

import pytest

from the_man_with_the_golden_gun.manuscript_variables import (
    DEFAULT_TIMESTAMP,
    PACKAGE_ROOT,
    generate_variables,
    load_manuscript_config,
    resolve_text,
    unresolved_tokens,
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
    for section in sorted((PACKAGE_ROOT / "manuscript").glob("[0-9]*.md")):
        for token in _TOKEN_RE.findall(section.read_text(encoding="utf-8")):
            key = token[2:-2]
            assert key in variables, f"{section.name}: {token} not generated"
