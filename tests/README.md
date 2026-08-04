# tests/ — the_man_with_the_golden_gun (SOLEX)

Zero-mock, real-data test suite. Every assertion checks a genuine computed
value or a real subprocess execution — no mock framework anywhere (no mocked
objects, patches, or autospecs).

| File | Coverage focus |
| --- | --- |
| `test_solar_concentration.py` | mirror/power/yield/allocation values + validation |
| `test_lair_topology.py` | escape path, bottlenecks, articulation, reachability |
| `test_duel_scheduler.py` | weighted interval scheduling + conflict semantics |
| `test_mission.py` | protocol conformance, determinism, serialization, gadgets |
| `test_manuscript_variables.py` | token map + live cross-reference gate |
| `test_figures.py` | deterministic figure rendering |
| `test_mission_cli.py` | phase exit codes + printed output |
| `test_scripts_smoke.py` | subprocess CLI runs via `sys.executable` |

Run: `uv run pytest tests/ --cov=src --cov-fail-under=90` (100% line+branch).
