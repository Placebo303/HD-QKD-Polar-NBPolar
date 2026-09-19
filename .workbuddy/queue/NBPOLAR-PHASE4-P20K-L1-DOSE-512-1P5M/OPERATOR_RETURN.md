# P20K Stage-B OPERATOR_RETURN (single authorized attempt, descriptive only)

- Packet: `NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M` (Tier-Y). Operator: Stage-B one-shot.
- Branch: `codex/nbpolar-phase0`, HEAD `faac0411` (matches PRE_EXECUTE_REVIEW provenance).
- Pre-execution re-verified: output root `l1_dose_512_1p5m/` ABSENT (stat no-such-file);
  frozen quadruple ΔK1=+512 / 1.5M TRAIN 1152..1535 (3 blocks) + remainder 1536..1659
  never-used / caps 34119-36679-32524+327743 / tag-master 2026092250 / K1 319→831 / K2 6492;
  budget 600 s / 2 GiB / single-thread; STATUS protected+decoder authorized true;
  PRE_EXECUTE PASS_CONDITIONAL (§4 standing-auth ruling, P20K-only).
- Module `FROZEN_COMMAND` import check: renders identical argv to FREEZE §10 (consistency True).
- Prior digest pre-check (worktree-file read, never a counts open):
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` match;
  lambda 137.3823795883264 / floor 1e-15 / keys exact-10 / H literals match.
- Transcription statement: the user-pasted command below was compared field-by-field
  against FREEZE §10 + module `FROZEN_COMMAND`; it matches verbatim — NO correction.

## Actual executed command (verbatim, one-shot)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_dose_512_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 1152 1535 --block-frames 128 --remainder-frames 1536 1659 --tag-master 2026092250 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m
```

- Exit code: 0. Stdout tail: 9 records, `integrity_all_pass: true`,
  `outcome_label: TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE`.
- Attempt consumption: first protected content open consumed DEV 1/1 + attempt 1/1
  in this single run; no reopen, no rerun, no tuning. Any repeat remains forbidden.

## Five files + gate statistics

Root `.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m/`:
`frozen_plan.json`, `input_and_predecessor_identity.json`,
`per_block_arm_outcomes.jsonl` (9 records), `aggregate_summary.json`, `report.md`.
Integrity: 21/21 gates PASS (`failing_integrity_gates: []`, `integrity_all_pass: true`):
predecessor_construction_identity / dev_split_manifest_identity /
dev_block_range_identity (sextuple) / calibration_identity /
target_population_contract / dev_population_exact / blocks_exact_with_declared_remainder /
nine_records_exact / sc_calls_exact (15) / tags_exact (9) /
orders_valid_k_prefixes_within_registered_arms / oracle_isolation /
buckets_disjoint_exhaustive / undetected_zero / nonfinite_zero / truth_isolation /
disclosure_recount_exact / one_open_per_protected_input / input_stat_unchanged /
no_unregistered_access / resource_limits_met_and_no_abort.
Wall 107.644398 s; peak RSS 558936064 B; resource stop not fired.

## Per-arm exact / L1 correctness / first-error endpoints (coordinate facts only)

| block | frames | arm | K1/K2 | outcome | exact | l1_exact | hard_l2 | oracle_l2 | pair | first coord/layer | raw SER |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1152..1279 | E0_sc_base | 319/6492 | verify_failed | F | F | F | — | F | 16/L1 | 0.258362 |
| 0 | 1152..1279 | E1_L1plus512 | 831/6492 | verify_failed | F | F | F | — | F | 3/L1 | 0.258362 |
| 0 | 1152..1279 | E2_true_l1 (oracle) | 0/6492 | exact | T | — | — | T | — | — | 0.258362 |
| 1 | 1280..1407 | E0_sc_base | 319/6492 | verify_failed | F | F | F | — | F | 7/L1 | 0.253876 |
| 1 | 1280..1407 | E1_L1plus512 | 831/6492 | verify_failed | F | F | F | — | F | 5/L1 | 0.253876 |
| 1 | 1280..1407 | E2_true_l1 (oracle) | 0/6492 | exact | T | — | — | T | — | — | 0.253876 |
| 2 | 1408..1535 | E0_sc_base | 319/6492 | verify_failed | F | F | F | — | F | 3/L1 | 0.257385 |
| 2 | 1408..1535 | E1_L1plus512 | 831/6492 | verify_failed | F | F | F | — | F | 2/L1 | 0.257385 |
| 2 | 1408..1535 | E2_true_l1 (oracle) | 0/6492 | exact | T | — | — | T | — | — | 0.257385 |

- E0 0/3 exact; E1 0/3 exact (dK1=512, rule `frozen-order-prefix-extension`,
  keyΔ +2560 vs base); E2 3/3 exact at base K2, provenance ORACLE_TRUE_L1_CONTROL,
  deployable=false, isolated from every operational aggregate (never a correction result).
- `e1_restored_count` analogue: 0/3 (blk0 E0 fail→E1 fail; blk1 E0 fail→E1 fail;
  blk2 E0 fail→E1 fail). Zero FER /晋级 claim; descriptive only.
- Same-block E0→E1 coordinate facts only (no deferral/saturation verdict here):
  blk0 16/L1→3/L1; blk1 7/L1→5/L1; blk2 3/L1→2/L1. All six operational first
  errors are L1-layer. `undetected` 0 (isolated, never success); `nonfinite` 0;
  `decode_failed` 0; `resource_abort` 0.
- E2 note: oracle arm conditions on true L1 at base K2 and is excluded from
  operational counts; it never becomes operational.

## Accounting identities (recount-0)

- SC: 15 total = 3 blocks × (E0 2 + E1 2 + E2 1); per-record `sc_calls_this_record`
  derived recomputation equals counters; `sc_calls_exact` PASS.
- Tags: 9 total = 9 records × 1; `tags_exact` PASS.
- Key bits: total 309966 = E0 102357 (3×34119) + E1 110037 (3×36679) + E2 97572
  (3×32524); operational 212394 + oracle 97572; E1Δ vs base exactly +2560 = 5·512
  per block. Public bits: total 2949687 = 9×327743. `disclosure_recount_exact` PASS
  (mismatch 0).
- Ratios descriptive: base 34119/327680 ≈ 10.41%; E1 36679/327680 ≈ 11.19% — far
  below raw; CE-normalized ratios are NOT qualification efficiency.

## Consumption counts

- Counts-calibration opens 0/0 (V25 NPZ never opened; prior load is a worktree-file
  read behind the digest gate; no NPZ loader in runner).
- DEV open 1/1 SPENT (first DEV content open in this run); HOLD 0/1 untouched.
- Attempts 1/1 SPENT. No second attempt, no reopen, no refit, no retune.

## 2M pristine confirmation

- The 2M session file (`type2_2M_20260121_183657`) was never opened, statted,
  listed, or read by this operator in any form (pristine by non-access; the only
  2M string in evidence is the runner's cross-file refusal literal).
- 1M full pool fail-closed (refused by cross-file gate first); P20H DEV 0..383 /
  P20I DEV 384..767 / P20J DEV 768..1151 excluded; remainder 1536..1659 counted
  (124 frames / 31744 pairs) and never decoded.

## Not run by this operator

- Pre-RESULT review (independent thread) and main-thread acceptance: PENDING.
  This return marks nothing accepted and authorizes nothing further.
- No commit/push; no `results/` or `comparison_bench/outputs_comparison/` writes;
  no SCL/new kernel/model/schema; no FER/qualification/promotion language.

## Blocker

- None. First (and only) attempt completed with exit 0 and all gates PASS.
  Awaiting independent Pre-RESULT review + main-thread acceptance.
