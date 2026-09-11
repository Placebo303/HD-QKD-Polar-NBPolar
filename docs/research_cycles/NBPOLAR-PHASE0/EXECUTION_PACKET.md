# NBPOLAR-PHASE0 operator packet

## State

This packet is prepared for review and is not an authorization. It covers only
Phase 0-2 of the NB-Polar roadmap.

## Allowed implementation scope after acceptance

- New files under `comparison_bench/src/comparison_bench/formal_ir/nbpolar/`.
- A thin `comparison_bench/src/comparison_bench/methods/nbpolar.py` only if
  the Phase 0-2 design requires it.
- Focused tiny tests under `comparison_bench/tests/`.
- The OpenSpec and cycle documents for this change.

## Forbidden in this packet

- Any modification to sibling `../HD-QKD_Polar_Release`.
- Any modification to `src/`, `experiments/`, `tools/`, `results/`, or
  existing comparison production outputs.
- Model-F/TTBin/CAL/VAL loading, real-data decoder calls, SCL, puncturing,
  shortening, rate scans, or performance claims.
- Copying LDPC matrices, graph construction, BP schedules, or old disclosure
  row counts into the Polar implementation.

## Fixed contract

`q=32`, polynomial `37`, `alpha=2`, natural-order `F_alpha` tensor transform,
float64 `(N,q)` log metric, actual known symbols including zero, independent tiny
enumerator, and no CRC path selection.

## Return conditions

Return after all Phase 0-2 acceptance items pass, or return `BLOCKED` with one
exact failing command/error, attempted remedies, and the single decision
needed from the main thread. Do not continue to later phases automatically.
