# NB-Polar implementation roadmap

## Current priority after P19

The original phase sequence below is retained as architecture history. The
active route is now governed by `REAL_DATA_FEASIBILITY_STRATEGY.md`:

1. prove real-data complete-block correction feasibility under a
   preregistered nontrivial disclosure cap;
2. confirm the frozen candidate on new real blocks and independent sessions;
3. only then reduce disclosure, time and memory and revisit `f<=1.3`.

P19 showed that its registered L1 repair and L2 backoff did not recover the
three diagnostic HOLD blocks, and the true-L1 control also failed. Therefore
ordinary L1 SCL is not the automatic next phase. P20A first repairs resource
exception classification and endpoint semantics with injected tests only.
The next scientific design then isolates L2 prior, construction, disclosure
and search one factor at a time on data independent of the closed P18/P19
blocks.

This is a plan candidate. Every decoder, Model-F, real-data, or expensive
benchmark run requires a fresh review and explicit authorization. No phase is
implicitly unlocked by a previous test or commit.

Unless a phase states otherwise, numerical tolerances are absolute maximum
errors: `max(abs(actual-reference)) <= tolerance`. Internal probability
metrics use float64 natural logs; conversion to bits occurs only for entropy
and disclosure reporting.

## Phase 0 — mathematical and document alignment

Freeze the GF32/poly37/alpha2 contract, row-vector orientation, natural index
order, probability axis, Model-F concentration smoothing, `d`/`q`/`N` units,
source disclosure semantics, CAL/DEV/EVAL boundary, and verification protocol.

Reuse the existing field and counts code only through explicit adapters.
Archive the old hybrid APP draft as superseded. Do not create a result root.

Minimum checks:

- `A=32*high+low` round-trips for all `0..1023`.
- every prior row normalizes and the D4R2 formula reference agrees within
  absolute tolerance `1e-12`;
- no cell-wise-vs-column-concentration ambiguity remains;
- an audit finds no Release or LDPC production file in the implementation scope.

Gate: documentation and pure-array checks pass; all execution flags remain
false.

## Phase 1 — minimum GF(q) transform

Implement `algebra.py` and `transform.py`, retaining a slow dense reference.
Test GF4 and GF32 before optimizing. Add the source compressor that returns
`U` and selected coordinate values.

Minimum checks:

- exhaustive GF4 `N=4` transform comparison;
- exhaustive GF32 `N=2` comparison;
- random `N=8,64,256,1024` butterfly-vs-dense comparison;
- `transform(transform(x)) == x` under the frozen convention;
- alpha=2 cycle length 31 and non-zero symbol bounds.

Gate: zero transform mismatches, zero inverse mismatches, and no hidden
bit-reversal discrepancy.

## Phase 2 — reference q-ary SC and tiny oracle

Implement log-domain `f/g` recursion, known values including zero, left partial sums,
normalization, exact-zero support, and explicit metric provenance. Build a new
independent enumerator for `N<=4` and a local `N=2` GF32 oracle.

Minimum checks:

- no-public, partial-public, and all-public coordinates;
- arbitrary disclosed values, including zero;
- uniform, asymmetric, non-uniform and one-hot priors;
- SC conditional probabilities versus enumeration;
- noiseless source loopback and the surprisal-chain identity.

Gate: noiseless exact recovery 100%; SC conditional probability error at most
`1e-12`; finite log-score error at most `1e-9`; no NaN or silent uniform
fallback. Do not require SC to equal whole-block MAP.

## Phase 3 — synthetic polarized-channel construction

Add q-ary erasure and QSC synthetic generators, then genie Monte Carlo
construction with disjoint train/evaluation streams. First use easy points to
prove that correction occurs after an initially wrong Bob MAP, not merely from
truth-centered priors.

Gate: erasure recursion agrees with `epsilon_minus=2*epsilon-epsilon**2` and
`epsilon_plus=epsilon**2`; an explicitly easy `q=32,N=256` point has no more
than the pre-registered failure bound over 300 blocks; at least 80% of the
blocks have an initial Bob symbol error; no crash/nonfinite result.

## Phase 4 — Model-F adapter and two-layer diagnostic

Fit an explicit concentration prior from CAL arrays, then evaluate on disjoint
DEV/EVAL data. Run three separated diagnostics: L1 exact, oracle-L2 conditional
on true L1, and operational L2 conditional on the L1 candidate. Keep the old
`app_fed_l2_prior` out of the first SC path.

Gate: factorization and normalization error at most `1e-12`; correct-L1 L2
prior agrees with the independent conditional calculation at most `1e-12`;
no Alice truth enters the operational decoder; entropy and held-out CE are
recomputed for the selected data domain rather than copied from `7.162347`.

## Phase 5 — static reconciliation protocol

Add the thin `IRMethod` adapter, one static disclosed coordinate set, actual
symbol values including zero, full-symbol re-encoding, and one final Toeplitz
tag.
Record exact/accepted/undetected/failed-decode separately and keep public seed
bits outside key-dependent disclosure.

Engineering gate: disclosure and transcript totals are independently
recomputed; rejected and resource-aborted candidates cannot become success;
verification never chooses a decoder path.

First useful development gate: on one frozen synthetic point and 300 blocks,
the one-sided 95% exact-recovery lower bound is at least 90%, and average
key-dependent disclosure is below the raw `10*N` input bits. This is a
development signal, not qualification.

## Phase 6 — nested disclosure and rate adaptation

Freeze `D0 subset D1 subset ...`, but initially run one static level. Later add
one fixed incremental schedule with restart-from-scratch SC. Count each
coordinate once, count every verification invocation, and report public control
separately.

Gate: set nesting, disclosure arithmetic, and verification failure bound all
recompute exactly; no candidate-selection-by-tag; at a paired fixed point,
average disclosure improves at least 5% without a pre-registered FER tolerance
breach. Do not assume every individual frame is monotonic.

## Phase 7 — ordinary q-ary SCL and measured optimization

Only after reference SC/protocol gates pass **and** true-L1-conditioned L2 is
recoverable at a meaningful real-data feasibility point, add ordinary q-ary SCL with
`L in {1,4,8}`. `L=1` must equal SC. Use tiny MAP cases to test path pruning,
known coordinates and path metrics. Profile q32/N64,256,1024 before any
convolution or FWHT optimization. Cross-family comparison with binary Polar or
NB-LDPC is deferred to the sibling Comparison route owner and is not an active
gate in this checkout.

Promotion inside this checkout first requires preregistered real-data complete-
block recovery, independent-session repetition and an accepted runtime/memory
ceiling. Efficiency criteria follow only after that. A passing unit test is
not a performance or qualification claim.

## Stop and attribution rules

- If Phase 1 or 2 fails, debug field/orientation/partial-sum semantics before
  touching construction or prior fitting.
- If Phase 3 fails with a verified SC oracle, inspect construction and metric
  mismatch before adding SCL.
- If Phase 4 fails, inspect axes, smoothing, support and provenance before
  blaming Polar.
- If Phase 5 fails, inspect disclosure units, symbol packing and verification
  accounting before adding adaptation.
- A route stop must name the tested field, kernel, N, metric, construction,
  decoder and budget. It must not be generalized to GF32, NB-Polar, or
  NB-LDPC as a whole.
