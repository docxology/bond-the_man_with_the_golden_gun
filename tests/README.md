# tests/ — the_man_with_the_golden_gun (SOLEX)

Zero-mock, real-data test suite. Every assertion checks a genuine computed
value, a genuinely written file, or a genuinely executed process — no mock
framework anywhere (no mocked objects, patches, or autospecs). The reasoning
behind each rule is in [`../docs/testing_philosophy.md`](../docs/testing_philosophy.md).

| File | Coverage focus |
| --- | --- |
| `test_solar_concentration.py` | Mirror/power/yield/concentration values, greedy budget allocation, and construction validation |
| `test_solar_tracking.py` | Declination and equation of time against solstice values, elevation/azimuth conventions, daylight clamping at the poles, insolation closed form, daily profile shape |
| `test_lair_topology.py` | Escape path, escape distance, exact bottlenecks, articulation points, reachability, graph-construction validation |
| `test_lair_flows.py` | Edmonds–Karp value, pairwise edge-disjointness of the decomposed routes, min-cut cardinality and membership, Dijkstra rerouting and its error paths |
| `test_duel_scheduler.py` | Weighted interval scheduling, earliest-finish greedy, conflict semantics, `active_at` |
| `test_deadline_scheduler.py` | Matroid greedy profit and slot assignment, their mutual consistency, and the over-subscribed rejection case |
| `test_mission.py` | Protocol conformance, determinism, provenance, serialization round-trip, gadget registry coverage, config-versus-brief objectives |
| `test_manuscript_variables.py` | Token values, the live cross-reference gate, the canonical section set, and the positive controls proving the config gate can fail |
| `test_figures.py` | Real rendering, byte-identity across runs, registry-versus-manuscript agreement in both directions |
| `test_mission_cli.py` | Phase exit codes and printed output |
| `test_scripts_smoke.py` | Real subprocess runs of the `scripts/` entry points via `sys.executable` |

Run the gate:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Line **and** branch coverage on `src/`; zero failures and zero skips are
required. The measured figures from the latest run are in
[`../docs/_generated/COUNTS.md`](../docs/_generated/COUNTS.md).

## Writing a new test

Derive the expected value from the algorithm's definition or from a structural
property — not from running the new code and pasting its output, which only
proves the code agrees with itself. Where a new gate is added, add the positive
control that makes it fire: a check that cannot fail proves nothing.
