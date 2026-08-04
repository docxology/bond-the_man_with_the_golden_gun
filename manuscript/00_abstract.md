# {{BOND_TITLE}}

**Mission codename: {{BOND_CODENAME}}** — Project BOND film dossier for *The
Man with the Golden Gun* (1974).

## Abstract

This dossier documents the deterministic mission software built for the SOLEX
operation. Three specialist capabilities support the field agent:

1. **Solar concentration yield** — a heliostat-field model that converts a
   mirror array's area and reflectivity into optical power and thermal heat
   output, and allocates a mirror-area budget to the highest-yield mirrors.
2. **Funhouse lair escape topology** — a graph solver over the villain's
   mirror-lined funhouse, producing a shortest escape route and identifying
   the bottleneck rooms that guard the exit.
3. **Assassin duel / bounty scheduling** — an appointment book solved by
   weighted interval scheduling, selecting a non-overlapping set of bounty
   duels that maximises total reward and reporting every scheduling conflict.

All results are computed from real, deterministic domain models with fixed
seeds and no wall-clock dependence; every metric in this manuscript flows from
code, never from hand-authored prose. The canonical SOLEX field converts a
{{SOLEX_DNI}} W/m² irradiance into a thermal output of {{SOLEX_HEAT_KW}} kW at a
concentration ratio of {{SOLEX_CONCENTRATION}}×, the lair has a
{{LAIR_ESCAPE_DISTANCE}}-passage shortest escape route guarded by
{{LAIR_NUM_BOTTLENECKS}} bottleneck rooms, and the duel book realises a maximum
bounty of {{DUEL_TOTAL_BOUNTY}} from {{DUEL_NUM_DUELS}} contracts.
