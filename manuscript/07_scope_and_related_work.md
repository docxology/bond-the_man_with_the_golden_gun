# Scope and Related Work

## What this package is

SOLEX is one film package in the PROJECT BOND fleet: a standalone,
deterministic implementation of the technical ideas that *The Man with the
Golden Gun* (1974) actually turns on, exposed through the fleet's frozen
`MissionProvider` protocol [@bond_protocol]. The film supplies the
specification — a solar concentrator whose output is worth killing for, a
mirror-walled funhouse an agent has to get out of, and an assassin who books
contracts one at a time — and the {{NUM_DOMAIN_MODULES}} domain modules supply
the implementation.

The design bet is that a film's premise is a legitimate specification. "How
much heat does a mirror field actually deliver" is a solar-engineering
question with a textbook answer; "which rooms must every escape route pass
through" is a graph question with an exact answer; "which contracts should the
assassin accept" is a scheduling question with two different exact answers
depending on what is being maximised. Building each one honestly is more
interesting than building a stub with a film title on it.

## What this package is not

It is not a heliostat design tool. The optical model is a lumped
area × reflectivity × efficiency chain: there is no ray tracing, no cosine
loss from individual heliostat aim points, no atmospheric attenuation between
mirror and tower, no receiver thermal-loss model, and no spillage. The
concentration ratio reported is a geometric flux ratio at the aperture, not a
peak flux map. A real central-receiver study would need all of these
[@duffie_beckman].

It is not a solar-position library. The Spencer Fourier series [@spencer] is
accurate to roughly a tenth of a degree in declination, which is ample for a
daily-energy figure and inadequate for tracker control. The standard upgrade
is the Astronomical Almanac algorithm [@michalsky]; it is deliberately not
implemented here because nothing in this dossier is sensitive at that
resolution, and implementing an unused higher-accuracy path would be
scaffolding rather than substance.

It is not a facility-security product. The lair graphs are hand-authored
fixtures of {{LAIR_NUM_ROOMS}} and {{LAIR_EXT_NUM_ROOMS}} rooms. The
bottleneck solver is *exact by exhaustive removal* — it deletes each room in
turn and re-tests reachability, which is O(V·(V+E)) and entirely appropriate at
this size, but it is not the algorithm to reach for on a large building. The
linear-time route is the biconnected-components decomposition
[@hopcroft_tarjan], which this package also implements
(`articulation_points`) but uses for a different question: cut vertices of the
whole graph rather than vertices separating a specific entry–exit pair. The
two answers differ, and conflating them would be the easy mistake here.

It is not a workforce scheduler. Both scheduling models assume perfect
information about a small, fixed contract book: no arrivals over time, no
uncertainty in duration, no cancellation, no travel time between targets.

## Relationship to the established literature

Nothing in the domain core is novel; that is the point. Each module is a
faithful implementation of a documented result, which is what makes the
outputs checkable against textbook values rather than against themselves:

| Module | Result implemented | Source |
| --- | --- | --- |
| `solar_concentration` | Lumped optical/thermal chain; fractional-knapsack greedy | [@duffie_beckman] |
| `solar_tracking` | Spencer declination and equation of time; Duffie–Beckman daily insolation closed form | [@spencer; @duffie_beckman] |
| `lair_topology` | BFS shortest path; Hopcroft–Tarjan cut vertices | [@cormen; @hopcroft_tarjan] |
| `lair_flows` | Edmonds–Karp max flow; max-flow min-cut; Dijkstra | [@edmonds_karp; @ford_fulkerson; @dijkstra] |
| `duel_scheduler` | Weighted interval scheduling DP; earliest-finish greedy | [@kleinberg_tardos] |
| `deadline_scheduler` | Unit-time scheduling with deadlines (matroid greedy) with union–find slot lookup | [@cormen; @tarjan_unionfind] |

The contribution, such as it is, lies in the *composition*: six textbook
results wired into a single deterministic mission lifecycle whose every
reported number is injected from the code that produced it, under gates that
fail rather than warn.

## Position in the fleet

SOLEX depends on exactly one fleet package, `bond-api`, and only through a
single adapter module. The {{NUM_DOMAIN_MODULES}} domain modules import
nothing outside the standard library, so the scientific core survives
independently of the protocol. Two integration points remain open and are
tracked in `TODO.md`: persisting executed outcomes to a provenance store once
`bond-utilities` ships, and cross-package missions once the coordinator lands.
Neither requires a change to the domain core.
