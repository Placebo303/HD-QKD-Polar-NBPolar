# P20C Stage-B operator return (single attempt, descriptive, no self-acceptance)

- Task: `NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF` (Tier-Y Stage B, one-shot).
- Authorization chain: user standing Stage-B authorization naming P20C +
  independent Pre-EXECUTE `PRE_EXECUTE_PASS_CONDITIONAL` (`PRE_EXECUTE_REVIEW.md`).
- Five iron rules observed: verbatim command / single attempt / no tuning-second-factor /
  descriptive-only / stop-on-anomaly. No repeat, no rerun, no SCL, no `results/` or
  `comparison_bench/outputs_comparison/` write, no commit/push, no self-acceptance.

## 1. Command / start-end / exit

- Verbatim FREEZE §10 command, executed once from
  `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (16 flags, unchanged, one line):
  `export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 &&
  ulimit -v 2097152 && timeout 600
  /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m
  comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_disclosure_backoff
  --counts .../run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768
  --k1 319 --k2 6492 --construction
  .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json
  --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b
  --dev-pairs .../type2_1M_20260121_184040/pairs.parquet --dev-frames 0 1199
  --block-frames 128 --remainder-frames 384 1199 --tag-master 2026092090
  --chunk-rows 512 --tag-bits 64 --out-dir
  .workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/l2_disclosure_backoff`
- Pre-execution recheck: branch `codex/nbpolar-phase0`; `stat` output root → absent
  (proceeded); frozen quadruple confirmed (ΔK2 +1024, K2 6492→7516; TRAIN blocks
  0..127/128..255/256..383, remainder 384..1199 never used; caps 34119/39239/32524 +
  327743 public; 16-flag command); budget 600 s / 2 GiB / single-thread.
- Start ≈ 18:43, end ≈ 18:45 local (root dir mtimes); runner wall 92.906254 s
  (inside 600 s ceiling). Exit code 0, first and only attempt.
- Stdout (whole): `{"analysis": "nbpolar-p20c-l2-disclosure-backoff",
  "b1_restored_count": 1, "integrity_all_pass": true, "operational_exact_count": 5,
  "out_root": ".../l2_disclosure_backoff", "outcome_label":
  "TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE", "records_completed": 9}`.

## 2. Five files + gate statistics

- Root `.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/l2_disclosure_backoff/`
  holds exactly five files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records), `aggregate_summary.json`, `report.md`.
- Integrity: 20/20 gates PASS, `failing_integrity_gates: []`:
  predecessor_construction_identity, dev_split_manifest_identity,
  dev_block_range_identity (dual overlap pre-check closed 1600..1983 + consumed
  1200..1599), target_population_contract, dev_population_exact,
  blocks_exact_with_declared_remainder, nine_records_exact, sc_calls_exact,
  tags_exact, orders_valid_k_prefixes_within_registered_arms, oracle_isolation,
  buckets_disjoint_exhaustive, undetected_zero, nonfinite_zero, truth_isolation,
  disclosure_recount_exact, one_open_per_protected_input, input_stat_unchanged,
  no_unregistered_access, resource_limits_met_and_no_abort.
- Outcome label (descriptive, integrity-gated, count-independent):
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE`.
- Outcome totals: exact 7 / verify_failed 2 / undetected 0 / decode_failed 0 /
  nonfinite 0 / resource_abort 0. `undetected` isolated (never success). B2 is
  `ORACLE_TRUE_L1_CONTROL`, deployable=false, excluded from operational aggregates —
  never operational. No FER / promotion / qualification language applies.
- Resource: peak RSS 579366912 B (< 2 GiB), VM peak 1768132 KB (< 2097152),
  `resource_stop_fired: false`.

## 3. Per-arm exact/found + endpoint table (descriptive)

| arm | exact | outcomes | key bits | public bits |
|---|---|---|---|---|
| B0_sc_base (operational, K1 319/K2 6492) | 2/3 | exact 2, verify_failed 1 | 102357 | 983229 |
| B1_L2plus (operational, K1 319/K2 7516, ΔK2 +1024) | 3/3 | exact 3 | 117717 | 983229 |
| B2_true_l1_diagnostic (oracle, K1 0/K2 6492) | 2/3 | exact 2, verify_failed 1 | 97572 | 983229 |
| operational total | 5/6 | — | 220074 | 1966458 |

Per-(arm, block) endpoint records (block-major slot order):

| arm | blk | frames | outcome | exact | l1 | hard-L2 | oracle-L2 | pair | first err | SC | tag | dK2 | rule | keyΔ | key | pub |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 0 | 0..127 | exact | T | T | T | — | T | — | 2 | T | 0 | base | 0 | 34119 | 327743 |
| B1 | 0 | 0..127 | exact | T | T | T | — | T | — | 2 | T | 1024 | frozen-order-prefix-extension | 5120 | 39239 | 327743 |
| B2 | 0 | 0..127 | exact | T | — | — | T | — | — | 1 | T | 0 | base | 0 | 32524 | 327743 |
| B0 | 1 | 128..255 | verify_failed | F | T | F | — | F | L2@723 | 2 | T | 0 | base | 0 | 34119 | 327743 |
| B1 | 1 | 128..255 | exact | T | T | T | — | T | — | 2 | T | 1024 | frozen-order-prefix-extension | 5120 | 39239 | 327743 |
| B2 | 1 | 128..255 | verify_failed | F | — | — | F | — | L2@723 | 1 | T | 0 | base | 0 | 32524 | 327743 |
| B0 | 2 | 256..383 | exact | T | T | T | — | T | — | 2 | T | 0 | base | 0 | 34119 | 327743 |
| B1 | 2 | 256..383 | exact | T | T | T | — | T | — | 2 | T | 1024 | frozen-order-prefix-extension | 5120 | 39239 | 327743 |
| B2 | 2 | 256..383 | exact | T | — | — | T | — | — | 1 | T | 0 | base | 0 | 32524 | 327743 |

(Correction to the B0-blk2 row above: dK2 0, rule base — the "1024? no: 0" is a
typo guard; authoritative values are in `per_block_arm_outcomes.jsonl`.)

- Disclosure comparison (descriptive): B1 restored a complete block where B0 failed
  on 1/3 blocks — block 1 (B0 verify_failed at L2@723 with L1 exact; B1 exact).
  Blocks 0 and 2 exact on both operational arms. `b1_restored_count: 1`.

## 4. Accounting identities (all exact)

- Key: 3×34119 = 102357 (B0) ✓; 3×39239 = 117717 (B1) ✓; 3×32524 = 97572 (B2) ✓;
  total 317646 = 102357 + 117717 + 97572 ✓; operational 220074 = 102357 + 117717 ✓.
  B1 key-bit delta vs base exactly +5120 = 5×1024 ✓.
- Public: 9×327743 = 2949687 ✓; per arm 3×327743 = 983229 ✓;
  operational 6×327743 = 1966458 ✓.
- SC calls: 6 operational records × 2 + 3 oracle records × 1 = 15 = counter ✓
  (per-record `sc_calls_this_record` recomputation; `sc_calls_exact` PASS).
- Tags: 9 records × 1 = 9 = counter ✓ (`tags_exact` PASS).
- Cap vs raw (10×N = 327680 bits/block): base 34119/327680 = 0.10412292 (~10.41%),
  B1 39239/327680 = 0.11974792 (~11.97%) — both far below raw ✓.
- Recount: `disclosure_recount_exact` PASS (mismatch 0) ✓.
- Construction digest recomputed `055c90…faea1b`, match ✓; input stats unchanged
  (NPZ 25166822 B, parquet 1354289 B, before == after) ✓.
- P20A endpoint separation held: operational records carry l1/hard-L2/pair with
  oracle-L2 null; oracle records carry oracle-L2 with l1/hard-L2/pair null ✓.

## 5. Consumption counts

- attempts: 1/1 consumed (first protected content open = attempt point; no reopen,
  no retry, `reopen_attempted: false`, `retries: 0`).
- Protected content opens: counts NPZ 1/1 + DEV TRAIN pairs parquet 1/1
  (one open per protected input; `one_open_per_protected_input` PASS).
- STATUS updated: `train_artifact_reads_used: 1` (DEV TRAIN-range content),
  `hold_data_reads_used: 0` (no HOLD read), `attempts_used: 1`,
  `state: STAGE_B_EXECUTED_AWAITING_PRE_RESULT`,
  `result: TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE`,
  `next_gate: PRE_RESULT_REVIEW`. (The counts-NPZ open is recorded here and in
  `attempt_read_accounting`; the YAML schema carries only train/hold counters.)
- Attempt budget exhausted: any repeat — including an execution-error repeat — is
  forbidden under the stricter standing authorization; further runs need a new packet.

## 6. Not run in this stage

- Independent Pre-RESULT review, main-thread acceptance, memory triage, OpenSpec
  archiving, any P20D work, any confirmation on new blocks/sessions.
- No focused-test rerun in Stage B (Stage-A suites: 34 P20C + 147 predecessors
  green, per freeze §11; Pre-RESULT may recompute §9 identities read-only).

## 7. Scope concerns

- None blocking: 20/20 gates PASS, no BLOCKED gate, no resource abort, no
  unexpected root content (exactly five files), no command deviation.
- B2 never operational; `undetected` zero and isolated; result is descriptive —
  operator marks nothing accepted. Awaiting Pre-RESULT review.
