# PRE-RESULT REVIEW — NBPOLAR-M2-PRIOR-G3-CONFIRM (independent)

- Reviewer: `reviewer-go` (independent of the operator and of the main thread's conclusions)
- Session: `ses_f376e04ceffenAuTYaqlppawX6`
- Date: 2026-09-22 ~18:34 +0800
- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verified `cat .git/HEAD` → `ref: refs/heads/codex/nbpolar-phase0`): `codex/nbpolar-phase0`
- Scope: AGENTS.md §3 Pre-RESULT — plan semantics (TASK_PACKET.md) verified against
  **artifacts only**. Narrative records (`STATUS.yaml`, `G3_ADJUDICATION.md`,
  `docs/decision-log.md`, `docs/nbpolar/STATE.md`, `.workbuddy/memory/*`,
  `CURRENT_TASK.md`) were treated as UNDER CORRECTION and are not evidence.
  `G3_PROCESS_DEVIATION.md` was cited for process facts only; Pre-EXECUTE was
  not re-audited (prior verdict `PRE_EXECUTE_MISSING` stands).

**This review verifies plan semantics against artifacts only. It does not cure
the missing Pre-EXECUTE review and does not authorize publication, citation of
NBPOLAR_M2_PRIOR_G3_SUCCESS, or any M2 promotion.**

Evidence base: `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/`
(`g3_summary.json`, `per_block_outcomes.jsonl`, `run_log.md`, `cal_ids.json`,
`g3.json`, `input/g3_freeze_config.json`),
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/g3_freeze_config.json`,
`TASK_PACKET.md`, `scripts/m2_prior_validation.py` (constants),
`comparison_bench/tests/test_nbpolar_m2_g3_confirm.py` (static inspection only;
no test run). No raw-data reads; no files outside the G3 output root were read
as data.

## 1. Frozen plan thresholds vs artifacts — PASS (with comment C1)

Command: `python3 -c` loading the packet freeze config; `grep -n` runner
constants; `python3 -c` loading `g3_summary.json` construction/contract.
Recomputed values (freeze):
`B_tail` 0.0002 (= 2.0e-4) ✓; `delta_min` 0.02 (= 0.020) ✓;
`pairing_window_primary` 200 ✓; `pairing_window_sensitivity` 500 ✓;
`mod_boundary` "CIRCULAR" ✓; `skip_frames` 702 ✓; `tag_master` 2026110101 ✓;
`g2_blocks` 14, `eval_blocks` 14 with exact indices
[2398,2525] [2526,2653] [2654,2781] [2782,2909] [2910,3037] [3038,3165]
[3166,3293] [3294,3421] [3422,3549] [3550,3677] [3678,3805] [3806,3933]
[3934,4061] [4062,4189] ✓;
`g2_arms` [A1_M0_1024f_incumbent, A2_M0_32f_matched, B_M2_32f_candidate] ✓;
`g2_success_rule` "Wilson-lower(B) > Wilson-upper(A2), strict non-overlap,
z=1.96" ✓; fail rule "point(B) <= point(A2)" ✓; inconclusive rule
"point(B) > point(A2) but CIs overlap => bounded negative" ✓; fallback
"COMPLETE-BLOCKS-ONLY, else INSUFFICIENT=>INCONCLUSIVE (never pad/reuse/shrink)" ✓.
N/K1/K2/P16/EVAL_SEED are NOT keys in the freeze (verified absent), but each
is pinned and matching elsewhere: runner `FROZEN_K1 = 319`, `FROZEN_K2 = 6492`,
`G2_N = 32768`, `G3_EVAL_SEED = 2026100101`, `G3_TAG_MASTER = 2026110101` with
in-code asserts `G3_TAG_MASTER == G3_EVAL_SEED + 10000 == 2026110101` and
`128 * 256 == G2_N == 32768` (line 4005); summary construction
`{k1: 319, k2: 6492, n: 32768,
inner_digest: 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b}`
✓; summary contract `{window: 200, mod: CIRCULAR, skip: 702, label: G3,
mode: g3-decode}` ✓. All match the inherited SHG `_1` contract. See C1.

## 2. Disclosure accounting, recomputed — PASS

Command: stdlib-Python sum over all 42 rows of `per_block_outcomes.jsonl`.
Recomputed: `sum(key_dependent_bits)` = **1432998** (claimed 1432998 — match);
`sum(public_control_bits)` = **13765206** (claimed 13765206 — match);
`tag_invoked` rows = **42**; per-row values uniform (key 34119, public 327743
on every row ⇒ 34119×42 = 1432998, 327743×42 = 13765206 exactly);
per-arm key 477666 × 3 arms; per-arm public 4588402 × 3.
`tag_pass` is True on exactly the 8 `exact` rows and False on all 34
`verify_failed` rows (tag ⟺ exact on 100% of rows — correct tag semantics, no
silent pass). `tag_fn_calls` = 2 on every row (84 total; the 42-invocation
count follows the `tag_invoked` rows, consistent with the summary).
`truth_leak_violation`: none. Summary `disclosure_recount.mismatches` = `[]`;
incremental == recount on all three counters. **Recount mismatch: 0.**
Consistency note: 34119/327743 per block are method-specific disclosure
magnitudes, not derivable from N×K (32768×42 = 1376256; 6811×42 = 286062);
they are internally exactly consistent (uniform rows × 42 = summary totals),
which is what the recount gate requires. Leakage semantics are
method-specific per the packet; no cross-method comparison is licensed here.

## 3. `undetected` isolation — PASS

Command: stdlib-Python scan of all 42 rows. Recomputed: `outcome ==
'undetected'` rows = **0**; `undetected` flag true = **0**; distinct outcome
values across all rows = exactly `['exact', 'verify_failed']` — no
`decode_failed`, no `resource_abort`, no `nonfinite` (all three counters 0),
`l1_decode_failed` 0, `l2_decode_failed` 0, `oracle_error` 0. `exact` boolean
flag agrees with `outcome == 'exact'` on all 42 rows. No `status`-like field
exists on any row (field scan for `status`/`ok`: none), so no status value
could have been or was converted to `ok`. `undetected` appears only as a
zero-valued isolated counter in row outcomes and summary arm outcomes; it is
never merged into success or any denominator. **Zero occurrences, isolated.**

## 4. Per-block breakdown, denominator, COMPLETE-BLOCKS-ONLY — PASS

Command: `Counter((arm, outcome))` + `Counter(arm)` over the 42 rows.
Recomputed: A1_M0_1024f_incumbent 14 rows (verify_failed 14);
A2_M0_32f_matched 14 rows (verify_failed 14); B_M2_32f_candidate 14 rows
(exact 8, verify_failed 6). Denominator **14 per arm** ✓. All 14 freeze
`eval_blocks` ranges are 128 frames each (2398–4189 contiguous, disjoint —
closure `disjointness_all_disjoint: true`, full zero-overlap matrix in the
packet freeze copy); every row carries `n = 32768`. No padding/reuse/shrink:
42 rows = 3 arms × 14 complete blocks, no short/duplicate block indices.

## 5. Gate arithmetic, recomputed to full precision — PASS

Command: stdlib-Python Wilson (z=1.96) from item-4 counts (k=8 and k=0, n=14).
Recomputed: B 8/14 lower = **0.3259026690286935**, upper =
**0.7861949006959947**, p̂ = 0.5714285714285714; A2 0/14 lower =
**0.0000000000000000**, upper = **0.2153170119271814**, p̂ = 0.0.
**`lower(B) > upper(A2)` strictly: True** (margin 0.11058565710151211) —
preregistered SUCCESS rule met. Summary `gate` block matches to 1 ulp
(B [0.3259026690286936, 0.7861949006959948], A2 [0.0, 0.21531701192718142];
verdict SUCCESS) — scientifically identical (see C5). A1 (0/14, all
`verify_failed`) carries outcomes only in every artifact and is labeled
descriptive with **no gate** in run_log, summary, and the packet — confirmed
gateless.

## 6. Plan-specified semantics — PASS

Commands: Python checks over rows/run_log/summary; `grep` runner seeds;
G2-freeze tag comparison; artifact mtimes.
- One-shot: single decode-evidence mtime cluster 17:50:13.789–17:50:13.798
  (per_block, summary, cal_ids, run_log); `reruns`/`g3_runs` counters live in
  STATUS (under correction, not cited as evidence); no second-run files exist.
- Budget: wall **858.4991674423218 s ≤ 900**, RSS **1.1271095275878906 GiB ≤
  2**, `budget_aborted: false` (summary timing) ✓.
- Participation disclosure: exact sentence ("decoder/model independence, NOT
  no-prior-contact independence") present on **42/42 rows** + run_log +
  summary ✓.
- `G3_NLL_DOMAINS`: `nll_l2_trueH_domain` =
  "polar-transformed u1 (isolated oracle view; NOT the operational domain)" on
  42/42 rows; `nll_l2_candH_domain` = "untransformed high_hat (operational
  view; hard L1 candidate)" on 42/42 rows ✓ — correct u1-vs-high_hat
  distinction, matching the G2 diagnostic.
- `oracle_l2_exact == 1` count = **0/42**; operational `hard_l2_exact == 1` =
  8/8 on B-exact blocks (repeats the G2 domain note; gate uses operational
  path + tag only) ✓.
- Seed/tag freshness: G3 `tag_master` 2026110101 / `EVAL_SEED` 2026100101
  (runner asserts + freeze + summary); G2 freeze `tag_master` = **2026103001**
  — distinct, no reuse ✓.
- Phase-0 tests exist (26 `def test` functions, fake-seam header, mtime
  17:20:04 pre-decode; static inspection only, no run).

## 7. Leakage-formula hook — PASS (absence stated as a finding)

Command: `grep -rho` for `H(q)|H(X|Y)|f_FER|leakage|efficiency|beta_eff|
secret key|net key` over the G3 output root. Exactly one distinct match, in
`g3.json`/`g3_summary.json` caveats: "…state it in any
rate/efficiency/leakage sentence. M2 is a CANDIDATE, never the baseline."
**No `H(q)` → empirical `H(X|Y)` substitution and no `f_FER` term appear in
any artifact.** What the artifacts expose for future leakage work (raw hooks
only): per-row `key_dependent_bits`, `public_control_bits`,
`floor_logloss_bits` (present 42/42; sample B-exact row: -0.0),
`n_raw_zero_hits`, `n_floor_lifted`, and the exact disclosure totals from
item 2. Absence of a leakage formula is recorded here as a finding, not a
failure — the packet's measurement set does not include one.

## 8. First-contact / provenance — PASS

Commands: `stat` mtimes; `python3 -c` closure fields; `git status
--porcelain -- results/ comparison_bench/outputs_comparison/` + `find
-newermt`.
- Freeze mtime 17:00:07.338 < decode mtime 17:50:13.789 ✓ (packet freeze
  config; input bootstrap snapshot 16:59:19).
- No code modified after the decode: runner 17:17:02, test file 17:20:04 —
  both pre-decode ✓. (Post-freeze code drift is Pre-EXECUTE territory and out
  of scope here.)
- No writes under `results/` or `comparison_bench/outputs_comparison/`
  (porcelain shows only the known pre-existing stat-dirty
  `test_fixtures/real_polar_max_pie_grid.csv`; `find -newermt 2026-09-22
  16:00` empty) ✓.
- Phase-A closure decoder-free: `g3.json` `mode: closure-only`, wall 29.28 s,
  census σ = **114.43029692866367** (center 50, status ok), reproduction
  verdict REPRODUCED, `n_eval_blocks` 14 ✓.

## Explicitly out of scope (not decided here)

- Whether the 17:50:13 run is **admissible** given the missing Pre-EXECUTE
  review — main-thread + PI decision; nothing in this file grants it.
- Promotion of M2 / the `VALIDATED_AT_FROZEN_CONTRACT` string — not mine to
  grant or deny.
- This review does not mark R1/R2, flip any STATUS gate, or adopt
  `NBPOLAR_M2_PRIOR_G3_SUCCESS`.

## Non-blocking comments (no rerun for any)

- C1: the packet freeze config omits N/K1/K2/P16-digest/EVAL_SEED (verified
  absent as keys); all five are pinned and matching in runner constants +
  summary construction. Recommend echoing them in future freeze configs.
- C2: `g3_summary.json` does not echo `tag_master`/`EVAL_SEED`; freshness is
  established by freeze + runner asserts. Recommend echoing in future
  summaries.
- C3: `input/g3_freeze_config.json` (19 keys, 16:59 bootstrap) vs packet
  `g3_freeze_config.json` (21 keys, 17:00 closure output with `eval_blocks` +
  full disjointness matrix) is an expected input→output enrichment; the other
  18 shared keys are equal. Not a freeze mismatch.
- C4: `tag_fn_calls` = 2 on every row (84 total) while `tag_invocations` = 42
  follows the `tag_invoked` rows; recommend documenting the 2-calls-per-block
  convention in the next packet.
- C5: summary Wilson bounds differ from the stdlib recompute by 1 ulp
  (library float formatting); gate margin is 0.1106 — unaffected.
- C6: `l1_exact == 1` on 22/42 rows while block-`exact` holds on 8/42;
  L1-exact does not imply block-exact. The `outcome` taxonomy field is
  authoritative and fully consistent (`tag_pass` ⟺ `exact` on all rows).

## Verdict: PASS_WITH_COMMENTS

All eight items pass on artifact evidence with independently recomputed
values (disclosure 1432998/13765206/42 with recount mismatch 0; undetected 0
isolated; 14/arm denominators; Wilson B [0.3259026690286935, 0.7861949006959947]
vs A2 [0.0, 0.2153170119271814] with strict non-overlap, margin 0.1106;
budget 858.5 s / 1.13 GiB; disclosure + NLL-domain labels on 42/42 rows;
G3-fresh seeds distinct from G2; freeze-before-decode ordering; clean
write-scope). Six non-blocking comments above, none requiring rerun. This
verdict covers plan-semantics-against-artifacts only; it leaves the
PRE_EXECUTE_MISSING finding, admissibility, and any promotion decision
entirely untouched.
