# Design: Phase 6 fixed incremental disclosure

## Frozen schedule

- Same point as Phase 5: GF32/poly37/alpha2, N=256, erasure epsilon=0.05.
- Worst-first analytic order from the accepted construction.
- Nested disclosure sizes `K=(29,33,37,41,45)`; level `i` publishes only the
  new coordinates in `D_i \ D_{i-1}` and every coordinate is counted once.
- SC restarts from scratch at each invoked level. No state, metric, hard
  decision or partial sum is carried across levels.
- Each invoked level receives an independent 64-bit Toeplitz seed and tag over
  the frozen 2560-bit `label=32*x_hat` message domain.

## Tag/continuation ruling

A tag is an accept/reject check for the current level. Match terminates the
fixed schedule. Mismatch discards that candidate and advances only to the next
predeclared level. It never selects among two candidates, supplies soft
information, changes a decoder parameter or skips/reorders a level. Final-level
mismatch is `verify_failed`. A matching non-exact candidate is `undetected`
and never success.

## Accounting

For a block accepted or terminated at disclosed size `K_j` after `j`
verification invocations:

`key_dependent_bits = 5*K_j + 64*j`

Public control is `2623*j` seed bits plus separately recorded fixed feedback
control. Every invocation contributes to the correctness union bound. Outcome,
invocation, cumulative disclosure and transcript recounts are independently
recomputed.

## Development comparison

Use a paired 300-block stream: static K45 and the fixed incremental schedule
receive identical synthetic blocks. Static is recomputed in the same run for
pairing and is not a rerun of the immutable Phase 5 evidence.

Incremental passes only if undetected is zero, exact recovery is at least
285/300, its one-sided 95% Wilson lower bound is at least 0.90, and its average
key-dependent disclosure is at least 5% below the paired static arm. All
invocation/accounting/resource gates must also pass.

## Rev note 2026-09-13 (frozen operator conventions; no task box checked)

- **Feedback bit convention.** Every level advance emits exactly one public
  `control` transcript event with `key_dependent_bits=0` and
  `public_control_bits=1`, counted separately as
  `feedback_control_invocations` / `feedback_control_bits`, included in the
  public-control total, and reported with the split. Per block: `feedback =
  tags - 1` for tag-terminated blocks (accept or final mismatch) and `feedback =
  tags` for a `decode_failed` block.
- **Per-arm seed derivation.** MSB-first SHA-256 counter stream over
  `"nbpolar-p6-toeplitz-seed:<master>:<arm>:<block_index>:<level>:<counter>"`
  truncated to `10*N + 63 = 2623` public control bits; `arm` in
  {`static`,`incremental`}; `block_index` 0-based; `level` 0-based (static
  comparator level 0, incremental levels 0..4 for K=29,33,37,41,45). Run seed
  `2026091340`, Toeplitz master `2026091341`; seeds are never persisted raw.
- **Paired comparator.** The static K=45 arm is a thin in-run re-implementation
  of the Phase 5 semantics with the Phase 6 seed derivation and runs on the same
  generated arrays as the incremental arm in the same order; the immutable
  Phase 5 evidence root is never read. Frozen ceilings: internal total wall
  600 s, per-paired-block soft cap 10 s, external `timeout 1200`, RSS envelope
  2 GiB.
