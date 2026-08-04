# SYNTAX — the_man_with_the_golden_gun (SOLEX) manuscript

Pandoc syntax conventions for this film package.

## Citations

Use BibTeX keys from `references.bib` in square brackets: `[@kleinberg_tardos]`
(parenthetical) or `@kleinberg_tardos` (narrative).

## Figures

Markdown image line with an alt text, a relative path under `../output/figures/`,
and a crossref label:

```md
![Thermal heat output versus DNI.](../output/figures/solex_yield.png){#fig:solex_yield}
```

Reference in prose with `[@fig:solex_yield]`.

## {{TOKEN}}s

`{{UPPERCASE_TOKEN}}` placeholders resolve through
`src/the_man_with_the_golden_gun/manuscript_variables.py`. The set of valid
tokens is exactly the keys returned by `generate_variables()`; the live gate
in `tests/test_manuscript_variables.py` fails on any unknown token in a
numbered section.
