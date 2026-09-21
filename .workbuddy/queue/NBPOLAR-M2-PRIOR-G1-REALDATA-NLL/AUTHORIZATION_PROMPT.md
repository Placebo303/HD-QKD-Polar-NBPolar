# AUTHORIZATION — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-G1-REALDATA-NLL on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/TASK_PACKET.md` and the freeze
`.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md`.
M2 is a CANDIDATE, never the baseline. G1 is DESCRIPTIVE / NON-CLAIM and DECODER-FREE.

A. Authorized work (three phases, in this order):
   - Phase 0: implement the `--stage-g1-nll` runner body + `--closure-only` flag per Spec,
     with synthetic-fixture/fake-runner tests only; NO data contact.
   - Phase A: freeze closure on SHG `_1` (`20260113_SHG_Type2PPLN_3s`) — ONE decoder-free
     framing pass reproducing the 2026-09-21 census (alignment + (N)-w=500 pairing),
     skip-702, segment lists, disjointness matrix, filled freeze-config JSON.
   - Phase B: G1 execution on SHG `_1` (G1-1..G1-4) + remainder-population NLL/H check —
     decoder-free, preregistered gates only. Phase B runs ONLY after the main thread
     records an independent freeze review PASS; a review FAIL blocks Phase B.
   Acceptance IDs: G1-0, G1-A, G1-1, G1-2, G1-3, G1-4.
   Touches: runner `scripts/m2_prior_validation.py` (only code file), tests,
   `workspace/m2_prior_validation/**` outputs, this packet's STATUS + freeze-config JSON.
   Touches nothing under `src/`/`experiments/`/`tools/`/`results/`/`comparison_bench/outputs_comparison/`
   or `formal_ir/nbpolar/`. No SHG `_2` read. No decoder call. No protected read outside SHG `_1`
   and the already-derived frozen-session artifacts.

B. Explicitly NOT authorized: G2 execution or G2 freeze closure beyond `g1_freeze.md`;
   G3; any FER/efficiency/qualification/promotion claim; any K decision; any construction
   re-derivation; any post-freeze threshold/seed/K/window change; any pooled-M1 CAL;
   any rerun/tuning after a gate verdict.

Constraints (binding): forbidden list + stop rules + budgets per TASK_PACKET
(Phase A ≤ 300 s; Phase B ≤ 600 s / 2 GiB per acquisition, single-threaded; exceeded ⇒ STOP).
Reporting: per-ID PASS with evidence paths + logs; or concrete blocker with failing command,
exact error, remedies, and the SINGLE decision needed. No decision-log / memory / index
updates in-packet (milestone batch).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — phase0_phaseA_authorized: true / phaseB_authorized: true (gated on recorded freeze-review PASS) / execution_of_decoder: false (G1 is decoder-free)
