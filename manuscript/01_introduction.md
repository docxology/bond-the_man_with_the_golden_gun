# Introduction

The Solex agitator concentrates sunlight from a field of tracking mirrors onto
a central receiver to produce the heat that powers the villain's island. A
field agent working against it needs answers to three concrete questions, and
each of them turns out to be a well-posed computational problem.

*How much heat can that array actually deliver?* This is a heliostat yield
question — aperture, reflectivity, and efficiency give the instantaneous
figure, and the sun's geometry over the day gives the energy figure. Both are
standard solar engineering [@duffie_beckman], and both are worth computing
rather than guessing, because the answer decides whether the installation is a
curiosity or a strategic asset.

*How does an agent get out of the mirror-lined funhouse — and how would the
enemy seal it?* This is a graph question with two distinct answers. The route
out is a shortest path; the rooms that *every* route must cross are the
bottlenecks, the single points of failure the defenders will garrison. Escape
redundancy is a flow question: the number of edge-disjoint routes is exactly
the entry–exit maximum flow, and the fewest mirror walls that seal the lair is
the matching minimum cut [@ford_fulkerson; @edmonds_karp].

*Which contracts should the assassin — or the agent tracking him — expect to be
taken?* This is scheduling, and the answer depends sharply on the objective.
Maximising the *number* of contracts is the earliest-finish greedy; maximising
their total *bounty* is weighted interval scheduling [@kleinberg_tardos], and
on a well-chosen book the two disagree. A separate deadline book, where each
contract occupies one slot and expires, is the unit-time deadline problem
solved exactly by a matroid greedy [@cormen].

This dossier presents the mission software for **{{BOND_CODENAME}}**:
{{NUM_DOMAIN_MODULES}} pure, deterministic domain modules
(`{{DOMAIN_MODULE_LIST}}`) adapted to the frozen PROJECT BOND
`MissionProvider` lifecycle — brief, recon, plan, execute, debrief
[@bond_protocol] — through a single thin adapter. The domain modules import
nothing outside the Python standard library and never import the protocol, so
the scientific core stands alone; the adapter is the only place the fleet
contract appears.

Determinism is a hard constraint rather than an aspiration: fixed inputs, no
random draws, sorted iteration in every graph traversal, and no wall-clock read
in any persisted artifact. Equally hard is the rule that no metric is typed by
hand — every number in [Results](#results) arrives as a placeholder resolved
from the code that computed it, under a gate that fails the build when prose
and code disagree.
