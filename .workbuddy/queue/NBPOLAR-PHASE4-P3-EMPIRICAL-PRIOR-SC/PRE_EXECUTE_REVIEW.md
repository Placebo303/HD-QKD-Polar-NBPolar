# Independent Pre-EXECUTE review — NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC

Reviewer: independent Pre-EXECUTE reviewer (read-only; did not write the reviewed code).
Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, HEAD `ab173f2a` (2026-09-12 03:36 +0800),
all P3 work uncommitted.
Date: 2026-09-13.

**Artifact content opened by this review: NO** (directory/`stat` metadata only).
**Artifact-content attempts consumed by this review: 0.**
**Stage B artifact command executed: NO.** Only (a) fake-path stageb refusal runs under
`/tmp/opencode/p3_review` and (b) an injected-table full-matrix dry run in `/tmp` were run.

## Verdict: NEEDS_CHANGES

One (1) blocking item — F-1, the freeze-v2 B5 attribution precedence text vs the implemented
classifier. Every other required check passes. The blocking item can be repaired **docs-only,
before the artifact read** (smallest repair below), so no artifact attempt is affected.

---

## A. Frozen checklist record (as verified against code + docs, not executed)

| item | frozen value | verified |
|---|---|---|
| artifact root (read-only sibling) | `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/` | yes (freeze v2 §2; TASK_PACKET lines 27–35) |
| npz | `model_f_input.npz` = **208467 bytes** | `stat -c '%s'` → 208467 |
| summary | `model_f_input_summary.json` = **752 bytes** | `stat -c '%s'` → 752 |
| loader | accepted `prior_artifact.load_prior_artifact`, single load | `prior_artifact.py:201`; `empirical_diagnostic.py:1216` (one call) |
| derivation | `prior.smooth_joint_to_conditional(counts_ab, LAMBDA_STAR)` → `prior.derive_p1`; `p_b = artifact.p_b` | `prior.py:100,162`; `empirical_diagnostic.py:1217–1219` |
| prob→log conversion | accepted `prior.probs_to_symbol_metric` (q=32) | `empirical_diagnostic.py:540,674,794`; `prior.py:288` |
| artifact-content attempts | allowed **1**, consumed **0** at freeze | STATUS.yaml `artifact_content_attempts_allowed: 1`; no ledger/counter file anywhere; EXPLORATION_NOTES.md:4 |
| attempt consumption point | first artifact-content open by the frozen command | `run_stageb_diagnostic` `empirical_diagnostic.py:1216` |
| banned predecessor range | 2026091200..1213 refused | `empirical_channel.py:76`; tested + CLI-verified |
| unit seed | **2026091314** (`P3_UNIT_SEED`), not used in Stage B | `empirical_channel.py:73`; plan records not-used (`empirical_diagnostic.py:882–884`) |
| TRAIN seed | **2026091315** (`P3_TRAIN_SEED`), not used in Stage B | `empirical_channel.py:74` |
| Stage B diagnostic seed | **2026091316** (`P3_DIAG_SEED` = `STAGEB_SEED`), single RNG stream, order B1→B2→B3→B4 | `empirical_channel.py:75`; `empirical_diagnostic.py:343,1213` |
| B1 block counts | N=2: **64**; N=4: **64**, no disclosure | `STAGEB_B1_N=(2,4)`, `STAGEB_B1_BLOCKS=64` (`:349–350`) |
| B2 block counts | N=16: 5 masks × **16** = 80; N=64: 5 masks × **16** = 80 | `STAGEB_B2_N`, `STAGEB_B2_BLOCKS=16` (`:351–352`) |
| B3 block count | N=256: 5 masks × **8** = **40** (within 20..64) | `STAGEB_B3_N=256`, `STAGEB_B3_BLOCKS=8` (`:353–354`); plan `total_blocks=40` (`:913`) |
| B4 profile | N=64/256/1024, M5 only, timing-only; 1 warm-up + ≥5 measured; metric (4×N batch) + one prebuilt (N,32) decode | `STAGEB_B4_N`, `STAGEB_B4_REPS=5` (`:355–356,750–837`) |
| B5 | attribution only, no samples; B4 scored blocks = 0 | `:1144` `b4_scored_blocks: 0` |
| M1 all-but-one | positions **0..N-2** (undisclosed N-1) | `stageb_masks` `:397`; independently dumped N=16/64/256 |
| M2 prefix | **0..N/2-1** | `:398`; dumped |
| M3 suffix | **N/2..N-1** | `:399`; dumped |
| M4 alternating | **0,2,...,N-2** | `:400`; dumped |
| M5 construction-order | **first N/2 of `construction.analytic_order(0.05, N)`**, imported unchanged | `:401–403`; `analytic_order` at `construction.py:274`; equality re-checked for N=16/64/256; `construction.py` untouched |
| disclosed values | true `U = polar_transform(A_high)` at mask positions (B2/B3; B4 has a documented argmax fallback) | `:681–688`, `:796–799` (see NB-2) |
| B1 gates | prob max err ≤ **1e-12**; finite-entry log max err ≤ **1e-9**; support mismatch **0**; numeric fail **0**; truth-leak **0** | `STAGEB_PROB_TOL`, `STAGEB_LOG_TOL` (`:347–348`); `_stageb_b1_gates` (`:615–629`) |
| budget | total **3600 s** (`timeout 3600`); per-case soft stop **120 s**; RSS **< 2 GiB** (`ulimit -v 2097152`), plan `rss_bytes_max=2147483648` | `:344–346`; `:924–928` |
| output root | `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/` — **ABSENT at start and end of review** | `ls -d` → "No such file or directory" |
| output files | exactly 5: `frozen_plan.json`, `oracle_records.json`, `stress_and_profile.json`, `diagnostic_summary.json`, `report.md` | `STAGEB_OUT_FILES` (`:373–379`); temp dry run listed exactly these 5 |

Exact frozen command (recorded, **NOT** executed; freeze v2 §7 lines 120–124):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_diagnostic --mode stageb --npz /mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz --summary /mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json --seed 2026091316 --out .workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic
```

---

## B. Numbered checklist (maps to the 13 required checks)

Result key: PASS / FAIL. All commands run with
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, cwd = repo root.

### 1. Premises — PASS

| probe | command | raw result |
|---|---|---|
| interpreter | `…/.venv/bin/python -c "import sys,numpy,pytest; …"` | `sys.executable=/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`; numpy **2.5.3**; pytest **9.1.1** |
| git delta | `git status --porcelain` | exactly the 8 declared paths: M `…/EXPLORATION_NOTES.md`, M `empirical_diagnostic.py`, M `empirical_oracle.py`, M `test_nbpolar_empirical_sc.py`, M `openspec/…/formal-ir-nbpolar-mvp/P3_STAGEB_FREEZE.md`, M `openspec/…/formal-ir-nbpolar-phase4-p0/tasks.md`, ?? `.workbuddy/…/P3_STAGEB_FREEZE.md`, ?? `openspec/…/specs/nbpolar-phase4-p3/`; **nothing else**; `git diff --cached` empty |
| artifact sizes | `stat -c '%s %n' …` | `208467 …/model_f_input.npz`; `752 …/model_f_input_summary.json` |
| target root | `ls -d .workbuddy/…/empirical_prior_sc_diagnostic` | `No such file or directory` (checked at review start and end) |
| attempt ledger | `find .workbuddy -iname '*ATTEMPT*' -o -iname '*COUNTER*' -o -iname '*consumed*'`; queue dir listing | empty; queue holds only `AUTHORIZATION_PROMPT.md`, `EXPLORATION_NOTES.md`, `P3_STAGEB_FREEZE.md`, `PROMPT.md`, `STATUS.yaml`, `TASK_PACKET.md`; no counter/ledger indicates consumption |

### 2. Artifact identity + attempt — PASS

- Freeze v2 §2 matches TASK_PACKET lines 27–35 and code: loader `prior_artifact.load_prior_artifact` (`prior_artifact.py:201–217`), derivation `smooth_joint_to_conditional(counts_ab, LAMBDA_STAR)` → `derive_p1` and `p_b=artifact.p_b` (`prior.py:100,162`; `empirical_diagnostic.py:1209–1219`), `LAMBDA_STAR=137.3823795883264` (`prior_artifact.py:49`).
- Single artifact open: exactly one `load_prior_artifact` call in the stageb path (`empirical_diagnostic.py:1216`); root is created only at the very end (`:1188`), after the full matrix; existing root refused first (`_check_out` at `:1212`, before `make_rng` and load — refusal order pinned by `test_sb_stageb_refusal_paths`, focused suite passed).

### 3. Seed — PASS

- `STAGEB_SEED = P3_DIAG_SEED = 2026091316` (`empirical_channel.py:75`, `empirical_diagnostic.py:343`); distinct from unit 2026091314 / TRAIN 2026091315 (`empirical_channel.py:73–74`); outside banned 2026091200..1213 (`empirical_channel.py:76`).
- Gate verified both boundaries in test (focused suite passed) and end-to-end via the exact CLI shape with fake `--npz`:
  `--seed 2026091200` → `empirical_diagnostic refused: seed contract: seed 2026091200 is a banned predecessor stream`, exit 2, no root created.
- No hidden seed: `make_rng` is the only RNG constructor in the stageb path; `grep np.random empirical_diagnostic.py` → only the `isinstance(rng, np.random.Generator)` guard (`:1039`); no default seed. Plan records unit/TRAIN as `not_used` (`:880–885`).
- Note NB-3: the API accepts any non-banned seed; only the frozen command fixes 2026091316. No alternate seed source exists.

### 4. Block counts + masks — PASS

- Counts/constants exactly as frozen (see table A; `STAGEB_B1_N/BLOCKS`, `B2`, `B3`, `B4` at `empirical_diagnostic.py:349–356`).
- Independent mask dump (`N=16/64/256`) confirmed M1 `0..N-2`, M2 `0..N/2-1`, M3 `N/2..N-1`, M4 even indices, M5 `analytic_order(0.05,N)[:N/2]` (equality asserted) — all `int64`, unique, in range.
- `construction.py` is not in `git diff --name-only` (imported unchanged).
- Disclosed values are `u_true[positions]` with `u_true = polar_transform(high)` (`:681–682, 687–688`; B4 `:797–799`). The only truth consumers are the generator/support flag (`:675`), initial-MAP scoring (`:679`), exact scoring (`:692`), disclosed map, truth-leak sentinel. `build_p1_metrics(bob, p1_table)` has no truth argument (`empirical_channel.py:329`; A04 test).

### 5. Exact command + target — PASS

- `--help` output shows exactly `--mode {synthetic,artifact,stageb}`, `--q`, `--n`, `--n-b`, `--seed` (required), `--n-blocks`, `--npz`, `--summary`, `--out` (required). No `--case`/`--mask` (stale draft flags confirmed nonexistent).
- stageb with no `--npz/--summary`: `refused: diagnostic contract: stageb mode requires --npz and --summary`, exit 2, no root.
- Fake-path stageb run under the exact frozen wrapper (`cd repo; ulimit -v 2097152; timeout 3600; absolute interpreter; --mode stageb --npz /tmp/opencode/p3_review/fake/model_f_input.npz --summary /tmp/opencode/p3_review/fake/model_f_input_summary.json --seed 2026091316 --out /tmp/opencode/p3_review/fake/empirical_prior_sc_diagnostic`):
  `refused: artifact contract: npz path is not a regular file: /tmp/...` → exit 2; **no root created** (checked); the real artifact paths were not used. This also proves the module imports and runs under `ulimit -v 2097152`.

### 6. Truth isolation — PASS

- Operational metric signature truth-free (`empirical_channel.py:329`; test A04 passed).
- Truth-leak sentinel `_truth_leak_violation` (`empirical_diagnostic.py:464–496`) returns only 0/1, rebuilds the metric from Bob+table, reruns SC with already-frozen disclosed values, and compares bitwise. Direct test passed in the focused suite: honest → 0, tampered probs → 1, tampered `res` → 1. Full-matrix dry runs report `truth_leak_violations = 0`.
- `empirical_oracle.py` imports only numpy/itertools/numbers + `.transform.polar_transform_reference` (`:36–43`); no `sc.py`/`oracle.py` import; no SC minus/plus/combine helpers (A11 test passed).
- No sibling-path markers in any reviewed file (grep; the only `D:`/`workspace` strings are the A12 self-scan literals built from parts, `test_nbpolar_empirical_sc.py:341–349`).

### 7. Forbidden paths closed — PASS

- Grep across the four reviewed files for `parquet|TTBin|held.?out|DEV|EVAL|reconcil|benchmark|results/|outputs_comparison|v72p2d5|allow_pickle|np\.load|/mnt/d|D:` → only prose docstrings naming the forbidden classes and the A12 marker construction; **no path literal, loader, or data access**.
- No default production path: `--npz/--summary` default `None`; `--out/--seed` required; stageb enforces npz/summary (`:1274–1276`). 
- Tests use injected tables + temp roots; refusal paths use nonexistent temp paths only (`test_nbpolar_empirical_sc.py:821–844, 596–625`). No test invokes the production artifact path.

### 8. Budget plumbing — PASS (with one docs note, NB-5)

- `STAGEB_SOFT_CAP_S=120.0`, `STAGEB_TOTAL_CAP_S=3600.0`, `STAGEB_RSS_LIMIT_BYTES=2147483648` (`:344–346`); per-case deadline `min(now+soft, total_deadline)` (`:456–457,1052`); expiry increments `n_resource_abort` and continues (`:534–536, 668–670, 779–781, 740–741`); `resource_abort` is separate from exact and from attribution (test `test_sb_soft_stop_bookkeeping_never_counts_exact` passed).
- **RSS fix verified**: old line `ru_maxrss / 1024**3` replaced by `raw / 1024**2` on Linux and `/1024**3` on macOS (`:118–127`). Independent full-matrix dry run under `ulimit -v 2097152`: peak RSS **0.217 GiB < 2 GiB**; plan records `rss_bytes_max = 2147483648` = 2097152 KiB.

### 9. Numerical gates — PASS

- B1 compares exactly the frozen five quantities (`_stageb_b1_gates` `:615–629`; constants `:347–348`), plus the conservative extras decode/oracle-exception and coverage (NB-4).
- Disjoint accounting enforced: `exact` only in the exact branch (`:555–571`, `:692–710`); `impossible`/`other`/`nonfinite` each have their own counters; `resource_abort` only via expiry. Injected-matrix test asserts `n_executed + n_resource_abort == n_blocks_planned` and `exact+impossible+other+nonfinite == n_executed`.

### 10. Oracle — PASS (independently re-checked)

- Default literal path and 4096 cap unchanged: `MAX_ORACLE_CANDIDATES=4096`, vector cap `1<<20` (`empirical_oracle.py:45–46`); all diff deletions in this file are cap-parameter threading; A06/A07/A08 passed in the suite.
- Vectorized backend independently implemented: no SC helper imports; own `_dense_generator`, batch dense transform, mixed-radix enumeration + slice logsumexp.
- Independent checks (my script, synthetic only):
  - batch transform vs `polar_transform_reference`, GF4+GF32, N=2/4/8, 17 rows each → bitwise equal;
  - vectorized vs literal: GF4 N=4 (4 modes × 6 prefixes incl. all coordinates), GF32 N=2 (4 modes × 3 prefixes), GF32 N=4 prefixes length 2/3 (explicit cap) → support equal, prob ≤1e-12, log ≤1e-9, rows normalized (`logsumexp=0`);
  - exact-zero vs `-inf` support preserved; impossible prefix all-`-inf` identical in both; all-`-inf` input row rejected by both;
  - uniform-row analytic 1/q at GF4 N=4 and GF32 N=2/4; batch API == single wrapper;
  - **N=4 chain cost: median 0.1985 s/block over 8 samples → 64 blocks ≈ 12.70 s**, well under the 120 s soft cap; my under-`ulimit` in-runner oracle wall was **11.71 s** (matches operator's 11.7 s).

### 11. Tests — PASS

- Focused: `python -m pytest comparison_bench/tests/test_nbpolar_empirical_sc.py -q -p no:cacheprovider --basetemp=/tmp/opencode/p3_review/basetemp_focused` → **32 passed in 27.79 s** (operator claimed 32 / 29.1 s).
- 8-file predecessor suite (transform, sc, construction, r1, prior, prior_artifact, p2r1_diagnostic, empirical_sc) → **120 passed in 64.68 s** (operator claimed 120 / 65.3 s).
- No sibling-root access by code inspection of all 8 files: sibling strings appear only in source-absence scans/fixtures of accepted tests. Residual risk: absence was checked by inspection + the tests' own AST/source scans, not by runtime tracing (strace); no contrary evidence found.

### 12. Freeze-doc adjudication — **FAIL (blocking F-1)**

- Stale `openspec/changes/formal-ir-nbpolar-mvp/P3_STAGEB_FREEZE.md`: banner-only diff (`21 insertions, 0 deletions`), original text preserved below; all three banner defect claims are factually correct (`--case/--mask` absent from CLI; stale target layout vs TASK_PACKET §Output; `MASTER_SEED=20260911` is the earlier sc-oracle seed while Stage B uses 2026091316). PASS.
- Freeze v2 vs code/TASK_PACKET: all values in §2–§8 agree with the code **except the B5 precedence statement (F-1)**; `spec.md`/`tasks.md` delta is consistent (spec states categories, not sub-order). FAIL on F-1 only.

### 13. Scope creep — PASS

- Accepted modules `transform.py`, `sc.py`, `prior.py`, `prior_artifact.py`, `cal_diagnostic.py`, `construction.py`, `synthetic.py`, `algebra.py`, `oracle.py`, `eval_r1.py` are untouched (`git diff --name-only` = 6 declared files only; no staged changes; untracked = exactly the 2 declared paths).
- No P3 acceptance box checked (`grep -c '^- \[ \] P3'` → **8**; `'^- \[[xX]\] P3'` → none).
- No forbidden writes: no files under `results/`, `outputs_comparison/`, or the sibling root; tests/dry runs wrote only to `/tmp` and pytest basetemps; target root absent.
- No commit/push from this work: HEAD `ab173f2a` predates the session (2026-09-12 03:36); all P3 edits are uncommitted.

---

## C. Findings

### Blocking

**F-1 — freeze v2 §4 B5 attribution precedence is the reverse of the implemented classifier.**
- Frozen text (`P3_STAGEB_FREEZE.md:73–75`): "`artifact_adapter_support` > `normalization` > `disclosure_contradiction` > `SC_numeric` > **`SC_decision` > `expected_under_disclosure` > `unattributed`**" (the module comment at `empirical_diagnostic.py:337–339` repeats it).
- Implementation (`classify_stageb_failure`, `empirical_diagnostic.py:407–437`), for `outcome="other"`: (1) `unclassified_error` → `unattributed`; (2) `under_disclosure_ambiguous` → `expected_under_disclosure`; (3) else `SC_decision`. Effective order: **`unattributed` > `expected_under_disclosure` > `SC_decision`** — reversed for the last three categories.
- Consequence: every finite non-exact B2/B3 block whose undisclosed-position argmax disagrees with truth is reported `expected_under_disclosure` (per the code), not `SC_decision` (per the printed chain); an unclassified decoder exception with ambiguous undisclosed positions is `unattributed` (failing the implementation-added `b2_b3_zero_unattributed` gate) instead of `SC_decision`/`expected_under_disclosure`. The reported B5 matrix is a required output, so the run's output semantics currently depend on which text governs. Read literally, the printed chain makes `expected_under_disclosure` unreachable, which indicates the chain text is defective.
- Single decision needed: **ratify the classifier's effective semantics and correct the frozen text** (recommended; smallest repair, docs-only: freeze v2 §4 precedence line + `empirical_diagnostic.py:337–339` comment; `spec.md` does not freeze the sub-order so no spec change is strictly required), **or** direct a code change to `classify_stageb_failure` plus its test. Either way, re-run the focused suite and re-review item 12.

### Non-blocking

- **NB-1** `empirical_channel.py:69–72` docstring claims `make_rng` refuses 1200..1203, 20260911 and 20260930, but `BANNED_SEEDS` is only `range(2026091200, 2026091214)` (`:76`). The packet-banned range is correctly refused and the frozen seed is unaffected; docs-precision fix at next touch.
- **NB-2** Freeze v2 line 55 ("disclosed values are always the true U symbols") does not mention the B4-only `metric_argmax` fallback (`empirical_diagnostic.py:805–809`, traced by `disclosed_value_source` `:799`). B4 is timing-only and ungated; document or scope the sentence to B2/B3 in the same revision as F-1.
- **NB-3** Stage B seed enforcement is process-level: any non-banned seed (including unit/TRAIN) passes `make_rng`; only the frozen command fixes 2026091316. No hidden/default seed exists and the plan records unit/TRAIN as not used. Accept as process discipline or add a stageb seed whitelist.
- **NB-4** Implementation-added hard gates go beyond the frozen "only" lists (freeze §4 B1/B3): `b2_b3_zero_unattributed`, `b2_b3_coverage_complete`, `b4_complete` (`empirical_diagnostic.py:1113–1125`). Direction is conservative (cannot create a false pass) but can suppress `candidate_conclusion` where the frozen gates would pass; reconcile wording or mark advisory.
- **NB-5** Stage A historical RSS figures (`EXPLORATION_NOTES.md:75–83`, 0.091–0.103 GiB) are at the corrected KiB→GiB scale and cannot have come from the pre-fix helper (which reports ~1024× smaller); the measurement source of that table is not recorded. Numerically plausible and consistent with my under-`ulimit` 0.217 GiB; docs-provenance note only.
- **NB-6** `_stageb_timed_median` (`empirical_diagnostic.py:735–747`) performs the warm-up without a deadline check and cannot interrupt an in-flight decode, so a pathological case may overshoot the 120 s soft cap by at most one call; the OS `timeout 3600` and the internal total deadline still bound the run. Residual-risk note, not a blocker.

---

## D. Closing statements

- The accepted artifact was **never opened** by this review: only `stat` (sizes 208467/752) and directory metadata were read. **Artifact-content attempts consumed: 0.**
- The target root `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/` was **still absent at the end of the review** (`ls -d` → "No such file or directory"), and the real Stage B command was never executed.
- Review-time writes by this reviewer: this file only. No reviewed file was modified, no commit/push was made.
