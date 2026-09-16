# Phase 4-P19 Tier-Y — 1M HOLD layer/backoff diagnostic

## Mission

On the exact three P18 HOLD blocks, determine descriptively whether additional
L1 disclosure, additional L2 disclosure, both, or true-L1 conditioning changes
recovery. This is the smallest finite-length backoff diagnostic justified by
P18. It has no FER, winner, monotonicity or qualification threshold.

## Frozen inputs and minimal implementation

Add one P19 OpenSpec delta, a thin
`formal_ir/nbpolar/holdout_backoff_diagnostic.py` runner and injected tests.
Reuse P18 loading/block formation and P16/P17 operational helpers unchanged.
Do not modify prior, SC, construction order, packing, tag or outcome logic.

Before content opens, verify N=32768, K1=319, K2=6492 and construction digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`,
the accepted P18 block ranges, and the 400-frame/102400-pair manifest.

Open V25 1M TRAIN counts once to rebuild the frozen floor-1e-15 prior, then
open the 1M pairs parquet once. The attempt is consumed at the first protected
open. Recreate only blocks 1600..1727, 1728..1855 and 1856..1983; record
1984..1999 unused. No shuffle, overlap, resampling, padding, pooling, fitting
or reopen.

## Five frozen arms

Use accepted empirical order prefixes, `chunk_rows=512`, tag master
`2026092060`, and P19/arm/block domain separation. Run in this order:

1. `base`: operational K1=319, K2=6492; leakage 34119 bits.
2. `l1_plus`: operational K1=447, K2=6492; leakage 34759 bits.
3. `l2_plus`: operational K1=319, K2=7004; leakage 36679 bits.
4. `both_plus`: operational K1=447, K2=7004; leakage 37319 bits.
5. `true_l1_control`: use true U1 only as an oracle-labelled L2
   conditioning/label control, disclose K2=6492, run one L2 SC and one tag;
   never present this as an operational protocol or deployable rate.

The increments +128 L1 and +512 L2 are fixed. Operational arms use eight SC
calls/block; the control uses one, for 27 SC calls and 15 tags. Alice truth may
enter operational arms only through disclosures, tag construction and
scoring. Extra truth use in the control carries `ORACLE_TRUE_L1_CONTROL`
provenance and is excluded from operational aggregates.

## Descriptive outputs and classification

Persist scalar outcomes for every block/arm, paired recovery tables versus
base, first operational recovery arm, L1 correctness, tag result,
disclosure/public counts, raw SER and fixed-prior NLL. Report each operational
leakage/NLL ratio as sample CE-normalized disclosure, not qualification
efficiency. Report non-monotone outcomes neutrally.

There is no recovery-count, Wilson, FER, superiority or route threshold. If
integrity holds, return `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`
for every outcome pattern. Integrity/resource failure returns
`BLOCKED(<earliest_gate>)`. Never convert 0/3 or 3/3 into pass/fail.

Integrity covers identities; exact blocks/remainder; 15 records; 27 SC calls
and 15 tags; K/order prefixes; oracle isolation; exhaustive buckets;
undetected/nonfinite/truth-leak zero; recount; one open per input; unchanged
stats; no unregistered calls or resource abort.

Create exactly five files in absent root
`.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`:
`frozen_plan.json`, `input_and_predecessor_identity.json`,
`per_block_arm_outcomes.jsonl`, `aggregate_summary.json`, `report.md`.
Checkpoint after each arm; persist no raw/private vectors, labels, metrics,
keys or raw seed bits.

Use single-thread BLAS/OpenMP, `MALLOC_ARENA_MAX=2`, 2 GiB virtual memory and
600 s timeout. Catch MemoryError over the full post-open path. Failure STOPs
without repair, rerun, tuning, cleanup, commit or push.

Injected tests cover identities-before-read, P18 slicing, five-arm semantics,
oracle isolation, counts/buckets, paired tables, non-monotone reporting,
accounting and checkpoint STOP. Run focused P19 plus P16/P17/P18 predecessor
suites. Run all NB-Polar tests only if shared predecessor code changes or a
focused failure requires it; record why. Obtain independent reviewer-go
Pre-EXECUTE PASS and Pre-RESULT review.

## Return contract

Return after the lifecycle or first concrete STOP. Report changed files,
commands/tests, read/attempt accounting, 15 outcomes, paired/first-recovery
diagnostics, accounting/resources, reviews, boundaries and unrun stages. The
operator/reviewer cannot choose a route or accept results. End with memory
triage; do not commit or push.
