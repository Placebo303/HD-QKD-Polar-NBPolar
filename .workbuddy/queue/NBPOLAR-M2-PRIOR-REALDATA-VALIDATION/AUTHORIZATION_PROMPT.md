# AUTHORIZATION — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.)

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-REALDATA-VALIDATION on branch `codex/nbpolar-phase0`
in repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
per `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md`.
M2 is a CANDIDATE, never the baseline. SHG `_2` stays FULLY RESERVED AND UNTOUCHED until its own G3 freeze.

A. Implementation (Stage 1 ONLY — decoder-free, no protected reads):
NEW strict 3-parameter M2 adapter beside `formal_ir/nbpolar/prior.py` (never inside `sc.py`) with explicit frozen MOD
param (S8 all-1024-δ fit SHALL NOT be reused), M0-reproducing switch, focused tests + T0,
frozen-`select_empirical_split` re-split path on synthetic fixtures (real-data numbers diagnostic-only, no K decision),
`docs/SECURITY_MODEL.md` CAL note (32-frame CANDIDATE budget sacrifice, reveal diagnostic, no λ_prior) + inventory
skeleton, runner `scripts/m2_prior_validation.py` with all TO-FREEZE flags. Acceptance IDs: I1, I2, I3, I4.
Touches nothing under `src/`/`experiments/`/`tools/`/`results/`. No SHG `_2` read.

B. Execution (Stages 2–3 ONLY after A accepted AND per-stage freezes recorded AND independent Pre-EXECUTE PASS
for G2 — G2 additionally needs its authorization line pasted before the run):
1. G1 decoder-free real-data characterisation (frozen 101-frame remainder NLL/H-only with frozen pairs, NO decode;
then SHG `_1` PRIMARY `.ttbin` only, correlation-derived alignment never inherited, frozen windows/skip/MOD/char-size
from the G1 freeze, RULE-FIT32-SCORE-HELDOUT, B_tail + Δ_min gates per §5):
`.../bin/python scripts/m2_prior_validation.py --stage-g1-nll --acq-id <ACQ> --window-primary <W_P-FROZEN> --window-sensitivity <W_S-FROZEN> --skip <SKIP-FROZEN> --mod <MOD-FROZEN> --char-pairs <NCHAR-FROZEN> --out-root workspace/m2_prior_validation/<ACQ> --authorized`
2. G2 one-shot Tier-Y decode on SHG `_1` ONLY, arms A1 (M0 at own 1024-frame CAL, incumbent reference, no gate) +
A2 (M0 at matched 32-frame CAL) + B (M2 CANDIDATE at 32 frames), matched frozen K1=319/K2=6492 + frozen P16 order,
same preregistered blocks/tag from the G2 freeze, Wilson-gate per §6, exactly once, no rerun/tuning/seed change:
`.../bin/python scripts/m2_prior_validation.py --stage-g2-decode --acq-id 20260113_SHG_Type2PPLN_3s --arms A1,A2,B --blocks <N-FROZEN> --k1 319 --k2 6492 --tag-master <FROZEN> --window-primary <W_P-FROZEN> --mod <MOD-FROZEN> --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/g2 --authorized`

Constraints (binding): forbidden list + stop rules per TASK_PACKET §§3/9; full §6 measurement semantics with
`undetected` never merged and `resource_abort` separated; S9 never FER evidence; no M1 pooling with delay-−50 in CAL;
writes ONLY under `workspace/m2_prior_validation/`; SHG `_2` never touched; no G3, no K re-split decision,
no construction re-derivation, no claim beyond packet scope in-packet.
Budgets (binding CAP): Stage 2 ≤600 s / 2 GiB per acq; Stage 3 ≤900 s / 2 GiB single-threaded; exceed ⇒ STOP.
Reporting: per-ID (I1–I4, G1-1–G1-4, G2-1–G2-4, R1–R2) PASS/FAIL/INCONCLUSIVE with evidence paths + U/Δ/CI arithmetic
+ run logs. R1 Pre-RESULT PASS required before any result publication. No decision-log / memory / index updates
in-packet (milestone batch).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: <name> — <UTC date> — implementation_authorized: true/false (Stage 1) / execution_authorized: true/false (Stages 2–3 per freezes + G2 Pre-EXECUTE)
G1 FREEZE REF: <doc + W_P/W_S/skip/MOD/NCHAR/B_tail/Δ_min/CAL-split values> — G2 FREEZE REF: <doc + N/tag/W_P/MOD/CAL-IDs values> — SHG_2 STILL RESERVED: <yes + untouched confirmation>
