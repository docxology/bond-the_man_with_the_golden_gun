# Methodology

## Solar concentration yield

Each mirror $M_i$ contributes optical power $P_i = I \cdot A_i \cdot \rho_i
\cdot c$ where $I$ is the direct normal irradiance, $A_i$ the mirror area,
$\rho_i$ its reflectivity, and $c$ an incidence factor (default 1). The field
optical power is the sum; thermal output multiplies by an optical efficiency
and a heat-transfer efficiency. The dimensionless concentration ratio at a
receiver of area $A_r$ is $C = \sum_i A_i \rho_i / A_r$. Given an area budget,
the highest-yield allocation is greedy: since yield-per-area is exactly
reflectivity, taking mirrors in descending reflectivity is optimal.

## Solar tracking & daily insolation

The daily resource follows the sun geometry. Solar declination $\delta$ and
the equation of time use Spencer's (1971) Fourier series. The daylight window
is $D = (2/15)\arccos(-\tan\varphi\tan\delta)$ hours from the sunrise hour
angle. For a fixed site and day the daily extraterrestrial irradiation on a
horizontal plane is the Duffie–Beckman closed form

$$H_0 = \frac{24}{\pi} G_{sc}\left[1 + 0.033\cos\frac{2\pi d}{365}\right]
\left(\cos\varphi\cos\delta\sin\omega_s + \omega_s\sin\varphi\sin\delta\right),$$

with $G_{sc}$ the solar constant and $\omega_s$ the sunrise hour angle in
radians; a clearness factor $\kappa$ converts it to a clear-sky resource. The
field's daily thermal energy is $\kappa H_0 \sum_i A_i \rho_i \eta_{opt}
\eta_{heat}$.

## Lair escape topology

Rooms are nodes and mirror passages are undirected edges of a graph $G$. The
shortest escape route is found by breadth-first search. A room is a
*bottleneck* between an entry and an exit if removing it disconnects the two,
computed by exact reachability after each removal; the canonical lair has
{{LAIR_NUM_ROOMS}} rooms, distances are in passages, and the set of cut
vertices is reported by Tarjan's algorithm.

## Lair flow analysis

Escape *redundancy* is quantified by max flow on the lair treated as a
unit-capacity network (each passage one mirror wall). The Edmonds–Karp
algorithm gives the number of **edge-disjoint** escape routes — the
entry–exit edge connectivity — and the residual graph's reachable set recovers
the **minimum cut**: the fewest mirror walls whose destruction seals the lair
(Cormen et al. 2009). When mirror passages carry a traversal cost (fragility,
guard density), Dijkstra's algorithm returns the cheapest escape route.

## Duel / bounty scheduling

Bounty contracts are half-open intervals $[s, e)$ carrying a bounty $w$. Two
overlap iff $s_a < e_b \wedge s_b < e_a$. The appointment book is solved by
*weighted interval scheduling*: sort by end time, binary-search the latest
non-overlapping predecessor, and run the classic dynamic program
$D(j)=\max(w_j + D(p(j)), D(j-1))$ to maximise total bounty.

## Deadline bounty scheduling

Unit-time bounty contracts each occupy one slot and must finish by their
deadline; the agent maximises accepted profit. The exact greedy processes
jobs in descending profit and assigns each to the latest free slot at or
before its deadline; a disjoint-set (union–find) structure answers the
"latest free slot" query with path compression (Kleinberg & Tardos 2006;
Cormen et al. 2009, ch. 16).
