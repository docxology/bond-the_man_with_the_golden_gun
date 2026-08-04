"""Tests for the SOLEX duel/bounty appointment-book scheduler (real data, no mocks)."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.duel_scheduler import (
    CANONICAL_DUELS,
    Appointment,
    active_at,
    canonical_bounty_schedule,
    earliest_finish_schedule,
    find_conflicts,
    max_bounty_schedule,
    overlaps,
)


def _appt(aid: str, start: float, end: float, bounty: float = 0.0) -> Appointment:
    return Appointment(id=aid, start=start, end=end, bounty=bounty)


def test_appointment_validation() -> None:
    with pytest.raises(ValueError):
        Appointment(id=" ", start=0.0, end=1.0)  # blank id
    with pytest.raises(ValueError):
        Appointment(id="a", start=2.0, end=1.0)  # end <= start
    with pytest.raises(ValueError):
        Appointment(id="a", start=0.0, end=1.0, bounty=-1.0)  # negative bounty


def test_overlaps_semantics() -> None:
    a = _appt("a", 0.0, 2.0)
    b = _appt("b", 1.0, 3.0)
    c = _appt("c", 2.0, 4.0)  # touches a's end exactly -> no overlap (half-open)
    assert overlaps(a, b)
    assert not overlaps(a, c)


def test_find_conflicts_canonical() -> None:
    conflicts = find_conflicts(CANONICAL_DUELS)
    assert conflicts == ("A|B",)


def test_find_conflicts_empty() -> None:
    assert find_conflicts(()) == ()


def test_max_bounty_canonical() -> None:
    total, selected = max_bounty_schedule(CANONICAL_DUELS)
    assert total == 13.0
    assert selected == ("B", "C", "D")


def test_max_bounty_empty() -> None:
    assert max_bounty_schedule(()) == (0.0, ())


def test_max_bounty_single() -> None:
    total, selected = max_bounty_schedule((_appt("only", 0.0, 1.0, bounty=7.0),))
    assert total == 7.0
    assert selected == ("only",)


def test_max_bounty_tie_prefers_skip_and_reconstructs() -> None:
    # Two equal-bounty overlapping appointments: only one can be taken; the
    # reconstruction must exercise the "skip the later job" branch.
    duels = (
        _appt("A", 0.0, 2.0, bounty=5.0),
        _appt("B", 1.0, 3.0, bounty=5.0),
    )
    total, selected = max_bounty_schedule(duels)
    assert total == 5.0
    assert selected == ("A",)


def test_canonical_bounty_schedule() -> None:
    duels = canonical_bounty_schedule()
    assert duels == CANONICAL_DUELS
    assert len(duels) == 4


def test_earliest_finish_canonical() -> None:
    # earliest finish picks A, then C (start>=2), then D (start>=6)
    assert earliest_finish_schedule(CANONICAL_DUELS) == ("A", "C", "D")


def test_active_at_boundaries() -> None:
    duels = CANONICAL_DUELS
    # t inside A and B
    assert active_at(duels, 1.5) == ("A", "B")
    # t == end of A (2.0) -> A no longer active, B still active
    assert active_at(duels, 2.0) == ("B",)
    # t == start of C (3.0) -> C active
    assert active_at(duels, 3.0) == ("C",)
    assert active_at(duels, 100.0) == ()
