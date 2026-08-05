# Methodology

## Solar concentration yield

Each mirror $M_i$ contributes optical power $P_i = I \cdot A_i \cdot \rho_i
\cdot c$ where $I$ is the direct normal irradiance, $A_i$ the mirror area,
$\rho_i$ its reflectivity, and $c$ an incidence factor (default 1). The field
optical power is the sum; thermal output multiplies by an optical efficiency
and a heat-transfer efficiency. The dimensionless concentration ratio at a
receiver of area $A_r$ is $C = \sum_i A_i \rho_i / A_r$. Given an area budget,
the highest-yield allocation is greedy: since yield-per-area is exactly
reflectivity, taking mirrors in descending reflectivity is optimal. The
implementation takes whole mirrors — a mirror is skipped when it does not fit
the remaining budget rather than being partially installed — so it is the
integral restriction of the fractional-knapsack greedy, and the budget can end
under-spent. Ties break on larger area first, which fixes the order
deterministically.

The model is deliberately lumped: the chain is
area × reflectivity × incidence × optical efficiency × heat-transfer
efficiency, with no ray tracing, per-heliostat aim geometry, atmospheric
attenuation, or receiver loss model. What it buys is a yield figure that is
exactly reproducible and exactly attributable; what it costs is documented in
[Scope and Related Work](#scope-and-related-work).

## Solar tracking & daily insolation

The daily resource follows the sun geometry. Solar declination $\delta$ and
the equation of time use Spencer's Fourier series [@spencer]. The daylight window
is $D = (2/15)\arccos(-\tan\varphi\tan\delta)$ hours from the sunrise hour
angle. For a fixed site and day the daily extraterrestrial irradiation on a
horizontal plane is the Duffie–Beckman closed form

$$H_0 = \frac{24}{\pi} G_{sc}\left[1 + 0.033\cos\frac{2\pi d}{365}\right]
\left(\cos\varphi\cos\delta\sin\omega_s + \omega_s\sin\varphi\sin\delta\right),$$

with $G_{sc}$ the solar constant and $\omega_s$ the sunrise hour angle in
radians [@duffie_beckman]; a clearness factor $\kappa$ converts it to a
clear-sky resource. The field's daily thermal energy is
$\kappa H_0 \sum_i A_i \rho_i \eta_{opt} \eta_{heat}$.

Elevation follows $\sin e = \sin\varphi\sin\delta + \cos\varphi\cos\delta\cos
H$, clamped to $[-1, 1]$ before the arcsine so a below-horizon sun returns a
non-positive elevation instead of raising. Horizontal beam flux is
$I\sin e$, floored at zero for a sun below the horizon, which is what truncates
the daily profile ([@fig:solex_daily]) to the daylight window rather than
folding negative flux into the integral.

## Lair escape topology

Rooms are nodes and mirror passages are undirected edges of a graph $G$. The
shortest escape route is found by breadth-first search over sorted neighbour
lists, so the route is not merely *a* shortest path but a fixed one. The
canonical lair has {{LAIR_NUM_ROOMS}} rooms and distances are counted in
passages.

Two distinct notions of "critical room" are computed, and they are not
interchangeable. A room is a *bottleneck* between a specific entry and exit if
removing it disconnects those two — computed exactly, by deleting each
candidate room in turn and re-testing reachability. A room is an *articulation
point* (cut vertex) if removing it disconnects any part of the graph at all,
computed in linear time by the Hopcroft–Tarjan depth-first low-link procedure
[@hopcroft_tarjan]. Every entry–exit bottleneck is an articulation point, but
the converse fails: a cut vertex hanging off a side branch splits the graph
without touching the escape route. The exhaustive-removal bottleneck solver is
$O(V(V+E))$, which is the right trade at lair scale and the wrong one at
building scale.

## Lair flow analysis

Escape *redundancy* is quantified by maximum flow on the lair treated as a
unit-capacity network: each undirected mirror passage becomes a pair of
opposed unit-capacity arcs. Edmonds–Karp augments along breadth-first paths
[@edmonds_karp], and by Menger's theorem the resulting flow value is exactly
the number of **edge-disjoint** escape routes — the entry–exit edge
connectivity. The residual graph's source-side reachable set then recovers the
**minimum cut**: the fewest mirror walls whose destruction seals the lair, with
cut value equal to flow value by max-flow min-cut [@ford_fulkerson]. The flow
is decomposed back into explicit routes by walking arcs that carry flow and
decrementing one unit per route, so the reported routes are real paths rather
than an aggregate number.

When mirror passages carry a traversal cost (mirror fragility, guard density),
Dijkstra's algorithm returns the cheapest escape route [@dijkstra]. Costs are
required for every passage — a missing cost raises rather than defaulting to
zero, since a silently free passage would fabricate an escape route.

## Duel / bounty scheduling

Bounty contracts are half-open intervals $[s, e)$ carrying a bounty $w$. Two
overlap iff $s_a < e_b \wedge s_b < e_a$. Two objectives are solved, because
they answer different questions and can disagree on the same book:

* **Maximum bounty** — *weighted interval scheduling* [@kleinberg_tardos]:
  sort by end time, binary-search the latest non-overlapping predecessor
  $p(j)$, and run the dynamic program $D(j)=\max(w_j + D(p(j)), D(j-1))$. Exact
  for arbitrary non-negative bounties.
* **Maximum count** — the earliest-finish greedy: repeatedly take the
  contract that finishes soonest among those still compatible. Exact for the
  count objective and, in general, wrong for the bounty objective.

Reporting only one of these would hide the trade-off the agent is actually
making, so [Results](#results) reports both.

## Deadline bounty scheduling

Unit-time bounty contracts each occupy one slot and must finish by their
deadline; the agent maximises accepted profit. The greedy that processes jobs
in descending profit and assigns each to the latest free slot at or before its
deadline is *exact*, not heuristic: the schedulable sets form a matroid, and
the greedy is optimal over a matroid [@cormen, sec. 16.5]. A path-compressed
disjoint-set structure [@tarjan_unionfind] answers the "latest free slot"
query in near-constant amortised time by merging each occupied slot onto its
left neighbour.

The reported profit and the reported slot assignment come from a single run of
this greedy rather than two independent ones, so the two views cannot
disagree — a divergence that would otherwise be invisible in the manuscript.
