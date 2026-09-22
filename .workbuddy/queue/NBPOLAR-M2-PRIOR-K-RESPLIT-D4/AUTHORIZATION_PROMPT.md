# AUTHORIZATION — NBPOLAR-M2-PRIOR-K-RESPLIT-D4
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-K-RESPLIT-D4 on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-K-RESPLIT-D4/TASK_PACKET.md`.
This is a **no-protected-data-contact, synthetic-only** planning-input packet (per the packet's SCOPE
CLARIFICATION 2026-09-22 — synthetic genie TRAIN on model-sampled blocks IS permitted; protected/real reads and
protected decoder/genie/SC remain forbidden; the earlier "decoder-free" label was withdrawn as contradictory):
it derives and REPORTS the D4
fixed-f vs fixed-K_total branches and the frozen-selector (K1,K2) for each. **It ADOPTS NEITHER.**

A. Authorized work: recompute both branch arithmetics in-packet (N=32768, M2 H_total = 0.8168138204133305,
   budget literal `K_total = floor((f·N·H − 64)/5)`; fixed-f=1.3 branch; fixed-K branch f for candidate
   K_total 6811 / 6946 / 7020); derive (K1,K2) per branch via the **frozen**
   `select_empirical_split` (imported from `nbpolar.empirical_genie_scaling`, never reimplemented) on
   **16 synthetic TRAIN blocks** at preregistered seeds 2026100101…2026100116; write
   `workspace/m2_prior_validation/k_resplit_d4/{report.md,results.json,run_log.md}` + focused tests
   `comparison_bench/tests/test_nbpolar_m2_k_resplit.py`; packet STATUS (ids/counters/artifacts only).
   Acceptance IDs: D4-A, D4-B, D4-C, D4-D.
   Touches nothing under `src/`, `experiments/`, `tools/`, `results/`,
   `comparison_bench/outputs_comparison/`, `formal_ir/nbpolar/`; does not modify
   `scripts/m2_prior_validation.py` or `prior_m2.py`. No real/protected data read. No decoder/genie/SC
   call on protected data (synthetic-only; test-only calls use a fake runner).

B. Explicitly NOT authorized: adopting or deciding fixed-f vs fixed-K (remains a later preregistered
   decision); any change to G2's frozen K (319/6492) or to any frozen constant; any real-data read; any
   decode; any construction re-derivation; any FER/efficiency/qualification claim; re-running G1/G1R2/G2;
   using H-proportional split as a selection rule (descriptive contrast column only, clearly labelled).

Constraints (binding): stop rules per TASK_PACKET — any real-data read or protected decoder/genie/SC call
⇒ STOP + blocker; if the frozen selector requires SC/genie to build e/h vectors ⇒ STOP and report rather
than improvising. Reporting: per-ID PASS with evidence paths + the two-branch table + `git status` snippet;
or concrete blocker with failing command, exact error, remedies, and the SINGLE decision needed.
No decision-log / memory / index updates in-packet (milestone batch).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <date> — derivation_authorized: true (report-only; no adoption) / real_data_contact: false
