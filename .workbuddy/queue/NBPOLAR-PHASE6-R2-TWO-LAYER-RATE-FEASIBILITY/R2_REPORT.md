# Phase 6-R2 — two-layer BEC rate feasibility (surrogate planning estimate)

**Label**: surrogate planning estimate only — not empirical neighbor-shift channel performance, not a rigorous lower bound, not decoder evidence.

Decoder-free analysis. No SC call, no artifact/parquet/TTBin read, no synthetic block sampling, no attempt/seed consumption; old evidence roots untouched.

## 1. Method and formulas

- BEC recurrence: `z_minus=2z-z**2; z_plus=z**2; natural order`.
- Per-layer erasure surrogate: `epsilon_l = H_l / 5` (bits/symbol over the 5-bit GF32 plane).
- Minimum-K rule: smallest K in 0..N with sum(z[K:]) <= budget_l after sorting z descending (suffix-sum based).
- FER allocations: `equal`: budget_l = 0.01/2 per layer; `entropy_proportional`: budget_l = 0.01*H_l/(H1+H2).
- Accounting: `leakage_bits = 5*(K1+K2)+64`, `leakage_bits_no_tag = 5*(K1+K2)`, `nH = N*(H1+H2)`, `f = leakage_bits/nH`, `f_no_tag = leakage_bits_no_tag/nH`.
- Sensitivity axes: N = 2**8..2**18 (11 values) x 3 sources x 2 allocations; f target <= 1.3.

## 2. Frozen inputs and provenance

| source | H1 | H2 | epsilon_1 | epsilon_2 | CSV | doc |
|---|---|---|---|---|---|---|
| 1M | 0.02428054681872374 | 0.7767572780789994 | 0.004856109363744749 | 0.15535145561579988 | docs/v49_distribution_tables/v49_train_val_hold_nll.csv:2 (source=1M, split=TRAIN, columns nll_u1,nll_u2) | docs/v49-distribution-shift-diagnosis-20260827.md:78 |
| 1p5M | 0.02519949687789926 | 0.8003665547438703 | 0.0050398993755798515 | 0.16007331094877406 | docs/v49_distribution_tables/v49_train_val_hold_nll.csv:7 (source=1p5M, split=TRAIN, columns nll_u1,nll_u2) | docs/v49-distribution-shift-diagnosis-20260827.md:81 |
| 2M | 0.025662048796915037 | 0.8069006731253232 | 0.005132409759383007 | 0.16138013462506465 | docs/v49_distribution_tables/v49_train_val_hold_nll.csv:12 (source=2M, split=TRAIN, columns nll_u1,nll_u2) | docs/v49-distribution-shift-diagnosis-20260827.md:84 |

H2 is the in-sample conditional entropy estimated as the TRAIN NLL of P_TRAIN(U2|B,U1) (column nll_u2); the same CSV row documents kl_sample = E[NLL]-E[H] ~= -1.5e-12. Cross-referenced to the accepted V26 A02 L1/L2 channel rows and the V27R audit review (channel_counts.npz recomputation matches the frozen docs; packet-documented agreement ~1e-15 with the accepted V32 audit chain).

## 3. Calibration (R2-A03)

N=256, epsilon=0.05, whole-block FER budget=0.01 -> K=43 (expected 43), residual union bound 0.0080281681532746; literal oracle K=43, max |operational-literal| 0.0. PASS.

## 4. Full sensitivity table

### 1M / equal

| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 10 | 94 | 0.00377889979823 | 0.00444063112877 | 584 | 2.84786801459 | 2.5357728897 |
| 9 | 512 | 16 | 171 | 0.00491316239575 | 0.00493499650428 | 999 | 2.43580492001 | 2.27975735757 |
| 10 | 1024 | 27 | 314 | 0.00457902956682 | 0.00497354654325 | 1769 | 2.15662607783 | 2.07860229661 |
| 11 | 2048 | 47 | 578 | 0.00466545810613 | 0.00483196194182 | 3189 | 1.94388936184 | 1.90487747123 |
| 12 | 4096 | 81 | 1077 | 0.00469108157678 | 0.00489902504605 | 5854 | 1.78418443465 | 1.76467848935 |
| 13 | 8192 | 138 | 2015 | 0.00485806405242 | 0.00493559762331 | 10829 | 1.65023345088 | 1.64048047822 |
| 14 | 16384 | 239 | 3794 | 0.00496508078968 | 0.00497379300088 | 20229 | 1.54135065462 | 1.53647416829 |
| 15 | 32768 | 420 | 7197 | 0.0048974627701 | 0.0049829861012 | 38149 | 1.453383413 | 1.45094516984 |
| 16 | 65536 | 742 | 13728 | 0.00488150591146 | 0.00499058302541 | 72414 | 1.37939797202 | 1.37817885043 |
| 17 | 131072 | 1332 | 26341 | 0.00496649419832 | 0.00499549871114 | 138429 | 1.31845141732 | 1.31784185653 |
| 18 | 262144 | 2415 | 50781 | 0.00496735472987 | 0.00499415607928 | 266044 | 1.26695305489 | 1.26664827449 |

### 1M / entropy_proportional

| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 16 | 90 | 0.000209618229268 | 0.00831593319319 | 594 | 2.89663287785 | 2.58453775296 |
| 9 | 512 | 25 | 165 | 0.000288525941312 | 0.00932926550172 | 1014 | 2.47237856746 | 2.31633100501 |
| 10 | 1024 | 42 | 304 | 0.000276365707325 | 0.00960138255232 | 1794 | 2.18710411737 | 2.10908033614 |
| 11 | 2048 | 67 | 562 | 0.000296097430444 | 0.00949963862796 | 3209 | 1.95608057766 | 1.91706868704 |
| 12 | 4096 | 109 | 1053 | 0.000284346887596 | 0.00949487914133 | 5874 | 1.79028004256 | 1.77077409725 |
| 13 | 8192 | 179 | 1974 | 0.000287023517648 | 0.00959502208046 | 10829 | 1.65023345088 | 1.64048047822 |
| 14 | 16384 | 297 | 3733 | 0.000301414812053 | 0.00969303546831 | 20214 | 1.54020772814 | 1.53533124181 |
| 15 | 32768 | 507 | 7095 | 0.000300634116134 | 0.00968448293892 | 38074 | 1.45052609679 | 1.44808785363 |
| 16 | 65536 | 874 | 13569 | 0.000301321971116 | 0.00967946085619 | 72279 | 1.37682638743 | 1.37560726585 |
| 17 | 131072 | 1530 | 26080 | 0.000299778203486 | 0.00967434701184 | 138114 | 1.31545123531 | 1.31484167452 |
| 18 | 262144 | 2715 | 50377 | 0.000301014052697 | 0.00969350098907 | 265524 | 1.26447671418 | 1.26417193378 |

### 1p5M / equal

| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 10 | 96 | 0.00434107267631 | 0.00423892019961 | 594 | 2.81057160168 | 2.50774907221 |
| 9 | 512 | 17 | 175 | 0.00367861297989 | 0.00486947968938 | 1024 | 2.42258023579 | 2.27116897106 |
| 10 | 1024 | 28 | 321 | 0.00421186547809 | 0.00459686896923 | 1809 | 2.13986701492 | 2.06416138255 |
| 11 | 2048 | 48 | 592 | 0.00491347924251 | 0.00491664884343 | 3264 | 1.9304936254 | 1.89264080921 |
| 12 | 4096 | 83 | 1099 | 0.00470786264684 | 0.00496550095614 | 5974 | 1.76666190535 | 1.74773549726 |
| 13 | 8192 | 142 | 2064 | 0.00489573439623 | 0.00492138532895 | 11094 | 1.64038727636 | 1.63092407231 |
| 14 | 16384 | 246 | 3886 | 0.00488412456757 | 0.00497982988035 | 20724 | 1.53215188008 | 1.52742027806 |
| 15 | 32768 | 432 | 7383 | 0.00490852856339 | 0.00499286675783 | 39139 | 1.44679821546 | 1.44443241445 |
| 16 | 65536 | 764 | 14096 | 0.00499644926962 | 0.00499505961513 | 74364 | 1.37445645641 | 1.3732735559 |
| 17 | 131072 | 1375 | 27047 | 0.00492817783859 | 0.00499062471365 | 142174 | 1.31388825395 | 1.3132968037 |
| 18 | 262144 | 2489 | 52161 | 0.00498730501133 | 0.00499605969467 | 273314 | 1.26290339387 | 1.26260766874 |

### 1p5M / entropy_proportional

| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 16 | 91 | 0.000242727715063 | 0.00935056823586 | 599 | 2.8342296118 | 2.53140708232 |
| 9 | 512 | 26 | 169 | 0.000259648007028 | 0.00886606454194 | 1039 | 2.45806725097 | 2.30665598623 |
| 10 | 1024 | 43 | 311 | 0.000275840500526 | 0.00937381778544 | 1834 | 2.16943952756 | 2.09373389519 |
| 11 | 2048 | 69 | 575 | 0.000276472724113 | 0.0096241856354 | 3284 | 1.94232263045 | 1.90446981427 |
| 12 | 4096 | 112 | 1076 | 0.000284988045745 | 0.00953725345006 | 6004 | 1.77553365914 | 1.75660725105 |
| 13 | 8192 | 183 | 2023 | 0.000287251292377 | 0.00968889743425 | 11094 | 1.64038727636 | 1.63092407231 |
| 14 | 16384 | 305 | 3824 | 0.000301760201424 | 0.00967331808539 | 20709 | 1.53104291086 | 1.52631130884 |
| 15 | 32768 | 520 | 7281 | 0.000298275846001 | 0.00966369504031 | 39069 | 1.44421062061 | 1.4418448196 |
| 16 | 65536 | 899 | 13933 | 0.00030267402525 | 0.00969168239543 | 74224 | 1.37186886155 | 1.37068596105 |
| 17 | 131072 | 1575 | 26789 | 0.000302406792565 | 0.00969214529573 | 141884 | 1.31120824499 | 1.31061679474 |
| 18 | 262144 | 2794 | 51748 | 0.000304475216767 | 0.00968863116913 | 272774 | 1.26040821312 | 1.26011248799 |

### 2M / equal

| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 10 | 96 | 0.00464545312307 | 0.00459826781612 | 594 | 2.78695218859 | 2.48667451171 |
| 9 | 512 | 17 | 176 | 0.0039488852834 | 0.00488860908865 | 1029 | 2.41395101183 | 2.26381217339 |
| 10 | 1024 | 28 | 322 | 0.00456490601751 | 0.00479826746608 | 1814 | 2.12774885105 | 2.05267943183 |
| 11 | 2048 | 49 | 596 | 0.00467573417021 | 0.00480282211094 | 3289 | 1.92893218608 | 1.89139747647 |
| 12 | 4096 | 84 | 1106 | 0.00473743674019 | 0.00490216556242 | 6014 | 1.76354487186 | 1.74477751706 |
| 13 | 8192 | 144 | 2077 | 0.00485544699335 | 0.00495156931846 | 11169 | 1.63759832672 | 1.62821464932 |
| 14 | 16384 | 250 | 3912 | 0.00482839006483 | 0.00498787446178 | 20874 | 1.53027251643 | 1.52558067773 |
| 15 | 32768 | 438 | 7436 | 0.00486101645121 | 0.00497453225329 | 39434 | 1.44545286991 | 1.44310695056 |
| 16 | 65536 | 776 | 14195 | 0.00496050669314 | 0.00498581947504 | 74919 | 1.37307759244 | 1.37190463277 |
| 17 | 131072 | 1395 | 27243 | 0.00493513708943 | 0.00498877471827 | 143254 | 1.31274347914 | 1.3121569993 |
| 18 | 262144 | 2528 | 52545 | 0.00498108852333 | 0.0049979126645 | 275429 | 1.26198090007 | 1.26168766015 |

### 2M / entropy_proportional

| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 8 | 256 | 16 | 92 | 0.000260791537616 | 0.00851135055695 | 604 | 2.8338705756 | 2.53359289872 |
| 9 | 512 | 26 | 170 | 0.000281392227872 | 0.00882488225995 | 1044 | 2.44913980209 | 2.29900096365 |
| 10 | 1024 | 43 | 313 | 0.000299150807136 | 0.00928215814756 | 1844 | 2.16293764131 | 2.08786822209 |
| 11 | 2048 | 69 | 579 | 0.000307191024551 | 0.00946269220242 | 3304 | 1.93772938365 | 1.90019467404 |
| 12 | 4096 | 113 | 1082 | 0.000291285557157 | 0.00961925488496 | 6039 | 1.77087586983 | 1.75210851503 |
| 13 | 8192 | 184 | 2037 | 0.000306685664108 | 0.00962172222352 | 11169 | 1.63759832672 | 1.62821464932 |
| 14 | 16384 | 309 | 3849 | 0.000302159592709 | 0.00966981974334 | 20854 | 1.52880631684 | 1.52411447814 |
| 15 | 32768 | 526 | 7332 | 0.000307760426394 | 0.00966427015076 | 39354 | 1.44252047072 | 1.44017455137 |
| 16 | 65536 | 911 | 14033 | 0.000305006962309 | 0.00967692354524 | 74784 | 1.37060338063 | 1.36943042095 |
| 17 | 131072 | 1597 | 26984 | 0.000307147404061 | 0.00967448875498 | 142969 | 1.31013181111 | 1.30954533128 |
| 18 | 262144 | 2833 | 52134 | 0.000306881790617 | 0.00968408435922 | 274899 | 1.25955250699 | 1.25925926707 |

## 5. First N meeting f <= 1.3 per axis

| source | allocation | first N | exponent | K1 | K2 | leakage_bits | f | f_no_tag |
|---|---|---|---|---|---|---|---|---|
| 1M | equal | 262144 | 18 | 2415 | 50781 | 266044 | 1.26695305489 | 1.26664827449 |
| 1M | entropy_proportional | 262144 | 18 | 2715 | 50377 | 265524 | 1.26447671418 | 1.26417193378 |
| 1p5M | equal | 262144 | 18 | 2489 | 52161 | 273314 | 1.26290339387 | 1.26260766874 |
| 1p5M | entropy_proportional | 262144 | 18 | 2794 | 51748 | 272774 | 1.26040821312 | 1.26011248799 |
| 2M | equal | 262144 | 18 | 2528 | 52545 | 275429 | 1.26198090007 | 1.26168766015 |
| 2M | entropy_proportional | 262144 | 18 | 2833 | 52134 | 274899 | 1.25955250699 | 1.25925926707 |

## 6. Checks

- rows 66 / expected 66; all_k_in_range=True; all_finite=True; axes_complete=True.

## 7. R2-A07 audit — L2 execution coverage

Claim: oracle-L2 (true-L1-conditioned) and operational candidate-L2 have never entered SC execution; only the single-layer L1 high-plane path (label=32*x_hat, constant-zero low half) has executed.

Code evidence:
- sc.py:188 sc_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None): one full-Bob metric; the decoder API has no L1/L2 conditioning or prior argument
- protocol.py:12-13 docstring and protocol.py:137-139 labels_from_symbols: label_j = 32*x_j single-layer packing (low half constant zero)
- protocol.py:639 builds the block metric via generate_erasure_block (Bob-only one-hot/uniform posterior); no L1 estimate conditions it
- incremental.py:1440-1444 and 2191-2195 freeze single_layer_low_half_constant_zero: True; metrics built at incremental.py:1669/2290 and every level calls sc_decode on the same original Bob metric (incremental.py:532/691)
- prior.py:222 gather_p2_metrics (candidate-L2 gather on hard u1) is defined/exported (prior.py:46; __init__.py:52) but has zero production call sites; only tests/test_nbpolar_prior.py:229-237,302 call it and that file never invokes SC
- prior.py:67-68 ORACLE_CONDITIONED/CANDIDATE_CONDITIONED are never constructed outside the enum; prior_artifact.py:215 constructs PRIOR_ONLY only
- empirical_channel.py:1-25: the P3 empirical path reduces the full mapping to the high level by marginalizing the low symbol and its operational builder signature has no Alice/truth/u argument

Document evidence:
- docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md:37-38: app_fed_l2_prior EXCLUDED from first SC path; oracle_l2_prior REFERENCE pattern only; section 4 P2_true oracle-only, P2_hat executable dependency
- docs/nbpolar/ROADMAP.md:82-84: L1 exact, oracle-L2 on true L1 and operational L2 on the L1 candidate are separated Phase 4 diagnostics
- docs/decision-log.md:3811-3812 (2026-09-13): the roadmap's oracle-L2 and candidate-conditioned operational L2 paths have not been exercised by the Phase 5/6 gates
- P5 OPERATOR_RETURN.md:45-46 and P5_FREEZE.md:22: R2 label domain is the 10-bit single-layer embedding with low half constant zero
- P6 OPERATOR_RETURN.md:31: physical labels 32*x_hat; R1 OPERATOR_RETURN.md:1-6: frozen single-layer synthetic scope
- P3 OPERATOR_RETURN.md:9-12: Stage A/A2 qualified only the P1 metric (high symbol) into SC; Stage B ran the P1 metric only

Conclusion: VERIFIED: no L2 prior and no L2-conditioned SC has ever executed; all accepted P3/P5/P6/R1 gates used the single-layer L1 high-plane path only.

## 8. R2-A09 successor prerequisites (decision output only)

- (a) L2 prior extraction per the P0 contract (P2_true/P2_hat tensors, PHASE4_P0_PRIOR_CONTRACT.md section 4) with an explicit two-stage restart SC that conditions the low-plane metric on the accepted L1 hard candidate under the same provenance/fail-closed rules (no APP import; floor policy per P0 section 3)
- (b) a paired two-layer development gate under the same accounting discipline (each coordinate disclosed once, one tag per accepted candidate, undetected isolated, no rerun/no tuning) with thresholds frozen before execution
- (c) empirical construction and a scalable decoder sufficient for N >= 2**17 (e.g. FWHT q-ary SC); explicitly OUT OF SCOPE of R2

_No OpenSpec task box is checked by this report; acceptance remains a main-thread decision. BEC figures are surrogate planning estimates, not real-channel performance or decoder evidence._
