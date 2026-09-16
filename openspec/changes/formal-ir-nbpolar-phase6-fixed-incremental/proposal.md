# Proposal: NB-Polar Phase 6 fixed incremental disclosure

## Why

Phase 5 accepted one static K=45 synthetic protocol at 289 key-dependent
bits/block. The next algorithmic question is whether a preregistered nested
schedule reduces average disclosure without losing the accepted development
recovery signal.

## Scope

Implement a fixed nested schedule at the same GF32/N256/erasure0.05 point,
restart reference SC from scratch at every invoked level, and use one fresh
64-bit Toeplitz verification per invoked level. A tag mismatch may only advance
to the next preregistered level; it cannot select among candidates or change
the decoder, construction or order.

## Out of scope

No real data, Model-F artifact, learned policy, per-frame tuning, warm start,
SCL/CRC, rate scan, comparison benchmark, key-rate claim, qualification,
promotion, sibling write, commit or push.
