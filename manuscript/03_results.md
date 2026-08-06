# Results

## Solar concentration yield

Under a direct normal irradiance of {{SOLEX_DNI}} W/m², the canonical mirror
field (total aperture {{SOLEX_FIELD_AREA}} m²) delivers
{{SOLEX_OPTICAL_POWER_KW}} kW of optical power to the receiver aperture
({{SOLEX_RECEIVER_AREA_M2}} m²) and, after optical and heat-transfer losses, a
thermal output of **{{SOLEX_HEAT_KW}} kW** at a concentration ratio of
**{{SOLEX_CONCENTRATION}}×**.

![Thermal heat output versus direct normal irradiance for the canonical SOLEX field.](../output/figures/solex_yield.png){#fig:solex_yield}

Offered the same {{SOLEX_NUM_MIRRORS}} mirrors under an area budget of
{{SOLEX_BUDGET_M2}} m², the greedy allocator installs
**{{SOLEX_BUDGET_SELECTION}}**. The selection is instructive: after taking the
two highest-reflectivity mirrors the remaining budget is too small for the next
two candidates, so the allocator falls through to the smallest, lowest-quality
mirror rather than leaving the budget idle. Whole mirrors cannot be split, so
the budget finishes under-spent — the integral restriction of the fractional
optimum, not a failure of the greedy.

## Solar tracking & daily insolation

At the canonical site ({{SOLAR_LATITUDE}}°N, day {{SOLAR_DAY_OF_YEAR}}) the
declination is {{SOLAR_DECLINATION}}° and daylight lasts
{{SOLAR_DAYLIGHT_HOURS}} hours. The sun reaches {{SOLAR_NOON_ELEVATION}}° at
solar noon. The daily extraterrestrial insolation on a horizontal plane is
{{SOLAR_EXTRATERRESTRIAL_KWH_M2}} kWh/m²; with a clearness factor this falls
to a clear-sky resource of {{SOLAR_CLEAR_SKY_KWH_M2}} kWh/m², which the field
concentrates into **{{SOLAR_FIELD_DAILY_KWH}} kWh/day** of thermal energy.

![Clear-sky horizontal beam flux across the canonical SOLEX day.](../output/figures/solex_daily.png){#fig:solex_daily}

### Sensitivity and uncertainty of the daily yield

The headline daily figure ({{SOLAR_FIELD_DAILY_KWH}} kWh) is a single point on
two continua, and reading it as a point obscures how much of the number is the
model's two free inputs — the clearness factor and the site latitude:

| Clearness $\kappa$ | Clear-sky insolation (kWh/m²/day) | Field daily energy (kWh/day) |
| --- | --- | --- |
{{SOLAR_CLEARNESS_SWEEP_ROWS}}

The clearness factor is the single largest source of uncertainty in the daily
number: it is a bulk sunshine-availability parameter, not a measured quantity
for any particular island day, and the deliberately unmodelled physics (real
circumsolar attenuation, receiver thermal loss, mirror soiling) all live
behind it. That is why the mission *reports* the clear-sky number only at the
canonical clearness factor, never as a forecast.

Holding clearness fixed and moving the site latitude shifts the overhead sun:

| Latitude (deg N) | Field daily energy (kWh/day) |
| --- | --- |
{{SOLAR_LATITUDE_SWEEP_ROWS}}

At the June solstice the sun stands directly over the Tropic of Cancer
(23.44°N), so moving the field north from the equator toward that latitude
raises the solstice noon elevation and, with it, the concentrated daily
energy; the maximum over this band is the 23.44°N row, where the sun is
overhead at noon. The canonical island ({{SOLAR_LATITUDE}}°N) is south of
that maximum and therefore delivers less than its northernmost placement — a
site-sensitivity the headline single number cannot show. Both sweeps are live
engine output — the same `field_daily_energy_kwh` call the Results section
uses, evaluated over a parameter grid — so they cannot drift from the model
that produced the headline number.

## Lair escape topology

The funhouse lair comprises {{LAIR_NUM_ROOMS}} rooms. The shortest escape route
from the entry to the vault is:

> {{LAIR_ESCAPE_PATH}}

covering {{LAIR_ESCAPE_DISTANCE}} passages. The {{LAIR_NUM_BOTTLENECKS}} rooms
that every escape route must pass through are **{{LAIR_BOTTLENECKS}}**; the lair
has {{LAIR_NUM_ARTICULATION}} articulation points (single rooms whose removal
disconnects part of the funhouse).

The two counts differ, and the difference is the point. Articulation points
include rooms on the dead-end side branch, whose loss splits the funhouse
without touching the route to the vault; the bottleneck set is strictly the
rooms that stand between the entry and the exit. A defender garrisoning
articulation points would spend part of the effort guarding rooms the escaping
agent never enters.

![SOLEX funhouse lair graph with the escape route and bottleneck rooms highlighted.](../output/figures/lair_topology.png){#fig:lair_topology}

## Lair flow analysis

The extended funhouse ({{LAIR_EXT_NUM_ROOMS}} rooms) offers
**{{LAIR_EXT_EDGE_CONNECTIVITY}} edge-disjoint escape routes**; destroying
every passage of any single route still leaves the others open. To seal the
lair the enemy must cut **{{LAIR_EXT_MIN_CUT_EDGES}} mirror walls** (the
minimum entry–exit cut), namely **{{LAIR_EXT_MIN_CUT_WALLS}}**. Cut value
equals flow value, as max-flow min-cut requires; the cheapest seal is at the
entry side, where the three corridors have not yet diverged. Under unit
traversal costs the cheapest escape route is

> {{LAIR_EXT_CHEAPEST_PATH}}

at cost {{LAIR_EXT_CHEAPEST_COST}}.

## Duel / bounty scheduling

The appointment book holds {{DUEL_NUM_DUELS}} bounty contracts and contains
{{DUEL_NUM_CONFLICTS}} overlapping pair(s). Weighted interval scheduling selects
the non-overlapping set **{{DUEL_SELECTED}}**, realising a maximum total bounty
of **{{DUEL_TOTAL_BOUNTY}}**.

The count-maximising earliest-finish greedy instead selects
**{{DUEL_EARLIEST_FINISH}}**: {{DUEL_NUM_EARLIEST_FINISH}} contracts worth
{{DUEL_EARLIEST_FINISH_BOUNTY}}, against the dynamic program's
{{DUEL_NUM_SELECTED}} contracts worth {{DUEL_TOTAL_BOUNTY}}. Both schedules are
optimal for their own objective, and the disagreement is exactly the trade-off
the agent faces: booking the earliest-finishing contract first forfeits the
more valuable contract that overlaps it. Choosing the greedy because it is
simpler would cost bounty here, which is why the exact dynamic program is the
solver wired into the mission outcome.

![SOLEX bounty appointment book with the maximum-bounty selection filled.](../output/figures/duel_schedule.png){#fig:duel_schedule}

## Deadline bounty scheduling

The deadline book holds {{DUEL_DEADLINE_NUM_JOBS}} unit-time bounty contracts.
The deadline greedy (union–find) accepts **{{DUEL_DEADLINE_SELECTED}}**,
realising a maximum profit of **{{DUEL_DEADLINE_MAX_PROFIT}}** with slot
assignment **{{DUEL_DEADLINE_SLOTS}}**.

All six solvers run through the frozen `MissionProvider` lifecycle; the
outcome carries full provenance including a deterministic input hash.
