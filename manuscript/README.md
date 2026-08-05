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

## Sections

`preamble.md` (Pandoc metadata, not token-gated), then the numbered set:
`00_abstract`, `01_introduction`, `02_methodology`, `03_results`,
`04_conclusion`, `05_experimental_setup`, `06_reproducibility`,
`07_scope_and_related_work`, `08_appendix`, `99_references`. Inputs live in
`config.yaml` and `references.bib`.

## Token pipeline

1. `scripts/z_generate_manuscript_variables.py` calls `generate_variables()`,
   which reads `config.yaml` and calls the domain models live.
2. Before producing anything, `verify_declared_experiment()` recomputes every
   canonical fact `config.yaml` restates and raises if the config disagrees
   with the code.
3. It writes `output/data/manuscript_variables.json` and the resolved tree to
   `output/manuscript/`, exiting non-zero if any placeholder survives.
4. The live gate
   `tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated`
   scans `[0-9]*.md` and fails if a section cites a token the generator does
   not produce. Its scan set is asserted non-empty, so it cannot pass by
   finding nothing.

To add a token: add it to the returned mapping in `manuscript_variables.py`,
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
`output/figures/`. The table above is not the source of truth — `figures.FIGURES`
is, and `tests/test_figures.py` binds it to the sections in both directions: a
section may not cite an unregistered figure, and a registered figure may not go
undeclared.
