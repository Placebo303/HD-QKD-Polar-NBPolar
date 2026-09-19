# P20N Stage-B operator return — NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M

- Operator: Stage-B operator (Tier-Y ONE-SHOT attempt, first and only run).
- Branch: `codex/nbpolar-phase0` (verified before execution).
- State after this return: Stage-B EXECUTED once; NOT accepted (no self-acceptance);
  `pre_result_review: PENDING_INDEPENDENT_ADJUDICATION`.
- Blocker: NONE. All frozen items complete; no rerun/tuning performed.

## 0. Honest scope (TASK_PACKET.md §0, verbatim, binding)

> this packet tests ONE preregistered alternative L2 construction at fixed
> disclosure on the first HOLD-segment use; it can restore L2 or falsify this
> construction; a budget-infeasible construction is returned without consuming
> HOLD; it licenses no reliability/recovery claim; 2M and VAL remainder
> remain untouched; the 1M-HOLD thread stays open.

(No reliability/recovery/FER/efficiency/qualification/promotion claim is made
below. B-vs-A and D-vs-C readings are descriptive only. C/D are oracle-labelled
diagnostic controls, never an operational protocol or deployable result.)

## 1. Transcription check (preconditions, all PASS, recorded BEFORE running)

1. Stage-B root
   `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`
   was ABSENT (`stat` ENOENT) immediately before execution. PASS.
2. Frozen identities (all PASS):
   - alt-table file-bytes sha256 `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`
     (`sha256sum`, matches freeze §1 pin and `--alt-digest`).
   - prior canonical digest `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`
     (`--prior-digest` pin; file-bytes reference `6b8ae9b81782312d53081a6742cc31ac53ef30e4e92b0b07c9eba7f9787a3481`
     as documented in freeze §1 — canonical digest vs file-bytes distinction preserved).
   - order-file sha `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`
     (`sha256sum`, matches freeze §3 pin and `--order-digest`).
   - `P20N_FREEZE.md` §5 Stage-B block == module `FROZEN_COMMAND` byte-identical
     (`diff` empty; extracted via module import vs freeze bash block #2). PASS.
3. Pasted user command byte-identical to `FROZEN_COMMAND`/freeze §5 (`diff` empty;
   `cd /mnt/d/Code/...`, `--alt-digest 6f4a4f76…2333e78`, `--k1 331 --k2 6689`,
   `--dev-frames 2213 2724`, `--remainder-frames 2725 2766`, `--tag-master 2026092300`,
   `--order-digest a9f18a9f…1bc638`). No silent correction. PASS.
4. Branch `codex/nbpolar-phase0`. PASS.
5. Independent Pre-EXECUTE review PASS on record (`PRE_EXECUTE_REVIEW.md`,
   reviewer-go session `ses_f480b89c3ffeF7kAH133WfZ4lf`). Filled STEP-2 Stage-B
   authorization pasted by the user (this turn). PASS.

## 2. Exact command (the single authorized attempt; run EXACTLY once)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 900 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest 6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78 --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 2213 2724 --block-frames 128 --remainder-frames 2725 2766 --tag-master 2026092300 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m
```

## 3. Execution record

| field | value |
|---|---|
| start UTC | 2026-09-19T05:20:01Z |
| end UTC | 2026-09-19T05:22:45Z |
| exit code | 0 |
| external wall (`/usr/bin/time -v`) | 2:44.37 (164.37 s; within 900 s ceiling; within ~2–4 min expectation) |
| in-runner `wall_s` | 162.174854 s |
| peak RSS (external max-RSS) | 646324 kB = 631.2 MB (marginally above the ≲600 MB expectation; ulimit 2 GiB never hit; runner `resource_limits_met_and_no_abort: true`, `resource_stop_fired: false`) |
| runner `rss_bytes_peak` | 661835776 B = 631.2 MB (consistent) |
| stdout tail (final JSON line) | `{"analysis": "nbpolar-p20n-l2-alt-hold-1p5m", "b_restored_count": 1, "d_restored_count": 1, "integrity_all_pass": true, "operational_exact_count": 1, "out_root": ".../l2_alt_hold_1p5m", "outcome_label": "TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE", "records_completed": 16}` |
| reruns / tuning | 0 (ONE-SHOT consumed at the first HOLD content open) |

## 4. Five-file inventory (all present; artifacts only, no re-run)

Under `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`:

| file | size (B) | check |
|---|---|---|
| `frozen_plan.json` | 6800 | arms K1/K2/caps, blocks, digests, `frozen_command` match §2 |
| `input_and_predecessor_identity.json` | 8603 | stat-before==stat-after on all three inputs; digests verified |
| `per_block_arm_outcomes.jsonl` | 35817 | 16 records (4 arms × 4 blocks) |
| `aggregate_summary.json` | 8925 | outcome label `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE` |
| `report.md` | 1381 | 16/16 records, integrity ALL PASS |

## 5. Per-arm outcomes (descriptive only; 16 records)

Blocks: b0 `2213..2340`, b1 `2341..2468`, b2 `2469..2596`, b3 `2597..2724`
(frames; natural block symbol index in `first_error_coord`).

| arm | K1/K2 | b0 | b1 | b2 | b3 | exact | verify_failed |
|---|---|---|---|---|---|---|---|
| A_incumbent_L2_operational | 331/6689 | verify_failed (L2/111) | verify_failed (L2/76) | verify_failed (L2/3) | verify_failed (L2/81) | 0/4 | 4/4 |
| B_alt_L2_operational | 331/6689 | verify_failed (L2/1009) | verify_failed (L2/20) | verify_failed (L2/5823) | **exact** (—) | 1/4 | 3/4 |
| C_incumbent_L2_oracle | 0/6689 | verify_failed (L2/111) | verify_failed (L2/76) | verify_failed (L2/3) | verify_failed (L2/81) | 0/4 | 4/4 |
| D_alt_L2_oracle | 0/6689 | verify_failed (L2/1009) | verify_failed (L2/20) | verify_failed (L2/5823) | **exact** (—) | 1/4 | 3/4 |

- Operational exact 1/8 (A 0, B 1); oracle exact 1/8 (C 0, D 1).
- `b_restored_count = 1` (descriptive: A fail → B exact on b3), `b_maintain_count = 0`;
  `d_restored_count = 1` (diagnostic only, never operational).
- Every failing record has `first_error_layer = L2` (14/14); both exact records have
  null first-error layer/coordinate. L1: `l1_exact = true` on all 8 operational records;
  C/D skip L1 (`l1_executed = false`, true-L1 oracle conditioning).
- Endpoint flags: `tag_pass` true exactly on the 2 exact records (B-b3, D-b3), false on
  all 14 failing records; `tag_invoked` 16/16; `error` null on all 16 (no crash/traceback);
  `truth_leak_violation` false on all 16; `deployable` true on A/B, false on C/D (oracle
  isolation); `pair_exact` mirrors `exact` on A/B.
- First-error coordinates mirror across constructions per block for A/C
  (111/76/3/81) and B/D (1009/20/5823/—): the failing coordinate MOVES under the alt
  conditional (not the same coordinate restored — b3 is the only block where alt
  decodes exactly while incumbent fails).

## 6. X09-R1 instrumentation scalars (H2 attribution payload; 8 fields × 16 records)

`l2_order_digest` = `a9f18a9f…1bc638` on all 16 records (frozen order identity);
`l2_prefix_len` = 6689 (gated) on all 16. Nullability correct: the four
`l2_fail_*` fields are non-null on the 14 L2-failing records and null on the 2 exact
records; `l2_prefix_*` fields non-null everywhere.

Failing-record scalar table (descriptive, post-decode recording-only):

| rec (arm/b) | l2_fail_in_prefix | l2_fail_hazard_bits | l2_fail_nbhd_mean_bits | l2_prefix_hazard_mean_bits | l2_fail_nbhd_floor_frac | l2_prefix_floor_frac |
|---|---|---|---|---|---|---|
| A/b0 | true | 2.0426443374085355 | 0.8013485556243274 | 0.8555589542988179 | 0.0 | 0.001345492599790701 |
| B/b0 | true | 2.0255350921071367 | 0.8521405581080223 | 0.9029491952400781 | 0.0 | 0.001345492599790701 |
| C/b0 | true | 2.0426443374085355 | 0.8013485556243274 | 0.8555589542988179 | 0.0 | 0.001345492599790701 |
| D/b0 | true | 2.0255350921071367 | 0.8521405581080223 | 0.9029491952400781 | 0.0 | 0.001345492599790701 |
| A/b1 | true | 1.8393599774521718 | 0.8618633754456193 | 0.8187260346827915 | 0.0 | 0.00044849753326356705 |
| B/b1 | true | 2.0285691521967704 | 1.0001162997862425 | 0.9031615266395793 | 0.0 | 0.00044849753326356705 |
| C/b1 | true | 1.8393599774521718 | 0.8618633754456193 | 0.8187260346827915 | 0.0 | 0.00044849753326356705 |
| D/b1 | true | 2.0285691521967704 | 1.0001162997862425 | 0.9031615266395793 | 0.0 | 0.00044849753326356705 |
| A/b2 | true | 2.0109989989493005 | 1.0833726254124474 | 0.8248133729522927 | 0.0 | 0.0005979967110180894 |
| B/b2 | **false** | 0.5679293035617142 | 0.8109664269756897 | 0.9035428418886212 | 0.0 | 0.0005979967110180894 |
| C/b2 | true | 2.0109989989493005 | 1.0833726254124474 | 0.8248133729522927 | 0.0 | 0.0005979967110180894 |
| D/b2 | **false** | 0.5679293035617142 | 0.8109664269756897 | 0.9035428418886212 | 0.0 | 0.0005979967110180894 |
| A/b3 | true | 0.42638247287289494 | 0.6971566805109777 | 0.7954019295969416 | 0.0 | 0.00014949917775452235 |
| C/b3 | true | 0.42638247287289494 | 0.6971566805109777 | 0.7954019295969416 | 0.0 | 0.00014949917775452235 |

Exact records (B/b3, D/b3): `l2_fail_in_prefix/hazard/nbhd/floor_frac` all null;
`l2_prefix_hazard_mean_bits = 0.8924603616627651`, `l2_prefix_floor_frac = 0.00014949917775452235`.

Notable (descriptive only, no verdict): all failing neighbourhood floor fractions are
0.0 (no floor-hit involvement at the R=8 fail neighbourhood on any failing record);
the only out-of-prefix first error under alt (B/D b2, coord 5823) carries the lowest
fail-hazard bits (0.568); alt prefix-hazard means (0.89–0.90) exceed incumbent
(0.80–0.86) on every block while alt still decodes b3 exactly. H2 attribution is for
the independent Pre-RESULT review to adjudicate, not this return.

## 7. Integrity gates, recount, accounting

- `integrity_all_pass: true`; `failing_integrity_gates: []` (26/26 gates true, incl.
  `alt_construction_budget_feasibility`, `alt_l2_identity`, `order_derivation_identity`,
  `k_literal_exact`, `disclosure_recount_exact`, `hazard_instrumentation_complete`,
  `oracle_isolation`, `truth_isolation`, `undetected_zero`, `nonfinite_zero`,
  `no_unregistered_access`, `input_stat_unchanged`, `resource_limits_met_and_no_abort`,
  `sixteen_records_exact`, `sc_calls_exact`, `tags_exact`, `target_population_contract`,
  `one_open_per_protected_input`).
- `undetected` isolated: `undetected_count = 0` (never merged into success/exact).
- `nonfinite_count = 0`; `decode_failed` outcomes 0/16; `error` null 16/16;
  `resource_stop_fired = false`; `resource_abort` 0.
- Recount: `recount_mismatch = 0`; key-dependent bits actual 549384 = planned 549384
  = 8×35164 + 8×33509 (281312 + 268072); public bits actual 5243888 = planned
  5243888 = 16×327743; SC 24/24 (operational 16 = 8×2, oracle 8 = 8×1); tags 16/16;
  records 16/16. Recomputed from `per_block_arm_outcomes.jsonl` exactly as the runner
  reports (sums match `aggregate_summary.json`).
- Stage-B sampling calls 0; TRAIN genie calls 0 (pinned).

## 8. Read audit + consumption (counts/VAL/1M/2M untouched)

| counter | value |
|---|---|
| V25 counts-calibration content opens | 0 (budget 0/0; unchanged) |
| HOLD parquet content opens | 0/1 → 1/1 SPENT (the single authorized attempt; `dev_content_opens: 1`, `reopen_attempted: false`) |
| attempts | 0/1 → 1/1 SPENT (consumed at the first HOLD content open; `retries: 0`, `retry_after_open: false`) |
| VAL-remainder reads | 0 (unchanged) |
| reserved 2M open/stat/listing/read | 0 — pristine by non-access; refused paths recorded, never touched |
| 1M-pool access | 0 — never accessed |
| `no_unregistered_access` | true; opened (3) == registered (3): incumbent npz + alt npz + 1.5M DEV parquet |
| input stat unchanged | true (prior/alt/DEV mtime+size before==after) |
| Stage-B output root | ABSENT → PRESENT (only the five frozen files; nothing else written) |

- 2M/VAL non-access statement: the reserved 2M session (`type2_2M_20260121_183657`)
  and the VAL remainder (`2044..2212`) were not opened, statted, listed, or read in
  any form during this Stage-B attempt; the 1M pool was never accessed; the HOLD
  remainder (`2725..2766`) was counted and never decoded.
- No writes outside the P20N packet dir + the frozen out-dir. No commit/push.
  `results/` and `comparison_bench/outputs_comparison/` untouched.

## 9. P20N-R1..R9 Stage-B evidence map

- R1 (alt table): `alt_digest 6f4a4f76…` re-verified at run open (`alt_table_gate.verified:
  true`, 9-key set, `p1_equality_max_abs_diff: 0.0`).
- R2 (population/gates): DEV `2213..2724` + remainder `2725..2766`, S2-ii disjointness
  `verified: true`, `target_population_contract: true`.
- R3 (caps): K1=331/K2=6689/K_total=7020 replayed; 35164/33509/327743 exact; recount §7.
- R4 (arms): four hardcoded arms, Δ caps exactly 0 (A vs B, C vs D).
- R5 (endpoints/taxonomy + instrumentation): outcomes `exact`/`verify_failed` only;
  `undetected` isolated at 0; eight scalars per record with correct nullability (§6).
- R6 (budget/stop): external 900 s + 2 GiB virtual cap + single thread; wall 164.37 s;
  peak RSS 631.2 MB; no abort; one-shot consumed.
- R7 (reviews): Pre-EXECUTE PASS (independent); Pre-RESULT PENDING independent
  adjudication — this return marks nothing accepted.
- R8 (tests): unchanged from Stage-A close (P20N suite 16/16 green); no test run in
  Stage B (frozen execution only).
- R9 (D1/D2): `alt_construction_budget_feasibility: true` re-asserted in-run.

## 10. Result label (as produced, not accepted)

`TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`
(16/16 records; operational exact 1; b_restored 1; d_restored 1; integrity ALL PASS).
Acceptance, if any, belongs to the main thread after independent Pre-RESULT review.

## 11. Blocker-or-none

NONE. Single attempt executed cleanly (exit 0), all artifacts verified against the
frozen pins. Next gate: independent Pre-RESULT review
(`PENDING_INDEPENDENT_ADJUDICATION`), then main-thread acceptance decision.
No further operator action exists under this packet (attempts 1/1 SPENT).
