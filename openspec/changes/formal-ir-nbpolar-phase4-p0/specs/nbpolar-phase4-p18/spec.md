# NB-Polar Phase 4-P18 specification delta

Phase 4-P18 is the N=32768 1M-HOLD real-input operational microcheck of
the accepted P16/P17 operational point. It runs the frozen point exactly
once on the only three complete, non-overlapping N=32768 blocks available
in the V25 1M HOLD split (frames 1600..1983 of the 1M ``pairs.parquet``,
128 frames = 32768 pairs each) and reports descriptive loading, ordering,
fixed-TRAIN prior, decoder and accounting scalars. It is not a FER gate,
has no recovery threshold and cannot promote or qualify anything: 0..3
exact outcomes are descriptive, and only integrity or resource failures
produce ``BLOCKED(<earliest gate>)``. Implementation tasks live in the
companion P18 section of `tasks.md`; status, acceptance and route
disposition are owned by the main thread, never by the implementing
session. This document authorizes no production behavior.

## Requirement: verified predecessor, split manifest and one-open protected inputs

Before any output root exists and before either protected content open,
the gate SHALL read the accepted P16
`construction_and_allocation.json` (JSON only, P16 immutable) and verify
N=`32768`, K_total=`6811`, K1=`319`, K2=`6492`, valid L1/L2 orders, the
K/f replay from the ratified literals (`floor((1.3*32768*H - 64)/5) =
6811`, leakage `5*6811+64 = 34119 <= 1.3*32768*H`) and the canonical
digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
(recomputed with the exact P16 canonical recipe). It SHALL additionally
read the V25 run_04 `split_manifest.json` (JSON only, schema
`nbldpc_v25_split_manifest_v1`) and verify that the 1M source
`type2_1M_20260121_184040` declares exactly 400 HOLD frames and 102400
HOLD pairs. Any mismatch SHALL stop before any root exists and before any
protected content open, consuming no read and no attempt.

The gate SHALL then content-open exactly two protected inputs, each
exactly once, in this order: (1) the V25 1M TRAIN
`nbldpc_v25_20260818/run_04/channel_counts.npz` through the accepted
`load_v25_channel_counts`, after a stat-only size check of exactly
`25,166,822` bytes, used only to rebuild the frozen floor-`1e-15` prior
and repeat the accepted P7 population guards; (2) the 1M
`v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet`
through the accepted `load_pairs_table`/`normalize_pair_columns` loader
(required schema `frame_id`/`pair_idx`/`alice_symbol`/`bob_symbol`),
used only for HOLD frames `1600..1999`. The single scientific attempt
SHALL be consumed at the first protected content open (the NPZ);
module-level guards SHALL refuse a second content open of either input.
Input size and mtime SHALL be recorded by stat before the opens and
rechecked unchanged after the run. Refusals (absent root, CLI parse,
contract flags, digest-flag pin, predecessor identity, manifest identity,
one-open guards, absent or wrong-sized NPZ input, absent HOLD parquet)
SHALL happen before any content open, consuming nothing; any post-open
failure SHALL be `BLOCKED(<earliest gate>)` with consumption already
spent and checkpoints preserved. The only support rule SHALL remain the
exact P7 rule (column-normalize, replace cells below `1e-15` by `1e-15`,
renormalize; `p_b` from column totals; accepted `derive_p1`/`derive_p2`
under `A = 32*U1 + U2`); no fitting, smoothing, floor scan or tuning is
permitted. No HOLD-data mutation is permitted.

## Requirement: deterministic HOLD block formation with declared remainder

The gate SHALL sort the loaded HOLD rows by `(frame_id, pair_idx)` and
SHALL require exactly 400 frames `1600..1999`, exactly 256 rows per
frame, `pair_idx` exactly `0..255` per frame and symbols in `0..1023`.
It SHALL form exactly three non-overlapping chronological blocks: block 0
frames `1600..1727`, block 1 frames `1728..1855`, block 2 frames
`1856..1983` (32768 pairs each), and SHALL record frames `1984..1999`
(16 frames, 4096 pairs) as the unused remainder. No shuffle, resampling,
overlap, padding, pooling with TRAIN/VAL/P16/P17 or fitting on HOLD is
permitted; the runner SHALL contain no random-number generator path at
all. Malformed frames, row counts, pair indices or symbol ranges SHALL
raise `BLOCKED(hold_population_exact)`; declared block/remainder
mismatches SHALL raise `BLOCKED(blocks_exact_with_declared_remainder)`.

## Requirement: frozen operational path and descriptive outputs

For each block the gate SHALL run exactly one L1 SC and one
candidate-conditioned L2 SC through the accepted `run_operational_block`
helper with the verified P16 orders and K1=`319`/K2=`6492` at
`chunk_rows=512`, SHALL reconstruct the 10-bit label and SHALL invoke
exactly one 64-bit Toeplitz tag in the P18/N/block seed domain (public
master `2026092050`, prefix `nbpolar-p18-holdout-microcheck-seed`,
different from the P16 and P17 prefixes; raw seed bits never persisted).
Alice truth SHALL enter only scoring, disclosed values and tag
construction/scoring; it SHALL NOT enter Bob metrics, candidate priors or
decisions. Each block SHALL persist scalar-only: frame range, raw channel
SER (`mean(alice_symbol != bob_symbol)`), per-layer and total NLL in bits
under the fixed TRAIN prior (`l1 = sum_i -log2 p1[high_i,bob_i]`,
`l2 = sum_i -log2 p2[high_i,bob_i,low_i]`), outcome bucket, L1
correctness, tag result, `34119` key-dependent bits, `327743`
public-control bits and wall/RSS-HWM/VmPeak/VmSize. The gate SHALL also
report `34119 / observed_block_NLL_bits` per block as a sample
cross-entropy-normalized disclosure ratio; it is descriptive and SHALL
NOT be described as qualification reconciliation efficiency. A fully
invoked block discloses exactly `5*(K1+K2)+64 = 34119` key-dependent bits
and `10*N+63 = 327743` public-control bits per tag; partial failure counts
only actually disclosed bits. An independent literal transcript recount
SHALL match the incremental totals with zero mismatch.

## Requirement: integrity gates, fixed labels and explicit no-threshold rule

The gate SHALL persist all integrity gates as booleans in frozen order:
predecessor construction identity; split-manifest identity; target
population contract; exact HOLD population; three exact non-overlapping
block ranges with the declared unused remainder; valid verified orders
with K replay and `f <= 1.3`; exact SC-call accounting (recomputed from
the persisted records, at most `6`); tag accounting (recomputed, at most
`3`); mutually exclusive exhaustive outcome buckets; truth isolation with
zero violations; `undetected` zero; `nonfinite` zero; fixed K/disclosure
plus literal recount exactness; one open per protected input; unchanged
input size/mtime; no unregistered access; and resource limits met with
zero aborts. There SHALL be no exact-count, FER, winner, promotion or
recovery threshold of any kind: if every integrity gate holds the label
SHALL be
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`
regardless of 0..3 exact outcomes; any integrity or resource failure
SHALL be `BLOCKED(<earliest gate>)`, and recovery SHALL never be
reinterpreted as an integrity gate. `undetected` SHALL never be success.

## Requirement: frozen CLI, five-file checkpointed output and bounded scope

The CLI SHALL require every flag with no production default — `--counts`,
`--source`, `--floor`, `--n`, `--k1`, `--k2`, `--construction`,
`--construction-digest`, `--hold-pairs`, `--hold-frames`,
`--block-frames`, `--remainder-frames`, `--tag-master`, `--chunk-rows`,
`--tag-bits`, `--out-dir` — and SHALL refuse an existing output root, any
N other than `32768`, K flags other than `319`/`6492`, a chunk-rows value
other than 512 (with the `_minus_block` default-512 contract check), a
tag-bits value other than 64, hold frames other than `1600..1999`, block
frames other than 128, remainder frames other than `1984..1999`, a
tag-master other than `2026092050`, a construction-digest flag other than
the frozen digest, and any CLI parse failure, all before either protected
content open. The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`
SHALL be absent before execution and SHALL be created with exactly five
files before the opens (`frozen_plan.json`,
`input_and_construction_identity.json`, `per_block_outcomes.jsonl`,
`aggregate_summary.json`, `report.md`), checkpointed after every block;
no sidecars SHALL be created. Predecessor/manifest identity, input stat
metadata and scalar block outcomes only — counts, sampled symbols, truth
vectors, decoded labels/keys, metric planes, raw rows, tag seeds and RNG
state SHALL NOT be persisted. The gate SHALL record wall, RSS HWM, Linux
`VmPeak` and `VmSize` per record. The frozen environment SHALL be
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`MALLOC_ARENA_MAX=2` with a 2 GiB virtual limit (`ulimit -v 2097152`) and
a 600 s external timeout; MemoryError SHALL be caught around the entire
post-open path, checkpoints preserved and the run finalized as BLOCKED
when possible. After a semantic or resource failure there SHALL be no
repair, rerun, seed/N/K/floor/order/change, tuning or cleanup. Forbidden:
Model-F artifact, raw/real/held-out frames, EVAL, other N in the frozen
run, any construction path, any second arm or retry, BEC, transform/
belief/list decoders, production benchmark, FER/efficiency/key-rate/
qualification/promotion claim, old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered COMPLETE label and the
blocker return; COMPLETE means the three registered HOLD blocks completed
with every identity, population, block, order, call, tag, bucket, truth,
accounting, one-open, stat, access and resource gate true, with 0..3
exact outcomes reported as descriptive scalars only. It SHALL NOT be
described as real-frame FER, reconciliation efficiency, leakage, key
rate, scaling superiority, qualification or promotion evidence; the
sample CE-normalized disclosure ratio is not qualification efficiency.
An independent Pre-EXECUTE review SHALL pass before the single attempt,
and an independent Pre-RESULT review SHALL recompute the identities,
population, three block outcomes, NLL/accounting, gates, input stats,
resources and five-file inventory from the artifacts before any result is
published; neither the run nor the implementing session may accept its own
work.
