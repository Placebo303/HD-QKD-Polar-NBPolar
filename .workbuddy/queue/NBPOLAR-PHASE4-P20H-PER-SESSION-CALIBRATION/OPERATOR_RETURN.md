# P20H Stage-B operator return (single authorized execution)

- Packet: `NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION` (Tier-Y). Operator: Stage-B
  executor. No self-acceptance; Pre-RESULT review + main-thread acceptance pending.
- Branch at execution: `codex/nbpolar-phase0`. Interpreter:
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (frozen path).
- Pre-execution re-verification (all PASS before the single attempt):
  1. Output root `per_session_confirmation/` ABSENT by stat (no such file or directory).
  2. Module `FROZEN_COMMAND` (import-printed) byte-identical to `P20H_FREEZE.md` §10
     Stage-B command; `--prior-digest` appears nowhere in it (`HAS_PRIOR_DIGEST_FLAG=False`).
  3. Prior digest precheck via the frozen `canonical_prior_digest` function on the
     Stage-A product: `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
     == frozen pin → match True.
  4. Frozen quadruple pinned: K1 319 / K2 6492 (+1024 → 7516), floor 1e-15, N 32768,
     construction digest `055c90…faea1b`, DEV 0..383 / remainder 384..1659,
     tag master 2026092220. Budget env: single-thread BLAS/OpenMP,
     `MALLOC_ARENA_MAX=2`, `ulimit -v 2097152`, `timeout 600`.
- CORRECTION DECLARED (freeze-original priority, per packet instruction): the
  delegating prompt transcribed a Stage-B command containing `--counts
  …/run_04/channel_counts.npz` and `--prior-digest e8dd078a0c3f…4c5`. The freeze
  original (§10, also equal to module `FROZEN_COMMAND`) is authoritative and
  contains NEITHER flag: Stage B loads `--prior …/calibrated_prior.npz` (digest
  gate internal, no `--prior-digest` CLI flag exists) and never opens the V25
  counts NPZ (`counts_content_opens` stays 0). The transcribed digest value also
  differs from the frozen pin; the frozen pin
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  (recalibrated_literals.json / calibration_input_identity.json) was used.
  Executed command below is the freeze verbatim.

## Actual executed command (verbatim, exit 0, one-shot)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_per_session_confirmation --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 0 383 --block-frames 128 --remainder-frames 384 1659 --tag-master 2026092220 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation
```

- Start ~00:33 +0800 2026-09-19, end ~00:35 (wall 114.272383 s per aggregate;
  P20C-class reference ~92.9 s; inside budget). Exit code 0, no retry, no reopen,
  no refit. Stdout tail:
  `{"analysis": "nbpolar-p20h-per-session-calibration", "b1_restored_count": 0,
  "integrity_all_pass": true, "operational_exact_count": 0, "records_completed": 9,
  "outcome_label": "TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE", …}`.

## Digest-gate results

- Prior digest (Stage-B `calibration_identity` gate): frozen pin
  `e8dd078a…e43b` matched the loaded `calibrated_prior.npz` → gate true (run
  would have refused before any SC call on mismatch; no refusal occurred).
- Recalibrated literals (`target_population_contract` gate, recomputed H1/H2
  within 1e-12 + column normalization): H1 2.006647056368773 / H2
  1.9017235959286112 / TOTAL 3.908370652297384 → gate true.
- Construction digest `055c90…faea1b` recomputed match → gate true.
- DEV source pin: size 1869178 B / sha `ca351e52…a06b` / tag `1p5M` → cross-file
  gate true; 1M + 2M paths refused by literal (recorded in artifact, never opened).

## Gate statistics (21/21 PASS, failing [])

All true: `predecessor_construction_identity`, `dev_split_manifest_identity`,
`dev_block_range_identity` (triple: cross-file → intra-file VAL-first →
calibration-identity), `calibration_identity`, `target_population_contract`,
`dev_population_exact` (384 frames / 98304 pairs / 256 rows/frame),
`blocks_exact_with_declared_remainder` (3 DEV ranges + remainder 1276 frames /
326656 pairs never decoded), `nine_records_exact`, `sc_calls_exact` (15),
`tags_exact` (9), `orders_valid_k_prefixes_within_registered_arms`,
`oracle_isolation`, `buckets_disjoint_exhaustive`, `undetected_zero`,
`nonfinite_zero`, `truth_isolation`, `disclosure_recount_exact` (mismatch 0),
`one_open_per_protected_input`, `input_stat_unchanged`, `no_unregistered_access`,
`resource_limits_met_and_no_abort` (no abort, RSS peak 558710784 B ≈ 533 MB < 2 GiB).

## Per-arm exact + endpoint table (descriptive, B2 oracle isolated)

| arm | blk | frames | outcome | l1_exact | hard_l2_exact | oracle_l2_exact | pair_exact | SC | first_err | raw SER | key bits | pub bits | K2/dK2/dkbit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0_sc_base | 0 | 0-127 | verify_failed | False | False | — | False | 2 | 16/L1 | 0.2563 | 34119 | 327743 | 6492/0/0 |
| B1_L2plus | 0 | 0-127 | verify_failed | False | False | — | False | 2 | 16/L1 | 0.2563 | 39239 | 327743 | 7516/1024/5120 |
| B2_true_l1_diagnostic (oracle) | 0 | 0-127 | exact | — | — | True | — | 1 | — | 0.2563 | 32524 | 327743 | 6492/0/0 |
| B0_sc_base | 1 | 128-255 | verify_failed | False | False | — | False | 2 | 6/L1 | 0.2541 | 34119 | 327743 | 6492/0/0 |
| B1_L2plus | 1 | 128-255 | verify_failed | False | False | — | False | 2 | 6/L1 | 0.2541 | 39239 | 327743 | 7516/1024/5120 |
| B2_true_l1_diagnostic (oracle) | 1 | 128-255 | exact | — | — | True | — | 1 | — | 0.2541 | 32524 | 327743 | 6492/0/0 |
| B0_sc_base | 2 | 256-383 | verify_failed | False | False | — | False | 2 | 8/L1 | 0.2551 | 34119 | 327743 | 6492/0/0 |
| B1_L2plus | 2 | 256-383 | verify_failed | False | False | — | False | 2 | 8/L1 | 0.2551 | 39239 | 327743 | 7516/1024/5120 |
| B2_true_l1_diagnostic (oracle) | 2 | 256-383 | exact | — | — | True | — | 1 | — | 0.2551 | 32524 | 327743 | 6492/0/0 |

\* All B2 records carry `sc_calls_this_record: 1` (aggregate
`sc_calls: 15` = 3 blocks × (2+2+1)). Outcome totals: exact 3 (all oracle),
verify_failed 6 (all operational), undetected 0, decode_failed 0, nonfinite 0,
resource_abort 0. `b1_restored_count` (B0 fail → B1 exact): 0/3 — no restoration
event on calibrated blocks; B1 maintain count likewise 0/3 (B0 exact nowhere).
Zero-FER/晋级: none claimed (descriptive COMPLETE regardless of count per §7).

## Accounting identities (all exact)

- Key bits: 3×34119 (102357) + 3×39239 (117717) + 3×32524 (97572) = 317646
  (operational 220074 + oracle 97572); B1−base delta exactly +5120 = 5×1024 per block.
- Public bits: 9×327743 = 2949687. Ratios vs raw (327680/block): base 0.10412292
  (~10.41%), B1 0.11974792 (~11.97%) — far below raw; CE ratios descriptive only.
- SC 15/15, tags 9/9, records 9/9; recount mismatch 0 (gate true).

## Consumption counters

- Counts-calibration open: 1/1 (spent Stage A, unchanged).
- DEV open: 0→1 SPENT (first DEV content open consumed the single attempt).
- Prior file load: 1 worktree-file read (not a protected open; `counts_content_opens`
  0 in Stage B). HOLD reads 0/1 untouched. Attempt: 0→1 SPENT. No reopen/refit/
  second calibration — any repeat forbidden and none performed.

## 2M pristine confirmation

- By non-access (packet rule: even stat violates): no 2M open/stat/list/read was
  performed in this stage; the runner's 2M refusal is a string literal recorded in
  `input_and_predecessor_identity.json`/`aggregate_summary.json` (`refused_2m_path`
  pins the 2M filename without touching it). 2M remains RESERVED pristine.

## Files

- Stage-B root (exactly five, created pre-open, checkpointed per (arm, block)):
  `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9), `aggregate_summary.json`, `report.md`.
- This return: `OPERATOR_RETURN.md`. `STATUS.yaml` updated (state
  STAGE_B_EXECUTED_AWAITING_PRE_RESULT, dev 1/1, attempts 1/1, result label).
- Untouched: `results/`, `comparison_bench/outputs_comparison/`, P16 root,
  P12–P20G roots, `src/`/`experiments/`/`tools/`. No commit/push. No self-acceptance.

## Not run in this stage

Pre-RESULT review, memory triage, main-thread acceptance, any follow-up branch
(§16 efficiency / P20D / minimality / 2M replication — planning input only after
acceptance, never an in-packet verdict).
