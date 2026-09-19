# P20S Stage-A implementation notes

Operator: `coder-fast` Stage-A instance (2026-09-20, branch
`codex/nbpolar-phase0`). No commit/push. Operator never self-accepts.

## 1. Callsite inventory (§12, read-only, no logic change)

- Import target: accepted `l2_alt_hold_ir_2m.py`, imported read-only as
  `p20q` by the new runner. Reused without modification:
  `run_operational_block` / `run_oracle_control_block` (+ result types),
  `verify_predecessor_construction`, `verify_dev_manifest_2m`,
  `verify_session_prior_2m`, `verify_alt_l2_arrays_2m`,
  `verify_alt_l2_identity_2m`, `verify_stage_b_order_file_2m`,
  `feasibility_literals_2m`, `check_k_literals`, `verify_reuse` (P20Q
  reuse core), `_hazard_bits`, `_raw_p2_from_counts`,
  `first_error_coordinate`, `l1_prefix_positions` / `l2_prefix_positions`,
  `seed_bits_for`, `_stat_record`, `_block_view` / `_dev_block_scoring` /
  `_scoring_absent` / `_selected_diagnostics`, block/recount event helpers,
  `_ir_hist_edges` / `_ir_hist_counts`, `OPERATIONAL_PROVENANCE` /
  `ORACLE_PROVENANCE`, plus `construction.py` / `prior.py` / `sc.py`
  contracts as called through them.
- Session helpers (all §12-listed, read-only): `l2_alt_hold_1p5m.py`
  as `p20n` (session-agnostic frozen α=1 prefloor rule
  `alt_prefloor_table` ONLY — no 1.5M file, path, frame range, or K
  literal enters this module);
  `raw_prior_val_1p5m.py` as `p20m` (session-agnostic budget-literal
  recomputation `verify_budget_literal` ONLY);
  `l2_alt_maintain_2m.py` as `p20o` (`_l2_hazard_diagnostics` (nine
  scalars), `HAZARD_FIELDS` incl. the ninth U-domain scalar, `ArmSpec`,
  consumed-session source tags, 2M reuse path/digest/H/K pins,
  `FROZEN_ALT_FLOOR_HIT_RATE`); `operational_f13.py` as `opf`
  (flag/record/resource/loader utilities); `prior.derive_p2` +
  `transform.polar_transform` contracts as called.
- P20R-local pattern reference (read-only): `l2_order_position_1p5m.py`
  dual-order + derivation-program pattern (`derive_new_l2_order` shape).
- P20S-local logic lives ONLY in the new module (own merged-2M
  constants, cross-file gate with P20S messages,
  `verify_merged_containment`, `verify_merged_frame_set_identity`,
  `verify_consumed_exclusions_merged`, `form_merged_blocks`,
  `derive_spike_l2_order` + `write_spike_order_file` +
  `verify_spike_order_file` + `order_set_delta`, arm-specific nine-scalar
  wrapper `_nine_scalars_for_arm`, `_ir_hazard_diagnostics` (same
  caps/formulas as P20Q §7, K2=6746 pin, full-block N=32768 pin),
  `_ir5_full_block_arrays` + `_ir5_full_block_writer` +
  `check_ir5_manifest_identity`, `ir_payload_complete` /
  `ir_payload_tables` (P20S arm names + IR-5 references),
  `mechanism_diagnostics` / `build_aggregates` / `oracle_isolation_ok` /
  `hazard_instrumentation_complete` (A/B/O arms + dual-digest rule), own
  arm table / record writers / gates / frozen plan / label / CLI): the
  2M-HOLD/1.5M predecessor gates and the single-order recorders cannot
  serve dual 2M orders on a merged block, so they are mirrored with merged
  pins/dual orders rather than edited. No accepted file was modified
  (verified by `git status`: only the pre-existing unrelated modifications
  plus the Stage-A additive files below).
- §2 delta list d1–d9 evidenced in the new module docstring; the P20Q
  `_ir_hazard_diagnostics` code point is cited there as the carried-over
  callsite pattern for the §7 recorder extension.
- F-median8 formula: carried verbatim from `TASK_PACKET.md` §3 (user
  decision 2026-09-20, DECIDED; F-mean8 / F-multi8_32 rejected, retained
  as historical context only in the packet); the implementation
  necessities pinned in `P20S_FREEZE.md` §4 are the cell convention
  `j = b*32+u2` (C-order) + hard-L1 argmax + clipped R=8 median windows.
  Recomputed `p2_alt` from the `counts_ab` worktree array reproduces the
  frozen alt file bit-exactly, so the
  "worktree-`raw_prior_2m.npz`-arrays-only" input contract and the "under
  the frozen DECIDED 2026-09-20 F-median8 formula-id" derivation contract
  both hold.

## 2. Files changed (additive only; no accepted file touched)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_mechanism_probe_2m.py`
  (new, ~3960 lines): thin mechanism-probe runner per §2 d1–d9 + frozen
  derivation program (`derive_spike_l2_order`); Stage-A pin fill is the
  single `FROZEN_SPIKE_ORDER_DIGEST_B` literal
  (`139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864`).
  One template-conformance fix during Stage A: `--verify-reuse` accepts
  and checks `--spike-formula` (packet §10 template lists it; the initial
  flag classification refused it as Stage-B-only).
- `comparison_bench/tests/test_nbpolar_mechanism_probe_2m.py`
  (new, 22 tests): focused injected tests, seeds `2026092361..2026092367`,
  `workspace/p20s/<uuid>/` temp roots (incl. one injected end-to-end
  single-block three-arm run exercising the real SC path on synthetic
  data with 3 records, arm-specific digests, IR-1..IR-4 PRESENT + IR-5
  manifest references, and the byte-exact set-delta).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json`
  (new, 438128 B, Stage-A product): full carried L1 + spike-L2 permutations +
  provenance; file-bytes sha256 pinned above and in `P20S_FREEZE.md`.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/P20S_FREEZE.md`
  (new): Stage-A freeze (this packet's §11 product, incl. the byte-exact
  A-vs-B set-delta table and both commands verbatim).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/STATUS.yaml`
  (pin/state updates only): `stage_a_authorized_step1_pasted` (standing
  pre-authorization), `planning_stage: STAGE_A_IN_PROGRESS` → Stage-A
  return state, `frozen_spike_order_digest_B` filled, D2 replay outcome
  frozen; stage_b/decoder/protected flags stay false, `attempts_used: 0`,
  all read counters 0.
- OpenSpec delta (staged, verified consistent):
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20s/spec.md`
  + `tasks.md` P20S section.

## 3. Test commands and results

- `.venv`-equivalent (sibling-checkout interpreter per packet §10):
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_mechanism_probe_2m.py -p no:cacheprovider`
  → **22/22 passed** (~63 s).
- Stage-A reuse + derivation commands (§10 templates, worktree files only):
  `--derive-spike-order ...` → spike digest
  `139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864`
  (`sampling_calls: 0, genie_calls: 0, dev_contact: 0`);
  `--verify-reuse ...` (four digests + K1/K2 + formula) → `verified: true`,
  `dev_contact: 0`, D2 margin `4791.0965273576585` (within 1e-6 of frozen
  `4791.09652735766`).
- `FROZEN_COMMAND` verified byte-identical to the packet §10 Stage-B
  template with pins filled (programmatic string comparison).
- Predecessor suites untouched and not re-run (no shared logic changed).

## 4. Deviations and scope notes

- The focused suite covers gates, merged formation, the frozen derivation
  (determinism/permutation/F-median8-scores/tie-break/refusals), the spike
  file round-trip + verifier refusals, the byte-exact set-delta, the
  reuse-identity replay (digests/H/`p_b`/`p1`-equality/key-set pins +
  spike identity/program/formula pins), the budget/K-literal replay (S2-i;
  alt-H never a budget input; zero sampling/genie pins), the nine carried
  scalars incl. the arm-specific digest rule + nullability, IR-1..IR-4
  (all PRESENT: 64-bin histogram shapes/caps, rank-percentile formula +
  nullability, IR-3 two-threshold 1.0×/2.0× counts on synthetic hazards,
  top-16 shapes/ranks) + IR-5 uncapped (array shapes/dtypes/popcount,
  writer byte sizes/digests/fail-if-present, nine-file manifest identity +
  tamper refusals, budgets) + the truth-isolation sentinel, the
  declared-remainder + counted-1.5M measurement, the one-open guard
  refusals, CLI refusals, the grep rule, and one injected end-to-end run
  (real SC path, synthetic data, 3 records, 15 files incl. manifest-verified
  `.bin` files). The end-to-end run's gates are structural
  (digests/IR/set-delta/records), never an outcome verdict.
- The accepted alt/order verifiers pin digests against predecessor module
  constants, so positive fixture tests use the established patched-pin seam
  (`patched(p20o/l2s, "FROZEN_*", ...)`); the real-file replay is
  evidenced by the operator-run `--verify-reuse`/`--derive-spike-order`
  above, not by tests. The D2 margin gate compares against the frozen
  real-data literal, so fixture tests patch `FROZEN_D2_MARGIN_BITS` with
  the fixture-computed margin (ceiling − ideal).
- Three fixture-luck findings, all fixed without scope change: (i) the
  injected `extra` table rows used frame 3644, which lies inside the HOLD
  tail remainder range (remainder gate counts pool rows) — replaced with
  frame 3645; (ii) the hostile truth-isolation test passes a real GF32
  field since the real IR-5 arrays path runs alongside the mocked IR-1..IR-4
  recorder; (iii) the bad-order-digest refusal surfaces the inner P20Q
  `reuse_order_freeze` gate name (the wrapper `reuse_order_freeze_A` gate
  runs after the base replay), so the test matches that substring.
- `git status` shows pre-existing unrelated modifications
  (`.codebuddy/memory/2026-09-19.md`,
  `comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`)
  not made by this operator and left untouched.

## 5. D1/D2 replay outcome

- D1 literals recomputed from the worktree counts at Stage A (zero DEV
  reads): `ce_alt` 0.8850983725781965, `ce_incumbent`
  0.8069006731253678, ceilings 33794/35464, `alt_ideal_length_bits`
  29002.90347264234 — all replay-EXACT.
- D2 `alt_construction_budget_feasibility_replayed` = **FEASIBLE**
  (margin `4791.09652735766` bits, TRAIN-only, zero merged-DEV reads),
  evaluated BEFORE any DEV contact; the packet proceeds to independent
  Pre-EXECUTE. A replay mismatch would have BLOCKED at Stage A with DEV
  untouched and no Stage-B request (not triggered).

(End of file)
