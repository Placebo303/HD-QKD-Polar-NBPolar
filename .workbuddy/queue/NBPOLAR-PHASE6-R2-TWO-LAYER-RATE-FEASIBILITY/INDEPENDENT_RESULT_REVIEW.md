# INDEPENDENT_RESULT_REVIEW — NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY

Reviewer: reviewer-go (independent; did not author the module, tests, JSON or report).
Date: 2026-09-13. Repository: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged at end of review; no commit/push performed).

Scope and isolation: decoder-free recomputation only. No SC/decoder call, no Model-F artifact/parquet/TTBin read, no synthetic block sampling, no attempt/seed consumption, no modification of any prior evidence root. The recomputation is an independent scratch implementation under `/tmp/opencode/r2_independent/` (`recompute.py`, `edge_checks.py`, `report_check.py`); it does **not** import the reviewed `two_layer_rate` module. The only repository file written by this review is this document.

Reviewed artifacts: `TASK_PACKET.md`, `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `two_layer_rate_sensitivity.json`, `R2_REPORT.md`, `P6R2_IMPLEMENTATION_NOTES.md`; `openspec/changes/formal-ir-nbpolar-phase6-r2-two-layer-rate-feasibility/{proposal.md,design.md,tasks.md,REV_NOTES.md,specs/nbpolar-two-layer-rate-feasibility/spec.md}`; the 2026-09-13 R2 entry in `docs/decision-log.md`; `docs/v49_distribution_tables/v49_train_val_hold_nll.csv`; `docs/v49-distribution-shift-diagnosis-20260827.md`; the P3/P5/P6/R1 queue `OPERATOR_RETURN.md`/freeze docs cited by the audit.

## Verdict: PASS_WITH_COMMENTS

No blocking issue found. Every numerical value required by the packet was reproduced independently, bit-exact; the calibration and the A07 audit claims hold. The comments below are citation/annotation precision notes only and do not change any result.

## 1. Frozen inputs and provenance (R2-A01)

My own read of `docs/v49_distribution_tables/v49_train_val_hold_nll.csv` TRAIN rows and `docs/v49-distribution-shift-diagnosis-20260827.md` §3.1:

| source | CSV row (skip=0) | H1 = nll_u1 | H2 = nll_u2 | JSON h1/h2 match | eps=H/5 match |
|---|---|---|---|---|---|
| 1M | csv:2 / md:78 | 0.02428054681872374 | 0.7767572780789994 | yes (exact) | yes (exact) |
| 1p5M | csv:7 / md:81 | 0.02519949687789926 | 0.8003665547438703 | yes (exact) | yes (exact) |
| 2M | csv:12 / md:84 | 0.025662048796915037 | 0.8069006731253232 | yes (exact) | yes (exact) |

- File:line citations verify exactly in both the CSV (TRAIN rows; header is line 1) and the diagnosis doc (§3.1). The chain references also verify: `docs/decision-log.md:402-404` (V27R H recomputation from `channel_counts.npz`: 1M 0.024280547/0.776757278; 1p5M 0.025199497/0.800366555; 2M 0.025662049/0.806900673) and `docs/decision-log.md:2879-2891` / `docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40` (V26 A02 L1/L2 H 0.02566205/0.80690067, all rounding-compatible).
- The mapping `epsilon_l = H_l/5` is explicit in the packet authorization, `design.md`, the module docstring, the JSON `model.entropy_to_erasure_mapping` and `REV_NOTES.md` §2; no hidden substitution.
- The `ent` column of the same TRAIN rows (e.g. 1M `0.024280546820265723`) differs from the chosen `nll_u1` by ~1.5e-12. The choice of the NLL columns is explicitly documented (provenance strings name `columns nll_u1,nll_u2`; H2 note explains the in-sample NLL estimate and `kl_sample ≈ -1.5e-12`), so it is not silent; as a robustness check I recomputed all 66 rows with H1 replaced by the `ent` value and **zero K selections change** (see §3). Numerically immaterial; recorded as a comment, not a blocker.
- Auxiliary note: the `h2_note` sub-claim "agreement ~1e-15 with the accepted V32 audit chain" could not be located in this checkout's searchable docs. The primary provenance (CSV, diagnosis doc, decision-log 402-404, V26 report 39-40) is fully verified; the ~1e-15 sub-claim is unverified annotation only.

## 2. Recurrence and calibration (R2-A02/A03)

Independent recurrence implementation: index-bit template, bits of the natural-order index processed MSB→LSB (0 → `z_minus=2z-z^2`, 1 → `z_plus=z^2`), plus an exact `fractions.Fraction` recursive expansion. Results:

- Bit-template vs interleaved-float reference order: elementwise bit-identical (`array_equal=True`, maxdiff 0.0) for N ∈ {2,4,8,16,256} and both tested epsilons — confirms natural order and values.
- Exact-rational oracle vs float recurrence: max deviation ≤ 1.11e-16 for N ≤ 64 (pure float representation rounding, as expected).
- Calibration N=256, epsilon=0.05, budget=1e-2:
  - K = 43 (my linear-scan minimum) = 43 (my pure-Python brute force) = 43 (JSON).
  - Achieved residual `sum(z[43:]) = 0.0080281681532746` — exactly equal to the JSON value.
  - K=42 residual `= 0.010563784528611946` (cumsum order) ≈ `0.010563784528611947` (slice-sum order) — both **> 1e-2**. The K-1 boundary is confirmed under either summation order; the last-digit difference is a summation-order artifact (the implementation note's value matches the cumsum order).
  - Minimality of K is confirmed directly: for every one of the 66 rows and both layers, my checker verified `suffix[K-1] > budget` (no K-1 shortcut anywhere) in addition to the smallest-K scan and a full pure-Python brute force (0 mismatches, 132 spectra).

## 3. Full 66-row recomputation (R2-A04/A05)

Full grid: 3 sources × 2 allocations × N=2^8..2^18 (66 rows), recomputed from scratch with my own recurrence and a linear-scan minimum-K plus an independent pure-Python suffix-sum brute force. Comparison against every field of the persisted JSON:

- max abs difference **0.0**, max rel difference **0.0** — over `k1, k2, budget_1, budget_2, residual_1, residual_2, leakage_bits, leakage_bits_no_tag, nH, f, f_no_tag`.
- integer fields (`k1, k2, leakage_bits, leakage_bits_no_tag`, `k_total`) exact; per-field max abs diff all 0.0; 0 non-exact entries; no missing/extra rows.
- Arithmetic labels: `leakage_bits = 5*(K1+K2)+64`, `leakage_bits_no_tag = 5*(K1+K2)`, `nH = N*(H1+H2)`, `f`, `f_no_tag` all consistent for all rows; `f > f_no_tag` everywhere (one 64-bit tag counted once).
- FER allocations: `equal = (0.005, 0.005)`; `entropy_proportional = (0.01*H1/(H1+H2), 0.01*H2/(H1+H2))` — verified exactly.
- Rendered report consistency: all 66 table lines and all 6 crossing lines in `R2_REPORT.md` match the JSON recomputation formatting exactly (0 missing).

## 4. Crossing and scratch-estimate cross-check (R2-A06)

| source | allocation | first N (exp) | f | f_no_tag | K1 | K2 | leakage_bits | previous f |
|---|---|---|---|---|---|---|---|---|
| 1M | equal | 262144 (18) | 1.266953054889159 | 1.2666482744937624 | 2415 | 50781 | 266044 | 1.31845141732 |
| 1M | entropy_proportional | 262144 (18) | 1.2644767141765612 | 1.2641719337811645 | 2715 | 50377 | 265524 | 1.31545123531 |
| 1p5M | equal | 262144 (18) | 1.262903393870052 | 1.2626076687436125 | 2489 | 52161 | 273314 | 1.31388825395 |
| 1p5M | entropy_proportional | 262144 (18) | 1.2604082131157188 | 1.2601124879892793 | 2794 | 51748 | 272774 | 1.31120824499 |
| 2M | equal | 262144 (18) | 1.2619809000672049 | 1.2616876601483715 | 2528 | 52545 | 275429 | 1.31274347914 |
| 2M | entropy_proportional | 262144 (18) | 1.2595525069893676 | 1.2592592670705345 | 2833 | 52134 | 274899 | 1.31013181111 |

- Every axis first meets `f <= 1.3` at 2^18 and the preceding exponent (2^17) exceeds 1.3 — verified per axis.
- Log2-linear interpolation between the 2^17 and 2^18 rows: 1M/equal 17.3583, 1M/entropy 17.3031, 1p5M/equal 17.2724, 1p5M/entropy 17.2206, 2M/equal 17.2510, 2M/entropy 17.2003 (range 17.20–17.36), matching the listed per-axis values in `P6R2_IMPLEMENTATION_NOTES.md` §4. The decision-log scratch estimate "near 2^17–2^18" is a loose window and the interpolated points lie inside it; "**MATCH (near 2^17–2^18)**" is warranted (the exact crossing is in the upper half of the window; grid first-hit is 2^18).
- No formula, budget, input or grid value was adjusted after results — no evidence to the contrary; the frozen constants in code/JSON equal the packet/authorization text.

## 5. Completeness, finiteness, labels, disclaimer (R2-A08)

- 66 rows, 66 unique (source, allocation, N) keys; all exponents 8..18 present; `N == 2**exponent` for all rows; no NaN/Infinity tokens in the JSON; all listed numeric fields finite.
- All K in 0..N (both layers); containment of K verified.
- Surrogate disclaimer present verbatim in both artifacts: JSON `surrogate_disclaimer` and `R2_REPORT.md` line 3; scan of the report finds only negated or scope-limited uses of "empirical"/"lower bound"/"decoder evidence" (disclaimer, audit-evidence string, R2-A09 out-of-scope prerequisite, closing note). No claim of empirical-channel performance, rigorous lower bound, or decoder evidence appears anywhere.
- Tag-inclusive vs tag-free values are consistently labelled and satisfy `f > f_no_tag` in all rows.

## 6. R2-A07 audit — L2 execution coverage (independently re-verified)

Claim: "oracle-L2 (true-L1-conditioned) and operational candidate-L2 have never entered SC execution; only the single-layer L1 high-plane path (label=32*x_hat, constant-zero low half) has executed."

Code verification (all citations checked at the stated lines):
- `sc.py:188`: `sc_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None)` is the sole decoder entry; the file defines no alternative decode entry (defs list: `sc_decode` only plus helpers). Its API has no prior/L1/L2 conditioning parameter. Confirmed.
- `protocol.py:12-13`, `protocol.py:137-139` (`labels_from_symbols`, `label_j = 32*x_j`), `protocol.py:639` (`generate_erasure_block` builds the Bob-only metric; `protocol.py:313` calls `sc_decode` with it and disclosed U values). Confirmed.
- `incremental.py:532/691`: both `sc_decode` calls receive `logp_arr` (the original Bob-only erasure metric) plus cumulative disclosed truth positions; `incremental.py:1444/2195` freeze `single_layer_low_half_constant_zero: True`; metrics built at `incremental.py:1669/2290`. Confirmed.
- `prior.py:46` exports `gather_p2_metrics`; `prior.py:222` defines it; `prior.py:67-68` declares `ORACLE_CONDITIONED`/`CANDIDATE_CONDITIONED`. Repo-wide grep: zero production call sites; only `comparison_bench/tests/test_nbpolar_prior.py:229,232,237,302` call it, and that file imports no `sc_decode` and performs no SC execution. No other test constructs an L2-conditioned metric before SC. `derive_p2` likewise has no production consumer.
- `prior_artifact.py:216` (not 215) constructs `provenance=Provenance.PRIOR_ONLY`; no other construction site of `SymbolMetric` uses `ORACLE_CONDITIONED`/`CANDIDATE_CONDITIONED` (repo-wide grep of `Provenance.` outside `prior.py`/`prior_artifact.py`: none).
- `empirical_channel.py:1-25` (docstring) confirms the P3 path marginalizes the low symbol and `build_p1_metrics(bob, p1_table)` (`:330`) takes no Alice/truth/U argument. The P3/P4 diagnostic SC callers (`empirical_diagnostic.py:187,210,285,305,488,553,690,805`; `construction.py:94,206`) all pass P1/erasure metrics — no P2 gather anywhere.
- I additionally verified the production `sc_decode` call-site families (protocol, incremental, construction, empirical_diagnostic) (protocol, incremental, construction, empirical_diagnostic); none conditions the metric on an L2 prior or L1 hard-estimate feedback. The only known-map inputs are Alice disclosures of U coordinates (protocol semantics), not an L2 prior.

Doc verification: `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md:37-38` (row 8 `app_fed_l2_prior` EXCLUDED from first SC path; row 9 `oracle_l2_prior` REFERENCE pattern only) and §4 (`:66-67`, P2_true oracle-only, P2_hat executable dependency) — confirmed. `docs/nbpolar/ROADMAP.md:82-84` — confirmed. `docs/decision-log.md:3811-3814` (the R2 entry states the roadmap oracle-L2 / candidate L2 paths "have not been exercised by those gates") — confirmed (range note below). `P5 OPERATOR_RETURN.md:45-47`, `P5_FREEZE.md:22`, `P6 OPERATOR_RETURN.md:31`, `R1 OPERATOR_RETURN.md:1-9`, `P3 OPERATOR_RETURN.md:9-12/:37` — all confirmed in the packet queue directories.

Conclusion: the audit claim is independently confirmed by code and docs. Only the single-layer L1 high-plane path has ever entered SC; no oracle-L2 or candidate-L2 prior exists in executable production form.

## 7. R2-A09 successor prerequisites

The three prerequisites appear only as decision-output text: `SUCCESSOR_PREREQUISITES` strings in `two_layer_rate.py`, `R2_REPORT.md` §8, and the JSON `successor_prerequisites`. Repo-wide grep finds no implementation (no `two_stage`/`restart_sc`/P2 tensor wiring in the NB-Polar package; the only `two_stage` hits are unrelated NB-LDPC v54/v55 history modules). `tasks.md` has all boxes unchecked; nothing was implemented under R2-A09. Confirmed.

## 8. Tests, scope and integrity

- Focused: `comparison_bench/tests/test_nbpolar_two_layer_rate.py` → **10 passed** (interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, `-q -p no:cacheprovider`, fresh basetemp `/tmp/opencode/pytest_p6r2_focused_review`).
- Full NB-Polar suite `comparison_bench/tests/test_nbpolar_*.py` → **180 passed** in 83.35s (170 predecessor + 10 new), fresh basetemp `/tmp/opencode/pytest_p6r2_full_review`.
- Analysis-path scope inspection: `two_layer_rate.py` imports only `argparse, json, numbers, pathlib, numpy`; no SC/decoder/artifact/parquet/TTBin/attempt/seed/RNG references outside scope-disclaimer strings; writes exactly the two registered artifacts into `--out-dir`; no import-time I/O. The focused test's writes go to pytest/tempdirs only.
- No SC call, no artifact read, no block sampling, no attempt/seed consumption, no old-evidence-root write attributable to the R2 path (code-level inspection; `attempts_used: 0` in STATUS.yaml).
- HEAD unchanged (`ab173f2a...`), R2 work remains uncommitted/untracked; no commit or push performed by the operator or by this review.

## Non-Blocking Suggestions

1. Citation range precision: `R2_REPORT.md` §7 cites `docs/decision-log.md:3811-3812` for the sentence about oracle-L2/candidate-L2 not being exercised; the sentence actually spans lines 3813-3814 (the quoted paragraph starts at 3811). Same item: `prior_artifact.py:215` is `Conditioning.FULL_BOB_ONLY`; `Provenance.PRIOR_ONLY` is at `:216`. `R1 OPERATOR_RETURN.md:1-6` is loosely labelled "single-layer synthetic scope" (the file's first lines describe the three-arm paired gate and line 9 carries the synthetic scope; the single-layer qualifier is in P5/P6). Consider tightening these three ranges in the report/JSON before archiving.
2. `P6R2_IMPLEMENTATION_NOTES.md` §3 K=42 residual uses the cumsum-order value `...946`; the slice-sum order gives `...947`. Both exceed 1e-2, so the boundary claim is unaffected; optionally note the summation order.
3. The `h2_note` sub-claim "agreement ~1e-15 with the accepted V32 audit chain" is not locatable in this checkout's docs; either cite the exact evidence location or soften to the verified V27R/V26 references.
4. The A07 evidence list does not enumerate the P3/P4 diagnostic SC call sites (`construction.py`, `empirical_diagnostic.py`), although they are P1-only and consistent with the claim. Adding one line would make the audit exhaustive.
5. H1 uses the `nll_u1` column while the same row has an `ent` (expected entropy) column differing by ~1.5e-12. Documented and immaterial (0 K changes under the alternative), but worth a one-line note in `REV_NOTES.md` for provenance completeness.

## Checklist

- [x] Matches OpenSpec spec (`f` formula, sensitivity-not-theorem labelling, operational-L2 gap requirement)
- [x] Tests pass (10 focused / 180 total, pinned interpreter, fresh basetemps)
- [x] No scope creep (decision-free analysis only; no decoder, artifact, sampling, attempt/seed, Phase 7, real data, commit/push)
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? — Not blocking: the R2 entry already exists; the citation-range nits above are report/JSON-level and can be fixed before archive. Memory triage (R2-A10) remains a separate pending step, not part of this review.

## Closure statement

No SC/decoder was called; no Model-F artifact/parquet/TTBin was read; no blocks were sampled; no attempts/seeds were consumed; no previous evidence root was modified. The only file written by this review is `.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/INDEPENDENT_RESULT_REVIEW.md`. HEAD remains `ab173f2a5e17336383a897b941080b731ba3dd9e`; no commit or push was made.

Recommendation: proceed to main-thread acceptance with the non-blocking citation fixes optionally applied; acceptance remains a main-thread decision and this review grants no promotion.
