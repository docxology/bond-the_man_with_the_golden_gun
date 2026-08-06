# TODO — the_man_with_the_golden_gun (SOLEX)

PROJECT BOND film package for *The Man with the Golden Gun* (1974), mission
codename **SOLEX**: six pure domain modules (heliostat yield, solar tracking,
lair escape topology, lair flows, duel scheduling, deadline scheduling) behind
the frozen `bond-api` `MissionProvider`. Local-only working tree — no remote,
never push. **Verified state today (measured 2026-08-06, round-2 improvement
session, Python 3.14.6 darwin): 206 tests passed, 0 failures / 0 errors / 0
skips, 100.00% line and 100.00% branch coverage on `src/` against a
`--cov-fail-under=90` gate;
`ruff check`, `ruff format --check` and `mypy` clean on `src/` and `scripts/`.**
All four findings in `output/verify/the_man_with_the_golden_gun.json` are
remediated and re-verified below; what remains is listed here.

This file lists only work that is still open. Completed history lives in the
git log and in the shipped code.

## Open work

### Correctness

**C1 — The lineage gate command in `AGENTS.md` does not do what its comment
says.**
`AGENTS.md:123` ships this as a required gate:

```
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' --glob '!.venv/**'   # -> zero
```

Run today it returns **two** hits, not zero: `README.md:107` (the gate row that
names the string while describing the rule) and `docs/AGENTS.md:42` (the
sentence permitting lineage to be mentioned as history). `README.md:107` states
the rule correctly — "zero … *outside docs explaining the exemplar lineage*" —
so the code is fine and the `AGENTS.md` comment is wrong. Anyone running the
documented gate literally concludes the package is red when it is green.
*Done when:* `AGENTS.md:123` either excludes the two documentation files with
explicit `--glob` negations, or its trailing comment states the true expected
result and names the permitted files.
*Command:* `rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' --glob '!.venv/**'`
— the output must match what `AGENTS.md:123` claims.

**C2 — The manuscript states two fleet packages have not shipped; both have.**
`manuscript/07_scope_and_related_work.md:80-83` reads "Two integration points
remain open … persisting executed outcomes to a provenance store once
`bond-utilities` ships, and cross-package missions once the coordinator lands."
Both premises are false as of today:

* `bond-utilities/src/bond_utilities/mission_io.py:153` defines
  `record_provenance_outcome`, plus `hash_payload:45`, `validate_record:61`,
  `save_record:92`, `verify_provenance:212`, `append_outcome:296`.
* `bond-coordinator/src/bond_coordinator/registry.py:174` already carries a
  `the_man_with_the_golden_gun` / SOLEX record, and
  `bond-coordinator/src/bond_coordinator/reconcile.py:109,137` provide
  `harvest_gadgets` and `reconcile_report`, driven by
  `bond-coordinator/scripts/reconcile.py`, which loads providers by slug via
  `bond_api.discovery.load_provider`.

Manuscript prose is deliberately not edited by this task; this is recorded, not
fixed. Note this is *scope* prose, not a token, so no gate can catch it — see
V1 for the same class of unbound restatement.
*Done when:* the paragraph either states the integration is complete (once E1
and V8 land) or names what is actually still missing.
*Command:* `ls ../bond-utilities/src/bond_utilities/mission_io.py ../bond-coordinator/src/bond_coordinator/reconcile.py`
— both exist, so the paragraph as written is falsified.

### Verification

Claims not currently bound by a test that can fail.

**V1 — `preamble.md`'s metadata duplicates `config.yaml` with nothing checking
agreement.**
`manuscript/preamble.md:63-64` asserts "Metadata here must agree with
`manuscript/config.yaml`". Only `title` is a token (`preamble.md:2` →
`BOND_TITLE`, gated). Everything else is a hand-typed second copy: `subtitle`
(`preamble.md:3` vs `config.yaml:12`), `date` (`preamble.md:9` vs
`config.yaml:14`), the author block (`preamble.md:4-8` vs `config.yaml:16-21`)
and `keywords` (`preamble.md:27-36` vs `config.yaml:48-60`, which are also not
identical sets today — the preamble omits "solar position algorithms",
"bottleneck analysis" and "thermal yield"). Change one and the render and the
token generator silently disagree.
*Done when:* a test in `tests/test_manuscript_variables.py` parses
`preamble.md`'s YAML front matter and asserts each duplicated field equals its
`config.yaml` counterpart — or the fields become tokens — with a positive
control that tampers with a copy in `tmp_path` and asserts red.
*Command:* `uv run pytest tests/test_manuscript_variables.py -k preamble -v`

**V2 — The zero-mock claim is policy, not a gate.**
`manuscript/config.yaml:71` declares `mock_frameworks_allowed: 0` under a
comment reading "Enforced quality gates", `domain_profile.yaml:21` declares
`zero_mock_tests: true`, and `README.md:101` / `AGENTS.md:8` state it as a rule.
No test scans `tests/` for `unittest.mock`, `MagicMock`, `mocker.patch` or
`monkeypatch`. `declarations.verify_domain_profile` checks only `project`,
`codename`, `source_policy.modules`, `artifact_expectations.script_artifacts`
and (optionally) the coverage floor —
`src/the_man_with_the_golden_gun/declarations.py:397-424`. The suite is in fact
mock-free today; nothing keeps it that way.
*Done when:* a test walks `tests/*.py` and asserts zero imports of a mocking
framework, with a positive control proving the scanner catches a planted import
in a `tmp_path` copy, and asserts the scanned file set is non-empty so it cannot
pass vacuously.
*Command:* `uv run pytest tests/ -k mock -v`

**V3 — The coverage floor has a third, unbound copy.**
`declarations.verify_domain_profile(coverage_gate=...)`
(`declarations.py:416-423`, driven by `tests/test_declarations.py:198-208`)
cross-checks `domain_profile.yaml:20` against `manuscript/config.yaml:70`. The
number that actually gates the suite is `pyproject.toml:61`
(`[tool.coverage.report] fail_under = 90`), and nothing binds it to either. Drop
it to 50 and every declaration check still passes.
*Done when:* a test reads `pyproject.toml`'s `tool.coverage.report.fail_under`
and asserts it equals `config.yaml` `gates.coverage_fail_under`, with a positive
control on a tampered copy.
*Command:* `uv run pytest tests/test_declarations.py -v`

**V4 — `verify_domain_profile` has no unknown-key guard, so two blocks are
silently unchecked.**
`verify_experiment_plan` refuses an unrecognised top-level key
(`declarations.py:315-317, 336-338`), so a new unchecked section in
`experiment_plan.yaml` cannot be added without a decision.
`verify_domain_profile` (`declarations.py:381-424`) has no equivalent: today
`domain_profile.yaml:17` (`film:`) and `domain_profile.yaml:49-52`
(`protocol.adapter`, `protocol.contract`, `protocol.gadgets_registry`) pass
unread. `protocol.adapter` names a real file path
(`src/the_man_with_the_golden_gun/mission.py`) that would go stale unnoticed if
the adapter moved.
*Done when:* `verify_domain_profile` raises on an unrecognised top-level key
(mirroring `_EXPERIMENT_PLAN_KEYS`), `film` is compared against the film title,
and `protocol.adapter` is asserted to be an existing file — each with the
tamper-a-copy positive control the sibling checks already have
(`tests/test_declarations.py:219-236`).
*Command:* `uv run pytest tests/test_declarations.py -v`

**V5 — The figure tests never assert what the images show.**
`tests/test_figures.py` proves the four PNGs are non-empty (`:31-35`),
byte-reproducible across two runs (`:64-77`), that the registry matches the
written filenames (`:57-61`), and that the registry and the manuscript agree in
both directions (`:80-101`). None of that would notice a plot drawing the wrong
series or an inverted axis — only the rendered bytes are checked, never the
data behind them.
*Done when:* each of the four plot builders exposes (or a test recomputes) its
plotted series, and at least one data-space property per figure is pinned — for
example that `solex_daily_profile`'s beam flux peaks at solar noon and is zero
outside the daylight window from `solar_tracking.daylight_hours`.
*Command:* `uv run pytest tests/test_figures.py -v`

**V6 — No test ever renders the manuscript.**
Carried forward from `output/verify/the_man_with_the_golden_gun.unresolved.json`
entry 1, which the remediation pass explicitly declined to close. Tokens are
gated end to end and `preamble.md` is now hydrated and scanned
(`manuscript_variables.py:88, 385-399`), but nothing runs Pandoc. The
`{#fig:...}` crossref labels, the `[@citekey]` references against
`manuscript/references.bib`, and the `preamble.md` front-matter keys are
verified structurally only. A citation key with a typo passes every gate in
this package.
*Done when:* an opt-in smoke test (skipped-with-reason when `pandoc` is absent,
so it cannot silently become a no-op) builds `output/manuscript/` into a single
document and asserts zero unresolved crossrefs and zero missing bibliography
keys in the Pandoc output. Note the current suite forbids skips — decide
explicitly whether this test is gated separately from
`pytest tests/ --cov=src` rather than weakening the zero-skip rule.
*Command:* `uv run pytest tests/test_manuscript_render.py -v` (test does not
exist yet)

**V7 — `requires-python = ">=3.10"` is unverified, and mypy is pinned below the
runtime.**
`pyproject.toml:18` promises 3.10+. The only measurement that exists is Python
3.14.6 (`docs/_generated/COUNTS.md`, and this session's run).
`pyproject.toml:74` pins `[tool.mypy] python_version = "3.12"`, so type checking
neither validates the declared 3.10 floor nor the 3.14 runtime.
*Done when:* either the suite is run once on 3.10 and the result recorded in
`docs/_generated/COUNTS.md`, or `requires-python` is narrowed to what is
actually exercised. Whichever is chosen, `tool.mypy.python_version` should match
the declared floor.
*Command:* `uv run --python 3.10 pytest tests/ --cov=src --cov-fail-under=90`

**V8 — The coordinator round trip is unexercised from this side.**
The provider is discoverable by slug (`scripts/00_preflight.py`, gated by
`tests/test_scripts_smoke.py:21-24`) and `GADGETS()` is pinned at 22 entries
(`tests/test_mission.py:82`). The coordinator's own roster already lists the
slug (`bond-coordinator/src/bond_coordinator/registry.py:174`) and its
reconcile path exists (`reconcile.py:109,137`), but no test in this package
proves the two views agree — this was previously recorded as blocked on
`bond-coordinator`, which has since landed, so it is now actionable.
*Done when:* a test loads this package's provider the way
`bond-coordinator/scripts/reconcile.py` does (`bond_api.discovery.load_provider`
with `search_paths=[<pkg>/src]`) and asserts the harvested gadget map has 22
entries matching `GADGETS()`, and the brief's codename equals the coordinator
record's `SOLEX`.
*Command:* `uv run pytest tests/test_mission.py -k coordinator -v` (test does
not exist yet)

### Documentation

**None open.** Checked this session: `README.md`, `AGENTS.md`, `docs/README.md`,
`docs/AGENTS.md`, `docs/architecture.md`, `docs/testing_philosophy.md`,
`docs/agent_instructions.md`, `src/README.md`, `tests/README.md`,
`manuscript/README.md`, `STANDALONE.md`. Module counts read "six" everywhere and
match `declarations.DOMAIN_MODULES` (itself gated by
`tests/test_declarations.py:139-146` and `:184-195`); the four figures match the
`FIGURES` registry; `docs/architecture.md:172`'s "currently 22 entries" is held
by `tests/test_mission.py:82`; `docs/_generated/COUNTS.md` matches this
session's measurement exactly (200 tests, 1047 statements, 326 branches,
100.00%). The two documentation problems found are stated wrongly enough to be
defects, not drift, and are filed above as C1 and C2.

### Extension

Genuine future work. Nothing here is a defect.

**E1 — Persist executed outcomes to a provenance store.** `execute` builds a
`Provenance` record inside the protocol object and
`scripts/generate_artifacts.py` writes `output/data/solex_outcome.json`
(asserted at `tests/test_scripts_smoke.py:40-44`), but nothing persists it
anywhere durable. Previously blocked; `bond-utilities` has since shipped the
API — `bond_utilities.mission_io.record_provenance_outcome:153`,
`save_record:92`, `verify_provenance:212`, `hash_payload:45`. Note
`pyproject.toml:19-27` declares only `bond-api` under `[tool.uv.sources]`, so a
`bond-utilities` path dependency must be added first.
*Done when:* a `scripts/` record step writes a validated mission record and a
test asserts the record is byte-identical across two runs for the canonical
inputs (`hash_payload` makes this a one-line comparison), plus a
`verify_provenance` round trip.
*Command:* `uv run pytest tests/test_scripts_smoke.py -v`

**E2 — Annual DNI sweep.** `solar_tracking.field_daily_energy_kwh:206` computes
clear-sky energy for one fixed day of year (`SOLEX_DAY_OF_YEAR = 172`). There is
no seasonal profile, so `SOLAR_FIELD_DAILY_KWH` is a single solstice number
rather than the annual yield curve an operator would want. Needs a
`field_annual_energy_kwh`, a fifth figure (which must be added to
`figures.FIGURES` and referenced by a manuscript section — both directions are
gated at `tests/test_figures.py:80-101`), and tokens for the annual total and
the solstice-to-solstice ratio.

**E3 — Incidence-angle losses.** `solar_concentration.mirror_optical_power:82`
takes `incidence_factor: float = 1.0` and every production call path uses the
default (`field_optical_power:102-105`), so mirror aim geometry contributes
nothing to any reported number. The parameter is unit-tested for linearity and
its zero-guard (`tests/test_solar_concentration.py:45-46,54`) but is never
driven from real heliostat positions. Wiring a per-heliostat cosine loss to
`solar_tracking.sun_position` would make the concentration ratio a function of
time of day rather than a constant. This is the single largest gap between the
model and a defensible heliostat calculation; it is stated as out of scope in
`manuscript/07_scope_and_related_work.md:24-30` rather than hidden.

**E4 — A large seeded lair fixture.** The exact bottleneck solver
(`lair_topology.mirror_gated_bottlenecks`, O(V·(V+E)) by exhaustive removal) is
exercised only on the 7-room canonical lair and the 10-room extended flow
fixture (verified this session). `articulation_points:146` answers a different
question and is tested only on the canonical lair plus three toy graphs
(`tests/test_lair_topology.py:25-29, 67-83`) — on those fixtures the two
answers barely diverge. A deterministic generated fixture at 100+ rooms would
scale-test the exact solver and give a graph where cut vertices and
entry→exit bottlenecks visibly differ, which is the mistake
`AGENTS.md:44-47` warns about.

**E5 — Cross-package scheduling scenario.** The duel and deadline books are
self-contained. A scenario sharing one appointment book across two film
packages would exercise the orchestrator's multi-package path
(`bond-orchestrator/src/bond_orchestrator/missions.py`, `planning.py`). Not
blocked on availability — the orchestrator exists — but it is fleet-level work
whose home is arguably `bond-orchestrator` rather than this package.

## Known limitations (not bugs)

Accepted and out of scope. Recorded so they are not re-litigated.

* **Lumped optical model.** No ray tracing, no atmospheric attenuation between
  mirror and tower, no receiver thermal-loss model, no spillage. The reported
  concentration ratio is a geometric flux ratio at the aperture, not a peak flux
  map. Stated in `manuscript/07_scope_and_related_work.md:24-30`. E3 above is
  the one piece of this deliberately left as future work rather than closed off.
* **Spencer solar position, not Michalsky.** Accurate to ~0.1° in declination,
  which is ample for a daily-energy figure and inadequate for tracker control.
  The higher-accuracy path is deliberately not implemented because nothing
  reported here is sensitive at that resolution
  (`manuscript/07_scope_and_related_work.md:32-38`).
* **Hand-authored lair fixtures.** 7 and 10 rooms; not a facility-security
  product (`manuscript/07_scope_and_related_work.md:40-49`).
* **Perfect-information scheduling.** No arrivals over time, no duration
  uncertainty, no cancellation, no travel time
  (`manuscript/07_scope_and_related_work.md:51-53`).
* **No publishing.** Local-only tree: no remote, no DOI, no archive deposit.
  `.zenodo.json`, `CITATION.cff` and `codemeta.json` omit DOI fields rather than
  carrying placeholders (`AGENTS.md:148-152`).
* **`__init__.py` excluded from coverage** (`pyproject.toml:52-56`). It is 161
  lines of re-exports; the exclusion is why "100.00%" covers eleven modules
  rather than twelve (`docs/_generated/COUNTS.md`).
* **`experiment_plan.yaml`'s `baseline` and `ablation` blocks are free prose and
  deliberately unchecked** (`declarations.py:328-331`). The unknown-top-level-key
  guard means the unchecked surface cannot widen silently — that guard is
  exactly what V4 asks for in the sibling verifier.
* **`review_gates` booleans other than the coverage floor are policy statements,
  not machine-checked facts** — `domain_profile.yaml:11-13` says so explicitly.
  V2 above proposes closing one of them (`zero_mock_tests`); the rest
  (`deterministic`, `git_clean_after_commit`, `no_remote_push`) stay policy.
* **Scope softened by audit:** the audit found `config.yaml`'s claim that
  "every key in this block is verified" was false when only 6 keys were checked.
  It is now true — `verify_declared_experiment` enumerates the leaf keys present
  and raises on any it cannot recompute (`config.yaml:73-82`,
  `declarations.experiment_expectations:211-236`, 14 leaf keys). The honest
  residual scope: this covers the `experiment:` block only. `paper:`, `authors:`,
  `publication:`, `keywords:`, `metadata:` and `gates:` in the same file are not
  recomputed against anything — see V1 and V3 for the two places that matters.

## Verification

Commands that gate this package. All were run this session at commit `49b6b2058`
plus the working-tree TODO change, from the package root.

| Command | Expected |
| --- | --- |
| `uv sync --extra dev` | resolves the `bond-api` path dependency and dev tools |
| `uv run pytest tests/ --cov=src --cov-fail-under=90` | **200 passed**, 0 failures / 0 errors / 0 skips, `TOTAL … 100.00%`, "Required test coverage of 90% reached" |
| `uv run ruff check src/ scripts/` | `All checks passed!` |
| `uv run ruff format --check src/ scripts/` | `23 files already formatted` |
| `uv run mypy src/ scripts/` | `Success: no issues found in 22 source files` |
| `uv run python scripts/00_preflight.py` | exit 0, prints `preflight OK` |
| `uv run python scripts/z_generate_manuscript_variables.py` | exit 0, prints `all manuscript tokens resolved` |
| `rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' --glob '!.venv/**'` | two hits, both documentation explaining the exemplar lineage (`README.md:107`, `docs/AGENTS.md:42`) — see **C1**, the comment at `AGENTS.md:123` says "zero" and is wrong |

Sandbox note: `uv` cannot write its cache under the default sandbox; re-run any
`uv` command with the sandbox disabled if it reports
"Failed to initialize cache at `~/.cache/uv`".

## Round-2 (2026-08-06)

Round-2 improvement pass: hostile self-review of the shipped code plus a
manuscript depth pass. Pre-existing entries above are untouched; this section
records only what this round changed.

### Baseline (round-2 start)

`uv run pytest tests/ --cov=src --cov-fail-under=90` → **200 passed**, 0
failures/errors/skips, 100.00% line and branch on `src/` (1047 statements, 326
branches). `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy
src` all clean.

### Round-2 findings & fixes

**R1 — `mirror_gated_bottlenecks` false-positives on an already-disconnected
entry/exit (correctness bug).** `lair_topology.py` computed a room as a
bottleneck by removing it and re-testing reachability. When the entry cannot
already reach the exit (no escape route), that test is vacuous: every candidate
room's removal "disconnects" an already-disconnected pair, so the function
reported *every* non-trivial room as a bottleneck (e.g. `('B',)` on a graph
`A–B, C` with entry `A`, exit `C`) — exactly the "looks fine but is wrong at
the edges" class.
*Fix:* early-return `()` when `exit_ not in reachable_rooms(graph, entry)`,
with a docstring stating that a maze with no way out has empty bottlenecks.
*Evidence:* `tests/test_lair_topology.py::test_disconnected_entry_exit_has_no_bottlenecks`
(a negative-control regression: asserts the empty set and that
`find_escape_path` returns `None`) and
`test_connected_bottleneck_still_detected` (positive control: `A–X–B` still
reports `X`). Verified by execution: the pre-fix code returned `('B',)`, post-fix
returns `()` while the canonical lair result is unchanged.

**R2 — `verify_domain_profile` fail-open: unchecked `film`/`protocol` blocks and
no unknown-key guard (verification gap; closes TODO V4).** The sibling
`verify_experiment_plan` refuses an unrecognised top-level key, but
`verify_domain_profile` did not: `domain_profile.yaml`'s `film:` and
`protocol:{adapter,contract,gadgets_registry}:` passed entirely unread, and a
new unchecked section could be added silently. `protocol.adapter` names a real
file path that would rot unnoticed if the adapter moved.
*Fix:* added `_DOMAIN_PROFILE_KEYS` (unknown-top-level-key guard), a pure-layer
`FILM_TITLE = "The Man with the Golden Gun (1974)"` constant compared against
`film`, and an existence check on `protocol.adapter`; the returned `checked`
tuple now includes `"film"` and `"protocol.adapter"`.
*Evidence:* four new tamper cases in
`tests/test_declarations.py::test_domain_profile_rejects_a_stale_declaration`
(unknown key → "unverified top-level key", wrong title → "film", non-mapping
`protocol` → "protocol.adapter", missing adapter file → "does not exist") plus
an updated live-profile assertion in
`test_live_domain_profile_matches_the_code`.

**R3 — manuscript: added a live-engine sensitivity analysis (depth pass).**
Before this round the daily yield was reported as a single number with no
analysis of what it depends on. `manuscript_variables.py::generate_variables()`
now emits two parameter-sweep tables computed from live `field_daily_energy_kwh`
calls — clearness factor (0.60/0.75/0.90) and site latitude (0°/8°/23.44°N) —
consumed by new `{{SOLAR_CLEARNESS_SWEEP_ROWS}}` and
`{{SOLAR_LATITUDE_SWEEP_ROWS}}` tokens in `03_results.md` (a new "Sensitivity
and uncertainty of the daily yield" subsection, with an honest uncertainty
paragraph naming the lumped-optical assumptions behind the clearness factor)
and in `08_appendix.md`.
*Evidence:* token gate green after regeneration
(`scripts/z_generate_manuscript_variables.py` → "all manuscript tokens
resolved", 11 sections, zero unresolved); the sweep numbers were cross-checked
against the engine and the latitude narrative corrected in-review (the June
solstice energy rises toward 23.44°N, the sub-solar latitude — not toward the
equator) so the prose matches the computed data.

### Round-2 gate numbers (all run this session)

| Gate | Result |
| --- | --- |
| `pytest tests/ --cov=src --cov-fail-under=90` | **206 passed**, 0 fail / 0 error / 0 skip, 100.00% line + branch (1070 statements, 338 branches) |
| `ruff check src/ scripts/ tests/` | `All checks passed!` |
| `ruff format --check src/ scripts/ tests/` | `37 files already formatted` |
| `mypy src scripts` | `Success: no issues found in 22 source files` / 10 scripts |
| `scripts/z_generate_manuscript_variables.py` | exit 0, 11 sections resolved, no unresolved tokens |
| `scripts/00_preflight.py` | exit 0 |

### Left for a future round

* TODO **C1** (lineage gate comment in `AGENTS.md` still claims "zero" while the
  documented command legitimately returns the two documentation hits) and **C2**
  (fleet-integration prose in `07_scope_and_related_work.md`) remain open —
  deliberately prose/scope, not fixed this round.
* TODO **E2** (annual DNI sweep as a fifth figure), **E3** (per-heliostat
  incidence/cosine loss), **E4** (large seeded lair fixture) remain open
  extensions; the new sensitivity tables are a partial, token-bound answer to
  E2/E3's "the daily number depends on inputs that are not swept" gap but do not
  add a figure or a per-heliostat aim model.
* `docs/_generated/COUNTS.md` was regenerated to 206 / 1070 / 338; future gate
  runs must re-copy from their own output per the file's own instruction.
