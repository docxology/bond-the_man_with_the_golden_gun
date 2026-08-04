# Appendix: Generated metric register

This appendix records the resolved values of every manuscript metric at
generation time (`{{GENERATION_TIMESTAMP}}`). The live inventory is produced
by `scripts/z_generate_manuscript_variables.py` into
`output/data/manuscript_variables.json`; the table below lists the
deterministic canonical outputs of the three domain models.

## Solar concentration

| Metric | Value |
| --- | --- |
| Direct normal irradiance | {{SOLEX_DNI}} W/m² |
| Field aperture | {{SOLEX_FIELD_AREA}} m² |
| Receiver aperture | {{SOLEX_RECEIVER_AREA_M2}} m² |
| Optical power | {{SOLEX_OPTICAL_POWER_KW}} kW |
| Thermal heat output | {{SOLEX_HEAT_KW}} kW |
| Concentration ratio | {{SOLEX_CONCENTRATION}}× |

## Lair topology

| Metric | Value |
| --- | --- |
| Rooms | {{LAIR_NUM_ROOMS}} |
| Escape distance | {{LAIR_ESCAPE_DISTANCE}} passages |
| Escape route | {{LAIR_ESCAPE_PATH}} |
| Bottleneck rooms | {{LAIR_BOTTLENECKS}} |
| Articulation points | {{LAIR_NUM_ARTICULATION}} |

## Duel scheduling

| Metric | Value |
| --- | --- |
| Contracts | {{DUEL_NUM_DUELS}} |
| Conflicts | {{DUEL_NUM_CONFLICTS}} |
| Selected | {{DUEL_SELECTED}} |
| Maximum bounty | {{DUEL_TOTAL_BOUNTY}} |

## Environment

| Metric | Value |
| --- | --- |
| Python | {{PYTHON_VERSION}} |
| Timestamp | {{GENERATION_TIMESTAMP}} |
