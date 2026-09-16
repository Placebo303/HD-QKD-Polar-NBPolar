# Phase 4-P8 Tier-Y packet — target rate SCREEN → CONFIRM

## Objective

At N=256 on the accepted V25 1M TRAIN model, select the lowest-disclosure
static two-layer point that clears a frozen SCREEN reliability rule, then test
that selected point once on disjoint CONFIRM streams. This calibrates the
finite-length target-population rate point before any adaptive-rate, N-scaling,
FWHT or SCL work.

## P8-01 — OpenSpec and implementation scope

Add a P8 delta/tasks section to the existing Phase 4 OpenSpec before code.
Implement only:

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py`;
- package export if required;
- `comparison_bench/tests/test_nbpolar_target_rate.py`;
- packet lifecycle/review/result and milestone documents.

Reuse the accepted P7 loader, fixed support rule, P1/P2, pooled empirical
orders, SC, two-layer hard-candidate semantics, Toeplitz tag and accounting.
Do not change construction orders, `sc.py`, priors, protocol semantics,
adapters, baselines or predecessor roots.

## P8-02 — Frozen inputs

Read the accepted P7 pooled empirical L1/L2 orders from the immutable P7
`construction_orders.json`; require valid 256-coordinate permutations and the
recorded P7 order identity
`8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`
before opening the channel artifact.

Open exactly once through the accepted loader:

`/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`

Use source `1M` and exactly the P7 rule: columnwise MLE, floor probabilities
below `1e-15`, renormalize columns, p_b from column totals, accepted
`A=32*U1+U2` P1/P2. Recheck P7 entropy/support preconditions before SC.

One artifact read and one scientific attempt are allowed and both are consumed
at the first NPZ content open. No Model-F, raw/held-out/real data or EVAL.

## P8-03 — Frozen SCREEN

- N=256, GF32 polynomial 37, alpha 2, natural SC semantics.
- SCREEN streams `2026091680..2026091682`, 64 common blocks each (192).
- Static empirical-order grid:
  - K1 = `[8,10,12,16,24,32,45]`;
  - K2 = `[80,94,110,125,140]`;
  - exactly 35 configurations.
- Sample `B~p_b`, then `A~P_floor(A|B)` once per shared block; every grid point
  uses the identical block.
- Each configuration runs L1 then candidate-conditioned L2 from scratch,
  reconstructs the full label and invokes one domain-separated 64-bit tag.

A SCREEN point is eligible iff all 192 blocks are accounted for, undetected /
nonfinite / resource_abort are zero, and its one-sided 95% Wilson exact-recovery
lower bound is >=0.95 (equivalently at this frozen shape, exact >=188/192;
independently verify the equivalence).

Choose exactly one point from eligible points by lexicographically minimizing
`(K1+K2, K1, K2)`. Do not use DEV/CONFIRM outcomes or runtime to break ties. If
no point is eligible, stop without CONFIRM and return
`TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` (a valid scientific negative result,
not BLOCKED).

## P8-04 — Frozen CONFIRM

CONFIRM streams are `2026091690..2026091694`, 128 common blocks each (640),
disjoint from SCREEN. Run only the selected empirical-order point plus a paired
BEC-order control at the same selected K1/K2. BEC orders use the accepted P7
H1/H2 surrogate and are report-only.

Toeplitz public master is `stream+10000`, domain-separated by phase/arm/block.
No SCREEN block, outcome or tag seed may enter CONFIRM.

The selected point confirms iff:

- empirical exact >=618/640;
- one-sided 95% Wilson exact-recovery lower bound >=0.95;
- undetected, nonfinite and resource_abort are zero.

BEC exact and empirical-vs-BEC paired cells are report-only; empirical is not
required to beat BEC.

## P8-05 — Accounting and outputs

For a fully invoked point, key-dependent disclosure is
`5*(K1+K2)+64`; public seed is 2623 bits/tag. Decode failure before tag counts
only actually disclosed coordinate bits. Keep exact, verify_failed,
decode_failed, undetected and resource_abort mutually exclusive; never merge
undetected into exact. Independently recount all disclosure/tag events.

Frozen root:

`.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/`

It must be absent before execution and contain exactly:

- `frozen_plan.json`;
- `screen_records.json`;
- `selection_and_confirmation_records.json`;
- `transcript_accounting.json`;
- `report.md`.

Persist scalar per-block outcomes only; no source/Bob/U/decoded/disclosed
vectors, metric arrays, labels, tags or raw seed material. Report every SCREEN
configuration, eligibility, deterministic selection, CONFIRM per-stream and
pooled outcomes, paired cells, Wilson values, leakage, planning-only
`f=mean_key_dependent/(256*0.8010378248977232)`, wall and RSS.

## P8-06 — Tests and reviews

Tests must cover grid completeness/shared-block identity; Wilson boundary
187/192 false and 188/192 true; deterministic selection including ties/no
eligible point; SCREEN/CONFIRM isolation; selected-only confirmation;
empirical/BEC same-K pairing; truth isolation; buckets; partial/full accounting
and transcript recount; no production/artifact invocation from tests. Use only
fresh test seeds. Run focused tests plus the accepted 228-test predecessor
suite.

Freeze the exact command/root/schema in `P8_FREEZE.md`. Independent reviewer-go
Pre-EXECUTE must check the complete selection rule, streams, support/order
identity, thresholds, attempt point, tests, root absence and resources.

Exact WSL command:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_rate --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --orders .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json --n 256 --floor 1e-15 --screen-seeds 2026091680 2026091681 2026091682 --screen-blocks 64 --k1-grid 8 10 12 16 24 32 45 --k2-grid 80 94 110 125 140 --confirm-seeds 2026091690 2026091691 2026091692 2026091693 2026091694 --confirm-blocks 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm
```

Limits: 2 GiB, 3600 seconds. No rerun, seed/grid/floor/order/threshold change.

Independent reviewer-go Pre-RESULT must reconstruct the 35-point SCREEN,
Wilson eligibility, deterministic selection, independent CONFIRM, paired cells,
accounting and every gate from the five artifacts before publication.

## P8-07 — Labels and boundaries

If no eligible SCREEN point exists, return
`TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT`. If a point is selected and every
CONFIRM/integrity gate passes, return `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE`.
If integrity passes but CONFIRM fails, return
`TARGET_EMPIRICAL_RATE_POINT_NOT_CONFIRMED`. Integrity failure returns
`BLOCKED(<earliest gate>)`.

STOP and preserve raw evidence on review failure, target presence, input/order
mismatch, test/command error, truth leak, resource breach or integrity failure.
Do not repair or rerun.

Scope is V25-1M-TRAIN model-sampled N=256 static development only. No held-out/
real FER, adaptive schedule, N>256, FWHT/APP/SCL, efficiency/key-rate,
qualification/promotion, old-root modification, commit or push.
