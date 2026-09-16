# Phase 4-X12 Tier-X packet — exact chunked direct-SC scaling probe

## Mission

After X11 rejected FWHT as an exact SC replacement, test the simplest
semantics-preserving scaling lever: evaluate the accepted q²
`logaddexp.reduce` minus-node in row chunks without changing any per-row
operation or reduction order. Measure bitwise equivalence and the reachable N
ceiling through N=2^18. This is non-claim engineering exploration.

## X12-01 — Strict Tier-X boundary

Write only:

- `workspace/probes/nbpolar_x12_exact_chunked_sc_scaling/prereg.md`
- `workspace/probes/nbpolar_x12_exact_chunked_sc_scaling/results.json`

Freeze exactly three top-level preregistration lines—question, exact parameters,
exact command—with the complete stdlib+NumPy body embedded before any probe
call. No production/test/OpenSpec/ledger/memory/index edit; no artifact,
evidence-root, official seed, raw/held-out/real/EVAL data, tag, APP/SCL/FWHT, or
scientific gate. No attempt, threshold, winner, candidate, or acceptance.

## X12-02 — Frozen exact chunk implementation

Use GF(32), primitive polynomial 37, alpha=2, float64, and the accepted
`_combination_index`. Implement a probe-local `_minus_block_chunked` that, for
each contiguous row slice only, executes the exact accepted expression:

`gathered = first[:, index] + second[:, None, :]`

then the same `np.logaddexp.reduce(gathered, axis=2)` and accepted row
normalization. It must not change axis order, dtype, field tables, support,
tie-breaking, or exception behavior. Chunking controls allocation only.

Temporarily monkeypatch `sc._minus_block` inside `try/finally`; restore and
verify the original function identity after every run and at process end.

## X12-03 — Frozen equivalence matrix

Probe seed `2026091780`; chunk-row values `[32,128,512,2048]`.

Primitive comparisons use row counts `[1,31,32,33,127,128,129,511,512,513,2048,8192]`
and three inputs: all-finite uniform logits [-20,0], finite wide [-160,0], and
deterministic `-inf` support with at least one finite entry per row. Compare
direct and every chunk size using exact array equality plus maximum finite
absolute error and support masks.

Full-SC semantic controls at N=64 and N=256 cover: moderate finite metrics;
wide finite metrics; registered `-inf` support; 25% known coordinates selected
from direct-positive support; the X11 C3 pattern; impossible disclosure; and
near/exact ties. For every chunk size compare exception type/message, status,
`u_hat`, `x_hat`, decision metrics/scores, known mask/count and provenance.
Also exercise the accepted invalid/nonfinite input-validation contract before
monkeypatch entry and require identical exception type/message.

## X12-04 — Frozen scaling matrix

Generate one normalized all-finite uniform-[-20,0] block per N using the same
probe RNG stream.

- Direct and chunk=512 paired runs at N `[1024,4096,16384,65536]`.
- Chunk=512 only at N `[131072,262144]`.
- Exactly 3 timed repetitions per arm through N=16384; exactly 1 per arm at
  N>=65536. Direct always runs before chunked at a given large N to keep the
  order frozen; timing is descriptive, not a winner claim.
- Record wall time and process peak RSS. A resource failure at a registered N
  is a descriptive ceiling result, not permission to change N/chunk/limits.

Resource bounds: 2 GiB virtual memory, 1800 seconds wall.

## X12-05 — Durable STOP behavior and results

Initialize `results.json` before the first semantic control and rewrite the same
single JSON record after every completed control/cell. On exception or resource
STOP, record the exact completed stages and blocker before returning; do not
discard already measured values as X11 did. This is simple checkpointing of one
result record, not an extra artifact or retry framework.

Persist all primitive/full-SC equality fields, raw timings, medians where
defined, RSS, estimated direct gather and chunked temporary bytes, restoration
checks, execution/error/rerun accounting, and the highest completed N. Report
descriptive observations only.

## X12-06 — Independent focused review

Obtain independent `reviewer-go` review in the return message without a third
file. It independently reconstructs primitive boundary sizes and all N=64
semantic controls, checks bitwise/exception parity, recomputes timing/RSS and
memory summaries, verifies durable result completeness and function
restoration, and confirms the two-file write scope and zero forbidden access.
Its explicit evidence is trusted by the main thread.

One execution-error rerun is allowed only with unchanged frozen parameters,
seed and semantics, and both executions recorded. A semantic mismatch is not
an execution error: STOP without rerun. STOP also on restoration failure,
external-input need, or production-edit requirement. No commit/push.

## Return contract

Return `X12 complete` or a concrete blocker. Include two-file inventory,
execution accounting, bitwise/exception parity, chunk-boundary results,
timing/RSS and memory table, highest completed N, independent review, and a
recommendation for or against a Tier-Y exact-chunked `sc.py` implementation.
