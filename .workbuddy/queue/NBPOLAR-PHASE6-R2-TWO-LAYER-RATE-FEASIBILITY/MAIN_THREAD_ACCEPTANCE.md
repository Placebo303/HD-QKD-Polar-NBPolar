# Main-thread acceptance — Phase 6-R2

Verdict: `TWO_LAYER_RATE_FEASIBILITY_ACCEPTED`.

The 66-row table, K43 calibration, full-precision entropy inputs, leakage/f
accounting and first-grid crossing at N=2^18 were independently reproduced.
The code/document audit also confirms that oracle-L2 and candidate-conditioned
operational L2 have never entered SC execution.

Accepted scope is decoder-free BEC-surrogate planning evidence only. The
2^17.20–2^17.36 interpolation and first tested passing N=2^18 are not
empirical-channel performance, a rigorous lower bound, decoder FER, achieved
efficiency, qualification or promotion.

Disposition: restore the omitted Phase-4 dependency before Phase 7. The next
packet implements and executes the smallest bounded two-stage operational SC
closed loop with paired oracle-L2 and candidate-L2 arms.
