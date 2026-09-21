# AUTHORIZATION — NBPOLAR-S11-SHG-TAIL-NATURE
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-S11-SHG-TAIL-NATURE on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/TASK_PACKET.md`.

This is a Tier-X probe (AGENTS.md §10.4): descriptive/non-claim, decoder-free,
zero prior fitting, zero model selection. It consumes no attempt, creates no
candidate/accepted token, and changes no scientific status.

A. Authorized work: ONE decoder-free probe run on SHG `_1`
   (`20260113_SHG_Type2PPLN_3s`, primary `.ttbin` via `FileReader` only) —
   vendored (N) nearest-unique pairing at the frozen constants, arms: W-grid
   {200,500,1000,2000} at the frozen derived offset +50 ps; anchor (w=500,
   skip-702, post-skip frames 1056–1837 = the G1 CHAR segment per the frozen SEG_RANGES (main-thread correction 2026-09-21), must reproduce
   p̂ = 0.0050202 exactly); offset scan {−50, 0, 25, 50, 75, 100} ps at w=500;
   far-offset baseline at 50 ± 409600 ps (w=500); per-frame clustering on the
   anchor. Output ONLY under `workspace/probes/nbpolar_s11_shg_tail_nature/`
   (`prereg.md` before compute, `body.py`, ONE `results.json`).
   Acceptance IDs: S11-P, S11-A, S11-B, S11-C, S11-D, S11-E, S11-R.
   Touches: the probe root + this packet's STATUS.yaml only. Touches NOTHING
   under `src/`/`experiments/`/`tools/`/`results/`/`comparison_bench/outputs_comparison/`,
   nothing under `formal_ir/` or any `.workbuddy` packet dir. No SHG `_2` read.
   No decoder call of any kind. No prior fit, no model selection, no window
   choice after prereg.

B. Explicitly NOT authorized: any prior-form or route decision; any G2/G3 work;
   any real-data decode; any claim (FER/efficiency/qualification/promotion);
   any post-prereg parameter change; any write outside the probe root + packet
   STATUS; any decision-log/memory/index update in-packet (milestone batch).

Constraints (binding): budgets and stop rules per TASK_PACKET (≤ 300 s / 2 GiB
single-threaded; anchor mismatch ⇒ STOP; exceeded ⇒ STOP, no tuning). Reporting:
per-ID PASS with evidence paths + results summary; or concrete blocker with
failing command, exact error, remedies, and the SINGLE decision needed.

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — probe_authorized: true (Tier-X, descriptive/non-claim) / decoder_contact: false
