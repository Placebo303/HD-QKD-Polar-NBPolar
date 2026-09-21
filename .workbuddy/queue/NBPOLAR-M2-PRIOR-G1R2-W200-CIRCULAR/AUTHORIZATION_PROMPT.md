# AUTHORIZATION — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/TASK_PACKET.md` and the delta
`.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1r2_delta.md` (delta-successor of the
executed and adjudicated G1 contract; everything not listed as CHANGED there is INHERITED;
the delta lists **8** CHANGED items, item 8 being the runner re-parameterization).
M2 is a CANDIDATE, never the baseline. This packet is G1-scope: DESCRIPTIVE / NON-CLAIM and
DECODER-FREE.

A. Authorized work (two phases, in this order):
   - Phase A: freeze closure on SHG `_1` (`20260113_SHG_Type2PPLN_3s`) — ONE decoder-free
     framing pass reproducing the 2026-09-21 census alignment + (N) w=200 pairing,
     skip-702, the inherited segment ranges, the four closure keys, and the complete
     19-key `g1r2_freeze_config.json`.
   - Phase B: G1-scope execution on SHG `_1` (G1R2-1..G1R2-4: alignment; pairing + δ-profile
     linear AND circular; CAL32 FIT + matched-CAL held-out NLL; H1/H2/H_total both models +
     both gate verdicts with U/Δ arithmetic) + the remainder-population NLL/H check
     (frozen derived pairs, no gate). Phase B runs ONLY after the main thread records the
     independent closure-verification PASS; a FAIL blocks Phase B.
   Acceptance IDs: G1R2-A, G1R2-1, G1R2-2, G1R2-3, G1R2-4, G1R2-R.
   Touches: `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/` +
   `workspace/m2_prior_validation/remainder_101f_g1r2/` outputs; this packet's `STATUS.yaml`
   (counters/artifacts/ids only) + `g1r2_freeze_config.json`. The runner re-parameterization
   (delta item **8**) is ALREADY APPLIED and separately reviewed — the operator must NOT modify
   `scripts/m2_prior_validation.py` any further (its inherited mechanics stay untouched). Touches nothing under
   `src/`/`experiments/`/`tools/`/`results/`/`comparison_bench/outputs_comparison/` or
   `formal_ir/nbpolar/`. No SHG `_2` read. No decoder call. No protected read outside SHG `_1`
   and the already-derived frozen-session artifacts.

B. Explicitly NOT authorized: G2 execution or G2 freeze closure; G3; any FER/efficiency/
   qualification/promotion claim; any K decision; any construction re-derivation; any
   post-freeze threshold/seed/K/window/MOD change; any pooled-M1 CAL; any rerun/tuning after a
   gate verdict; any modification of the runner or of the G1 contract's inherited values.

Constraints (binding): budgets and stop rules per TASK_PACKET (Phase A ≤ 300 s;
Phase B ≤ 600 s / 2 GiB per invocation, single-threaded; exceeded ⇒ STOP, no tuning;
reproduction mismatch ⇒ STOP loudly; runner modification need ⇒ STOP and report).
Reporting: per-ID PASS with evidence paths + gate arithmetic + run logs + scoped `git status`;
or concrete blocker with failing command, exact error, remedies, and the SINGLE decision needed.
No decision-log / memory / index updates in-packet (milestone batch).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — phaseA_authorized: true / phaseB_authorized: true (gated on recorded closure-verification PASS) / execution_of_decoder: false (G1 scope is decoder-free)
