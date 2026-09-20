# P20T Stage-B Operator Return (Stage-B operator, 2026-09-20)

Packet: `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL`
Branch: `codex/nbpolar-phase0`. Tier-Y one-shot. This return covers Stage B ONLY.
The operator marks nothing accepted; acceptance belongs to the main thread
after independent Pre-RESULT review.

## 0. Authorization and root state

- Standing pre-authorization (user, 2026-09-20, autonomous推進, renewed
  2026-09-20) applied by the main thread to this Stage-B execution.
- Independent Pre-EXECUTE: PASS (reviewer-go, session
  ses_f4313eceaffebVIFYfTW0Iz1xj, 13/13, incl. spike-h reading
  WITHIN-CONTRACT).
- Filled STEP-2 in `AUTHORIZATION_PROMPT.md` names the exact frozen command.
- Stage-B root `n8192_persistence_probe_2m/` verified ABSENT (existence check
  only) before execution. STEP 0 recorded in `STATUS.yaml`
  (`stage_b_authorized: true`, `decoder_execution_authorized: true`,
  `protected_data_read_authorized: true`, `planning_stage: STAGE_B_IN_PROGRESS`)
  and in `STAGE_A_AUTHORIZATION_RECORD.md` (Stage-B section, 2026-09-20).

## 1. Command executed (EXACTLY ONE attempt, byte-identical)

- `FROZEN_COMMAND` printed from the module (import only, no decoder contact)
  and verified byte-identical field-by-field with `P20T_FREEZE.md` §10 and the
  STEP-2 pins (`--prior-digest b16f5216…`, `--construction-digest d77466ec…`,
  `--order-digest 66aefea8…`, `--spike-order-digest 355a32d3…`,
  `--spike-formula F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192`,
  `--k1 84 --k2 1676 --tag-master 2026092400 --chunk-rows 128 --n 8192`,
  DEV HOLD `3595 3626`, remainder `3627 3644`, out-dir
  `n8192_persistence_probe_2m/`). No flag change.
- Executed once under `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` with
  single-thread exports, `ulimit -v 2097152`, `timeout 1200`, interpreter
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`. Exit code 0.
- Stdout summary: `integrity_all_pass: true`,
  `outcome_label: TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE`,
  `records_completed: 3`, set-delta
  (1676/1676, intersection 713, a-b 963, b-a 963, size-delta 0).

## 2. Stage-B artifact inventory (15 files, root now PRESENT)

Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/n8192_persistence_probe_2m/`

| file | bytes |
|---|---|
| `frozen_plan.json` | 57345 |
| `input_and_predecessor_identity.json` | 56626 |
| `per_block_arm_outcomes.jsonl` (3 records) | 17418 |
| `aggregate_summary.json` | 60285 |
| `report.md` | 2671 |
| `ir5_full_manifest.json` | 3981 |
| `A_hazard_bits_f32le.bin` | 32768 |
| `A_inprefix_u8.bin` | 8192 |
| `A_inu_u8.bin` | 8192 |
| `B_hazard_bits_f32le.bin` | 32768 |
| `B_inprefix_u8.bin` | 8192 |
| `B_inu_u8.bin` | 8192 |
| `O_hazard_bits_f32le.bin` | 32768 |
| `O_inprefix_u8.bin` | 8192 |
| `O_inu_u8.bin` | 8192 |

- IR-5 manifest: `ir5full-v1`; A/B/O hazard series `[8192] <f4` LE;
  in-prefix/in-u `[8192] u1`; order-identity = fresh digest `66aefea8…` on
  A/O, spike digest `355a32d3…` on B; per-record digests match the JSONL
  references (A hazard `2d66f009…` shared by all three records).
- Per-record K pins: A/B `k1=84 k2=1676 k_total=1760`; O `k1=0 k2=1676`;
  budget literal replayed on every record; construction digest `d77466ec…`;
  prior digest `b16f5216…` on every record.

## 3. Per-record geometry (within-N descriptive ONLY, n=1 — Q-G1/Q-G2)

Outcomes recorded as `verify_failed` on all 3 records with `l1_exact: true`
(A/B), first-error layer L2 on all 3, `undetected: 0`, `nonfinite: 0`.
Per-record outcome rows are recorded for completeness and are explicitly NOT
read as recovery rates (no transition cells computed:
`transition_cells_computed: false`).

Q-G1 — spike-local L2 fail-site geometry, paired within-N (same block, same
K sizes with Δ exactly 0, byte-identical hazard series A/B):

- A (newly-derived frozen-order equivalent): first error L2 coord 193;
  X-domain disclosed (`l2_fail_in_prefix: true`), U-domain undisclosed
  (`false`); fail-site hazard 0.509 bits vs record prefix mean 0.873 bits
  (below-mean); R=8 nbhd mean 0.678 bits, nbhd floor frac 0.0; record prefix
  floor frac 0.000597; record floor hits 12 (rate 0.000732); IR2 rank pct
  0.4001.
- B (spike-local order): first error L2 coord 3; X-domain undisclosed under
  the spike order (`l2_fail_in_prefix: false`), U-domain undisclosed
  (`false`); fail-site hazard 0.438 bits vs record prefix mean 0.888 bits
  (below-mean); R=8 nbhd mean 0.757 bits, nbhd floor frac 0.0; record prefix
  floor frac 0.0; record floor hits 1084 (rate 0.0662); IR2 rank pct 0.0500.
- O (true-L1 oracle diagnostic, never operational): geometry identical to A
  (coord 193, disclosed, rank 0.4001, 12 floor hits).
- Byte-exact set context: A-vs-B disclosed-L2 symmetric difference 963/963,
  intersection 713, size-delta exactly 0.

Q-G2 — top-hazard-tail disclosure contrast at the same N (within-N only):

- IR-1 prefix-tail8 mass: A=1, B=0, O=1 (prefix mass 1676 / outside 6516 on
  every record).
- IR-4 top-16 in-prefix count: A=4, B=3, O=4 (top-16 coords/hazards
  byte-identical across records; only the per-order in-prefix flags differ).
- IR-3 above-threshold prefix counts: A 403/403 above lo/hi (frac 0.2405;
  thresholds 0.873/1.746 bits), B 419/417 (frac 0.25/0.2488; thresholds
  0.888/1.777 bits), O = A.
- Prefix hazard means: A=O=0.873 bits, B=0.888 bits.

No FER / reliability / efficiency / leakage / key-rate / recovery / scaling /
promotion reading is made; no cross-N inference; no H2 input.

## 4. Split open audit

- counts-calibration: 0/0 (V25 counts NPZ never opened/statted/listed).
- DEV: 1/1 (single content open of the 2M pairs parquet at first DEV contact;
  `one_open_per_protected_input` true, `reopen_attempted: false`).
- 1M: 0. 1.5M: 0. 2M-non-DEV: 0.
- Registered content paths (2): worktree `raw_prior_2m.npz` + 2M pairs
  parquet. `no_unregistered_access: true`. HOLD remainder 3627..3644 and
  1.5M stubs 2172..2212 / 2725..2766 counted never-decoded, never contacted
  beyond counting.

## 5. Integrity gates, recount, counters, resources, sizes

- Integrity: ALL PASS — 31/31 gates true, `failing_integrity_gates: []`
  (incl. `reuse_prior_arrays_identity`, `new_construction_identity_8192`,
  `fresh_order_identity_A_8192`, `spike_order_identity_B_8192`,
  `order_derivation_identity`, `k_rule_derived`, `target_population_contract`,
  `dev_population_exact`, `blocks_exact_with_declared_remainder`,
  `three_records_exact`, `sampling_calls_exact`, `sc_calls_exact`,
  `tags_exact`, `orders_valid_k_prefixes_within_registered_arms`,
  `order_set_delta_recorded`, `hazard_instrumentation_complete`,
  `ir_payload_complete`, `ir5_full_manifest_identity`, `truth_isolation`,
  `oracle_isolation`, `undetected_zero`, `nonfinite_zero`,
  `disclosure_recount_exact`, `resource_limits_met_and_no_abort`,
  `evidence_size_rule_met`).
- Recount: mismatch 0; key-dependent 26172 bits; public 245949 bits
  (A/B 8864+81983 each, O 8444+81983).
- SC/tag/genie: Stage-B sampling calls 0; SC calls 5/5 (A 2 / B 2 / O 1);
  tags 3/3; derivation budget (Stage A) 16 TRAIN blocks / 32 genie calls,
  unchanged.
- Wall/RSS: total wall 8.36 s (records ≈ 2.80/2.81/1.62 s) vs 1200 s ceiling;
  RSS peak 366481408 B (≈ 350 MiB) vs 2 GiB ceiling; vm_peak 1567472 KB vs
  `ulimit -v 2097152`; `resource_stop_fired: false`.
- IR-5 size check: largest single file 60285 B (`aggregate_summary.json`);
  largest `.bin` 32768 B; per-record binary triple 48 KiB; every file ≤ 2 MB.
- No writes under `results/` or `comparison_bench/outputs_comparison/` by
  this operator (pre-existing unrelated working-tree modifications noted in
  §6, untouched). No commit/push. `test_evidence_package.py` NOT run.

## 6. Acceptance IDs (stage-appropriate)

- P20T-R1: COMPLETE (Stage-A reuse/derivation pins replayed by the runner
  gates at Stage-B load; all identity gates true).
- P20T-R2: COMPLETE (DEV HOLD 3595..3626 one N=8192 block; remainder +
  1.5M stubs counted never-decoded; consumed-range exclusions held).
- P20T-R3: COMPLETE (caps A/B 8864 Δ=0, O 8444, public 81983; recount 0;
  set-delta byte-exact size-delta 0).
- P20T-R4: COMPLETE (arms/pins unchanged; formula-id + R=8 re-freeze +
  program pin replayed).
- P20T-R5: COMPLETE (endpoints separated; undetected isolated at 0; nine
  scalars + IR-1..IR-4 PRESENT on every completed record with own-order
  prefix flags; IR-5 nine `.bin` + manifest digests matched).
- P20T-R6: COMPLETE (single attempt; reads 0/0 + 1/1 + 0 + 0 + 0; 5 SC /
  3 tags / 3 records; no abort; stop rules intact).
- P20T-R7: Pre-EXECUTE PASS recorded; Pre-RESULT + main-thread acceptance
  PENDING (not this operator's to grant).
- P20T-R8: Stage-A suites green carried (23/23); no commit/push; frozen
  dirs untouched by this operator. Pre-existing working-tree modifications
  NOT made by this operator: `M .codebuddy/memory/2026-09-19.md`,
  `M comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`,
  `M docs/decision-log.md` (left untouched).
- P20T-R9: COMPLETE (derivation gate held — no mismatch, DEV consumed
  exactly once by the authorized attempt).

## 7. Honest-scope statement (verbatim from §0)

a descriptive N=8192 persistence probe on one 2M HOLD-tail block; n=1;
within-N paired comparison only (Q-G1/Q-G2); no FER/reliability/efficiency/
leakage/key-rate/recovery/scaling/promotion claim; no cross-N inference; no
H2 input; the DEV block is consumed by this packet; the HOLD remainder
3627..3644 and all 1.5M remainders stay untouched; any exact count is COMPLETE
when integrity holds and is explicitly NOT read as a recovery rate.

## 8. Close state

- `STATUS.yaml`: `attempts_used: 1`, `dev_reads_used: 1`,
  `stage_b_out_root: PRESENT`,
  `planning_stage: STAGE_B_COMPLETE_AWAITING_PRE_RESULT`; counts 0/0,
  1M/1.5M/2M-non-DEV 0; `pre_result_review: PENDING`,
  `main_thread_acceptance: PENDING`, `next_gate: PRE_RESULT_REVIEW_AWAITING`.
- Next gate: independent Pre-RESULT review on the actual artifacts above.

(End of return)
