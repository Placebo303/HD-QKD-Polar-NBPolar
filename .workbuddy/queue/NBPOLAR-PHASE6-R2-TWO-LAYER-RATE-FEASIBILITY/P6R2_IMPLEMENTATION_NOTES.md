# P6-R2 implementation notes — two-layer rate feasibility (decoder-free)

Operator session, 2026-09-13, repo `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
Candidate only: no task box checked, no acceptance claimed, no commit/push.

## 1. Deliverables and commands

| item | path |
|---|---|
| analysis module | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer_rate.py` |
| focused tests | `comparison_bench/tests/test_nbpolar_two_layer_rate.py` |
| result JSON | `.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/two_layer_rate_sensitivity.json` |
| result report | `.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/R2_REPORT.md` |

Exact analysis command (writes only the two result files into the packet dir):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m \
  comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer_rate \
  --out-dir .workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY
```

```text
{"calibration_k": 43, "checks": {"all_finite": true, "all_k_in_range": true,
 "axes_complete": true, "expected_rows": 66, "rows": 66},
 "written": {.../two_layer_rate_sensitivity.json, .../R2_REPORT.md}}
```

## 2. Frozen inputs (R2-A01) and provenance

TRAIN rows of `docs/v49_distribution_tables/v49_train_val_hold_nll.csv`
(columns `nll_u1`, `nll_u2`; also mirrored in
`docs/v49-distribution-shift-diagnosis-20260827.md` §3.1):

| source | H1 | H2 | CSV file:line | doc file:line |
|---|---|---|---|---|
| 1M | 0.02428054681872374 | 0.7767572780789994 | `docs/v49_distribution_tables/v49_train_val_hold_nll.csv:2` | `docs/v49-distribution-shift-diagnosis-20260827.md:78` |
| 1p5M | 0.02519949687789926 | 0.8003665547438703 | `...csv:7` | `...md:81` |
| 2M | 0.025662048796915037 | 0.8069006731253232 | `...csv:12` | `...md:84` |

Chain cross-references (recorded in the module/JSON): V27R review recomputes H
from `channel_counts.npz` and matches the frozen docs
(`docs/decision-log.md:402-404`); V26 A02 GF32+GF32 f=1.3 (30/30)
(`docs/decision-log.md:2879-2891`); V26 A02 L1/L2 H 0.02566205/0.80690067
(`docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40`).
`H2` is the in-sample conditional entropy NLL_U2; the same CSV row documents
`kl_sample = E[NLL]-E[H] ≈ -1.5e-12`. Mapping recorded: `epsilon_l = H_l/5`.
No ambiguity was found; no provenance stop triggered.

## 3. K43 calibration reproduction (R2-A03, exact evidence)

Frozen point: N=256, epsilon=0.05, whole-block FER union-bound target 1e-2.

```text
operational minimum_k(erasure_spectrum(0.05,256), 1e-2) -> K=43
achieved residual sum(z[43:]) = 0.0080281681532746   (<= 1e-2)
K=42 residual sum(z[42:])     = 0.010563784528611946 (>  1e-2)
literal oracle  K=43; max|operational - literal| = 0.0
```

`verify_calibration()` is called before any table row is produced and raises
`AssertionError` on a K mismatch or on operational-vs-literal disagreement
> 1e-15; the run aborts rather than emitting a table. Independent brute-force
minimum-K in the focused tests also gives 43.

## 4. Sensitivity results (R2-A04..A06)

66 rows = 3 sources × 2 allocations × N = 2^8..2^18. Formulas:
`leakage_bits = 5*(K1+K2)+64`, `leakage_bits_no_tag = 5*(K1+K2)`,
`nH = N*(H1+H2)`, `f = leakage_bits/nH`. All K in 0..N; all values finite;
`axes_complete=true`.

First N with `f <= 1.3` (all six axes cross at 2^18):

| source | allocation | first N | f | f_no_tag | K1 | K2 |
|---|---|---|---|---|---|---|
| 1M | equal | 262144 | 1.266953 | 1.266648 | 2415 | 50781 |
| 1M | entropy_proportional | 262144 | 1.264477 | 1.264172 | 2715 | 50377 |
| 1p5M | equal | 262144 | 1.262903 | 1.262608 | 2489 | 52161 |
| 1p5M | entropy_proportional | 262144 | 1.260408 | 1.260112 | 2794 | 51748 |
| 2M | equal | 262144 | 1.261981 | 1.261686 | 2528 | 52545 |
| 2M | entropy_proportional | 262144 | 1.259553 | 1.259258 | 2833 | 52134 |

1M f excerpt (tag-inclusive / tag-free): 2^8 2.847868/2.535773,
2^10 2.156626/2.078602, 2^12 1.784184/1.764678, 2^14 1.541351/1.536474,
2^16 1.379398/1.378179, 2^18 1.266953/1.266648 (equal); the
entropy-proportional axis is marginally worse at small N and marginally better
from 2^14 onward (2^13 is a tie: 1.650233 both), with the same 2^18 first
crossing.

**Cross-check vs the decision-log scratch estimate ("near 2^17–2^18")**:
MATCH. The first N meeting `f <= 1.3` is 2^18 on every axis, and a
log2-linear interpolation of the last two rows places the exact f=1.3
crossing at 2^17.20–2^17.36 (per-axis values 17.20/17.22/17.25/17.27/17.30/
17.36), i.e. inside the documented 2^17–2^18 window. No formula, budget, input
or grid value was changed after seeing results.

## 5. R2-A07 audit conclusion

Code and doc evidence is listed in full in `R2_REPORT.md` §7 and in the JSON
`audit` field. Conclusion: the accepted gates only ever exercised the
single-layer L1 high-plane path (`label=32*x_hat`, low half constant zero).
`sc_decode` has no L1/L2 conditioning argument; every P5/P6/R1 metric comes
from `generate_erasure_block` (Bob-only). `prior.gather_p2_metrics`
(candidate-L2) and the `ORACLE_CONDITIONED`/`CANDIDATE_CONDITIONED` provenance
members have zero production call sites; the P4-P0 contract marks
`app_fed_l2_prior` as EXCLUDED from the first SC path and `oracle_l2_prior` as
reference-only; the P3 empirical path qualified the P1 metric only. No
oracle-L2 or candidate-L2 SC has ever executed.

R2-A09 successor prerequisites are recorded as a decision output only (L2
prior extraction + two-stage restart SC per the P0 contract; a paired
two-layer development gate under the same accounting discipline; empirical
construction and scalable decoder such as FWHT for N >= 2^17). Nothing under
R2-A09 is implemented in this packet.

## 6. Alternatives tried / simplifications

- Recurrence: vectorized doubling kept; an independent literal per-element
  recursive oracle is retained for cross-checking rather than a second
  vectorized variant (would share the same failure mode).
- Minimum-K: suffix-sum + `searchsorted` on the descending spectrum; brute
  force only in tests. Residual at K=N is defined as exact 0.0 (empty sum).
- Robustness: the crossing lookup returns `None` if an axis never crosses;
  with the frozen inputs none is None. No fallback or extrapolation exists.
- I/O: the module writes only the two registered artifacts and has no
  import-time I/O; no logging, caching, or extra diagnostics files.

## 7. Verification

```bash
# focused (10 tests)
.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_two_layer_rate.py \
  -q -p no:cacheprovider --basetemp=/tmp/opencode/pytest_p6r2_focused
# -> 10 passed in 4.77s

# full NB-Polar suite (12 files)
.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_*.py \
  -q -p no:cacheprovider --basetemp=/tmp/opencode/pytest_p6r2_full
# -> 180 passed in 86.89s  (170 predecessor + 10 new)
```

Scope confirmation: no SC call, no artifact/parquet/TTBin read, no synthetic
block sampling, no attempt/seed consumed (`attempts_allowed: 0`,
`attempts_used: 0`), no FWHT/SCL/Phase 7, no real data, no qualification or
promotion, no modification of old evidence roots, no commit/push.

OpenSpec: conventions frozen by this implementation are recorded in
`openspec/changes/formal-ir-nbpolar-phase6-r2-two-layer-rate-feasibility/REV_NOTES.md`;
no proposal/design/task box was modified, no requirement redefined.
