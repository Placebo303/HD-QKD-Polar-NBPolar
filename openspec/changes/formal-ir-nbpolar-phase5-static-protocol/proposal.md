# Proposal: NB-Polar Phase 5 static reconciliation protocol

## Why

Phase 4-P3 accepted the empirical P1-metric-to-SC interface, but it did not
exercise a reconciliation transcript. The next scientific risk is protocol
correctness: actual GF32 coordinate values, full-symbol reconstruction,
verification, outcome separation and disclosure accounting.

## Scope

Implement one static, synthetic-only NB-Polar reconciliation path at the
accepted Phase 3 point (`q=32`, `N=256`, erasure `epsilon=0.05`, `K=45`). Add a
thin adapter without changing `FrameBatch`, `IRRunConfig` or `IRRunResult`.
Run one independently reviewed 300-block development gate only after focused
synthetic qualification.

## Out of scope

No Model-F/real-data/DEV/EVAL input, adaptive disclosure, retry, SCL/CRC,
benchmark comparison, rate scan, key-rate claim, qualification, promotion,
sibling write, commit or push.
