# P19 freeze — N=32768 1M-HOLD layer/backoff diagnostic (Wave-A implementation)

Packet: `NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC` (`TASK_PACKET.md`, 88
lines, frozen). Predecessor:
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE_ACCEPTED_DESCRIPTIVE`
(P18 STATUS.yaml). Wave-A scope ONLY: OpenSpec delta + implementation + tests +
this freeze. This document authorizes nothing. No box in `tasks.md` is checked
by the implementing session.

## 1. Mission

On the exact three accepted P18 HOLD blocks (frames 1600..1727, 1728..1855,
1856..1983 of the 1M `pairs.parquet`), determine **descriptively** whether
additional L1 disclosure (+128 coordinates), additional L2 disclosure (+512
coordinates), both, or true-L1 conditioning changes hard recovery. This is the
smallest finite-length backoff diagnostic justified by P18's accepted 0/3
descriptive microcheck. It is not a FER gate and has no recovery, winner,
monotonicity or qualification threshold: every recovery pattern (0/3..3/3) is
a descriptive COMPLETE when integrity holds, and only integrity or resource
failures produce `BLOCKED(<earliest gate>)`.

## 2. Fixed identities (verified in this session before any protected open)

P16 accepted file
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
(JSON read only; P16 immutable, never modified):

| item | verified value |
|---|---|
| protocol | `nbpolar-p16-operational-f13-gate`, frozen before first DEV |
| N / K_total / K1 / K2 | 32768 / 6811 / 319 / 6492 |
| L1/L2 orders | valid permutations of length 32768 |
| canonical digest (recomputed here) | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` |
| stored digest | identical (match) |
| K replay | `floor((1.3*32768*H-64)/5) = 6811`, `319+6492 = 6811` |
| leakage / f | `5*6811+64 = 34119`, `f = 1.2998502888172847 <= 1.3` |

Split manifest
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`
(JSON read only):

| item | verified value |
|---|---|
| schema | `nbldpc_v25_split_manifest_v1` |
| 1M source tag | `type2_1M_20260121_184040` |
| HOLD frames / pairs | 400 / 102400 (frozen requirement) |
| TRAIN / VAL context | 1200 frames / 307200 pairs, 400 frames / 102400 pairs |

Accepted P18 block pin (code level, against the accepted P18 module
`formal_ir/nbpolar/holdout_microcheck.py`; no P18 root is re-read):

| item | pinned value |
|---|---|
| N / base K1 / base K2 / K_total | 32768 / 319 / 6492 / 6811 |
| construction digest | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` |
| block count / frames per block | 3 / 128 (32768 pairs each) |
| block ranges | `1600..1727`, `1728..1855`, `1856..1983` |
| remainder | frames `1984..1999`, 4096 pairs, unused |
| HOLD frame range / population | `1600..1999` / 400 frames, 102400 pairs |

Any mismatch stops before any root exists and before either protected content
open, consuming no read and no attempt.

## 3. Protected inputs, one content open each

Both are read-only inputs. Each is content-opened **exactly once**; the single
scientific attempt is consumed at the **first** protected content open (the
NPZ). Module-level guards refuse a second content open of either input.

| input | registered path (repo-relative) | resolved absolute path | expected size (stat only) |
|---|---|---|---|
| V25 1M TRAIN NPZ | `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz` (cross-checkout absolute) | same | 25,166,822 bytes (refusal if different) |
| 1M HOLD pairs parquet | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet` | `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet` | 1,354,289 bytes (provenance only; never a refusal) |

Per-input content opens, attempt consumption and before/after (size, mtime_ns)
stats are recorded in `input_and_predecessor_identity.json`.

Refusal ordering (all before any content open, consuming nothing): absent
output root → CLI parse → frozen flag contracts (floor/source/N/base-K/
chunk-rows/tag-bits/hold-frames/block-frames/remainder-frames/tag-master) →
frozen arm-table pin → construction digest-flag pin → P16 construction
identity → split manifest identity → accepted P18 block pin → one-open guards
→ NPZ/HOLD path existence and stat-only checks. After the first content open
there is no repair, rerun, seed/N/K/floor/order/arm change, tuning or cleanup.

## 4. Deterministic HOLD block formation and remainder

Blocks are formed by the accepted P18 `form_holdout_blocks` (sort HOLD rows by
`(frame_id, pair_idx)`; require exactly 400 frames 1600..1999, exactly 256 rows
per frame, `pair_idx` exactly 0..255 per frame and symbols 0..1023):

| block | frames | pairs |
|---|---|---|
| 0 | 1600..1727 | 32768 |
| 1 | 1728..1855 | 32768 |
| 2 | 1856..1983 | 32768 |
| unused remainder | 1984..1999 | 4096 (recorded, never used) |

No shuffle, resampling, overlap, padding, pooling with TRAIN/VAL/P16/P17 or
fitting on HOLD is permitted; the runner contains no random-number generator
path at all.

## 5. Five frozen arms (run in this exact order; no threshold)

| # | arm | kind | K1 | K2 | leakage bits (full block) | SC/block | provenance |
|---|---|---|---|---|---|---|---|
| 1 | `base` | operational | 319 | 6492 | 34119 | 2 (L1 + candidate L2) | `OPERATIONAL` |
| 2 | `l1_plus` | operational | 447 | 6492 | 34759 | 2 | `OPERATIONAL` |
| 3 | `l2_plus` | operational | 319 | 7004 | 36679 | 2 | `OPERATIONAL` |
| 4 | `both_plus` | operational | 447 | 7004 | 37319 | 2 | `OPERATIONAL` |
| 5 | `true_l1_control` | oracle control | 0 | 6492 | 32524 | 1 (oracle-conditioned L2) | `ORACLE_TRUE_L1_CONTROL` |

Increments are fixed (+128 L1 coordinates = +640 bits; +512 L2 coordinates =
+2560 bits; both = +3200 bits). Design totals asserted by the runner: **27 SC
calls** (4 × 3 × 2 + 3 × 1) and **15 tags** (5 × 3), 15 records. `base` alone
replays the accepted `f<=1.3` planning budget; `l1_plus`/`l2_plus`/`both_plus`
disclose above it by the fixed increments and are descriptive diagnostic
disclosure levels, **not qualified operational points**. The control conditions
the L2 metric on the true high-layer symbol (the `[U1,B,U2]` index space used
by the accepted operational path for its hard L1 candidate) and reconstructs
`label_hat = 32*true_high + low_hat`; it is never an operational protocol or
deployable rate and never enters an operational aggregate. Alice truth enters
operational arms only through disclosed values, tag construction and scoring
(accepted `run_operational_block` truth boundary and sentinel).

Tag domain: public master `2026092060`, prefix
`nbpolar-p19-holdout-backoff-diagnostic-seed`, seed string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
truncated to `10*N+63 = 327743` bits). The P19 prefix and arm token differ from
the P16, P17 and P18 domains; raw seed bits are never persisted (only the bit
length is recorded).

## 6. Frozen command (verbatim; constructed from the P18 pattern with P19 values)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_backoff_diagnostic --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --hold-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 --tag-master 2026092060 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic
```

Sixteen flags, all required, no production default: the packet lists the
expected flag set but has no literal command block, so the command was
constructed from the accepted P18 pattern with P19 values. No new flag was
invented for P19; every field is either literally given by the packet
(`--counts`, `--source 1M`, `--floor 1e-15`, `--n 32768`, `--construction`,
`--construction-digest`, `--hold-pairs`, `--hold-frames 1600 1999`,
`--block-frames 128`, `--remainder-frames 1984 1999`,
`--tag-master 2026092060`, `--chunk-rows 512`, `--tag-bits 64`, `--out-dir`)
or is the frozen base-arm pin (`--k1 319 --k2 6492`). `--k1`/`--k2` pin the
`base` arm only; the other four arms are module constants and are not
CLI-tunable (flagged R8 in the implementation notes for Pre-EXECUTE review).
Budgets: 600 s external timeout, 2 GiB virtual limit (`ulimit -v 2097152`),
2 GiB RSS cap, single-thread BLAS/OpenMP + `MALLOC_ARENA_MAX=2`.

## 7. Output root and five-file schema (absent until authorized execution)

Root
`.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`
is ABSENT (verified §10). Exactly five files, created as stubs BEFORE the
content opens, checkpointed after every (arm, block) record (same files, no
sidecars): `frozen_plan.json`, `input_and_predecessor_identity.json`,
`per_block_arm_outcomes.jsonl` (15 records at completion),
`aggregate_summary.json`, `report.md`. Scalar-only: never counts, sampled
symbols, truth vectors, decoded labels/keys, metric planes, raw rows, per-arm
orders, tag seeds or RNG state (banned-key walk in the focused tests). Per
record: arm/arm-index/kind/provenance, frame range, outcome bucket,
exact/label-match/tag-pass, L1/L2 invocation flags, K1/K2 and prefix lengths,
raw channel SER, per-layer/total NLL bits, actual key-dependent and
public-control bits, `arm_leakage/NLL` CE-normalized ratio (explicitly not
qualification efficiency), L1 correctness, wall, RSS HWM, Linux VmPeak/VmSize.

## 8. Gates, labels, no-threshold rule, oracle boundary and accounting

Integrity (frozen order, all persisted as booleans and all required):
`predecessor_construction_identity`; `hold_split_manifest_identity`;
`p18_block_range_identity`; `target_population_contract`;
`hold_population_exact` (400 frames / 102400 pairs / 256 rows per frame /
pair indices / symbol range); `blocks_exact_with_declared_remainder` (three
exact ranges per arm + unused remainder 4096 pairs);
`fifteen_records_exact`; `sc_calls_exact`; `tags_exact`;
`orders_valid_k_prefixes_within_registered_arms`;
`oracle_isolation`; `buckets_disjoint_exhaustive`; `undetected_zero`;
`nonfinite_zero`; `truth_isolation`; `disclosure_recount_exact`;
`one_open_per_protected_input`; `input_stat_unchanged`;
`no_unregistered_access`; `resource_limits_met_and_no_abort`.

The SC/tag gates are recomputed from the persisted records and require the
frozen full-invocation totals **exactly** (27/15); the only exception is a
registered resource stop, where the fully accounted partial transcript is
accepted and the resource gate is the label blocker (flagged R1). This is
stricter than P18's "at most" wording and follows this packet's "27 SC calls +
15 tags / Assert these counts" instruction: a legitimate `decode_failed`
block keeps its bucket and bits but shortens the transcript, so it surfaces as
`BLOCKED(sc_calls_exact)` (or `tags_exact`) rather than COMPLETE. The
Pre-EXECUTE reviewer may require the P18-style recomputed-maxima reading
instead; that decision must be taken before the single attempt.

Disclosure per fully invoked record: operational `5*(K1+K2)+64` key-dependent
bits (base 34119) and `10*N+63 = 327743` public-control bits per tag; control
`5*6492+64 = 32524` key-dependent bits per tagged record. Planned totals if
all invoked: 526,200 key-dependent bits and 4,916,145 public-control bits. An
independent literal transcript recount must equal the incremental totals with
zero mismatch. The NLL is the descriptive block cross-entropy in bits under
the fixed TRAIN prior; `raw_ser = mean(alice_symbol != bob_symbol)`.

Labels: every integrity gate true →
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` regardless of the
0/3..3/3 recovery pattern; any integrity/resource failure →
`BLOCKED(<earliest gate>)`. **There is no exact-count, Wilson, FER, winner,
monotonicity, promotion or recovery threshold anywhere in this gate**, and
recovery is never reinterpreted as an integrity gate. `undetected` is never
success. Non-monotone exact-count patterns are reported neutrally (no
monotonicity/superiority/winner claim). The oracle control is
provenance-isolated: it is excluded from every operational aggregate, and no
operational record may carry oracle conditioning.

## 9. No-rerun rule, budgets and frozen environment

After the single attempt: no repair, rerun, seed/N/K/floor/order/arm change,
re-tuning, cleanup, commit or push. Wall/RSS breaches abort-fill the remaining
(arm, block) slots, preserve checkpoints and finalize BLOCKED; MemoryError is
caught around the entire post-open path, checkpoints preserved and BLOCKED
finalized when possible. Env: `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`; 600 s external timeout; 2 GiB
virtual limit and 2 GiB RSS cap.

## 10. Forbidden paths and scope boundary

Forbidden: Model-F artifact, raw/real/held-out/EVAL frames, other N in the
frozen run, any added or changed arm/grid/interpolation/adaptive choice or
post-result arm, any construction path, BEC, transform/belief/list or
soft-marginal decoders, a second tag outside the registered arms,
fitting/sampling/shuffling on HOLD, any use of the remainder frames,
production benchmark, `results/` or `comparison_bench/outputs_comparison/`
writes, P12-P18 code or old-root modification, official prior/probe seed
reuse, commit/push. Scope is a descriptive real-input layer/backoff diagnostic
of the frozen V25 1M HOLD split; it is not real-frame FER, reconciliation
efficiency, leakage, key rate, scaling, qualification or promotion evidence,
and the oracle true-L1 arm is never an operational or deployable result.

## 11. Wave-A verification evidence (implementation time)

- Output root absent: the queue dir holds only `TASK_PACKET.md`, `STATUS.yaml`,
  `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P19_FREEZE.md`,
  `P19_IMPLEMENTATION_NOTES.md`. `holdout_backoff_diagnostic/` does not exist.
- NPZ stat metadata only: 25,166,822 bytes, mtime_ns 1787074449691122000;
  content never opened (reads/attempts used 0).
- HOLD parquet stat metadata only: 1,354,289 bytes, mtime_ns
  1789155517259296100; content never opened. Registered relative path
  resolved to the absolute path in §3 (exists).
- Split manifest read (JSON only): schema and 400/102400 verified as in §2.
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal to the
  stored freeze digest and the frozen flag; P16 root untouched (read-only
  stat: five files: construction 2581862 B, aggregate 2586645 B,
  frozen_plan 6991 B, per_block 42760 B, report 2529 B).
- P18 accepted root untouched (read-only stat: five files, mtimes 2026-09-16
  01:51/01:52).
- Fresh focused-test seeds 2026092070..076 appear in no tracked file outside
  the P19 test file (hidden-path repo search).
- Focused suite `test_nbpolar_holdout_backoff_diagnostic.py`: 30/30 green
  (fresh `/tmp` basetemp, pinned interpreter, `-p no:cacheprovider`).
- Packet-scoped predecessor suites: `test_nbpolar_operational_f13.py` 23/23
  green; `test_nbpolar_operational_f13_replication.py` +
  `test_nbpolar_holdout_microcheck.py` 51/51 green (same settings). No shared
  predecessor code was changed, so the full NB-Polar suite was not run (the
  packet permits the scoped set in that case; recorded in the notes).
- HEAD unchanged at `ab173f2a`; no commit (worktree carries only pre-existing
  unrelated modifications plus this wave's untracked additions).
