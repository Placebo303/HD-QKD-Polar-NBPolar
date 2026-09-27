# Pre-RESULT Review — m2-scl-rescue-g2g3

Reviewer: independent Pre-RESULT reviewer (reviewer-go role, AGENTS.md §3/§10.3).
Scope: `workspace/m2_scl_rescue_g2g3/{run.py,results.json,part_*.json,
EXECUTION_TRANSCRIPT.md,STATUS.yaml,TASK_PACKET.md,prereg.md,
PRE_EXECUTE_REVIEW.md,session_setup_execution_error_attempt1.json}`.
No decoder rerun, no raw `.ttbin` read, no git write. Only new files written:
this file and `review_scratch/verify.py` (independent recompute script).

## Verdict: PASS

## Findings

1. **[PASS] Post-Pre-EXECUTE code change scope.** `workspace/m2_scl_rescue_g2g3/`
   is git-ignored (`git status --ignored` shows `!! workspace/m2_scl_rescue_g2g3/`),
   so no git diff exists between attempt-1 and attempt-2 `run.py`; verified by
   structural cross-check against `PRE_EXECUTE_REVIEW.md`'s described structure
   instead. Every item PRE_EXECUTE verified (TARGETS 9-tuple, K1=319/K2=6492/N=32768,
   ARM, LIST_WIDTH_L=16/TOP_M=4, kdb formula, budgets/MAX_PARALLEL=8, write scope,
   fidelity-field diff) is byte-identical in the current `run.py`. The only
   structural change is: `chain, scl_joint_mod = _load_scl_joint(mod)` now called
   once in `main()` (line 581) and passed as explicit params into
   `_reproduce_session_context(mod, chain, scl_joint_mod, session)` (signature
   line 175, call site line 586) for both sessions, instead of loading inside
   that function per session. This exactly matches the documented root cause in
   `session_setup_execution_error_attempt1.json` (`_load_g2_decoder_chain`'s
   pandas-stub guard breaks on a second per-process call) and the fix note in
   `run.py`'s own docstring (lines 184-198). No parameter, seed, target block,
   K/N/window, tag_master/eval_seed, or budget constant changed. Attempt 1
   traceback confirms the death occurred inside module/chain loading during G3
   session-context setup, before any raw-data read for G3 and before any
   per-block fidelity/SC/SCL/tag call for either session (0 part files, G2's own
   setup had already completed and printed real `H_total`/`f_book` — that is
   session-context prep, not a target-block measurement). This matches the
   AGENTS.md/coordinator-approved "pre-measurement implementation-defect restart"
   exception; attempt 1 is correctly excluded from `reruns` (`STATUS.yaml
   counters.reruns=0`).

2. **[PASS] Fidelity check.** Independently re-read both reference
   `per_block_outcomes.jsonl` files (arm=`B_M2_32f_candidate`) for all 9 target
   blocks and diffed the 5 fields (`outcome`, `first_error_coordinate`,
   `first_error_layer`, `l1_exact`, `hard_l2_exact`) against `results.json`'s
   `fidelity.expected`: exact match for all 9, including G3 block 11's
   `l1_exact=False` (the one block with a genuine SC L1 error). Reference files'
   mtimes (2026-09-22) predate this run (2026-09-27/28) and `git status` shows
   no changes under `workspace/m2_prior_validation/` or `workspace/analysis/` —
   the frozen ground truth was not touched.

3. **[PASS] Rescue counting — independently recomputed** (script written to
   `review_scratch/verify.py`, run against all 9 `part_*.json`): recomputing
   `accepted = crc_pass AND tag_pass`, `exact = accepted AND label_exact`,
   `undetected = accepted AND NOT label_exact`, `verify_failed = NOT accepted`
   from each part file's raw `crc_pass`/`tag_pass`/`label_exact` reproduces
   `results.json`'s stored values for all 9 blocks with zero mismatches, and
   reproduces the summary exactly: `n_fidelity_ok=9, n_rescued_exact=8,
   n_still_failed=1, n_undetected=0`. `results.json["blocks"]` is byte-identical
   to the 9 `part_*.json` files. No block has `exact` and `undetected` both true
   (isolation holds structurally, not just numerically). `label_exact`'s
   comparison object is `labels_true` from `mod.g2_truth_views(alice, ...)`,
   i.e. Alice's real frames (`run.py` lines 369-372) — genuine truth, not a
   proxy. Independently confirmed in `scl_joint.py` (source, not just the
   Pre-EXECUTE report) that `scl_joint_decode` ranks candidates purely by
   `joint_metric` (`sorted(..., key=lambda k: (-merged[k].joint_metric, ...))`,
   line 247) computed from Bob-only likelihoods (docstring: "this function
   never sees Alice truth"), and only *after* that fixed ranking does it scan
   for the first candidate whose `crc_hat == crc_true_int` (lines 250-256) — so
   truth enters only via the disclosed CRC/tag evaluation, never the ranking
   itself, consistent with the task's truth-use constraint.

4. **[PASS] Disclosure bookkeeping / `f_book`.** `kdb_no_crc=34119`,
   `kdb_with_crc=34135` reproduce exactly from `5*(319+6492)+64` and `+16`.
   `docs/decision-log.md` line 5465 records the canonical G1R2 (= G2 session)
   value `H_M2 = 0.8168138` — `results.json`'s G2 `h_total_bits=0.8168138204133305`
   matches this to full precision, confirming reuse of the accepted G2 entropy
   figure rather than a hand-filled number. G3's `h_total_bits=0.8214782076249098`
   has no prior decision-log precedent (none found by grep) — it is freshly and
   legitimately derived by the same frozen `model_entropy_bits` call on G3's own
   CAL fit inside `run.py`, consistent with §5.5 (never hand-filled). Recomputing
   `f_book = kdb/(H*N)` independently from these two H values reproduces
   `1.274745/1.275343` (G2) and `1.267507/1.268101` (G3) to the stated precision.

5. **[PASS] Per-source breakdown.** Recomputed independently from the 9 part
   files: G2 = 1/3 blocks still failed (block 5 only; blocks 1/12 rescued), G3 =
   0/6 still failed (all 6 rescued) — matches the operator's report exactly.

6. **[PASS] Claim scope.** `results.json["claims"]`, `results.json["classification"]`,
   and `STATUS.yaml`'s `classification`/`main_thread_rulings` all explicitly
   disclaim any threshold, pass/fail verdict, state-string change, or
   candidate/accepted promotion, and state the count is withheld entirely if
   fidelity is compromised. No file in scope combines this 8/9 rescue count with
   the 19 previously-successful B-arm blocks into any synthetic aggregate (grepped
   for "13/16", "14/14", "FER", full-success framing — none found). **Permitted
   conclusion sentence**: "Of the 9 real-data B-arm blocks that failed under the
   frozen SC path, CRC-16-aided joint SCL(L=16, top_m=4) re-decoding the *same*
   failed blocks recovers 8/9 exactly (G2 2/3, G3 6/6), with 0 undetected errors;
   whether SCL would also preserve or disturb the 19 blocks SC already decoded
   correctly has not been tested on real data and is not claimed here."

7. **[PASS] Write scope.** `git status --porcelain` (repo root) shows changes
   only under `workspace/pytest-evidence-test/` and one test-fixture CSV —
   unrelated pre-existing modifications, not touched by this task. This
   review's own writes are confined to `PRE_RESULT_REVIEW.md` and
   `review_scratch/verify.py` under `workspace/m2_scl_rescue_g2g3/`. The two
   reference `per_block_outcomes.jsonl` files carry mtimes from 2026-09-22,
   before this run existed, and show no git diff — confirming they were not
   modified by this diagnostic.

## Blocking items

None. No FAIL findings.
