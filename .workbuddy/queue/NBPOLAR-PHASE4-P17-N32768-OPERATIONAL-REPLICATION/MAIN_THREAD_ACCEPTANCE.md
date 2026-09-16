# Main-thread acceptance — Phase 4-P17 operational replication

Decision: accept `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`
as an independently replicated, model-sampled operational development signal.

P17 recovered 123/128 blocks with zero undetected outcomes and a one-sided
95% Wilson lower bound of 0.92193404995. The frozen threshold was 121/128, so
the count margin is two blocks. P16 is not pooled into this decision. The
single protected read and attempt were consumed without rerun or tuning, and
the independent Pre-EXECUTE and Pre-RESULT reviews support the classification.

This acceptance establishes neither real-data FER nor qualification. It also
does not promote the empirical construction or f=1.3 point beyond the sampled
V25-TRAIN channel model. The next gate is a three-block, non-overlapping 1M
HOLD microcheck using the unchanged P16/P17 construction and disclosure. Its
purpose is real-input/interface and mismatch diagnosis; three chronological
blocks are explicitly insufficient for a FER claim.

Route principle: empirical construction selects a candidate finite-length
point; operational decoder evidence and real held-out behavior are separate
stages. Information-theoretic backoff and graph/decoder effects remain
separate quantities.
