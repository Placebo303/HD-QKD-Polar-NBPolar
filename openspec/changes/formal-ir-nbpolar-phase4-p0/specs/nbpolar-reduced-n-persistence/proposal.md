# Proposal — N=8192 persistence probe on the 2M HOLD tail (SCOPING ONLY)

- Status: `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`. Scoping proposal only.
  Companion design: `design.md`; delta spec: `spec.md`; tasks: umbrella
  `tasks.md` reduced-N section. Packet skeleton (no authorization):
  `.workbuddy/queue/NBPOLAR-REDUCED-N-PERSISTENCE/`.
- Parent analyses: `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md`
  (feasibility study, main-thread decision basis) and
  `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-PHASE-PLAN.md` (option (iv)).

## Problem

The N=32768 real-data ladder is exhausted under the authorized rules (0
full blocks remain; D1-A spent the single authorized merge on P20S; R1
accepted descriptively). The only remaining high-information population
is the 2M HOLD tail 3595..3644 (50 frames / 12,800 pairs) — insufficient
for N=32768 but exactly sufficient for ONE N=8192 block (32 frames) with
an 18-frame remainder. The open question is whether the L2-spike failure
mechanism (first-error at a local-hazard spike; spike-order coverage)
persists off the N=32768 point — a qualitative, descriptive-only
persistence check that the zero-cost archive (option (iii)) cannot
answer once its named trigger question is written.

## Proposal

Scope (not yet authorize) a single-block N=8192 persistence probe on 2M
HOLD frames 3595..3626 with three arms (newly derived N=8192
frozen-order-equivalent anchor α1; spike-local order at identical K;
true-L1 oracle diagnostic), P20Q-identical IR-1..IR-4 plus N=8192-sized
uncapped IR-5, full P16-scale re-derivation (construction/allocation, K
via the frozen budget formula with 2M H, fresh L1/L2/spike orders, new
tag domain), within-N paired judgment on Q-G1/Q-G2 only, and the full
Tier-Y gate sequence — each gate requiring its own future explicit
authorization.

## Scope

- In scope of THIS scoping: the delta spec (`spec.md`), this proposal,
  the freeze design (`design.md`), the appended task list (umbrella
  `tasks.md`, clearly marked, append-only), and the packet skeleton
  (`STATUS.yaml` + `SCOPING_NOTES.md`, state
  `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`, all counters 0).
- Out of scope (explicitly NOT authorized by this scoping): any `.py`
  implementation; any construction/order/K derivation or recompute; any
  protected open (pairs parquet, counts NPZ, prior/alt content — not
  even stat); any decoder/RNG/tag execution; any DEV/HOLD contact beyond
  counting (already counted); any new tag domain activation; any
  Stage-A/Stage-B authorization; any scientific or performance claim
  (including any FER, efficiency, leakage, key-rate, reliability,
  recovery-rate, or scaling reading); any H2 verdict; any cross-N
  inference; any overwrite under `results/` or
  `comparison_bench/outputs_comparison/`; any commit/push.

## Honest scope statement

A descriptive persistence probe; n=1; no FER/reliability/efficiency
claim; no cross-N inference. Per-N results are NOT comparable across N:
the 1/4→2/5→4/5 chain, the H2 verdicts, the IR-5 32768 geometry, and all
leakage literals stay at N=32768. The probe can neither extend nor break
any accepted verdict; it can only record whether the spike-local
fail-site pattern recurs at N=8192 within-N.

## Impact

- Reads (this scoping): worktree queue docs + accepted evidence JSON/md
  + source-code constants only (per the feasibility-study header). Touches
  no runner, no frozen evidence root, no existing OpenSpec section.
- Writes (additive only): `specs/nbpolar-reduced-n-persistence/spec.md`,
  `design.md`, `proposal.md` (this file); appended tasks section in
  umbrella `tasks.md`; skeleton
  `.workbuddy/queue/NBPOLAR-REDUCED-N-PERSISTENCE/` (`STATUS.yaml` +
  `SCOPING_NOTES.md`).
- Affects: main-thread authorization planning only. This proposal
  authorizes nothing and modifies no existing section.

## Source of truth

The feasibility study (population arithmetic, C1–C10, comparability
verdict, gate class), the P16 packet (construction/allocation pattern),
the P20S packet + R1 evidence root (arm/IR/tag/ledger pattern at
N=32768), and this directory's `spec.md`/`design.md`. This proposal
authorizes no execution.

(End of file)
