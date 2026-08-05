# Manuscript editing rules — the_man_with_the_golden_gun (SOLEX)

Agent directives for editing this package's manuscript. Package-level rules are
in [`../AGENTS.md`](../AGENTS.md); this file covers manuscript-specific
concerns. See also [`README.md`](README.md) (token and figure pipeline) and
[`SYNTAX.md`](SYNTAX.md) (Pandoc conventions).

## Section set

| File | Holds |
| --- | --- |
| `preamble.md` | Pandoc document metadata only — not a numbered section, not token-gated |
| `00_abstract.md` | The dossier in one page, with headline results as tokens |
| `01_introduction.md` | The three film premises restated as computational problems |
| `02_methodology.md` | The algorithms and why each is exact, with citations |
| `03_results.md` | Every quantitative finding, entirely token-injected |
| `04_conclusion.md` | What the findings mean plus the methodological claim |
| `05_experimental_setup.md` | Every fixture and parameter the results depend on |
| `06_reproducibility.md` | Regeneration procedure, determinism surfaces, gates |
| `07_scope_and_related_work.md` | What this is not, and the literature each module implements |
| `08_appendix.md` | The full generated metric register |
| `99_references.md` | Bibliography rendering hook |
| `config.yaml` | Token inputs and the verified `experiment` declarations |
| `references.bib` | Real, checkable sources only |

Sections matching `[0-9]*.md` are hydrated by
`manuscript_variables.write_resolved_tree()` and scanned by the live token
gate. `preamble.md` is deliberately outside that glob.

## Token protocol

Any value derived from the domain must be a `{TOKEN}` produced by
`src/the_man_with_the_golden_gun/manuscript_variables.py::generate_variables()`.
Never hardcode a computed metric in prose — including counts ("six modules",
"four figures"), which are tokens too.

* New metric → add the entry to `generate_variables()` **first**, then cite it.
* `tests/test_manuscript_variables.py` fails on any token in a numbered section
  that the generator does not produce.
* Do not write a literal double-brace placeholder as illustrative prose inside a
  numbered section: the gate reads it as a real token and fails. Describe it in
  words instead, or put the example in this file, which is not scanned.
* Threshold values (the coverage gate, the mission seed) come from
  `config.yaml` through tokens as well, so no section quotes a gate by hand.

## Figure protocol

Declare figures with a Pandoc-crossref label and a path under
`../output/figures/`:

```md
![Caption.](../output/figures/solex_yield.png){#fig:solex_yield}
```

Reference them in prose as `[@fig:solex_yield]`. The label must exist in the
`FIGURES` registry in `figures.py`, and every registered figure must be declared
by some section — `tests/test_figures.py` enforces both directions, so a figure
cannot be silently orphaned or invented. Regenerate with
`scripts/generate_artifacts.py`.

## References

`references.bib` entries must be real and verifiable: real authors, real
titles, real years, real venues. If you cannot confirm an entry exists as
stated, delete it rather than ship it. Every entry should back something this
package actually implements; the one deliberate exception (Michalsky 1988, the
unimplemented accuracy upgrade) is called out as such in `99_references.md`.

## Section modification workflow

1. Change the domain code or `config.yaml`.
2. Regenerate: `scripts/generate_artifacts.py`, then
   `scripts/z_generate_manuscript_variables.py`.
3. Re-run the suite — the token gate, the figure cross-check, the
   config-versus-code verification, and the config-versus-brief objectives
   check all live in `tests/`.
4. Confirm `output/manuscript/` contains no unresolved placeholder.
5. Commit code, config, and prose together. A prose change describing behaviour
   the code does not have is the failure mode this whole pipeline exists to
   prevent.
