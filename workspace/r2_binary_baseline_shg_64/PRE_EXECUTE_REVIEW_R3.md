# PRE-EXECUTE REVIEW ROUND 3 — r2-binary-baseline-shg-64

Reviewer: independent reviewer-go, round 3. Scope: round-2 F4 fix, C4/C5/C6, D_BIN_TWO_PASS, plus regression of round-1/2 PASS items.
Not done: no `--authorize` real phase, no `.ttbin` read, no git write. Only synthetic/mocked scripts (WSL venv).

## Verdict: PASS_WITH_COMMENTS (no blocking finding)

## 1. F4 — PASS
- `_total_wall_exceeded` = `(_now() - t_start) > BUDGET_WALL_S_TOTAL` (strict >; edge E3), `_CLOCK = time.monotonic`, t_start taken at the top of main(). Checkpoints: before each session's construction and before each pass-1 block (and before each pass-2 block). The running block is never interrupted (per-block wall is separate). not_started record: status `not_started_total_wall_budget`, grid=[], block_hash None, `not_started_detail{checked_at, elapsed_total_wall_s, budget_wall_s_total}`; frame ranges/strata kept.
- Doc-vs-code: serial, 4 h, 1200 s cumulative-from-block-start (checked before each grid point), 4 GiB VmHWM after each grid point — AUTHORIZATION copy block + table, contract §6/§7/§8, prereg, TASK_PACKET E4/S15/S16, STATUS all agree. Grep: no stale "8-way/parallel/120 s/hard-terminate" text outside explicit "removed" notes. run.py: MAX_PARALLEL / HARD_TERMINATE_MARGIN_S / CONSTRUCTION_PATH / multiprocessing gone (py_compile OK).
- Note (accepted, documented): the block running at the 4 h mark may finish, so total wall can exceed 4 h by up to ~20 min worst case (per-block cap 1200 s).

## 2. D_BIN_TWO_PASS — PASS
- Pass 1 (`_run_one_block_entry`) calls decode with `run_scl=False`; pass 2 (`_run_scl_block_entry`) uses `run_sc=False` and only READS the pass-1 part (status check) — never rewrites it. Real-function edge case E1 (synthetic N=256, fake clock, fake CA-SCL): pass-1 part_*.json SHA-256 identical before the first pass-2 call vs after the whole run (6/6); pass 2 truncated after 1 block -> 1 `ok` + 5 `ca_scl_not_started_total_wall_budget` scl_parts (grid entries carry the status).
- D / Tables A, B1 / margins / block accounting depend only on `records` (pass 1): E1 D=6 exact=6 unchanged; B2 counts only status-ok pass-2 entries and `table_B2_coverage` states n_B2 vs n_matched; per-margin/per-session `ca_scl_descriptive.coverage` (E1: 1/6) + n_not_started. Truncation flag semantics correct (not_started entries never enter numerator or SC counts).
- Start guard also rejects any top-level `scl_part_*.json` (G7 PASS).

## 3. C4 — PASS
- Identity 64 = contributing + error + not_started + resource_abort (+ no_grid_entries) with precedence not_started > error > contributing (>=1 status ok entry) > resource_abort > no_grid; `consistent` also requires n_records == expected. Verified W5 (8=1+1+1+5) and E2 (error block 3 + contributing 3 -> consistent, error_block_ids listed, no scl_part for the error session). Per-margin tallies/tables use block-level status=="ok" only, same convention as the NB `_taxonomy_counts`.
- undetected scan covers all pass-1 records (any block/entry status). CA-SCL question: pass-2 records have NO accept/tag/exact concept (only codeword msg_exact), hence no `undetected` field exists there; E4 confirms an `undetected` key inside an scl record is ignored (stop_undetected False). Recommendation: do NOT let the CA-SCL arm trigger stop_undetected (it is undefined for that arm); Pre-RESULT should state it explicitly. (Note stop_undetected is only a post-hoc flag; nothing halts mid-run, consistent with contract §5/§7.)

## 4. Self-checks (all run by me)
py_compile OK; AST %-scan 0; `_smoke_synthetic.py` PASS (5.2 s); `_test_aggregation.py` PASS; `_test_f3_guard.py` G1–G7 PASS; `_test_total_wall.py` W1–W6 PASS; own edge cases `review_scratch/edge_r3.py` E1–E4 PASS (E1/E2 exercise the REAL block runners + `_run_sessions`, which the shipped tests replace with fakes — they pass).

## 5. Regression — intact
Data source still the imported r2_fer_shg_64 `build_session_blocks/_reproduce_session_context`; construction uses only `g2_cal_ids` (CAL32); write scope: `git status` under src/, experiments/, tools/, workspace/r2_fer_shg_64/ empty; comparison_bench/src shows only the pre-existing NB untracked `_native/`, `scl_joint_native.py`; packet dir has no results.json, part_*.json, scl_part_*.json or dry_run/ (my tests used tempdirs).

## Non-blocking comments
- C7. `VmHWM` is process-lifetime peak in a single serial process: one breach (e.g. during construction/pass 1) marks every later entry, including all of pass 2, `resource_abort_rss_post_decode`. Realistically <4 GiB here; Pre-RESULT should check `rss_gib_peak_advisory` values.
- C8. Pass 2 iterates G2 blocks first, so a truncation leaves CA-SCL coverage session-skewed (G3 first to be lost); `taxonomy_by_session[*].ca_scl_descriptive.coverage` shows it — Pre-RESULT must read B2 with that in mind.
- C9. Worst-case total = 4 h + one block; if pass 1 itself is cut, pooled D<56 => INSUFFICIENT is flagged (already documented).
- Carried: C3 (f_book_sc not monotone in margin, MC noise, unseeded numba RNG in calibration) still applies; PI authorization text still needs the blanks in AUTHORIZATION_PROMPT filled (main-thread step, not a code issue).
