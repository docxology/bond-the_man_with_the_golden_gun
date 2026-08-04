# {{BOND_TITLE}}

**Mission codename: {{BOND_CODENAME}}** — Project BOND film dossier for *The
Man with the Golden Gun* (1974).

## Abstract

This dossier documents the deterministic mission software built for the SOLEX
operation. Six specialist capabilities support the field agent:

1. **Solar concentration yield** — a heliostat-field model that converts a
   mirror array's area and reflectivity into optical power and thermal heat
   output, and allocates a mirror-area budget to the highest-yield mirrors.
2. **Solar tracking & daily insolation** — the sun-geometry layer: declination,
   daylight window, and the Duffie–Beckman clear-sky daily energy the field
   concentrates.
3. **Funhouse lair escape topology** — a graph solver over the villain's
   mirror-lined funhouse, producing a shortest escape route and identifying
   the bottleneck rooms that guard the exit.
4. **Lair flow analysis** — max-flow / min-cut over the lair, returning the
   edge-disjoint escape routes and the minimum mirror walls that seal the
   lair, plus a cost-aware (Dijkstra) cheapest escape.
5. **Assassin duel / bounty scheduling** — an appointment book solved by
   weighted interval scheduling, selecting a non-overlapping set of bounty
   duels that maximises total reward and reporting every scheduling conflict.
6. **Deadline bounty scheduling** — unit-time bounty contracts scheduled by
   the deadline-greedy (union–find) algorithm to maximise accepted profit.

All results are computed from real, deterministic domain models with fixed
seeds and no wall-clock dependence; every metric in this manuscript flows from
code, never from hand-authored prose. The canonical SOLEX field converts a
{{SOLEX_DNI}} W/m² irradiance into a thermal output of {{SOLEX_HEAT_KW}} kW
(concentration {{SOLEX_CONCENTRATION}}×) and, over a clear-sky solstice day at
{{SOLAR_LATITUDE}}°N, concentrates {{SOLAR_FIELD_DAILY_KWH}} kWh. The extended
funhouse has {{LAIR_EXT_EDGE_CONNECTIVITY}} edge-disjoint escape routes (min
cut {{LAIR_EXT_MIN_CUT_EDGES}} mirror walls), the canonical lair is guarded by
{{LAIR_NUM_BOTTLENECKS}} bottleneck rooms, the duel book realises a maximum
bounty of {{DUEL_TOTAL_BOUNTY}}, and the deadline book a maximum profit of
{{DUEL_DEADLINE_MAX_PROFIT}}.
