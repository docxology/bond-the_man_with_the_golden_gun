# data/ — the claim ledger, and nothing else

This directory holds one curated file: [`claim_ledger.yaml`](claim_ledger.yaml), the register of the
sourced numeric claims that the manuscript and the mission outcome rest on.

## Why a ledger rather than numbers in prose

Every figure in the manuscript is computed by the models in `src/`, and
`src/the_man_with_the_golden_gun/manuscript_variables.py` hydrates the `{{TOKEN}}`s from those
computations. The ledger is the other half of that arrangement: for each claim it records the value,
the `evidence` symbol that computes it (`module.py::symbol`) and the `test` file that locks it, so a
figure traces back to code and to a test rather than to whoever typed it.

It is **verified, not documentation**. `declarations.verify_claim_ledger()` recomputes every value from
the domain models at the precision recorded beside it, checks that each `evidence` file defines the
symbol it names and that each `test` file exists, and requires the claim set to equal the recomputation
registry exactly in both directions. The verifier runs during token generation, because
`manuscript/config.yaml` declares this path as `experiment.data_ledger`: a run of
[`../scripts/z_generate_manuscript_variables.py`](../scripts/z_generate_manuscript_variables.py)
fails if the ledger and the code have drifted apart.

## What that means for a reader

- The code is the source of truth; the ledger is a checked restatement of it. To change a claim,
  change the model first, then the entry.
- A claim cannot be added without a recomputation behind it, and cannot be left behind when the code
  moves.
- Each value carries the precision at which it is verified, which is part of the claim.

## What is not here

No datasets, no fixtures, no generated output. The canonical inputs are declared under
`canonical_inputs` in `experiment_plan.yaml` at the repository root; generated artifacts are written
under the ignored `output/`; prose figures belong in `manuscript/`. The rules that govern all of this
are in [the root guide](../AGENTS.md), and the layer contract is in
[`../docs/architecture.md`](../docs/architecture.md).
