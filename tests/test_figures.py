"""Tests for SOLEX deterministic figure generation (real rendering, no mocks)."""

from __future__ import annotations

from pathlib import Path

from the_man_with_the_golden_gun.figures import (
    generate_all_figures,
    plot_duel_schedule,
    plot_lair_topology,
    plot_solex_yield,
)


def _assert_png(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.suffix == ".png"


def test_generate_all_figures(tmp_path) -> None:  # type: ignore[no-untyped-def]
    solar, lair, duel = generate_all_figures(tmp_path)
    _assert_png(solar)
    _assert_png(lair)
    _assert_png(duel)
    assert solar.name == "solex_yield.png"
    assert lair.name == "lair_topology.png"
    assert duel.name == "duel_schedule.png"


def test_individual_plot_functions(tmp_path) -> None:  # type: ignore[no-untyped-def]
    out = tmp_path / "nested" / "fig"
    _assert_png(plot_solex_yield(out / "a.png"))
    _assert_png(plot_lair_topology(out / "b.png"))
    _assert_png(plot_duel_schedule(out / "c.png"))
