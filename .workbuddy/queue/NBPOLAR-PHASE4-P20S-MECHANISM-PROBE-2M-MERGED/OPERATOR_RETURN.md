# Stage-B OPERATOR_RETURN — NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED

- Date: 2026-09-20. Operator: Stage-B subagent (coder-fast instance).
  Branch `codex/nbpolar-phase0`, workdir
  `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Authorization basis: user standing pre-authorization —
  "我预授权给你向下自主探索与推进的权力，允许你往下推进至少十轮，需要抉择的地方都自动选择recommend项，需要授权的地方都标注我已预授权" —
  applied to this Stage-B execution (recommend path); independent
  Pre-EXECUTE PASS (reviewer-go, session ses_f44e12d50ffeGf5QnxJNUQg4eU,
  12/12). Stage-B section appended to
  `STAGE_A_AUTHORIZATION_RECORD.md` (that file not rewritten).
- Return form: §15(a) — single authorized attempt executed once
  (attempts 1/1 SPENT), all fifteen Stage-B files present — with one
  integrity gate reporting BLOCKED, disclosed below for Pre-RESULT
  adjudication. No rerun, no tuning, no commit/push, no self-acceptance.
  Judgment form is geometry/coverage quantities ONLY; per-record outcomes
  are recorded below but NEVER read as recovery rates; no threshold votes.

## 1. Frozen command executed (byte-identical to P20S_FREEZE.md §10 and the module FROZEN_COMMAND)

- Pre-print check: `FROZEN_COMMAND` read back from
  `comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m`
  matched the freeze §10 text; no flag changed.
- Step-1 existence check: Stage-B root ABSENT before execution (verified).
- Executed exactly once under `cd
  /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` with
  `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
  MALLOC_ARENA_MAX=2`, `ulimit -v 2097152`, `timeout 1200`, interpreter
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --source 2M --floor 1e-15 --n 32768 --k1 334 --k2 6746 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames-val 2827 2915 --dev-frames-hold 3556 3594 --block-frames 128 --remainder-frames 3595 3644 --tag-master 2026092360 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --spike-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json --spike-order-digest 139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864 --spike-formula F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m
```

- Exit code 0. Stdout outcome label:
  `BLOCKED(blocks_exact_with_declared_remainder)`; records 3/3 completed.

## 2. Stage-B file inventory (15/15 present, root PRESENT)

Under `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m/`:

| file | bytes |
|---|---|
| `frozen_plan.json` | 93701 |
| `input_and_predecessor_identity.json` | 90763 |
| `per_block_arm_outcomes.jsonl` (3 records) | 17285 |
| `aggregate_summary.json` | 95524 |
| `report.md` | 2489 |
| `ir5_full_manifest.json` (ir5full-v1, 9 entries) | 3966 |
| `A_hazard_bits_f32le.bin` | 131072 |
| `A_inprefix_u8.bin` | 32768 |
| `A_inu_u8.bin` | 32768 |
| `B_hazard_bits_f32le.bin` | 131072 |
| `B_inprefix_u8.bin` | 32768 |
| `B_inu_u8.bin` | 32768 |
| `O_hazard_bits_f32le.bin` | 131072 |
| `O_inprefix_u8.bin` | 32768 |
| `O_inu_u8.bin` | 32768 |

- IR-5 size check: per-record binary triple 131072+32768+32768 =
  196608 B (~192 KiB ≤ 400 KB per-record budget); binary root total
  589824 B (~576 KiB ≤ 1.5 MB root budget); every committed file ≤ 2 MB
  (largest single file 131072 B). Size rule met.
- IR-5 manifest digests: A/O hazard `ef4398d3…52863` identical across
  A/B/O (shared arm table, expected); inprefix A/O `9e9f5e98…ad28a`
  identical, B differs `cf75440d…6830e` (spike order, expected); inu all
  differ per arm order-domain flags. Order identities pinned per file
  (frozen-A digest on A/O, spike digest on B), format `ir5full-v1`.
- Changed files this stage: `STAGE_A_AUTHORIZATION_RECORD.md` (Stage-B
  section appended), `STATUS.yaml` (attempts 1/1, merged-DEV 1/1, root
  PRESENT, `STAGE_B_COMPLETE_AWAITING_PRE_RESULT`), the 15 evidence
  files above, this `OPERATOR_RETURN.md`. No other writes; nothing under
  `results/` or `comparison_bench/outputs_comparison/` overwritten.

## 3. Per-record geometry/coverage (descriptive ONLY, not recovery framing)

- Population geometry: merged block = VAL tail 2827..2915 (89 frames)
  then HOLD head 3556..3594 (39 frames) = 128 frames / 32768 pairs, ONE
  N=32768 block; remainder 3595..3644 (50 frames / 12800 pairs) counted
  never decoded; 1.5M stub 2172..2212 (41) + 1.5M HOLD remainder
  2725..2766 (42) counted never decoded. `dev_population_exact` TRUE,
  `dev_block_range_identity` TRUE, `target_population_contract` TRUE.
- Per-arm records (1 block x 3 arms; SC A 2 / B 2 / O 1 = 5; tags 3/3):
  - A_anchor_frozen_order: outcome `exact`; first-error None; floor hits
    17 (rate 0.0002593994140625); L2 prefix mean 0.8740592319509212 bits;
    NLL true-L1 779.0023699150852 / true-L2 28888.199925933186 bits;
    raw SER 0.25128173828125 (recorded, never a reliability claim);
    key 35464 / public 327743 bits; tag pass True.
  - B_spike_local_order: outcome `verify_failed`; first-error layer L2 at
    coordinate 0; fail-site hazard 0.5131718176531462 bits with
    IR-2 rank percentile 0.432220458984375; fail site NOT in the
    disclosed prefix under either domain flag (`l2_fail_in_prefix`
    False, `l2_fail_in_prefix_u_domain` False); fail neighborhood mean
    0.6992590731236983 bits, neighborhood floor frac 0.0; floor hits
    24362 (rate 0.371734619140625); L2 prefix mean 0.8768295338061611
    bits; NLL true-L1 779.0023699150852 / selected true-H L2
    235108.15220301936 bits; raw SER 0.25128173828125 (recorded, never
    a reliability claim); key 35464 / public 327743 bits; tag pass False.
  - O_true_l1_oracle (diagnostic control, never operational): outcome
    `exact`; first-error None; floor hits 17 (rate
    0.0002593994140625); L2 prefix mean 0.8740592319509212 bits; key
    33794 / public 327743 bits; tag pass True; `deployable` False,
    `oracle_control` True.
- A-vs-B disclosed-L2-set delta (byte-exact, size-delta 0): A 6746 / B
  6746 / intersection 5147 / A−B 1599 / B−A 1599; full 1599-entry
  position lists + rank-displacement tables carried in
  `aggregate_summary.json` `order_set_delta` (identical to the Stage-A
  freeze values).
- IR-1 tails under both orders (record's OWN order; 64-bin, 65-edge
  frozen log-spaced formula): every record prefix mass 6746 / outside
  26022 / prefix-tail8 0. IR-3 (1.0x/2.0x prefix-mean): A/O thresholds
  0.8740592319509212 / 1.7481184639018423 bits with 1641 prefix
  positions above (frac 0.2432552623777053); B thresholds
  0.8768295338061611 / 1.7536590676123223 bits with 1651 above (frac
  0.24473762229469315). IR-4 top-16: `topk_in_prefix_count` 0 on all
  three arms (all top-16 ranks 1..16 outside every disclosed prefix).
  IR-2: null on A/O (no L2 failure); B single value above.
- Full-scope concentration: no separate top-128/1024 concentration
  object is present in `aggregate_summary.json`; full-block scope is
  carried by the nine uncapped IR-5 `.bin` series (32768 positions per
  record, `ir5full-v1` manifest) for main-thread analysis. Transition
  (A→B) cells NOT computed (`transition_tables` null,
  `transition_cells_computed` False — counting vocabulary out of scope
  by D2 form).

## 4. Integrity gates: 35/36 TRUE, 1 BLOCKED

- `integrity_all_pass` False; `failing_integrity_gates` =
  `["blocks_exact_with_declared_remainder"]`; outcome label
  `BLOCKED(blocks_exact_with_declared_remainder)` with 3/3 records
  completed, exit 0.
- Root cause (read-only post-hoc analysis, no code touched, no rerun):
  the gate conjunct at runner lines 2541–2553 evaluates
  `list(formation["remainder"]["frame_start"])`, but `formation`
  stores `frame_start` as scalar int `3595` (runner line 1590), so
  `list(3595)` raises `TypeError: 'int' object is not iterable`,
  caught by the gate's `except (KeyError, TypeError, ValueError)` →
  `blocks_ok = False`. Every other conjunct verifies TRUE from frozen
  artifacts: block segments [[2827,2915],[3556,3594]] equal frozen;
  blocks 1 == FROZEN_BLOCK_COUNT 1; remainder used False, 50 frames /
  12800 symbols equal frozen; remainder range [3595,3644] equal frozen;
  counted-1.5M used False with stub [2172,2212] and hold [2725,2766]
  equal frozen. The hold-tail remainder rows/frames/min/max were
  additionally validated inside `form_merged_blocks` without raising
  (otherwise no record would exist).
- This is a Stage-A-frozen gate-expression representation defect
  (scalar-vs-list), NOT a population deviation: `dev_population_exact`,
  `dev_block_range_identity`, `dev_split_manifest_identity`,
  `reuse_prior_identity`, `reuse_alt_identity`,
  `frozen_order_identity_A`, `spike_order_identity_B`,
  `order_derivation_identity`, `order_derivation_program_identity`,
  `k_literal_exact`, `budget_literal_replayed`,
  `alt_construction_budget_feasibility_replayed`, `three_records_exact`,
  `genie_calls_exact`, `sc_calls_exact`, `tags_exact`,
  `order_set_delta_recorded`, `hazard_instrumentation_complete`,
  `ir_payload_complete`, `ir5_full_manifest_identity`,
  `evidence_size_rule_met`, `disclosure_recount_exact`,
  `one_open_per_protected_input`, `no_unregistered_access`,
  `resource_limits_met_and_no_abort`, `truth_isolation`,
  `undetected_zero`, `nonfinite_zero`, `oracle_isolation`,
  `orders_valid_k_prefixes_within_registered_arms`,
  `floor_hit_rate_reported`, `buckets_disjoint_exhaustive`,
  `input_stat_unchanged`, `predecessor_construction_identity` are all
  TRUE (35 TRUE total).
- No repeat was made: the run completed (exit 0, deterministic frozen
  code); a repeat would reproduce the identical label, and rerun/tuning
  is NOT authorized. The BLOCKED label plus this root cause go to
  Pre-RESULT review and main-thread adjudication (e.g., whether to
  accept the BLOCKED-labelled evidence with the predicate defect noted,
  or to frame a follow-up packet fixing the gate expression — that
  decision belongs to the main thread, not this operator).

## 5. Accounting

- Disclosure recount: key-dependent 104722 bits
  (A 35464 + B 35464 + O 33794) / public 983229 bits (3 x 327743);
  `recount_mismatch` 0; `disclosure_recount_exact` TRUE.
- SC calls 5/5 (A 2 / B 2 / O 1); tags 3/3; genie calls Stage-A 0 +
  Stage-B 0 (`genie_calls_exact` TRUE, `stage_b_sampling_calls` 0).
- Resources: run wall 35.131961 s (records A 12.673539 / B 13.173959 /
  O 7.280900 s); RSS peak 567750656 B (~541.4 MiB); VM peak
  1764204 KiB (~1.68 GiB, under the 2097152 KiB virtual limit);
  `resource_stop_fired` False; abort never success path.
- `undetected` 0 (`undetected_zero` TRUE, never merged into success);
  `nonfinite` 0; `truth_leak_violation` False on all 3 records;
  `truth_isolation` TRUE.

## 6. Split audit (protected opens)

- counts 0/0; merged-DEV 1/1 (`dev_content_opens` 1, `counts_content_opens`
  0, `attempts_consumed_by_this_run` 1/1, no reopen, no retry-after-open);
- 1M 0 (1M path refused by source-tag identity, recorded in
  `dev_source.refused_1m_path`); 1.5M 0 (refused path recorded; stub +
  hold remainder counted only, never decoded); 2M-non-DEV 0 (HOLD tail
  3595..3644 rows counted for the remainder check, never decoded).
- DEV source verified: 2M session `type2_2M_20260121_183657`, pairs
  size 2458335 B, sha256
  `d5a36eec8a03ce7e801bba4fd4b2e62cf8aef13c1efe1166766db79364ffc307`.
- Reuse pins replayed in-run: prior
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`,
  alt `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`,
  order-A `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`,
  spike-B `139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864`,
  formula `F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8`, K
  334/6746/7080, tag master 2026092360 — all equal frozen.
- `test_evidence_package.py` was NOT run (per hard limits).

## 7. Honest scope (verbatim from TASK_PACKET.md §0)

- "a single merged-block (2M VAL-remainder tail + HOLD-remainder head) mechanism probe of one local-spike L2-order position rule under the frozen α1 construction at frozen disclosure with full-block hazard geometry recorded; descriptive geometry only; the merged DEV block is consumed by this packet; the HOLD tail 3595..3644 and all 1.5M remainders stay untouched; no recovery claim, no H2 verdict; the H2 decision is analysis, not a block result."

## 8. Handoff

- `STATUS.yaml`: `attempts_used` 1, `merged_dev_reads_used` 1/1,
  `stage_b_out_root` PRESENT, `planning_stage`
  `STAGE_B_COMPLETE_AWAITING_PRE_RESULT`; counts 0/0, 1M 0, 1.5M 0,
  2M-non-DEV 0 unchanged.
- Next gates: independent Pre-RESULT review on actual artifacts, then
  main-thread acceptance. The operator marks nothing accepted.
- ONE decision needed from the main thread at adjudication: accept the
  15-file evidence with the `BLOCKED(blocks_exact_with_declared_remainder)`
  label and the scalar-vs-list predicate defect noted (population and
  geometry artifacts verified intact), or frame a follow-up packet for
  the gate expression. No operator-side rerun is available or requested.
