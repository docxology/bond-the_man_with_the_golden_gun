# Architecture — the_man_with_the_golden_gun (SOLEX)

How this package is put together, module by module. For the rules an agent must
follow when changing it, see [`AGENTS.md`](AGENTS.md) and
[`agent_instructions.md`](agent_instructions.md); for the reasoning behind the
test suite, see [`testing_philosophy.md`](testing_philosophy.md).

## The shape in one paragraph

There are three layers and one hard rule. The **domain core** is six pure
modules that import nothing outside the Python standard library and know
nothing about PROJECT BOND. The **adapter** is a single module, `mission.py`,
which is the only file in `src/` that imports `bond_api`. The **presentation
layer** — token hydration, figures, CLI output shaping — sits beside the
adapter and depends on the core. The hard rule is that dependencies point
inward only: if `bond_api` disappeared tomorrow, every domain module would
still import, still compute, and still pass its tests.

```
scripts/                     thin argv-forwarding orchestrators
   │
   ├─► mission_cli.py ──► mission.py ──────────► bond_api  (the ONLY edge to the protocol)
   │                          │
   ├─► figures.py             │
   ├─► manuscript_variables.py│
   ├─► declarations.py        │
   │        │                 │
   └────────┴─────────────────┴──► domain core (stdlib only)
                                     solar_concentration.py
                                     solar_tracking.py
                                     lair_topology.py
                                     lair_flows.py
                                     duel_scheduler.py
                                     deadline_scheduler.py
```

## Domain core

### `solar_concentration.py` — heliostat field yield

The instantaneous half of the Solex model. A `Mirror` is a frozen dataclass of
`(id, area_m2, reflectivity)` validated at construction: a blank id, a
non-positive area, or a reflectivity outside `[0, 1]` raises rather than
producing a quietly wrong field.

* `mirror_optical_power` / `field_optical_power` — `DNI × area × reflectivity ×
  incidence`, summed over the field.
* `thermal_output_kw` — applies optical-intercept and heat-transfer
  efficiencies, both constrained to `(0, 1]`.
* `concentration_ratio` — flux concentration at the receiver aperture. The DNI
  factor cancels analytically, so the result is effective mirrored area per
  receiver area.
* `optimal_mirror_allocation` — the budget problem. Yield per unit area is
  exactly reflectivity, so descending reflectivity is the greedy order. The
  implementation takes **whole** mirrors, skipping any that do not fit the
  remaining budget, which is the integral restriction of the fractional
  optimum and can leave the budget under-spent.
* `solex_yield` — a JSON-serialisable record of the canonical field, consumed
  by the mission outcome.

Canonical constants: `SOLEX_FIELD` (5 mirrors, 300 m²), `SOLEX_DNI`,
`SOLEX_RECEIVER_AREA_M2`.

### `solar_tracking.py` — solar geometry and daily energy

The time half of the Solex model. Declination and equation of time come from
Spencer's Fourier series; the daily extraterrestrial irradiation on a
horizontal plane uses the Duffie–Beckman closed form with the sunrise hour
angle.

* `solar_declination_deg`, `equation_of_time_min` — Spencer series, with the
  day of year validated to `[1, 366]`.
* `solar_hour_angle_deg`, `solar_elevation_deg`, `solar_azimuth_deg` — position.
  Elevation clamps its `asin` argument, so a below-horizon sun returns a
  non-positive elevation instead of raising; azimuth has an explicit branch for
  the vanishing denominator at the zenith.
* `daylight_hours` — sunrise hour angle, clamped to give 0 at polar night and
  24 at polar day rather than a domain error.
* `beam_flux_kw_m2` — horizontal beam flux, floored at zero below the horizon.
* `daily_extraterrestrial_insolation_kwh_m2`, `daily_clear_sky_insolation_kwh_m2`,
  `field_daily_energy_kwh` — the daily resource and what the field converts.
* `solex_daily_profile` — sunrise-to-sunset flux samples for the daily figure.

This module is the only place in the core that imports another core module: it
takes `Mirror` from `solar_concentration` for the field aperture sum.

### `lair_topology.py` — funhouse escape topology

Rooms are nodes, mirror passages undirected edges. `build_lair_graph` rejects a
passage naming an undeclared room, so a typo cannot silently create a phantom
corridor.

* `find_escape_path` / `escape_distance` — BFS shortest route. Neighbours are
  visited in sorted order, so the route is a *fixed* shortest route, not merely
  one of them.
* `reachable_rooms` — BFS reachability.
* `articulation_points` — Hopcroft–Tarjan cut vertices of the whole graph.
* `mirror_gated_bottlenecks` — the rooms separating a **specific** entry from a
  **specific** exit, computed exactly: delete each candidate, re-test
  reachability. `O(V(V+E))`, correct at lair scale.

The distinction between the last two matters and is the easiest mistake in this
package to make. Every entry→exit bottleneck is an articulation point; the
converse is false, because a cut vertex on a dead-end branch splits the graph
without touching the escape route.

Canonical fixture: `adjacency()` / `canonical_lair()` — 7 rooms, `Entrance` to
`Vault` with one dead-end branch.

### `lair_flows.py` — redundancy, sealing, and cost

The flow layer over the same graph type.

* `to_directed_network` — each undirected passage becomes two unit-capacity
  arcs.
* `edmonds_karp` — max flow by BFS augmenting paths, returning both the value
  and the per-arc flow so the result can be decomposed rather than just
  reported.
* `edge_connectivity` — the flow value, which by Menger is the number of
  edge-disjoint escape routes.
* `min_cut_edges` — the residual source-side reachable set gives the cut;
  returns the actual passages, sorted.
* `edge_disjoint_escape_routes` — decomposes the flow into explicit room
  sequences.
* `cost_aware_escape` — Dijkstra over per-passage costs. A passage with no
  registered cost raises; defaulting to zero would fabricate a free route.
* `unit_traversal_costs` — the unit-cost convenience metric.
* `build_extended_lair` — the 10-room fixture with three parallel corridors,
  which exists because a lair with one route makes every flow answer trivial.

### `duel_scheduler.py` — bounty appointment book

Half-open intervals `[start, end)` carrying a bounty. `Appointment` validates a
non-empty id, `end > start`, and a non-negative bounty.

* `overlaps` / `find_conflicts` — pairwise overlap, each unordered pair once.
* `max_bounty_schedule` — weighted interval scheduling: sort by `(end, id)`,
  binary-search the predecessor table, run the DP, reconstruct. Exact.
* `earliest_finish_schedule` — the count-maximising greedy. Exact for count,
  generally wrong for bounty — both are reported precisely so the trade-off is
  visible.
* `active_at` — which contracts are live at a time.

### `deadline_scheduler.py` — unit-time deadline contracts

Each `DeadlineJob` occupies one slot and expires at an integer deadline.

* `_greedy_assignment` — the single implementation: descending profit, each job
  to the latest free slot at or before its deadline, with a path-compressed
  `_SlotUnionFind` answering "latest free slot".
* `max_profit_with_deadlines` and `assign_slots` are two **views** over one run
  of that greedy, which is why the reported profit and the reported slot
  assignment cannot disagree.

The greedy is exact rather than heuristic: the schedulable sets form a matroid.

## Adapter: `mission.py` and the frozen protocol

`mission.py` implements the frozen `bond_api` `MissionProvider`. Its public
shape is consumed by `bond-cli`, the coordinator's reconcile step, and the
orchestrator, so it is **not** free to change:

| Surface | Contract |
| --- | --- |
| `MissionProvider` class | Top-level in `the_man_with_the_golden_gun.mission`; discovered by slug via `bond_api.discovery.load_provider` |
| `MissionProvider.film` | `"the_man_with_the_golden_gun"` — must equal the package slug |
| `.brief()` | `MissionBrief` — objectives, assets, determinism/real-data constraints |
| `.recon(ReconRequest)` | `ReconReport` of findings |
| `.plan(MissionBrief)` | `MissionPlan` — one step per domain model plus a provenance step |
| `.execute(MissionPlan)` | `MissionOutcome` with results and `Provenance(package_version, seed, input_hash, wall_time_s)` |
| `.debrief(MissionOutcome)` | `Debrief` with standing lessons |
| `GADGETS()` | Callable returning the film's gadget map (currently 22 entries) |
| `register_gadgets(registry)` | Registers that map into any `GadgetRegistry` |
| `FILM`, `CODENAME`, `SEED`, `PACKAGE_VERSION`, `mission_id()` | Identity surface used by preflight |

Deepening the package means adding modules and enriching `run_domain()`'s
payload — never renaming or removing the rows above.

`run_domain()` is the seam between adapter and core: it calls every domain
solver and returns a flat, JSON-serialisable mapping keyed
`solar / tracking / lair / flows / duel / deadline / integrated`.
`_input_hash()` fingerprints the canonical inputs with SHA-256 over a
sort-keyed JSON dump, so provenance changes if and only if the inputs change.

## Presentation layer

**`manuscript_variables.py`** turns config plus live domain calls into the
`{TOKEN}` map. Two things make it more than a formatter: `generate_variables()`
calls the real solvers rather than reading stored numbers, and
`verify_declared_experiment()` recomputes every value `manuscript/config.yaml`
restates and raises on disagreement — so a stale config fails the build. The
check is exhaustive by construction: it enumerates the leaf keys present in the
`experiment` block and raises on any key it has no recomputation for.
`manuscript_sources()` names the files carrying tokens (the numbered sections
plus `preamble.md`); `write_resolved_tree()` hydrates exactly that set and the
live gate scans exactly that set, so hydration and gating cannot diverge.
Unresolved placeholders are left verbatim so the gate can see them.

**`declarations.py`** owns the package's self-description and the verification
of the YAML files that restate it: `DOMAIN_MODULES`, the mission codename, the
claim-recomputation registry, and `verify_claim_ledger` /
`verify_experiment_plan` / `verify_domain_profile`. Every value in
`data/claim_ledger.yaml`, `experiment_plan.yaml` and `domain_profile.yaml` is
recomputed here from the domain models and compared, including both directions
of the claim set (no unrecomputed claim, no orphaned recomputation) and the
existence of each claim's cited evidence symbol and test file. The ledger runs
during token generation (`config.yaml` declares its path); the two overlays are
gated by `tests/test_declarations.py`.

**`figures.py`** renders the four concept figures under `output/figures/` with
the `Agg` backend forced at import. The `FIGURES` registry is the single source
of truth for which figures exist; `generate_all_figures` is driven from it, and
the test suite binds it in both directions against the manuscript's
`{#fig:...}` labels.

**`mission_cli.py`** renders one lifecycle phase (or `all`) as deterministic
JSON through `bond_api.serialization`. Exit `0` on success, `2` on an unknown
phase.

## `scripts/` — thin orchestrators

Every script is argv forwarding plus I/O. None contains domain logic.
`_bootstrap.py` inserts `src/` onto `sys.path` so a bare
`python scripts/<name>.py` works without installation.

| Script | Role |
| --- | --- |
| `00_preflight.py` | Loads the provider by slug through `bond_api.discovery` exactly as the orchestrator does, and checks protocol conformance |
| `brief.py` / `recon.py` / `plan.py` / `execute.py` / `debrief.py` | One phase each |
| `run_mission.py` | Any phase or the full flow |
| `generate_artifacts.py` | Mission outcome JSON plus all figures |
| `z_generate_manuscript_variables.py` | Token map, resolved manuscript tree, strict unresolved-token gate |

## Data flow, end to end

```
manuscript/config.yaml ─┐
data/claim_ledger.yaml ─┼─► verify_declared_experiment()  ── raises on drift
domain core ────────────┘   (+ verify_claim_ledger)
        │
        ├─► generate_variables() ─► output/data/manuscript_variables.json
        │                        └─► output/manuscript/*.md   (tokens resolved,
        │                            numbered sections + preamble.md)
        │
        ├─► run_domain() ─► MissionOutcome ─► output/data/solex_outcome.json
        │
        └─► figures.py ─► output/figures/*.png
```

Everything under `output/` is git-ignored and regenerable; nothing there is
ever hand-edited.
