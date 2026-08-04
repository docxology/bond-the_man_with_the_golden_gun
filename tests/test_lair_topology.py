"""Tests for the SOLEX lair escape-topology solver (real graph data, no mocks)."""

from __future__ import annotations

import pytest

from the_man_with_the_golden_gun.lair_topology import (
    articulation_points,
    build_lair_graph,
    canonical_lair,
    escape_distance,
    find_escape_path,
    mirror_gated_bottlenecks,
    reachable_rooms,
)


def test_canonical_lair_path() -> None:
    graph, entry, exit_ = canonical_lair()
    path = find_escape_path(graph, entry, exit_)
    assert path == ("Entrance", "Hall", "Mirror_Room", "Gallery", "Vault")
    assert escape_distance(graph, entry, exit_) == 4


def test_canonical_bottlenecks_and_articulation() -> None:
    graph, entry, exit_ = canonical_lair()
    bottlenecks = mirror_gated_bottlenecks(graph, entry, exit_)
    assert set(bottlenecks) == {"Hall", "Mirror_Room", "Gallery"}
    arts = articulation_points(graph)
    assert arts == {"Hall", "Mirror_Room", "Gallery", "Side_Passage"}


def test_start_equals_exit() -> None:
    graph, entry, _ = canonical_lair()
    assert find_escape_path(graph, entry, entry) == (entry,)
    assert escape_distance(graph, entry, entry) == 0
    assert mirror_gated_bottlenecks(graph, entry, entry) == ()


def test_unreachable_returns_none() -> None:
    graph = build_lair_graph(["a", "b"], [])
    assert find_escape_path(graph, "a", "b") is None
    assert escape_distance(graph, "a", "b") is None


def test_reachable_rooms() -> None:
    graph = build_lair_graph(["a", "b", "c"], [("a", "b")])
    assert reachable_rooms(graph, "a") == frozenset({"a", "b"})
    assert reachable_rooms(graph, "c") == frozenset({"c"})


def test_missing_room_raises() -> None:
    graph, entry, _ = canonical_lair()
    with pytest.raises(ValueError):
        find_escape_path(graph, entry, "Nowhere")
    with pytest.raises(ValueError):
        reachable_rooms(graph, "Nowhere")
    with pytest.raises(ValueError):
        mirror_gated_bottlenecks(graph, entry, "Nowhere")


def test_build_lair_undeclared_room() -> None:
    with pytest.raises(ValueError):
        build_lair_graph(["a"], [("a", "ghost")])


def test_triangle_has_no_articulation() -> None:
    graph = build_lair_graph(["a", "b", "c"], [("a", "b"), ("b", "c"), ("a", "c")])
    assert articulation_points(graph) == frozenset()


def test_star_centre_is_articulation() -> None:
    graph = build_lair_graph(
        ["hub", "leaf1", "leaf2", "leaf3"],
        [("hub", "leaf1"), ("hub", "leaf2"), ("hub", "leaf3")],
    )
    # hub is the DFS root with >1 children -> articulation
    assert articulation_points(graph) == frozenset({"hub"})


def test_isolated_node_not_articulation() -> None:
    graph = build_lair_graph(["solo"], [])
    assert articulation_points(graph) == frozenset()
