---
title: "{{BOND_TITLE}}"
subtitle: "Heliostat Yield and Solar Tracking, Funhouse Lair Escape Topology and Flow Analysis, and Duel/Deadline Bounty Scheduling"
author:
  - name: "Daniel Ari Friedman"
    orcid: "0000-0001-6232-9096"
    email: "daniel@activeinference.institute"
    affiliation: "Active Inference Institute"
date: "2026-08-04"
lang: en
documentclass: article
papersize: a4
geometry: margin=1in
fontsize: 11pt
numbersections: true
secnumdepth: 3
toc: true
toc-depth: 3
linkcolor: NavyBlue
citecolor: NavyBlue
urlcolor: NavyBlue
link-citations: true
bibliography: references.bib
figPrefix: ["Figure", "Figures"]
secPrefix: ["Section", "Sections"]
tblPrefix: ["Table", "Tables"]
keywords:
  - solar concentration
  - heliostat field
  - clear-sky insolation
  - graph escape topology
  - maximum flow and minimum cut
  - weighted interval scheduling
  - deadline scheduling
  - deterministic reproducible research
  - PROJECT BOND
---

<!--
PROJECT BOND · the_man_with_the_golden_gun (mission SOLEX) — Pandoc preamble.

This file carries document metadata only, so it is not a numbered section — but
it does carry a token, so it IS hydrated and IS gated. `manuscript_sources()`
returns the numbered sections plus this file; `write_resolved_tree` hydrates
every file it returns into `output/manuscript/`, and the live token gate scans
the same set. Before that was fixed, the title token above was hydrated by
nothing and scanned by nothing, and would have rendered as literal braces.

Section order for a combined render:

    preamble.md
    00_abstract.md
    01_introduction.md
    02_methodology.md
    03_results.md
    04_conclusion.md
    05_experimental_setup.md
    06_reproducibility.md
    07_scope_and_related_work.md
    08_appendix.md
    99_references.md

Metadata here must agree with `manuscript/config.yaml`; `config.yaml` is the
source of truth for the token generator, this file for the Pandoc render.
-->
