# Main-thread acceptance — Phase 5 static protocol

Disposition: `STATIC_PROTOCOL_DEVELOPMENT_ACCEPTED`.

The main thread accepts the independently reviewed single synthetic
development attempt at GF32/poly37/alpha2, N=256, erasure epsilon=0.05 and
K=45. The static disclosure set is `analytic_order(0.05,256)[:45]`; physical
labels use `label=32*x_hat`; each attempted block uses one SC call and one final
64-bit Toeplitz verification over 2560 bits.

Accepted bounded facts: 300/300 exact, zero undetected/verify-failed/
decode-failed/resource-abort, one-sided 95% Wilson exact-recovery lower bound
0.9910621278248719, 289 key-dependent bits and 2623 public-control bits per
block, zero transcript-recount mismatch, zero truth leak/nonfinite, and all 11
hard gates true. Independent Pre-EXECUTE returned PASS and Pre-RESULT returned
PASS_WITH_COMMENTS; its required attempt-state correction is complete.

Attempt 1/1 and run seed 2026091317 are consumed. Toeplitz master 2026091318 is
public-control provenance. The five-file `static_protocol_dev_gate/` root is
immutable and must not be rerun, replaced or tuned.

This is a synthetic static-protocol development signal only. It is not
real-data FER, leakage efficiency, key rate, qualification, promotion,
adaptive disclosure or Phase 6 evidence. It grants no Phase 6 authorization.
