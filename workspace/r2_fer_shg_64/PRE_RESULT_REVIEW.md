# Pre-RESULT Review — r2-fer-shg-64

Reviewer: independent reviewer-go subagent (AGENTS.md §3/§10.3/§5.8).
Scope: `workspace/r2_fer_shg_64/{results.json, part_*.json (64), STATUS.yaml,
EXECUTION_TRANSCRIPT.md, execution_*.log, run.py, prereg.md,
PRE_EXECUTE_REVIEW.md, PRE_EXECUTE_REVIEW_R2.md}`. No file outside this
directory was modified; no decoder rerun, no raw `.ttbin` read, no git write.
All recomputation done independently in
`review_scratch/independent_check.py` (pure stdlib, reads only the 64
`part_*.json` files, never imports `run.py`).

## Verdict: **PASS**

No discrepancy found between the independently recomputed taxonomy/CI/leakage
figures and the artifacts. All frozen-contract checks pass. Adjudication of
`FER_MEASURED_AT_CONTRACT` remains a main-thread act (not rendered here).

---

## Findings

**F1 — Taxonomy recomputation matches exactly (pooled / by_task / by_official).**
Independently recomputed from the 64 `part_*.json` files, own Wilson(z=1.96)
formula: pooled `n=64, D=64, exact=62, verify_failed=2, decode_failed=0,
undetected=0, resource_abort=0, fidelity_mismatch=0`, `p̂=0.03125`, CI
`[0.008612, 0.106975]` — matches operator report and `results.json` bit-for-bit
(cross-check loop: zero diffs on every field, every group). `stratum_task`
pooled = 28/8/28 (never_decoded/heldout_model_selection/previously_decoded_eval);
`stratum_official` pooled = 16/20/28 (A1_CAL/HELDOUT/EVAL) — both match the
frozen (14,4,14)×2 / (8,10,14)×2 layout. Per-session: G2 D=32 exact=31
verify_failed=1; G3 D=32 exact=31 verify_failed=1.

**F2 — Threshold rule (input only, not final adjudication).** D=64≥56;
undetected=0 (no STOP trigger). Under the PI-authorized rule
(STATUS.yaml `pi_authorization_2026_09_28.verbatim`), this input set is
consistent with `FER_MEASURED_AT_CONTRACT` — main thread still renders the
actual verdict.

**F3 — undetected isolation verified, zero formula violations.** Checked all
64 blocks: `accepted == crc_pass AND tag_pass AND NOT decode_failed`,
`exact == accepted AND label_exact`, `undetected == accepted AND NOT
label_exact`, `verify_failed == NOT accepted AND NOT decode_failed` — 0
violations. No block has both `undetected=True` and `exact=True` (never
merged). `undetected` in the taxonomy tables is gated on `status=="ok"`; a
separate all-block scan (matching `stop_undetected`'s scope) also returns 0 —
both scans agree here since no `resource_abort` occurred, so the F1
round-1→round-2 fix (PRE_EXECUTE_REVIEW_R2.md) had no observable effect on
this run's numbers, consistent with 0 aborts.

**F4 — Fidelity: 28/28 EVAL blocks match, 100% cross-consistent with prior
descriptive results.** All 28 EVAL blocks' `fidelity.match=true`, zero
mismatches on the 5 fields (null==null treated as equal). Cross-checked
against the 28 predecessor part files (`m2_scl_rescue_g2g3/` 9 files +
`m2_scl_check_g2g3_success/` 19 files, keyed by `eval_original_index`):
28/28 consistent on `exact/verify_failed/undetected/label_exact/crc_pass/
tag_pass`. The single previously-known failure (G2 EVAL block 5,
`eval_original_index=5`) reproduces exactly as `part_G2_23.json`
(`verify_failed=True`, same `first_error_coordinate=978`/`first_error_layer=
L2`/`hard_l2_exact=False`/`l1_exact=True`). `part_G3_38.json` (the other
verify_failed block) is a `never_decoded` (A1_CAL) block with no prior SCL
record — a new observation, not a fidelity check subject; correctly has
`fidelity=None`. `fidelity_compromised=False` confirmed (0 mismatches).

**F5 — Block framing / stratum labels clean.** All 64 blocks are exactly
128 frames; none overlaps CAL32 (1024–1055); `global_block_index` is exactly
`{0..63}` with no duplicates; per-session stratum split 8/10/14 (official)
and 14/4/14 (task) both confirmed for G2 and G3 independently.

**F6 — Leakage decomposition recomputed, matches contract.**
`kdb_no_crc = 5*(319+6492)+64 = 34119`, `kdb_with_crc = 34135` (both sessions,
fixed, block-outcome-independent by construction — computed once per
session before any block decode). Recomputing `f_book = kdb/(H_total_bits*
32768)` from each session's own `H_total_bits` read out of `results.json`:
G2 `H_total=0.816814` → `f_no_crc=1.274745`, `f_with_crc=1.275343`; G3
`H_total=0.821478` → `f_no_crc=1.267507`, `f_with_crc=1.268101`. Matches the
expected ranges (G2 ≈1.27474–1.27534, G3 ≈1.26751–1.26810) and matches
`results.json`'s own reported values exactly.

**F7 — Session-level exact counts.** G2: 31/32 exact (1 verify_failed);
G3: 31/32 exact (1 verify_failed). (Not 32/32 — the task's phrasing
"G2 exact/32, G3 exact/32" is read as "report exact-out-of-32 per session,"
which is what is reported here.)

**F8 — Execution consistency.** `reruns=0`; all 64 `part_*.json` have
`status=="ok"` (0 `resource_abort`, 0 `error`, 0 `STOPPED_FIDELITY_MISMATCH`);
`wall_total_s` range [534.2s, 574.4s] ≤ 1200s/block; `rss_gib_peak_advisory`
range [0.5205, 0.5767] GiB ≤ 2GiB/block; total `wall_s_total`=4493.4s ≤ 10800s
(3h). `EXECUTION_TRANSCRIPT.md`'s command is byte-identical to `prereg.md`'s
§C line (venv, `PYTHONPATH`, script path all match). Write scope: `git status`
shows only the pre-existing, unrelated modified files
(`comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`,
`docs/nbpolar/DATA_LEDGER.md` — both already modified before this session per
the conversation's initial git-status snapshot, unrelated to this execution)
plus the new untracked `workspace/r2_fer_shg_64/` directory; no other path
touched. mtimes confirm no disturbance of read-only inputs: both predecessor
part-file directories and both `per_block_outcomes.jsonl` files have mtimes
far older (`1790017505`–`1790576618`) than `run.py`/`results.json`/part files
(`1790597325`+), i.e. untouched by this run.

**F9 — Report-completeness inputs present, no verdict string.** `results.json`
carries both `taxonomy_by_stratum_task` and `taxonomy_by_stratum_official`
alongside `taxonomy_pooled` (P-1's "pooled table must accompany stratified
table" requirement is satisfiable from this one file); `undetected`/
`resource_abort`/`fidelity_mismatch` are explicit `0` fields in every group,
not omitted; `selection_freedom_exercised` dict present (A1_CAL/HELDOUT/EVAL
roles stated); `f_book_*_computed` sits beside `h_total_bits` per session (f
and H reported together). Grep for `FER_MEASURED_AT_CONTRACT`/`verdict`/
`PASS` in `results.json` finds only descriptive text disclaiming that no such
judgment is computed — no verdict field or boolean anywhere. Applicable-scope
statement (D-ACQ-05: limited to the two 2026-01-13 SHG acquisitions' own
conditions) lives in the contract docs
(`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md` §5 D-ACQ-05 row), not inside
`results.json` itself — **flag for the main thread**: when drafting the
actual `OPERATOR_RETURN.md`/`RESULT_SUMMARY.md`, restate that scope sentence,
the caveats (SCL-arm only; A1_CAL/HELDOUT blocks are first-time SCL
observations with no prior comparable record; PENDING-BUDGET numbers were
PI-confirmed as this execution's formal budget, not a re-adjudication of
D-ACQ-06 in general), and the one permitted conclusion sentence (config +
64 blocks + p̂ + CI + scope + stratification + `undetected=0` +
`f_book≈1.268–1.275` with CRC) — this is a drafting reminder, not an artifact
defect.

---

## Conclusion

All nine checklist items verified independently against the raw `part_*.json`
files with a self-written script; zero discrepancies against `results.json`,
zero formula violations, zero fidelity mismatches, 100% cross-consistency
with the two predecessor descriptive-result directories on the 28 EVAL
blocks (including exact reproduction of the one previously-known failure at
the same original index). Frozen thresholds (D≥56, undetected=0), budget
caps, one-shot/no-rerun discipline, and write-scope containment all hold.
**PASS.** Final `FER_MEASURED_AT_CONTRACT` adjudication and drafting of the
result summary (with the F9 scope/caveat reminders folded in) remain
main-thread acts.
