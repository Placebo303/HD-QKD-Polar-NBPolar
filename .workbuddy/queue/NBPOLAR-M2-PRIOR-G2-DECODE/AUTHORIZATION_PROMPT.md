# AUTHORIZATION — NBPOLAR-M2-PRIOR-G2-DECODE
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-G2-DECODE (Tier-Y one-shot three-arm decode on SHG `_1`,
w=200 / CIRCULAR) on branch `codex/nbpolar-phase0` in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/TASK_PACKET.md` and the freeze
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze.md` (implementing
`openspec/changes/nbpolar-prior-rebaseline/` **T6 + T7**). M2 is a CANDIDATE, never "baseline".

A. Authorized work (Tier-Y, one-shot; phases in this order):
   - Phase 0: implement the `--stage-g2-decode` body in `scripts/m2_prior_validation.py` per Spec 1
     (preserving every Stage-1/G1R2 guard) + focused tests per Spec 2 — **synthetic fixtures and
     fake runner only; no production decode from tests**.
   - Phase A: freeze closure — emit `g2_freeze_config.json` with every TO-FREEZE non-null, plus the
     four closure keys (1024-frame A1-CAL, 32-frame CAL32, HELDOUT, disjointness) at w=200 / CIRCULAR / skip-702.
   - **Pre-EXECUTE: independent review PASS + this authorization recorded BEFORE any decode.**
   - Phase B: ONE-SHOT three-arm decode — A1 = M0 at its own 1024 sacrificed frames (incumbent
     as-deployed reference, no gate), A2 = M0 at matched 32 frames (prior-form control),
     B = M2 CANDIDATE at matched 32 frames — at frozen K1=319/K2=6492, frozen P16 construction +
     orders (digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), N=32768,
     on the 14 preregistered EVAL blocks (post-skip frames 2398–4189), one 64-bit Toeplitz tag per
     block from tag_master 2026103001, then the preregistered Wilson gate.
   - Pre-RESULT: independent review PASS before any publication/commit.
   Touches: `scripts/m2_prior_validation.py` (only code file), `comparison_bench/tests/test_nbpolar_m2_g2_decode.py`,
   `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/` (canonical; the alternate
   `…/20260113_SHG_Type2PPLN_3s/g2/` spelling is withdrawn), packet `g2_freeze_config.json` + `STATUS.yaml`
   (ids/counters/artifacts). Touches nothing under `src/`, `experiments/`, `tools/`, `results/`,
   `comparison_bench/outputs_comparison/`, `formal_ir/nbpolar/`; never modifies `sc.py`/`algebra.py`/`transform.py`.
   No SHG `_2` read. No writes outside `workspace/`.

B. Explicitly NOT authorized: G2 rerun or tuning after a verdict; any K increase or re-split
   (D4 DEFERRED); construction re-derivation; M1 pooling; G3 / SHG `_2`; any FER/efficiency/
   qualification/promotion claim; any post-freeze threshold/seed/K/window/MOD change; padding,
   reusing or borrowing CAL/EVAL frames; any Pre-EXECUTE/Pre-RESULT gate self-approval.

Constraints (binding): budget ≤ 900 s wall / 2 GiB RSS single-threaded (exceeded ⇒ STOP, record as
blocker, no tuning to fit); δ-tail FAIL ⇒ no proceed; any FORBIDDEN touch ⇒ STOP + blocker; every
TO-FREEZE non-null (null/absent ⇒ hard error, never a default); verdict rendered ⇒ no rerun/tuning;
ambiguity ⇒ STOP and report. Reporting: per-ID PASS (G2-0, G2-A, G2-1..G2-4, R1, R2) with evidence
paths + logs + gate arithmetic + scoped `git status`; or concrete blocker with failing command, exact
error, remedies, and the SINGLE decision needed. No decision-log / memory / index updates in-packet
(milestone batch).

AUTHORIZED BY: <name> — <date> — freeze_and_implementation_authorized: true (T6) / execution_authorized: true (T7, one-shot) / decoder_modification: false
