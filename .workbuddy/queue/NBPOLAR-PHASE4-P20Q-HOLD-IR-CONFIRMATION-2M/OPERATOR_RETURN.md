# Stage-B Operator Return — NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M

- Operator: Stage-B operator (coder-fast instance, session ses_f46416d10ffei5VCN8BiZ0bUjd).
- Branch: `codex/nbpolar-phase0`.
- Return condition: **(a)** — ALL stage-appropriate P20Q-R1..R9 complete. Single
  authorized attempt consumed (attempts 0/1 → 1/1). No rerun, no tuning, no seed
  change. `test_evidence_package.py` NOT run. No commit/push. Operator marks
  nothing accepted (`pre_result_review: PENDING`, `main_thread_acceptance: PENDING`).

## 1. Changed files

- `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/STATUS.yaml`
  (Stage-B flags + close counts; `pre_result_review`/`main_thread_acceptance` left PENDING).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/`
  (new Stage-B evidence root, exactly five files — was ABSENT at Pre-EXECUTE, verified
  by existence check before execution).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/OPERATOR_RETURN.md`
  (this file).
- No other files touched. No overwrite under `results/` or
  `comparison_bench/outputs_comparison/`.

## 2. Exact command executed (ONCE, byte-identical to P20Q_FREEZE.md §8)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_ir_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --source 2M --floor 1e-15 --n 32768 --k1 334 --k2 6746 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2916 3555 --block-frames 128 --remainder-frames 3556 3644 --tag-master 2026092330 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m
```

- Exit code: 0. No execution error; no repeat needed (identical-freeze repeat
  allowance unused).
- Stdout tail: `outcome_label =
  TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE`,
  `records_completed = 20`, `integrity_all_pass = true`,
  `operational_exact_count = 4`, `b_maintained_count = 0`,
  `b_restored_count = 4`, `d_maintained_count = 0`, `d_restored_count = 4`.

## 3. Five-file inventory (all PRESENT)

| file | size (B) | content |
|---|---|---|
| `frozen_plan.json` | 8876 | frozen pins (digests, K, blocks, tag domain, IR-3 multipliers, IR caps) |
| `input_and_predecessor_identity.json` | 9625 | reuse gate proofs + K/budget-literal replay + split + disjointness + IR pins |
| `per_block_arm_outcomes.jsonl` | 2248515 | **20 records** (5 blocks × A/B/C/D, block-major), each carrying the nine scalars + IR-1..IR-5 |
| `aggregate_summary.json` | 31145 | per-arm aggregates + maintenance tables + IR payload tables + integrity + accounting |
| `report.md` | 1818 | human-readable descriptive summary |

## 4. Reuse digest replays (all replay-EXACT at Stage B)

- Prior canonical digest: `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`
  (expected == recomputed; H recomputed `0.02566204884275839 / 0.8069006731309891 /
  0.8325627219737475`, within 1e-12 of frozen literals).
- Alt file-bytes digest: `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
  (expected == file digest; alpha 1.0; floor 1e-15).
- Order file-bytes digest: `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`
  (K1 334 / K2 6746 replayed).
- Construction digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  (expected == recomputed).
- Prior/alt/DEV input stats unchanged (before == after). Tag master 2026092330,
  prefix `nbpolar-p20q-hold-ir-2m-seed`, IR pins (64 bins / 1.0×+2.0× / top-16 /
  4096 cap) frozen.

## 5. Per-arm exact counts + maintenance (descriptive only)

- A_incumbent_L2_operational: **0/5 exact** (5 verify_failed).
- B_alt_L2_operational: **4/5 exact** (4 exact + 1 verify_failed).
- C_incumbent_L2_oracle: **0/5 exact** (5 verify_failed; diagnostic only).
- D_alt_L2_oracle: **4/5 exact** (4 exact + 1 verify_failed; diagnostic only).
- `b_maintained_count = 0` (A-exact blocks: 0, so vacuous); `b_restored_count = 4`
  (A-fail → B-exact on blocks 0..3; block 4 A-fail → B-fail).
- A→B transition: `{a_exact_b_exact: 0, a_exact_b_fail: 0, a_fail_b_exact: 4,
  a_fail_b_fail: 1}`.
- C→D transition (diagnostic only): `{c_exact_d_exact: 0, c_exact_d_fail: 0,
  c_fail_d_exact: 4, c_fail_d_fail: 1}`; `d_restored_count = 4`,
  `d_maintained_count = 0`.
- First-error layers: all A/C first errors L2; B/D null on restored blocks, L2 on
  block 4. L2-fail records: 12 total, ALL natural-in-prefix (X-domain True 12/12)
  but U-domain-out (False 12/12) — P20O-pattern continuity, descriptive only.
- `undetected = 0` (isolated, never success); `nonfinite = 0`.
- B-vs-A and D-vs-C key-bit deltas exactly 0 on every record.

## 6. Nine scalars + IR-1..IR-5 payload

- Missing nine-scalar cells over 20 records: **0**. `l2_prefix_len = 6746` on every
  record.
- Missing IR-field cells over 20 records: **0** (all IR-1..IR-5 PRESENT).
  IR-1: 65 edges / 64+64 counts per record; prefix mass 6746 + outside 26022 =
  32768 on every row; prefix-tail-8 mass 1..9 (alt rows ≤ incumbent rows per block).
  IR-2: 12 values (A-operational 5, median 0.8585; B-operational 1, 0.9894; oracle
  6, median 0.8830; all-median 0.8830, range 0.3802..0.9894).
  IR-3: lo = 1.0× / hi = 2.0× record prefix-mean; above-lo frac ~0.241..0.252,
  above-hi frac equal or one count lower (blocks 1/3 alt rows).
  IR-4: top-16 with 1-based ranks on every record; in-prefix counts 1..5 per row.
  IR-5: 4096 float32 + 4096 flags per record, `truncated = true` on all 20,
  `total_len = 32768` on all 20.
- `truth_leak_violation`: false on all 20 records. C/D `deployable = false`,
  `oracle_control = true` (oracle isolation holds).

## 7. Split open audit

- Counts-calibration opens: **0/0** (V25 counts NPZ never opened/statted/listed).
- HOLD-DEV opens: **1/1** (single parquet content open, consumed at first HOLD
  content open; `reopen_attempted: false`, `retries: 0`).
- VAL-DEV reads: **0**. VAL-remainder reads: **0**. 1M-pool reads: **0**.
  Any-1.5M reads: **0**. 2M TRAIN-as-DEV / 2M VAL access: none (gated disjoint).
- Registered content paths: exactly 3 (prior NPZ, alt NPZ, 2M pairs parquet);
  `no_unregistered_access: true`.

## 8. Integrity gates (30/30 true, `failing_integrity_gates: []`)

`predecessor_construction_identity`, `reuse_prior_identity`,
`reuse_alt_identity`, `alt_construction_budget_feasibility_replayed`,
`dev_split_manifest_identity`, `dev_block_range_identity`,
`order_derivation_identity`, `k_literal_exact`, `budget_literal_replayed`,
`target_population_contract`, `dev_population_exact`,
`blocks_exact_with_declared_remainder`, `twenty_records_exact`,
`genie_calls_exact`, `sc_calls_exact`, `tags_exact`,
`orders_valid_k_prefixes_within_registered_arms`,
`hazard_instrumentation_complete`, `ir_payload_complete`,
`floor_hit_rate_reported`, `oracle_isolation`, `buckets_disjoint_exhaustive`,
`undetected_zero`, `nonfinite_zero`, `truth_isolation`,
`disclosure_recount_exact`, `one_open_per_protected_input`,
`input_stat_unchanged`, `no_unregistered_access`,
`resource_limits_met_and_no_abort` — ALL true.

## 9. Disclosure / counters / resources

- Key-dependent bits: **692580** (per-record sum matches); public control bits:
  **6554860** (per-record sum matches); recount mismatch **0**.
- SC calls: **30/30** (per-record `sc_calls_this_record` sums to 30; L1-executed
  10 + L2-invoked 20). Tag invocations: **20/20** (`tag_invoked` 20/20;
  `tag_pass` 8/20 = the 8 exact records, consistent).
- Genie/sampling: Stage-A 0 + Stage-B `stage_b_sampling_calls = 0`.
- Wall: **198.393291 s** (external timeout 1200 s unfired). RSS peak:
  **650346496 B** (~620 MiB, under 2 GiB cap). `resource_stop_fired: false`.
- Planned totals replayed: K 334/6746/7080; blocks 2916..3043 / 3044..3171 /
  3172..3299 / 3300..3427 / 3428..3555; remainder 3556..3644 counted never decoded.

## 10. Stage-appropriate P20Q-R1..R9

- R1 (reuse): PASS — three digests replay-exact + H within 1e-12 + key-set/alpha/
  floor/`p1`-equality pins via Stage-B gates; zero counts opens.
- R2 (population): PASS — DEV 2916..3555 (5 × 128) + remainder 3556..3644 declared
  and gated; 1M/1.5M/2M-VAL untouched in every form.
- R3 (disclosure): PASS — per-arm caps preregistered; totals 692580/6554860;
  recount 0; B−A = D−C = 0.
- R4 (single factor): PASS — A/B/C/D pins unchanged; α=1 alt rule replayed;
  construction digest match; shared frozen order prefixes.
- R5 (endpoints + instrumentation): PASS — four endpoints separated; undetected
  isolated; nine scalars complete; IR-1..IR-5 PRESENT on all 20 records with frozen
  caps/nullability; truth-isolation clean.
- R6 (one-shot): PASS — one attempt, no rerun/tuning; HOLD-DEV 1/1; aborts none.
- R7 (reviews): Stage-B half complete — Pre-EXECUTE PASS (independent); Pre-RESULT
  + acceptance remain with the main thread. Honest-scope statement below verbatim.
- R8 (suites/audit): Stage-A 14/14 (frozen) + zero-open audit; no commit/push;
  frozen dirs untouched except the §12 packet manifest.
- R9 (D1/D2): PASS — FEASIBLE replay (margin 4791.09652735766) frozen before HOLD
  contact; Stage-B gates re-adjudicated true.

## 11. Honest-scope statement (verbatim, binding)

"third-segment (2M HOLD) confirmation of the frozen α1 construction with the
mandatory H2 instrumentation; descriptive only; 2M HOLD is consumed by this
packet; 1.5M VAL remainder stays untouched; no reliability/FER claim; the H2
decision is analysis, not a FER result."

## 12. Next gate

Pre-RESULT review (independent) on the actual artifacts above, then main-thread
acceptance. The H2 decision stays main-thread analysis after acceptance, never an
in-packet verdict.
