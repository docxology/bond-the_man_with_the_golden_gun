# Introduction

The Solex agitator concentrates sunlight from a field of tracking mirrors onto
a central receiver to produce the heat that powers the villain's island. A
field agent cut off from the objective needs three things: an honest model of
how much heat the mirror array can deliver, a reliable route out of the
mirror-lined funhouse lair, and an appointment book that maximises reward
without double-booking a single duel.

This dossier presents the mission software for **{{BOND_CODENAME}}**, the
frozen protocol contract of Project BOND (bond-api). It is organised as three
pure, deterministic domain modules — solar concentration, lair escape
topology, and duel/bounty scheduling — adapted to the shared
`MissionProvider` lifecycle (brief, recon, plan, execute, debrief) through a
thin adapter.

Determinism is a hard constraint: fixed seeds, no untracked random reliance,
and no wall-clock in persisted artifacts. The conventions follow the Project
BOND guardrail preamble documented in the suite-level scratchpads.
