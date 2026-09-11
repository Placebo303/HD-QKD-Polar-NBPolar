# Independent review: NBPOLAR-PHASE2-SC-ORACLE

Date: 2026-09-11  
Verdict: `IMPLEMENTATION_ACCEPTED`

## Accepted evidence

The execution-session reviewer-go result is accepted as the independent test
authority for this packet. It reports 33/33 pytest tests passing: 17 unchanged
Phase 1 regressions and 16 Phase 2 tests. The oracle comparison covers 221 SC
rows with maximum probability error `3.331e-16`, maximum finite log error
`1.776e-15`, zero support mismatches, and zero NaN. Noiseless loopback is
831/831 exact. The two N=64 sanity cases complete in 0.004 s and 0.009 s.

The implementation matches the frozen natural-order row-vector recursion.
The plus branch uses transformed left partial sums. Known zero and non-MAP
values are forced by coordinate membership, suffix symbols remain marginalized,
and Alice truth is absent from the operational decoder API. The exhaustive
oracle shares only the accepted Phase 1 reference transform and implements its
own enumeration and logsumexp.

## Review comments closed

1. The operator return said “all 32 betas” for four GF32 pair fixtures. The
   test uses four representative betas `(0,1,17,31)`; the return is corrected.
2. The reviewer-go pytest result is accepted without a duplicate main-thread
   run under the user's standing instruction.
3. Phase 1 files remain untracked, so Git cannot produce a base-relative diff.
   Their current content matches the accepted review surface and reviewer-go
   reports no Phase 1 edit. This provenance limitation is recorded rather than
   replaced with a checksum mechanism.
4. Generic alpha remains an API limitation; every accepted Phase 2 test and
   the operative MVP use `alpha=2`.
5. Pre-existing dirty files remain outside the Phase 2 allowlist. Frozen
   source/output paths and `nonbinary_field.py` show no scoped change.

## Boundary

This is implementation acceptance for the synthetic reference SC and tiny
oracle. It is not construction quality, FER, Model-F, real-data, protocol,
benchmark, qualification, or promotion evidence. Phase 3 requires a separate
packet and must retain disjoint construction/evaluation streams.
