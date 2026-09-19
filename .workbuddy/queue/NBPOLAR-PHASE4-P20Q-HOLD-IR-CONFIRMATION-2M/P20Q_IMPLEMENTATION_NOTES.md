# P20Q Stage-A implementation notes

Operator: `coder-fast` Stage-A instance (2026-09-19, branch
`codex/nbpolar-phase0`). No commit/push. Operator never self-accepts.

## 1. Callsite inventory (§12, read-only, no logic change)

- Import target: accepted `l2_alt_maintain_2m.py` (3476 lines), imported
  read-only as `p20o` by the new runner. Reused without modification:
  `run_operational_block` / `run_oracle_control_block` (+ result types),
  `verify_predecessor_construction`, `verify_dev_manifest_2m`,
  `verify_session_prior_2m`, `verify_alt_l2_arrays_2m`,
  `verify_alt_l2_identity_2m`, `verify_stage_b_order_file_2m`,
  `feasibility_literals_2m`, `check_k_literals`, `frozen_arm_table` /
  `check_frozen_arm_table`, `planned_totals`, `_l2_hazard_diagnostics`
  (the carried-over §7 callsite pattern), `_hazard_bits`,
  `_raw_p2_from_counts`, `first_error_coordinate`,
  `l1_prefix_positions` / `l2_prefix_positions`, `seed_bits_for`,
  `_block_view` / `_dev_block_scoring` / `_scoring_absent` /
  `_selected_diagnostics`, block/recount event helpers,
  `maintenance_diagnostics`, `build_aggregates`,
  `hazard_instrumentation_complete`, `oracle_isolation_ok`, `ArmSpec`,
  plus `construction.py` / `prior.py` / `sc.py` contracts as called
  through them.
- HOLD-specific logic lives ONLY in the new module (own frozen HOLD
  constants, cross-file gate with P20Q messages, `verify_hold_containment`,
  `verify_consumed_exclusions_hold`, `form_hold_blocks`,
  `_ir_hazard_diagnostics`, `ir_payload_complete`, `ir_payload_tables`,
  own record writers / gates / frozen plan / label / CLI): the VAL-hardcoded
  predecessor gates (`verify_val_containment`,
  `verify_consumed_exclusions_2m`, `form_val_blocks`, `_check_dev_frames`)
  cannot serve HOLD ranges, so they are mirrored with HOLD ranges rather
  than edited.
- §2 delta list d1–d8 evidenced in the new module docstring; the P20O
  `_l2_hazard_diagnostics` code point is cited there as the carried-over
  callsite pattern for the §7 IR recorder extension.

## 2. Files changed (additive only; no accepted file touched)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_ir_2m.py`
  (new, ~1400 lines): thin HOLD-IR runner per §2 d1–d8.
- `comparison_bench/tests/test_nbpolar_l2_alt_hold_ir_2m.py`
  (new, 14 tests): focused injected tests, seeds `2026092331..2026092337`,
  `workspace/p20q/<uuid>/` temp roots.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/P20Q_FREEZE.md`
  (new): Stage-A freeze (this packet's §11 product).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/STATUS.yaml`
  (untouched by operator; planner values confirmed: `stage_a_authorized_step1_pasted:
  true`, `planning_stage: STAGE_A_IN_PROGRESS`, `stage_b_authorized: false`,
  `decoder_execution_authorized: false`, `protected_data_read_authorized: false`,
  `attempts_used: 0`, all read counters 0).
- OpenSpec delta (planner-staged, verified consistent, unchanged):
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20q/spec.md`
  + `tasks.md` P20Q section.

## 3. Test commands and results

- `.venv`-equivalent (sibling-checkout interpreter per packet §10):
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_l2_alt_hold_ir_2m.py -p no:cacheprovider`
  → **14/14 passed** (~35 s).
- Stage-A verify command (§10 template, worktree files only):
  `... l2_alt_hold_ir_2m --verify-reuse --prior .../raw_prior_2m.npz
  --prior-digest b16f52... --alt-prior .../alt_l2_tables_2m.npz --alt-digest
  98e254... --order-file .../raw_prior_orders_2m.json --order-digest
  b22554... --k1 334 --k2 6746`
  → `verified: true`, `hold_contact: 0`, D2 margin `4791.0965273576585`.
- `FROZEN_COMMAND` verified byte-identical to the packet §10 Stage-B
  template with pins filled (programmatic string comparison).
- Predecessor suite untouched and not re-run (no shared logic changed).

## 4. Deviations and scope notes

- The focused tests exercise gates, formation, recorders (nine-scalar via
  the accepted recorder, IR-1..IR-5 formulas/caps/nullability), the
  truth-isolation sentinel, CLI refusals, one-open guard refusals (via
  monkeypatched gate helpers + guard flags), and the grep rule on injected
  fixtures — but they do NOT run a full injected end-to-end Stage-B pass
  (no SC execution in tests; the SC path is the accepted
  `run_operational_block` / `run_oracle_control_block` reused read-only).
  This matches the P20O test-suite precedent (gate/recorder coverage, no
  full injected run).
- The accepted alt/order verifiers pin digests against the predecessor
  module constants, so the positive `verify_reuse` fixture test uses the
  established patched-pin seam (`patched(p20o, "FROZEN_*_DIGEST", ...)` +
  `FROZEN_ALT_H1_INC`); the real-file replay is evidenced by the
  operator-run `--verify-reuse` above, not by tests.
- `git status` shows a pre-existing unrelated modification
  (`comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`)
  not made by this operator and left untouched.

## 5. D1/D2 replay outcome

D1 literals replayed from worktree files BEFORE any HOLD contact;
D2 = FEASIBLE (margin `4791.09652735766`); HOLD stays 0/1. A replay
mismatch would have ended the packet at Stage A with HOLD untouched and
no Stage-B request — no mismatch occurred.

(End of file)
