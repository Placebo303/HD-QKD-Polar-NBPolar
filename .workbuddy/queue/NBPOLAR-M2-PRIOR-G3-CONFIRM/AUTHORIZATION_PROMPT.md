# AUTHORIZATION — NBPOLAR-M2-PRIOR-G3-CONFIRM
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

**PRECONDITION (verified by the main thread before this authorization is requested):** the G2 adjudication
must ADOPT M2 (SUCCESS). If G2 is FAIL or INCONCLUSIVE, this packet is VOID — do not paste this authorization.

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-G3-CONFIRM (Tier-Y independent-session confirmation on SHG `_2`)
on branch `codex/nbpolar-phase0` in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/TASK_PACKET.md`
(D6 gate G3; change `openspec/changes/nbpolar-prior-rebaseline/`). M2 remains a CANDIDATE until G3 passes.

A. Authorized work (Tier-Y one-shot; phases in order):
   - Phase 0: implement the G3 stage/body in `scripts/m2_prior_validation.py` (additive; preserving every
     Stage-1/G1R2/G2 guard) + focused tests `comparison_bench/tests/test_nbpolar_m2_g3_confirm.py` —
     synthetic fixtures and fake runner only; no production decode from tests.
   - Phase A: the FIRST permitted SHG `_2` contact — decoder-free closure: derive alignment by the
     INHERITED method (reproduction check vs census σ ≈ 114.4 ps; mismatch ⇒ STOP loudly), pair at
     W_P=200, skip-702, enumerate the post-skip ledger, allocate A1-CAL / CAL32 / CHAR / HELDOUT /
     EVAL / RESERVE (target 14 complete EVAL blocks; COMPLETE-BLOCKS-ONLY else INSUFFICIENT ⇒
     INCONCLUSIVE), emit the closure keys + `g3_freeze_config.json`.
   - Pre-EXECUTE: independent review PASS + this authorization recorded BEFORE any decode.
   - Phase B: ONE-SHOT three-arm decode (A1 = M0@1024f descriptive / A2 = M0@32f comparator /
     B = M2 CANDIDATE@32f) at frozen K1=319/K2=6492, frozen P16 construction + orders
     (digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), N=32768,
     64-bit Toeplitz tag per block from tag_master 2026110101 (EVAL_SEED 2026100101), then the
     preregistered Wilson gate.
   - Pre-RESULT: independent review PASS before any publication/commit.
   Acceptance IDs: G3-0, G3-A, G3-1, G3-2, G3-3, G3-4, R1, R2.
   Touches: `scripts/m2_prior_validation.py` (only code file), the G3 test file,
   `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/`, packet `g3_freeze_config.json` +
   `STATUS.yaml` (ids/counters/artifacts). Touches nothing under `src/`, `experiments/`, `tools/`,
   `results/`, `comparison_bench/outputs_comparison/`, `formal_ir/nbpolar/`; never modifies
   `sc.py`/`algebra.py`/`transform.py`/`prior_m2.py`. No writes outside `workspace/`.

B. Explicitly NOT authorized: any SHG `_2` contact before this packet's Phase-A closure; re-deriving or
   tuning alignment/window/MOD/skip against SHG `_2` (all INHERITED from SHG `_1`'s frozen rules); model
   selection on SHG `_2`; any K increase or re-split; construction re-derivation; G4 inventory work; any
   FER/efficiency/qualification/promotion claim; any rerun/tuning after a verdict; padding, reusing or
   borrowing frames; any Pre-EXECUTE/Pre-RESULT self-approval.

Constraints (binding): budget ≤ 900 s wall / 2 GiB RSS single-threaded for the decode phase (closure ≤ 300 s);
exceeded ⇒ STOP, record as blocker, no tuning. Alignment reproduction mismatch ⇒ STOP loudly. Every
TO-FREEZE non-null (null/absent ⇒ hard error, never a default). Verdict rendered ⇒ no rerun/tuning.
Ambiguity ⇒ STOP and report. Reporting: per-ID PASS with evidence paths + logs + gate arithmetic +
scoped `git status`; or concrete blocker with failing command, exact error, remedies, and the SINGLE
decision needed. The G3 participation disclosure (decoder/model independence, NOT no-prior-contact
independence) must appear in every output. No decision-log / memory / index updates in-packet.

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <date> — g3_authorized: true (precondition: G2 adjudication ADOPTED M2) / execution_one_shot: true / decoder_modification: false
