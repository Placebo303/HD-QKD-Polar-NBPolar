# G1 MAIN-THREAD ADJUDICATION — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL (2026-09-21)

Label: `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`.

## 1. Basis

User authorization pasted verbatim (kai, 20260921; Phase 0/A/B scoped, decoder-free) + operator all-complete return (G1-0, G1-1..G1-4, remainder check) + independent closure verification `CLOSURE_PASS_WITH_COMMENTS` (Phase B unblocked) + independent focused numerical review `G1_NUMERICS_PASS` (every recomputed number agrees; both gate rules applied exactly per freeze §6; no operator discretion in the FAIL). G1 executed exactly once per freeze on SHG `_1`; no rerun, no tuning, no seed/window/K change; decoder never called; SHG `_2` never read; reproduction gate bit-exact vs the Phase-A closure ledger (peak 50 / σ 112.45189572400645 / ok / 1,269,268 / 4,958 pre-skip; post-skip 4,256).

## 2. Results (descriptive / non-claim; M2 remains a CANDIDATE throughout)

SHG `_1` (`20260113_SHG_Type2PPLN_3s`), (N) W_P=500, MOD LINEAR_ONLY, skip-702, CHAR 200,192 pairs, CAL32 = post-skip frames 1024–1055 (8,192 pairs, sacrificed), HELDOUT = 1838–2397 (143,360 symbols):

- **δ-tail gate: FAIL.** p̂ = 1005/200,192 = 0.0050202; one-sided 95% upper U = 0.0052879 (Clopper-Pearson; independently recomputed, abs diff 1.4e-14) vs B_tail = 2.0e-4 — ~25× over budget. Linear profile `{0: 149852, +1: 48639, −1: 696, tail: 1005}`; circular differs only in the expected wrap cells. **The ±1 parametric premise does not hold on this source.** Per freeze §6/§8: record; do NOT proceed to G2.
- **NLL gate: PASS (near-uninformative by design).** Δ = 3.043859 − 1.093192 = 1.950667 > Δ_min 0.020, matched 32-frame CAL, FIT32, seed N/A. The freeze's binding caveat applies: the matched-CAL M0 is NOT the incumbent (its as-deployed regime is 1024 frames, measurable only by G2 arm A1, now blocked); this NLL quantifies M0's sparse-table pathology at an 8,192-symbol CAL and never promotes M2.
- CAL triple q0/q+1/q−1/q_rest = 0.746704/0.243652/0.004395/0.005249; H_M0 = 0.730680 / H_M2 = 0.841180 (frozen helpers, PRIOR_ONLY). CAL-vs-CHAR tail rates consistent within noise (z = 0.28).
- **Remainder check (frozen sessions; NLL/H level only; no gate):** pooled Δ = 1.957900; per-segment 1.5M-VAL-9f 1.978823 / 1.5M-HOLD-42f 2.024941 / 2M-HOLD-18f 1.791009; CAL = VAL 2172–2203 (single-session); parquet pins match accepted records (1p5M `ca351e52…a06b`; 2M `d5a36eec…c307` per P20O). The matched-CAL M0 pathology replicates on the frozen sessions; their 32-frame CAL triple had q_rest = 0.0 (tail ≈ 0 there, vs 0.50% on SHG `_1`).

## 3. Adjudication

1. **G1 verdict: bounded negative for the M2 route on SHG `_1`.** The ±1 parametric prior's premise fails on the new SHG data at the frozen window; the preregistered STOP applies; G2 is NOT proceeded to. No tuning, no rerun, no post-hoc window switch (frozen).
2. **What this does NOT establish:** it does not refute the M0 floor-mishandling MECHANISM on frozen sessions (the matched-CAL NLL gap ~1.95 replicates on both populations — the sparse-table pathology is real and reproducible); it does not refute M2 on every source (frozen sessions show tail ≈ 0 — but that ladder is exhausted: 101 frames, 69 after CAL); it does not license any new route without its own preregistration; S9 remains synthetic-only and was never FER/efficiency evidence.
3. **Diagnostic observations (recorded, not adjudicated as science):** (a) the 0.50% CHAR tail is BELOW the uniform-accidental prediction from the census w=500 accidental estimate (1.44%) — the tail is not explained as pure uniform accidentals; the far-offset baseline may overestimate the in-window accidental rate, or the tail is non-accidental structure (broader/multimodal peaks on SHG). (b) q−1 on SHG `_1` (0.0044) is ~2.5× the frozen-session value (0.0014) — within-CAL noise is large at 8,192 symbols, but the direction is worth a future look. (c) The evidence root lacks the primary `.ttbin` identity pin (numerics unaffected; a future freeze should pin it in `run_log.md`).
4. **Route consequence (main-thread planning input, NOT an automatic pivot):** the `nbpolar-prior-rebaseline` change's D6 gate sequence is halted at G1 for the M2 candidate: T5 is complete; T6/T7 (G2 freeze/execute) are blocked by the premise FAIL and must not be prepared as if M2 were validated. G3 (SHG `_2`, reserved) presupposes an adopted candidate — void unless a new candidate emerges. Candidate directions for the next planning cycle (each needs its own preregistration; none selected here): (i) a richer parametric δ model with explicit tail mass (the SHG tail is small but 25× over the ±1-only budget); (ii) a preregistered investigation of the SHG tail's nature (structure vs contamination) before any prior-form decision; (iii) treating the M0-at-small-CAL pathology as the actionable finding (any smoother fixes the matched-CAL NLL — the incumbent 1024-frame arm A1 comparison never ran and remains the unmeasured reference).

## 4. Ledger

- Packet `STATUS.yaml`: ids G1-0/G1-A/G1-1..G1-4 recorded; result = this label; next_gate = milestone batch → main-thread route planning.
- Parent packet: G1 outcome recorded; TO-FREEZE closure keys now filled in `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/g1_freeze_config.json` (verified); T5 complete; T6/T7 blocked pending a route decision.
- Consumption: SHG `_1` decoder-free reads only (no decode); no attempt counters exist for G1 (descriptive); frozen-session remainder read as frozen derived pairs only (no new derivation); SHG `_2` untouched.
- Milestone batch (decision-log / memory / index) is main-thread work, executed after this adjudication.
