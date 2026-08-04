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

## Lair escape topology

Rooms are nodes and mirror passages are undirected edges of a graph $G$. The
shortest escape route is found by breadth-first search. A room is a
*bottleneck* between an entry and an exit if removing it disconnects the two,
computed by exact reachability after each removal; the canonical lair has
{{LAIR_NUM_ROOMS}} rooms, distances are in passages, and the set of cut
vertices is reported by Tarjan's algorithm.

## Duel / bounty scheduling

Bounty contracts are half-open intervals $[s, e)$ carrying a bounty $w$. Two
overlap iff $s_a < e_b \wedge s_b < e_a$. The appointment book is solved by
*weighted interval scheduling*: sort by end time, binary-search the latest
non-overlapping predecessor, and run the classic dynamic program
$D(j)=\max(w_j + D(p(j)), D(j-1))$ to maximise total bounty.
