# Phase 4-P9 Tier-Y packet — lower-rate boundary resolution

## Mission

Resolve P8's left-censored rate search at N=256. Reuse the accepted P8 static
target-population protocol and extend the SCREEN grid down to both zero axes,
then confirm exactly one deterministically selected point on disjoint streams.
This is the final N=256 static-rate localization gate before a main-thread
choice between adaptive target-rate work and N-scaling/decoder acceleration.

## P9-01 — Delta-only implementation scope

Add a P9 OpenSpec delta/tasks section before code. Reuse
`formal_ir/nbpolar/target_rate.py` and its tests; add a required closed-choice
CLI field `--gate-id p9-lower-rate-boundary` that selects only the P9 protocol
name, tag-domain prefix and result labels, while preserving the existing P8
behavior. Make no other change beyond the new frozen grid and output root. Do
not alter SC, prior, construction, tag, outcome, support, truth,
accounting, or accepted P7/P8 evidence roots.

## P9-02 — Frozen inputs and preconditions

- V25 1M TRAIN `channel_counts.npz`, source `1M`, accepted loader.
- Accepted P7 pooled empirical orders with identity
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`.
- N=256; columnwise MLE, entries below `1e-15` floored to `1e-15`, then
  columnwise renormalization; accepted raw-MLE entropy and floor guards.
- Accepted two-stage hard-candidate SC and 64-bit Toeplitz verification.
- Validate order identity, input stat, absent target root, seed disjointness,
  support/entropy guards, and full grid before the first NPZ content open.

The single artifact read and scientific attempt are consumed together at the
first NPZ content open. No reopen, retry, rerun, tuning, or post-result change.

## P9-03 — Frozen SCREEN

- Streams: `2026091710 2026091711 2026091712`.
- 64 shared blocks per stream; total 192.
- K1 grid: `[0,2,4,6,8,12,24,45]`.
- K2 grid: `[0,20,40,50,60,70,80]`.
- Exact Cartesian product: 56 points, including global zero-disclosure corner
  `(0,0)` and the accepted P8 anchor `(8,80)`.
- Every point uses identical sampled blocks and independent P9-domain tag
  control. `undetected` never counts as exact.
- A point is eligible iff all point-level integrity conditions hold and its
  empirical exact count is at least 188/192, equivalently its one-sided 95%
  Wilson lower bound is at least 0.95.
- Select the eligible point minimizing `(K1+K2,K1,K2)` lexicographically.
- If no point is eligible, return the valid negative label
  `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT`; do not run CONFIRM.

Because both axes include zero, a selected grid boundary is not by itself a
search-truncation ambiguity. No interpolation or unregistered point is allowed.

## P9-04 — Frozen CONFIRM

- Streams: `2026091720 2026091721 2026091722 2026091723 2026091724`.
- 128 blocks per stream; total 640; disjoint from SCREEN and all prior official
  streams.
- Run only the selected empirical-order point plus a same-K BEC-order control,
  which is report-only.
- Empirical confirmation gates: exact at least 618/640 and one-sided 95%
  Wilson lower bound at least 0.95.
- Record paired cells and per-stream buckets; no empirical-over-BEC gate.
- Toeplitz master is `stream+10000`, domain-separated by P9 phase/arm/block.

## P9-05 — Accounting and outputs

For a fully invoked arm, key-dependent disclosure is
`5*(K1+K2)+64`; public control is 2623 bits per tag. Preserve partial-call
accounting and independently recount all transcript totals.

The absent output root is:

`.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/`

Create exactly five compact files:

1. `frozen_plan.json`
2. `screen_records.json`
3. `selection_and_confirmation_records.json`
4. `transcript_accounting.json`
5. `report.md`

No private vectors, decoded keys, raw counts, or raw Toeplitz seeds.

## P9-06 — Tests and reviews

Add focused tests for the 56-point grid, zero-K behavior, P8 anchor inclusion,
shared-block identity, eligibility boundary, deterministic selection, no
eligible path, disjoint confirmation, same-K control, buckets/truth isolation,
accounting/recount, P9 domain separation, absent root, and no production input
from tests. Run focused tests plus the accepted 240-test predecessor suite.

Independent reviewer-go Pre-EXECUTE PASS is mandatory before the NPZ open.
Independent reviewer-go Pre-RESULT review must recompute grid completeness,
eligibility, selection, confirmation, Wilson values, pairing, accounting, and
all gates before return.

Frozen execution command (three lines):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_rate --gate-id p9-lower-rate-boundary --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --orders .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json --n 256 --floor 1e-15 --screen-seeds 2026091710 2026091711 2026091712 --screen-blocks 64 --k1-grid 0 2 4 6 8 12 24 45 --k2-grid 0 20 40 50 60 70 80 --confirm-seeds 2026091720 2026091721 2026091722 2026091723 2026091724 --confirm-blocks 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm
```

The P9 gate id must be persisted and must produce a P9-specific protocol name,
tag-domain prefix and labels. Silent reuse of P8 identifiers is forbidden.

## P9-07 — Result labels and STOP rules

- All integrity and CONFIRM gates true:
  `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE`.
- No eligible SCREEN point: `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT`.
- Eligible point but CONFIRM failure:
  `TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED`.
- Earliest integrity failure: `BLOCKED(<gate>)`.

STOP immediately and preserve evidence on a blocker, integrity failure,
unexpected existing root, input/order mismatch, test failure, review failure,
resource abort, or command/schema ambiguity. Do not repair or rerun after the
attempt is consumed.

Forbidden: Model-F, raw frames, held-out/real/EVAL data; adaptive schedules;
N>256; FWHT/APP/SCL; qualification/promotion; modification of old evidence
roots; commit or push.
