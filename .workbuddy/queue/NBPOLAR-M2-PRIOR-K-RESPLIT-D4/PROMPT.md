# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-K-RESPLIT-D4 (report-only; no adoption)

You are the operator deriving a frozen D4 comparison. Do NOT redesign. Do NOT guess. If the packet is ambiguous,
STOP and report (second return condition). **This packet REPORTS both branches; it ADOPTS NEITHER.**

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD`. Else STOP.
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-K-RESPLIT-D4/TASK_PACKET.md` (authoritative).
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim per `docs/troubleshooting.md`)
- NEVER modify `scripts/m2_prior_validation.py`, `prior_m2.py`, or anything under `formal_ir/nbpolar/`, `src/`,
  `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`. NEVER read real/protected data.
  NEVER call a decoder/genie/SC on protected data (synthetic-only; test-only calls use a fake runner).
  NEVER write outside `workspace/m2_prior_validation/k_resplit_d4/`, the new test file, and this packet's STATUS.yaml
  (ids/counters/artifacts only).

## 1. Inputs (frozen, from G1R2 — do not re-derive from data)

M2 CIRCULAR CAL triple (SHG `_1`, 32-frame CAL, frames 1024–1055): q0 = 0.7562255859375, q+1 = 0.241943359375,
q−1 = 0.0018310546875, q_rest = 0. Measured entropies: **H_M2 = 0.8168138204133305** (H1 0.02525363754305251 +
H2 0.791560182870278); H_M0 = 0.6910589201904378. N = 32768. Budget literal: `K_total = floor((f·N·H − 64)/5)`.

## 2. Derivation (compute in-packet; never copy hand arithmetic)

1. **Branch A (fixed f = 1.3)**: recompute N·H, 1.3·N·H, −64, ÷5, floor ⇒ K_total (target ≈ 6946).
2. **Branch B (fixed K_total)**: f = (5·K_total + 64)/(N·H) for K_total ∈ {6811 (frozen G2 point 319+6492),
   6946 (Branch A), 7020 (1.5M session-scale)} → 1.2747449 / 1.2999641 / 1.3137879. **R5 tolerance (binding;
   supersedes the former "must return exactly 1.3" line):** 6946 gives f ≈ 1.2999641, deviation −3.59e-5 from 1.3
   (floor-loss artifact; exact closure unattainable) — report the deviation explicitly, never round it to "1.3".
3. **(K1,K2) per branch** via the **frozen** `select_empirical_split(n, e1_mean, h1_mean, e2_mean, h2_mean, k_total)`
   imported from `nbpolar.empirical_genie_scaling` — **never reimplemented**. Build e/h vectors from the M2 model on
   **16 synthetic TRAIN blocks**, preregistered seeds **2026100101 … 2026100116** (fresh; see packet for the
   no-collision list). `k_total` is a REQUIRED caller argument with no literal baked in.
4. H-proportional split is BANNED as a selection rule — descriptive contrast column only, clearly labelled.

## 3. Outputs

`workspace/m2_prior_validation/k_resplit_d4/{report.md,results.json,run_log.md}`: per-branch K_total, derived f,
(K1,K2), explicit arithmetic, frozen-selector provenance (import path + exact call), the 16 seeds, and a
**NO-ADOPTION** banner. Plus focused tests `comparison_bench/tests/test_nbpolar_m2_k_resplit.py` (hand-built
synthetic e/h vectors; literal-enumeration replay; branch arithmetic; `k_total` required/no-literal;
H-proportional text absent as a selection rule).

## 4. Return (exactly two)

1. All-complete: per-ID PASS (D4-A..D4-D) with evidence paths + the two-branch table + pytest log + scoped
   `git status`.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed.
   "Still incomplete" is not a report.

## Stop rules

Any real-data read or protected decoder/genie/SC call ⇒ STOP + blocker. If the frozen selector needs SC/genie to
build e/h vectors ⇒ STOP and report (do not improvise). Ambiguity ⇒ STOP. No decision-log / memory / index /
parent-packet STATUS updates (main-thread milestone batch).
