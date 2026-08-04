"""Tests for the SOLEX deadline-based bounty scheduler (greedy + union-find)."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.deadline_scheduler import (
    SOLEX_DEADLINE_JOBS,
    DeadlineJob,
    assign_slots,
    canonical_deadline_book,
    max_profit_with_deadlines,
)


def _job(jid: str, deadline: int, profit: float = 0.0) -> DeadlineJob:
    return DeadlineJob(id=jid, deadline=deadline, profit=profit)


def test_deadline_job_validation() -> None:
    with pytest.raises(ValueError):
        DeadlineJob(id=" ", deadline=1, profit=1.0)  # blank id
    with pytest.raises(ValueError):
        DeadlineJob(id="a", deadline=0, profit=1.0)  # deadline < 1
    with pytest.raises(ValueError):
        DeadlineJob(id="a", deadline=1, profit=-1.0)  # negative profit


def test_canonical_max_profit() -> None:
    total, selected = max_profit_with_deadlines(SOLEX_DEADLINE_JOBS)
    assert total == 18.0
    assert selected == ("E", "C", "B")


def test_canonical_slots() -> None:
    slots = assign_slots(SOLEX_DEADLINE_JOBS)
    assert slots == ((1, "B"), (2, "C"), (3, "E"))


def test_empty_book() -> None:
    assert max_profit_with_deadlines(()) == (0.0, ())
    assert assign_slots(()) == ()


def test_single_job() -> None:
    assert max_profit_with_deadlines((_job("only", 1, profit=7.0),)) == (7.0, ("only",))
    assert assign_slots((_job("only", 1, profit=7.0),)) == ((1, "only"),)


def test_tie_break_by_id() -> None:
    # equal profit, one slot: the earlier id wins deterministically
    jobs = (_job("A", 1, profit=5.0), _job("B", 1, profit=5.0))
    total, selected = max_profit_with_deadlines(jobs)
    assert total == 5.0
    assert selected == ("A",)


def test_all_feasible_distinct_deadlines() -> None:
    jobs = (_job("a", 1, profit=1.0), _job("b", 2, profit=2.0), _job("c", 3, profit=3.0))
    total, selected = max_profit_with_deadlines(jobs)
    assert total == 6.0
    assert set(selected) == {"a", "b", "c"}


def test_deadline_beyond_max_slot_uses_latest() -> None:
    # a job with a deadline beyond every other job still gets its own slot
    jobs = (_job("x", 9, profit=1.0), _job("y", 1, profit=10.0))
    total, selected = max_profit_with_deadlines(jobs)
    assert total == 11.0
    assert selected == ("y", "x")
    assert assign_slots(jobs) == ((1, "y"), (9, "x"))


def test_canonical_deadline_book() -> None:
    assert canonical_deadline_book() == SOLEX_DEADLINE_JOBS
    assert len(SOLEX_DEADLINE_JOBS) == 5
