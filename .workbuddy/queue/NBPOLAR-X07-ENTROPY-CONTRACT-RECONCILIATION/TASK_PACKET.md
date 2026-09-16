# X07 Tier-X packet — entropy-contract reconciliation

## Question

Why does the accepted V49 TRAIN channel report approximately
`H1+H2=0.801 bits/symbol`, while the Model-F distribution sampled by X06 reports
approximately `7.61 bits/symbol`? Identify the exact distributions, weighting,
axis convention and smoothing operation behind each number before any further
construction, scaling or decoder work.

This is a deterministic decoder-free provenance audit. It must not decide a
new estimator or silently relabel one entropy as another.

## Frozen inputs

Read:

- `docs/v49_distribution_tables/v49_train_val_hold_nll.csv`, restricted to the
  frozen 1M TRAIN row;
- `docs/v49-distribution-shift-diagnosis-20260827.md`, relevant entropy contract
  only;
- `workspace/probes/nbpolar_x06_empirical_construction_order/results.json`;
- the accepted estimator implementations and already recorded P0/P2/D5/D7
  provenance documents;
- exactly one loader call for the sibling Model-F pair
  `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz`
  and `model_f_input_summary.json`.

X07 has one artifact-content read allowance, consumed on that loader call.
Keep arrays in memory and do not reopen them. No other sibling artifact or raw
data may be read.

## Required calculations

Using float64 plus an independent literal implementation, compute and label
separately:

1. Raw-count MLE `P(A|B)` from `counts_ab[A,B]`, weighted by the empirical Bob
   marginal; report `H(A|B)`, chain `H(U1|B)+H(U2|U1,B)`, and chain residual.
2. Accepted concentration/backoff table produced by
   `smooth_joint_to_conditional(counts_ab,LAMBDA_STAR)`; under empirical `p_b`,
   report:
   - entropy of the smoothed model itself;
   - cross-entropy of raw counts under that model;
   - H1/H2 decompositions and chain residuals for both.
3. The exact distribution X06 sampled (`B~p_b`, then `A~smoothed P(A|B)`), and
   prove algebraically/numerically which result in item 2 its expected H1/H2
   must equal.
4. The V49 CSV definitions and sample domain; compare its H1/H2/total with each
   computed quantity without assuming equality.
5. Axis/packing controls: `[A,B]` versus transpose; `A=32*U1+U2`; p_b versus
   counts-derived Bob marginal; column normalization; zero/unseen columns. A
   mismatched orientation must be reported, never normalized into agreement.
6. Smoothing diagnostics by Bob column: observed count quantiles, number of
   zero/nonzero columns, backoff mixture weight implied by LAMBDA_STAR, and its
   p_b-weighted quantiles/mean. Explain quantitatively whether sparse-column
   shrinkage can account for the entropy jump.
7. For diagnostic attribution only, recompute lambda=0 and the accepted lambda
   table. Do not tune or scan lambda and do not evaluate decoder recovery.

Report a provenance table whose rows are at least: V49 empirical TRAIN entropy,
raw artifact-count MLE entropy, accepted smoothed-model entropy, raw-count
cross-entropy under the smoothed model, and X06 sampling entropy. Each row must
state source population, conditional table, Bob weights, smoothing, and whether
it is an entropy, cross-entropy or sampling-model entropy.

## Output and review

Before the artifact loader call, write `prereg.md` containing the complete
stdlib/NumPy analysis body. Write exactly `prereg.md` and `results.json` under
`workspace/probes/nbpolar_x07_entropy_contract_reconciliation/`; the root must
be absent beforehand. Persist aggregate tables and column-count/weight
quantiles only—no 1024x1024 table, raw counts, samples or private vectors.

Record the loader-call count, formulas, tolerances, mismatches, wall/RSS and
source identities. No decoder, RNG or tag function may be called. No numerical
discrepancy may be repaired by changing axes, floors or weights after reading.

An independent reviewer-go focused review must independently implement all
entropy/CE formulas, audit axes and sampling law, recompute the provenance table
and smoothing-weight diagnostics, and confirm zero decoder/RNG/tag calls and the
two-file write boundary. Its result is trusted under AGENTS.md section 4.1.

## Return and decision boundary

Return descriptive identities and mismatches, including the single earliest
contract divergence that explains X06's all-zero recovery point if one is
established. Do not choose a replacement estimator or claim real-channel
performance. Main thread will use the result to freeze exactly one successor:

- empirical-count construction with an explicit support/backoff rule;
- a justified Model-F smoothing revision; or
- route stop if the accepted artifact cannot represent the intended channel.

STOP on input/root mismatch, second artifact open, axis ambiguity, formula
disagreement, nonfinite result or review mismatch. No retry after artifact open.

Forbidden: production/OpenSpec behavior edits, decoder/RNG/tag, new scientific
attempt, real/raw data, EVAL, construction execution, N>256, FWHT/APP/SCL,
threshold/pass-fail/candidate/accepted, ledger/memory/index update,
qualification/promotion, commit or push.

