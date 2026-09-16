# Phase 4-P11 Tier-Y packet — exact chunked SC allocation gate

## Mission

Promote X12's bitwise-equivalent row chunking into the accepted reference SC
implementation as an allocation-only change, then execute one frozen synthetic
engineering gate proving semantic parity and N=2^18 reachability. This does not
change the decoder algorithm or establish target-channel FER/efficiency.

## P11-01 — OpenSpec and owned files

Add a P11 delta/tasks section before production edits. Allowed implementation
files:

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py`;
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc_chunked_gate.py`
  as a thin injected-data gate runner with no production default;
- `comparison_bench/tests/test_nbpolar_sc.py` and, only if already the canonical
  SC test location requires it, one new focused `test_nbpolar_sc_chunked.py`;
- P11 OpenSpec delta/tasks and this queue directory's lifecycle documents.

No prior/artifact/construction/protocol/two-layer/adaptive/target-rate/module
logic or old evidence root may change.

## P11-02 — Frozen implementation contract

Change only `_minus_block` allocation:

- retain the accepted expression, dtype and reduction order;
- add keyword-only `chunk_rows` with production default exactly `512`;
- process contiguous row slices in original order, each using
  `first_slice[:, index] + second_slice[:, None, :]`,
  `np.logaddexp.reduce(..., axis=2)`, and accepted `_normalize_rows`;
- `chunk_rows=None` invokes the original unchunked expression and exists only
  as the golden comparator for tests/gate;
- reject bool/non-integral/nonpositive explicit chunk sizes with a clear
  `TypeError`/`ValueError` before allocation;
- do not add FWHT, clipping, caching, reordered summation, dynamic-range logic,
  approximation, environment configuration, or a public `sc_decode` option.

`sc_decode` continues calling `_minus_block` without a new public argument, so
the existing public signature and all result/provenance schemas remain stable.

## P11-03 — Focused tests

Use injected arrays only. Cover chunk sizes 32/128/512/2048; row boundaries
1/31/32/33/127/128/129/511/512/513/2048; finite moderate/wide and exact `-inf`
support; exact array equality against `chunk_rows=None`; N=64/256 full-SC
equality for moderate, wide, mixed support, known coordinates, X11-C3,
impossible disclosure, near/exact ties, and invalid/nonfinite inputs; default
is 512; original public signature unchanged; invalid chunk sizes rejected.

Run focused tests and the complete accepted 252-test NB-Polar predecessor
suite with temporary writable roots and no production input/output.

## P11-04 — Frozen one-shot engineering gate

Gate seed: `2026091800`; NumPy float64; GF(32) polynomial 37; alpha=2. Before
execution freeze exact implementation, tests, command, output schema, target
absence and resource checks in `P11_FREEZE.md`, then obtain independent
reviewer-go Pre-EXECUTE PASS.

The single scientific/engineering attempt is consumed at the first formal
`sc_decode` call. No artifact read is authorized or consumed.

The one execution performs:

1. the frozen injected semantic matrix from P11-03 for default 512 versus
   `chunk_rows=None` and requires exact equality/exception parity everywhere;
2. one paired N=65536 moderate all-finite block, direct first then default-512,
   requiring exact `u_hat`, `x_hat`, decision metrics/scores, status and
   provenance equality;
3. one default-512 N=262144 moderate all-finite block requiring status `ok`,
   finite outputs, no resource failure, and process peak RSS below
   1,610,612,736 bytes (1.5 GiB). Record, but do not gate on, the planning
   targets decode wall <=120 seconds and RSS <=1 GiB.

The hard large-N completion/RSS gates are supported by X12's 65.73-second and
754.6-MB cumulative-HWM observations. One draw cannot discriminate timing
variance, so the 120-second/1-GiB values are report-only and no throughput
superiority claim is allowed. The complete command must also finish within its
600-second timeout.

Resource envelope: `ulimit -v 2097152`, total timeout 600 seconds. Any semantic
mismatch, resource abort, threshold miss, test/review failure or unexpected
existing root returns the earliest `BLOCKED(<gate>)`; never rerun or retune.

## P11-05 — Outputs and result labels

Absent root:

`.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/`

Create exactly four compact files:

1. `frozen_plan.json`
2. `equivalence_records.json`
3. `scaling_record.json`
4. `report.md`

Persist parameters, environment, every semantic comparison, exceptions,
large-N wall/RSS, attempt/seed accounting, gates and bounded wording. No input
vectors, decisions, metrics, decoded keys, raw arrays, or artifacts.

All frozen gates true returns `EXACT_CHUNKED_SC_CANDIDATE`. A candidate remains
pending main-thread acceptance. Independent reviewer-go Pre-RESULT must
recompute the recorded equivalence/resource facts before return.

## P11-06 — Command

Freeze and execute exactly these three lines:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc_chunked_gate --seed 2026091800 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate
```

The runner must require every argument and have no production default.
Pre-EXECUTE confirms byte-equivalence between this command and `P11_FREEZE.md`.

## P11-07 — Boundaries and STOP

Forbidden: artifact/evidence-root/raw/held-out/real/EVAL access; official prior
seeds; tag/protocol execution; N>262144; FWHT/APP/SCL; FER/efficiency/key-rate,
qualification or promotion claims; old-root edits; commit/push.

STOP after full completion or on a concrete blocker. No repair, cleanup, seed
change, chunk change, threshold change, or rerun after attempt consumption.

## Return contract

Return candidate or blocker with changed files, tests, both independent review
verdicts, attempt/seed accounting, semantic matrix totals, N65536 parity,
N262144 wall/RSS, gates, four-file inventory, unrun stages and scope.
