# Stage-B operator return — NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M (Tier-Y ONE-SHOT)

- Packet: `NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M`, branch `codex/nbpolar-phase0`.
- Attempt: exactly one Stage-B run, consumed. No rerun, no tuning, no second attempt.
- Result label (descriptive, NOT acceptance): `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`.
- Blocker: none. All 25 integrity gates PASS; 9/9 records complete.
- Next gate: independent Pre-RESULT review awaiting (`pre_result_review: PENDING_INDEPENDENT_ADJUDICATION`). Operator marks nothing accepted.

## 1. Pasted-command transcription check (byte-identical — PASS)

- The pasted STEP-2 command's python argv is byte-identical to the module
  `FROZEN_COMMAND` (printed via `raw_prior_val_1p5m.FROZEN_COMMAND` repr) and to
  `P20M_FREEZE.md` §5 Stage-B block, including `--k1 331 --k2 6689`,
  `--dev-frames 1660 2043`, `--remainder-frames 2044 2212`,
  `--tag-master 2026092280`, construction digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`,
  order digest `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`.
- Pins: corrected-prior digest `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`,
  session H literals `0.02519949692375297 / 0.8003665547495433 / 0.8255660516732963`,
  budget literal `1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020`.
- No difference found; nothing corrected.

## 2. Preconditions (checked BEFORE running — all PASS)

1. Stage-B root `raw_prior_val_1p5m/` ABSENT (`stat` ENOENT, exit=1).
2. `raw_prior_1p5m.npz` canonical digest via authoritative
   `per_session_calibration.canonical_prior_digest` = `372dcc1c…f7d46ac` (match;
   keys exactly the frozen 10-key set; `lambda_star` 0.0, floor 1e-15, H literals match).
3. `raw_prior_orders_1p5m.json` file-bytes sha256 = `a9f18a9f…1da11bc638` (match).
4. P16 construction file present (digest re-verified by the runner: match).
5. Branch `codex/nbpolar-phase0`; no other packet's Stage-B root touched.

## 3. Exact command (the single attempt)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 1660 2043 --block-frames 128 --remainder-frames 2044 2212 --tag-master 2026092280 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m
```

- Start UTC: ~2026-09-19T02:52:03Z (first artifact `frozen_plan.json` mtime 10:52:03 +0800).
- End UTC: 2026-09-19T02:53:48Z (last artifact mtime 10:53:48 +0800).
- Exit code: 0. Wall: `wall_s` 104.848503 (in-artifact; elapsed ~105 s, within 600 s envelope).
- Peak RSS: `rss_bytes_peak` 556785664 (~531 MB, within 2 GiB cap).
- Stdout tail (single JSON line):
  `{"analysis": "nbpolar-p20m-raw-prior-val-1p5m", "g1_restored_count": 0, "integrity_all_pass": true, "operational_exact_count": 0, "out_root": ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m", "outcome_label": "TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE", "records_completed": 9}`
- No crash/execution-error; the identical-freeze repeat allowance was NOT used (zero repeats).

## 4. Five-file inventory (frozen out-dir)

- `frozen_plan.json` (3600 B): K1 331 / K2 6689 / K_total 7020; G0 319/6492;
  prior digest `372dcc1c…`; order digest `a9f18a9f…`; budget literal frozen-H display `…2963`.
- `input_and_predecessor_identity.json` (8281 B): construction digest match;
  S2-ii build∩DEV disjoint true; P20H/I/J/K + remainder exclusions true;
  HOLD 2213..2766 disjoint; input stats before==after (prior/DEV/lambda).
- `per_block_arm_outcomes.jsonl` (15672 B): 9 records (3 blocks x 3 arms).
- `aggregate_summary.json` (7331 B): outcome label + 25/25 gates + accounting.
- `report.md` (990 B): descriptive one-page summary.

## 5. Gate statistics (expect all-pass — ALL PASS)

- `integrity_all_pass: true`; `failing_integrity_gates: []` (25/25 true, incl.
  `undetected_zero`, `nonfinite_zero`, `oracle_isolation`, `truth_isolation`,
  `disclosure_recount_exact`, `one_open_per_protected_input`,
  `input_stat_unchanged`, `no_unregistered_access`,
  `resource_limits_met_and_no_abort`, `nine_records_exact`, `tags_exact`,
  `sc_calls_exact`, `genie_calls_exact`, `budget_literal_recomputed`).
- `undetected_count: 0` (isolated, never success); `nonfinite_count: 0`;
  no `decode_failed` / `resource_abort` / `error` outcomes (all 9 `verify_failed`);
  `recount_mismatch: 0`; tags 9/9; SC 15/15; Stage-B sampling 0.
- Key-dependent bits G0 34119 / G1 35164 / G2 33509; public 327743/tag;
  totals 308376 / 2949687 (recount exact).
- Honest note (non-blocking, gate PASS): the in-run recomputed H display reads
  `h2 0.8003665547495431 / h_total 0.8255660516732961` (last-ulp float repr vs the
  Stage-A frozen `…5433 / …2963`); K_total identical (7020) and
  `budget_literal_recomputed: true`.

## 6. Per-arm outcomes (descriptive only)

| block (frames) | G0 λ-control (319/6492) | G1 raw+session budget (331/6689) | G2 oracle true-L1 (K2 6689) |
|---|---|---|---|
| 0: 1660..1787 | verify_failed, first-error L1/coord 24, l1_exact false | verify_failed, first-error L2/coord 26, l1_exact TRUE | verify_failed, first-error L2/coord 26, oracle_l2_exact false |
| 1: 1788..1915 | verify_failed, first-error L1/coord 5, l1_exact false | verify_failed, first-error L1/coord 848, l1_exact false | verify_failed, first-error L2/coord 3646, oracle_l2_exact false |
| 2: 1916..2043 | verify_failed, first-error L1/coord 17, l1_exact false | verify_failed, first-error L2/coord 31, l1_exact TRUE | verify_failed, first-error L2/coord 31, oracle_l2_exact false |

- Exact counts: G0 0/3, G1 0/3, G2 0/3; operational exact 0/6; oracle exact 0/3.
- `g1_restored_count: 0`; maintain 0. First-error moves (G0→G1): L1→L2 (b0), L1→L1 (b1), L1→L2 (b2).
- Per-record floor-hit fields complete (e.g. G1 floor hits 43/82/25 vs G0 3064/2946/3100;
  `floor_hit_log_loss_bits`, `floor_hit_rate`, `raw_zero_count_hits` on every record).
- Oracle isolation: `oracle_truth_use` true ONLY on the 3 G2 records;
  `truth_leak_violation` false on all 9; G2 `deployable: false`.
- Descriptive observation (no verdict): the corrected prior moves the operational
  first error off L1 on 2/3 blocks (G1 L1-exact on b0/b2), but restores zero blocks;
  the oracle arm is non-exact on all 3 blocks at candidate K2. Branch reading per
  packet §16 stays planning input, never an in-packet verdict.

## 7. Read accounting (from artifacts only)

- Counts-calibration content opens: 0/0 (V25 counts NPZ never opened).
- DEV content opens: 1 → 0/1 SPENT-consumed at first DEV parquet open; HOLD 0/1 untouched
  (HOLD 2213..2766 disjoint, never opened).
- Attempts: 1/1 SPENT (`attempts_consumed_by_this_run: 1`, `retries: 0`, `reopen_attempted: false`).
- Worktree-file loads (registered, one-open-guarded): raw prior 1 + P20H calibrated
  (G0 λ-control) 1; opened==registered (3 paths); input stats unchanged.
- 1M/2M non-access: the runner pins `refused_1m_path` and `refused_2m_path` fail-closed;
  `no_unregistered_access: true`; 1M pool and reserved 2M never opened/statted/listed
  by this operator (2M stays pristine as the follow-up confirmation population).

## 8. P20M-R1..R8 (stage-appropriate, descriptive)

- R1: corrected-prior identity gate PASS (digest `372dcc1c…`, H/floor pins, `p_b` lineage carried in freeze).
- R2: session-derived point + order-file gates PASS (K1 331/K2 6689, order digest match,
  S2-ii disjointness, 2M non-access).
- R3: per-arm caps + recount PASS (34119/35164/33509 + 327743; mismatch 0).
- R4: operating-point swap rule frozen in `frozen_plan.json`, unchanged after execution.
- R5: endpoints separated; `undetected` isolated (0); oracle never operational;
  first-error rows + floor-hit fields complete on all 9 records.
- R6: one-shot Tier-Y honored (1 attempt, DEV 1/1, HOLD 0/1, no resource abort, no repeat used).
- R7: Pre-EXECUTE (prior/budget/gates/delta) is main-thread business — operator asserts
  nothing; Pre-RESULT PENDING independent adjudication; honest-scope §0 repeated below.
- R8: no commit/push; no writes outside the P20M packet dir + frozen out-dir;
  no `results/` or `comparison_bench/outputs_comparison/` writes.

## 9. Honest-scope statement (§0 verbatim)

this packet tests the corrected prior + session-derived budget at the operational point on the first genuinely out-of-sample 1.5M segment; it does not establish NB-Polar real-block recovery in general, does not close the 1M-HOLD thread, and the current published gates on DEV must not be confused with out-of-sample evidence.

## 10. Blocker-or-none

None. Single authorized attempt complete, exit 0, all gates pass, attempt consumed.
The operator never marks its own work accepted and authorizes nothing further.
