# G3 MAIN-THREAD ADJUDICATION — NBPOLAR-M2-PRIOR-G3-CONFIRM (2026-09-22)

Label: `NBPOLAR_M2_PRIOR_G3_SUCCESS` — Tier-Y one-shot three-arm confirmation decode on SHG `_2`
(independent session; D6 gate G3).
**Verdict: SUCCESS** — the M2 ±1 CANDIDATE's independent-session confirmation PASSED.

## 1. Basis (Tier-Y authorization chain — R2 closes G3-1 here)

1. User authorization pasted verbatim (kai, 2026-09-22) while the packet precondition (G2 SUCCESS) was unmet →
   **HELD**: not dispatched, SHG `_2` untouched (recorded in STATUS `authorization_hold_note`).
2. G2 adjudicated `NBPOLAR_M2_PRIOR_G2_SUCCESS` → precondition MET → held authorization OPERATIVE
   (`precondition_status: MET`), recorded in STATUS before any G3 dispatch.
3. Independent **Pre-EXECUTE PASS_WITH_COMMENTS** (12/12 checklist; zero blocking) — completed BEFORE the
   `--stage-g3-decode` body existed, covering Phase-0/A code, closure artifacts, guards, decoder-free AST pin.
4. Focused **DELTA_PASS** on the decode body (zero blocking; scope notes a/b/c ruled acceptable-or-correct;
   `g2_arms` faithful) — completed BEFORE the one-shot run.
5. **One-shot execution**: decode artifacts mtime 17:50 (2026-09-22); every review above and the recorded
   authorization precede it. `g3_runs: 1`, `reruns: 0`, single closure→decode mtime sequence (16:59→17:00→17:50),
   no second-run evidence.
6. Independent **Pre-RESULT PASS_WITH_COMMENTS** (all 10 items recomputed from artifacts; zero blocking;
   publication/commit MAY PROCEED).

Counterfactual check: had G2 returned FAIL/INCONCLUSIVE, this packet was VOID and SHG `_2` would have remained
untouched. That path was never taken.

## 2. Result

| Arm | Prior / CAL | exact | Wilson 95% (n=14, z=1.96) | Gate role |
|---|---|---:|---|---|
| **B** | M2 CANDIDATE @ matched 32f | **8/14** | **[0.3259026690, 0.7861949007]** (p̂=0.5714285714) | candidate |
| **A2** | M0 @ matched 32f | **0/14** | [0.0, 0.2153170119] (p̂=0.0) | comparator |
| **A1** | M0 @ own 1024f (incumbent) | **0/14** (all `verify_failed`) | — | descriptive, **no gate** |

**SUCCESS**: Wilson-lower(B) = 0.3259 > Wilson-upper(A2) = 0.2153 — strict non-overlap, preregistered rule,
independently recomputed bit-exact by the Pre-RESULT reviewer.

Integrity facts (all independently verified):
- `undetected` = 0/42, isolated (never merged); taxonomy = {exact 8, verify_failed 34}; no
  `decode_failed`/`nonfinite`/`resource_abort`.
- Disclosure recount mismatch 0: key 1,432,998 = 34,119 × 42; public 13,765,206 = 327,743 × 42; 42 tags from
  **tag_master 2026110101** (G3-fresh, distinct from G2's inherited 2026103001; runner constant +
  drift-refused test + both freeze files).
- Budget: per-block wall 19.38–20.13 s; total **858.5 s ≤ 900**; RSS 1.13 GiB ≤ 2; 126 SC (3/block × 42);
  `budget_aborted: false`.
- Contract: frozen K1=319/K2=6492, P16 digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  (orders len 32768), W_P=200/W_S=500/CIRCULAR/skip=702, EVAL 2398–4189 = 14 blocks, segments all-disjoint,
  acq `20260113_SHG_Type2PPLN_3s_2` only, census repro σ = 114.43029692866367 bit-exact (center 50, ok),
  ledger 4289 (242 dropped).
- Every row stamped with `G3_NLL_DOMAINS` labels (true-H on polar-transformed `u1` isolated-oracle view;
  cand-H on untransformed `high_hat` operational view) + participation disclosure; caveats (a)–(d) in
  summary/run_log; "M2 is a CANDIDATE, never the baseline".

## 3. Adjudication

1. **G3 SUCCESS is adopted.** The preregistered independent-session Wilson gate was met on the first (and only)
   verdict-bearing execution; no rerun, no tuning, no seed/threshold/K/window/MOD change.
2. **What this establishes**: at frozen K and frozen P16 construction, under the inherited w=200/CIRCULAR
   contract on a **second, independent SHG session**, the M2 ±1 CANDIDATE again restores complete blocks where
   the matched-CAL M0 control restores none (8/14 vs 0/14, strictly non-overlapping CIs), with `undetected`
   isolated, disclosure recount exact, and G3-fresh tag provenance. The G2 result (11/14 vs 0/14 on SHG `_1`)
   was therefore not a single-session accident.
3. **M2 status — state transition per the PRE-REGISTERED ladder** (`docs/nbpolar/STATE.md` §4.1, main-thread
   ruling written BEFORE the decode; semantics pre-write `G3_ADJUDICATION_PREWRITE.md` §9 present at G3-1 —
   presence check satisfied): the ladder defines `CANDIDATE → (G3 preregistered-gate PASS)
   VALIDATED_AT_FROZEN_CONTRACT`. The G3 preregistered Wilson gate PASSED on the one-shot execution, so the entry
   condition is met and **M2 transitions from `CANDIDATE` to `VALIDATED_AT_FROZEN_CONTRACT`** as of this
   adjudication (2026-09-22). This is the SECOND rung only: the ladder's later rungs are NOT met —
   `FER_MEASURED_AT_CONTRACT` requires the R2 preregistered FER gate + sample size; `EFFICIENCY_ACCOUNTED`
   requires R3; `READY_FOR_QUALIFICATION` requires ≥2 independent-session replication + sample + G4 exhaustive
   public-message inventory + independent Pre-RESULT all-pass. No level-skipping, no synthetic-S9 promotion, no
   cross-contract narrative promotion (§4.1 binding). Final rebaseline completion still requires **G4** and the
   OpenSpec archive; nothing here pre-empts those. Status string used: `NBPOLAR_M2_PRIOR_G3_SUCCESS` exactly as
   preregistered in the §4.1 three-state table (no invented label).
4. **What this does NOT establish** (binding): no FER-as-population estimate; no efficiency, qualification,
   promotion, or composable net-key claim; **no cross-session superiority** reading of 11/14 vs 8/14 (different
   sessions, each gate evaluated on its own CI — the correct claim is replication of the *direction*, not
   comparability of magnitudes); no cross-contract comparison vs G1 (w=500/LINEAR, its own bounded negative);
   q_rest = 0 remains weak at a 32-frame CAL (zero-observation bound 3/8192 = 3.66e-4) with the no-misread rule;
   w=200 keeps a timing-truncated population — must be stated in any future rate/efficiency/leakage sentence;
   the far-offset accidental baseline is structured, not uniform.
5. **A1 = 0/14 on both sessions** is a descriptive first measurement of the incumbent as-deployed regime —
   NOT a benchmark claim, NOT a failure of the incumbent proof.
6. **NLL domain semantics carried forward**: `oracle_l2_exact` = 0/42 with operational `hard_l2_exact` 8/8 on
   B-exact blocks repeats the G2 domain note; domains are now labeled per row, so future NLL statements must
   cite the label, not an implicit "H".

## 4. Provenance / traceability notes (Pre-RESULT comments, recorded here)

- **tag_master traceability**: `g3_summary.json` does not echo `tag_master`/`EVAL_SEED`; G3-freshness
  (2026110101 / EVAL_SEED 2026100101) is established by `g3_freeze_config.json` (both copies), STATUS, runner
  constants (`G3_TAG_MASTER`, `G3_EVAL_SEED`), and the drift-refused test. Recommend echoing both fields in
  G4-era summaries; **no rerun**.
- **input-vs-closure freeze files**: `input/g3_freeze_config.json` (19-key bootstrap) vs packet
  `g3_freeze_config.json` (21-key closure output with `eval_blocks` + full matrix) — expected
  input→output relationship; all shared keys equal. NOT a freeze mismatch.
- **Execution provenance**: the chat dispatch contained a venv path typo (`timetetagger`) that exists in no
  repo file; the operator used the STATUS-mandated venv (same interpreter as all prior stages) and the exact
  shell command is not logged in-repo — provenance rests on freeze + code pins + artifact consistency, which
  the reviewer assessed sufficient and non-material.
- **Diagnostic carry-forward**: `oracle_l2_exact` 0/42 across arms; gate unaffected (frozen operational path +
  tag + label only).

## 5. Ledger / next gates

- D6 sequence: G1 (bounded negative, own contract) → G1R2 (re-baseline contract established) → **G2 SUCCESS** →
  **G3 SUCCESS** → **G4 pending** (exhaustive public-message inventory; requires its own packet + authorization).
- Re-split: still DEFERRED. D4 report (K_total 6946 @ fixed-f 1.3; f(6811)=1.2747, f(7020)=1.3138;
  splits (335,6611)/(328,6483)/(346,6674)) is planning input only; G2/G3 both ran at frozen 319/6492.
- Consumption: SHG `_1` EVAL 2398–4189 consumed by G2; SHG `_2` EVAL 2398–4189 consumed by G3; RESERVE
  segments (29 / 99) untouched; both sessions remain otherwise unclaimed.
- Milestone batch (decision-log / STATE / index / memory / scoped commit) follows this record — main-thread work.
