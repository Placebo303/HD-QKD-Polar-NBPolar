# P20J Stage-B OPERATOR_RETURN (single authorized attempt SPENT — descriptive, no self-acceptance)

- Packet: `NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M` (Tier-Y). Operator: Stage-B one-shot.
- Branch: `codex/nbpolar-phase0`, HEAD `faac0411`. Interpreter: frozen-command-family
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (this checkout carries no `.venv`).
- No freeze-transcription correction: the command below is byte-consistent with
  `P20J_FREEZE.md` §10 and the module `FROZEN_COMMAND` (import-printed pre-run).

## Actual executed command (verbatim)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && ulimit -v 2097152 && timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_dose_escalation_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 768 1151 --block-frames 128 --remainder-frames 1152 1659 --tag-master 2026092240 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/l1_dose_escalation_1p5m
```

- Start: 2026-09-18T20:26:29Z. End: 2026-09-18T20:28:19Z. Exit: 0. Wall 107.75 s
  (budget 600 s), peak RSS 558669824 B (~533 MB, budget 2 GiB), single thread.
- Pre-run gates (all PASS): output root ABSENT (stat confirmed); module
  `FROZEN_COMMAND` import-print consistent; `--prior` digest precheck
  `e8dd078a…e43b` match + lambda `137.3823795883264` + floor `1e-15` + 10-key set
  (worktree-file read only, counts 0/0 unaffected).

## Gate statistics (21/21 PASS, `integrity_all_pass: true`, failing `[]`)

`predecessor_construction_identity` / `dev_split_manifest_identity` /
`dev_block_range_identity` (quintuple: cross-file 1.5M pin first, VAL-before-HOLD
intra-file, P20H-DEV 0..383 exclusion, P20I-DEV 384..767 exclusion,
calibration-identity) / `calibration_identity` / `target_population_contract` /
`dev_population_exact` (384 frames / 98304 pairs / 256 rows/frame) /
`blocks_exact_with_declared_remainder` (remainder 1152..1659 = 508/130048 counted,
never decoded) / `nine_records_exact` / `sc_calls_exact` (15) / `tags_exact` (9) /
`orders_valid_k_prefixes_within_registered_arms` / `oracle_isolation` /
`buckets_disjoint_exhaustive` / `undetected_zero` / `nonfinite_zero` /
`truth_isolation` / `disclosure_recount_exact` (recount-0) /
`one_open_per_protected_input` / `input_stat_unchanged` / `no_unregistered_access` /
`resource_limits_met_and_no_abort` (no abort). Outcome label:
`TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_ESCALATION_1P5M_COMPLETE` (descriptive only).

## Per-arm exact counts + L1 correctness

- D0_sc_base (K1=319/K2=6492, operational): 0/3 exact, all `verify_failed`.
- D1_L1plus (K1=575/K2=6492, operational, ΔK1=+256 order-prefix of the SAME frozen
  P16 L1 order, keyΔ +1280): 0/3 exact, all `verify_failed`. L1 correctness pinned
  by `orders_valid_k_prefixes_within_registered_arms` + per-record disclosure triple
  (ΔK1=256, order-prefix, +1280 vs base).
- D2_true_l1_diagnostic (oracle, deployable=false, isolated): 3/3 exact.
- `d1_restored_count` analogue: 0/3 (D0 fail → D1 exact on zero new-segment blocks).
- `undetected`: 0 (isolated, never success). `decode_failed`/`nonfinite`/
  `resource_abort`: 0. Zero FER/promotion claim; D2 never operational.

## First-error layer + endpoint table (all six operational first errors L1-layer)

| block (frames) | D0 outcome / first error | D1 outcome / first error | D2 |
|---|---|---|---|
| blk0 768..895 | verify_failed, 14/L1 (l1 F, hard_l2 F, pair F) | verify_failed, 23/L1 (moved later) | exact (oracle_l2 T) |
| blk1 896..1023 | verify_failed, 6/L1 | verify_failed, 25/L1 (moved later) | exact |
| blk2 1024..1151 | verify_failed, 1/L1 | verify_failed, 21/L1 (moved later) | exact |

Reading (descriptive): +256 moved every first-error coordinate later (14→23,
6→25, 1→21) but restored nothing — same sensitivity-without-restoration pattern
as P20I +128, at double the dose. Genuine L1-negative under the frozen +256 tier
(zero-restoration with D0 failures present); §16 branch decision belongs to
main-thread planning AFTER acceptance, never to this packet.

## Accounting identity

- Key bits: 306126 = 3×34119 (D0 102357) + 3×35399 (D1 106197) + 3×32524 (D2 97572)
  = operational 208554 + oracle 97572 (sum verified in aggregate file).
- Public bits: 2949687 = 9×327743. SC 15/15 derived, tags 9/9 derived, recount-0.
- Ratios vs raw (327680 bits/block): base 0.10412292 (~10.41%), D1 0.10802917
  (~10.80%) — far below raw; CE ratios descriptive, not efficiency.

## Consumption counts

- DEV open 1/1 SPENT (first content open; `dev_content_opens: 1`,
  `reopen_attempted: false`). Attempt 1/1 SPENT. No reopen, no rerun, no refit.
- Counts-calibration 0/0 (prior load is a frozen worktree-file read behind the
  digest gate; V25 counts NPZ never opened). HOLD 0/1 untouched.
- Five files present: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records), `aggregate_summary.json`, `report.md`.

## 2M pristine confirmation

`opened_content_paths` = exactly 2 (prior NPZ + 1.5M pairs.parquet); 1M path and
2M path both listed as REFUSED by the cross-file gate; `no_unregistered_access:
true`. Reserved 2M never opened/statted/listed. 1M pool untouched.

## Stages not run

Pre-RESULT review (pending), main-thread acceptance (pending). No follow-up
packet, no P20D, no efficiency/minimality work, no commit/push, no self-acceptance.
