# S11 MAIN-THREAD ADJUDICATION — NBPOLAR-S11-SHG-TAIL-NATURE (2026-09-21)

Label: `NBPOLAR_S11_SHG_TAIL_NATURE_COMPLETE_DESCRIPTIVE`. Tier-X probe: descriptive/non-claim, decoder-free; no token, no attempt consumption, no scientific-status change.

## 1. Basis

User authorization pasted verbatim (Kai, 2026-09-21) + operator all-complete return (S11-P..S11-R PASS) after one main-thread scoped packet correction (anchor = post-skip frames 1056–1837, replacing the contradictory "first 782 post-skip frames" wording) + independent focused numerical review `S11_NUMERICS_PASS` (every recomputed number agrees to full precision; prereg 22:21:04 < body 22:23:02 < results 22:23:30; scope clean; anchor cell-exact incl. sparse histogram cells). One run, 19.5 s / 1.24 GiB, no rerun.

## 2. Results (descriptive; all values recomputed independently)

SHG `_1` (`20260113_SHG_Type2PPLN_3s`), vendored (N) nearest-unique pairing, frozen constants, frozen derived offset +50 ps (σ=112.45189572400645), LINEAR_ONLY semantics:

- **Anchor** (w=500, skip-702, frames 1056–1837): tail 1005/200,192, p̂ = 0.0050202 — cell-exact reproduction of the G1 CHAR profile {0: 149852, +1: 48639, −1: 696, tail: 1005} incl. sparse cells; full-stream n_pairs 1,269,268 = census/G1. Pipeline healthy.
- **W-grid** (offset +50, no skip): p̂ = 0.0002389 (w=200, 301/1,259,992) / 0.0050155 (w=500, 6366/1,269,268) / 0.0168189 (w=1000, 21604/1,284,506) / 0.0394334 (w=2000, 51845/1,314,747); ratio p̂_2000/p̂_200 = 165.07. The w=200 LINEAR tail (301) is **entirely wrap-alias cells** (8 + 293); the w=200 **CIRCULAR tail = 0**. Wrap+ fixed at 8 and wrap− at 293→294 across all windows.
- **Offset scan** (w=500): p̂ = {50: 0.0050155, 25: 0.0049358, 75: 0.0052069, 0: 0.0048899, 100: 0.0054196, −50: 0.0051207}; minimum at offset 0 (not the derived +50); spread (max−min)/min = 10.83% — offset-insensitive within that band; no alignment signature.
- **Far-offset baseline** (w=500, 50±409600 ps): p̂ = 0.4067 / 0.3988 vs uniform 0.99707 and in-window 0.0050155 — the far-offset pairs retain channel structure (≈0.41× uniform, ≈80× in-window): **the census far-offset baseline is NOT a uniform-accidental reference**; far n (18340/18224) matches the census far yields exactly.
- **Clustering** (anchor, 782 frames): 578 frames with ≥1 tail vs Poisson-expected 565.70 (λ = 1.28517); dispersion = 1.21152/1.28517 = 0.94269 — independent-per-pair consistent.
- Window dependence vs the census accidental estimates (0.0058/0.0144/0.0284/0.0555): the tail rises **steeper than proportional** — per-point p̂/accidental ratios 0.041 → 0.348 → 0.592 → 0.711; OLS slope 0.803 with intercept −0.0055 (magnitude exceeding the entire w=500 signal), so "proportional to the accidental estimate" is NOT supported (reviewer-corrected characterization).

## 3. Adjudication (descriptive; binds nothing)

1. **The G1 δ-tail FAIL at w=500 is substantially a pairing-contamination effect, not a channel-structure refutation of the ±1 premise.** The tail scales steeply with the pairing window (165× across the grid; ~21× from w=200 to w=500) and is offset-insensitive, unclustered, and independent-per-pair consistent. At w=200 the CIRCULAR δ-mass ≤ 1 holds exactly on the full event stream (non-wrap tail = 0); the only LINEAR tail there is 301 wrap-alias events.
2. **The census far-offset accidental baseline is structured, not uniform** (tail ≈ 0.40 at ±2 superframes): the accidental estimates used across the census/G1 arithmetic cannot be read as uniform-accidental levels, and any accidental/true mixture model must carry this caveat.
3. **What this does NOT establish**: no prior-form decision, no window decision, no route selection. Post-hoc window switching remains forbidden by the frozen discipline; W_S=200's marginal bias (gauss cover 0.9247) stands as recorded. Nothing here touches M2's CANDIDATE status or the G1 bounded negative (which was correctly recorded under the frozen w=500 contract).
4. **Route input for main-thread planning (not selected here)**: the evidence reopens a narrow-window-centred validation as the leading candidate route — a w=200-centred M2-family validation would need its own freeze: explicit pairing-contract change (W_P 500→200) with the bias caveat, MOD/tail-budget re-derivation (note: at w=200 the LINEAR p̂ = 0.0002389 still exceeds the frozen B_tail = 2.0e-4, while the CIRCULAR tail = 0 — the gate semantics would have to be preregistered explicitly), gates re-preregistered, and its own authorization. Alternatives (explicit-tail-mass parametric model; the unmeasured incumbent 1024-frame arm) remain open.

## 4. Ledger

Probe artifacts stay worktree-only/gitignored by design (`workspace/probes/nbpolar_s11_shg_tail_nature/`); durable record = this adjudication + the milestone-batch decision-log entry + packet dir (committed at the next milestone). Packet STATUS: all ids pass; `result`/`next_gate` = main-thread closure. No ledger/memory/index updates were made in-packet (Tier-X rule; batch now).
