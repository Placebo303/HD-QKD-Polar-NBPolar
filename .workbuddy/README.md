# NB-Polar WorkBuddy queue

This directory is the handoff surface for long implementation sessions. Every
work item is a directory under `queue/` containing:

- `TASK_PACKET.md`: complete scope, requirements, tests, gates, and return
  contract;
- `PROMPT.md`: directly usable execution-session prompt;
- `AUTHORIZATION_PROMPT.md`: copy-paste command that grants the packet's exact
  bounded authorization to another session when present;
- `STATUS.yaml`: compact lifecycle state.

The main thread owns mathematical choices, acceptance, and scientific claims.
The execution session implements one packet at a time and returns either
`COMPLETE` with the frozen evidence or `BLOCKED` with one concrete blocker.
It must not widen scope or unlock the next packet itself.

The durable sequence and responsibility split are defined in
`docs/nbpolar/WORKBUDDY_LIFECYCLE.md`. At an authorization gate, the main
thread provides both the file links and the complete copyable authorization
message in chat.

Packets are intentionally milestone-sized. A new packet is issued only after
the previous packet's implementation and focused evidence have been reviewed.
This keeps transform, decoder, prior, construction, and protocol failures
separable.

Current queue:

1. `queue/NBPOLAR-PHASE1-GF32-TRANSFORM/` — implementation accepted.
2. `queue/NBPOLAR-PHASE2-SC-ORACLE/` — implementation accepted.
3. `queue/NBPOLAR-PHASE3-SYNTHETIC-CONSTRUCTION/` — blocked; diagnostic retained.
4. `queue/NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY/` — EVAL accepted as a bounded synthetic diagnostic; seed/root frozen.
5. `queue/NBPOLAR-PHASE4-P0-PRIOR-CONTRACT-FREEZE/` — FREEZE_ACCEPT.
6. `queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/` — IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY; 66/66 + independent 11/11; P2 closed.
7. `queue/NBPOLAR-PHASE4-P2-CAL-DEV/` — prepared by P1, all-false and not authorized.
8. `queue/NBPOLAR-PHASE4-P2-R1-DIAGNOSTIC-INDEX-RECOVERY/` — accepted bounded CAL prior-table recovery; both artifact attempts consumed.
9. `queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/` — heavy autonomous model-sampled empirical-prior SC/interface exploration; prepared, not authorized.

Planned and not yet authorized: Phase 4-P2 defines the CAL/DEV evidence slice.
CAL/data and decoder work remain closed until its contract is reviewed and
explicitly authorized.
