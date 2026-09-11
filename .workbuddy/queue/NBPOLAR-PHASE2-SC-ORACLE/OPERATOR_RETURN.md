# OPERATOR_RETURN — NBPOLAR-PHASE2-SC-ORACLE

Terminal: IMPLEMENTATION_CANDIDATE

## 1. Terminal

`IMPLEMENTATION_CANDIDATE`. All P2 acceptance IDs pass. This return does
not accept the work and does not unlock Phase 3.

## 2. Changed files and line counts

| File | Lines | Note |
|------|-------|------|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py` | 257 (new) | reference SC, contracts, result type |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/oracle.py` | 150 (new) | independent exhaustive oracle + evidence comparator |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` | 20 (edited, +6) | export Phase 2 API only |
| `comparison_bench/tests/test_nbpolar_sc.py` | 616 (new) | 16 focused tests, plain-python runnable |
| `.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/EXPLORATION_NOTES.md` | (new) | design evidence |
| `.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/STATUS.yaml` | (edited) | → `IMPLEMENTATION_CANDIDATE` |

Phase 1 `algebra.py`/`transform.py` unmodified. No commit, no push.

## 3. Selected API and recursion design

`sc_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None)
-> SCResult`. Pure recursive segment function over contiguous `(m,q)`
blocks; one `(q,q)` combination index per decode; vectorized
minus (`logsumexp_v L0[u+αv]+L1[v]`) and plus (`L0[beta+αv]+L1[v]`) with
per-row normalization; partial sums via accepted `polar_transform` on
decoded left-U segments; natural-order concat; leaf-only known forcing
(dict position→value, zero is a value); argmax ties to smallest index.
`SCResult`: `u_hat`, `x_hat`, `status="ok"`, `decision_metrics`,
`decision_log_scores`, `metric_provenance` (prior input role, SC
conditional row role, natural log base), `known_count`, `known_mask`. No
`final_beliefs`/`APP`. Rejected: node-object tree with cached buffers
(same algebra, ~3× code, stack-order risk, no N≤64 benefit).

## 4. Acceptance table

| ID | Result | Evidence |
|----|--------|----------|
| P2-T0-01 | PASS | `py_compile` OK on all 4 files; `test_nbpolar_transform.py` 17/17 unchanged; new suite 16/16; `__all__` exact 11-name set; imports create no files |
| P2-T0-02 | PASS | shape/dtype/q-N/NaN/+inf/all-`-inf`/bool rejected with `metric` or `field/shape` contract; unnormalized finite rows explicitly normalized; post-decode `max\|lse\| ≤ 1e-12`; `-inf` preserved |
| P2-T1-01 | PASS | GF4 81² finite pairs + masked `-inf` variants + 4 GF32 representative pairs (4 representative betas each: 0, 1, 17, 31): prob ≤ 3.4e-16, log ≤ 1.8e-15, support exact, no NaN |
| P2-T1-02 | PASS | 221 production-vs-oracle row comparisons (GF4 N=2/N=4, GF32 N=2; none/partial/interleaved/all known; forced zero, non-MAP, off-MAP prefixes): max prob 3.331e-16, max log 1.776e-15, 0 support mismatches |
| P2-T1-03 | PASS | frozen GF4 N=4 metric; `beta=[1,3]` vs raw `[0,3]`; production U_2 matches oracle to 1.1e-16 (MAP 1); raw-beta row misses by 0.32 prob (MAP 2) and trips the comparator |
| P2-T1-04 | PASS | empty/sparse/interleaved/all-known; forced zero chosen; non-MAP forced with oracle agreement downstream; shuffled input order identical; 9 malformed inputs fail with `known-coordinate` contract; later knowns leave earlier rows bitwise equal |
| P2-T1-05 | PASS | 831/831 exact `u_hat`+`x_hat` (below); decoder takes disclosed positions/values only, truth never enters |
| P2-T1-06 | PASS | frozen metric below: X-MAP errs at row 3, undisclosed SC echoes it, one disclosed U coordinate recovers the full block |
| P2-T1-07 | PASS | GF4 N=4 ×2 + GF32 N=2 chain-vs-block within 1e-9; one-hot contradiction gives all-`-inf` oracle row and `ImpossibleDisclosedValueError` |
| P2-T1-08 | PASS | metric (NaN), field/shape (bad field, bool alpha), known (2-D positions), impossible-disclosed, numeric (`_normalize_rows` NaN → `NumericNonfiniteError`; all-`-inf` kept for leaf attribution) — each in its stable category |
| P2-T1-09 | PASS | scoped `rg` over the 3 production files: zero hits; `final_beliefs`/`APP` substrings absent; oracle source has no `sc` import or minus/plus references |
| P2-T1-10 | PASS | GF32 N=64 noiseless 0.004 s, asymmetric 0.009 s; `(64,32)` rows normalized; no tuning |

## 5. Pytest and compile commands/results

- `.venv` absent in this container; WSL venv
  `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` (numpy
  2.4.4, no pytest) ran the plain-python runners.
- `PYTHONPATH=<root> …/bin/python comparison_bench/tests/test_nbpolar_sc.py`
  → `16 passed`; oracle 221 comparisons; loopback 831/831; N=64 times above.
- Official path:
  `PYTHONPATH="D:\Code\HD-QKD_Polar_Comparison-nbpolar"
  "/mnt/d/software/Miniforge3/python.exe" -m pytest -q -p no:cacheprovider
  <transform test> <sc test>` → `33 passed, 1 warning in 21.28s`
  (17 Phase 1 + 16 Phase 2; warning is the known unrelated
  `cache_dir`/`PytestConfigWarning`).
- `python -m py_compile` on all 4 new/edited files → `COMPILE_OK`.
- `git diff --check` on scope → clean.

## 6. Oracle errors and support

221 comparisons: maximum probability error 3.331e-16 (gate 1e-12),
maximum finite log-score error 1.776e-15 (gate 1e-9), support mismatches
0, NaN 0.

## 7. Noiseless exact counts by field/N/known pattern

GF4 N=4 exhaustive (256 U words × none/partial-{0,2}/all): 768/768.
GF32 deterministic: N=2 (8×3) 24/24, N=4 (6×3) 18/18, N=8 (4×3) 12/12,
N=64 (3×3) 9/9. Total 831/831 `u_hat` and `x_hat` exact (100%).

## 8. Partial-sum discriminator identity

Metric rows `[-1,-2,-3,-3],[-2,0,-1,-1],[-2,-2,-3,-2],[-1,0,-2,-2]`
(GF4, N=4): production `u_hat=[0,3,1,1]`, `beta=[1,3]≠[0,3]=raw`;
oracle U_2 at prefix `[0,3]` MAP 1, production matches to 1.1e-16;
raw-beta reconstruction MAP 2, prob error 0.32, fails the comparator —
the suite would fail for the wrong implementation.

## 9. Nontrivial correction example summary

Frozen metric rows
`[-1.5,-1.5,-1.5,0.5],[-1.5,-1.5,0.5,-1.5],[-1.5,-1.5,0.5,-1.5],[-1.0,-1.0,-1.0,0.5]`
(GF4, N=4): planted `U=[0,0,0,1]`/`X=[3,2,2,1]`; X-MAP `[3,2,2,3]`
errs at row 3; undisclosed SC gives `[1,3,3,3]` (echoes MAP); disclosing
`{U_0:0}` recovers `U` and `X` exactly. Correction beyond pointwise MAP,
no performance claim.

## 10. N=64 sanity time

Noiseless one-hot 0.004 s; finite asymmetric 0.009 s; both < 30 s gate
by three orders of magnitude. Peak block `(32,32,32)` float64 ≈ 256 KiB.

## 11. Frozen-directory and forbidden-coupling audit

`git diff --stat -- src experiments tools results
comparison_bench/outputs_comparison` → empty. Scoped `rg` (packet §8
pattern incl. `SCL`, `Model-F`, `IRRunResult`) over
`formal_ir/nbpolar` → zero hits (exit 1). Unrelated pre-existing dirty
entries (`AGENTS.md`, `AGENT_PROJECT_MEMORY.md`, etc.) preserved
untouched; no production output directory created.

## 12. Known limitations and rejected alternatives

- Support contradiction through the public API always surfaces as
  impossible-disclosed-value (conditional-consistency argument in
  exploration notes); the numeric category guards internal arithmetic.
- N=1 covered as a bonus; generic-alpha argument retained from Phase 1
  discipline but only alpha=2 tested.
- Rejected: node-object recursion, per-element field calls, `metrics.py`
  split, oracle-in-test-helper layout.
- First probe-side mismatches (internal-row vs leaf comparison,
  max- vs logsumexp normalization, one hand-derived expectation) were
  classified before editing; no production-logic change resulted.

## 13. Next gate

Next gate: INDEPENDENT_IMPLEMENTATION_REVIEW

## 14. Authorization boundary

Phase 3, Model-F, CAL/VAL/TTBin and real data, benchmark/result roots,
SCL, construction, rate adaptation, protocol, qualification, commits,
pushes, and every scientific conclusion remain closed and untouched. No
decoder object beyond the reference SC exists; no result directory was
created; Alice truth never enters the operational decoder.
