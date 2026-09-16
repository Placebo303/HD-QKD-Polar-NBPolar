# OPERATOR_RETURN — NBPOLAR-PHASE6-FIXED-INCREMENTAL

Operator session 2026-09-13 (WSL). Frozen packet returned as
**`BLOCKED(incremental_exact_ge_285)`**. This is a negative development result
awaiting main-thread disposition; it claims no acceptance, FER, leakage
efficiency, key rate, qualification or promotion.

## 1. Mission

Determine whether one preregistered nested-disclosure schedule reduces average
key-dependent disclosure by at least 5% while preserving the accepted Phase 5
synthetic development recovery signal. This was the packet's single authorized
paired 300-block development gate.

## 2. Implementation summary

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`
  (core + CLI, new).
- `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py`
  (thin `IRMethod` adapter, new).
- `comparison_bench/tests/test_nbpolar_incremental.py` (17 tests, new;
  P6-A01..A12 + refusals).
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py`
  (explicit Phase 6 aliases only).
- Test suites: focused 17 passed; full NB-Polar suite 153 passed
  (17 + 136 predecessors). No Phase 5 code was modified.

## 3. Frozen schedule and identity

- Point: GF32/poly37/alpha2, natural order, N=256, erasure epsilon=0.05;
  physical labels `32*x_hat`; Toeplitz message domain 2560 bits.
- Nested schedule `K=(29,33,37,41,45)`; worst-first `analytic_order(0.05,256)`;
  `D_5` equals the accepted Phase 5 static K=45 set.
- Run seed `2026091340` (consumed at the first `sc_decode`, static comparator
  block 0); Toeplitz master `2026091341` (public control).
- Command (frozen, executed once):
  ```
  cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
  ulimit -v 2097152
  timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental --mode paired-dev-gate --run-seed 2026091340 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate
  ```
- Output root:
  `.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`

## 4. Run result (single paired attempt, exit 0)

Paired identical 300 blocks: 300/300 `paired_match`.

| bucket | static K=45 | incremental |
|---|---|---|
| exact | 298 | 271 |
| decode_failed | 2 | 29 |
| undetected | 0 | 0 |
| verify_failed | 0 | 0 |
| resource_abort | 0 | 0 |
| sum | 300 | 300 |

- Static arm: average key-dependent bits 288.573333 (`298*289 + 2*225`);
  Wilson one-sided 95% LB `0.9800565738801275`; 298 tag invocations.
- Incremental arm: average key-dependent bits 207.293333; Wilson one-sided 95%
  LB `0.8715597837542944`; 287 tag invocations; 16 feedback invocations
  (16 bits); undetected 0; verify_failed 0; resource_abort 0.
- Disclosure: integer rule `6218800 <= 8224340` holds; saving fraction
  `0.281661507` (28.2% key-dependent disclosure saved versus the paired static
  arm).
- Transcript recount mismatch 0/0 (sha256 both arms); union bound
  `3.1712913545201005e-17` over 585 tag invocations; truth leak 0; nonfinite 0.
- Wall 9.619874 s; peak RSS 111816704 B (advisory — see §8 N-2).
- All 29 static and incremental decode failures were
  `ImpossibleDisclosedValueError` at invoked level 0.

## 5. Failing gates and earliest failure

18 hard gates persisted; 16 true, 2 false:

| gate | observed | threshold | result |
|---|---|---|---|
| `incremental_exact_ge_285` | 271 | >= 285 | False (shortfall 14) |
| `incremental_wilson_lower_ge_0_90` | 0.8715597837542944 | >= 0.90 | False |

Frozen gate order makes **`incremental_exact_ge_285` the earliest failing
gate**; `candidate` is `null`.

## 6. Failure-mechanism audit (Pre-RESULT §6)

The 29 level-0 `decode_failed` are a valid scheduled-science result, not an
implementation defect. On a q-ary erasure channel the true disclosed value
always has positive posterior mass under the true prefix; an exact-zero support
for a true `U[D_1]` value implies an earlier wrong SC decision (prefix error
propagation). The accepted `sc.py` raises `ImpossibleDisclosedValueError`, and
the frozen fail-closed rule terminates the block at level 0. Reproduced on
injected seeds with a harness spy (true `U[D1]`, unmutated Bob metric, 0 tags,
145 bits). No tuning, threshold, K, epsilon, N or seed change was made or is
permitted.

## 7. Attempt and seed accounting

- Attempt 1/1 consumed at the first scientific `sc_decode` (static comparator
  arm, block 0); no rerun, seed change, tuning or partial credit.
- Run seed `2026091340` consumed; Toeplitz master `2026091341` is public
  control.
- `STATUS.yaml` now records `attempts_used: 1`.

## 8. Review verdicts

- **Pre-EXECUTE: PASS** (`PRE_EXECUTE_REVIEW.md`); all 12 checks pass, 4
  non-blocking findings (F-1 RSS `ru_maxrss` quirk, F-2 one vacuous test
  assertion, F-3 doc import-list omission, F-4 `paired_match` on aborted pairs).
- **Pre-RESULT: PASS_WITH_COMMENTS** (`PRE_RESULT_REVIEW.md`); artifacts
  self-consistent, recomputed numbers match, gate failure genuine.
  - N-1 closeout (this `STATUS.yaml`/`OPERATOR_RETURN.md`).
  - N-2 RSS advisory; not gate-bearing.
  - N-3 one vacuous test assertion at `tests/test_nbpolar_incremental.py:766`
    (carried, not fixed under the freeze).
  - N-4 Wilson float vs Decimal 1-ulp note; no action.

## 9. Output files

| file | bytes |
|---|---|
| `frozen_plan.json` | 6640 |
| `per_block_paired_outcomes.json` | 470477 |
| `transcript_accounting.json` | 1810 |
| `aggregate_comparison.json` | 4822 |
| `report.md` | 2314 |

## 10. Bounded scope

Synthetic paired development signal only. This is **not** real-data FER,
leakage-efficiency, key-rate, qualification or promotion evidence. The real
output root was absent before the run and was created only by this authorized
attempt. Model-F artifact, real data, DEV/EVAL, sibling checkouts, `results/`,
`comparison_bench/outputs_comparison/` and the immutable Phase 5 evidence root
were not read or written. No commit or push.

## 11. Unrun stages

None. All packet stages (implementation, tests, profile, independent
Pre-EXECUTE, the single paired development attempt, independent Pre-RESULT)
were executed. Only main-thread disposition remains.

## 12. One main-thread decision requested

Disposition of the negative result. All candidate dispositions are design
changes the operator may not make:

- **(a)** successor OpenSpec/packet that redefines decode-failure handling as
  level-advance reject semantics;
- **(b)** successor with a different frozen K schedule / early safety level;
- **(c)** accept the negative result and close the route.

No commit or push was performed; none is requested.
