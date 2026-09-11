# NB-Polar MVP specification

## Requirement: field and kernel

The MVP SHALL use polynomial-basis GF(32) with primitive polynomial 37,
integer symbols `0..31`, `alpha=2`, and the row-vector kernel
`F=[[1,0],[alpha,1]]`. It SHALL define transform order explicitly and test it
against an independent dense reference.

## Requirement: source coding

The MVP SHALL treat reconciliation as source polarization with side
information: Alice computes `U=A G`, discloses selected coordinates with their
actual values, and Bob reconstructs `A_hat` after SC. Disclosed coordinates
MUST NOT be silently replaced by zero frozen bits.

## Requirement: metric contract

Decoder input SHALL be float64 normalized log probabilities with shape
`(N,q)` and probability axis last. SC conditional scores SHALL carry explicit
provenance and SHALL NOT be described as a complete symbol APP.

## Requirement: validation

The implementation SHALL include an independent tiny enumerator. It SHALL
verify transform, inverse, known-coordinate handling, noiseless recovery and
SC conditional metrics before any Model-F or real-data execution.

## Requirement: repository boundary

The MVP SHALL modify only the Comparison layer in the NB-Polar worktree and
focused tests. It SHALL not modify the Release checkout, frozen baseline,
historical result roots, or run a production decoder implicitly.

