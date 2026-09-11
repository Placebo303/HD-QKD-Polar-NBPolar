# Autonomous Phase 3 execution prompt

Work in the current repository root on branch `codex/nbpolar-phase0` and
execute the complete packet:

`.workbuddy/queue/NBPOLAR-PHASE3-SYNTHETIC-CONSTRUCTION/TASK_PACKET.md`

This is a heavy autonomous research-engineering task. Build q-ary erasure and
QSC synthetic channels, a genie construction engine, analytic/tiny oracles,
disjoint TRAIN/DEV/EVAL handling, and one bounded q=32 N=256 easy-point
evaluation. Explore and compare reasonable construction implementations; use
the accepted Phase 2 SC as the decoder oracle, isolate mismatches, and choose a
simple design supported by evidence.

You may autonomously prototype, revise your design, run synthetic TRAIN/DEV,
and ask an independent reviewer-go subagent to review the frozen EVAL record.
Run EVAL exactly once only after that review passes. Do not ask the main thread
to choose routine implementation details.

Model-F/CAL/VAL/TTBin, real data, protocol/leakage, method adapters, SCL, rate
adaptation, production benchmark roots, commit/push, and broad performance or
scientific claims remain forbidden. End at `IMPLEMENTATION_CANDIDATE` with a
bounded synthetic result or one exact `BLOCKED` root cause. Do not start
Phase 4.

