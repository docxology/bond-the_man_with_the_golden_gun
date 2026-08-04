---
title: "Manuscript directory — the_man_with_the_golden_gun (SOLEX)"
type: "manuscript_guide"
version: "0.1.0"
---

# Manuscript (`manuscript/`)

Numbered prose sections (`[0-9]*.md`) drive the film's mission dossier. Every
`{{TOKEN}}` metric is hydrated from `config.yaml` plus the deterministic
domain models via `src/the_man_with_the_golden_gun/manuscript_variables.py` —
never hand-authored in prose.

## Token pipeline

1. `scripts/z_generate_manuscript_variables.py` calls `generate_variables()`.
2. It writes `output/data/manuscript_variables.json` and the resolved tree to
   `output/manuscript/`.
3. The live gate `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
   scans `[0-9]*.md` only and fails if any `{{TOKEN}}` is not generated.

To add a token: add it to the `variables` dict in `manuscript_variables.py`,
then reference it in a section by the same name.

## Figure protocol

Reference images via Pandoc-crossref labels, never hardcoded numbers:

| Label | PNG | Generator |
| --- | --- | --- |
| `{#fig:solex_yield}` | `../output/figures/solex_yield.png` | `figures.plot_solex_yield` |
| `{#fig:solex_daily}` | `../output/figures/solex_daily.png` | `figures.plot_daily_solar_profile` |
| `{#fig:lair_topology}` | `../output/figures/lair_topology.png` | `figures.plot_lair_topology` |
| `{#fig:duel_schedule}` | `../output/figures/duel_schedule.png` | `figures.plot_duel_schedule` |

Figures are rendered by `scripts/generate_artifacts.py` into the git-ignored
`output/figures/`.
