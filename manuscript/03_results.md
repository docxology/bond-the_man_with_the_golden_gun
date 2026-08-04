# Results

## Solar concentration yield

Under a direct normal irradiance of {{SOLEX_DNI}} W/m², the canonical mirror
field (total aperture {{SOLEX_FIELD_AREA}} m²) delivers
{{SOLEX_OPTICAL_POWER_KW}} kW of optical power to the receiver aperture
({{SOLEX_RECEIVER_AREA_M2}} m²) and, after optical and heat-transfer losses, a
thermal output of **{{SOLEX_HEAT_KW}} kW** at a concentration ratio of
**{{SOLEX_CONCENTRATION}}×**.

![Thermal heat output versus direct normal irradiance for the canonical SOLEX field.](../output/figures/solex_yield.png){#fig:solex_yield}

## Solar tracking & daily insolation

At the canonical site ({{SOLAR_LATITUDE}}°N, day {{SOLAR_DAY_OF_YEAR}}) the
declination is {{SOLAR_DECLINATION}}° and daylight lasts
{{SOLAR_DAYLIGHT_HOURS}} hours. The sun reaches {{SOLAR_NOON_ELEVATION}}° at
solar noon. The daily extraterrestrial insolation on a horizontal plane is
{{SOLAR_EXTRATERRESTRIAL_KWH_M2}} kWh/m²; with a clearness factor this falls
to a clear-sky resource of {{SOLAR_CLEAR_SKY_KWH_M2}} kWh/m², which the field
concentrates into **{{SOLAR_FIELD_DAILY_KWH}} kWh/day** of thermal energy.

![Clear-sky horizontal beam flux across the canonical SOLEX day.](../output/figures/solex_daily.png){#fig:solex_daily}

## Lair escape topology

The funhouse lair comprises {{LAIR_NUM_ROOMS}} rooms. The shortest escape route
from the entry to the vault is:

> {{LAIR_ESCAPE_PATH}}

covering {{LAIR_ESCAPE_DISTANCE}} passages. The {{LAIR_NUM_BOTTLENECKS}} rooms
that every escape route must pass through are **{{LAIR_BOTTLENECKS}}**; the lair
has {{LAIR_NUM_ARTICULATION}} articulation points (single rooms whose removal
disconnects part of the funhouse).

![SOLEX funhouse lair graph with the escape route and bottleneck rooms highlighted.](../output/figures/lair_topology.png){#fig:lair_topology}

## Lair flow analysis

The extended funhouse ({{LAIR_EXT_NUM_ROOMS}} rooms) offers
**{{LAIR_EXT_EDGE_CONNECTIVITY}} edge-disjoint escape routes**; destroying
every passage of any single route still leaves the others open. To seal the
lair the enemy must cut **{{LAIR_EXT_MIN_CUT_EDGES}} mirror walls** (the
minimum entry–exit cut). Under unit traversal costs the cheapest escape route
is

> {{LAIR_EXT_CHEAPEST_PATH}}

at cost {{LAIR_EXT_CHEAPEST_COST}}.

## Duel / bounty scheduling

The appointment book holds {{DUEL_NUM_DUELS}} bounty contracts and contains
{{DUEL_NUM_CONFLICTS}} overlapping pair(s). Weighted interval scheduling selects
the non-overlapping set **{{DUEL_SELECTED}}**, realising a maximum total bounty
of **{{DUEL_TOTAL_BOUNTY}}**.

![SOLEX bounty appointment book with the maximum-bounty selection filled.](../output/figures/duel_schedule.png){#fig:duel_schedule}

## Deadline bounty scheduling

The deadline book holds {{DUEL_DEADLINE_NUM_JOBS}} unit-time bounty contracts.
The deadline greedy (union–find) accepts **{{DUEL_DEADLINE_SELECTED}}**,
realising a maximum profit of **{{DUEL_DEADLINE_MAX_PROFIT}}** with slot
assignment **{{DUEL_DEADLINE_SLOTS}}**.

All six solvers run through the frozen `MissionProvider` lifecycle; the
outcome carries full provenance including a deterministic input hash.
