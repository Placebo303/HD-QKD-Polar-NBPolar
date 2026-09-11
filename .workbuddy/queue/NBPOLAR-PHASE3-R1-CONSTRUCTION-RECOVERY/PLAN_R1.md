# PLAN_R1 — Phase 3-R1 construction recovery (frozen before TRAIN/DEV)

Date: 2026-09-11. Branch `codex/nbpolar-phase0` confirmed; unrelated dirty
preserved; predecessor artifacts immutable (seed 2026091203 never rerun or
reused; 299/300 + block-104 diagnostic retained; no relabel; no EVAL-driven
selection). Pre-EXECUTE self-check PASS (see OPERATOR_RETURN_R1 §3).

## 1. Defects under repair (one plan, three independent fixes)

- D1 finite-TRAIN rank resolution: 512-sample genie `(e,h)` ties ~187/256
  coordinates at exactly 0, so full-vector Spearman mixes unresolvable noise
  with signal. Fix: preregister tie-aware construction metrics; full-vector
  Spearman is reported, never a gate.
- D2 impossible-disclosure semantics: a wrong earlier undisclosed prefix can
  give the true later value exact-zero conditional support, which is a
  legitimate decode failure, not automatically a numeric fault. Fix: new
  prereg counts impossible as failed decode + non-exact, reported separately
  inside the same total; zero-tolerance gate dropped prospectively only.
- D3 review/invocation reality: predecessor EVAL was self-authorized with a
  placeholder order. Fix: dedicated entry point, literal full 256-order in
  the frozen command, real reviewer-go PASS required, else no EVAL.

## 2. Options compared on TRAIN/DEV only (document ≥3, choose 1)

- O1 genie-512: original genie `(e,h)` estimator, 512 TRAIN blocks (fresh
  stream replication baseline).
- O2 genie-2048: original genie estimator, 2048 TRAIN blocks (finer rank
  resolution, same statistic family).
- O3 analytic: exact BEC erasure order as disclosure ground truth; genie
  TRAIN retained as calibration diagnostic only (no sampling in the order).

## 3. Frozen streams (all differ from predecessor 2026091200–1203)

```text
R1 unit/sanity = 2026091210
R1 TRAIN       = 2026091211 (sequential: O1/eps0.05 512, O1/eps0.10 512,
                             O2/eps0.05 2048, O2/eps0.10 2048)
R1 DEV         = 2026091212 (sequential: per passing option, grid order §5)
R1 EVAL        = 2026091213 (chosen here before use; exactly one future use
                             after reviewer-go PASS, else never consumed)
```

## 4. Construction gate (rank resolution; separates from disclosure)

At q=32, N=256, eps=0.10 TRAIN:

- G1 resolvable-subset Spearman (genie `e>0`, n≥20) ≥ 0.90 (O1/O2);
  O3 passes by exactness, genie-vs-analytic calibration reported instead.
- G2 top-50 overlap (candidate order vs analytic order) ≥ 0.80.
- Full-vector Spearman reported with tie count, never a gate.
- Why these measure construction quality: disclosure uses only the
  worst-first head of the order; G2 scores exactly that head, and G1 scores
  rank signal where finite samples resolve it, excluding the ~187-way exact
  zero tie whose internal order is pure quantization noise.

## 5. DEV grid (disclosure performance; frozen before DEV)

eps=0.05, K ∈ {45, 53, 61, 69} (margins 32/40/48/56) + one harder sanity
(eps=0.10, K=58). 100 blocks/candidate/option. Denominator = all attempted
blocks; impossible/other/nan counted as failures with separate tags.

## 6. Selection rule (deterministic, TRAIN/DEV only)

1. Options failing §4 do not enter DEV.
2. Retain (option, eps, K) with DEV exact ≥ 98/100.
3. Pick smallest K, then smaller eps, then higher DEV exact, then
   O3 > O2 > O1 (exactness over sampling, predeclared).
4. None retained → `BLOCKED(NO_EASY_SYNTHETIC_POINT)`, no EVAL.

## 7. Fresh-EVAL prereg (thresholds before EVAL; impossible inclusive)

Single 300-block run at the selected (order, eps, K) with R1 EVAL seed:
success = exact(U and X) ≥ 285/300 over all 300 attempts (impossible counts
as non-exact inside the denominator, reported as its own decode-failure
class with indices); initial-error blocks ≥ 240/300 (nontrivial-point
check); NaN 0 and other-failure 0 hard. No MAP-equality requirement beyond
exact U/X recovery; no rerun/replacement.

## 8. Budgets and stop rules

TRAIN+DEV+tests target < 30 min wall; N=256 decode ~0.016 s; peak extra
~1 MiB per block, stop at 2 GiB or first NaN/resource abort. Scoped files:
`synthetic.py` (untouched), `construction.py` (+3 helpers),
`__init__.py` (+exports), one new `eval_r1.py` entry, one new R1 test file,
packet artifacts. No Model-F/real-data/SCL/adapters/benchmark roots.

## 9. EVAL command shape (literals frozen in EVAL_FREEZE_R1 §4)

`PYTHONPATH=<root> <py> -m
comparison_bench.src.comparison_bench.formal_ir.nbpolar.eval_r1
--q 32 --n 256 --channel erasure --param <eps> --k <K> --seed 2026091213
--order <literal full 256-permutation> --n-blocks 300 --out
<packet-dir>/eval_r1_fresh` (refuses banned seeds and existing out dir).
EVAL has not run as of this plan.
