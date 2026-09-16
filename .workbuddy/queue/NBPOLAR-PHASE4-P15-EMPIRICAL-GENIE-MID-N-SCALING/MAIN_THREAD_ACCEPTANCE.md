# Main-thread acceptance — Phase 4-P15 empirical-genie mid-N scaling

Decision: accept `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` as a
valid negative within the frozen V25-1M-TRAIN model-sampled genie-proxy scope.

All integrity gates passed; the one read/attempt was consumed without rerun or
tuning; independent Pre-EXECUTE and Pre-RESULT reviews support the result.
Neither N=32768 (DEV mean/UCB 0.01915/0.03590) nor N=65536
(0.02877/0.07613) met the conservative genie-residual UCB threshold 0.01.
The N=65536 mean was dominated by a rare high-residual block, so no monotone
cross-N improvement is accepted.

This does not establish operational FER. At N=32768 the mean genie residual is
already small enough that the conservative UCB gate may obscure useful
operational recovery. The next gate therefore tests the actual frozen
two-layer hard-candidate SC plus tag at N=32768 and f<=1.3. It does not extend
the genie curve, retry P12 or use BEC construction.

