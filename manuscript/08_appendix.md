# Appendix: Generated metric register

This appendix records the resolved values of every manuscript metric at
generation time (`{{GENERATION_TIMESTAMP}}`). The live inventory is produced by
`scripts/z_generate_manuscript_variables.py` into
`output/data/manuscript_variables.json`; the tables below list the
deterministic canonical outputs of the {{NUM_DOMAIN_MODULES}} domain models.
Nothing here is transcribed by hand — every cell is the same placeholder
mechanism used in the body sections, so the register cannot drift from the
prose that cites it.

## Solar concentration

| Metric | Value |
| --- | --- |
| Direct normal irradiance | {{SOLEX_DNI}} W/m² |
| Field aperture | {{SOLEX_FIELD_AREA}} m² |
| Receiver aperture | {{SOLEX_RECEIVER_AREA_M2}} m² |
| Optical power | {{SOLEX_OPTICAL_POWER_KW}} kW |
| Thermal heat output | {{SOLEX_HEAT_KW}} kW |
| Concentration ratio | {{SOLEX_CONCENTRATION}}× |
| Mirrors in field | {{SOLEX_NUM_MIRRORS}} |
| Allocation budget | {{SOLEX_BUDGET_M2}} m² |
| Allocation selection | {{SOLEX_BUDGET_SELECTION}} |

## Solar tracking & daily insolation

| Metric | Value |
| --- | --- |
| Latitude | {{SOLAR_LATITUDE}}°N |
| Day of year | {{SOLAR_DAY_OF_YEAR}} |
| Declination | {{SOLAR_DECLINATION}}° |
| Noon elevation | {{SOLAR_NOON_ELEVATION}}° |
| Daylight | {{SOLAR_DAYLIGHT_HOURS}} hours |
| Extraterrestrial insolation | {{SOLAR_EXTRATERRESTRIAL_KWH_M2}} kWh/m² |
| Clear-sky insolation | {{SOLAR_CLEAR_SKY_KWH_M2}} kWh/m² |
| Field daily energy | {{SOLAR_FIELD_DAILY_KWH}} kWh |

Sensitivity — clearness factor (kWh/m²/day, kWh/day):

| Clearness | Clear-sky insolation (kWh/m²/day) | Field daily energy (kWh/day) |
| --- | --- | --- |
{{SOLAR_CLEARNESS_SWEEP_ROWS}}

Sensitivity — site latitude (deg N, kWh/day):

| Latitude (deg N) | Field daily energy (kWh/day) |
| --- | --- |
{{SOLAR_LATITUDE_SWEEP_ROWS}}

## Lair topology (canonical)

| Metric | Value |
| --- | --- |
| Rooms | {{LAIR_NUM_ROOMS}} |
| Escape distance | {{LAIR_ESCAPE_DISTANCE}} passages |
| Escape route | {{LAIR_ESCAPE_PATH}} |
| Bottleneck rooms | {{LAIR_BOTTLENECKS}} |
| Articulation points | {{LAIR_NUM_ARTICULATION}} |

## Lair flow (extended)

| Metric | Value |
| --- | --- |
| Rooms | {{LAIR_EXT_NUM_ROOMS}} |
| Edge connectivity | {{LAIR_EXT_EDGE_CONNECTIVITY}} |
| Min-cut wall count | {{LAIR_EXT_MIN_CUT_EDGES}} |
| Min-cut walls | {{LAIR_EXT_MIN_CUT_WALLS}} |
| Cheapest escape cost | {{LAIR_EXT_CHEAPEST_COST}} |
| Cheapest escape route | {{LAIR_EXT_CHEAPEST_PATH}} |

## Duel interval scheduling

| Metric | Value |
| --- | --- |
| Contracts | {{DUEL_NUM_DUELS}} |
| Conflicts | {{DUEL_NUM_CONFLICTS}} |
| Max-bounty selection | {{DUEL_SELECTED}} ({{DUEL_NUM_SELECTED}}) |
| Maximum bounty | {{DUEL_TOTAL_BOUNTY}} |
| Earliest-finish selection | {{DUEL_EARLIEST_FINISH}} ({{DUEL_NUM_EARLIEST_FINISH}}) |
| Earliest-finish bounty | {{DUEL_EARLIEST_FINISH_BOUNTY}} |

## Deadline scheduling

| Metric | Value |
| --- | --- |
| Jobs | {{DUEL_DEADLINE_NUM_JOBS}} |
| Selected | {{DUEL_DEADLINE_SELECTED}} |
| Maximum profit | {{DUEL_DEADLINE_MAX_PROFIT}} |
| Slot assignment | {{DUEL_DEADLINE_SLOTS}} |

## Environment and gates

| Metric | Value |
| --- | --- |
| Package version | {{PACKAGE_VERSION}} |
| Mission seed | {{MISSION_SEED}} |
| Domain modules | {{NUM_DOMAIN_MODULES}} |
| Figures | {{NUM_FIGURES}} |
| Coverage gate | {{COVERAGE_GATE_PCT}}% line + branch on `src/` |
| Python | {{PYTHON_VERSION}} |
| Timestamp | {{GENERATION_TIMESTAMP}} |
