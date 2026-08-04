# TODO.md — the_man_with_the_golden_gun (SOLEX)

Project BOND film package · The Man with the Golden Gun (1974) · mission
codename **SOLEX**. Local-only working tree (no remote, never push).

## Done (phase-2 conversion)

- [x] Stripped the exemplar scaffold (src/scripts/tests/docs/manuscript
      vendored template resources removed; metadata rewritten for this film).
- [x] Pure domain core under `src/the_man_with_the_golden_gun/`:
  - [`solar_concentration.py`](src/the_man_with_the_golden_gun/solar_concentration.py) —
    mirror-array → heat-output yield model (field optical power, thermal
    output, concentration ratio, greedy optimal mirror-budget allocation).
  - [`lair_topology.py`](src/the_man_with_the_golden_gun/lair_topology.py) —
    funhouse rooms/mirrors as an undirected graph: BFS escape route,
    reachability, Tarjan cut vertices, exact entry→exit bottleneck rooms.
  - [`duel_scheduler.py`](src/the_man_with_the_golden_gun/duel_scheduler.py) —
    bounty appointment book: conflict detection, weighted interval scheduling
    (max-bounty DP), earliest-finish greedy, `active_at`.
- [x] Frozen protocol integration:
  - `[tool.uv.sources] bond-api` path dependency wired in `pyproject.toml`.
  - [`mission.py`](src/the_man_with_the_golden_gun/mission.py) implements the
    frozen bond_api `MissionProvider` (film, brief, recon, plan, execute,
    debrief) and registers domain gadgets with `bond_api.registry.GadgetRegistry`.
  - Pure domain modules importable standalone (no `bond_api` import).
- [x] Thin per-phase CLIs in `scripts/` (brief/recon/plan/execute/debrief +
      `run_mission.py` all) + `00_preflight.py`, `generate_artifacts.py`,
      `z_generate_manuscript_variables.py`.
- [x] `manuscript_variables.py` — `{{TOKEN}}` hydration from `config.yaml` +
      deterministic domain models; live cross-reference gate in tests.
- [x] `figures.py` — three deterministic concept figures (solar yield, lair
      topology, duel schedule) under `output/figures/`.
- [x] Manuscript rewritten for the film (config identity + SOLEX mission block,
      numbered `{{TOKEN}}` sections, figures).
- [x] Zero-mock real-data test suite: 72 tests, **100% line+branch** on `src/`.
- [x] Gates green: pytest `--cov-fail-under=90`, ruff check+format, mypy,
      zero lineage strings, git clean.

## Integration points (declared)

- `mission_io.record_provenance_outcome` (bond-utilities): the SOLEX outcome
  currently carries `Provenance` inside the protocol object; once
  bond-utilities ships, add a script that persists each executed outcome to a
  provenance store via `mission_io.record_provenance_outcome`.
  Acceptance: `scripts/` gains a record step producing a byte-identical record
  for a fixed seed, verified in `test_scripts_smoke.py`.
- `bond-coordinator`: when the fleet coordinator lands, the SOLEX provider is
  already discoverable by slug via `bond_api.discovery` — no rework expected.

## Not done / future

- [ ] Optional: multi-Day DNI profile sweep for solar yield (currently a fixed
      canonical DNI in `manuscript/config.yaml`).
- [ ] Optional: larger random-lair stress fixtures (deterministic seeded) to
      scale-test the exact bottleneck solver beyond the 7-room canonical lair.
- [ ] Optional: tie the mission to a second film package for a cross-package
      scheduling scenario (duel book shared across two appointment books).
