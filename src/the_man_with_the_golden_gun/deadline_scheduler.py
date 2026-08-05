"""Deadline-based bounty scheduling for the SOLEX mission.

The duel book is not only an interval problem: the agency also receives
*unit-time bounty contracts* — each contract takes one time slot to complete
and must be finished by its deadline, and the agent wants to maximise the
total bounty of the contracts it accepts.

This is the classic *scheduling to maximise profit with deadlines* problem
(Kleinberg & Tardos 2006, ch. 4; Cormen et al. 2009, ch. 16). The greedy
solution is exact: process jobs in descending profit and assign each to the
latest free slot at or before its deadline; the disjoint-set (union–find)
structure makes the "latest free slot" query near-constant time with path
compression.

Everything is deterministic — ties are broken by job id, and the assignment
is fully specified by the sorted order.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "SOLEX_DEADLINE_JOBS",
    "DeadlineJob",
    "assign_slots",
    "canonical_deadline_book",
    "max_profit_with_deadlines",
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class DeadlineJob:
    """A unit-time bounty contract: must finish by ``deadline``, worth ``profit``.

    ``deadline`` is a positive integer time slot; ``profit`` is non-negative.
    """

    id: str
    deadline: int
    profit: float

    def __post_init__(self) -> None:
        _require(bool(self.id.strip()), "DeadlineJob.id must be a non-empty string")
        _require(isinstance(self.deadline, int) and self.deadline >= 1, "DeadlineJob.deadline must be an int >= 1")
        _require(self.profit >= 0.0, "DeadlineJob.profit must be non-negative")


#: Canonical SOLEX deadline book (five contracts, max profit 18).
SOLEX_DEADLINE_JOBS: tuple[DeadlineJob, ...] = (
    DeadlineJob(id="A", deadline=1, profit=3.0),
    DeadlineJob(id="B", deadline=2, profit=5.0),
    DeadlineJob(id="C", deadline=2, profit=6.0),
    DeadlineJob(id="D", deadline=3, profit=2.0),
    DeadlineJob(id="E", deadline=3, profit=7.0),
)


def canonical_deadline_book() -> tuple[DeadlineJob, ...]:
    """The canonical SOLEX deadline book (avoids dataclass-name collisions)."""
    return SOLEX_DEADLINE_JOBS


class _SlotUnionFind:
    """Disjoint-set structure over time slots: ``find`` = latest free slot.

    ``find(x)`` returns the latest slot ≤ x that is still free, merging
    occupied slots onto their left neighbour so future queries skip them.
    """

    def __init__(self, size: int) -> None:
        self._parent = list(range(size + 1))

    def find(self, x: int) -> int:
        if x <= 0:
            return 0
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def occupy(self, slot: int) -> None:
        self._parent[slot] = self.find(slot - 1)


def _greedy_assignment(jobs: tuple[DeadlineJob, ...]) -> list[tuple[int, DeadlineJob]]:
    """Run the deadline greedy once; return accepted ``(slot, job)`` pairs.

    Jobs are processed in descending profit (ties: ascending id) and each
    accepted job takes the latest still-free slot at or before its deadline.
    Both :func:`max_profit_with_deadlines` and :func:`assign_slots` are views
    over this single computation, so the reported profit and the reported slot
    assignment can never disagree.
    """
    if not jobs:
        return []
    ordered = sorted(jobs, key=lambda job: (-job.profit, job.id))
    union = _SlotUnionFind(max(job.deadline for job in ordered))
    accepted: list[tuple[int, DeadlineJob]] = []
    for job in ordered:
        slot = union.find(job.deadline)
        if slot > 0:
            union.occupy(slot)
            accepted.append((slot, job))
    return accepted


def max_profit_with_deadlines(jobs: tuple[DeadlineJob, ...]) -> tuple[float, tuple[str, ...]]:
    """Maximum total profit schedule for unit-time jobs with deadlines.

    Returns ``(total_profit, selected_ids)`` — the exact greedy solution:
    jobs in descending profit (ties: ascending id), each assigned to the
    latest free slot ≤ its deadline. Ids are returned in acceptance order
    (descending profit), which is deterministic.
    """
    accepted = _greedy_assignment(jobs)
    return float(sum(job.profit for _, job in accepted)), tuple(job.id for _, job in accepted)


def assign_slots(jobs: tuple[DeadlineJob, ...]) -> tuple[tuple[int, str], ...]:
    """Slot assignment ``(slot, job_id)`` for the max-profit schedule.

    Only accepted jobs appear; slots are 1-indexed time slots, sorted.
    """
    return tuple(sorted((slot, job.id) for slot, job in _greedy_assignment(jobs)))
