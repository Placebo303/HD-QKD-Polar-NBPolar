# AUTHORIZATION — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-REALDATA-VALIDATION on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md`.

A. Implementation (Stage 1 ONLY — decoder-free, no protected reads):
New adapter module beside `formal_ir/nbpolar/prior.py` (never inside `sc.py`), M0-reproducing switch, focused
tests + T0, frozen-`select_empirical_split` re-split path on synthetic fixtures (real-data numbers diagnostic-only),
`docs/SECURITY_MODEL.md` CAL note + inventory skeleton, runner `scripts/m2_prior_validation.py`.
Acceptance IDs: I1, I2, I3, I4. Touches nothing under `src/`/`experiments/`/`tools/`/`results/`.

B. Execution (Stages 2–3 ONLY after A accepted AND per-stage freezes recorded AND independent Pre-EXECUTE PASS
for G2 — G2 additionally needs its authorization line pasted before the run):
1. G1 decoder-free real-data NLL (per acquisition, PRIMARY `.ttbin` only, correlation-derived alignment never
   inherited, frozen (N) window/skip/bound from the G1 freeze):
   `.../bin/python scripts/m2_prior_validation.py --stage-g1-nll --acq-id <ACQ> --out-root workspace/m2_prior_validation/<ACQ> --authorized`
2. G2 one-shot Tier-Y decode, arms A (M0+frozen P16) vs B (M2+frozen P16), matched K1=319/K2=6492, preregistered
   blocks/tag from the G2 freeze, exactly once, no rerun/tuning/seed change:
   `.../bin/python scripts/m2_prior_validation.py --stage-g2-decode --acq-id <ACQ> --arms A,B --blocks <N-FROZEN> --k1 319 --k2 6492 --tag-master <FROZEN> --out-root workspace/m2_prior_validation/<ACQ>/g2 --authorized`

Constraints (binding): forbidden list + stop rules per TASK_PACKET §§3/9; `undetected` never merged; S9 never FER
evidence; no M1 pooling with delay-−50 in CAL; writes ONLY under `workspace/m2_prior_validation/`; no G3,
no construction re-derivation, no claim beyond packet scope in-packet.
Budgets (binding CAP): Stage 2 ≤300 s / 2 GiB per acq; Stage 3 ≤900 s / 2 GiB single-threaded; exceed ⇒ STOP.
Reporting: per-ID (I1–I4, G1-1–G1-4, G2-1–G2-4, R1–R2) PASS/FAIL with evidence paths + run logs. R1 Pre-RESULT
PASS required before any result publication. No decision-log / memory / index updates in-packet (milestone batch).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — implementation_authorized: true/false (Stage 1) / execution_authorized: true/false (Stages 2–3 per freezes + G2 Pre-EXECUTE)
G1 FREEZE REF: <doc + window/skip/bound values> — G2 FREEZE REF: <doc + blocks/tag values>
