# Heavy task packet — Phase 6 fixed incremental disclosure

## Mission

Determine whether one preregistered nested-disclosure schedule reduces average
key-dependent disclosure by at least 5% while preserving the Phase 5 synthetic
development recovery signal. The packet is inert until the exact user grant in
`AUTHORIZATION_PROMPT.md` is supplied.

## Frozen contract

- GF32/poly37/alpha2, natural order, N=256, erasure epsilon=0.05.
- Physical labels `32*x_hat`; Toeplitz message domain 2560 bits.
- Worst-first order from `analytic_order(0.05,256)`.
- Nested sizes `K=(29,33,37,41,45)`.
- Publish only `D_i - D_{i-1}` with actual GF32 values, including zero.
- Restart reference SC from scratch at every invoked level.
- One independent 64-bit Toeplitz verification per invoked level.
- Match accepts; mismatch discards and advances only to the immediately next
  frozen level. No candidate ranking/selection, skipped level or decoder change.

## Allowed files

- `formal_ir/nbpolar/incremental.py`
- `methods/nbpolar_incremental.py`
- `tests/test_nbpolar_incremental.py`
- `formal_ir/nbpolar/__init__.py` only for explicit exports
- this Phase 6 OpenSpec and queue directory
- required lifecycle/index/decision/troubleshooting/project-memory documents

Phase 5 code may be changed only for a concrete reusable defect proven by a
failing predecessor test; otherwise reuse it unchanged. Frozen Phase 5 evidence
is read-only.

## Acceptance IDs

- **P6-A01** all five sets equal the corresponding analytic-order prefixes and are strictly nested.
- **P6-A02** only new coordinate/value pairs are transmitted; zeros round-trip.
- **P6-A03** each invoked SC starts from original Bob metrics with empty decoder state.
- **P6-A04** a tag mismatch advances exactly one level and never selects among candidates.
- **P6-A05** a matching non-exact candidate is undetected and never success.
- **P6-A06** final mismatch is verify-failed; resource/decode failures stop fail-closed.
- **P6-A07** cumulative disclosure is `5*K_final + 64*n_verify` and independently recounts exactly.
- **P6-A08** public seed/control and verification union bound count every invocation.
- **P6-A09** outcome buckets are disjoint and exhaustive; truth leak/nonfinite are zero.
- **P6-A10** paired arms consume identical blocks in identical order.
- **P6-A11** existing public type signatures and Phase 5 behavior remain unchanged.
- **P6-A12** tiny exhaustive, mutation/tamper, restart and predecessor suites pass.

## Autonomous work before execution

Implement the minimum fixed scheduler and thin adapter. On injected/synthetic
data, exercise pass at each level, all-level failure, false tag match,
decode/resource failure, arbitrary disclosed zeros and transcript tampering.
Instrument SC entry in tests to prove fresh state. Profile paired execution at
N=256 and use it only to freeze a safe budget. Do not search K, epsilon, N,
construction, tag size or thresholds.

## Pre-EXECUTE

Freeze one new run seed and one public Toeplitz master absent from all accepted
streams; deterministic independent per-arm/per-block/per-level seed derivation;
the full 300-block paired matrix; exact command; absent additive output root;
attempt-consumption point; budget/stop rules; compact scalar-only output schema;
outcome precedence; Wilson and 5% calculations. An independent reviewer must
PASS and prove forbidden inputs/roots unreachable. FAIL blocks execution.

## Single paired development attempt

Run static K45 and incremental arms on the same 300 newly generated blocks.
The paired static arm is an in-run comparator, not the immutable Phase 5 root.
Consume attempt 1/1 at the first scientific SC call. Never rerun or tune.

Candidate requires all:

1. incremental undetected = 0;
2. incremental exact >=285/300 and one-sided 95% Wilson LB >=0.90;
3. incremental average key-dependent bits <=0.95 times paired-static average;
4. exhaustive/disjoint outcomes and complete paired coverage;
5. zero transcript/invocation/union-bound mismatch, truth leak and nonfinite;
6. all resource and frozen-order/nesting gates true.

Persist only the frozen plan, per-block scalar paired outcomes, accounting
summary, aggregate comparison and bounded report. Never persist symbols,
labels, disclosed values, decoded keys or raw seed bits.

## Pre-RESULT and return

An independent reviewer recomputes paired identity, outcome totals, Wilson
bound, average disclosure delta, invocation universe, union bound and transcript
recount from actual artifacts. FAIL blocks solidification.

Return only `FIXED_INCREMENTAL_DEVELOPMENT_CANDIDATE` or
`BLOCKED(<single earliest gate>)` with raw failure, attempt/seed state, unrun
stages and the one main-thread decision required. No commit or push.
