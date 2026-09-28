# PRE-EXECUTE REVIEW — m2-scl-check-g2g3-success

Reviewer: independent reviewer-go subagent (AGENTS.md §3/§10.3/§10.4
delta-successor fast path). Scope: this packet only; predecessor
`workspace/m2_scl_rescue_g2g3/` (Pre-EXECUTE PASS_WITH_COMMENTS, Pre-RESULT
PASS, commit 326594ca) inherited unchanged except the stated delta. No
files modified outside this directory; run.py/decoder not executed; raw
`.ttbin` not read; no git write performed by this review.

**VERDICT: PASS**

## Findings

1. **run.py diff scope (`git diff --no-index` predecessor vs successor,
   312 lines)**: matches TASK_PACKET.md §3's claimed change classes
   exactly — (a) `TARGETS` constant (9 verify_failed pairs -> 19 exact
   pairs), (b) prose/docstrings (rescue->preservation-check framing,
   9->19 counts, output-dir path strings), (c) summary field rename incl.
   the D_NEW1 redefinition (`n_broken` = `rescue.verify_failed`
   specifically, not "not exact"), (d) `authorization.verbatim`/docstring
   PI-quote update (D_NEW2). Independently confirmed unchanged: module
   loading (`_load_mod`, `_load_scl_joint`, singleton chain/module load in
   `main()`), all frozen params (`ARM`, `LIST_WIDTH_L`, `TOP_M`,
   `CRC_BITS_EXTRA`, K1=319/K2=6492/N=32768, construction-digest
   verification call, `tag_master`/`eval_seed` per session), the
   `accepted = crc_pass and tag_pass` formula and all of `_rescue_block`'s
   arithmetic, `_fidelity_check`'s comparison logic, budget/backstop
   constants (`MAX_PARALLEL=8`, `BUDGET_WALL_S_PER_BLOCK=1200.0`,
   `BUDGET_RSS_GIB_PER_BLOCK=2.0`, `HARD_TERMINATE_MARGIN_S=120.0`), and
   write-path logic. Only additional diff noise is em-dash->`--`
   normalization inside rewritten docstring paragraphs (cosmetic). No
   undisclosed change found.
2. **Target-list independent re-derivation**: filtered both frozen
   `per_block_outcomes.jsonl` files myself for
   `arm=="B_M2_32f_candidate" and outcome=="exact"` (14 B-arm rows each):
   G2 -> `[0,2,3,4,6,7,8,9,10,11,13]` (11), G3 -> `[3,5,6,7,8,9,12,13]`
   (8). Byte-for-byte identical to `run.py::TARGETS` and to
   TASK_PACKET.md §2's/prereg.md's stated 19-block list. No mismatch.
3. **Null-fidelity fidelity check**: `_fidelity_check` uses
   `expected.get(k) != actual.get(k)` verbatim (unchanged from
   predecessor) over `_FIDELITY_FIELDS` incl.
   `first_error_coordinate`/`first_error_layer`. Confirmed Python
   semantics: `None != None` -> `False` (treated as match), so a
   correctly-reproduced exact-outcome block (both sides `null`) is not
   misflagged as a mismatch and is not silently skipped — the field is
   still compared, it just evaluates equal. Logic is identical to the
   predecessor's, which already covered 6/9 verify_failed blocks with
   non-null error fields; this packet is the first to exercise the
   both-sides-null path but the same generic comparison handles it
   correctly.
4. **Three-way partition / D3 gating**: `exact = accepted and
   label_exact`; `undetected = accepted and not label_exact`;
   `verify_failed = not accepted` — mutually exclusive and exhaustive by
   construction (unchanged code). `n_broken` (this packet) now counts
   `verify_failed` specifically, eliminating the predecessor's
   `n_still_failed` double-count of `undetected` inside "not exact";
   D_NEW1 is a strict improvement and is what the task instruction
   literally specified. `fidelity_compromised` gating (STOP per block on
   any mismatch, withhold aggregate tally, keep per-block detail) is
   byte-identical to the predecessor's `main()` logic.
5. **Write-scope**: `git status`/`git diff` confirm zero changes under
   `comparison_bench/src/comparison_bench/formal_ir/`,
   `scripts/m2_prior_validation.py`, `src/`, `experiments/`, `tools/`, and
   under the predecessor's own directory
   (`workspace/m2_scl_rescue_g2g3/`). `workspace/m2_scl_check_g2g3_success/`
   contains only the five prep artifacts (`run.py`, `TASK_PACKET.md`,
   `prereg.md`, `STATUS.yaml`, `AUTHORIZATION_PROMPT.md`);
   `results.json` and all `part_*.json` are confirmed absent (one-shot
   readiness intact). No write under `results/` or
   `comparison_bench/outputs_comparison/`.
6. **Branch/cleanliness**: current branch `codex/nbpolar-phase0` matches
   `STATUS.yaml`'s recorded branch. All named frozen files
   (`scl_joint.py`, `two_layer.py`, `scripts/m2_prior_validation.py`, and
   the rest of `formal_ir/`) show empty `git diff`/`git status`.
7. **Authorization**: PI verbatim "授权，19 块也跑 SCL L=16" (2026-09-28)
   recorded identically in `AUTHORIZATION_PROMPT.md`, `STATUS.yaml`, and
   `run.py`'s `results["authorization"]`. `TARGETS` is a hardcoded module
   constant (19 pairs, matching Finding 2) — never re-derived at runtime,
   so authorization scope and actual executed scope cannot drift apart.
8. **Focused test**:
   `D:\software\Miniforge3\python -m pytest -p no:cacheprovider comparison_bench/tests/test_nbpolar_scl_joint.py -q`
   (PYTHONPATH = repo root) -> **6 passed, 1 warning (unrelated
   `cache_dir` config-option warning), 47.7s**. No failures.

## Comments (do not block PASS)

- D_NEW1/D_NEW2 are main-thread decision points per TASK_PACKET.md §3; both
  are already recorded as `ACCEPTED` in `STATUS.yaml`'s
  `main_thread_rulings_successor_2026_09_28` block, so this reviewer treats
  them as already adjudicated rather than open. Recommend the main thread
  confirm that recording is intentional (it reads as self-adjudicated in the
  packet, but the task instruction states the main thread already accepted
  both).
- Timing estimate (~35 min wall) is unverified by this review (no execution
  performed) but is consistent with the predecessor's empirical precedent
  cited in TASK_PACKET.md §6; no action needed pre-execution.

## Scope not re-litigated (inherited from predecessor per delta-successor rule)

Decoder correctness of `scl_joint_decode` itself, the CAL-fit/P16
construction-digest verification mechanism, budget/backstop
implementation correctness, and the fidelity-check re-derivation
mechanism (`run_g2_block` reuse) were reviewed at the predecessor's
Pre-EXECUTE (PASS_WITH_COMMENTS) and are not re-reviewed here since this
packet's diff does not touch that code (Finding 1).
