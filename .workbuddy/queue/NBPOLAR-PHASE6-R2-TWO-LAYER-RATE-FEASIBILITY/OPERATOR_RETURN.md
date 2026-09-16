# OPERATOR_RETURN — NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY

Candidate only: no OpenSpec task box checked, no acceptance claimed, no
commit/push. Decoder-free analysis of two-layer BEC rate feasibility.

## 1. Mission

Determine whether the NB-Polar route can reach `f<=1.3` under explicit
two-layer BEC surrogate assumptions, identify the target-N band, and close the
audit gap between the roadmap's oracle/candidate L2 paths and the SC executions
actually performed (R2-A01..A10).

## 2. Frozen inputs and provenance

Per-source L1/L2 entropies from the TRAIN rows of
`docs/v49_distribution_tables/v49_train_val_hold_nll.csv` (columns `nll_u1`,
`nll_u2`; mirrored in `docs/v49-distribution-shift-diagnosis-20260827.md` §3.1):

| source | CSV row | H1 = nll_u1 | H2 = nll_u2 |
|---|---|---|---|
| 1M | csv:2 / md:78 | 0.02428054681872374 | 0.7767572780789994 |
| 1p5M | csv:7 / md:81 | 0.02519949687789926 | 0.8003665547438703 |
| 2M | csv:12 / md:84 | 0.025662048796915037 | 0.8069006731253232 |

Chain cross-refs: `docs/decision-log.md:402-404` (V27R H recomputation),
`docs/decision-log.md:2879-2891` and
`docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40`
(V26 A02 L1/L2 H). Mapping `epsilon_l = H_l/5`.

## 3. Method and formulas

- BEC recurrence: `z_minus = 2z - z**2`, `z_plus = z**2`, natural order.
- Minimum worst-first disclosure `K`: smallest `K` in `0..N` with suffix union
  bound `sum(z[K:]) <= budget_l` on the descending spectrum.
- Allocations: `equal` budget_l = `0.005`; `entropy_proportional` budget_l =
  `0.01*H_l/(H1+H2)`.
- Accounting: `leakage_bits = 5*(K1+K2)+64` (one 64-bit tag),
  `leakage_bits_no_tag = 5*(K1+K2)`, `nH = N*(H1+H2)`, `f = leakage_bits/nH`,
  `f_no_tag = leakage_bits_no_tag/nH`.
- Grid: 11 N = 2^8..2^18 x 3 sources x 2 allocations.

## 4. K43 calibration (R2-A03)

N=256, epsilon=0.05, whole-block budget 1e-2 -> K=43; achieved residual
`sum(z[43:]) = 0.0080281681532746`; K=42 residual `0.010563784528611946`
(> 1e-2). Literal-oracle K=43, max|operational-literal| = 0.0. PASS.

## 5. Full-table result (R2-A04/A05/A06)

66/66 rows complete and finite across all axes. First `f<=1.3` crossing is
2^18 for all six axes; per-axis crossing values (tag-inclusive / tag-free):

| source | allocation | first N | f | f_no_tag |
|---|---|---|---|---|
| 1M | equal | 262144 | 1.266953055 | 1.266648274 |
| 1M | entropy_proportional | 262144 | 1.264476714 | 1.264171934 |
| 1p5M | equal | 262144 | 1.262903394 | 1.262607669 |
| 1p5M | entropy_proportional | 262144 | 1.260408213 | 1.260112488 |
| 2M | equal | 262144 | 1.261980900 | 1.261687660 |
| 2M | entropy_proportional | 262144 | 1.259552507 | 1.259259267 |

Log2-linear interpolation between the 2^17 and 2^18 rows places the exact
f=1.3 crossing at 2^17.20-2^17.36. Decision-log scratch cross-check "near
2^17-2^18": MATCH (the interpolated points lie inside the documented window).

## 6. Tag accounting

Tag-inclusive leakage counts exactly one 64-bit tag; tag-free counts none.
`f > f_no_tag` in every row. Both values are reported per axis.

## 7. L2 audit (R2-A07)

Conclusion: VERIFIED — no oracle-L2 (true-L1-conditioned) and no operational
candidate-L2 SC has ever executed; only the single-layer L1 high-plane path
(`label=32*x_hat`, low half constant zero) has executed.

- `sc.py:188` `sc_decode(logp_x, *, field, alpha=2, known_positions=None,
  known_values=None)` is the sole decoder entry; no L1/L2 prior argument.
- `protocol.py:12-13,137-139,639`: `label_j = 32*x_j`; Bob-only erasure metric.
- `incremental.py:532/691,1440-1444,2191-2195`: single-layer metric, low half
  constant zero.
- `prior.py:222` `gather_p2_metrics` and `prior.py:67-68` ORACLE/CANDIDATE
  provenance have zero production call sites; `prior_artifact.py:216`
  constructs PRIOR_ONLY only.
- Docs: `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md:37-38`, `ROADMAP.md:82-84`,
  `docs/decision-log.md:3811-3814`; P3/P5/P6/R1 returns.

## 8. Successor prerequisites (decision output only)

- (a) L2 prior extraction per P0 (P2_true/P2_hat) + two-stage restart SC.
- (b) A paired two-layer development gate under the same accounting discipline.
- (c) Empirical construction and a scalable decoder (e.g. FWHT) for N>=2^17
  (explicitly out of R2 scope).

Nothing under this list is implemented.

## 9. Review and carried comments

`INDEPENDENT_RESULT_REVIEW.md`: PASS_WITH_COMMENTS; 66/66 rows recomputed with
zero difference. Non-blocking nits carried (not fixed): decision-log range
3811-3812 vs 3813-3814; `prior_artifact.py:216` vs 215; R1 OPERATOR_RETURN
"single-layer" wording; K=42 residual last-digit summation-order note; an
uncited "~1e-15 V32 chain" sub-claim (not load-bearing; frozen provenance is
the v49 CSV/doc chain); A07 list omits some P1-only call sites; `ent` vs
`nll_u1` documented alternative.

## 10. Files, tests and scope

Changed/added by this packet: `two_layer_rate.py`,
`test_nbpolar_two_layer_rate.py`, `two_layer_rate_sensitivity.json`,
`R2_REPORT.md`, `P6R2_IMPLEMENTATION_NOTES.md`, `REV_NOTES.md`. Tests: 10
focused new + 180 total NB-Polar suite passed.

Labelling: these BEC figures are a **surrogate planning estimate only** — not
empirical neighbor-shift channel performance, not a rigorous lower bound, not
decoder evidence.

Scope confirmation: no SC call, no artifact/parquet/TTBin read, no sampling,
no attempt/seed consumed (`attempts_allowed: 0`, `attempts_used: 0`), old
evidence roots untouched, no code/result-artifact modification by this return,
no commit/push. No OpenSpec box checked; acceptance remains a main-thread
decision.
