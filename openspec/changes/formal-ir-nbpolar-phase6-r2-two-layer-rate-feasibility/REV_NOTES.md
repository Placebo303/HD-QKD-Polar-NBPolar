# R2 Rev note — conventions frozen during implementation

Scope: documentation of the conventions actually frozen by the Phase 6-R2
decoder-free implementation (`two_layer_rate.py`). This file adds no
requirement, changes no proposal/design/spec text, and checks no
`tasks.md` box; acceptance remains a main-thread decision.

## Frozen conventions (as implemented and reported)

1. **Inputs / provenance (R2-A01).** TRAIN `nll_u1`/`nll_u2` values with
   file:line provenance:
   - 1M: `docs/v49_distribution_tables/v49_train_val_hold_nll.csv:2`
     (mirror `docs/v49-distribution-shift-diagnosis-20260827.md:78`);
     H1=0.02428054681872374, H2=0.7767572780789994.
   - 1p5M: `...csv:7` / `...md:81`; H1=0.02519949687789926,
     H2=0.8003665547438703.
   - 2M: `...csv:12` / `...md:84`; H1=0.025662048796915037,
     H2=0.8069006731253232.
   - Cross-refs: `docs/decision-log.md:402-404` (V27R H recomputation),
     `docs/decision-log.md:2879-2891` and
     `docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40`
     (V26 A02 L1/L2 H).
2. **Erasure mapping.** `epsilon_l = H_l / 5` (5-bit GF32 plane), as in
   `design.md`.
3. **FER allocations.** Whole-block budget `1e-2`:
   - `equal`: `(0.01/2, 0.01/2)`;
   - `entropy_proportional`: `(0.01*H1/(H1+H2), 0.01*H2/(H1+H2))`.
4. **Minimum-K rule.** Sort the layer spectrum descending (worst-first) and
   take the smallest `K` in `0..N` with suffix union bound
   `sum(z[K:]) <= budget_l`; `K=N` has residual exactly `0.0`.
5. **Accounting.** `leakage_bits = 5*(K1+K2)+64` (exactly one 64-bit tag),
   `leakage_bits_no_tag = 5*(K1+K2)`, `nH = N*(H1+H2)`,
   `f = leakage_bits/nH`, `f_no_tag = leakage_bits_no_tag/nH`.
6. **Axes.** `N` in `2^8..2^18`, 3 accepted sources, 2 allocations; first `N`
   with tag-inclusive `f <= 1.3` reported per axis.
7. **Calibration.** `N=256, epsilon=0.05, budget=1e-2 -> K=43`, reproduced by
   the operational recurrence and an independent literal oracle; mismatch is a
   hard stop before any table is emitted.

No formula, budget or input was adjusted after results were observed.
