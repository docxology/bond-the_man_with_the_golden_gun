"""Tests for the SOLEX lair flow / min-cut / cost-aware escape analysis."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.lair_flows import (
    EXTENDED_ENTRY,
    EXTENDED_EXIT,
    build_extended_lair,
    cost_aware_escape,
    edge_connectivity,
    edge_disjoint_escape_routes,
    edmonds_karp,
    min_cut_edges,
    to_directed_network,
    unit_traversal_costs,
)
from the_man_with_the_golden_gun.lair_topology import adjacency, build_lair_graph


def test_extended_lair_fixture() -> None:
    graph, entry, exit_ = build_extended_lair()
    assert len(graph) == 10
    assert entry == EXTENDED_ENTRY == "Entry"
    assert exit_ == EXTENDED_EXIT == "Vault"


def test_to_directed_network() -> None:
    graph, entry, exit_ = build_extended_lair()
    network = to_directed_network(graph)
    assert set(network) == set(graph)
    # symmetric unit arcs
    assert network["Entry"]["Hall"] == 1.0
    assert network["Hall"]["Entry"] == 1.0
    with pytest.raises(ValueError):
        to_directed_network(graph, capacity=0.0)


def test_edmonds_karp_extended() -> None:
    graph, entry, exit_ = build_extended_lair()
    value, flow = edmonds_karp(to_directed_network(graph), entry, exit_)
    assert value == 3.0
    assert flow  # non-empty flow edges
    # self-loop degenerate case
    assert edmonds_karp(to_directed_network(graph), entry, entry) == (0.0, {})
    with pytest.raises(ValueError):
        edmonds_karp(to_directed_network(graph), entry, "Ghost")


def test_edge_connectivity() -> None:
    graph, entry, exit_ = build_extended_lair()
    assert edge_connectivity(graph, entry, exit_) == 3.0
    # the canonical lair has exactly one escape route -> connectivity 1
    assert edge_connectivity(adjacency(), "Entrance", "Vault") == 1.0


def test_min_cut_edges() -> None:
    graph, entry, exit_ = build_extended_lair()
    cut = min_cut_edges(graph, entry, exit_)
    assert len(cut) == 3
    assert set(cut) == {("Courtyard", "Entry"), ("Entry", "Hall"), ("Entry", "Tunnel")}
    # canonical lair: a single mirror wall seals the vault
    canonical_cut = min_cut_edges(adjacency(), "Entrance", "Vault")
    assert len(canonical_cut) == 1


def test_edge_disjoint_routes() -> None:
    graph, entry, exit_ = build_extended_lair()
    routes = edge_disjoint_escape_routes(graph, entry, exit_)
    assert len(routes) == 3
    for route in routes:
        assert route[0] == entry
        assert route[-1] == exit_
    # pairwise edge-disjoint
    edge_sets = [set(zip(route, route[1:])) for route in routes]
    for i, first in enumerate(edge_sets):
        for second in edge_sets[i + 1 :]:
            assert not (first & second)


def test_cost_aware_escape_unit_costs() -> None:
    graph, entry, exit_ = build_extended_lair()
    result = cost_aware_escape(graph, unit_traversal_costs(graph), entry, exit_)
    assert result == (3.0, ("Entry", "Tunnel", "Armory", "Vault"))


def test_cost_aware_escape_reroutes_around_expensive_wall() -> None:
    graph, entry, exit_ = build_extended_lair()
    costs = unit_traversal_costs(graph)
    costs[("Tunnel", "Armory")] = 10.0
    result = cost_aware_escape(graph, costs, entry, exit_)
    # default Tunnel route rises to 12; the Courtyard route is now cheapest
    assert result == (3.0, ("Entry", "Courtyard", "Backdoor", "Vault"))


def test_cost_aware_escape_validation() -> None:
    graph, entry, exit_ = build_extended_lair()
    with pytest.raises(ValueError):
        cost_aware_escape(graph, {}, entry, exit_)  # missing edge cost
    bad = unit_traversal_costs(graph)
    bad[("Entry", "Hall")] = -1.0
    with pytest.raises(ValueError):
        cost_aware_escape(graph, bad, entry, exit_)  # negative cost
    ghost = unit_traversal_costs(graph)
    ghost[("Ghost", "Hall")] = 1.0
    with pytest.raises(ValueError):
        cost_aware_escape(graph, ghost, entry, exit_)  # undeclared room
    with pytest.raises(ValueError):
        cost_aware_escape(graph, unit_traversal_costs(graph), "Ghost", exit_)


def test_cost_aware_escape_unreachable() -> None:
    graph = build_lair_graph(["a", "b", "c", "d"], [("a", "b"), ("c", "d")])
    costs = unit_traversal_costs(graph)
    assert cost_aware_escape(graph, costs, "a", "d") is None


def test_cost_aware_escape_skips_stale_heap_entry() -> None:
    # b is reachable at cost 2 (a->c->b) and 5 (a->b direct); the stale 5-cost
    # entry is popped after b is already settled and must be skipped.
    graph = build_lair_graph(["a", "b", "c", "t"], [("a", "b"), ("a", "c"), ("c", "b"), ("b", "t")])
    costs = unit_traversal_costs(graph)
    costs[("a", "b")] = 5.0
    costs[("b", "t")] = 100.0
    result = cost_aware_escape(graph, costs, "a", "t")
    assert result == (102.0, ("a", "c", "b", "t"))


def test_min_cut_interior_reachable() -> None:
    # Three source edges but a sink bottleneck of two -> maxflow 2; the
    # residual source-side set reaches interior nodes (BFS interior paths).
    graph = build_lair_graph(
        ["a", "b", "c", "d", "e", "f", "t"],
        [
            ("a", "b"),
            ("a", "c"),
            ("a", "d"),
            ("b", "e"),
            ("b", "f"),
            ("c", "e"),
            ("c", "f"),
            ("d", "e"),
            ("d", "f"),
            ("e", "t"),
            ("f", "t"),
        ],
    )
    assert edge_connectivity(graph, "a", "t") == 2.0
    cut = min_cut_edges(graph, "a", "t")
    assert len(cut) == 2
    assert all(edge[1] == "t" for edge in cut)


def test_unit_traversal_costs_complete() -> None:
    graph, entry, exit_ = build_extended_lair()
    costs = unit_traversal_costs(graph)
    edge_count = sum(len(neighbours) for neighbours in graph.values()) // 2
    assert len(costs) == edge_count
    assert all(cost == 1.0 for cost in costs.values())
