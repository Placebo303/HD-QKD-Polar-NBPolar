# Phase 4-P6R1 Δ packet — multi-stream gate identity repair

## Main-thread disposition

The original P6 evidence root and its persisted
`BLOCKED(d1_exactly_nested_and_d2_disclosed_once)` label remain immutable. The
independent Pre-RESULT review established that the sole false gate was caused
by grouping L2 events by `(block,arm)` although block indices repeat across five
streams. This successor repairs the checker and revalidates the existing five
artifacts without any decoder call, new sample, seed, tag or attempt.

## R1-01 — Exact code delta

Before code changes, add a P6-R1 rev note to the existing Phase 4 OpenSpec.
Then:

- fix `adaptive_l1.py` so every future transcript event has an unambiguous
  public `(stream_seed,block_index,arm)` identity and the D2-once gate groups by
  that compound identity;
- keep all scientific constants, decoder paths, outcomes, disclosure formulas
  and thresholds unchanged;
- add a focused multi-stream test whose streams share block indices and which
  fails under the old `(block,arm)` grouping but passes only when every
  `(stream,block,arm)` has exactly one D2 disclosure;
- retain single-stream, transcript recount and tamper coverage.

Allowed code files are `adaptive_l1.py`, its focused test, and at most one
small read-only `adaptive_l1_revalidate.py` helper plus a package export if
needed. Do not edit `sc.py`, prior/construction/two-layer semantics, adapters,
P5, or any probe/evidence root.

## R1-02 — Tests

Run compile/import, focused adaptive-L1 tests, and the full accepted NB-Polar
predecessor suite. No test may invoke a production decoder or write into the P6
evidence root. Test-only injected records must include at least two streams with
the same block indices.

## R1-03 — Frozen read-only revalidation

Input is exactly the existing directory:

`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`

It must contain the original five files and must not be changed. The verifier
must read stored per-block records and transcript accounting only; it must not
call SC, RNG, sampling, tag construction or the development runner.

Require 640 unique `(stream_seed,block_index)` records, two arms per record,
`l2_invoked=true` for all 1280 arm-blocks, the recorded/recounted L2-disclosure
total of 1280, and all other original frozen integrity/scientific gates. Reuse
the original P6 thresholds verbatim:

- static exact >=620/640;
- adaptive exact equals static exact;
- adaptive-only=static-only=0;
- `100*adaptive_total_key_dependent <= 85*static_total_key_dependent`;
- all integrity/accounting/truth-isolation/resource gates true after the sole
  identity correction.

Write exactly one machine-readable result outside the old root:

`.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json`

It must report the original persisted label, the corrected gate value, all 12
integrity gates, all four scientific gates, paired/outcome/disclosure totals,
input file inventory, `decoder_calls=0`, `rng_calls=0`, `tag_calls=0`, and
`attempts_consumed=0` for R1.

If every corrected gate is true, return successor label
`ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`. If the compound-identity gate or any
other frozen gate is false, return `BLOCKED(<earliest gate>)`. Never rewrite the
original aggregate summary/report or reinterpret its persisted BLOCKED field.

## R1-04 — Independent review and return

No Pre-EXECUTE gate is required because R1 cannot execute a decoder or create
scientific samples. Before operator return, an independent reviewer-go must:

- inspect the code delta and prove it is limited to event identity/checking;
- independently reconstruct all 640 compound identities and 1280 D2 arm-block
  obligations from the original records;
- recompute every original integrity/scientific gate and compare with
  `revalidation.json`;
- verify zero decoder/RNG/tag calls and unchanged old-root file inventory;
- run or inspect the multi-stream regression test.

Record this as `INDEPENDENT_REVALIDATION_REVIEW.md` and return in
`OPERATOR_RETURN_R1.md`. Reviewer PASS/PASS_WITH_COMMENTS allows candidate
return, but main-thread acceptance remains separate.

## Stop and forbidden actions

STOP on missing/extra old-root files, ambiguous stored identity, any old-root
write, test failure, a second gate discrepancy, or any path that could call the
decoder/RNG/tag generator. Report the raw mismatch; do not regenerate data.

No new attempt or seed is authorized. No decoder, development gate, rerun,
artifact/real data, threshold/model/K change, APP/SCL/FWHT, qualification,
promotion, commit or push. Preserve the original failure root and status
history.

