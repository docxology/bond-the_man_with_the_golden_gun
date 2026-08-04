"""Assassin duel / bounty scheduling for the SOLEX mission.

The agent keeps an appointment book of bounty contracts — duels with a target
at a fixed interval of time that carries a bounty. This module solves the
scheduling problems deterministically with classic, exact algorithms:

* :func:`find_conflicts` — all overlapping pairs of appointments;
* :func:`max_bounty_schedule` — *weighted interval scheduling* (dynamic
  programming) choosing a non-overlapping subset that maximises total bounty;
* :func:`earliest_finish_schedule` — the greedy count-maximising selection
  (the "book as many contracts as possible" rule);
* :func:`active_at` — which appointments are live at a given time (the "paced
  at noon" check).

Appointments are half-open intervals ``[start, end)``; two overlap iff
``a.start < b.end and b.start < a.end``. Everything is deterministic — tie
breaks are fixed by appointment id and interval bounds.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Appointment",
    "active_at",
    "earliest_finish_schedule",
    "find_conflicts",
    "max_bounty_schedule",
    "overlaps",
    "CANONICAL_DUELS",
    "canonical_bounty_schedule",
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Appointment:
    """A bounty contract occupying the half-open interval ``[start, end)``."""

    id: str
    start: float
    end: float
    bounty: float = 0.0
    target: str = ""

    def __post_init__(self) -> None:
        _require(bool(self.id.strip()), "Appointment.id must be a non-empty string")
        _require(self.end > self.start, f"Appointment {self.id!r}: end must be after start")
        _require(self.bounty >= 0.0, f"Appointment {self.id!r}: bounty must be non-negative")


#: Canonical set of SOLEX bounty contracts (duels) for deterministic scheduling.
CANONICAL_DUELS: tuple[Appointment, ...] = (
    Appointment(id="A", start=0.0, end=2.0, bounty=3.0, target="First_Heel"),
    Appointment(id="B", start=1.0, end=3.0, bounty=5.0, target="Second_Heel"),
    Appointment(id="C", start=3.0, end=6.0, bounty=6.0, target="Solex_Guard"),
    Appointment(id="D", start=6.0, end=8.0, bounty=2.0, target="Night_Watch"),
)


def canonical_bounty_schedule() -> tuple[Appointment, ...]:
    """The canonical SOLEX appointment book (avoids dataclass-name collisions)."""
    return CANONICAL_DUELS


def overlaps(a: Appointment, b: Appointment) -> bool:
    """True when two half-open duel intervals overlap in time."""
    return a.start < b.end and b.start < a.end


def find_conflicts(appointments: tuple[Appointment, ...]) -> tuple[str, ...]:
    """Every overlapping pair of appointments as ``"<a.id><b.id>"`` pairs.

    Deterministic: each unordered pair appears once, sorted by appointment id.
    """
    conflicts: list[tuple[str, str]] = []
    ordered = sorted(appointments, key=lambda a: a.id)
    for i, first in enumerate(ordered):
        for second in ordered[i + 1 :]:
            if overlaps(first, second):
                conflicts.append((first.id, second.id))
    return tuple(f"{a}|{b}" for a, b in conflicts)


def _previous_index(sorted_by_end: list[Appointment]) -> list[int]:
    """For each job, the index of the last job ending no later than its start."""
    ends = [job.end for job in sorted_by_end]
    previous: list[int] = []
    for job in sorted_by_end:
        # binary search: rightmost end <= job.start
        lo, hi = 0, len(ends)
        while lo < hi:
            mid = (lo + hi) // 2
            if ends[mid] <= job.start:
                lo = mid + 1
            else:
                hi = mid
        previous.append(lo - 1)
    return previous


def max_bounty_schedule(appointments: tuple[Appointment, ...]) -> tuple[float, tuple[str, ...]]:
    """Weighted interval scheduling: non-overlapping subset of maximum bounty.

    Returns ``(total_bounty, selected_ids)``. Exact dynamic-programming
    solution, deterministic via stable ordering by ``(end, id)``.
    """
    if not appointments:
        return 0.0, ()
    ordered = sorted(appointments, key=lambda a: (a.end, a.id))
    previous = _previous_index(ordered)
    dp: list[float] = [0.0] * len(ordered)
    for j, job in enumerate(ordered):
        include = job.bounty + (dp[previous[j]] if previous[j] >= 0 else 0.0)
        dp[j] = max(include, dp[j - 1] if j > 0 else 0.0)
    # reconstruct
    selected: list[str] = []
    j = len(ordered) - 1
    while j >= 0:
        include = ordered[j].bounty + (dp[previous[j]] if previous[j] >= 0 else 0.0)
        if include > (dp[j - 1] if j > 0 else 0.0):
            selected.append(ordered[j].id)
            j = previous[j]
        else:
            j -= 1
    # emit in the stable (end, id) order of the source scan
    return dp[-1], tuple(reversed(selected))


def earliest_finish_schedule(appointments: tuple[Appointment, ...]) -> tuple[str, ...]:
    """Greedy count-maximising schedule (take the earliest-finishing duel)."""
    ordered = sorted(appointments, key=lambda a: (a.end, a.start, a.id))
    selected: list[str] = []
    last_end = float("-inf")
    for job in ordered:
        if job.start >= last_end:
            selected.append(job.id)
            last_end = job.end
    return tuple(selected)


def active_at(appointments: tuple[Appointment, ...], t: float) -> tuple[str, ...]:
    """Appointment ids live at time ``t`` (``start <= t < end``), sorted by id."""
    return tuple(sorted(a.id for a in appointments if a.start <= t < a.end))
