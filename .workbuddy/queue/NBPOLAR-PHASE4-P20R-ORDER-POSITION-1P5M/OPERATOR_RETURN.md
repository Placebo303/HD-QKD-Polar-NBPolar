# Stage-B Operator Return — NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M (Tier-Y)

- Date: 2026-09-19; operator: `coder-fast` Stage-B instance; branch `codex/nbpolar-phase0`.
- Return condition: **(a)** — single authorized attempt executed EXACTLY once, all
  stage-appropriate P20R-R1..R9 complete. No blocker. No rerun/tuning.
  Operator marks nothing accepted; `pre_result_review`/`main_thread_acceptance`
  stay PENDING.

## 1. Frozen command executed (byte-identical, once, exit 0)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_order_position_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest 6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78 --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 2044 2171 --block-frames 128 --remainder-frames 2172 2212 --tag-master 2026092340 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --new-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/new_l2_order_1p5m.json --new-order-digest c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/l2_order_position_1p5m
```

- Pre-conditions verified before execution: Pre-EXECUTE PASS on file; STEP-2
  pasted verbatim in the delegating turn; Stage-B root
  `l2_order_position_1p5m/` ABSENT (existence check); branch
  `codex/nbpolar-phase0`; STATUS set to `stage_b_authorized: true`,
  `decoder_execution_authorized: true`, `protected_data_read_authorized: true`,
  `planning_stage: STAGE_B_IN_PROGRESS`.
- Runner stdout (exit 0): `outcome_label =
  TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE`,
  `records_completed: 4`, `integrity_all_pass: true`,
  `operational_exact_count: 0`, `b_maintained_count: 0`,
  `b_restored_count: 0`, `d_maintained_count: 0`, `d_restored_count: 0`,
  set-delta `a 6689 / b 6689 / intersection 1213 / |A-B| 5476 / |B-A| 5476 /
  size-delta 0`.

## 2. Five-file inventory (Stage-B root PRESENT)

`.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/l2_order_position_1p5m/`:

| file | size (B) |
|---|---|
| `frozen_plan.json` | 287875 |
| `input_and_predecessor_identity.json` | 287845 |
| `per_block_arm_outcomes.jsonl` | 452774, 4 records |
| `aggregate_summary.json` | 292664 |
| `report.md` | 2034 |

Each of the 4 `per_block_arm_outcomes.jsonl` records carries the nine §7
scalars (eight X09-R1 + ninth U-domain `l2_fail_in_prefix_u_domain`,
arm-specific `l2_order_digest`) with correct nullability plus IR-1..IR-5 ALL
PRESENT (IR-1 64-bin histograms + 65 edges; IR-2 rank percentile; IR-3 exactly
two thresholds at 1.0×/2.0× record prefix-mean; IR-4 top-16 with 1-based ranks;
IR-5 capped 4096×2 float32 with `truncated: true`, `total_len: 32768`).

## 3. Per-arm exact counts + transition tables (descriptive only)

- Per-arm exact: A 0/1, B 0/1, C 0/1, D 0/1. Operational exact 0/2; oracle
  exact 0/2. All 4 records `verify_failed` (tag-verified non-exact);
  `undetected: 0`; `nonfinite: 0`.
- First errors (natural block symbol index, settled X09-R1 D4): A coord 133
  layer L2; B coord 0 layer L2; C coord 133 layer L2; D coord 0 layer L2.
  A/C fail in-prefix (`l2_fail_in_prefix: true`, U-domain `false`); B/D fail
  out-of-prefix (`false`/`false`). L1 exact: A/B `true`; oracles `null`.
- A→B transition table: `a_exact_b_exact 0 / a_exact_b_fail 0 /
  a_fail_b_exact 0 / a_fail_b_fail 1`. `b_maintained_count 0`,
  `b_restored_count 0` (descriptive: no restoration event on this block).
- C→D diagnostic (never operational): `c_exact_d_exact 0 / c_exact_d_fail 0 /
  c_fail_d_exact 0 / c_fail_d_fail 1`. `d_maintained_count 0`,
  `d_restored_count 0`.
- Order-set delta (byte-exact, recorded in `aggregate_summary.json` +
  identity): K2 6689; A disclosed 6689; B disclosed 6689; `size_delta_b_minus_a
  0`; intersection 1213; `|A-B| 5476`; `|B-A| 5476` (+ full sorted lists and
  rank-displacement tables).
- IR payload tables (descriptive): IR-2 rank-pct all n=4 median
  0.6644287109375 (min 0.329193115234375, max 0.999664306640625); A-operational
  0.999664306640625 (n=1); B-operational 0.329193115234375 (n=1); oracle median
  0.6644287109375 (n=2). IR-1 prefix/outside mass 6689/26079 per record;
  tail-8 mass A/C 8, B/D 4. IR-3 lo/hi above-counts A/C 1682/1648, B/D
  1703/1671 (fracs recorded per record). IR-4 top-16 in-prefix count 4 on all
  four records. IR-5 truncated-all `true`.

## 4. Split audit (split-counted)

- counts-calibration opens 0/0 (V25 counts NPZ never opened/statted/listed).
- VAL-remainder-DEV open 1/1 (first DEV content open consumed the single
  attempt; `attempts 0/1 → 1/1`; `reopen_attempted: false`; `retries: 0`).
- VAL-DEV 0, HOLD 0, 1M 0, 2M 0 in every form. 2M HOLD remainder 3556..3644
  counted never-decoded, never contacted beyond counting. Stub 2172..2212
  counted never-decoded. DEV block `2044..2171` (1 × 128 frames, 32768 pairs);
  S2-ii disjointness verified (`dev [2044,2171]` vs `build [0,1659]`,
  consumed-1M/1.5M/2M exclusions all disjoint).

## 5. Integrity-gate outcome

- `integrity_all_pass: true`; `failing_integrity_gates: []`. All 34 frozen
  gates true in order, incl. `reuse_prior_identity`, `reuse_alt_identity`,
  `alt_construction_budget_feasibility_replayed`,
  `order_derivation_identity`, `order_derivation_program_identity`,
  `frozen_order_identity_A`, `new_order_identity_B`, `k_literal_exact`,
  `budget_literal_replayed`, `dev_population_exact`,
  `blocks_exact_with_declared_remainder`, `four_records_exact`,
  `genie_calls_exact`, `sc_calls_exact`, `tags_exact`,
  `order_set_delta_recorded`, `hazard_instrumentation_complete`,
  `ir_payload_complete`, `oracle_isolation`, `undetected_zero`,
  `nonfinite_zero`, `truth_isolation`, `disclosure_recount_exact`,
  `one_open_per_protected_input`, `no_unregistered_access`,
  `resource_limits_met_and_no_abort`.

## 6. Key/public/tag recount + SC/tag/genie counters + resources

- Key-dependent bits 137346 (A/B 35164 each, C/D 33509 each; B−A Δ exactly 0,
  D−C Δ exactly 0); public bits 1310972 (327743 × 4); `recount_mismatch: 0`.
- SC calls 6/6 (A 2 + B 2 + C 1 + D 1); tag invocations 4/4 (all `tag_invoked:
  true`, all `tag_pass: false`); Stage-B sampling calls 0; Stage-A genie 0 +
  Stage-B genie 0 (no genie fields on any record).
- Wall 44.368862 s; RSS peak 546258944 B (~521 MiB); `resource_stop_fired:
  false`; external timeout 1200 s / virtual 2 GiB envelope met, no abort.

## 7. Changed files

- `STATUS.yaml` (authorization flags true; `attempts_used: 1`;
  `val_remainder_dev_reads_used: 1`; `stage_b_out_root: PRESENT`;
  `planning_stage: STAGE_B_COMPLETE_AWAITING_PRE_RESULT`; `next_gate:
  PRE_RESULT_REVIEW_PENDING`; pre-result/acceptance stay PENDING).
- New Stage-B root `l2_order_position_1p5m/` (five files above).
- This `OPERATOR_RETURN.md`.
- No other files written. `test_evidence_package.py` NOT run. No commit/push.
  `results/` untouched; `comparison_bench/outputs_comparison/` untouched by
  this run (the one `M` entry there,
  `test_fixtures/real_polar_max_pie_grid.csv`, is the pre-existing stat-dirty
  unrelated state already noted non-blocking in `PRE_EXECUTE_REVIEW.md`,
  mtime 19:36 predating this 23:22–23:23 run, zero content diff).

## 8. P20R-R1..R9 (stage-appropriate, Stage-B close)

R1 reuse/new-order read-only verified behind digest gates (prior
`372dcc1c…`, alt `6f4a4f7…`, frozen-A `a9f18a9f…`, new-B `c7853286…`,
program pin, set-delta recorded); R2 same-session S2-i replay + closed-range
exclusions + first-use VAL-remainder DEV consumed once; R3 preregistered caps
with recount 0 and size-delta 0; R4 single-factor order pins unchanged after
freeze; R5 endpoints separated, `undetected` isolated, nine scalars +
IR-1..IR-5 PRESENT on every record with truth-isolation intact; R6 one-shot
Tier-Y semantics (1 attempt, reads counts 0/0 + DEV 1/1 + VAL-DEV 0 + HOLD 0
+ 1M 0 + 2M 0, no abort); R7 Pre-EXECUTE PASS recorded, Pre-RESULT +
acceptance PENDING with main thread owning the label; R8 Stage-A 21/21 green
with zero-open audit carried (this return adds no test run per packet orders);
R9 D2 FEASIBLE replay + new-order gate both satisfied before DEV contact
(margin 3928.304784481981).

## 9. Honest-scope statement (verbatim)

single-block (1.5M VAL remainder) single-factor test of one alternate L2-order position rule under the frozen α1 construction at frozen disclosure with the mandatory H2 instrumentation; descriptive only; the VAL-remainder DEV block is consumed by this packet; the 41-frame stub and the 2M HOLD remainder stay untouched; no H2 verdict, no reliability claim; the H2 decision is analysis, not a block result.
