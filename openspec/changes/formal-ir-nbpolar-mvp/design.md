# Design: NB-Polar MVP

## Field and symbol contract

Use integer symbols `0..31` in polynomial-basis GF(32), primitive polynomial
37, with `alpha=2`. The physical `d=1024` label remains a pair of GF32 tags:
`A=32*high+low`; it is not a GF1024 arithmetic contract.

## Transform

For row vectors, `x0=u0+alpha*u1` and `x1=u1`. Recursively apply the 2x2
butterfly in natural order. Keep a slow dense reference in tests and assert
the transform is self-inverse under characteristic two.

## Metric and decoder

The decoder accepts `logp_x[N,q]`, float64, normalized on the last axis. It
uses log-sum-exp for the minus branch and a conditioned plus branch with the
left encoded partial sums. Known coordinates contain Alice's disclosed symbol
value; all other coordinates are decided by maximum conditional probability.

The result distinguishes hard output from any metric output. SC conditional
scores are not called full APP and cannot feed the legacy `q @ P` interface.

## Construction and protocol boundary

Construction is a later genie Monte Carlo step with disjoint training and
evaluation data. The MVP has no Model-F execution and no adaptive disclosure.
When protocol work opens, a static coordinate set sends actual q-ary values at
5 bits per GF32 coordinate, followed by one independent full-symbol Toeplitz
tag. CRC is not part of path selection or verification.

## Repository boundary

Only this worktree's `comparison_bench/` and focused tests are implementation
scope. Sibling `../HD-QKD_Polar_Release` is read-only. Historical Comparison
NB-LDPC modules are input/reference assets, not a new inheritance hierarchy.
