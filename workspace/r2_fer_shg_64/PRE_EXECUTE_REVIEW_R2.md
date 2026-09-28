# Pre-EXECUTE Review — Round 2 — r2-fer-shg-64

Reviewer: independent reviewer-go subagent (AGENTS.md §3/§10.3/§10.4).
Date: 2026-09-28. Scope: `workspace/r2_fer_shg_64/run.py` only (delta review
against round-1 FAIL, `PRE_EXECUTE_REVIEW.md`, finding F1). No execution, no
decoder run, no raw `.ttbin` read, no git write performed by this review.
Writes confined to this file and `review_scratch/verify_taxonomy_r2.py`.

## Verdict: **PASS**

F1 (round-1 blocking defect) is fixed. Both post-F1 changes (a)
`_taxonomy_counts` ok-gate and (b) `stop_undetected` all-block scan are
correctly implemented and internally consistent. No new defect found.

---

## Findings

### R2-F1 — RESOLVED: F1 no longer reproduces

`_taxonomy_counts` (run.py:751-780) now builds `ok = [b for b in blocks if
b.get("status")=="ok" and b.get("scl")]` and sums `exact`/`verify_failed`/
`decode_failed`/`undetected` only over `ok`. `resource_abort` (line 763) and
`error` (line 764) are still computed over the full `blocks` list, keyed on
`status` string content, independent of the `ok` gate — so a
`resource_abort_wall_post_scl` block (populated `scl`, non-`"ok"` status)
now lands **only** in `resource_abort`, never in `exact`/`D`.

Verified by importing the real `_taxonomy_counts`/`_wilson` from run.py
(`importlib.util.spec_from_file_location`, `exec_module` — confirmed this
does not trigger `main()`, guarded by `if __name__ == "__main__"`) and
feeding an 11-block synthetic set covering every status branch, including
the exact F1 regression case (`resource_abort_wall_post_scl` with
`scl["exact"]=True`) — see `review_scratch/verify_taxonomy_r2.py`. Result:
`D_valid_denominator=3` (not 4), `exact=1` (not 2) — the leaked block did
NOT enter D. Five-way taxonomy mutually exclusive/exhaustive over `ok`
blocks; `resource_abort=5` correctly picked up all 5 `resource_abort_*`
statuses (2 in-worker post-scl-abort variants + pre_scl + 2 parent-side
terminate/not-started records, both of which correctly carry `scl: None`
per `_resource_abort_record`, run.py:657-685). Full run output: `ALL CHECKS
PASSED`.

### R2-F2 — Change (b) `stop_undetected` verified correct and intentional

`main()` (run.py:829-840) now computes `n_undetected_total` and
`undetected_block_ids` by scanning **all** `blocks` (`b.get("scl") and
b["scl"]["undetected"]`), not the `ok`-gated subset — so an over-budget
block (`resource_abort_wall_post_scl`) with `scl["undetected"]=True` still
trips `stop_undetected=True` and appears in `undetected_block_ids`, even
though it is correctly excluded from the mutually-exclusive taxonomy's
`undetected`/`D` count. This is the documented intent (comment at
run.py:829-830: "undetected is a security signal ... including an
over-budget ... block excluded from the taxonomy"). Both fields use the
identical predicate (verified by inspection — same boolean expression,
same field access), so they cannot drift apart. Reproduced in
`review_scratch/verify_taxonomy_r2.py`: with block#4 (ok/undetected) and
block#8 (post-scl-abort/undetected) present, `n_undetected_total=2`,
`stop_undetected=True`, `undetected_block_ids` length 2; a clean set with
no undetected anywhere gives `n_undetected_total=0` (no false positive).

### R2-F3 — `fidelity_mismatch`/`fidelity_compromised` unaffected by (a) — PASS

`fidelity_mismatch` (run.py:765) is computed over the full `blocks` list
(`b["status"]=="STOPPED_FIDELITY_MISMATCH"`), not the `ok`-gated subset, so
change (a) cannot affect it. `fidelity_compromised = bool(pooled
["fidelity_mismatch"] >= 1)` (run.py:836) reads `pooled["fidelity_mismatch"]`
from the same unaffected field. Confirmed in the synthetic test: with 1
`STOPPED_FIDELITY_MISMATCH` block present, `fidelity_mismatch=1` and the
`fidelity_compromised` formula evaluates `True`. This top-level flag and
the `R2_TAG_MASTER=2026102801`/`R2_EVAL_SEED=2026092801` fill were both
already present and already PASSed in round 1 (items 2, 5) — confirmed
unchanged here, not a new edit.

### R2-F4 — Full-file re-read: no undocumented change beyond (a)/(b)

No backup of the round-1 `run.py` exists (`git log`/`git status` on
`workspace/r2_fer_shg_64/` return nothing — this directory is untracked),
so a `git diff --no-index` was not possible; instead the entire current
`run.py` (923 lines) was read top-to-bottom and checked against every
quoted line range and PASS item in round-1's `PRE_EXECUTE_REVIEW.md`.
Everything round 1 already verified as present/correct (frozen ARM/SCL
params/K1/K2/P16 digest, 64-block layout constants, seed scheme, budget
constants `MAX_PARALLEL=8`/`BUDGET_WALL_S_PER_BLOCK=1200.0`/
`BUDGET_RSS_GIB_PER_BLOCK=2.0`/`BUDGET_WALL_S_TOTAL=10800.0`/
`HARD_TERMINATE_MARGIN_S=120.0`, `_scl_call`'s five-way boolean formulas at
lines 531-537, one-shot/no-overwrite guards in `main()`) is textually
identical to what round 1 quoted or described. The only functional diffs
found are: (1) the `_taxonomy_counts` ok-gate (F1 fix) with an added
explanatory comment (run.py:755-757); (2) `_run_one_block_entry`'s
`resource_abort_wall_post_scl` line gained a trailing comment only (line
624), no logic change; (3) the `stop_undetected`/`undetected_block_ids`
block (run.py:829-840) with its explanatory comment. No other line differs
in effect from round 1's described state.

---

## Items re-checked (inherited from round 1, re-confirmed valid)

- **Branch/cleanliness**: still `codex/nbpolar-phase0`; this review touched
  only `PRE_EXECUTE_REVIEW_R2.md` (new) and
  `review_scratch/verify_taxonomy_r2.py` (new). No other file touched.
- **STATUS.yaml**: `main_thread_fix_F1_2026_09_28` entry (line 183)
  correctly describes both changes (a)/(b), matches the actual diff found
  above. `pre_execute_round1: {verdict: FAIL, ...}` (line 182) correctly
  recorded. `D_BUDGET_CONFLICT` remains `PENDING PI` (line 181) — same as
  round 1, where this was explicitly ruled non-blocking for the
  Pre-EXECUTE code-correctness verdict (round-1 item 9): the packet
  correctly refuses to silently pick a budget number, and PI authorization
  is a separate, already-tracked gate (round-1 item 11), not a defect in
  `run.py`. `authorizations: []` / `execution_authorized: false` still
  correctly reflect "not yet authorized" — execution must still wait for
  the PI's verbatim `AUTHORIZATION_PROMPT.md` text regardless of this
  review's PASS. `pre_execute_review: {state: not_started, ...}` (line 43)
  is now stale (should be updated by the main thread to record this
  round's PASS); not a `run.py` defect, flagged for main-thread bookkeeping
  only.
- **Focused tests**: `py_compile workspace/r2_fer_shg_64/run.py` → OK.
  `PYTHONPATH=D:\Code\HD-QKD_Polar_Comparison-nbpolar python -m pytest -p
  no:cacheprovider comparison_bench/tests/test_nbpolar_scl_joint.py -q` →
  **6 passed**, 59.07s (same 1 benign `cache_dir` config warning as round
  1, no failures) — identical result to round 1's run.

---

## review_scratch evidence

`review_scratch/verify_taxonomy_r2.py` — imports run.py's actual
`_taxonomy_counts`/`_wilson` via `importlib.util` (module executed only up
to its top-level statements; `main()` never called), feeds an 11-block
synthetic set spanning every status branch (`ok`×4 taxonomy outcomes,
`STOPPED_FIDELITY_MISMATCH`, `resource_abort_wall_pre_scl`,
`resource_abort_wall_post_scl`×2 (exact / undetected — the F1 regression
cases), `resource_abort_wall_hard_terminate`,
`resource_abort_total_wall_budget_not_started`, `error:RuntimeError`). No
real data, no `.ttbin`, no decoder call. Terminal output:
`ALL CHECKS PASSED` (0 issues).

---

## Conclusion

F1 is fixed; no double-counting into `D`/`exact`/taxonomy `undetected`. The
`stop_undetected` safety-signal widening (change b) is correct and
consistent with its own `undetected_block_ids` listing. `fidelity_mismatch`/
`fidelity_compromised` are unaffected by (a), as required. No other change
was introduced beyond (a) and (b) plus non-functional comments. **PASS.**
Execution remains additionally gated on PI's verbatim authorization
(`AUTHORIZATION_PROMPT.md`) and resolution of `D_BUDGET_CONFLICT`
(`PENDING PI`), per STATUS.yaml and AGENTS.md §3/§10.3 — neither of which
is a `run.py` code defect.
