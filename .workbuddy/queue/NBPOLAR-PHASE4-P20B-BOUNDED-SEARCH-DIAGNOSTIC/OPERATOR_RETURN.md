# P20B Stage-B operator return (single authorized execution)

- Task: `NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC` (Tier-Y, one-shot, attempt 1/1 consumed).
- State after this return: `STAGE_B_EXECUTED_AWAITING_PRE_RESULT`. No self-acceptance; Pre-RESULT
  review + main-thread acceptance own the label.

## 1. Executed command (verbatim, §10 freeze)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && ulimit -v 2097152 && timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.bounded_search_diagnostic --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --dev-frames 1200 1599 --block-frames 128 --remainder-frames 1584 1599 --tag-master 2026092080 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/bounded_search_diagnostic
```

- 16 flags, all required, no production default; bound pinned M=8 (fail-closed, not CLI-tunable).
- Exit code 0, first and only invocation. No rerun, no retune, no second factor.

## 2. Pre-execution recheck (all PASS, then executed)

- Branch `codex/nbpolar-phase0` confirmed (`git branch --show-current`).
- Output root `bounded_search_diagnostic/` confirmed ABSENT (`stat`: No such file or directory);
  queue dir held only the 6 expected planning files.
- Frozen quadruple confirmed against `P20B_FREEZE.md`: M=8 / `P20B-NBHD-1` / single NLL model;
  VAL 1200..1599, blocks 1200..1327 / 1328..1455 / 1456..1583, remainder 1584..1599 unused;
  caps 34119 / 32524 + 327743 public; 16-flag command verbatim.
- Budget envelope in command: 600 s external timeout, 2 GiB virtual limit, single-thread
  BLAS/OpenMP + `MALLOC_ARENA_MAX=2`.

## 3. Wall / RSS (artifact-reported)

- `wall_s`: 111.305401 (ceiling 600 s — inside).
- `rss_bytes_peak`: 541188096 (~516 MiB; 2 GiB cap — inside).
- `resource_stop_fired`: false; `resource_abort` records: 0.

## 4. Gate statistics (20/20 true, `integrity_all_pass: true`, failing: [])

`predecessor_construction_identity`, `dev_split_manifest_identity`, `dev_block_range_identity`,
`target_population_contract` (7/7), `dev_population_exact` (400 frames / 102400 pairs / 256 rows
per frame), `blocks_exact_with_declared_remainder`, `nine_records_exact`, `sc_calls_exact`
(derived 15), `tags_exact` (derived 9), `orders_valid_k_prefixes_within_registered_arms`,
`oracle_isolation`, `buckets_disjoint_exhaustive`, `undetected_zero`, `nonfinite_zero`,
`truth_isolation`, `disclosure_recount_exact` (mismatch 0), `one_open_per_protected_input`,
`input_stat_unchanged`, `no_unregistered_access`, `resource_limits_met_and_no_abort`.

- Outcome label (descriptive): `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE`.
- Outcome counts: 9x `verify_failed`; `exact` 0; `undetected` 0 (isolated, never success);
  `nonfinite` 0; `decode_failed` 0; `resource_abort` 0.
- No FER / Wilson / superiority / qualification / promotion claim of any kind.

## 5. Per-block endpoints (frame ranges disjoint from closed 1600..1983)

| blk | frames | arm | outcome | exact | l1 | hard-L2 | oracle-L2 | pair | first err | SC | rescores | selected | better | dNLL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1200..1327 | S0 | verify_failed | F | F | F | — | F | L1@15433 | 2 | — | — | — | — |
| 0 | 1200..1327 | S1 | verify_failed | F | F | F | — | F | L1@15433 | 2 | 8 | greedy#0 | F | 0.0 |
| 0 | 1200..1327 | S2 | verify_failed | F | — | — | F | — | L2@22 | 1 | — | — | — | — |
| 1 | 1328..1455 | S0 | verify_failed | F | T | F | — | F | L2@42 | 2 | — | — | — | — |
| 1 | 1328..1455 | S1 | verify_failed | F | T | F | — | F | L2@0 | 2 | 8 | greedy#0 | F | 0.0 |
| 1 | 1328..1455 | S2 | verify_failed | F | — | — | F | — | L2@42 | 1 | — | — | — | — |
| 2 | 1456..1583 | S0 | verify_failed | F | T | F | — | F | L2@55 | 2 | — | — | — | — |
| 2 | 1456..1583 | S1 | verify_failed | F | T | F | — | F | L2@0 | 2 | 8 | greedy#0 | F | 0.0 |
| 2 | 1456..1583 | S2 | verify_failed | F | — | — | F | — | L2@55 | 1 | — | — | — | — |

- Per-arm exact: S0 0/3, S1 0/3, S2 0/3 (oracle control, deployable=false, never operational).
- Search-vs-SC: `search_better_count` 0/3 blocks; every S1 block selected greedy with 0.0-bit
  NLL improvement — the preregistered bounded negative holds (descriptive, development data).
- Floor diagnostics: S0 raw zero-count/floor-1e-15 hits 71/48/46 per block (log loss 3524.08 /
  2391.79 / 2288.90 bits); S1 search-aggregated hits 29469/29521/29514 (log loss ~1.468M /
  ~1.470M / ~1.470M bits across rescored candidates); S2 73/48/46.
- Raw SER per block: 0.242431640625 / 0.2393798828125 / 0.238189697265625 (identical across arms).
- `truth_leak_violation`: false on all 9 records.

## 6. Disclosure accounting (recount mismatch 0)

- Per-block key-dependent: S0/S1 34119 = 5*6811+64; S2 32524 = 5*6492+64.
- Per-tag public control: 327743 = 10*32768+63 (all 9 tags).
- Totals: key 302286 = 6*34119 + 3*32524 (operational 204714 + oracle 97572);
  public 2949687 = 9*327743.
- Cap meaningfulness: 34119/327680 = 0.10412292 (~10.41% of raw input bits per block).
- `disclosure_ce_ratio` (descriptive, NOT efficiency): S0/S1 1.221202 / 1.220193 / 1.248606;
  S2 1.164113 / 1.163151 / 1.190236.
- Call identities: 15 SC (3 blocks x (2+2+1); search rescores are NLL evaluations, not SC calls),
  9 tags; derived recomputation equals counters (gates `sc_calls_exact`, `tags_exact`).

## 7. Consumption (one-shot semantics observed)

- `counts_content_opens` 1/1 (TRAIN counts NPZ), `dev_content_opens` 1/1 (VAL pairs parquet),
  `reopen_attempted` false, `retries` 0, `retry_after_open` false.
- `attempts_consumed_by_this_run` 1/1; input stats unchanged before/after
  (NPZ 25166822 bytes; parquet 1354289 bytes).
- STATUS.yaml: `attempts_used` 0→1, `train_artifact_reads_used` 0→1, `hold_data_reads_used` 0→1,
  state → `STAGE_B_EXECUTED_AWAITING_PRE_RESULT`.

## 8. Five-file inventory (exactly five, scalar-only)

`frozen_plan.json`, `input_and_predecessor_identity.json`, `per_block_arm_outcomes.jsonl`
(9 records), `aggregate_summary.json`, `report.md` — under
`.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/bounded_search_diagnostic/`.
No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push.

## 9. Honest limitations (for Pre-RESULT review)

- Descriptive development diagnostic on one VAL draw (3 DEV blocks, single 1M session); not
  FER, efficiency, key-rate, scaling, qualification or promotion evidence; S2 never operational.
- Observed S0/S1 endpoint nuance (values reported as-is, Pre-RESULT to adjudicate): on blocks 1-2
  S1 records `first_error_layer/coord` L2@0 while S0 records L2@42 / L2@55, although S1 selected
  the greedy candidate (dNLL 0.0); block 0 agrees (L1@15433). S1 zero/floor-hit fields aggregate
  over rescored candidates by design, hence the large S0-vs-S1 hit totals.
- CE-normalized ratios are sample cross-entropy ratios, explicitly not reconciliation efficiency.
- `undetected` is isolated (0 records) and never merged into success.
