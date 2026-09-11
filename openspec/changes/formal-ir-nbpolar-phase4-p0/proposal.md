# Phase 4-P0 prior-contract freeze — proposal

## Status

`PLAN_CANDIDATE / IMPLEMENTATION_NOT_AUTHORIZED / EXECUTE_NOT_AUTHORIZED`.
Companion packet: `.workbuddy/queue/NBPOLAR-PHASE4-P0-PRIOR-CONTRACT-FREEZE/TASK_PACKET.md`
(`PLAN_READY_AWAITING_EXPLICIT_AUTHORIZATION`; authorized for read-only
audit + document freeze only per its `STATUS.yaml`).

## Problem

Model-F statistics arrive with several historical smoothing formulas, axis
layouts, and packing names, while the Phase 1–3 q-ary Polar stack consumes
only explicit normalized `(N,q)` log metrics with no Alice truth. Without a
frozen boundary, an axis transpose, a per-cell pseudocount, a silently
dropped Bob component, or a truth-leaking L2 path would be undetectable
before the first q-ary SC call.

## Proposal

Freeze the Model-F → GF32 prior contract as documents and an OpenSpec delta
only: accepted per-Bob-column concentration formula, exact axis/provenance
table with the per-cell competitor banned by callable/path, 5+5 symbol
contract, minimal `SymbolMetric` API, CAL/DEV/EVAL separation with three
diagnostics (L1 / oracle-L2 / candidate-L2), a 12-gate validation matrix,
three-way design alternative with one MVP selection, and an unauthorized
Phase 4-P1 implementation packet. No `.py` is added or modified; no CAL
data, Model-F execution, decoder, benchmark, or EVAL runs.

## Scope

- Read-only audit of Phase 1–3 `formal_ir/nbpolar/` code/tests, accepted
  Phase 3-R1 artifacts, Model-F builders/consumers, and D7 belief-provenance
  findings (all inside this worktree's `comparison_bench/`).
- New OpenSpec change `formal-ir-nbpolar-phase4-p0` (proposal/design/tasks/
  spec delta); additive freeze records in the P0 packet dir and one new
  `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`.
- Prepared-but-unauthorized Phase 4-P1 packet under
  `.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/`.

Out of scope: any `.py` implementation, CAL/TTBin reads, Model-F/decoder/
benchmark/EVAL execution, Phase 1–3 or frozen-artifact modification,
reconciliation/SCL/rate adaptation, commit/push, and any scientific or
performance claim (including reuse of `7.162347` outside its CAL domain).

## Source of truth

`docs/nbpolar/ARCHITECTURE.md` (prior contract), `docs/nbpolar/ROADMAP.md`
Phase 4 gate, `docs/nbpolar/VALIDATION_GATES.md`, the P0 `TASK_PACKET.md`
acceptance matrix (P0-1–P0-6), and this change's `design.md`/`specs/`.
This proposal authorizes no execution.
