# docs/ — the_man_with_the_golden_gun (SOLEX)

Agent- and reader-facing documentation for this PROJECT BOND film package:
*The Man with the Golden Gun* (1974), mission codename **SOLEX**. Local-only
working tree — no remote, never pushed.

## Contents

| File | Read it when you want |
| --- | --- |
| [`architecture.md`](architecture.md) | The module-by-module map of `src/`: what each of the six domain modules computes, how the layers compose, and the frozen `MissionProvider` surface `mission.py` must keep |
| [`testing_philosophy.md`](testing_philosophy.md) | Why the suite is zero-mock, real-data and deterministic; how fixtures are chosen so gates can actually fail; what the coverage number does and does not mean |
| [`agent_instructions.md`](agent_instructions.md) | The read-first operational constraints and the gate checklist to run before claiming done |
| [`AGENTS.md`](AGENTS.md) | Rules for editing this directory: describe what exists, never carry a measured number in prose, what to update when code changes |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | The measured test count and coverage, copied from a real gate run |

## Where the rest lives

| Question | File |
| --- | --- |
| What is this package and how do I run it? | [`../README.md`](../README.md) |
| What are the package-wide rules and the layer contract? | [`../AGENTS.md`](../AGENTS.md) |
| What work is left? | [`../TODO.md`](../TODO.md) |
| What are the results, and where do the numbers come from? | [`../manuscript/`](../manuscript/) — every metric is token-injected from `manuscript_variables.py` plus `config.yaml` |
| How do I edit the manuscript safely? | [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md) and [`../manuscript/SYNTAX.md`](../manuscript/SYNTAX.md) |
| How do I write a test here? | [`../tests/README.md`](../tests/README.md) |
| Fork / standalone contract | [`../STANDALONE.md`](../STANDALONE.md) |

## Orientation in sixty seconds

SOLEX implements three of the film's technical premises as real algorithms: the
Solex solar concentrator (heliostat yield plus the sun geometry that drives its
daily energy), the mirror-walled funhouse lair (shortest escape route,
bottleneck rooms, edge-disjoint route redundancy, minimum cut, cheapest
escape), and the assassin's contract book (weighted interval scheduling,
earliest-finish greedy, and unit-time deadline scheduling).

Six pure domain modules do the computation and import nothing beyond the Python
standard library. One adapter, `mission.py`, exposes them through the frozen
`bond-api` protocol — it is the only file in `src/` that imports `bond_api`, so
the scientific core stands alone. Start at
[`architecture.md`](architecture.md).
