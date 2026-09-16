# P18 freeze — N=32768 1M-HOLD operational microcheck (Wave-A implementation)

Packet: `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK` (`TASK_PACKET.md`, 100
lines, frozen). Predecessor:
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE_ACCEPTED_MODEL_SAMPLED`
(P17 main-thread acceptance).
Wave-A scope ONLY: OpenSpec delta + implementation + tests + this freeze.
This document authorizes nothing. No box in `tasks.md` is checked by the
implementing session.

## 1. Mission

Run the accepted P16/P17 operational point exactly once on the only three
complete, non-overlapping N=32768 blocks available in the V25 1M HOLD
split (frames 1600..1983 of the 1M `pairs.parquet`). This is a real-input
microcheck of loading, ordering, fixed-TRAIN prior use, decoder behavior
and accounting. It is not a FER gate and has no recovery threshold: 0..3
exact outcomes are descriptive, and only integrity or resource failures
produce `BLOCKED(<earliest gate>)`.

## 2. Fixed identities (verified in this session before any protected open)

P16 accepted file
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
(read JSON only; P16 immutable, never modified):

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
(JSON read only; the manifest owned by the same run_04 as the TRAIN NPZ):

| item | verified value |
|---|---|
| schema | `nbldpc_v25_split_manifest_v1` |
| 1M source tag | `type2_1M_20260121_184040` |
| HOLD frames / pairs | 400 / 102400 (frozen requirement) |
| TRAIN / VAL context | 1200 frames / 307200 pairs, 400 frames / 102400 pairs |

Any mismatch stops before any root exists and before either protected
content open, consuming no read and no attempt.

## 3. Protected inputs, one content open each

Both are read-only inputs. Each is content-opened **exactly once**; the
single scientific attempt is consumed at the **first** protected content
open (the NPZ). Module-level guards refuse a second content open of
either input.

| input | registered path (repo-relative) | resolved absolute path | expected size (stat only) |
|---|---|---|---|
| V25 1M TRAIN NPZ | `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz` (cross-checkout absolute) | same | 25,166,822 bytes (refusal if different) |
| 1M HOLD pairs parquet | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet` | `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet` | 1,354,289 bytes (provenance only; never a refusal) |

The accepted pairs loader is the repo-convention loader
`comparison_bench/src/comparison_bench/io/pairs_loader.py`
(`load_pairs_table` + `normalize_pair_columns`), required schema
`frame_id` / `pair_idx` / `alice_symbol` / `bob_symbol` with integer
coercion. It is the same loader used by the V25 gate registry
(`nonbinary_v25_gate.SOURCES`) and the V64 fresh registry, i.e. the
registered `v13r3fresh_pairs_20260816/<source_tag>/pairs.parquet`
convention resolved from the repository root. Only HOLD frames
1600..1999 are selected after loading; no other rows are used for
anything. Per-input content opens, attempt consumption and
before/after (size, mtime_ns) stats are recorded in
`input_and_construction_identity.json`.

Refusal ordering (all before any content open, consuming nothing):
absent output root → CLI parse → frozen flag contracts (floor/source/N/K/
chunk-rows/tag-bits/hold-frames/block-frames/remainder-frames/tag-master)
→ construction digest-flag pin → P16 construction identity → split
manifest identity → one-open guards → NPZ/HOLD path existence and
stat-only checks. After the first content open there is no repair, rerun,
seed/N/K/floor/order/change, tuning or cleanup.

## 4. Deterministic HOLD block formation and remainder

Sort HOLD rows by `(frame_id, pair_idx)`; require exactly 400 frames
1600..1999, exactly 256 rows per frame, `pair_idx` exactly 0..255 per
frame and symbols 0..1023. Blocks (each 128 frames = 32768 pairs):

| block | frames | pairs |
|---|---|---|
| 0 | 1600..1727 | 32768 |
| 1 | 1728..1855 | 32768 |
| 2 | 1856..1983 | 32768 |
| unused remainder | 1984..1999 | 4096 (recorded, never used) |

No shuffle, resampling, overlap, padding, pooling with TRAIN/VAL/P16/P17
or fitting on HOLD is permitted; the runner contains no random-number
generator path at all.

## 5. Frozen command (verbatim; P18-05 block constructed from the P17 pattern)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_microcheck --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --hold-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 --tag-master 2026092050 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck
```

Sixteen flags, all required, no production default. The packet has no
P18-05 command block, so this command was constructed from the P17
pattern with P18 values; the five flags absent from the P17 command
(`--hold-pairs`, `--hold-frames`, `--block-frames`, `--remainder-frames`,
`--tag-master`) are invented and flagged for Pre-EXECUTE review. Budgets:
600 s external timeout, 2 GiB virtual limit (`ulimit -v 2097152`), 2 GiB
RSS cap, single-thread BLAS/OpenMP + `MALLOC_ARENA_MAX=2`.

## 6. Output root and five-file schema (absent until authorized execution)

Root
`.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`
is ABSENT (verified §10). Exactly five files, created as stubs BEFORE the
content opens, checkpointed after every block (same files, no sidecars):
`frozen_plan.json`, `input_and_construction_identity.json` (predecessor
and manifest identity scalars + order heads only; full orders stay in the
immutable P16 file + input stat metadata + open/attempt accounting),
`per_block_outcomes.jsonl` (3 records at completion),
`aggregate_summary.json`, `report.md`. Scalar-only: never counts, sampled
symbols, truth vectors, decoded labels/keys, metric planes, raw rows, tag
seeds or RNG state (banned-key walk in the focused tests). Per record:
frame range, raw channel SER, per-layer/total NLL bits, outcome bucket,
L1 correctness, tag result, 34119/327743 constants, actual key-dependent
and public-control bits, wall, RSS HWM, Linux VmPeak/VmSize.

## 7. Gates, labels, no-threshold rule and accounting

Integrity (frozen order, all persisted as booleans and all required):
predecessor_construction_identity; hold_split_manifest_identity;
target_population_contract; hold_population_exact (400 frames / 102400
pairs / 256 rows per frame / pair indices / symbol range);
blocks_exact_with_declared_remainder (three exact ranges + unused
remainder 4096 pairs); orders_valid_k_replay_f_within_budget;
sc_calls_exact (one L1 + one L2 per executed block recomputed from the
records, at most 6); tags_exact (at most 3, recomputed); buckets
disjoint/exhaustive; truth_isolation; undetected_zero; nonfinite_zero;
disclosure_recount_exact; one_open_per_protected_input;
input_stat_unchanged; no_unregistered_access;
resource_limits_met_and_no_abort. The SC-call and tag gates are
recomputed maxima, so a legitimate `decode_failed` block (no tag, one
call) never becomes an integrity failure; only undetected/nonfinite/
resource/truth/accounting failures block.

Disclosure per fully invoked block: `5*(K1+K2)+64 = 34119` key-dependent
bits and `10*N+63 = 327743` public-control bits per tag; partial failure
counts only actually disclosed bits; an independent literal transcript
recount must equal the incremental totals with zero mismatch. The NLL is
the descriptive block cross-entropy in bits under the fixed TRAIN prior
(`l1 = sum_i -log2 p1[high_i,bob_i]`,
`l2 = sum_i -log2 p2[high_i,bob_i,low_i]`, `high = A//32`, `low = A%32`);
`raw_ser = mean(alice_symbol != bob_symbol)`. `34119 /
observed_block_NLL_bits` is reported per block as a sample
cross-entropy-normalized disclosure ratio and is explicitly NOT
qualification reconciliation efficiency.

Labels: every integrity gate true →
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`
regardless of 0..3 exact outcomes; any integrity/resource failure →
`BLOCKED(<earliest gate>)`. **There is no exact-count, Wilson, FER,
winner, promotion or recovery threshold anywhere in this gate**, and
recovery is never reinterpreted as an integrity gate. `undetected` is
never success.

## 8. No-rerun rule, budgets and frozen environment

After the single attempt: no repair, rerun, seed/N/K/floor/order/change,
re-tuning, cleanup, commit or push. Wall/RSS breaches abort-fill the
remaining blocks, preserve checkpoints and finalize BLOCKED; MemoryError
is caught around the entire post-open path, checkpoints preserved and
BLOCKED finalized when possible. Env: `OPENBLAS_NUM_THREADS=1`,
`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`; 600 s
external timeout; 2 GiB virtual limit and 2 GiB RSS cap.

## 9. Forbidden paths and scope boundary

Forbidden: Model-F artifact, raw/real/held-out/EVAL frames, other N in
the frozen run, any construction path, any second arm or retry, BEC,
adaptive/FWHT/APP/SCL decoders, second tag, fitting/sampling on HOLD,
production benchmark, `results/` or `comparison_bench/outputs_comparison/`
writes, P12-P17 code or old-root modification, official prior/probe seed
reuse, commit/push. Scope is a real-input operational microcheck of the
frozen V25 1M HOLD split; it is not real-frame FER, reconciliation
efficiency, leakage, key rate, scaling, qualification or promotion
evidence.

## 10. Wave-A verification evidence (implementation time)

- Output root absent: queue dir holds only `TASK_PACKET.md`, `STATUS.yaml`,
  `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P18_FREEZE.md`,
  `P18_IMPLEMENTATION_NOTES.md`. `holdout_microcheck/` does not exist.
- NPZ stat metadata only: 25,166,822 bytes, mtime_ns 1787074449691122000;
  content never opened (reads/attempts used 0).
- HOLD parquet stat metadata only: 1,354,289 bytes, mtime_ns
  1789155517259296100; content never opened. Registered relative path
  resolved to the absolute path in §3 (exists).
- Split manifest read (JSON only): 849 bytes, schema and 400/102400
  verified as in §2.
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal to the
  stored freeze digest and the frozen flag; P16 root untouched (read-only
  stat: five files: construction 2581862 B, aggregate 2586645 B,
  frozen_plan 6991 B, per_block 42760 B, report 2529 B).
- Frozen tag master 2026092050 and the fresh focused-test seeds
  2026092060..066 appear in no tracked `.py`, `.json`, `.yaml` or `.md`
  outside the P18 code, tests, packet, spec, task section and P18 queue
  documents (hidden-path repo search).
- Focused suite `test_nbpolar_holdout_microcheck.py`: 26/26 green (fresh
  `/tmp` basetemp, pinned interpreter, `-p no:cacheprovider`).
- Full NB-Polar suite (`test_nbpolar_*.py`): 409 tests green (same
  settings); baseline before this wave 383, all green (383 + 26 = 409).
- Interrupted-run resumption: the final focused file holds 26 tests and
  the full suite 409; both were re-run green in the resuming Wave-A
  session (same pinned interpreter, fresh `/tmp` basetemps). The output
  root remains absent and reads/attempts remain 0.
- HEAD unchanged at `ab173f2a`; no commit (worktree carries only
  pre-existing unrelated modifications plus this wave's untracked
  additions).
