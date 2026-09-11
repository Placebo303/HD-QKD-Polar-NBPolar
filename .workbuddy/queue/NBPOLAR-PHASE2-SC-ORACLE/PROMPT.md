# Autonomous execution-session prompt

Work in the current repository root on branch `codex/nbpolar-phase0`.

Execute the complete packet:
`.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/TASK_PACKET.md`.

This is deliberately a heavy autonomous implementation task. Read the frozen
contracts and Phase 1 code, investigate the mathematics, compare plausible SC
architectures, and choose the simplest implementation that satisfies every
oracle and attribution gate. You may write small temporary in-memory probes,
change direction, and refactor your own new Phase 2 files. Record the important
alternatives and why the selected design is correct; do not ask the main thread
to choose routine implementation details.

The fixed boundaries are non-negotiable: GF32/poly37/alpha2, natural-order
row-vector transform, normalized float64 natural-log symbol metrics, classic
source SC that marginalizes undecoded suffix coordinates, actual known symbol
values including zero, and an oracle independent of production SC. Alice truth
must never enter the operational decoder.

You are authorized to implement and run focused synthetic decoder/oracle tests.
You are not authorized to load Model-F/CAL/VAL/TTBin or real data, create a
benchmark/result root, implement SCL/construction/rate adaptation/protocol,
commit/push, or make performance or scientific claims.

Return only `COMPLETE` with an implementation candidate and complete evidence,
or `BLOCKED` with the packet's exact single-blocker return. Do not start Phase 3
and do not accept your own work.

