"""Lair flow and cost analysis for the SOLEX mission.

The funhouse lair is an undirected graph of rooms and mirror passages; this
module adds the *flow* layer of the escape-topology model:

* :func:`edmonds_karp` — maximum flow from entry to exit on the lair's
  mirror-passage network (each passage a unit-capacity arc in both
  directions), the standard augmenting-path algorithm (Cormen et al. 2009);
* :func:`edge_connectivity` / :func:`min_cut_edges` — the number of
  edge-disjoint escape routes and the minimum set of mirror walls whose
  destruction seals the lair (the min s–t cut, recovered from the residual
  graph);
* :func:`edge_disjoint_escape_routes` — flow decomposition into the actual
  edge-disjoint routes;
* :func:`cost_aware_escape` — Dijkstra's shortest-cost escape when mirror
  passages carry a traversal cost (mirror fragility / guard density).

The extended lair fixture (:func:`build_extended_lair`) is a larger funhouse
with three edge-disjoint escape routes, giving the flow layer real numbers to
bite on. Everything is deterministic — sorted neighbour iteration, no random
draws.
"""

from __future__ import annotations

import heapq
from collections import deque

from .lair_topology import Adjacency, build_lair_graph

__all__ = [
    "EXTENDED_EXIT",
    "EXTENDED_ENTRY",
    "build_extended_lair",
    "cost_aware_escape",
    "edge_connectivity",
    "edge_disjoint_escape_routes",
    "edmonds_karp",
    "min_cut_edges",
    "unit_traversal_costs",
]

#: Entry/exit room names for the extended SOLEX funhouse lair.
EXTENDED_ENTRY = "Entry"
EXTENDED_EXIT = "Vault"

#: A directed capacity network: node -> neighbour -> capacity.
Network = dict[str, dict[str, float]]


def build_extended_lair() -> tuple[Adjacency, str, str]:
    """Build the extended funhouse lair: 10 rooms, three disjoint escape routes.

    Edge-disjoint routes Entry→Vault:

    * Entry–Hall–MR1–Gallery–Vault
    * Entry–Tunnel–Armory–Vault
    * Entry–Courtyard–Backdoor–Vault

    so the entry–exit edge connectivity is exactly 3.
    """
    graph = build_lair_graph(
        [
            "Entry",
            "Hall",
            "MR1",
            "Gallery",
            "Vault",
            "Tunnel",
            "Armory",
            "Courtyard",
            "Backdoor",
            "Wine_Cellar",
        ],
        [
            ("Entry", "Hall"),
            ("Hall", "MR1"),
            ("MR1", "Gallery"),
            ("Gallery", "Vault"),
            ("Entry", "Tunnel"),
            ("Tunnel", "Armory"),
            ("Armory", "Vault"),
            ("Entry", "Courtyard"),
            ("Courtyard", "Backdoor"),
            ("Backdoor", "Vault"),
            ("Backdoor", "Wine_Cellar"),
        ],
    )
    return graph, EXTENDED_ENTRY, EXTENDED_EXIT


def to_directed_network(graph: Adjacency, capacity: float = 1.0) -> Network:
    """Convert an undirected lair graph into a directed capacity network.

    Every mirror passage becomes two arcs (u→v and v→u), each with the given
    capacity. Sorted neighbour order keeps BFS/DFS iteration deterministic.
    """
    _require_capacity(capacity)
    network: Network = {node: {} for node in graph}
    for node in sorted(graph):
        for neighbour in sorted(graph[node]):
            if node < neighbour:  # add each undirected edge once
                network[node][neighbour] = capacity
                network[neighbour][node] = capacity
    return network


def _require_capacity(capacity: float) -> None:
    if capacity <= 0:
        raise ValueError(f"capacity must be positive, got {capacity}")


def _require_node(network: Network, node: str, label: str) -> None:
    if node not in network:
        raise ValueError(f"{label} node {node!r} is not part of the network")


def _bfs_parent(
    network: Network,
    source: str,
    sink: str,
    flow: dict[tuple[str, str], float],
) -> dict[str, str | None]:
    """Breadth-first search for an augmenting path in the residual network."""
    parent: dict[str, str | None] = {source: None}
    queue: deque[str] = deque([source])
    while queue:
        node = queue.popleft()
        for neighbour in sorted(network[node]):
            if neighbour in parent:
                continue
            residual = network[node][neighbour] - flow.get((node, neighbour), 0.0)
            if residual > 1e-9:
                parent[neighbour] = node
                if neighbour == sink:
                    return parent
                queue.append(neighbour)
    return parent


def edmonds_karp(network: Network, source: str, sink: str) -> tuple[float, dict[tuple[str, str], float]]:
    """Maximum s–t flow via Edmonds–Karp (BFS augmenting paths).

    Returns ``(max_flow_value, flow_edges)`` where ``flow_edges[(u, v)]`` is
    the amount carried on arc u→v. Deterministic: neighbours visited in sorted
    order, so the decomposition is stable.
    """
    _require_node(network, source, "source")
    _require_node(network, sink, "sink")
    if source == sink:
        return 0.0, {}
    flow: dict[tuple[str, str], float] = {}
    max_value = 0.0
    while True:
        parent = _bfs_parent(network, source, sink, flow)
        if sink not in parent:
            break
        # unit-ish bottleneck along the path (min residual capacity)
        bottleneck = float("inf")
        node = sink
        while True:
            prev = parent[node]
            if prev is None:
                break
            residual = network[prev][node] - flow.get((prev, node), 0.0)
            bottleneck = min(bottleneck, residual)
            node = prev
        node = sink
        while True:
            prev = parent[node]
            if prev is None:
                break
            flow[(prev, node)] = flow.get((prev, node), 0.0) + bottleneck
            flow[(node, prev)] = flow.get((node, prev), 0.0) - bottleneck
            node = prev
        max_value += bottleneck
    return max_value, flow


def edge_connectivity(graph: Adjacency, entry: str, exit_: str) -> float:
    """Number of edge-disjoint escape routes (entry–exit max flow)."""
    return edmonds_karp(to_directed_network(graph), entry, exit_)[0]


def min_cut_edges(graph: Adjacency, entry: str, exit_: str) -> tuple[tuple[str, str], ...]:
    """Minimum mirror walls separating entry from exit (the min s–t cut).

    After max flow, the source-side reachable set in the residual graph gives
    the cut; the cut edges are the original undirected passages crossing it,
    returned sorted.
    """
    network = to_directed_network(graph)
    _, flow = edmonds_karp(network, entry, exit_)
    reachable = _residual_reachable(network, entry, flow)
    cut: set[tuple[str, str]] = set()
    for node in sorted(network):
        for neighbour in sorted(network[node]):
            if node < neighbour and (node in reachable) != (neighbour in reachable):
                cut.add((node, neighbour))
    return tuple(sorted(cut))


def _residual_reachable(
    network: Network,
    source: str,
    flow: dict[tuple[str, str], float],
) -> set[str]:
    """Nodes reachable from ``source`` in the residual graph."""
    seen: set[str] = set()
    queue: deque[str] = deque([source])
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        for neighbour in sorted(network[node]):
            if network[node][neighbour] - flow.get((node, neighbour), 0.0) > 1e-9:
                queue.append(neighbour)
    return seen


def edge_disjoint_escape_routes(graph: Adjacency, entry: str, exit_: str) -> tuple[tuple[str, ...], ...]:
    """Decompose the max flow into explicit edge-disjoint escape routes.

    Follows arcs carrying flow from the entry, subtracting one unit per route,
    until no flow remains. Returns routes as room sequences, in deterministic
    order.
    """
    network = to_directed_network(graph)
    _, flow = edmonds_karp(network, entry, exit_)
    routes: list[tuple[str, ...]] = []
    remaining = dict(flow)
    while True:
        path: list[str] = [entry]
        node = entry
        advanced = False
        while node != exit_:
            chosen: str | None = None
            for neighbour in sorted(network[node]):
                if remaining.get((node, neighbour), 0.0) > 1e-9:
                    chosen = neighbour
                    break
            if chosen is None:
                break
            remaining[(node, chosen)] -= 1.0
            path.append(chosen)
            node = chosen
            advanced = True
        if not advanced or node != exit_:
            break
        routes.append(tuple(path))
    return tuple(routes)


def cost_aware_escape(
    graph: Adjacency,
    costs: dict[tuple[str, str], float],
    entry: str,
    exit_: str,
) -> tuple[float, tuple[str, ...]] | None:
    """Cheapest escape route under per-passage traversal costs (Dijkstra).

    ``costs`` keys are undirected edges ``(a, b)`` (either orientation); a
    missing edge cost raises ``ValueError``. Returns ``(total_cost, path)`` or
    ``None`` when the exit is unreachable.
    """
    if entry not in graph or exit_ not in graph:
        raise ValueError("entry and exit must be rooms of the lair graph")
    # Normalise costs into a both-directions lookup.
    edge_cost: dict[tuple[str, str], float] = {}
    for (left, right), cost in costs.items():
        if cost < 0:
            raise ValueError(f"edge cost must be non-negative, got {cost}")
        if left not in graph or right not in graph:
            raise ValueError(f"cost edge references an undeclared room: {left!r}-{right!r}")
        if left > right:
            left, right = right, left
        edge_cost[(left, right)] = cost
    for node in graph:
        for neighbour in graph[node]:
            key = (min(node, neighbour), max(node, neighbour))
            if key not in edge_cost:
                raise ValueError(f"no traversal cost registered for passage {node!r}-{neighbour!r}")

    dist: dict[str, float] = {entry: 0.0}
    prev: dict[str, str | None] = {entry: None}
    heap: list[tuple[float, str]] = [(0.0, entry)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        if node == exit_:
            break
        for neighbour in sorted(graph[node]):
            cost = edge_cost[(min(node, neighbour), max(node, neighbour))]
            candidate = d + cost
            if candidate < dist.get(neighbour, float("inf")):
                dist[neighbour] = candidate
                prev[neighbour] = node
                heapq.heappush(heap, (candidate, neighbour))
    if exit_ not in dist:
        return None
    path: list[str] = []
    cur: str | None = exit_
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return dist[exit_], tuple(reversed(path))


def unit_traversal_costs(graph: Adjacency) -> dict[tuple[str, str], float]:
    """Unit traversal costs for every passage (distance metric convenience)."""
    costs: dict[tuple[str, str], float] = {}
    for node in graph:
        for neighbour in graph[node]:
            key = (min(node, neighbour), max(node, neighbour))
            costs[key] = 1.0
    return costs
