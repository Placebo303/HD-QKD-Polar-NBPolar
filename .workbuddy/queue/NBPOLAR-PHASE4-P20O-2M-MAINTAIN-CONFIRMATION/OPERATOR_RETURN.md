# P20O Stage-B operator return (Tier-Y ONE-SHOT, attempt 1/1 SPENT)

Packet: `NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION` · Operator: backup `coder-fast` instance ·
Branch: `codex/nbpolar-phase0` · Date: 2026-09-19 · No commit/push · Nothing marked accepted.

Result label (as produced): `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`
Blocker: NONE. The single authorized attempt completed exit 0; all 20 records written.

## 1. Transcription check + preconditions (all PASS, recorded BEFORE running)

1. Stage-B root `l2_alt_maintain_2m/` ABSENT (`stat` ENOENT) — PASS.
2. Frozen identities recomputed read-only before execution — PASS:
   - prior canonical digest (accepted `canonical_prior_digest` recipe): `b16f5216…ae1c587` match;
   - alt file sha256: `98e25495…ae5fb5` match; order file sha256: `b2255449…0906` match.
3. `P20O_FREEZE.md` §8 block == module `FROZEN_COMMAND` byte-identical (1435 chars) — PASS;
   user-pasted STEP-2 command byte-identical to both (same `cd`, digests, `--k1 334 --k2 6746`,
   `--dev-frames 2187 2826`, `--remainder-frames 2827 2915`, `--tag-master 2026092310`,
   `--order-digest b2255449…`, `timeout 1200`) — PASS, never silently corrected.
4. Branch `codex/nbpolar-phase0` — PASS. Independent Pre-EXECUTE PASS on record
   (`PRE_EXECUTE_REVIEW.md`, reviewer-go `ses_f46e4e9ddffeqvIlFewSzcTLVv`) — PASS.

## 2. Exact command (the one and only run)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --source 2M --floor 1e-15 --n 32768 --k1 334 --k2 6746 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2187 2826 --block-frames 128 --remainder-frames 2827 2915 --tag-master 2026092310 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m
```

- Start UTC: 2026-09-19T10:12:10Z · End UTC: 2026-09-19T10:15:45Z · Exit code: 0.
- External wall: 215 s (runner `wall_s`: 208.563459). Expected 3–6 min — within envelope.
- Peak RSS: operator sampler VmRSS peak 503220 KB (~491 MiB); runner `rss_bytes_peak`
  682881024 B (~651 MiB), per-record `vm_peak_kb` max 1770432 — all under the 2 GiB cap;
  `resource_stop_fired: false`, `resource_limits_met_and_no_abort: true`.
- Stdout tail (runner summary JSON):
  `records_completed: 20, operational_exact_count: 2, b_maintained_count: 0,
  b_restored_count: 2, d_maintained_count: 0, d_restored_count: 3,
  integrity_all_pass: true, outcome_label:
  TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`.
- Attempt consumed at the first VAL content open; no rerun, no tuning, no second open.

## 3. Five-file inventory (all present, 20 records)

| file | bytes | content |
|---|---|---|
| `frozen_plan.json` | 8239 | frozen command/pins/arms/blocks; `hazard_fields` 9 incl. `l2_fail_in_prefix_u_domain`, `u_domain_scalar_frozen_present: true` |
| `input_and_predecessor_identity.json` | 9192 | prior/alt/order/construction digests all verified; stat before==after on all three inputs |
| `per_block_arm_outcomes.jsonl` | 48091 | 20 records (5 blocks × 4 arms) |
| `aggregate_summary.json` | 10653 | aggregates + 28-gate integrity table, all true |
| `report.md` | 1723 | human summary + oracle/claim caveats |

## 4. Per-arm outcomes (descriptive only)

Blocks: b0 `2187..2314` / b1 `2315..2442` / b2 `2443..2570` / b3 `2571..2698` / b4 `2699..2826`
(K1=334/K2=6746 operational A/B; K2=6746 oracle C/D; remainder `2827..2915` never decoded).

| block | A (incumbent, operational) | B (alt, operational) | C (incumbent, oracle) | D (alt, oracle) |
|---|---|---|---|---|
| b0 | verify_failed, fel=L1 | verify_failed, fel=L1 | verify_failed, fel=L2 coord 78 | verify_failed, fel=L2 coord 121 |
| b1 | verify_failed, fel=L2 coord 45 | **exact** | verify_failed, fel=L2 coord 45 | **exact** |
| b2 | verify_failed, fel=L2 coord 153 | **exact** | verify_failed, fel=L2 coord 153 | **exact** |
| b3 | verify_failed, fel=L2 coord 14 | verify_failed, fel=L2 coord 35 | verify_failed, fel=L2 coord 14 | verify_failed, fel=L2 coord 35 |
| b4 | verify_failed, fel=L1 | verify_failed, fel=L1 | verify_failed, fel=L2 coord 274 | **exact** |

- Exact counts: A 0/5, B 2/5, C 0/5, D 3/5; operational exact 2/10; oracle exact 3/10.
- Outcome vocabulary over 20 records: `exact` 5, `verify_failed` 15; `error` null ×20.
- Endpoint flags: `deployable` true on all 10 A/B records, false on all 10 C/D records
  (`oracle_control` true on C/D only); `tag_pass` true exactly on the 5 exact records;
  `truth_leak_violation` false ×20; `l1_exact` true on 6 records (both B-exact blocks plus
  all four b3 L2-fail records); `l2_invoked` 20/20; `oracle_truth_use` 10/10 oracle records.
- Maintain/restore: `b_maintained_count` (A-exact→B-exact) = 0; `b_restored_count`
  (A-fail→B-exact) = 2 (b1, b2); `d_maintained_count` = 0; `d_restored_count` = 3 (b1, b2, b4,
  diagnostic only, never operational).
- A→B transition table: `a_exact_b_exact` 0, `a_exact_b_fail` 0, `a_fail_b_exact` 2,
  `a_fail_b_fail` 3. C→D table: 0 / 0 / 3 / 2.
- First-error moves per block (A/B/C/D layers): b0 L1/L1/L2/L2; b1 L2/—/L2/—;
  b2 L2/—/L2/—; b3 L2/L2/L2/L2; b4 L1/L1/L2/— (— = exact, no first error).

## 5. Instrumentation scalars (nine per record, nullability correct)

All L2-failing records (11) carry all nine scalars non-null with
`l2_order_digest=b2255449…0906`, `l2_prefix_len=6746`:

| block-arm | coord | in_prefix | hazard_bits | nbhd_mean | prefix_mean | nbhd_floor | prefix_floor | u_domain |
|---|---|---|---|---|---|---|---|---|
| b0-C | 78 | true | 1.9890 | 0.6898 | 0.8396 | 0.0000 | 0.0007 | false |
| b0-D | 121 | true | 9.1799 | 1.5323 | 0.8876 | 0.0588 | 0.0007 | false |
| b1-A | 45 | true | 1.9069 | 0.9608 | 0.8552 | 0.0000 | 0.0012 | false |
| b1-C | 45 | true | 1.9069 | 0.9608 | 0.8552 | 0.0000 | 0.0012 | false |
| b2-A | 153 | true | 1.9821 | 0.8966 | 0.8508 | 0.0000 | 0.0009 | false |
| b2-C | 153 | true | 1.9821 | 0.8966 | 0.8508 | 0.0000 | 0.0009 | false |
| b3-A | 14 | true | 0.3918 | 0.6859 | 0.8313 | 0.0000 | 0.0006 | false |
| b3-B | 35 | true | 0.4548 | 1.0020 | 0.8854 | 0.0000 | 0.0006 | false |
| b3-C | 14 | true | 0.3918 | 0.6859 | 0.8313 | 0.0000 | 0.0006 | false |
| b3-D | 35 | true | 0.4548 | 1.0020 | 0.8854 | 0.0000 | 0.0006 | false |
| b4-C | 274 | true | 1.8590 | 0.8341 | 0.8020 | 0.0000 | 0.0003 | false |

(columns: `l2_fail_in_prefix`, `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits`,
`l2_prefix_hazard_mean_bits`, `l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`,
`l2_fail_in_prefix_u_domain`. `l2_fail_in_prefix` true on all 11 failing records;
the ninth U-domain scalar present and false on all 11 — the P20N domain-mixed ambiguity
stays closed: every L2 first error is in-prefix in natural coordinates but NOT in the
U-domain disclosed prefix set.)
The other 9 records (4 L1-fail + 5 exact) have the five fail-conditioned scalars null
(`l2_fail_in_prefix`, `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits`,
`l2_fail_nbhd_floor_frac`, `l2_fail_in_prefix_u_domain`) with prefix-level scalars
(`l2_order_digest`, `l2_prefix_len`, `l2_prefix_hazard_mean_bits`, `l2_prefix_floor_frac`)
always present — frozen nullability holds; `hazard_instrumentation_complete: true`.

## 6. Gates / recount / accounting

- `failing_integrity_gates: []`, `integrity_all_pass: true` (28/28 true, incl.
  `undetected_zero`, `nonfinite_zero`, `truth_isolation`, `oracle_isolation`,
  `no_unregistered_access`, `input_stat_unchanged`, `one_open_per_protected_input`,
  `disclosure_recount_exact`, `sc_calls_exact`, `tags_exact`, `twenty_records_exact`).
- `undetected_count` 0 (isolated, never success); `nonfinite_count` 0; no `decode_failed`
  or `resource_abort` outcomes (vocabulary is exactly {exact, verify_failed}); errors null ×20.
- `recount_mismatch` 0; tags 20/20; SC 30/30 (`sum sc_calls_this_record` = 30);
  `stage_b_sampling_calls` 0.
- Key-dependent bits (recomputed exactly as the runner reports): 692580 =
  10×35464 (A/B records) + 10×33794 (C/D records) = 354640 + 337940. (Note: the task
  packet's parenthetical `8*35464 + 8*33794` = 554064 does NOT reproduce this; the
  runner's per-record actuals sum to 10+10 as above, consistent with freeze §6
  `5*(2*35464+2*33794)`.)
- Public bits: 6554860 = 20×327743. CE ratios (`disclosure_ce_ratio`) recorded per
  record, never called efficiency.
- Split-counted reads: counts opens this run 0 (cumulative counts 1/1, 2M array ONLY);
  VAL-DEV 0/1→1/1 SPENT; attempts 0/1→1/1 SPENT at the first VAL content open;
  VAL-remainder 0; 2M HOLD 0; 1M/1.5M 0 in every form.
- `opened_content_paths` == `registered_content_paths` (3 paths: session prior, alt table,
  2M VAL pairs parquet); `reopen_attempted: false`, `retries: 0`.
- Input stat unchanged: prior/alt/dev `stat_before` == `stat_after` (sizes
  25438650 / 25430240 / 2458335 B).
- 2M VAL DEV `2187..2826` is CONSUMED by this packet regardless of outcome; remainder
  `2827..2915` never decoded; 2M HOLD pristine (`2916..3644` untouched).

## 7. P20O-R1..R9 (stage-appropriate)

- R1: Stage-A 2M raw prior (digest `b16f5216…`, H 0.8325627219737477) + alt table (α=1,
  digest `98e25495…`, `p1`-equality 0.0) loaded read-only behind identity gates — evidenced
  in `input_and_predecessor_identity.json` (both digests verified).
- R2: 2M-session-derived budget/orders/population; DEV `2187..2826` + remainder `2827..2915`
  gated, S2-ii disjointness verified; order digest equality `b2255449…`; zero Stage-B
  sampling; 1M/1.5M refused by name; 2M TRAIN-as-DEV/HOLD excluded.
- R3: per-arm caps exact (A/B 35464 Δ0; C/D 33794 Δ0; public 327743); planned totals
  692580/6554860 reproduced in actuals; recount 0.
- R4: single-factor instantiation unchanged (A incumbent / B alt at session K with SAME
  order prefixes / C-D oracle pair); `p1`-equality 0.0; P16 construction digest verified.
- R5: endpoints separated (§4 table); `undetected` isolated at 0; oracles non-deployable;
  first-error rows + floor fields + all nine scalars complete with frozen nullability;
  truth-isolation sentinel green (`truth_leak_violation` 0/20).
- R6: one-shot Tier-Y honored — one attempt, no rerun/tuning; reads counts 1/1 + VAL-DEV
  1/1 + remainder 0 + HOLD 0 + 1M/1.5M 0; no resource abort; stop rules intact.
- R7: Pre-EXECUTE PASS recorded; Pre-RESULT + main-thread acceptance PENDING (not mine to
  grant); descriptive-only language kept; honest-scope statement repeated verbatim below.
- R8: Stage-A suites were green (20/20 pre+post freeze, per STATUS); no commit/push; frozen
  dirs untouched by this run (writes only: packet dir return + STATUS, and the frozen out-dir).
- R9: D1/D2 frozen at Stage A (FEASIBLE, margin 4791.09652735766);
  `alt_construction_budget_feasibility: true` re-pinned in the Stage-B summary.

## 8. Non-access statement

This run opened no 1M-pool and no 1.5M-split content in any form; no 2M TRAIN-as-DEV or
2M HOLD access; no second counts open; no `results/` or `comparison_bench/outputs_comparison/`
writes; no commit or push. Writes: this return + in-place STATUS.yaml inside the P20O packet
dir, and the five frozen files under the authorized out-dir. Nothing else.

## 9. Honest scope (packet §0, verbatim)

> first use of the reserved 2M independent session to attempt to maintain one prior 1.5M
> restoration event with the frozen construction; positive/negative both informative; no
> reliability claim; 1.5M VAL remainder and the 1M-HOLD thread stay out of scope; 2M is
> consumed by this packet regardless of outcome.

Branch reading (§16) stays planning input for the main thread, never an in-packet verdict;
no FER / reliability / recovery / maintenance / superiority / qualification / promotion claim
is made. Next gate: independent Pre-RESULT adjudication, then main-thread acceptance.
