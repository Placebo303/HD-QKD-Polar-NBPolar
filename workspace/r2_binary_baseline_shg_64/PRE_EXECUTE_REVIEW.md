# PRE-EXECUTE REVIEW — r2-binary-baseline-shg-64

Reviewer: independent reviewer-go (AGENTS.md §3/§5.1/§5.6/§10.3). Scope: contract
`docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` +
`workspace/r2_binary_baseline_shg_64/{run.py,TASK_PACKET.md,prereg.md,STATUS.yaml,AUTHORIZATION_PROMPT.md}`.
No `--authorize` phase run; no `.ttbin` read; no git write. Only ran
`py_compile`, the AST %-format scan, `_selfcheck_involution.py`,
`_smoke_synthetic.py`, `_test_aggregation.py` (all read-only/synthetic).

## Verdict: **FAIL (revise-required)**

All findings below are mechanical/documentation-consistency fixes — no
redesign, no re-derivation of the scientific plan is needed. Re-review after
fixes should be fast.

## Blocking findings

**F1 — `AUTHORIZATION_PROMPT.md`'s copy-paste block still states the
SUPERSEDED `sc_margin` range.** Line 27: `[___,___] 步长 ___` defaulting to
"合同 §3 的 [0.00,0.30] step 0.01 提案", and the confirm-table (line 56)
repeats `[0.00, 0.30] step 0.01`. Contract §3.1 / `STATUS.yaml`
(`D_BIN_F_GRID_SEARCH_RANGE`) / `run.py:156` (`SC_MARGIN_CANDIDATES = (0.02,
0.05, 0.08, 0.12, 0.18, 0.25, 0.30)`) all agree the dense sweep was found
infeasible and replaced by this 7-point list. If pasted to the PI as-is, the
PI would be confirming a parameterization that is NOT what `run.py` will
run (`run.py` never reads this file — it is a human sign-off document only,
so the mismatch is invisible to the code path but real for authorization
validity). This is the same class of error AGENTS.md §3 names explicitly
("V55 reused a V54 template constant instead of checking the actual plan
content"). **Fix**: update the copy-paste block and confirm-table to the
7-point list before requesting PI sign-off.

**F2 — `prereg.md`'s P: section is stale in the same way.** Lines 33-36 state
`CALIB_N_FRAMES=4000` and "scanning `sc_margin` over [0.00,0.30] step 0.01" —
superseded by the same §3.1 finding (`run.py:148` has `CALIB_N_FRAMES=100`).
`run.py` does not read `prereg.md` either, so execution is unaffected, but a
preregistration document that contradicts what actually ran is an audit-trail
risk for a project this focused on no-post-hoc-tuning discipline (someone
re-reading `prereg.md` later could reasonably ask whether the grid was
changed after seeing results, even though the contract's own §3.1 already
discloses the revision with full justification). **Fix**: sync `prereg.md`'s
P: section to the frozen values, or add a dated addendum pointing to
contract §3.1 as superseding text.

**F3 — code does not actually enforce the "no pre-existing `part_*.json`"
STOP rule it claims to.** Contract §7 and `TASK_PACKET.md` S8 both state
readiness requires `results.json` AND any `part_*.json` to be absent, "checked
in-code at runtime." Reading `run.py::main` (lines 939-940): only
`RESULTS_PATH.exists()` is checked; there is no glob/check against
`part_*.json` before the block loop starts, and `_run_one_block_entry` opens
each part path with mode `"w"` unconditionally (silent overwrite). Concretely:
`--dry-run-one` itself writes `construction_frozen_G2.json` and
`part_G2_00.json` for real (session G2, `global_block_index=0`,
`frame_start=0`/`frame_end=127`, `stratum_official=A1_CAL_characterization`,
confirmed against `workspace/r2_fer_shg_64/part_G2_00.json`) — these files are
not deleted afterward. A subsequent full run silently re-decodes and
overwrites that same block/file (SC decode is deterministic, so in THIS
specific case the overwrite is content-equivalent — not a scientific-validity
bug), but the missing check means the code would just as silently clobber a
genuinely stale/different-provenance part file in a less benign scenario,
which is exactly what the contract's STOP rule was written to prevent.
**Fix**: add a `part_*.json` glob-emptiness check alongside the existing
`RESULTS_PATH` check (mirrors what §7/S8 already claim is done), and correct
S8's evidence-table wording.

## Non-blocking comment

**C1 — RSS budget constant mismatch (zero execution risk).** Contract §6 and
`AUTHORIZATION_PROMPT.md`'s confirm-table both say "RSS ≤ 4 GiB" (explicitly
"宽于 r2_fer_shg_64 的 2 GiB"), but `run.py:163` has
`BUDGET_RSS_GIB_PER_BLOCK = 2.0`. Neither r2_fer_shg_64's nor this packet's
`run.py` actually enforces an RSS check anywhere in code (no `psutil`, no
memory monitoring — grep confirms only the constant's definition exists, same
as the "PENDING-BUDGET" precedent already flagged non-blocking in the
predecessor packet). Since it's advisory-only in both packets, this has no
functional effect regardless of which number is "correct," and
`r2_fer_shg_64`'s own measured peak RSS was 0.52–0.58 GiB — far below either
number. Recommend syncing `run.py`'s constant to `4.0` for documentation
consistency, but not blocking.

**C2 — TASK_PACKET.md §3's construction-search time estimate is off by ~2x.**
Contract §3.1 computes ~75 min PER SESSION (7×10×8×100×80.8ms), but
`TASK_PACKET.md`'s D_BIN_SC_DECODER_COMPLEXITY paragraph characterizes 75 min
as "both sessions combined order of magnitude." Correct combined estimate:
~150 min construction (2 sessions) + ~28 min decode (64 blocks) ≈ 178 min ≈
3.0 h, which still clears the 4 h total-wall budget with margin — the
PASS-worthy conclusion ("budget is generously conservative") is unaffected,
just the arithmetic write-up should be corrected.

**C3 — `_smoke_synthetic.py`'s own diagnostic output shows `f_book_sc` is NOT
monotone in `sc_margin`** (margin=0.02 → f=0.6951 vs margin=0.05 → f=0.6777,
i.e. smaller margin gave higher f — inverted from the naive expectation).
This is very plausibly Monte-Carlo noise from `CALIB_N_FRAMES=100` at a
threshold of `FER_THRESH=0.05` (relative sampling noise ~2%, non-trivial near
that threshold), not a logic bug: `freeze_binary_construction` sorts usable
points by their actual computed `f_book_sc` (not by margin) before picking
low/mid/high, so correctness does not depend on monotonicity. Flagging only
so the eventual `RESULT_SUMMARY.md` doesn't over-interpret the grid points as
a smooth margin-vs-f curve.

## Checks that PASSED / were verified sound (no rework needed)

- **Baseline protection**: `git status --porcelain` on `src/`, `experiments/`,
  `tools/`, `comparison_bench/src/`, and `workspace/r2_fer_shg_64/` is clean
  (no modifications); no writes under `results/` or
  `comparison_bench/outputs_comparison/`. Only new file this pass touches is
  this review doc and its scratch dir.
- **Same-data guarantee (item 2)**: `run.py` imports
  `workspace/r2_fer_shg_64/run.py` by file path and calls
  `build_session_blocks`/`_reproduce_session_context` unchanged (no
  reimplementation) — this is a code-identity guarantee, not a runtime hash
  cross-check, and is reasonable given there is no independent-implementation
  divergence risk. Residual gap (correctly flagged in TASK_PACKET §7 already):
  `workspace/r2_fer_shg_64/part_*.json` never stored a raw-symbol hash of its
  own, so this packet's per-block `block_hash` (SHA-256) cannot be
  cross-verified against a stored NB-side value — it is audit-only, not a
  verification gate. Acceptable as a disclosed, non-blocking residual
  limitation (R1/§9 of the contract already covers this).
- **CAL32-only construction (item 3)**: `main()` builds `cal_a`/`cal_b`
  strictly from `mod.g2_cal_ids(nb_mod.ARM)` (lines 955-958) before any block
  in `blocks_meta` is touched; `freeze_binary_construction` never receives
  EVAL/HELDOUT/A1_CAL data. Confirmed by direct code read.
- **Binary mapping/config (item 4)**: MSB-first bit-planes (`layer_bit`,
  `shift = bits-1-layer_idx`), N=4096/layer, 8 codewords/layer, 80/block,
  PW order via `_polar_weight_order(4096)[::-1]` — all match the contract.
  `CALIB_N_FRAMES=100` and the 7-point `sc_margin` list match §3.1's revision
  (code, not the stale docs above). SC-primary/CA-SCL-secondary rationale is
  sound and fully disclosed: CA-SCL's internal CRC path-selection genuinely
  requires overwriting 16 real u-domain bits/codeword
  (`scl_descriptive_codeword`), which SC's single-path decode does not need —
  accepting this asymmetry rather than inventing an unreviewed CRC-preserving
  protocol is the right call for this task's scope.
- **f accounting (item 5)**: `h_total_bits` is read straight from the NB
  packet's own `ctx_nb["f_book_with_crc"]`/`h_total_bits` (never refit); SC
  numerator = frozen bits + tag; SCL numerator additionally adds 16
  bits/codeword CRC tax; both fields kept separate
  (`kdb_sc`/`kdb_scl`, `f_book_sc`/`f_book_scl`) and never conflated.
- **Taxonomy/success rule (item 6)**: `_binary_taxonomy_counts` mirrors
  `workspace/r2_fer_shg_64/run.py::_taxonomy_counts` exactly (ok-only-into-`D`,
  isolated `undetected`/`resource_abort`/`error`). Verified: (a) by direct
  side-by-side code comparison; (b) `_test_aggregation.py` PASS against
  hand-built fake records covering every status branch (including
  block-level `error` with an empty grid). Grid-point-level `status` field
  (not block-level) is what both the per-margin taxonomy and the top-level
  `stop_undetected` scan key off, which correctly avoids missing an
  `undetected` signal on a block that partially failed after some grid points
  already completed — verified by code read, not just assumed.
- **Table A/B semantics (item 7)**: confirmed against the ACTUAL 64 files in
  `workspace/r2_fer_shg_64/`: `sc_descriptive` populated in exactly 36 files
  (`never_decoded`(28)+`heldout_model_selection`(8)), `fidelity` populated in
  exactly 28 (`previously_decoded_eval`), the other field `null` in each case
  — and both trace to the SAME underlying `run_g2_block` call
  (`_sc_call`/`_fidelity_check` in `workspace/r2_fer_shg_64/run.py`), so
  `load_nb_parts()`'s fallback logic (`sc_descriptive` else
  `fidelity.actual`) reads the same `outcome` semantics either way — not
  `fidelity.match` (a different, historical-consistency field). Table B1/B2
  decoder-strength-parity warnings (§4.1) are present and correctly worded in
  both the contract and `build_cross_comparison`'s
  `decoder_strength_parity_note`.
- **Judgment/reporting rules (item 8)**: `aggregate_results`/
  `build_cross_comparison` never emit a win/lose or pass/fail string
  (grep-confirmed; `_test_aggregation.py` E5 asserts this against fake data);
  §5's scope-limitation language is present in the contract.
- **Budget/STOP mechanics (item 9)**: wall-per-block check is real
  (`elapsed_so_far > BUDGET_WALL_S_PER_BLOCK` at line 518, records
  `resource_abort_wall_mid_grid` per remaining grid point, does not drop
  silently); one-shot/`reruns=0` is a process-discipline item, not
  code-enforced (consistent with the predecessor packet's own precedent).
  Dry-run traceability: see F3 above (real answer to "which block, does it
  leave a trace, is it redecoded" is block G2 idx 0 / yes it leaves
  `construction_frozen_G2.json`+`part_G2_00.json` / yes the full run redecodes
  and overwrites it, harmlessly given determinism).
- **Static checks (item 10)**: `py_compile` → pass; AST %-format scan → 0
  found; `_selfcheck_involution.py` → self-inverse CONFIRMED (n_log∈{2,3,4,6},
  30 trials each, 0 failures); `_smoke_synthetic.py` → PASS, wall 5.2s (this
  run) vs 5.6s recorded in STATUS.yaml, consistent; `_test_aggregation.py` →
  PASS, all fake-data branches hand-verified correct.

## Summary

Scientific design, data-fairness discipline, taxonomy/accounting logic, and
disclosure of decoder-strength asymmetries are all sound and match the
contract. The blocking items are all template/documentation drift (stale
numbers in the PI-facing authorization text and the preregistration doc) plus
one missing defensive check (part-file pre-existence) that the contract
already promised existed. None require revisiting the scientific plan. Fix
F1–F3, leave a one-line note on C1, and this packet should re-review quickly
to PASS.
