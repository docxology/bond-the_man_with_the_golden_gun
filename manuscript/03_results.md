# Results

## Solar concentration yield

Under a direct normal irradiance of {{SOLEX_DNI}} W/m², the canonical mirror
field (total aperture {{SOLEX_FIELD_AREA}} m²) delivers
{{SOLEX_OPTICAL_POWER_KW}} kW of optical power to the receiver aperture
({{SOLEX_RECEIVER_AREA_M2}} m²) and, after optical and heat-transfer losses, a
thermal output of **{{SOLEX_HEAT_KW}} kW** at a concentration ratio of
**{{SOLEX_CONCENTRATION}}×**.

![Thermal heat output versus direct normal irradiance for the canonical SOLEX field.](../output/figures/solex_yield.png){#fig:solex_yield}

## Lair escape topology

The funhouse lair comprises {{LAIR_NUM_ROOMS}} rooms. The shortest escape route
from the entry to the vault is:

> {{LAIR_ESCAPE_PATH}}

covering {{LAIR_ESCAPE_DISTANCE}} passages. The {{LAIR_NUM_BOTTLENECKS}} rooms
that every escape route must pass through are **{{LAIR_BOTTLENECKS}}**; the lair
has {{LAIR_NUM_ARTICULATION}} articulation points (single rooms whose removal
disconnects part of the funhouse).

![SOLEX funhouse lair graph with the escape route and bottleneck rooms highlighted.](../output/figures/lair_topology.png){#fig:lair_topology}

## Duel / bounty scheduling

The appointment book holds {{DUEL_NUM_DUELS}} bounty contracts and contains
{{DUEL_NUM_CONFLICTS}} overlapping pair(s). Weighted interval scheduling selects
the non-overlapping set **{{DUEL_SELECTED}}**, realising a maximum total bounty
of **{{DUEL_TOTAL_BOUNTY}}**.

![SOLEX bounty appointment book with the maximum-bounty selection filled.](../output/figures/duel_schedule.png){#fig:duel_schedule}

All three solvers run through the frozen `MissionProvider` lifecycle; the
outcome carries full provenance including a deterministic input hash.
