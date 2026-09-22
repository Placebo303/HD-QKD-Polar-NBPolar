# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-G3-CONFIRM (gated: only if the G2 adjudication ADOPTS M2)

**PRECONDITION**: dispatch only after the main thread confirms the G2 adjudication ADOPTED M2 (SUCCESS).
If G2 is FAIL or INCONCLUSIVE, this packet is VOID — STOP and report; do not touch SHG `_2`.
Do NOT redesign. Do NOT guess. Ambiguity ⇒ STOP and report (second return condition). M2 remains a CANDIDATE
until G3 passes.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD`. Else STOP.
- Venv: `/home/karel_303/.venvs/timetagger/bin/python`
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/TASK_PACKET.md` (authoritative).
- NEVER modify `sc.py`/`algebra.py`/`transform.py`/`prior_m2.py` or anything under `formal_ir/nbpolar/`, `src/`,
  `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`.
  **NEVER touch SHG `_2` before this packet's Phase-A closure.** No writes outside `workspace/` + the runner file
  + the G3 test file + packet STATUS/config.

## 1. Phase 0 (synthetic; no data, no decode)

Implement the additive G3 stage/body in `scripts/m2_prior_validation.py`, preserving every Stage-1/G1R2/G2 guard
(`--authorized` store_true, 19-key enforcement, flag↔key cross-checks, K pin 319/6492, out-root confinement,
import purity). Reuse the frozen P16 construction + orders (digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), N=32768, chunk_rows 512, floor 1e-15,
64-bit Toeplitz tag from tag_master 2026110101; per-arm priors via `build_m0_joint` / `fit_m2_triple`→`build_m2_joint`
(CIRCULAR) and the UNCHANGED frozen layer factorization. Tests `comparison_bench/tests/test_nbpolar_m2_g3_confirm.py`:
fake runner only, never production decode from tests; cover the Wilson gate and the closure rules.

## 2. Phase A (first permitted SHG `_2` contact; decoder-free)

Derive alignment by the **INHERITED** method (scan_range 409600, bin 100, accept `status==ok AND peak_to_bg>=10`
+ yield-sweep self-check; never inherit an offset VALUE) and **reproduce the census σ ≈ 114.4 ps** — mismatch
⇒ STOP loudly (ALIGN_INCONSISTENT). Pair at W_P=200, apply skip-702, enumerate the post-skip ledger, allocate
A1-CAL / CAL32 / CHAR / HELDOUT / EVAL / RESERVE with **target 14 complete 128-frame EVAL blocks**
(COMPLETE-BLOCKS-ONLY; if < 14 ⇒ record INSUFFICIENT ⇒ INCONCLUSIVE; never pad/reuse/shrink N). Emit the closure
keys + `g3_freeze_config.json` (all TO-FREEZE non-null). Budget ≤ 300 s / 2 GiB.

## 3. STOP — do not decode

Return Phase 0 + A results. Phase B decodes ONLY after an independent Pre-EXECUTE PASS and the main thread's
recorded authorization.

## 4. Phase B (after authorization)

ONE-SHOT three-arm decode on the frozen EVAL blocks at K1=319/K2=6492, tag_master 2026110101; record the full
measurement set (`l1_exact`/`hard_l2_exact`/`oracle_l2_exact`/`pair_exact`; first-error coordinate AND layer; raw
zero-count hits; floor hits + log loss; true-H and candidate-H L2 NLL; taxonomy with `undetected` isolated;
disclosure recount; wall/RSS; SC/tag counts); apply Wilson (SUCCESS iff Wilson-lower(B) > Wilson-upper(A2);
FAIL iff point(B) ≤ point(A2); INCONCLUSIVE iff point(B) > point(A2) with overlap). A1 has no gate.
**Every output must carry the G3 participation disclosure** (decoder/model independence, NOT no-prior-contact
independence).

## 5. Return (exactly two)

1. All-complete: per-ID PASS (G3-0, G3-A; later G3-2..G3-4, R1) with evidence paths + logs + gate arithmetic +
   scoped `git status`. For Phase 0 + A: state explicitly that Phase B is NOT run.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed.

## Stop rules

Budget ≤ 900 s / 2 GiB single-threaded (decode); exceeded ⇒ STOP (no tuning). Any SHG `_2` contact before Phase-A
closure ⇒ STOP + blocker. Alignment reproduction mismatch ⇒ STOP loudly. Verdict ⇒ no rerun/tuning.
No decision-log / memory / index / parent-packet STATUS updates.
