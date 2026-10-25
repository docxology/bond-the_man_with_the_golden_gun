# Testing philosophy — the_man_with_the_golden_gun (SOLEX)

Why the test suite in this package looks the way it does, and what each rule is
actually protecting against. The mechanical instructions are in
[`agent_instructions.md`](agent_instructions.md); this file is the reasoning.

## The three commitments

1. **No mock framework.** Not `unittest.mock`, not `MagicMock`, not
   `mocker.patch`, not `monkeypatch` standing in for a dependency.
2. **Real data, real computation.** Every assertion checks a value the code
   genuinely produced, a file it genuinely wrote, or a process that genuinely
   ran.
3. **Deterministic.** The same inputs give the same outputs, byte for byte,
   across runs and machines.

These are not stylistic preferences. Each one closes a specific way a green
suite can lie.

## Why no mocks

A mock asserts that the code called something in a particular way. It cannot
assert that the thing it called would have produced the right answer. For a
package whose entire purpose is numerical and combinatorial results, that is
the wrong question: mocking `edmonds_karp` to return `3.0` and asserting the
caller reports `3.0` proves nothing about max flow.

The domain here is also unusually easy to test for real. Every module is pure,
stdlib-only, and fast — the whole suite runs in a couple of seconds. There is
no network, no database, no clock, and no external service, so there is nothing
a mock would be buying. Where a real dependency does exist (matplotlib, the
`bond_api` protocol, the `scripts/` entry points), the test uses the real one:
figures are actually rendered to PNG, protocol conformance is checked with
`isinstance` against the runtime-checkable Protocol, and CLI tests run
`sys.executable` in a subprocess.

`pytest`'s `tmp_path` is used freely. A real temporary directory is a real
filesystem, not a stand-in for one.

## Known vectors over self-consistency

The default failure mode of an algorithm test is checking the implementation
against itself. This suite prefers assertions whose expected value is derived
from the definition of the algorithm or from an independent property:

* **Textbook values.** `solar_declination_deg(172) ≈ 23.45°` is the June
  solstice declination, known before the code was written.
  `beam_flux_kw_m2(1000, 90°) == 1.0` is the definition of the projection.
* **Structural properties.** The edge-disjoint routes are checked to be
  *pairwise edge-disjoint*, not merely three in number. The min cut is checked
  to have the same cardinality as the flow value, which is max-flow min-cut.
  The deadline scheduler's reported profit is checked to equal the summed
  profit of exactly the jobs in its slot assignment.
* **Divergence between two solvers.** The duel book is deliberately built so
  the earliest-finish greedy and the weighted-interval DP select different
  schedules. If both solvers ever agreed on this fixture, one of them would be
  broken and the test would say so.

## Fixtures are chosen so the answer is not trivial

A fixture that makes every gate pass by construction is worse than no fixture.

* The **extended lair** has three parallel corridors specifically because a
  single-route lair has max flow 1 and a one-edge min cut regardless of whether
  the flow code is correct.
* The **deadline book** over-subscribes its slots (5 contracts, 3 slots) so the
  scheduler must actually reject work. A book that fit entirely would pass with
  a scheduler that accepted everything.
* The **mirror budget** (200 m² against a 300 m² field) is smaller than the
  field so the allocator has to choose, and it is sized so the greedy skips two
  mid-size mirrors and falls through to the smallest — behaviour a
  take-everything implementation would not reproduce.

## Positive controls: every gate must be able to fail

A check that cannot fail is decoration. Where this package added a gate, it also
added a test that makes the gate fire:

* `verify_declared_experiment()` cross-checks the config against the models.
  `test_declared_experiment_rejects_a_stale_config` tampers with each declared
  key in turn and asserts the mismatch raises and names the offending key, and
  `test_declared_experiment_verifies_every_key_of_the_live_config` compares the
  verified set against the leaf keys really present in the file — a key nobody
  wired up is a failure, not a silent omission.
* `verify_claim_ledger()` recomputes every claim in `data/claim_ledger.yaml`.
  `test_every_claim_value_can_fail` runs one case per claim: perturb the
  recorded value by one and assert the verifier names that claim. The evidence
  column is controlled too — a renamed symbol or a deleted test file raises.
* The `experiment_plan.yaml` / `domain_profile.yaml` overlays are checked
  against `DOMAIN_MODULES`, the figure registry, the canonical inputs and the
  ledger claim ids, each with a tampered-copy control. These files are the
  reason this section exists: before the checks they were pure prose, and both
  sat three modules and one figure behind the code without anything noticing.
* The token gate scans the manuscript for placeholders the generator does not
  produce. Its scan set is asserted non-empty first, because a gate that finds
  zero sections would report a clean sweep — and it is the same set
  `write_resolved_tree()` writes, because a file that is hydrated but not
  scanned (as `preamble.md` once was) is a gap the gate cannot see.
* The figure cross-check runs in **both** directions: no section may cite a
  figure the registry lacks, and no registered figure may go unreferenced.
* The determinism claim is not asserted in prose alone —
  `test_figures_are_byte_identical_across_runs` renders every figure twice into
  separate directories and compares raw bytes.

## Error paths are behaviour

Validation is part of the contract, so it is tested like any other behaviour.
`Mirror`, `Appointment`, and `DeadlineJob` all reject malformed construction;
`build_lair_graph` rejects a passage naming an undeclared room;
`cost_aware_escape` rejects a missing or negative passage cost. That last one is
load-bearing: defaulting a missing cost to zero would invent a free escape
route, so the test asserting it raises is protecting a result, not a signature.

## Coverage: what the number does and does not mean

The gate is **90% line and branch** on `src/`, enforced by
`pytest --cov-fail-under` and mirrored in `manuscript/config.yaml` as
`gates.coverage_fail_under` (which is where the manuscript reads it from, so no
document quotes a threshold by hand). The suite currently sits above that gate;
the live measurement is recorded in
[`_generated/COUNTS.md`](_generated/COUNTS.md) rather than in prose that would
drift.

Branch coverage is enabled deliberately. Line coverage alone would call the
clamped `daylight_hours` polar-day and polar-night branches covered after a
single mid-latitude call.

What coverage does not mean: it is a floor on *execution*, not evidence of
*correctness*. A suite can execute every line while asserting nothing that
matters. Coverage is therefore treated here as necessary and insufficient — the
substance is in the known vectors, the structural properties, and the positive
controls above.

## Determinism, concretely

Three surfaces could introduce nondeterminism, and each is closed in the code
rather than tolerated in the tests:

* **Randomness** — there is none. No module imports `random` or
  `numpy.random`. The mission seed is recorded for protocol conformance, not
  consumed.
* **Iteration order** — every graph traversal iterates `sorted(neighbours)`, so
  the BFS route, the flow decomposition, and the min cut are stable across runs
  and interpreter hash seeds. Schedulers break ties on explicit keys.
* **Wall clock** — persisted artifacts carry a fixed `DEFAULT_TIMESTAMP`, and
  the mission outcome records `wall_time_s = 0.0` rather than a measurement, so
  a re-run is byte-identical.

## Running the suite

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90     # the gate
uv run pytest tests/test_lair_flows.py -v              # one module
uv run pytest tests/ -k determinis -v                  # one theme
```

`uv run` needs the suite monorepo — the `bond-api` path dependency. On a clone
without that checkout, run the same commands as `python -m pytest …` against a
venv; the recipe is in [`../STANDALONE.md`](../STANDALONE.md).

Coverage below the gate, any failure, or any skip is a red build. Skips are
treated as failures of the fixture, not as an acceptable state: there is no
environment-dependent test in this package that would legitimately need one.
