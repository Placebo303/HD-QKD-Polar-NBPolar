# NB-Polar Phase 4-P19 specification delta

Phase 4-P19 is the N=32768 1M-HOLD layer/backoff diagnostic of the accepted
P16/P17 operational point on the exact three accepted P18 HOLD blocks
(frames 1600..1727, 1728..1855, 1856..1983 of the 1M ``pairs.parquet``,
128 frames = 32768 pairs each). It determines *descriptively* whether
additional L1 disclosure (+128 coordinates), additional L2 disclosure
(+512 coordinates), both, or true-L1 conditioning changes hard recovery. It
is not a FER gate, has no recovery/winner/monotonicity/qualification
threshold and cannot promote or qualify anything: every recovery pattern
(0/3..3/3 exact) is a descriptive COMPLETE when integrity holds, and only
integrity or resource failures produce ``BLOCKED(<earliest gate>)``. The
``true_l1_control`` arm is an oracle-labelled diagnostic control, never an
operational protocol or deployable rate. Implementation tasks live in the
companion P19 section of `tasks.md`; status, acceptance and route disposition
are owned by the main thread, never by the implementing session. This
document authorizes no production behavior.

## Requirement: verified predecessor, split manifest, accepted P18 blocks and one-open protected inputs

Before any output root exists and before either protected content open, the
diagnostic SHALL read the accepted P16
`construction_and_allocation.json` (JSON only, P16 immutable) and verify
N=`32768`, K_total=`6811`, K1=`319`, K2=`6492`, valid L1/L2 orders, the K/f
replay from the ratified literals (`floor((1.3*32768*H - 64)/5) = 6811`,
leakage `5*6811+64 = 34119 <= 1.3*32768*H`) and the canonical digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
(recomputed with the exact P16 canonical recipe). It SHALL additionally read
the V25 run_04 `split_manifest.json` (JSON only, schema
`nbldpc_v25_split_manifest_v1`) and verify that the 1M source
`type2_1M_20260121_184040` declares exactly 400 HOLD frames and 102400 HOLD
pairs, and SHALL pin the accepted P18 block constants at code level (same N,
base K1/K2, block ranges `1600..1727`/`1728..1855`/`1856..1983`, remainder
`1984..1999`, hold frame range `1600..1999`, 32768 pairs per block). Any
mismatch SHALL stop before any root exists and before any protected content
open, consuming no read and no attempt.

The diagnostic SHALL then content-open exactly two protected inputs, each
exactly once, in this order: (1) the V25 1M TRAIN
`nbldpc_v25_20260818/run_04/channel_counts.npz` through the accepted
`load_v25_channel_counts`, after a stat-only size check of exactly
`25,166,822` bytes, used only to rebuild the frozen floor-`1e-15` prior and
repeat the accepted P7 population guards; (2) the 1M
`v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet` through
the accepted `load_pairs_table`/`normalize_pair_columns` loader (required
schema `frame_id`/`pair_idx`/`alice_symbol`/`bob_symbol`), used only for
HOLD frames `1600..1999`. The single scientific attempt SHALL be consumed at
the first protected content open (the NPZ); module-level guards SHALL refuse
a second content open of either input. Input size and mtime SHALL be
recorded by stat before the opens and rechecked unchanged after the run.
Refusals (absent root, CLI parse, contract flags, digest-flag pin,
predecessor identity, manifest identity, P18 block pin, one-open guards,
absent or wrong-sized NPZ input, absent HOLD parquet) SHALL happen before any
content open, consuming nothing; any post-open failure SHALL be
`BLOCKED(<earliest gate>)` with consumption already spent and checkpoints
preserved. The only support rule SHALL remain the exact P7 rule
(column-normalize, replace cells below `1e-15` by `1e-15`, renormalize;
`p_b` from column totals; accepted `derive_p1`/`derive_p2` under
`A = 32*U1 + U2`); no fitting, smoothing, floor scan or tuning is permitted.
No HOLD-data mutation is permitted.

## Requirement: deterministic P18 block formation with declared remainder

The diagnostic SHALL form its blocks through the accepted P18
`form_holdout_blocks`: sort the loaded HOLD rows by `(frame_id, pair_idx)`
and require exactly 400 frames `1600..1999`, exactly 256 rows per frame,
`pair_idx` exactly `0..255` per frame and symbols in `0..1023`. It SHALL use
exactly three non-overlapping chronological blocks: block 0 frames
`1600..1727`, block 1 frames `1728..1855`, block 2 frames `1856..1983`
(32768 pairs each), and SHALL record frames `1984..1999` (16 frames, 4096
pairs) as the unused remainder that never enters any arm. No shuffle,
resampling, overlap, padding, pooling with TRAIN/VAL/P16/P17 or fitting on
HOLD is permitted; the runner SHALL contain no random-number generator path
at all. Malformed frames, row counts, pair indices or symbol ranges SHALL
raise `BLOCKED(hold_population_exact)`; declared block/remainder mismatches
SHALL raise `BLOCKED(blocks_exact_with_declared_remainder)`.

## Requirement: five frozen arms, exact order and the oracle control boundary

The diagnostic SHALL run exactly five frozen arms in this exact order with
the verified P16 empirical orders and the fixed increments +128 L1 / +512 L2
coordinates, at `chunk_rows=512` and P19 tag master `2026092060` with
P19/arm/block seed-domain separation (prefix
`nbpolar-p19-holdout-backoff-diagnostic-seed`; raw seed bits never
persisted). The arms SHALL be module constants, never CLI-tunable and never
extensible:

1. `base`: operational K1=`319`, K2=`6492`; leakage `34119` bits.
2. `l1_plus`: operational K1=`447`, K2=`6492`; leakage `34759` bits.
3. `l2_plus`: operational K1=`319`, K2=`7004`; leakage `36679` bits.
4. `both_plus`: operational K1=`447`, K2=`7004`; leakage `37319` bits.
5. `true_l1_control`: true high-layer conditioning used ONLY as an
   oracle-labelled L2 conditioning/label control; no L1 SC and no L1
   disclosure; discloses K2=`6492`, runs exactly one L2 SC and at most one
   tag; provenance `ORACLE_TRUE_L1_CONTROL`.

Each operational arm SHALL run one operational L1 SC (disclosing true U1 at
`order1[:K1]`) plus one candidate-conditioned L2 SC (disclosing true U2 at
`order2[:K2]`) per block through the accepted `run_operational_block`; the
control SHALL run one oracle-conditioned L2 SC per block; the design totals
SHALL be exactly 27 SC calls and 15 tags for the 15 (arm, block) records and
SHALL be asserted. The `base` arm alone replays the accepted f<=1.3 planning
budget; `l1_plus`/`l2_plus`/`both_plus` disclose above it by the fixed
increments and SHALL be reported as descriptive diagnostic disclosure levels,
never as qualified operational points. The control SHALL be excluded from
every operational aggregate and SHALL never be presented as an operational
protocol or deployable rate. Alice truth SHALL enter operational arms only
through disclosed values, tag construction and scoring (accepted truth
boundary and sentinel); the control's additional truth use (true high-layer
metric conditioning and label reconstruction) SHALL be confined to its own
arm and provenance label.

## Requirement: descriptive outputs, paired tables and neutral non-monotone reporting

For every (arm, block) the diagnostic SHALL persist scalar-only: the outcome
bucket (exactly one of `exact`/`undetected`/`verify_failed`/`decode_failed`/
`nonfinite`/`resource_abort`, `undetected` never success), L1 correctness,
tag result, actual key-dependent and public-control bits, the frame range,
raw channel SER (`mean(alice_symbol != bob_symbol)`), per-layer and total NLL
in bits under the fixed TRAIN prior (`l1 = sum_i -log2 p1[high_i,bob_i]`,
`l2 = sum_i -log2 p2[high_i,bob_i,low_i]`, `high = A//32`, `low = A%32`), the
sample `arm_leakage_bits / observed_block_NLL_bits` cross-entropy-normalized
disclosure ratio and wall/RSS-HWM/VmPeak/VmSize. A fully invoked operational
record SHALL disclose exactly `5*(K1+K2)+64` key-dependent bits and `327743`
public-control bits per tag; the control SHALL disclose exactly
`5*K2+64 = 32524` key-dependent bits per tagged record; partial failure
counts only actually disclosed bits; an independent literal transcript
recount SHALL equal the incremental totals with zero mismatch.

The diagnostic SHALL report, descriptively and without any threshold: paired
recovery tables of each ordered operational arm versus `base` (per-block
outcome pairs, recovered-vs-base and lost-vs-base counts), a
first-operational-recovery-arm pointer (first operational arm in frozen
order with at least one `exact` record, `null` when none exists; the oracle
control is never a candidate), and a neutral
`ordered_exact_counts_non_monotone` flag. Non-monotone outcomes SHALL be
reported neutrally: no monotonicity, superiority, winner, FER or
qualification claim is permitted anywhere. The CE-normalized disclosure
ratio SHALL NOT be described as qualification reconciliation efficiency.

## Requirement: integrity gates, fixed labels and explicit no-threshold rule

The diagnostic SHALL persist all integrity gates as booleans in frozen order:
predecessor construction identity; split-manifest identity; accepted P18
block-range identity; target population contract; exact HOLD population;
exact three blocks per arm with the declared unused remainder; exactly 15
records; exactly 27 SC calls; exactly 15 tags; valid verified orders with per
arm K/prefix arithmetic and the registered arm table (recomputed from the
persisted records; the fully accounted partial transcript is accepted only
under a registered resource stop, where the resource gate is the blocker);
oracle isolation (control records in their own provenance partition, excluded
from operational aggregates, no oracle conditioning on any operational
record); mutually exclusive exhaustive record buckets with duplicate-free
(arm, block) keys; `undetected` zero; `nonfinite` zero; truth isolation with
zero leak violations; fixed disclosure plus literal recount exactness;
exactly one content open per protected input; unchanged input size/mtime; no
unregistered access or calls; and resource limits met with zero aborts.
There SHALL be no exact-count, FER, winner, monotonicity, promotion or
recovery threshold of any kind: if every integrity gate holds the label SHALL
be `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` regardless of
the 0/3..3/3 recovery pattern (0/3 and 3/3 alike); any integrity or resource
failure SHALL be `BLOCKED(<earliest gate>)`, and recovery SHALL never be
reinterpreted as an integrity gate. `undetected` SHALL never be success.

## Requirement: frozen CLI, five-file checkpointed output and bounded scope

The CLI SHALL require every flag with no production default — `--counts`,
`--source`, `--floor`, `--n`, `--k1`, `--k2`, `--construction`,
`--construction-digest`, `--hold-pairs`, `--hold-frames`, `--block-frames`,
`--remainder-frames`, `--tag-master`, `--chunk-rows`, `--tag-bits`,
`--out-dir` — where `--k1`/`--k2` pin the `base` arm and the other four arms
are frozen module constants only, and SHALL refuse an existing output root,
any N other than `32768`, K flags other than `319`/`6492`, a chunk-rows value
other than 512 (with the `_minus_block` default-512 contract check), a
tag-bits value other than 64, hold frames other than `1600..1999`, block
frames other than 128, remainder frames other than `1984..1999`, a
tag-master other than `2026092060`, a construction-digest flag other than the
frozen digest, and any CLI parse failure, all before either protected content
open. The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`
SHALL be absent before execution and SHALL be created with exactly five files
before the opens (`frozen_plan.json`,
`input_and_predecessor_identity.json`, `per_block_arm_outcomes.jsonl`,
`aggregate_summary.json`, `report.md`), checkpointed after every (arm, block)
record; no sidecars SHALL be created. Predecessor/manifest/P18 identity, input
stat metadata and scalar (arm, block) outcomes only — counts, sampled symbols,
truth vectors, decoded labels/keys, metric planes, raw rows, tag seeds,
per-arm orders and RNG state SHALL NOT be persisted. The diagnostic SHALL
record wall, RSS HWM, Linux `VmPeak` and `VmSize` per record. The frozen
environment SHALL be `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2` with a 2 GiB virtual limit
(`ulimit -v 2097152`) and a 600 s external timeout; MemoryError SHALL be
caught around the entire post-open path, checkpoints preserved and the run
finalized as BLOCKED when possible. After a semantic or resource failure
there SHALL be no repair, rerun, seed/N/K/floor/order/arm change, tuning or
cleanup, and the remainder frames SHALL never be used. Forbidden: Model-F
artifact, raw/real/held-out/EVAL frames, other N in the frozen run, any added
or changed arm/grid/interpolation/adaptive choice or post-result arm, any
construction path, BEC, transform/belief/list or soft-marginal decoders, a
second tag outside the registered arms, fitting/sampling/shuffling on HOLD,
production benchmark, FER/efficiency/key-rate/qualification/promotion claim,
old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered COMPLETE label and the
blocker return; COMPLETE means the 15 registered (arm, block) records
completed with every identity, population, block, count, order/prefix,
oracle-isolation, bucket, truth, accounting, one-open, stat, access and
resource gate true, with the 0/3..3/3 recovery patterns and paired tables
reported as descriptive scalars only. It SHALL NOT be described as real-frame
FER, reconciliation efficiency, leakage, key rate, scaling superiority,
qualification or promotion evidence; the sample CE-normalized disclosure
ratio is not qualification efficiency; the true-L1 control is never an
operational protocol or deployable rate. An independent Pre-EXECUTE review
SHALL pass before the single attempt, and an independent Pre-RESULT review
SHALL recompute the identities, population, 15 records, per-arm outcomes,
paired/first-recovery diagnostics, NLL/disclosure accounting, oracle
isolation, gates, input stats, resources and five-file inventory from the
artifacts before any result is published; neither the run nor the
implementing session may accept its own work.
