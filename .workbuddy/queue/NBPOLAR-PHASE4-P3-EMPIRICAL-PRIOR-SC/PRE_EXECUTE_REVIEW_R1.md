# Independent Pre-EXECUTE re-review R1 — NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC

Reviewer: fresh independent Pre-EXECUTE re-reviewer (read-only; did not write the code,
the repair, or the R0 review).
Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e`
(2026-09-12 03:36 +0800, unchanged from R0), all P3 work uncommitted.
Date: 2026-09-13. Scope: verify the R0 NEEDS_CHANGES repair is docs/comments only and the
frozen Stage B plan is internally consistent and safe to execute once.

**Artifact content opened by this review: NO** (directory/`stat` metadata only).
**Artifact-content attempts consumed by this review: 0.**
**Real frozen Stage B command executed: NO.** Only the focused/predecessor pytest suites
(temp basetemp) and one synthetic injected-table behavior-equivalence dry run under `/tmp`
were run; neither touches the sibling artifact or the target root.

## Verdict: PASS

F-1 is closed: freeze v2 §4 B5 precedence, the code comment, and `classify_stageb_failure`
now agree exactly on ordering and applicability conditions, and the added hard-gate mapping
paragraph maps every implementation-added gate to a frozen gate with no new scientific
threshold. NB-1 and NB-2 are closed; NB-4 is resolved by the mapping paragraph. No frozen
value drifted. The repair is confirmed docs/comments-only by every available channel.
**The frozen Stage B plan is cleared for its single authorized execution** (once, exact
command, no rerun), subject only to the main thread's authorization gate.

---

## A. Check table (8 required checks)

| # | check | result | evidence |
|---|---|---|---|
| 1 | Delta-only (comments only) | **PASS** | see §B |
| 2 | F-1 closure + hard-gate mapping | **PASS** | see §C |
| 3 | NB-1 closure | **PASS** | see §D |
| 4 | NB-2 closure | **PASS** | see §D |
| 5 | No frozen value drift | **PASS** | see §E |
| 6 | Premises | **PASS** | see §F |
| 7 | Tests | **PASS** | focused 32 passed / 28.61 s; predecessor 8-file 120 passed / 63.72 s |
| 8 | Scope | **PASS** | see §H |

All commands run with `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, cwd = repo root.

## B. Check 1 — delta-only verification (docs/comments only)

**R1a. Repair window (mtimes).** `stat -c '%y %n' …` on all declared paths shows exactly three
files touched after R0 (R0 file mtime 00:56:01): `empirical_channel.py` 00:58:21,
`empirical_diagnostic.py` 00:58:21, queue `P3_STAGEB_FREEZE.md` 00:58:34. Every other declared
path predates R0 (`empirical_oracle.py` 00:31, test file 00:36, mvp freeze 00:41, tasks.md
00:41, EXPLORATION_NOTES 00:45). No other file was touched by the repair.

**R1b. `empirical_channel.py` is comment-only (directly visible in git diff).**
`git diff -- empirical_channel.py` = a single hunk `@@ -67,9 +67,10 @@`, 3 deletions / 4
insertions, entirely inside the frozen-seeds comment. Constants byte-identical:
`P3_UNIT_SEED = 2026091314` (74), `P3_TRAIN_SEED = 2026091315` (75), `P3_DIAG_SEED =
2026091316` (76), `BANNED_SEEDS = frozenset(range(2026091200, 2026091214))` (77),
`make_rng` body unchanged (80–87). No logic, threshold, count, mask, command or target.

**R1c. `empirical_diagnostic.py` — only the module comment expanded by 3 lines.**
- Current module comment: `:337–342` (6 lines), corrected precedence ordering (pre-repair
  occupied 3 lines `:337–339`).
- R0 recorded 19 distinct line anchors across the whole file; every anchor at or after the
  comment is now exactly **+3** lines, and no anchor deviates:

| R0 anchor | R0 lines | current | Δ |
|---|---|---|---|
| `STAGEB_SOFT/TOTAL/RSS` constants | 344–346 | 347–349 | +3 |
| `STAGEB_PROB_TOL` / `LOG_TOL` | 347–348 | 350–351 | +3 |
| `B1_N/BLOCKS, B2, B3, B4` constants | 349–356 | 352–359 | +3 |
| `stageb_masks` expressions | 397–403 | 400–406 | +3 |
| `classify_stageb_failure` | 407–437 | 410–440 | +3 |
| `_truth_leak_violation` | 464–496 | 467–499 | +3 |
| `probs_to_symbol_metric` call sites | 540,674,794 | 543,677,797 | +3 |
| `_stageb_b1_gates` | 615–629 | 618–632 | +3 |
| B2/B3 disclosed values | 681–688 | 684–691 | +3 |
| B2/B3 exact branch | 692 | 695 | +3 |
| `_stageb_timed_median` | 735–747 | 738–750 | +3 |
| B4 profile case | 750–837 | 753–840 | +3 |
| B4 `true_U` / `metric_argmax` fallback | 799 / 805–809 | 802 / 808–812 | +3 |
| plan `unit/train_not_used` | 880–885 | 883–888 | +3 |
| B3 `total_blocks=40` | 913 | 916 | +3 |
| `rss_bytes_max` in plan | 924–928 | 927–931 | +3 |
| rng `Generator` guard | 1039 | 1042 | +3 |
| hard gates (NB-4) | 1113–1125 | 1116–1127 | +3 |
| `b4_scored_blocks: 0` | 1144 | 1147 | +3 |
| stageb root creation `outp.mkdir` | 1188 | 1191 | +3 |
| stageb `_check_out` call | 1212 | 1215 | +3 |
| `load_prior_artifact` call | 1216 | 1219 | +3 |

  A line-count-changing edit anywhere else in the file would have broken this uniform shift;
  none does.

**R1d. Behavior-equivalence against the pre-repair binary output (strongest available check).**
R0's injected-table full-matrix dry run wrote
`/tmp/opencode/p3_review/ulimit_run/stageb/diagnostic_summary.json` at **2026-09-13 00:54:02**
(before the repair). I re-ran the identical deterministic construction
(`ulimit_matrix.py` tables: `np.random.default_rng(20260913)`, p1/p_b as scripted; same
`make_rng(P3_DIAG_SEED)`), current code, fresh root `/tmp/opencode/p3_rereview_r1/stageb_behavior`.
Comparison of every non-timing field (hard_gates, hard_gates_pass, truth_leak_violations,
resource_abort totals, nonfinite_total, candidate_conclusion, all B1 per-case counts/gates/
attribution, B2/B3 totals + per-case counts/attribution, B4 profile non-timing fields, B5
per-case/totals): **0 differences**. The pre-repair run exercised the classifier on 295
non-exact blocks (`SC_decision` 128, `expected_under_disclosure` 167); the post-repair rerun
reproduced both totals exactly, so `classify_stageb_failure` behavior is unchanged.
Both runs: `hard_gates_pass = True`, exactly the same 5 output files.

**R1e. Classifier semantics re-read from source** (`empirical_diagnostic.py:410–440`):
`support_failure → artifact_adapter_support`; `normalization_failure → normalization`;
`impossible → disclosure_contradiction`; `nonfinite → SC_numeric`; `other`: `unclassified_error
→ unattributed`, else `under_disclosure_ambiguous → expected_under_disclosure`, else
`SC_decision`; `exact`/`resource_abort` raise `ValueError`. A 9-case semantic matrix (including
support > impossible and normalization > nonfinite) matches R0's description exactly, and the
unchanged test `test_sb_attribution_classifier_forced_categories` (test file mtime 00:36,
pre-repair) pins the same semantics; it passed.

No executable logic, constant, threshold, seed, count, mask, command or target changed.
Residual epistemic limit (non-blocking, N-2): no pre-repair blob of
`empirical_diagnostic.py` is retained, so literal byte-identity of all 1291 lines cannot be
shown by diff alone; the +3 anchor shift, deterministic pre/post output equality, classifier
re-read and green suites provide converging evidence and no contrary evidence was found.

## C. Check 2 — F-1 closure and hard-gate mapping

Frozen text (queue `P3_STAGEB_FREEZE.md` §4 lines 81–92) now reads, per non-exact executed
block: `artifact_adapter_support` (sampled true symbol zero-probability in its metric row) >
`normalization` (metric-row normalization failure) > `disclosure_contradiction`
(`ImpossibleDisclosedValueError`) > `SC_numeric` (nonfinite decision metrics /
`NumericNonfiniteError`) > `unattributed` (unclassified decoder exception; frozen crash=0) >
`expected_under_disclosure` (finite non-exact with an undisclosed-coordinate pointwise MAP
mismatch) > `SC_decision` (remaining finite non-exact); B1 finite non-exact = `SC_decision`
(or `unattributed`). Code comment `empirical_diagnostic.py:337–342` repeats the same ordering
and conditions. Cross-check against the implementation:
- `support_failure = np.any(probs[np.arange(n), high] == 0)` (B1 `:544`, B2/B3 `:678`);
- `normalization_failure = |logaddexp.reduce(logp, axis=1)|.max() > 1e-9` (`:545–547`, `:679–681`);
- `impossible`/`nonfinite`/`unclassified` mapping as in R1e;
- `ambiguous = any((~mask) & (argmax(logp,axis=1) != high))` (`:720–723`, B2/B3 only; B1 call
  passes no ambiguity).
Ordering and applicability conditions match exactly. No stale reversed-order text remains
anywhere (grep for the old chain found it only inside the historical R0 review, where it
correctly describes the pre-repair defect).

Hard-gate mapping paragraph (freeze lines 97–103) vs code (`:1113–1128`):
- `b1_all_gates` = B1 five frozen gates (prob 1e-12, log 1e-9, support 0, numeric 0,
  truth-leak 0) + `decode_exceptions`/`oracle_exceptions` = 0 (crash=0) — code
  `_stageb_b1_gates` `:618–632`, `b1_all_gates_pass` `:1113–1115`. ✓
- `b2_b3_zero_nonfinite` = frozen nonfinite=0 (code `nonfinite_total == 0`, `:1109–1118`). ✓
- `b2_b3_zero_unattributed` = frozen crash=0 for decoder exceptions (`:1119`). ✓
- `b2_b3_coverage_complete` / `b4_complete` = frozen evidence completeness: all planned
  blocks executed (`:1120–1124`) and `>= STAGEB_B4_REPS` measured calls per B4 leg
  (metric and decode; `:838–840`). ✓
- `zero_truth_leak` = frozen sentinel=0 (`:1126`). ✓
- "B3 applies no exact-count threshold": code has no exact threshold for B3. ✓
No new scientific threshold is introduced by any mapped gate. Non-blocking precision note N-1
below (gate scopes vs names).

## D. Checks 3 and 4 — NB-1 / NB-2 closure

- **NB-1 PASS.** `empirical_channel.py:69–73` now reads: the Phase 3 range 2026091200..1213
  (containing 2026091200..1203) "is refused by make_rng"; 20260911 (SC-oracle) and 20260930
  (prior-adapter) "are packet-banned and must never be used (not runtime-refused)". Matches
  `BANNED_SEEDS = frozenset(range(2026091200, 2026091214))` (`:77`) and `make_rng` (`:80–87`)
  exactly; no runtime-refusal claim remains.
- **NB-2 PASS.** Freeze §4 masks paragraph (lines 60–64) now scopes true-U disclosure to
  B2/B3 and documents B4 as timing-only: it discloses true U when available and records
  `disclosed_value_source` (`true_U`, or a `metric_argmax` fallback when true-U disclosure is
  unsupported), with the fallback affecting no B1–B3 count or gate. Code matches
  (`:801–802` sets `true_U`; `:808–812` falls back to `metric_argmax` on
  `ImpossibleDisclosedValueError`; B4 never scored, `:1147`).

## E. Check 5 — no frozen value drift

| item | frozen value | re-verified |
|---|---|---|
| Stage B seed | 2026091316 (`P3_DIAG_SEED` = `STAGEB_SEED`) | constants + command; ✓ |
| exact command | R0-recorded 20-token command | token-identical to queue freeze §7 (`TOKEN-IDENTICAL`) |
| output root | `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/` | freeze §6; **ABSENT** at start and end |
| output files | exactly 5: `frozen_plan.json`, `oracle_records.json`, `stress_and_profile.json`, `diagnostic_summary.json`, `report.md` | `STAGEB_OUT_FILES` `:376–382`; `mkdir(exist_ok=False)` + 5 writes `:1191–1200` |
| artifact sizes | 208467 / 752 bytes | `stat -c '%s'` → 208467, 752 (metadata only) |
| B1 | N=(2,4), 64 blocks each | `:352–353`; dumped values identical |
| B2 | N=(16,64), 5 masks × 16 = 80 each | `:354–355` |
| B3 | N=256, 5 masks × 8 = 40 | `:356–357`, plan `total_blocks` `:916` |
| B4 | N=(64,256,1024), M5, ≥5 measured, 1 warm-up | `:358–359`, `:738–750`, `:838–840` |
| masks M1–M5 | M1 0..N-2; M2 0..N/2-1; M3 N/2..N-1; M4 even indices; M5 `analytic_order(0.05,N)[:N/2]` | independently re-dumped and equality-asserted for N=16/64/256 (int64, unique, in range); imported `construction.analytic_order` unchanged |
| budget | soft 120 s; total 3600 s; RSS 2147483648 B | `:347–349`; `_peak_rss_gib` Linux scale `1024**2` intact (`:118–127`) |

## F. Check 6 — premises

| probe | command | raw result |
|---|---|---|
| interpreter | `…/.venv/bin/python -c "import sys,numpy,pytest; …"` | `sys.executable=…/.venv/bin/python`; numpy 2.5.3; pytest 9.1.1 |
| git delta | `git status --porcelain` | exactly the 10 declared paths (7 `M`, 3 `??`: EXPLORATION_NOTES.md, empirical_channel.py, empirical_diagnostic.py, empirical_oracle.py, test_nbpolar_empirical_sc.py, mvp P3_STAGEB_FREEZE.md, phase4-p0 tasks.md, queue P3_STAGEB_FREEZE.md, queue PRE_EXECUTE_REVIEW.md, phase4-p3 spec dir); `git diff --cached` empty |
| target root | `ls -d .workbuddy/…/empirical_prior_sc_diagnostic` | "No such file or directory" (checked at start and end) |
| attempt ledger | `find .workbuddy -iname '*ATTEMPT*' -o -iname '*COUNTER*' -o -iname '*consumed*' -o -iname '*ledger*'`; queue listing | empty; queue holds only the 7 declared files; STATUS.yaml `artifact_content_attempts_allowed: 1`, no consumption counter; freeze records 0 consumed |
| commit | `git log -1`, `git diff --cached --stat` | HEAD `ab173f2a…` unchanged; nothing staged |
| production outputs | `find .workbuddy results comparison_bench/outputs_comparison -name frozen_plan.json -o -name diagnostic_summary.json -o -name stress_and_profile.json` | empty |

Post-review note: writing this R1 file adds one untracked path (11 total); no other change.

## G. Check 7 — tests

- Focused: `…/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_empirical_sc.py -q -p no:cacheprovider --basetemp=/tmp/opencode/p3_rereview_r1/basetemp_focused` → **32 passed, 1 warning in 28.61 s** (expected 32; R0: 32 / 27.79 s).
- Predecessor 8-file suite (transform, sc, construction, r1, prior, prior_artifact, p2r1_diagnostic, empirical_sc): **120 passed, 1 warning in 63.72 s** (expected 120; R0: 120 / 64.68 s). The single warning is the pre-existing pytest `cache_dir` config warning.
- Additionally (check 1 support): deterministic injected-table full-matrix rerun under `/tmp`, `hard_gates_pass = True`, 5 files, 0 field differences vs the pre-repair output. This consumed no artifact attempt and wrote nothing into the repo.

## H. Check 8 — scope

- Accepted modules `transform.py`, `sc.py`, `prior.py`, `prior_artifact.py`, `cal_diagnostic.py`, `construction.py`, `synthetic.py`, `algebra.py`, `oracle.py`, `eval_r1.py`: none appear in `git diff --name-only`. ✓
- P3 acceptance boxes: `grep -c '^- \[ \] P3' tasks.md` → **8**; `grep -c '^- \[[xX]\] P3'` → **0**. ✓
- No writes outside declared paths: no outputs under `results/`, `comparison_bench/outputs_comparison/`, `.workbuddy` output roots, or the sibling artifact root; tests/dry runs wrote only to `/tmp` and the pytest basetemp. ✓
- No commit/push; HEAD unchanged. ✓

## I. Findings

### Blocking
None.

### Non-blocking
- **N-1 (docs precision).** The merged gate totals include B1 where the name says `b2_b3_*`
  (`nonfinite_total` adds B1 `numeric_failures` `:1109–1111`; `attribution_totals` merges
  b1+b2+b3 `:1102–1103`), and `b1_all_gates` also contains B1 `coverage_complete`
  (`:619–624`). All are conservative supersets of already-frozen B1 gates; the mapping
  paragraph's "no new scientific threshold" claim is unaffected. No action needed before
  execution; a one-line scope note could be folded into a future doc touch.
- **N-2 (evidence limit).** Byte-identity of the pre-repair `empirical_diagnostic.py` cannot be
  proven (no retained blob); mitigated by R1c/R1d. No contrary evidence found.
- R0's NB-3 (process-level seed enforcement), NB-5 (Stage A RSS provenance) and NB-6
  (`_stageb_timed_median` warm-up overshoot ≤ one call) remain as recorded process notes; none
  blocks this execution.

## J. Closure statements

- The accepted artifact was **never opened** by this review: only `stat` sizes (208467 / 752)
  and directory metadata were read. **Artifact-content attempts consumed: 0.**
- The target root `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/`
  was **absent at the start and at the end** of this review.
- The real frozen Stage B command was **not executed**; no rerun/tuning was performed. The
  synthetic behavior rerun used caller-injected tables and a `/tmp` output root only.
- Review-time writes: this file only (plus `/tmp` scratch). No reviewed file was modified; no
  commit/push was made.

**PASS — F-1, NB-1, NB-2 closed; no frozen value drift; the frozen Stage B plan is cleared for
its single authorized execution** (exact §7 command, one attempt, no rerun), subject to the
main thread's authorization gate and the standing Pre-RESULT review before publication.
