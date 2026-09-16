# Design: NB-Polar Phase 5 static reconciliation protocol

## Rev note (2026-09-13, main-thread rulings R1/R2)

- **R1 (disclosure orientation).** The frozen DISCLOSED set is
  `construction.analytic_order(0.05, 256)[:45]` — the 45 *highest-risk*
  coordinates, matching the accepted Phase 3 point (`evaluate_blocks(...,
  k=45)`) and `docs/nbpolar/ARCHITECTURE.md`. The earlier wording in this file
  and in the task packet that described disclosing the complement is
  superseded: Alice publishes the actual `U[D]` values for that worst-first
  slice and SC reconstructs the remaining 211 coordinates.
- **R2 (label domain).** The physical label vector is the 10-bit single-layer
  embedding `label_j = 32 * x_hat_j` (low half constant zero). The Toeplitz
  message domain is `10*N = 2560` bits and the per-block seed length is
  `message_bits + 63 = 2623` public control bits.

These rulings were applied to the implementation and to the frozen plan in
`.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/P5_FREEZE.md`; no task box is
checked here (acceptance is main-thread-owned).

## Frozen protocol

- Field/kernel/order: accepted GF32, polynomial 37, alpha 2, natural order.
- Development point: q-ary erasure channel, `N=256`, `epsilon=0.05`, `K=45`.
- Static disclosure set: disclose the first 45 coordinates in the accepted
  Phase 3 analytic order. That order is worst-first, and this is exactly the
  `evaluate_blocks(..., k=45)` convention behind the accepted 299/300 Phase 3
  point. Publish the actual GF32 values, including zero; never encode “known”
  by a truthy sentinel. SC reconstructs the remaining 211 coordinates.
- Bob runs the accepted reference SC once. There is no retry or candidate
  selection. Re-encode the recovered full `U` vector to 1024-ary physical
  labels and compare only for scoring.
- Invoke one 64-bit Toeplitz tag after decoding. A mismatch rejects; a match on
  a non-exact block is `undetected`, never success. The tag cannot select or
  alter a decoder path.

## Accounting

Each disclosed GF32 coordinate costs 5 key-dependent bits. The 64-bit tag is
also key-dependent. Toeplitz seed material is public control and is reported
separately. Thus per attempted block:

`key_dependent_disclosure_bits = 5 * 45 + 64 = 289`

Independent recount must derive the same value from transcript events.
Attempted, exact, verified, undetected, failed-decode, verify-failed and
resource-abort remain separate. `IRRunResult` is populated without changing its
signature; richer per-frame fields live in metadata and the protocol result.

## Development gate

After independent Pre-EXECUTE PASS, use one fresh synthetic seed for exactly
300 blocks. Pass only if all accounting/truth-isolation gates pass, undetected
is zero, and the one-sided 95% Wilson lower bound for exact recovery is at
least 0.90. Average key-dependent disclosure must be below `10*N` raw bits.
This is a development signal only.
