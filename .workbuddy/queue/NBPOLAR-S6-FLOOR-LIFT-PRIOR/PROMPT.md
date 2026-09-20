# PROMPT — S6 operator (`nbpolar_s6_floor_lift_prior`)

Self-contained. Execute EXACTLY as written; do not redefine requirements. If
anything is unclear or any stop rule fires, STOP and return under condition 2
— do not guess.

## Context

S5 (`workspace/probes/nbpolar_s5_prior_floor_screen/results.json`, already
complete) found on CAL-split-A-fit / split-B-score (seed 20260920): FLOOR_1e-6
has the best held-out NLL (0.8397/0.8488) AND zero spikes, while Laplace-α1 —
the only rule that ever restored blocks (P20N 1/4, P20O 2/5, P20Q 4/5) —
ranks 5th by NLL (~+2.5 bits/symbol worse) because it smears +2.6 bits onto
99.9% of symbols to save ~30–40 bits on ~0.1%. The RAW-vs-FLOOR_1e-6 gap
(0.0240/0.0300) ≈ the spike mass itself. Hypothesis for S6: restoration came
from SPIKE SUPPRESSION, not fit quality, and a pure floor lift achieves it
without Laplace's H1 destruction (0.025 → 4.70) or its construction change
(h2_alt 1.44/1.32). Your job: run the frozen skeleton and report. No analysis
beyond the script's outputs; NO claim.

## Step 1 — Verify (no execution yet)

1. Confirm branch is `codex/nbpolar-phase0` (`git branch --show-current`).
2. Confirm these exist (read-only): the 7 artifacts in `TASK_PACKET.md` §3,
   plus `workspace/probes/nbpolar_s6_floor_lift_prior/prereg.md` and `body.py`.
3. Confirm target-output absence: `workspace/probes/nbpolar_s6_floor_lift_prior/results.json`
   must NOT exist. If it exists, STOP (no-overwrite) and report.
4. Re-run the compile check:
   `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m py_compile workspace/probes/nbpolar_s6_floor_lift_prior/body.py`
   and confirm imports are stdlib+numpy only (S6-A2).

## Step 2 — Execute (ONLY after the main thread confirms user authorization)

Run EXACTLY:
`cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_s6_floor_lift_prior/body.py`

Do NOT edit `body.py`. Do NOT add flags, env vars, or follow-up commands. One
run; if it errors, ONE fix-run for execution errors only is allowed (params
frozen — never change seed/rules/split), recorded in `results.json`.

## Step 3 — Return (condition 1: all-complete)

Report: (a) files created with line counts (`results.json` only, plus its
top-level keys); (b) exact command run; (c) per-variant decisive triples
(spike_symbols, H1_full, H2_full) per session + cross-session NLL stats;
(d) recommendation ranking + recommended variant; (e) acceptance-ID checklist
S6-A1..S6-A8 with evidence each; (f) counters (decoder_calls, protected_reads,
rng_calls); (g) confirmation of every §4 non-touch (no decoder, no protected
reads, no docs/memory/index writes, no commits). If any acceptance ID fails or
any §4 item was touched, that is condition 2 (blocker), not condition 1.

## Hard boundaries (recap — violation = STOP)

Reads ⊆ `TASK_PACKET.md` §3. Writes = `results.json` in the probe root ONLY.
No decoder import/run. No protected-segment open (any need ⇒ STOP). No
`docs/`/`AGENT_PROJECT_MEMORY.md`/index writes. No `git commit`. No λ/Laplace/
construction change. No threshold, verdict, or claim language in any output.
