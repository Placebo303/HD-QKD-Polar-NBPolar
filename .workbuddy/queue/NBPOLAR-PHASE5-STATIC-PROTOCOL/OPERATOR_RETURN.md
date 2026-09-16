# Operator return — NBPOLAR-PHASE5-STATIC-PROTOCOL

Candidate label: **`STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE`** (synthetic
development signal only; NOT acceptance). Returned by the operator session,
2026-09-13, from `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`. No commit and no
push were performed.

## 1. Mission

Implement and measure the smallest scientifically valid static NB-Polar
reconciliation protocol: publish the actual GF32 values of the frozen 45-coordinate
disclosure set, SC-reconstruct the remaining 211 coordinates, run at most one
64-bit Toeplitz verification after decode, and account key-dependent versus
public-control disclosure — with one preregistered 300-block synthetic
development gate. The main thread owns acceptance and scientific conclusions.

## 2. Implementation

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/protocol.py` — static
  protocol core: per-block protocol, disjoint/exhaustive outcome accounting,
  transcript recount, truth-isolation sentinel, budget/resource-stop handling and
  the dev-gate CLI.
- `comparison_bench/src/comparison_bench/methods/nbpolar_static.py` — thin
  `IRMethod` adapter over the core; refuses `verify_mode != "toeplitz64"`; metric
  built from the observation only.
- `comparison_bench/tests/test_nbpolar_protocol.py` — 16 focused tests covering
  P5-A01..A11 plus refusals, resource abort, Wilson values, five-file schema and
  forbidden-marker scan.
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` — explicit
  re-exports only.

Tests: 16 focused passed; full NB-Polar suite 136 passed = 16 new + 120
predecessor (identical counts independently reproduced by both reviewers).
Existing `FrameBatch`/`IRRunConfig`/`IRRunResult` signatures unchanged; no SCL,
CRC, retry, adaptation or rate scan.

## 3. Freeze identity

- **R1 (disclosure orientation).** Disclosed set
  `D = analytic_order(0.05, 256)[:45]` — the 45 highest-risk coordinates
  (worst-first slice), SC-reconstruct the remaining 211. This matches the accepted
  Phase 3 `evaluate_blocks(..., k=45)` convention and `ARCHITECTURE.md`; the
  packet/design "disclose the complement" wording is superseded (see
  `P5_FREEZE.md` §0 and `docs/decision-log.md`, 2026-09-13).
- **R2 (label domain).** Physical label `label_j = 32 * x_hat_j` (10-bit
  single-layer embedding, low half constant zero); verification message domain
  `10*N = 2560` bits; Toeplitz seed `2560 + 63 = 2623` public-control bits per
  block.
- Frozen point: GF32 polynomial 37, alpha 2, natural order, `N=256`, `K=45`,
  `epsilon=0.05`.

## 4. Exact frozen command

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol --mode dev-gate --run-seed 2026091317 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate
```

No flags added or changed; output root was absent at execution and produced a
single generation (all five file mtimes 2026-09-13 02:31:13).

## 5. Run result summary

- Outcome totals: exact 300 / undetected 0 / verify_failed 0 / decode_failed 0 /
  resource_abort 0; attempted 300 of 300, coverage 1.0; buckets disjoint and
  exhaustive.
- Wilson one-sided 95% lower bound (exact recovery, 300/300):
  `0.9910621278248719` (reviewer Decimal recomputation
  `0.99106212782487182232487…`, difference 7.8e-17); threshold 0.90.
- Disclosure: average key-dependent 289.0 bits per attempted block (< `10*N` =
  2560); key-dependent total 86700 (= 300 × 289); public-control total 786900
  (= 300 × 2623).
- Transcript recount mismatch 0; transcript sha256
  `767418d2670fb1f7e36d71a23ab1afb4593ec6164aef62bce5d97f5b7903b048`.
- Truth-leak violations 0; nonfinite 0; `resource_stop_fired` false.
- Wall 4.998916 s (< 300 s); peak RSS 111190016 B (< 2 GiB envelope).
- Hard gates: 11/11 true. Candidate label `STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE`.

## 6. Attempt and seed accounting

- Single attempt consumed at the first scientific `sc_decode` call of the frozen
  command (1/1); no rerun, no parameter tuning, no seed change, no partial credit.
- Run seed **2026091317** consumed by this run only.
- Toeplitz master seed **2026091318** is public control; per-block seeds derived
  deterministically (SHA-256 counter mode) and never persisted raw.
- `STATUS.yaml` `attempts_used` corrected `0 → 1` in this closeout (R-1); this
  closes the only mandatory Pre-RESULT closeout item.

## 7. Review verdicts

- **Pre-EXECUTE** (`PRE_EXECUTE_REVIEW.md`): **PASS** — independent
  reviewer-go; frozen record, command, root-absence, budget and code all
  independently verified; no blocking issues; executed command was NOT run by the
  reviewer.
- **Pre-RESULT** (`PRE_RESULT_REVIEW.md`): **PASS_WITH_COMMENTS** — fresh
  independent reviewer; all outcome totals, per-block disclosure, transcript
  recount, Wilson bound and 11 gates independently recomputed from the five
  persisted files and matched; `undetected` isolated; no private/raw content.
- Closeout item **R-1** (`attempts_used 0 → 1`) is the only required correction
  and is completed by this return. **R-2** and **R-3** are cosmetic/optional and
  require no artifact change.

## 8. Output files (evidence root, read-only)

`.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/`

| file | bytes |
|---|---|
| `frozen_plan.json` | 2028 |
| `per_block_outcomes.json` | 103070 |
| `transcript_accounting.json` | 391 |
| `aggregate_summary.json` | 1999 |
| `report.md` | 1524 |

No symbol vectors, decoded keys, per-block disclosed value lists, per-block
Toeplitz seed contents or raw transcript events are persisted.

## 9. Bounded scope

`STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE` is a synthetic development signal only.
It is not real-data FER, leakage efficiency, reconciliation efficiency, key rate,
qualification, promotion, or evidence for adaptive disclosure. No construction,
K-selection or performance claim is made.

## 10. Execution observations adjudicated

- **(a)** `frozen_plan.json` has no `command` / `attempts_used` key — **not a
  defect**: freeze §6.1 defines exactly those 19 keys; the command lives in
  `P5_FREEZE.md` §8 and attempt state in `STATUS.yaml`.
- **(b)** `STATUS.yaml` still showed `attempts_used: 0` after the run — a
  closeout-owned correction; **fixed by this return** (`0 → 1`, R-1).
- **(c)** no literal `hard_gates_pass` key — **not a defect**: freeze §7 requires
  11 booleans in `hard_gates{}`; the candidate rule is `all(gates.values())`.

## 11. Forbidden writes / later stages

- No code, no frozen `src/`/`experiments/`/`tools/`, no `results/`,
  `comparison_bench/outputs_comparison/`, no sibling checkout, no Model-F
  artifact and no real data were modified or touched; no commit and no push.
- Later stages: **none** in this packet. Only main-thread acceptance remains;
  real data, DEV/EVAL and Phase 6 stay closed.
