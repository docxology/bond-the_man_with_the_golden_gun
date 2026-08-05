"""Tests for SOLEX deterministic figure generation (real rendering, no mocks)."""

from __future__ import annotations

import re
from pathlib import Path

from the_man_with_the_golden_gun.figures import (
    FIGURES,
    figure_labels,
    generate_all_figures,
    plot_daily_solar_profile,
    plot_duel_schedule,
    plot_lair_topology,
    plot_solex_yield,
)
from the_man_with_the_golden_gun.manuscript_variables import PACKAGE_ROOT

#: `![alt](path){#fig:label}` figure declarations in a manuscript section.
_DECLARED_RE = re.compile(r"\]\((?P<path>[^)]+)\)\{#fig:(?P<label>[A-Za-z0-9_]+)\}")
#: `[@fig:label]` crossref citations in prose.
_CITED_RE = re.compile(r"\[@fig:(?P<label>[A-Za-z0-9_]+)\]")


def _manuscript_sections() -> list[Path]:
    sections = sorted((PACKAGE_ROOT / "manuscript").glob("[0-9]*.md"))
    assert sections, "no numbered manuscript sections found — the scan set is empty"
    return sections


def _assert_png(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.suffix == ".png"


def test_generate_all_figures(tmp_path) -> None:  # type: ignore[no-untyped-def]
    solar, daily, lair, duel = generate_all_figures(tmp_path)
    _assert_png(solar)
    _assert_png(daily)
    _assert_png(lair)
    _assert_png(duel)
    assert solar.name == "solex_yield.png"
    assert daily.name == "solex_daily.png"
    assert lair.name == "lair_topology.png"
    assert duel.name == "duel_schedule.png"


def test_individual_plot_functions(tmp_path) -> None:  # type: ignore[no-untyped-def]
    out = tmp_path / "nested" / "fig"
    _assert_png(plot_solex_yield(out / "a.png"))
    _assert_png(plot_daily_solar_profile(out / "b.png"))
    _assert_png(plot_lair_topology(out / "c.png"))
    _assert_png(plot_duel_schedule(out / "d.png"))


def test_registry_matches_generated_filenames(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """`generate_all_figures` writes exactly the files `FIGURES` declares."""
    written = generate_all_figures(tmp_path)
    assert [path.name for path in written] == [filename for _, filename in FIGURES]
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(f for _, f in FIGURES)


def test_figures_are_byte_identical_across_runs(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Determinism proof for the reproducibility claim: same bytes, twice.

    The manuscript states that regenerating the figures produces byte-identical
    PNGs. That claim is only worth making if something checks it, so this
    renders every figure into two separate directories and compares the raw
    bytes rather than merely asserting the files exist.
    """
    first = generate_all_figures(tmp_path / "run_a")
    second = generate_all_figures(tmp_path / "run_b")
    assert len(first) == len(second) == len(FIGURES)
    for left, right in zip(first, second):
        assert left.name == right.name
        assert left.read_bytes() == right.read_bytes(), f"{left.name} is not byte-reproducible"


def test_every_manuscript_figure_label_is_registered() -> None:
    """No section may declare or cite a figure the code does not produce."""
    registered = set(figure_labels())
    for section in _manuscript_sections():
        text = section.read_text(encoding="utf-8")
        for match in _DECLARED_RE.finditer(text):
            label = match.group("label")
            assert label in registered, f"{section.name}: {label} is not in the FIGURES registry"
            expected = dict(FIGURES)[label]
            assert match.group("path").endswith(expected), (
                f"{section.name}: {label} points at {match.group('path')!r}, expected .../{expected}"
            )
        for match in _CITED_RE.finditer(text):
            assert match.group("label") in registered, f"{section.name}: cited unknown figure {match.group('label')}"


def test_every_registered_figure_is_used_by_the_manuscript() -> None:
    """The reverse direction: a rendered figure nobody references is dead weight."""
    declared: set[str] = set()
    for section in _manuscript_sections():
        declared.update(m.group("label") for m in _DECLARED_RE.finditer(section.read_text(encoding="utf-8")))
    assert declared == set(figure_labels())
