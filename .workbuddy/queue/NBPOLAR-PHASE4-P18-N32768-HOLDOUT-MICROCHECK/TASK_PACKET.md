# Phase 4-P18 Tier-Y — N=32768 1M HOLD operational microcheck

## Mission

Run the accepted P16/P17 operational point on the only three complete,
non-overlapping N=32768 blocks available in the V49/V25 1M HOLD split. This is
a real-input microcheck of loading, ordering, fixed-TRAIN prior use, decoder
behavior and accounting. It is not a FER gate and has no recovery threshold.

## P18-01 — Fixed identities and implementation

Add an OpenSpec P18 delta, one thin
`formal_ir/nbpolar/holdout_microcheck.py` runner, and injected tests. Reuse the
accepted loader, P7 floor-1e-15 prior contract, P16 construction and P17
operational path. Do not change decoder, prior, construction, disclosure,
tag, packing, or outcome semantics.

Before either protected content open, verify P16 construction identity:
N=32768, K1=319, K2=6492, K_total=6811, leakage=34119 and digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`.
Verify the split manifest says the 1M population has 400 HOLD frames and
102400 HOLD pairs. Any mismatch STOPs with zero protected reads/attempts.

## P18-02 — Protected inputs and deterministic block formation

Protected inputs, each opened for content exactly once:

1. V25 1M TRAIN `nbldpc_v25_20260818/run_04/channel_counts.npz`, used only to
   reconstruct the frozen floor-1e-15 prior and repeat P17 population guards.
2. `v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet`, loaded
   through the accepted pairs loader and used only for HOLD frames 1600..1999.

The scientific attempt is consumed at the first protected content open. No
reopen or retry is allowed. Sort HOLD rows by `(frame_id,pair_idx)`; require
exactly 256 rows per frame, pair indices 0..255 and symbols 0..1023. Form:

- block 0: frames 1600..1727;
- block 1: frames 1728..1855;
- block 2: frames 1856..1983.

Record frames 1984..1999 (4096 symbols) as unused remainder. No shuffle,
resampling, overlap, padding, pooling with TRAIN/VAL/P16/P17, or fitting on
HOLD is permitted.

## P18-03 — Frozen operational path and descriptive outputs

For each block run exactly one L1 SC and one candidate-conditioned L2 SC with
the P16 order/K and `chunk_rows=512`, reconstruct the 10-bit label, and invoke
one 64-bit Toeplitz tag. Use public master `2026092050`, domain-separated by
P18/block. Alice truth may enter only disclosed values, tag construction and
scoring; it must not enter Bob metrics, candidate priors or decisions.

Persist scalar-only per block: frame range, raw SER, total and per-layer NLL
under the fixed TRAIN prior, outcome bucket, L1 correctness, tag result,
34119 key-dependent bits, 327743 public-control bits, wall/RSS/VmPeak/VmSize.
Report `34119 / observed_block_NLL_bits` as a sample CE-normalized disclosure
ratio, explicitly not as qualification efficiency.

There is no exact-count, Wilson, FER, winner or promotion threshold. If all
integrity gates hold, label the result
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE` regardless
of 0..3 exact outcomes. An integrity/resource failure is
`BLOCKED(<earliest_gate>)`; never reinterpret recovery as an integrity gate.

## P18-04 — Integrity, evidence and STOP rules

Integrity gates: accepted predecessor identity; correct 1M HOLD population;
three exact non-overlapping block ranges plus declared remainder; six SC
calls; three tags; exhaustive mutually exclusive outcomes; undetected,
nonfinite and truth-leak zero; fixed K/disclosure and literal recount; one
open per protected input; input size/mtime unchanged; no unregistered access;
no resource abort.

Create exactly five files under absent root
`.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`:
`frozen_plan.json`, `input_and_construction_identity.json`,
`per_block_outcomes.jsonl`, `aggregate_summary.json`, `report.md`. Checkpoint
after each block. Persist no private vectors, labels, metrics, raw rows, or tag
seed bits.

Freeze single-thread BLAS/OpenMP and `MALLOC_ARENA_MAX=2`; use 2 GiB virtual
memory and 600 s timeout. Catch MemoryError around the entire post-open path.
After semantic/resource failure preserve checkpoints and STOP: no repair,
rerun, seed change, tuning, cleanup, commit or push.

Focused injected tests cover identity refusal before reads, exact HOLD slicing
and remainder, malformed frame/pair rejection, one-open guards, no fitting or
sampling, fixed construction/path, truth isolation, all outcome buckets,
NLL/disclosure arithmetic, checkpoint recovery and failure precedence. Run
the complete NB-Polar suite. Then obtain independent reviewer-go Pre-EXECUTE
PASS before the single run and independent Pre-RESULT review before return.

## Return contract

Return only after the full lifecycle completes, or on a concrete STOP with
the earliest gate, exact command/error, consumed reads/attempt, preserved
files, and the one main-thread decision required. Include changed files,
commands/tests, three per-block outcomes, NLL/accounting, resources, reviews,
unused remainder, boundaries, and unrun stages. Do not commit or push. End
with memory triage.
