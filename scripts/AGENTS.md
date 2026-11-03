# scripts/ — agent guidance

The reader's view is [README.md](README.md); the package-wide rules are in
[the root guide](../AGENTS.md); the operational checklist is
[`../docs/agent_instructions.md`](../docs/agent_instructions.md).

## Rules that hold inside this directory

1. **Thin wrappers only.** A script shapes `argv`, calls into `src/`, and prints or writes. A
   computation written here bypasses the tests and the manuscript's recomputation; it belongs in
   `src/`.
2. **Use the shared bootstrap.** `_bootstrap.py` inserts `src/` onto `sys.path` so a bare
   `python scripts/<name>.py` works without an install. Import it rather than repeating the insert.
3. **Run from the repository root.** That is what makes `pythonpath = [".", "src"]` apply; the
   bootstrap makes the scripts robust to a different working directory, but the root is the documented
   route.
4. **Write only under `output/`.** It is in `.gitignore` and regenerable; nothing generated may be
   committed, and no script may write into `data/` or `manuscript/`.

## The generation script carries gates, not just output

`z_generate_manuscript_variables.py` exits non-zero if any manuscript placeholder survives hydration,
and while it runs it also executes `declarations.verify_claim_ledger()` (because
`manuscript/config.yaml` declares `data/claim_ledger.yaml` as `experiment.data_ledger`). A green run
therefore says the tree resolved *and* the recorded claims still match the models. Treat a failure here
as a real gate failure, not as a stale output file.

Measured on 2026-11-03 at `026d766`, run from the repository root: `scripts/00_preflight.py` reports
the film slug and codename and exits 0; `scripts/run_mission.py` prints the lifecycle objects tagged
with `__bond_type__`; `z_generate_manuscript_variables.py` resolves the tree and reports every token
resolved, exit 0. Test counts and coverage are not repeated here — they live in the regenerated
[`docs/_generated/COUNTS.md`](../docs/_generated/COUNTS.md).

## Dated, and the first thing to re-check

`[tool.uv.sources]` in `pyproject.toml` pins `bond-api = { path = "../bond-api" }`, so `uv sync` and
`uv run` need that sibling checkout present; without it, run the suite and these scripts through an
interpreter that already has `bond_api` installed. As of 2026-11-03 a vendoring change in this suite
replaces the path dependency with a `vendor/bond-api` directory, after which an ordinary `uv sync`
resolves locally — re-check this paragraph if that change has landed here.

One discrepancy to know about, since it misleads: the root guide's "Protocol integration" section
prints this pin as a path inside the suite monorepo. The value in `pyproject.toml` at this head is the
sibling `../bond-api`; the file is the truth, and the prose there is stale.
