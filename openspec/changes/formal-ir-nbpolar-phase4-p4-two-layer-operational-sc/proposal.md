# Proposal: Phase 4-P4 two-layer operational SC

The accepted R2 audit proves that all prior SC gates were single-layer. Close
the omitted Phase-4 dependency before empirical construction, scalable
optimization or SCL: execute L1 SC, condition L2 on the recovered hard L1
candidate, execute L2 SC, reconstruct the 10-bit symbol, and verify it.

Pair the operational candidate-conditioned L2 path with a true-L1-conditioned
oracle diagnostic on the same bounded synthetic blocks. This establishes
causal wiring and measures cross-layer error propagation; it does not establish
real-data performance or `f<=1.3`.
