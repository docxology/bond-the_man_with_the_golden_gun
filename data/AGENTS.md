# data/ — agent guidance

The reader's view is [README.md](README.md); the package-wide rules are in
[the root guide](../AGENTS.md); the operational checklist is
[`../docs/agent_instructions.md`](../docs/agent_instructions.md).

## The one rule that matters here

`claim_ledger.yaml` is checked against the code, so editing it cannot make a failing figure pass:

- every `value` is recomputed from the domain models at the precision recorded beside it;
- every `evidence` entry must name a symbol the cited file actually defines;
- every `test` entry must name a file that exists;
- the claim set must equal the recomputation registry in both directions — no orphan claim, and no
  recomputation left unrecorded.

`declarations.verify_claim_ledger()` runs while `scripts/z_generate_manuscript_variables.py` hydrates
the manuscript, because `manuscript/config.yaml` declares this path as `experiment.data_ledger`. If a
number is wrong, either the model is wrong or the ledger records it at the wrong precision; the
ledger's arithmetic is never the fix.

## Adding or moving a claim

1. Put the computation in `src/` (or move it there), with the test that locks it.
2. Record the claim with its value, precision, `evidence` symbol and `test` file.
3. Run `scripts/z_generate_manuscript_variables.py` and let the verifier decide.

## What does not belong in this directory

Datasets and fixtures (declared under `canonical_inputs` in `experiment_plan.yaml`), generated
artifacts (the ignored `output/`), and prose figures (`manuscript/`). This directory is curated input
that the code verifies — not a place to park anything a script happens to need.
