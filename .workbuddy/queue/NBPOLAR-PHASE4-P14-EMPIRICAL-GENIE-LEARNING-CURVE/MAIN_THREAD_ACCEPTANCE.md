# Main-thread acceptance — Phase 4-P14 empirical-genie learning curve

Decision: accept
`TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` as a valid negative
within the frozen V25-1M-TRAIN model-sampled genie-proxy scope.

All integrity gates passed, the one read/attempt was consumed without rerun or
tuning, and both independent reviews support the result. Increasing the nested
TRAIN prefix from 8 to 128 blocks did not produce a monotone or material DEV
residual reduction: B=8 mean/UCB was 0.1176/0.1725 and B=128 was
0.1420/0.2011; the paired B128-B8 mean was +0.0244. The construction orders
were already highly stable. Therefore eight-block construction sample size is
not accepted as the material cause of P13's N=16384 miss.

This does not prove operational FER or a minimum N. The next gate resumes the
N axis with empirical genie construction at N=32768 and N=65536; it does not
retry P12 or use BEC orders.

