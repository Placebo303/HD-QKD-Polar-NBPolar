# P20R Stage-A implementation notes

Operator: `coder-fast` Stage-A instance (2026-09-19, branch
`codex/nbpolar-phase0`). No commit/push. Operator never self-accepts.

## 1. Callsite inventory (§12, read-only, no logic change)

- Import target: accepted `l2_alt_hold_ir_2m.py` (2609 lines), imported
  read-only as `p20q` by the new runner. Reused without modification:
  `run_operational_block` / `run_oracle_control_block` (+ result types),
  `verify_predecessor_construction`, `_hazard_bits`,
  `_raw_p2_from_counts`, `first_error_coordinate`,
  `l1_prefix_positions` / `l2_prefix_positions`, `seed_bits_for`,
  `_stat_record`, `_block_view` / `_dev_block_scoring` / `_scoring_absent` /
  `_selected_diagnostics`, block/recount event helpers,
  `ir_payload_complete`, `IR_FIELDS`, `_ir_hist_edges` / `_ir_hist_counts`,
  `oracle_isolation_ok` (2M-name version, superseded locally),
  `OPERATIONAL_PROVENANCE` / `ORACLE_PROVENANCE`, plus `construction.py` /
  `prior.py` / `sc.py` contracts as called through them.
- 1.5M session helpers (all §12-listed, read-only): `l2_alt_hold_1p5m.py`
  as `p20n` (`verify_alt_l2_arrays`, `verify_alt_l2_identity`,
  `feasibility_literals`, `check_k_literals`, `alt_prefloor_table`,
  `_l2_hazard_diagnostics` (eight X-domain scalars),
  `FROZEN_ALT_FLOOR_HIT_RATE`); `raw_prior_val_1p5m.py` as `p20m`
  (`verify_corrected_prior`, `verify_stage_b_order_file_p20m`,
  `verify_budget_literal`, path/digest/H/K pins); `l1_order_1p5m.py` as
  `p20l` (1.5M DEV path/size/sha pins, manifest/construction pins,
  `verify_dev_manifest`); `l2_alt_maintain_2m.py` as `p20o`
  (`HAZARD_FIELDS` incl. the ninth U-domain scalar, `ArmSpec`,
  consumed-session source tags); `operational_f13.py` as `opf`
  (flag/record/resource/loader utilities); `prior.derive_p2` +
  `transform.polar_transform` contracts as called.
- P20R-local logic lives ONLY in the new module (own frozen VAL-remainder
  constants, cross-file gate with P20R messages,
  `verify_val_remainder_containment`,
  `verify_consumed_exclusions_val_remainder`, `form_val_remainder_blocks`,
  `derive_new_l2_order` + `write_new_order_file` + `verify_new_order_file`
  + `order_set_delta`, arm-specific nine-scalar wrapper
  `_nine_scalars_for_arm` (accepted eight + frozen ninth U-domain formula),
  `_ir_hazard_diagnostics` (same caps/formulas as P20Q §7, K2=6689 pin),
  `ir_payload_tables` (new arm names), `maintenance_diagnostics` /
  `build_aggregates` / `oracle_isolation_ok` / `hazard_instrumentation_complete`
  (new arm names + dual-digest rule), own arm table / record writers /
  gates / frozen plan / label / CLI): the 2M-hardcoded predecessor gates
  (`verify_hold_containment`, `verify_consumed_exclusions_hold`,
  `form_hold_blocks`, `_check_dev_frames`, arm tables, K2=6746 gates) and
  the single-order recorders cannot serve dual 1.5M orders, so they are
  mirrored with 1.5M pins/dual orders rather than edited. No accepted file
  was modified (verified by `git status`: only the pre-existing unrelated
  `comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`
  modification plus the Stage-A additive files below).
- §2 delta list d1–d8 evidenced in the new module docstring; the P20Q
  `_ir_hazard_diagnostics` code point is cited there as the carried-over
  callsite pattern for the §7 recorder extension.
- B-1 ranking functional: carried verbatim from `TASK_PACKET.md` §3 (user
  decision 2026-09-19); the one implementation necessity pinned in
  `P20R_FREEZE.md` §4 is the cell convention `j = b*32+u2` (C-order).
  Recomputed `p2_alt` from the `counts_ab` worktree array reproduces the
  frozen alt file bit-exactly (max-abs-diff `0.0`), so the
  "worktree-`raw_prior_1p5m.npz`-arrays-only" input contract and the "under
  `p2_alt`" functional coincide exactly.

## 2. Files changed (additive only; no accepted file touched)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_order_position_1p5m.py`
  (new, 3468 lines): thin order-position runner per §2 d1–d8 + frozen
  derivation program (`derive_new_l2_order`); Stage-A pin fill is the single
  `FROZEN_NEW_ORDER_DIGEST_B` literal
  (`c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751`).
- `comparison_bench/tests/test_nbpolar_l2_order_position_1p5m.py`
  (new, 21 tests): focused injected tests, seeds `2026092341..2026092347`,
  `workspace/p20r/<uuid>/` temp roots (incl. one injected end-to-end
  single-block dual-order run exercising the real SC path on synthetic
  data with 4 records, arm-specific digests, and IR-1..IR-5 PRESENT).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/new_l2_order_1p5m.json`
  (new, Stage-A product): full carried L1 + new-L2 permutations +
  provenance; file-bytes sha256 pinned above and in `P20R_FREEZE.md`.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/P20R_FREEZE.md`
  (new): Stage-A freeze (this packet's §11 product, incl. the byte-exact
  A-vs-B set-delta table and both commands verbatim).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/STATUS.yaml`
  (pin/state updates only): `stage_a_authorized_step1_pasted: true`,
  `planning_stage: STAGE_A_IN_PROGRESS` → Stage-A return state,
  `frozen_new_order_digest_B` + `frozen_derivation_program` filled, D2
  replay outcome frozen; stage_b/decoder/protected flags stay false,
  `attempts_used: 0`, all read counters 0.
- OpenSpec delta (staged, verified consistent):
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20r/spec.md`
  + `tasks.md` P20R section.

## 3. Test commands and results

- `.venv`-equivalent (sibling-checkout interpreter per packet §10):
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_l2_order_position_1p5m.py -p no:cacheprovider`
  → **21/21 passed** (~73 s).
- Stage-A reuse + derivation commands (§10 templates, worktree files only):
  `--derive-new-order ...` → new-B digest
  `c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751`
  (`sampling_calls: 0, genie_calls: 0, dev_contact: 0`);
  `--verify-reuse ...` (four digests + K1/K2) → `verified: true`,
  `dev_contact: 0`, D2 margin `3928.304784481981`.
- `FROZEN_COMMAND` verified byte-identical to the packet §10 Stage-B
  template with pins filled (programmatic string comparison).
- Predecessor suites untouched and not re-run (no shared logic changed).

## 4. Deviations and scope notes

- The focused suite covers gates, formation, the frozen derivation
  (determinism/permutation/ranking/tie-break/refusals), the new-order
  file round-trip + verifier refusals, the byte-exact set-delta, the
  reuse-identity replay (digests/H/`p_b`/`p1`-equality/key-set pins +
  new-B identity/program pins), the budget/K-literal replay (S2-i; alt-H
  never a budget input; zero sampling/genie pins), the nine carried
  scalars incl. the arm-specific digest rule + nullability, IR-1..IR-5
  (all PRESENT: 64-bin histogram shapes/caps, rank-percentile formula +
  nullability, IR-3 two-threshold 1.0×/2.0× counts on synthetic hazards,
  top-16 shapes/ranks, capped-series truncation flag) + the truth-isolation
  sentinel, the declared-remainder measurement, the one-open guard
  refusals, CLI refusals, the grep rule, and one injected end-to-end run
  (real SC path, synthetic data, 4 records). The end-to-end run's gates are
  structural (digests/IR/set-delta/records), never an outcome verdict.
- The accepted alt/order verifiers pin digests against predecessor module
  constants, so positive fixture tests use the established patched-pin seam
  (`patched(p20m/p20n/l2r, "FROZEN_*", ...)`); the real-file replay is
  evidenced by the operator-run `--verify-reuse`/`--derive-new-order`
  above, not by tests.
- Two seed-luck findings, both fixed without scope change: (i) the
  synthetic p2 from sparse counts is last-axis-degenerate, so the
  truth-mutation test uses a denser synthetic prior; (ii) the end-to-end
  test's asserts moved inside the patched-pin context.
- `git status` shows a pre-existing unrelated modification
  (`comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`)
  not made by this operator and left untouched.

## 5. D1/D2 replay outcome

D1 literals replayed from worktree files BEFORE any DEV contact;
D2 = FEASIBLE (margin `3928.304784481981`); DEV stays 0/1. A replay
mismatch would have ended the packet at Stage A with DEV untouched and
no Stage-B request — no mismatch occurred.

(End of file)
