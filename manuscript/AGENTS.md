# Manuscript editing rules — the_man_with_the_golden_gun (SOLEX)

Agent directives for editing this package's manuscript. The package-level
rules live in ../../AGENTS.md; this file covers manuscript-specific concerns.

## {{TOKEN}} protocol

Numeric values derived from the domain must use `{{TOKEN}}` syntax and come
from `src/the_man_with_the_golden_gun/manuscript_variables.py::generate_variables()`.
Never hardcode a computed metric in prose. The live cross-reference test
(`tests/test_manuscript_variables.py`) enforces this across `[0-9]*.md`.

## Figure protocol

Reference the three concept figures with Pandoc-crossref labels
(`[@fig:solex_yield]`, `[@fig:lair_topology]`, `[@fig:duel_schedule]`) and the
relative paths under `../output/figures/` shown in `README.md` of this
directory. Regenerate via `scripts/generate_artifacts.py`.

## Section modification workflow

When you change domain behaviour or config, regenerate artifacts
(`scripts/generate_artifacts.py`) and re-run
`scripts/z_generate_manuscript_variables.py`, then confirm the live token and
figure references still resolve before committing.
