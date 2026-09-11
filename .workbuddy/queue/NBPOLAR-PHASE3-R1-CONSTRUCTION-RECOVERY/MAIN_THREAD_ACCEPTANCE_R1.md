# Main-thread acceptance — Phase 3-R1

Disposition: `EVAL_ACCEPTED_DIAGNOSTIC`.

The main thread accepts the reviewed single fresh synthetic EVAL at O3 analytic,
q=32, N=256, erasure epsilon=0.05, K=45, seed 2026091213. The accepted bounded
facts are 299/300 exact, 1/300 impossible decode failure at block 219,
300/300 initial-error blocks, zero other failures, and zero NaNs.

The earlier `OPERATOR_RETURN_R1.md` remains an immutable record of the temporary
reviewer-unavailable stop and is superseded for current lifecycle status. The
predecessor Phase 3 seed 2026091203 and block-104 diagnostic remain separately
blocked historical evidence.

This acceptance does not open Phase 4 and does not support claims about unique
N/K causality, general finite-length performance, Model-F, real data,
reconciliation efficiency, leakage, key rate, qualification, or promotion.
Seed 2026091213 and `eval_r1_fresh/` must never be rerun, replaced, or modified.
