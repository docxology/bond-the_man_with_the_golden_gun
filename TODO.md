# TODO.md — the_man_with_the_golden_gun (SOLEX)

PROJECT BOND film package · The Man with the Golden Gun (1974) · mission
codename **SOLEX**. Local-only working tree (no remote, never push).

This file lists **work that is still open**. Completed build history is not
kept here — it is in the git log and in the shipped code, which is the honest
record. What follows is either genuinely undone or a declared integration point
waiting on another package.

## Blocked on other BOND packages

- [ ] **Provenance persistence** (`bond-utilities`, `mission_io`). Executed
      outcomes currently carry a `Provenance` record inside the protocol object
      and are written to `output/data/solex_outcome.json`, but nothing persists
      them to a shared provenance store.
      *Integration point:* `mission_io.record_provenance_outcome`.
      *Acceptance:* a `scripts/` record step produces a byte-identical record
      for the canonical inputs across two runs, asserted in
      `tests/test_scripts_smoke.py`.
      *Status:* waiting on `bond-utilities` shipping `mission_io`.

- [ ] **Coordinator registration.** The provider is already discoverable by slug
      through `bond_api.discovery` and `scripts/00_preflight.py` proves it, so
      no rework is expected — but the round trip through the coordinator's
      reconcile step is unexercised from this side.
      *Acceptance:* the coordinator lists SOLEX with its 22 gadgets and the
      package's own preflight and the coordinator's view agree.
      *Status:* waiting on `bond-coordinator`.

## Open domain work

- [ ] **Multi-day DNI sweep.** `solar_tracking` computes daily clear-sky energy
      for one fixed day of year; there is no seasonal profile. A sweep over the
      year would turn the single `SOLAR_FIELD_DAILY_KWH` figure into an annual
      yield curve, which is the number an operator would actually care about.
      Needs: a `field_annual_energy_kwh`, a fifth figure, and tokens for the
      annual total and the solstice-to-solstice ratio.

- [ ] **Incidence-angle losses.** The optical chain applies a flat
      `incidence_factor` defaulting to 1.0, so mirror aim geometry contributes
      nothing. Adding a real cosine loss per heliostat position would make the
      concentration ratio a function of time of day rather than a constant.
      This is the largest single gap between the model and a defensible
      heliostat calculation, and it is documented as out of scope in
      `manuscript/07_scope_and_related_work.md` rather than hidden.

- [ ] **Larger seeded lair fixtures.** The exact bottleneck solver is
      `O(V(V+E))` and is exercised only on the 7-room canonical lair. A
      deterministic generated fixture at 100+ rooms would both scale-test it and
      let the `articulation_points` fast path be compared against the exact
      answer on a graph where they visibly differ.

- [ ] **Cross-package scheduling scenario.** The duel and deadline books are
      self-contained. A scenario sharing one appointment book across two film
      packages would exercise the orchestrator's multi-package path.
      Blocked on `bond-orchestrator`.

## Open verification work

- [ ] **Figure content assertions.** `tests/test_figures.py` proves the PNGs are
      non-empty and byte-reproducible, and that the registry and the manuscript
      agree in both directions. It does not assert anything about what the
      images *show* — a plot drawing the wrong series would pass. Pinning a few
      data-space properties (for example, that the daily-profile curve peaks at
      solar noon) would close that.

- [ ] **Manuscript render.** The token pipeline is gated end to end, but no test
      runs Pandoc, so the `{#fig:...}` crossref labels, the citation keys, and
      the `preamble.md` metadata are verified only by structure, never by an
      actual build. A render smoke test would catch a broken citation key that
      the current gates cannot see.

## Deliberately not doing

* **Ray-traced optics, atmospheric attenuation, receiver thermal loss.** Out of
  scope by design; the lumped model's limits are stated in
  `manuscript/07_scope_and_related_work.md`.
* **A higher-accuracy solar position algorithm** (e.g. Michalsky 1988). The
  Spencer series is accurate to about a tenth of a degree, and nothing reported
  here is sensitive at that resolution. Implementing an unused precision path
  would be scaffolding.
* **Publishing.** This tree is local-only. No remote, no DOI, no archive
  deposit — the metadata sidecars omit DOI fields rather than carrying
  placeholders.
