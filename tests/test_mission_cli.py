"""Tests for the SOLEX mission CLI phase runner (exits + printed output)."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.mission_cli import PHASES, run_phase


@pytest.mark.parametrize("phase", PHASES)
def test_phase_exit_zero(phase: str, capsys) -> None:  # type: ignore[no-untyped-def]
    code = run_phase(phase)
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip()  # each phase prints deterministic JSON


def test_all_phase(capsys) -> None:  # type: ignore[no-untyped-def]
    assert run_phase("all") == 0
    captured = capsys.readouterr()
    for label in PHASES:
        assert f"== {label} ==" in captured.out


def test_unknown_phase(capsys) -> None:  # type: ignore[no-untyped-def]
    assert run_phase("bogus") == 2
    captured = capsys.readouterr()
    assert "unknown phase" in captured.err
