"""Funhouse lair escape-topology solver for the SOLEX mission.

The villain's lair is a funhouse maze of rooms connected by mirror-walled
passages. This module treats the lair as an undirected graph — rooms are
nodes, mirror passages are edges — and answers the agent's tactical questions
deterministically:

* :func:`find_escape_path` — a shortest escape route from an entry room to an
  exit room (breadth-first search);
* :func:`reachable_rooms` — the rooms reachable from a given room;
* :func:`articulation_points` — Tarjan's cut-vertex algorithm, the rooms whose
  single removal disconnects a part of the funhouse;
* :func:`mirror_gated_bottlenecks` — the rooms (other than entry/exit) that
  every escape route must pass through: the rooms guarding the way out.

Pure stdlib (``collections``), no external graph library, deterministic output.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

__all__ = [
    "adjacency",
    "articulation_points",
    "build_lair_graph",
    "escape_distance",
    "find_escape_path",
    "mirror_gated_bottlenecks",
    "reachable_rooms",
    "CANONICAL_EXIT",
    "CANONICAL_ENTRY",
    "canonical_lair",
]

#: Room names for the canonical SOLEX funhouse lair.
CANONICAL_ENTRY = "Entrance"
CANONICAL_EXIT = "Vault"

Adjacency = dict[str, set[str]]


def build_lair_graph(rooms: Iterable[str], passages: Iterable[tuple[str, str]]) -> Adjacency:
    """Build an undirected adjacency map from room labels and mirror passages.

    Args:
        rooms: Iterable of room names (nodes).
        passages: Iterable of ``(a, b)`` mirror passages (edges).

    Raises:
        ValueError: if any passage references an undeclared room.
    """
    graph: Adjacency = {room: set() for room in rooms}
    known = set(graph)
    for left, right in passages:
        if left not in known or right not in known:
            raise ValueError(f"passage references an undeclared room: {left!r}-{right!r}")
        graph[left].add(right)
        graph[right].add(left)
    return graph


def adjacency() -> Adjacency:
    """Canonical SOLEX lair graph (independent rooms fixture for tests)."""
    return build_lair_graph(
        [
            "Entrance",
            "Hall",
            "Mirror_Room",
            "Gallery",
            "Vault",
            "Side_Passage",
            "Garden",
        ],
        [
            ("Entrance", "Hall"),
            ("Hall", "Mirror_Room"),
            ("Mirror_Room", "Gallery"),
            ("Gallery", "Vault"),
            ("Hall", "Side_Passage"),
            ("Side_Passage", "Garden"),
        ],
    )


def canonical_lair() -> tuple[Adjacency, str, str]:
    """Return ``(graph, entry, exit)`` for the canonical SOLEX funhouse lair."""
    return adjacency(), CANONICAL_ENTRY, CANONICAL_EXIT


def _require_node(graph: Adjacency, room: str, label: str) -> None:
    if room not in graph:
        raise ValueError(f"{label} room {room!r} is not part of the lair")


def find_escape_path(graph: Adjacency, start: str, exit_: str) -> tuple[str, ...] | None:
    """Shortest escape route (room sequence) from ``start`` to ``exit_``.

    Uses breadth-first search for shortest path in unweighted rooms. Returns
    ``None`` when no route exists (the mirror maze is disconnecting).
    """
    _require_node(graph, start, "start")
    _require_node(graph, exit_, "exit")
    if start == exit_:
        return (start,)
    prev: dict[str, str | None] = {start: None}
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in sorted(graph[node]):
            if neighbour in prev:
                continue
            prev[neighbour] = node
            if neighbour == exit_:
                path: list[str] = []
                cur: str | None = neighbour
                while cur is not None:
                    path.append(cur)
                    cur = prev[cur]
                return tuple(reversed(path))
            queue.append(neighbour)
    return None


def escape_distance(graph: Adjacency, start: str, exit_: str) -> int | None:
    """Number of passages in the shortest escape route (``None`` if blocked)."""
    path = find_escape_path(graph, start, exit_)
    return None if path is None else len(path) - 1


def reachable_rooms(graph: Adjacency, start: str) -> frozenset[str]:
    """All rooms reachable from ``start`` via mirror passages (BFS)."""
    _require_node(graph, start, "start")
    seen: set[str] = set()
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(graph[node])
    return frozenset(seen)


def articulation_points(graph: Adjacency) -> frozenset[str]:
    """Rooms whose removal disconnects the funhouse (Tarjan cut vertices)."""
    disc: dict[str, int] = {}
    low: dict[str, int] = {}
    parents: dict[str, str | None] = {}
    children: dict[str, int] = {}
    is_art: set[str] = set()
    time = 0

    def _dfs(node: str) -> None:
        nonlocal time
        disc[node] = low[node] = time
        time += 1
        children[node] = 0
        for neighbour in sorted(graph[node]):
            if neighbour not in disc:
                children[node] += 1
                parents[neighbour] = node
                _dfs(neighbour)
                low[node] = min(low[node], low[neighbour])
                if parents[node] is None and children[node] > 1:
                    is_art.add(node)
                if parents[node] is not None and low[neighbour] >= disc[node]:
                    is_art.add(node)
            elif neighbour != parents[node]:
                low[node] = min(low[node], disc[neighbour])

    for room in sorted(graph):
        if room not in disc:
            parents[room] = None
            _dfs(room)
    return frozenset(is_art)


def mirror_gated_bottlenecks(graph: Adjacency, entry: str, exit_: str) -> tuple[str, ...]:
    """Rooms every escape route from ``entry`` to ``exit_`` must pass through.

    Computed honestly: a room is a bottleneck if removing it disconnects the
    entry from the exit (verified by reachability after each removal), which
    is exact for small lairs. Sorted for deterministic reporting.

    When the entry cannot already reach the exit — a lair with no escape route
    at all — the set of bottlenecks is empty: the vacuous case must not
    degenerate into reporting every room as critical, which is what the raw
    removal test would produce.
    """
    _require_node(graph, entry, "entry")
    _require_node(graph, exit_, "exit")
    if entry == exit_:
        return ()
    if exit_ not in reachable_rooms(graph, entry):
        return ()
    bottlenecks: list[str] = []
    for room in sorted(graph):
        if room in (entry, exit_):
            continue
        reduced = {node: (neighbours - {room}) for node, neighbours in graph.items() if node != room}
        reduced = {node: {n for n in neighbours if n in reduced} for node, neighbours in reduced.items()}
        # entry and exit are never removed (they are skipped above), so the
        # only failure mode is the exit becoming unreachable from the entry.
        reachable = reachable_rooms(reduced, entry)
        if exit_ not in reachable:
            bottlenecks.append(room)
    return tuple(bottlenecks)
