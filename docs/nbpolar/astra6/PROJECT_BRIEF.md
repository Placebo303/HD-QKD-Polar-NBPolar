# Project brief: native GF(32) NB-Polar reconciliation for HD-QKD

## Objective

Develop a scientifically defensible, high-performance nonbinary Polar
information-reconciliation method for the actual high-dimensional QKD
channel. Benchmark and lifecycle machinery support this goal; they are not
the goal.

## Frozen mathematical contract

- Two GF(32) layers are packed as `A = 32*U1 + U2`.
- Field: GF(32), polynomial basis, primitive polynomial 37.
- Kernel: `[x0,x1]=[u0,u1]F_alpha`, `x0=u0+2*u1`, `x1=u1`.
- Transform: natural order and self-inverse under the frozen convention.
- Decoder: normalized float64 log-domain q-ary source SC.
- Minus recursion: `L-(u)=logsumexp_v[L0(u+2v)+L1(v)]`.
- Plus recursion uses encoded left partial sums.
- Alice discloses actual transformed GF(32) coordinates; this is source
  reconciliation, not zero-frozen channel coding or syndrome decoding.
- Operational L2 is conditioned on the hard L1 candidate. True-L1
  conditioning is oracle-only.
- One final 64-bit Toeplitz tag verifies a candidate; it never selects a path.
- `undetected`, `verify_failed`, `decode_failed`, and resource failure remain
  distinct from exact recovery.

## Current evidence

1. Algebra, transform, SC tiny-oracle, prior tables, static protocol, and
   accounting gates are accepted within their stated synthetic scopes.
2. On a dependent synthetic two-layer point, hard candidate-conditioned L2
   recovered 233/384; true-L1 oracle-conditioned L2 recovered 377/384. Paired
   cells were: both 233, oracle-only 144, operational-only 0, neither 7. This
   is mechanism evidence for hard-L1 propagation, not real-channel FER.
3. An adaptive L1 ladder matched static recovery at 632/640 and reduced
   key-dependent disclosure by 20.2484% at frozen N=256. This is not scaling
   or real-channel efficiency evidence.
4. The target population is V25 1M TRAIN, not the earlier Model-F CAL
   population. Its raw-MLE conditional entropies are H1=0.02428054681872374,
   H2=0.7767572780789994, total=0.8010378248977232 bits/physical symbol.
5. At N=256, empirical construction was accepted. A frozen-grid search chose
   K1=6, K2=70 and recovered 624/640 model-sampled blocks, but planning-only
   `f=2.1652` remained above the project goal `f<=1.3`.
6. Exact row chunking preserved direct q-squared SC arithmetic and enabled
   N=262144 under the registered resource bound. A tested FWHT prototype
   changed exact support; tiny roundoff changed near-tied early decisions and
   later exception behavior. That exact-semantics FWHT route was rejected.
7. Empirical-genie studies at N=4096..65536 missed their residual-UCB gate and
   were non-monotone. They are construction proxies, not operational FER.
8. At N=32768, empirical construction with K1=319 and K2=6492 uses 34119
   key-dependent bits. V25-TRAIN-model samples recovered 62/64 and then
   123/128 on fresh replication blocks, with zero undetected outcomes. The
   first run had zero count margin; replication had count margin 2. This is
   accepted model-sampled development evidence, not qualification.
9. The only 1M HOLD material provides three chronological non-overlapping
   N=32768 blocks. All returned `verify_failed` (0/3 exact), with no
   undetected/decode/nonfinite/resource failures. Aggregate
   sample-CE-normalized disclosure ratio was 1.23082048. This is too small and
   adjacent for a FER claim or route rejection.
10. The frozen next diagnostic reuses those blocks in five arms: base; +128
    L1 coordinates; +512 L2 coordinates; both; and a provenance-isolated
    true-L1 L2 control. It has no winner/recovery threshold and is not
    authorized by this pack.

## Core contradiction

The TRAIN model suggests an N=32768 point near the intended disclosure budget
is operationally plausible, but the tiny HOLD sample failed under the same
construction and prior. Candidate causes include finite-sample chance,
population/session shift, prior support or calibration error, construction
transfer failure, insufficient layer-specific backoff, hard L1 propagation,
or interactions among them.

## Non-negotiable boundaries

- Do not infer FER from three HOLD blocks.
- Planning `f`, sample-CE ratios, and qualified efficiency are distinct.
- Alice truth may enter operational work only through disclosed symbols, tag
  construction, and scoring.
- Do not relabel SC decision metrics as full APPs.
- Do not combine posteriors as independent evidence without proof.
- Do not generalize one construction/decoder/rate/population failure to the
  NB-Polar family.
- Execution requires a separate frozen packet, independent review, and
  explicit user authorization.

