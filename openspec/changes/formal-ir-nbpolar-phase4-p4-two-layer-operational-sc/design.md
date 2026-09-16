# Design: Phase 4-P4 two-layer operational SC

Use injected full-symbol conditional tables only. Derive P1 `[U1,B]` and P2
`[U1,B,U2]` through the accepted prior helpers. For each block:

1. build P1 from Bob only and run fresh L1 SC;
2. recover the L1 source-domain hard candidate;
3. build `P2_hat` from Bob plus that candidate, mark
   `CANDIDATE_CONDITIONED`, and run fresh L2 SC;
4. combine `low_hat+32*high_hat`, then apply one final 64-bit tag;
5. in a diagnostic-only paired arm replace the candidate at step 3 with true
   L1 and mark `ORACLE_CONDITIONED`.

Truth may enter generation, scoring, disclosures and the oracle arm only. It
must not enter the operational L2 metric. L1/L2 disclosures and failures are
separate; final exact/undetected/verify/decode/resource buckets remain mutually
exclusive. No APP/soft feedback or state is carried between SC calls.

Tiny N=2/4 cases use exhaustive two-layer oracles. A single bounded N=256
model-sampled interface gate uses frozen injected tables, construction sets,
block count, seed and thresholds. It is not an efficiency gate.
