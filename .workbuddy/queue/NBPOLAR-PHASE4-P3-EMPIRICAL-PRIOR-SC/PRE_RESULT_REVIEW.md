# Pre-RESULT review — NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC (Stage B)

- Reviewer: fresh independent reviewer-go instance (did not write the code, the
  freeze, or run the Stage B command).
- Date: 2026-09-13 (review written 01:21 +0800).
- Scope reviewed: frozen contract `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/P3_STAGEB_FREEZE.md`
  (v2 + Rev 2a), `TASK_PACKET.md`, the five artifacts under
  `empirical_prior_sc_diagnostic/`, and the round's Pre-RESULT requirements.
- Verdict: **PASS_WITH_COMMENTS** — no blocking issues; all scientific gates,
  counts, isolation and wording checks pass. Three naming-level comments only.

## Independence statement

- I did not write any reviewed file and did not participate in the run.
- The accepted sibling artifact content was **not opened**: only `stat`/directory
  metadata was read. The only JSON/MD content I opened is the five output files
  under `empirical_prior_sc_diagnostic/`.
- The Stage B command was **not rerun**; attempt 1/1 stands consumed
  (`frozen_plan.json` → `attempt_accounting.consumed_at_write = 1`), and no
  second output root exists.
- All numbers below were independently recomputed from the five artifacts with
  a script, not copied from the summary booleans.

## Blocking issues

None.

## Non-blocking suggestions

1. **B2 per-case `n_nan` alias.** B3 cases carry both `n_nonfinite` and `n_nan`;
   B2 cases carry only `n_nonfinite`. This matches freeze §4 verbatim (B2 row
   mandates "nonfinite", B3 row mandates "n_nan"), so no frozen semantics are
   missing — the NaN/nonfinite count is present and 0 for both. If the round
   intended a literal `n_nan` key on B2 too, treat it as a schema note for the
   main thread, not a defect; no count or gate is affected.
2. **`attempt_accounting` key name.** The block records `consumed_at_write: 1`
   plus `consumed_on: "first artifact content open"`; there is no key literally
   named `consumed`. Value and semantics match the requirement.
3. **Bounded-note wording.** `report.md`'s closing note lists FER, reconciliation,
   leakage, key rate and construction/K (not the word "performance" that
   `frozen_plan.json`'s `no_claim_note` includes). The B4 timing medians are the
   frozen required resource profile, not a performance claim, so no correction
   is required; adding "performance" to the report note would make the two
   disclaimers identical.
4. **Informational — concurrent sibling activity.** The sibling checkout had
   unrelated D7-H writes at 01:08:36–01:08:54 (before this run's start,
   ≈01:08:59.9) and at 01:15+ (after). The frozen artifact root
   `.../v72p2d5_model_f_input/20260907_r1/` itself is untouched (Sep 7 mtimes).
   None of this activity belongs to this packet's run.

## Numbered checklist (raw recomputed values)

### 1. Output root: exactly 5 frozen files — PASS

`ls -A .../empirical_prior_sc_diagnostic | wc -l` → `5` (no extras, no hidden).

| file | size (bytes) | mtime |
|---|---|---|
| frozen_plan.json | 3560 | 2026-09-13 01:09:17.527 |
| oracle_records.json | 1612 | 2026-09-13 01:09:17.535 |
| stress_and_profile.json | 2435 | 2026-09-13 01:09:17.542 |
| diagnostic_summary.json | 21529 | 2026-09-13 01:09:17.549 |
| report.md | 3331 | 2026-09-13 01:09:17.556 |

Payload scan across all JSON keys/sections: longest list = 14 elements (the
banned-seed range), longest string = 187 chars (artifact path / derivation).
No count tables, symbol vectors, private rows, or per-block posterior arrays.
Strict JSON parse with `parse_constant` rejection: OK (no NaN/Infinity).
Key-name hits `oracle_rows` (integer count of oracle comparisons) and
`counts_ab_shape` (shape `[1024,1024]` only, not the matrix) are benign.

### 2. frozen_plan.json — PASS

- seed = 2026091316; `unit_not_used` = 2026091314 and `train_not_used` =
  2026091315 both present and marked not used; banned predecessor range
  recorded as 2026091200..2026091213 (14 values).
- Artifact identity: paths match freeze §2; `npz_bytes` 208467, `summary_bytes`
  752; loader `prior_artifact.load_prior_artifact`; `lambda_star` =
  137.3823795883264; shapes counts_ab `[1024,1024]`, p_b `[1024]`, derived_p1
  `[32,1024]`.
- Derivation string exactly: `prior.smooth_joint_to_conditional(counts_ab,
  LAMBDA_STAR) -> prior.derive_p1; p_b = artifact.p_b; probs ->
  prior.probs_to_symbol_metric (q=32)`.
- `attempt_accounting`: `attempts_allowed` 1, `consumed_at_write` 1,
  `consumed_on` "first artifact content open".
- `invocation` matches freeze §7 exactly: mode `stageb`; npz/summary paths
  byte-identical to the command; out `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic`.
  Source argparse (`empirical_diagnostic.py:1243–1251`) has exactly the frozen
  flag set; no extra flags.
- Thresholds: max_prob_err 1e-12, max_log_err 1e-9, support_mismatches 0,
  numeric_failures 0, truth_leak_violations 0.
- Budget: 3600.0 s / 120.0 s / rss_bytes_max 2147483648.
- `out_files` equals the freeze §6 order (frozen_plan, oracle_records,
  stress_and_profile, diagnostic_summary, report).

### 3. Recomputed counts and thresholds (no rerun) — PASS

**B1** (oracle_records.json cross-checked equal to diagnostic_summary.json):

| case | max_prob_err (≤1e-12) | max_log_err (≤1e-9) | support | numeric | decode_exc | oracle_exc | leak | executed |
|---|---|---|---|---|---|---|---|---|
| B1_N2 | 1.1102230246251565e-15 | 2.220446049250313e-15 | 0 | 0 | 0 | 0 | 0 | 64/64 |
| B1_N4 | 7.771561172376096e-16 | 5.329070518200751e-15 | 0 | 0 | 0 | 0 | 0 | 64/64 |

Per-case closure: N2 8+0+56+0+0 = 64; N4 1+0+63+0+0 = 64.

**B2** (10 cases, all `n_executed == n_blocks_planned == 16`, each closure
`exact+impossible+other+nonfinite+resource_abort == 16`): totals planned 160 =
executed 160; exact 31 (=15+16), impossible 0, other 129 (=1+64+64), nonfinite
0, resource_abort 0. Re-derived from cases: 160/31/129 — equal to totals.

**B3** (5 cases, all `n_executed == n_blocks_planned == 8`, closure = 8):
totals planned 40 = executed 40; exact 8, impossible 0, other 32, nonfinite 0,
`n_nan` 0, `n_initial_error` 40 (=8×5), resource_abort 0. Re-derived — equal.

**Grand invariants:** total executed (B1+B2+B3) = 328; total exact = 48; total
non-exact = 280. B5 attribution totals sum to exactly 280 (SC_decision 119 =
56+63; expected_under_disclosure 161 = 1+16×4+16×4+8×4; all other categories
0). All category counts ≥ 0; the 7 categories are distinct/disjoint labels
(each per-case closure `sum(attribution) == n_other` held for all 17 cases).
`b5.b4_scored_blocks = 0` (B4 timing-only). `impossible`, `nonfinite`,
`resource_abort` are separate keys propagated per case and in totals, never
folded into exact (arithmetic closure proves it); resource_abort blocks 0 and
B4 profiles 0 are reported separately and are not an attribution category.

### 4. Truth isolation — PASS

`truth_leak_violations` = 0 at top level and for every B1/B2/B3 case.
Artifact usage is recorded as the accepted loader/derivation in
`frozen_plan.json` (loader, derivation string, shapes) and corroborated by
`run_stageb_diagnostic` (`empirical_diagnostic.py:1212–1233`): single
`load_prior_artifact`, then `smooth_joint_to_conditional(artifact.counts_ab,
LAMBDA_STAR)` → `derive_p1`, with `probs_to_symbol_metric` only; counts are
consumed to derive the table, not copied. Sibling metadata (`stat`, no content
open): npz **208467** bytes mtime 2026-09-07 02:07:07; summary **752** bytes
same mtime; directory holds only these two files. Bounded window searches
(01:07–01:12 on `workspace/` maxdepth 3; 01:08:30–01:10:30 on the sibling's
comparison_bench/docs/openspec/scripts/.workbuddy) found no writes to the
artifact root and no writes attributable to this run (see Non-blocking #4).

### 5. B4 resource profile — PASS

| N | reps measured (metric/decode) | complete | metric shape | decision shape | disclosed_value_source | decode_status | peak RSS GiB (<2) |
|---|---|---|---|---|---|---|---|
| 64 | 5/5 | true | [64,32] | [64,32] | true_U | ok | 0.23288726806640625 |
| 256 | 5/5 | true | [256,32] | [256,32] | true_U | ok | 0.23288726806640625 |
| 1024 | 5/5 | true | [1024,32] | [1024,32] | true_U | ok | 0.23288726806640625 |

Batch shapes `[4,N,32]`, `resource_abort` false. Recorded medians (s): metric
3.799899423029274e-05 / 4.309399810153991e-05 / 1.1792199802584946e-04;
decode 7.757172992569394e-03 / 3.448710800148547e-02 / 1.6753002499171998e-01.
`stress_and_profile.json` B4 equals the summary B4 block exactly.

### 6. Hard gates (independently recomputed) — PASS

`hard_gates` contains exactly 6 keys, all true; `hard_gates_pass` true;
`candidate_conclusion` "EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE" (label only).
Recomputed from underlying counts/thresholds — every recomputation agrees with
the summary booleans:

| gate | recomputation basis | recomputed |
|---|---|---|
| b1_all_gates | B1 five thresholds + zero decode/oracle exceptions, all cases | true |
| b2_b3_zero_nonfinite | B2/B3 per-case nonfinite 0, `nonfinite_total` 0 | true |
| b2_b3_zero_unattributed | B5 `unattributed` 0 (per case and totals) | true |
| b2_b3_coverage_complete | B2 160/160, B3 40/40 executed | true |
| b4_complete | 3 profiles complete, ≥5 measured per leg | true |
| zero_truth_leak | top-level and per-case sentinel 0 | true |

### 7. Bounded wording — PASS

Read `report.md` and every prose string in `diagnostic_summary.json` in full.
No FER/reconciliation/leakage/key-rate/performance/protocol or construction/K
success claim. `report.md` ends with "Candidate label only: acceptance is
owned by the main thread and an independent Pre-RESULT review. This is not
real-data FER, reconciliation, leakage, key rate or construction/K evidence."
`diagnostic_summary.json` `candidate_conclusion_note` and
`frozen_plan.json` `no_claim_note` carry the same bounded semantics. B3 exact
counts (8/40) appear as descriptive counts only; no B3 exact threshold is
stated anywhere (freeze semantics "zero crash/nonfinite/truth-leak only"
records no exact-count gate). See Non-blocking #3 for one optional wording
uniformity tweak.

### 8. Scope / attempt / no rerun — PASS

- `git status --porcelain`: the only entries are the declared packet paths
  (7 modified: EXPLORATION_NOTES.md, empirical_channel.py,
  empirical_diagnostic.py, empirical_oracle.py, test_nbpolar_empirical_sc.py,
  mvp P3_STAGEB_FREEZE.md banner, phase4-p0 tasks.md; untracked: queue
  P3_STAGEB_FREEZE.md, PRE_EXECUTE_REVIEW.md, PRE_EXECUTE_REVIEW_R1.md,
  phase4-p0 specs/nbpolar-phase4-p3/spec.md) plus the declared new output
  root. No staged changes.
- `results/` does not exist in this checkout (nothing written);
  `comparison_bench/outputs_comparison/` dir mtime 2026-09-12 03:38:37 with
  only Sep-12 entries — untouched.
- Sibling artifact root untouched (check 4). Unrelated concurrent D7-H
  sibling writes at 01:08:36–01:08:54 predate this run's start (≈01:08:59.9,
  = last output mtime 01:09:17.556 minus wall 17.645 s) and are not this run's.
- HEAD unchanged: `ab173f2a` (reflog contains only the clone entry, 4 refs
  total, newest branch creatordate 2026-09-12 03:36:31; no commit/push).
- Single attempt: exactly one output root (only
  `empirical_prior_sc_diagnostic/`, no sibling roots); all five files written
  in a 29 ms window at end of run; `attempt_accounting.consumed_at_write = 1`.
  No attempt counter/ledger file exists.
- Implementation files predate the run (latest declared doc: R1 review
  01:08:07; sources 00:58:21) — no post-run edits.

### 9. Plan-specified cross-checks — PASS

- Seed separation: diagnostic 2026091316 distinct from unit 2026091314 /
  TRAIN 2026091315 (both marked not used) and outside 2026091200..1213.
- Disclosure per mask: B2 N16 M1 15 (=N-1), M2/M3/M4/M5 8 (=N/2); B2 N64 M1
  63, others 32; B3 N256 M1 255, others 128; B4 M5 32/128/512. All exact.
- Per-case breakdown fields: B3 `n_initial_error` present per case and in
  totals (8 each, 40 total); `n_nan` present on B3 per case and totals; B2
  presence of the nonfinite count is via `n_nonfinite` (freeze §4 B2 wording)
  — see Non-blocking #1.

## Bounded-wording corrections required

None. (Optional only: add "performance" to the `report.md` closing note for
uniformity with `frozen_plan.json`.)

## Evidence commands

- `ls -A`/`stat -c '%s %y %n'` on output root and sibling artifact.
- Strict-JSON parse + full invariant recomputation script
  `/tmp/opencode/p3_prereview_recompute.py` (all values above).
- `git status --porcelain`, `git reflog --all`, `git for-each-ref`,
  `git branch -vv`, `git diff --stat`, `git diff --cached --stat`.
- Bounded `find -newermt` window checks on `results/`,
  `comparison_bench/outputs_comparison/`, the sibling artifact root and the
  sibling checkout.
- Read-only source corroboration: `empirical_diagnostic.py:1195–1274`.

## Verdict

**PASS_WITH_COMMENTS** — solidification is not blocked; the artifact set is
scientifically consistent with the frozen contract and bounded wording is
respected. Acceptance remains owned by the main thread plus this independent
review.
