# Experimental Setup

This section fixes every input the results depend on. Nothing in the SOLEX
package is sampled, fitted, or drawn from an external service: each model is
evaluated on a canonical fixture defined in code, and the fixture is restated
in `manuscript/config.yaml` where it is verified against the code at token
generation time (see [Reproducibility](#reproducibility)).

## Software environment

| Item | Value |
| --- | --- |
| Package | `the_man_with_the_golden_gun` v{{PACKAGE_VERSION}} |
| Mission codename | {{BOND_CODENAME}} |
| Python | {{PYTHON_VERSION}} |
| Domain modules | {{NUM_DOMAIN_MODULES}} (`{{DOMAIN_MODULE_LIST}}`) |
| Third-party runtime dependencies | `numpy`, `matplotlib`, `pyyaml`, `bond-api` |
| Deterministic seed | {{MISSION_SEED}} |
| Figures | {{NUM_FIGURES}} |

`numpy` is used only to build the irradiance sweep grid for
[@fig:solex_yield]; `matplotlib` only to render figures; `pyyaml` only to read
`config.yaml`. Every quantitative result in [Results](#results) is computed
with the Python standard library.

## Heliostat field

The canonical SOLEX field is {{SOLEX_NUM_MIRRORS}} tracking mirrors totalling
{{SOLEX_FIELD_AREA}} m² of aperture, each with a fixed area and specular
reflectivity:

| Mirror | Area (m²) | Reflectivity |
| --- | --- | --- |
{{SOLEX_MIRROR_ROWS}}

The receiver aperture is {{SOLEX_RECEIVER_AREA_M2}} m². Optical efficiency
(receiver intercept) is 0.90 and heat-transfer efficiency is 0.85; both are
module defaults and are swept by no experiment here. The direct normal
irradiance used for the headline yield is {{SOLEX_DNI}} W/m².

The mirror-budget allocation experiment offers the same
{{SOLEX_NUM_MIRRORS}}-mirror candidate set under an area budget of
{{SOLEX_BUDGET_M2}} m² — deliberately smaller than the field, so the greedy
allocator must actually choose.

## Solar site and day

| Parameter | Value |
| --- | --- |
| Latitude | {{SOLAR_LATITUDE}}°N |
| Day of year | {{SOLAR_DAY_OF_YEAR}} (northern solstice) |
| Solar constant | 1361 W/m² |
| Clearness factor | 0.75 |
| Peak DNI | {{SOLEX_DNI}} W/m² |

The site stands in for the villain's island: a low northern latitude where the
solstice sun passes close to the zenith. The daily beam-flux profile
([@fig:solex_daily]) is sampled at 10-minute steps in solar time and truncated
to elevations above the horizon.

## Funhouse lair fixtures

Two graph fixtures are used, and they answer different questions.

The **canonical lair** ({{LAIR_NUM_ROOMS}} rooms) is a mostly linear funhouse
with one dead-end branch. It is the fixture for escape routing and bottleneck
analysis, because a chain of forced rooms is exactly what makes the bottleneck
question interesting.

The **extended lair** ({{LAIR_EXT_NUM_ROOMS}} rooms) adds two parallel
corridors from the entry to the vault plus a dead-end wine cellar. It is the
fixture for flow analysis, because a lair with only one route has a trivial max
flow; three parallel routes give the Edmonds–Karp decomposition and the minimum
cut something to separate. Every passage carries unit capacity (one mirror
wall) and, for the cost-aware escape, unit traversal cost.

## Bounty contract books

The **duel book** holds {{DUEL_NUM_DUELS}} contracts as half-open intervals
`[start, end)` with a bounty:

| Contract | Interval | Bounty | Target |
| --- | --- | --- | --- |
{{DUEL_BOOK_ROWS}}

The book is constructed so the greedy count-maximising answer and the
bounty-maximising answer differ — that divergence is the point of running both
solvers in [Results](#results).

The **deadline book** holds {{DUEL_DEADLINE_NUM_JOBS}} unit-time contracts,
each with an integer deadline slot and a profit:

| Contract | Deadline | Profit |
| --- | --- | --- |
{{DUEL_DEADLINE_BOOK_ROWS}}

Total demand ({{DUEL_DEADLINE_NUM_JOBS}} contracts) exceeds the
{{DUEL_DEADLINE_NUM_SLOTS}} available slots, so the scheduler must reject work;
a book that fit entirely would make the greedy vacuous.
