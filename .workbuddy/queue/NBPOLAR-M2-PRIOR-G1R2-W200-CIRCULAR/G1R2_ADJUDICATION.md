# G1R2 MAIN-THREAD ADJUDICATION — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR (2026-09-22)

Label: `NBPOLAR_M2_PRIOR_G1R2_COMPLETE_DESCRIPTIVE` (G1-scope successor: decoder-free, descriptive/non-claim).

## 1. Basis

User authorization pasted verbatim (kai, 2026-09-22) + operator all-complete return for both phases + independent delta review `DELTA_PASS_WITH_COMMENTS` (after one DELTA_FAIL cycle on the runner block) + independent closure verification `G1R2_CLOSURE_PASS_WITH_COMMENTS` (Phase B unblocked) + independent focused numerical review `G1R2_NUMERICS_PASS_WITH_COMMENTS` (every recomputed number agrees; both gate rules applied on the correct freeze branch). Executed once per contract; no rerun, no tuning, no post-freeze change; decoder never called; SHG `_2` never read; G1's executed/adjudicated record byte-identical.

## 2. Results (descriptive; all independently recomputed)

SHG `_1` (`20260113_SHG_Type2PPLN_3s`), (N) W_P=200, MOD CIRCULAR, skip-702, W_S=500 readout recorded without switching:

- **Reproduction**: 5/5 exact (peak 50 / σ 112.45189572400645 / ok / n_pairs 1,259,992 / pre-skip 4,921); post-skip ledger 4,219 (216 trailing pairs dropped); segment lists element-identical to closure; reserve 4190–4218 (29), no id ≥ 4219.
- **G1R2-2 (δ-profile, CHAR 200,192 pairs)**: linear {−1023: 44, −1: 450, **0: 150909**, +1: 48788, +1023: 1}, tail 45; circular {−1: 451, **0: 150909**, +1: 48832}, **tail 0**. Wrap accounting closes exactly (linear −1023 → circular +1; linear +1023 → circular −1). CHAR δ=0 fraction **75.382%** vs full-stream **75.419%** — representative subset. (Record correction: an intermediate review-reading misidentified the δ=+1 cell 48,788 as c0; the artifacts are correct and self-consistent — do not propagate that misreading.)
- **G1R2-3 (CAL32 + held-out NLL)**: CAL = frames 1024–1055 (32 f, 8,192 pairs, sacrificed); M2 circular triple **q0 = 0.7562255859375 / q+1 = 0.241943359375 / q−1 = 0.0018310546875 / q_rest = 0**; matched M0 from the same 32 frames; HELDOUT 560 f = 143,360 symbols ⇒ NLL_M0 = 2.9623453, NLL_M2 = 0.8231435.
- **G1R2-4 (H + gates)**: H_M2 = 0.0252536 + 0.7915602 = **0.8168138**; H_M0 = 0.0215025 + 0.6695565 = **0.6910589**. δ-tail: n_tail 0, p̂ 0, U = 3/200192 = **1.4986e-5** < B_tail 2.0e-4 ⇒ **PASS**. NLL: Δ = **2.1392018** > 0.020 ⇒ **PASS**.
- **Remainder check (frozen sessions, no gate)**: CAL = stream 0–31 (1.5M VAL 2172–2203); HELDOUT 69 f = 17,664 symbols; CAL circular triple q0/q+/q− = 0.7476806640625 / 0.251220703125 / 0.0010986328125, **q_rest = 0**; H_M2 = 0.8251321, H_M0 = 0.7081275; pooled **Δ = 1.9575437** = symbol-weighted mean of VAL-9f 1.9786419 (n=2304) / HOLD-42f 2.0244344 (n=10752) / 2M-18f 1.7909163 (n=4608).

## 3. Adjudication

1. **δ-tail: PASS — a consequence of S11, NOT new validation of the ±1 premise.** CHAR is a subset of the full stream whose w=200 CIRCULAR tail S11 measured as 0, so p̂ = 0 is forced by inclusion. What G1R2 genuinely adds is the CAL32 triple, the H values and the held-out NLL under this contract.
2. **q_rest = 0 on both populations** (SHG `_1` and the frozen-session remainder, 8,192-pair CALs, CIRCULAR): at 32-frame CAL resolution nothing contradicts the ±1+wrap model. This is a weak statement by construction — 8,192 samples give a zero-observation upper bound of 3/8192 = 3.66e-4, which is exactly why the large CHAR sample gate exists and why G1R2 does not replace it.
3. **The M0 sparse-table pathology is confirmed again, now under the narrow-window contract** (matched-32f NLL Δ = 2.1392 on SHG `_1`; pooled 1.9575 on the remainder, essentially unchanged from G1's 1.9579). The mechanism remains unrefuted; note H_M0 on the remainder is bit-identical across the two contracts (0.7081275), consistent with M0 being window-independent there (observation only).
4. **No cross-contract superiority claim.** G1 (w=500/LINEAR) and G1R2 (w=200/CIRCULAR) measure different (window, MOD) populations; H and Δ are contract-relative. G1's bounded negative stands under its own contract and is not retroactively changed.
5. **M2 remains a CANDIDATE, not validated.** The δ-tail PASS removes the premise blocker that stopped G2; it does not demonstrate decoding success, FER, efficiency or reliability. Any such reading requires the G2 one-shot three-arm decode (Tier-Y, its own freeze, Pre-EXECUTE + explicit authorization).

## 4. Route consequence and inputs for the next freeze

- The premise blocker on the G2 path is lifted **for this contract**; T6/T7 (G2 freeze + execution) are no longer blocked by G1, and a G2 packet now has a defensible basis. G3 (SHG `_2`) presupposes an adopted candidate and remains void unless G2 succeeds.
- **G2/K_total inputs produced here (planning input, NOT a decision)**: H_M2 = 0.8168138 (SHG `_1`, w=200/CIRCULAR) is the decoder-input entropy; under the D4 budget literal K_total = floor((1.3·N·H_total − 64)/5) at N=32768 this arithmetic lands ≈ 6,946 (vs the frozen 7,020), i.e. a slightly smaller budget — but (a) the D4 fixed-f vs fixed-K choice is still DEFERRED and must be preregistered in the G2 freeze, (b) G2 decodes at the frozen K1=319/K2=6492 regardless, and (c) any re-split must come from the frozen `select_empirical_split`, not from this hand arithmetic.
- **Truncation caveat carried into G2**: w=200 keeps a timing-truncated population (c0 count is identical across windows, but jitter-heavy coincidences are preferentially dropped). Any rate/efficiency/leakage reading must state this.
- The previously recorded alternative routes remain open and unselected (explicit-tail-mass parametric model; the unmeasured incumbent 1024-frame arm — which is itself one of G2's three arms, A1).

## 5. Ledger

- Packet STATUS: G1R2-A and G1R2-1..G1R2-4 + remainder recorded; result = this label; `next_gate` = main-thread route decision (G2 freeze preparation, if authorized).
- Parent packet `NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1r2_delta.md` carries the 8-item delta; G1's own record untouched.
- Consumption: SHG `_1` decoder-free reads only (no decode, no attempt counters for G1-scope); frozen-session remainder read as frozen derived pairs only; SHG `_2` untouched.
- Milestone batch (decision-log / memory / index / scoped commit incl. the item-8 runner rework) is main-thread work executed after this adjudication.
