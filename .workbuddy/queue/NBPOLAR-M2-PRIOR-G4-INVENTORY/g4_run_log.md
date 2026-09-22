# G4 run log — NBPOLAR-M2-PRIOR-G4-INVENTORY

- built_at: 2026-09-22T21:52:37
- command: `/home/karel_303/.venvs/timetagger/bin/python g4_build_inventory.py`
- python: 3.12.3
- branch: codex/nbpolar-phase0 | authorization: recorded in STATUS.yaml before build
- budget: wall 0.15 s / 300 s, RSS peak 0.026 GiB / 2 GiB, single-threaded
- counters: sc_calls 0, tag_invocations 0, g4_runs 1, reruns 0, rebuilds 0
- resources: read-only aggregation over frozen JSON/JSONL; no decode, no SC, no tags, no raw-data read, no sigma re-derivation (string consistency check only)

## Self-checks (all ran BEFORE any output file was written)

| check | ok | detail |
|-------|----|--------|
| SC3a_branch | PASS | ref: refs/heads/codex/nbpolar-phase0 |
| SC3b_authorization_recorded | PASS | AUTHORIZED line present: True |
| SC2a_to_freeze_pointer_list | PASS | 44 pointers |
| SC2b_to_freeze_non_null | PASS | null/empty: [] |
| SC1a_input_paths_exist | PASS | missing: [] |
| SC1b_locators_non_empty | PASS | no locators: [] |
| SC1c_manifest_count | PASS | 63 vs manifest_count 63 |
| SC4_target_outputs_absent | PASS | already exist: [] |
| SC10a_N_K_agreement | PASS | cell n/k1/k2 vs frozen constants |
| SC10b_orders_len | PASS | l1/l2 order presence + length (no digest computed) |
| SC10c_p16_digest_string | PASS | inner_digest string equality vs frozen digest |
| SC10d_window_mod_skip_agreement | PASS | w/mod/skip in g2/g3 freeze configs vs frozen constants |
| SC10e_tag_master_agreement | PASS | tag_master values vs frozen constants |
| SC10f_frame_pairs_bin | PASS | frame_pairs/bin_width_ps vs frozen constants |
| SC10g_floor_chunk_line | PASS | g2_freeze.md line 91 |
| SC10h_sigma_string_consistency | PASS | sigma string across g3_summary / G3_ADJUDICATION / decision-log: 114.43029692866367 |
| SC10i_md_locators | PASS | markdown locator spot checks |
| SC5a_shg1_cal_set_equality | PASS | sources differing from g1 cal_ids.json: [] |
| SC5b_g1_closure_common_lists | PASS | cal_ids vs cal_ids_closure common list keys |
| SC5c_g2_eval_blocks | PASS | g2 eval_blocks |
| SC5d_shg2_cal_set_equality | PASS | shg_2 cal_ids vs packet freeze vs input freeze copy |
| SC5e_cal_counts_expected | PASS | cal list lengths vs frozen expectations |
| SC6_recount_G2 | PASS | rows=42 key=1432998 public=13765206 tags=42 undetected=0 mismatch_list=[] |
| SC6_recount_G3 | PASS | rows=42 key=1432998 public=13765206 tags=42 undetected=0 mismatch_list=[] |
| SC5_rows_match_source_G1 | PASS | inventory CAL rows vs workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/cal_ids.json |
| SC10_runlog_heading_run_log.md | PASS | # G1 science run log — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL |
| SC10_runlog_heading_run_log_closure.md | PASS | # G1 Phase-A closure run log — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL |
| SC5_rows_match_source_G1R2 | PASS | inventory CAL rows vs workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/cal_ids.json |
| SC10_runlog_heading_run_log.md | PASS | # G1R2 science run log — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR |
| SC10_runlog_heading_run_log_closure.md | PASS | # G1R2 Phase-A closure run log — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR |
| SC5_rows_match_source_G2 | PASS | g2 CAL rows vs source |
| SC10j_runlog_heading_g2 | PASS | # G2 one-shot run log — NBPOLAR-M2-PRIOR-G2-DECODE |
| SC5_rows_match_source_G3 | PASS | g3 CAL rows vs source |
| SC10j_runlog_heading_g3 | PASS | # G3 one-shot run log — NBPOLAR-M2-PRIOR-G3-CONFIRM |
| SC7a_unique_ids | PASS | duplicate ids |
| SC7b_schema_enums_mapping_sources | PASS |  |
| SC7c_zero_to_freeze_rows | PASS | rows still to_freeze |
| SC7d_expected_coverage_CONTRACT | PASS | unmet classes: [] |
| SC7d_expected_coverage_G1 | PASS | unmet classes: [] |
| SC7d_expected_coverage_G1R2 | PASS | unmet classes: [] |
| SC7d_expected_coverage_G2 | PASS | unmet classes: [] |
| SC7d_expected_coverage_G3 | PASS | unmet classes: [] |
| SC8a_row_count_agreement | PASS | json=107 stage=107 class=107 handling=107 md=107 |
| SC8b_ids_sequential | PASS | per-stage id sequences |
| SC8c_counts_sums | PASS | counts sums vs row_count |
| SC9a_wall_budget | PASS | 0.15s / 300s |
| SC9b_rss_budget | PASS | 0.026 GiB / 2 GiB |

## Rows built (107; by stage {'CONTRACT': 20, 'G1': 21, 'G1R2': 21, 'G2': 22, 'G3': 23})

- G4-CONTRACT-001  ok  contract_param / structural_public_parameter
- G4-CONTRACT-002  ok  contract_param / structural_public_parameter
- G4-CONTRACT-003  ok  contract_param / structural_public_parameter
- G4-CONTRACT-004  ok  construction / structural_public_parameter
- G4-CONTRACT-005  ok  construction / structural_public_parameter
- G4-CONTRACT-006  ok  contract_param / structural_public_parameter
- G4-CONTRACT-007  ok  contract_param / structural_public_parameter
- G4-CONTRACT-008  ok  contract_param / structural_public_parameter
- G4-CONTRACT-009  ok  contract_param / structural_public_parameter
- G4-CONTRACT-010  ok  contract_param / structural_public_parameter
- G4-CONTRACT-011  ok  contract_param / structural_public_parameter
- G4-CONTRACT-012  ok  contract_param / structural_public_parameter
- G4-CONTRACT-013  ok  contract_param / structural_public_parameter
- G4-CONTRACT-014  ok  tag / structural_public_parameter
- G4-CONTRACT-015  ok  tag / structural_public_parameter
- G4-CONTRACT-016  ok  contract_param / structural_public_parameter
- G4-CONTRACT-017  ok  fitted_prior / structural_public_parameter
- G4-CONTRACT-018  ok  reveal_bits_diagnostic / diagnostic_only_never_lambda
- G4-CONTRACT-019  ok  contract_param / structural_public_parameter
- G4-CONTRACT-020  ok  disclosure_bits / charged_0_labeled_public_ec_only_not_secure
- G4-G1-001  ok  contract_param / structural_public_parameter
- G4-G1-002  ok  ledger_allocation / structural_public_parameter
- G4-G1-003  ok  alignment_record / structural_public_parameter
- G4-G1-004  ok  threshold_or_gate_record / structural_public_parameter
- G4-G1-005  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G1-006  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G1-007  ok  ledger_allocation / structural_public_parameter
- G4-G1-008  ok  threshold_or_gate_record / structural_public_parameter
- G4-G1-009  ok  fitted_prior / structural_public_parameter
- G4-G1-010  ok  result_publication / result_publication
- G4-G1-011  ok  result_publication / result_publication
- G4-G1-012  ok  result_publication / result_publication
- G4-G1-013  ok  threshold_or_gate_record / structural_public_parameter
- G4-G1-014  ok  blocked / blocked_never_public
- G4-G1-015  ok  blocked / blocked_never_public
- G4-G1-016  ok  blocked / blocked_never_public
- G4-G1-017  ok  tag / structural_public_parameter
- G4-G1-018  ok  none_recorded / structural_public_parameter
- G4-G1R2-001  ok  contract_param / structural_public_parameter
- G4-G1R2-002  ok  ledger_allocation / structural_public_parameter
- G4-G1R2-003  ok  alignment_record / structural_public_parameter
- G4-G1R2-004  ok  threshold_or_gate_record / structural_public_parameter
- G4-G1R2-005  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G1R2-006  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G1R2-007  ok  ledger_allocation / structural_public_parameter
- G4-G1R2-008  ok  threshold_or_gate_record / structural_public_parameter
- G4-G1R2-009  ok  fitted_prior / structural_public_parameter
- G4-G1R2-010  ok  result_publication / result_publication
- G4-G1R2-011  ok  result_publication / result_publication
- G4-G1R2-012  ok  result_publication / result_publication
- G4-G1R2-013  ok  threshold_or_gate_record / structural_public_parameter
- G4-G1R2-014  ok  blocked / blocked_never_public
- G4-G1R2-015  ok  blocked / blocked_never_public
- G4-G1R2-016  ok  blocked / blocked_never_public
- G4-G1R2-017  ok  tag / structural_public_parameter
- G4-G1R2-018  ok  none_recorded / structural_public_parameter
- G4-G2-001  ok  contract_param / structural_public_parameter
- G4-G2-002  ok  ledger_allocation / structural_public_parameter
- G4-G2-003  ok  alignment_record / structural_public_parameter
- G4-G2-004  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G2-005  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G2-006  ok  ledger_allocation / structural_public_parameter
- G4-G2-007  ok  fitted_prior / structural_public_parameter
- G4-G2-008  ok  disclosure_bits / counted_in_leak_IR
- G4-G2-009  ok  disclosure_bits / counted_in_leak_IR
- G4-G2-010  ok  result_publication / result_publication
- G4-G2-011  ok  tag / structural_public_parameter
- G4-G2-012  ok  result_publication / result_publication
- G4-G2-013  ok  threshold_or_gate_record / structural_public_parameter
- G4-G2-014  ok  result_publication / result_publication
- G4-G2-015  ok  result_publication / result_publication
- G4-G2-016  ok  result_publication / result_publication
- G4-G2-017  ok  result_publication / result_publication
- G4-G2-018  ok  blocked / blocked_never_public
- G4-G2-019  ok  blocked / blocked_never_public
- G4-G2-020  ok  blocked / blocked_never_public
- G4-G2-021  ok  none_recorded / structural_public_parameter
- G4-G2-022  ok  none_recorded / structural_public_parameter
- G4-G3-001  ok  contract_param / structural_public_parameter
- G4-G3-002  ok  ledger_allocation / structural_public_parameter
- G4-G3-003  ok  ledger_allocation / structural_public_parameter
- G4-G3-004  ok  alignment_record / structural_public_parameter
- G4-G3-005  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G3-006  ok  cal_frame_list / sacrificed_excluded_from_denominator
- G4-G3-007  ok  ledger_allocation / structural_public_parameter
- G4-G3-008  ok  fitted_prior / structural_public_parameter
- G4-G3-009  ok  disclosure_bits / counted_in_leak_IR
- G4-G3-010  ok  disclosure_bits / counted_in_leak_IR
- G4-G3-011  ok  result_publication / result_publication
- G4-G3-012  ok  tag / structural_public_parameter
- G4-G3-013  ok  result_publication / result_publication
- G4-G3-014  ok  threshold_or_gate_record / structural_public_parameter
- G4-G3-015  ok  result_publication / result_publication
- G4-G3-016  ok  result_publication / result_publication
- G4-G3-017  ok  participation_disclosure / structural_public_parameter
- G4-G3-018  ok  result_publication / result_publication
- G4-G3-019  ok  result_publication / result_publication
- G4-G3-020  ok  blocked / blocked_never_public
- G4-G3-021  ok  blocked / blocked_never_public
- G4-G3-022  ok  blocked / blocked_never_public
- G4-G3-023  ok  none_recorded / structural_public_parameter
- G4-G1-019  ok  none_recorded / structural_public_parameter
- G4-G1-020  ok  none_recorded / structural_public_parameter
- G4-G1-021  ok  none_recorded / structural_public_parameter
- G4-G1R2-019  ok  none_recorded / structural_public_parameter
- G4-G1R2-020  ok  none_recorded / structural_public_parameter
- G4-G1R2-021  ok  none_recorded / structural_public_parameter

## Disclosure recount (frozen cross-check)

- G2: rows=42 key=1432998 public=13765206 tags=42 undetected=0
- G3: rows=42 key=1432998 public=13765206 tags=42 undetected=0

## Acceptance IDs

- G4-0..G4-4: evidence produced in `g4_freeze_config.json`, `g4_inventory.json`, `g4_inventory.md`, `g4_counts.json`; reviewed by R1 (independent Pre-RESULT) and R2 (main-thread adjudication) — both PENDING, no self-approval in this log.
- outcome strings frozen BEFORE this build; the state string is applied only by the reviewed return.


## Post-write read-back

- SC8d_postwrite_readback: PASS — row_count == len(JSON rows) == MD table rows == counts rows_by_stage sum, after re-reading the written files.
