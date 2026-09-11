# Validation and early-falsification gates

## Required metric distinctions

Every run record must keep these fields separate:

```text
initial_map_error
sc_hard_exact
constraint_satisfied
posterior_or_metric_provenance
verified
undetected
failed_decode
resource_abort
```

`decision_logp` is a sequence of SC conditional scores. It is not a complete
posterior over the original symbols. `verified` is a Toeplitz correctness
check, and `undetected` is never merged into exact success or FER.

All `1e-12` and `1e-9` gates below are absolute maximum-error tolerances.
Metrics are float64 natural logs internally; bits are report-boundary units.

## Earliest falsification experiments

| Question | Small experiment | Falsifies the route when |
|---|---|---|
| Does the kernel polarize? | GF32 alpha cycle and alpha=1/2 conditional-entropy toy | alpha does not generate GF32, or the frozen transform fails the analytic toy |
| Is the transform orientation right? | GF4 `N=4` exhaustive dense reference | any output or inverse mismatch |
| Is SC recursion right? | GF32 `N=2`, GF4 `N<=4` exhaustive posterior | conditional metric differs by more than `1e-12` |
| Is the decoder doing work? | QSC/erasure blocks with intentionally wrong initial MAP | every result is truth-centered or SC does not improve a known easy point |
| Is the prior right? | reconstruct `P1*P2`, surprisal and held-out CE | axis, normalization or held-out calculation differs |
| Is two-layer propagation causal? | L1 / oracle-L2 / candidate-L2 paired records | operational L2 silently receives truth or unlabelled APP |
| Is the protocol cost real? | static full-symbol packing and independent disclosure recount | q-ary coordinates are counted as one bit or seed/tag are mixed into EC leakage |
| Is NB-Polar useful? | matched binary Polar/NB-LDPC comparison | no disclosure or resource advantage at comparable FER |

## Complexity ceiling

Reference q-ary SC is `O(N*q^2*log N)` and transform is `O(N*log N)` field
operations. For q=32 this is a deliberate correctness reference, not the final
performance target. GF1024 is deferred because its direct q-squared path is
too expensive for the first implementation. Any FWHT or table optimization
must remain behind reference-equivalence tests.

## Verification accounting

For one serialized final message, one independent 64-bit Toeplitz tag has a
`2^-64` correctness bound. For a fixed batch, use the pre-registered number of
invocations times `2^-64`. Incremental disclosure, retries, and candidate
selection require a new explicit invocation universe; they cannot silently
inherit the fixed-batch bound.

## Evidence boundaries

Synthetic gates establish implementation behavior. CAL/DEV/EVAL tests establish
model behavior. A real-data result requires its own packet, authorization and
pre-result review. None of these gates changes the frozen Release mainline or
promotes an NB-Polar method automatically.
