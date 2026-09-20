# P20T Stage-A implementation notes

Operator: `coder-fast` Stage-A instance (2026-09-20, branch
`codex/nbpolar-phase0`). No commit/push. Operator never self-accepts.

## 1. Callsite inventory (§12, read-only, no logic change)

- Import target: accepted `l2_alt_maintain_2m` (as `p20o`), accepted
  `raw_prior_val_1p5m` (as `p20m`), accepted `l2_mechanism_probe_2m` (as
  `p20s`, for the IR histogram helpers only), accepted
  `l2_alt_hold_1p5m` (as `p20n`, for the session-agnostic frozen α=1
  prefloor rule `alt_prefloor_table` ONLY — no 1.5M file, path, frame
  range, or K literal enters this module), accepted `operational_f13`
  (as `opf`, for flag/record/resource/loader utilities +
  `OperationalBlockResult`), `empirical_genie_scaling`
  (`select_empirical_split`: exhaustive TRAIN-residual (K1,K2)
  selection), `target_n_scaling` (`budget_k_total`: frozen f-budget
  rule), `target_construction` (`entropy_bits`: H recomputation inside
  the accepted verifier), `per_session_calibration`
  (`canonical_prior_digest`: digest recipe pin only), `prior`
  (`derive_p2`), `transform` (`polar_transform`), `algebra`
  (`make_gf32`), `toeplitz_tag`, `SOURCE_IDS`, `load_pairs_table` /
  `normalize_pair_columns` (Stage-B DEV loader, never used at Stage A).
  Reused without modification: `run_operational_block` /
  `run_oracle_control_block` (+ `OracleControlResult`),
  `verify_dev_manifest_2m` (JSON-only), `verify_session_prior_2m`
  (pure arrays), `_hazard_bits`, `_raw_p2_from_counts`,
  `first_error_coordinate`, `l1_prefix_positions` /
  `l2_prefix_positions`, `seed_bits_for`, `_stat_record`, `_block_view` /
  `_dev_block_scoring` / `_scoring_absent` / `_selected_diagnostics`,
  block/recount event helpers, `_ir_hist_edges` / `_ir_hist_counts`,
  `OPERATIONAL_PROVENANCE` / `ORACLE_PROVENANCE`, `ArmSpec`,
  `HAZARD_FIELDS`, `RAW_PRIOR_NPZ_KEYS`, plus `construction.py` /
  `prior.py` / `sc.py` contracts as called through them.
- P16-local pattern reference (read-only): `operational_f13`
  construction/allocation pattern (P16-02: synthetic TRAIN blocks,
  pooled risks, worst-first orders, K rule, TRAIN-residual (K1,K2)
  selection) — executed here through the accepted
  `sample_synthetic_train_blocks` choke point with the P20T frozen
  seeds/budget at N=8192.
- P20S-local pattern references (read-only): `l2_mechanism_probe_2m`
  spike-derivation + IR-5 writer patterns (mirrored at N=8192 with the
  in-packet K2 pin + TRAIN-pooled h2_mean spike input + R=8 re-freeze).
- P20T-local logic lives ONLY in the new module (own N=8192 constants,
  derivation program, cross-file gate with P20T messages,
  single-segment containment/frame-set/exclusions, `form_single_segment_block`,
  `derive_spike_order_8192` + file writers/verifiers + `order_set_delta_8192`,
  arm-specific nine-scalar wrapper `_nine_scalars_for_arm`,
  `_ir_hazard_diagnostics_8192` (same caps/formulas as P20Q §7, in-packet
  K2 pin, full-block N=8192 pin), `_ir5_full_block_arrays_8192` +
  `_ir5_full_block_writer_8192` + `check_ir5_manifest_identity`,
  `ir_payload_complete` / `ir_payload_tables` (P20T arm names + within-N
  flags + IR-5 references), `mechanism_diagnostics` / `build_aggregates` /
  `oracle_isolation_ok` / `hazard_instrumentation_complete` (A/B/O arms +
  dual-digest rule), own arm table / record writers / gates / frozen plan
  / label / CLI): the N=32768 recorders, gates, K literals, tag domain,
  and IR-5 geometry cannot serve N=8192, so they are mirrored with P20T
  pins rather than edited. No accepted file was modified (verified by
  `git status`: only the pre-existing unrelated modifications plus the
  Stage-A additive files below).
- §2 delta list d1–d9 evidenced in the new module docstring; the P20Q
  `_ir_hazard_diagnostics` code point is cited there as the carried-over
  callsite pattern for the §7 recorder extension.
- F-median8 formula: carried shape from `TASK_PACKET.md` §3 with R=8
  re-frozen as a NEW decision for 8192-geometry; the spike-h source
  (TRAIN-pooled mean L2 hazard, shared 16-block budget, +0/+0 of its
  own) is pinned in the module docstring, `DERIVATION_PROGRAM_PIN`,
  `SPIKE_FORMULA_TEXT`, and `P20T_FREEZE.md` §4 for Pre-EXECUTE
  adjudication (R7). Implementation necessities: TRAIN-pooled `h2_mean`
  vector + R=8 clipped natural neighborhoods + stable descending
  argsort (ties ascending).

## 2. Files changed (additive only; no accepted file touched)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/n8192_persistence_probe_2m.py`
  (new, ~4180 lines): thin N=8192 probe runner per §2 d1–d9 + frozen
  derivation program (`run_derive_stage_a` + `derive_spike_order_8192`).
  Stage-A pin fill is the single edit of eight literals
  (`FROZEN_K_TOTAL/FROZEN_K1/FROZEN_K2` = 1760/84/1676,
  `FROZEN_BUDGET_LITERAL`, `FROZEN_TRAIN_RESIDUAL =
  0.013377854243068005`, construction/order/spike digests
  `d77466.../66aefe.../355a32...`).
  Three conformance fixes during Stage A: (i) `--verify-derivation`
  accepts and checks `--spike-formula` (packet §10 template lists it);
  (ii) budget-literal float-repr hardening — records/plan/summary carry
  the same-run-H display while the gate replays the K_total int from the
  frozen H (the recomputed H `...7475` differs from the frozen literal
  `...7477` in the last digit; both give K_total 1760); (iii) chunk_rows
  128 needs its own contract check (`_check_chunk_contract_8192`
  carrying the accepted sc structural pins — the accepted
  `opf._check_chunk_contract` hard-pins 512).
- `comparison_bench/tests/test_nbpolar_n8192_persistence_probe_2m.py`
  (new, 23 tests): focused injected tests, seeds `2026092401..2026092407`,
  `workspace/p20t/<uuid>/` temp roots (incl. one injected end-to-end
  single-block three-arm run exercising the real SC path on synthetic
  data with 3 records, arm-specific digests, IR-1..IR-4 PRESENT + IR-5
  manifest references, and the byte-exact set-delta).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/construction_and_allocation_8192.json`
  (new, 1819 B, Stage-A product): K rule + (K1,K2) + TRAIN residual +
  sampling provenance; file-bytes sha256 pinned above and in
  `P20T_FREEZE.md`.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/fresh_orders_8192.json`
  (new, 97848 B, Stage-A product): full fresh L1+L2 length-8192
  permutations + provenance; file-bytes sha256 pinned above and in
  `P20T_FREEZE.md`.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/new_spike_order_8192.json`
  (new, 98906 B, Stage-A product): full carried-L1 + spike-L2
  length-8192 permutations + provenance (formula-id + R=8 re-freeze +
  program pin + zero-sampling attestation); file-bytes sha256 pinned
  above and in `P20T_FREEZE.md`.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/P20T_FREEZE.md`
  (new): Stage-A freeze (this packet's §11 product, incl. the byte-exact
  A-vs-B set-delta table and both commands verbatim).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/STATUS.yaml`
  (pin/state updates only): `stage_a_authorized_step1_pasted` (standing
  pre-authorization), `planning_stage: STAGE_A_IN_PROGRESS` → Stage-A
  return state, K/budget/residual/digest pins filled; stage_b/decoder/
  protected flags stay false, `attempts_used: 0`, all read counters 0.
- OpenSpec delta (already exists, verified consistent, NOT restructured):
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/`
  (spec.md + design.md + proposal.md) + `tasks.md` RN section. Every
  R1–R11 shape matches the Stage-A outputs (K_total 1760 actual vs
  ≈1760 estimate; key 8864 exact; tag 81983; 48 KiB/record IR-5).

## 3. Test commands and results

- `.venv`-equivalent (sibling-checkout interpreter per packet §10;
  local `.venv` absent):
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_n8192_persistence_probe_2m.py -p no:cacheprovider`
  → **23/23 passed** (~60 s).
- Stage-A reuse + derivation commands (§10 templates, worktree files only):
  `--derive ...` (executed EXACTLY once, exit 0) → K 1760/84/1676,
  residual 0.013377854243068005, digests
  `d77466.../66aefe.../355a32...`
  (`train_blocks_used: 16, train_genie_calls: 32,
  counts_content_opens: 0, dev_contact: 0`);
  `--verify-derivation ...` → `verified: true`, `dev_contact: 0`,
  H `0.02566204884275839 / 0.8069006731309891 / 0.8325627219737475`
  (within 1e-12 of frozen).
- `FROZEN_COMMAND` verified field-by-field against the packet §10
  Stage-B template with pins filled (all 18 flag fields verbatim +
  timeout/ulimit/exports).
- Predecessor suites untouched and not re-run (no shared logic changed).

## 4. Deviations and scope notes

- The focused suite covers pins/population/tag-domain/derivation-seed
  arithmetic, the frozen derivation (determinism/permutation/
  F-median8-scores/tie-break/refusals, seed/budget/n refusals), the
  Stage-A file round-trip + verifier refusals, the byte-exact set-delta,
  the derivation-identity replay (digest/H/`p_b`/floor pins +
  construction/order/spike identity/program/formula pins + K-rule
  replay), the single-segment population + gate family (a)->(g) +
  formation refusals, the nine carried scalars incl. the arm-specific
  digest rule + nullability, IR-1..IR-4 (all PRESENT: 64-bin histogram
  shapes/caps, rank-percentile formula + nullability, IR-3 two-threshold
  1.0x/2.0x counts on synthetic hazards, top-16 shapes/ranks) + IR-5
  N=8192-sized (array shapes/dtypes/popcount, writer byte
  sizes/digests/fail-if-present, nine-file manifest identity + tamper
  refusals, budgets) + the truth-isolation sentinel, the sampling-chain
  smoke (test seeds, 2x2 blocks), the declared-remainder +
  counted-1.5M measurement, the one-open guard refusals, CLI refusals,
  the grep rule, and one injected end-to-end run (real SC path,
  synthetic data, 3 records, 15 files incl. manifest-verified `.bin`
  files). The end-to-end run's gates are structural
  (digests/IR/set-delta/records), never an outcome verdict.
- Fixture tests use the established patched-pin seam (`patched(p20t,
  "FROZEN_*", ...)`); the real-file replay is evidenced by the
  operator-run `--derive`/`--verify-derivation` above, not by tests.
- Three fixture-luck findings, all fixed without scope change: (i) the
  K-drift refusal test had to keep k_total constant (k1+1/k2−1) to reach
  the pins-level `k_rule_derived` check (the file gate fires first
  otherwise); the runner was reordered to check pins before file reads;
  (ii) `opf._check_chunk_contract` hard-pins 512, so Stage A added
  `_check_chunk_contract_8192` carrying the accepted sc structural pins
  with the re-frozen 128 value; (iii) the IR tests needed the eight
  Stage-A pins patched to fixture values (recorders gate on them).
- One float-repr finding, fixed without scope change: the recomputed H
  (`...7475`) differs from the frozen H literal (`...7477`) in the last
  digit, so budget-literal STRINGS differ while K_total is identical
  (1760); records/plan/summary carry the same-run-H display and the
  gate replays the K_total int from the frozen H plus the same-run-H
  display equality.
- `git status` shows pre-existing unrelated modifications
  (`.codebuddy/memory/2026-09-19.md`,
  `comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`,
  `docs/decision-log.md`) not made by this operator and left untouched.

## 5. D-status

- No D1/D2 recompute beyond the packet's own TRAIN-residual selection;
  the P20O D1/D2 2M literals are NOT carried. The TRAIN-residual
  selection outcome (K1=84, K2=1676, residual 0.013377854243068005) is
  frozen in the construction file BEFORE any DEV contact; a
  derivation-gate mismatch would have BLOCKED at Stage A with DEV
  untouched and no Stage-B request (not triggered).

(End of file)
