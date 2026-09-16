# X06 heavy Tier-X packet — empirical construction-order discriminator

## Question

Using the accepted CAL Model-F distribution, do empirical genie construction
orders for L1 and oracle-conditioned L2 differ materially and stably from the
BEC analytic order, and do those orders change held-out model-sampled SC
recovery at the same disclosure sizes?

This is the last construction discriminator before choosing empirical
construction engineering versus decoder-scaling/FWHT work. It is exploratory:
no threshold, winner, candidate/accepted label or qualification conclusion.

## Frozen input and access accounting

Read these sibling-checkout files exactly once into memory through the accepted
`prior_artifact.load_prior_artifact` path:

- `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz`;
- `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json`.

This package has one artifact-content read allowance, consumed at the first
content open even if later work fails. Do not read raw parquet/TTBin or another
artifact. Derive the conditional table only by the accepted
`smooth_joint_to_conditional(counts_ab,LAMBDA_STAR)`, then `derive_p1` and
`derive_p2`; use stored `p_b`. Keep arrays in memory for all streams. Do not
alter source files or the earlier P3 evidence root.

## Frozen experiment

- GF32 polynomial 37, alpha 2, natural SC order, N=256.
- Model-sample `Bob_full ~ p_b`, then
  `Alice_full ~ P(Alice|Bob_full)` from the accepted in-memory table;
  `high=Alice//32`, `low=Alice%32`.
- TRAIN construction streams `2026091600..2026091602`, 256 blocks each.
- DEV evaluation streams `2026091610..2026091614`, 128 blocks each.
- Streams are disjoint and probe-only. No EVAL stream exists.
- L1 metric is `P(U1|B)`; oracle-L2 metric is `P(U2|U1_true,B)`. Alice truth is
  permitted only in TRAIN genie prefixes, oracle-L2 conditioning, disclosed
  values and scoring. Candidate-conditioned L2 and end-to-end claims are out.

For each layer and each TRAIN stream, use existing `genie_conditionals`
semantics to accumulate per-coordinate error probability and conditional
entropy and produce a worst-first order. Also produce one pooled TRAIN order by
pooling sufficient statistics across all three streams—not by selecting after
DEV.

Construct BEC analytic controls using `epsilon_l=H_l/5`, with H1/H2 recomputed
from the same table. Record that this is a surrogate only.

## Frozen comparisons

Freeze all learned orders before DEV. Report:

- pairwise TRAIN-order and TRAIN-vs-pooled Spearman correlations;
- top-K overlaps at L1 K=`45,60,72,112` and L2 K=`140`;
- pooled empirical-vs-BEC Spearman and the same top-K overlaps;
- coordinate-risk/entropy summaries and complete 256-coordinate public order
  permutations.

On every DEV block, compare pooled empirical and BEC orders at identical sizes:

- L1 SC at K=`45,60,72,112`;
- oracle-conditioned L2 SC at K=`140`.

Use fresh restart SC for each layer/order/K. Persist per-block scalar outcome,
exact flag, initial-error flag and failure class only. Do not persist source,
Bob, U, decoded/disclosed vectors or metric arrays. Report per-stream and pooled
exact/decode-failed/nonfinite counts and paired four-cell tables. `undetected`
is not applicable without a tag and must not be invented or merged into exact.

## Implementation, review and output

Use one preregistered probe body under `/tmp`; no production
module edit. Existing public NB-Polar functions may be imported. Before the
artifact is opened, create
`workspace/probes/nbpolar_x06_empirical_construction_order/prereg.md` containing
the full executable body, inputs, streams and comparisons.

The root must be absent beforehand and contain exactly `prereg.md` and
`results.json` afterward. Record command, artifact-read consumption, wall/RSS,
failures and counts. Limits: 2 GiB and 3600 seconds. Do not rerun or alter the
frozen design after content open.

An independent reviewer-go focused review must independently verify loader and
table derivation, reconstruct one TRAIN stream and one DEV stream, recompute
ranks/overlaps/paired tables, audit truth isolation and confirm the write
boundary. Its result is trusted under AGENTS.md section 4.1.

Return a descriptive summary only. STOP on input mismatch, target-root
presence, loader/normalization failure, truth leak, nonfinite value, resource
limit, unexpected decoder exception or review mismatch; preserve the failure
root with no retry.

Forbidden: production edits, real/raw data, candidate-conditioned L2,
end-to-end claims, new scientific attempt, EVAL, N>256, FWHT, APP, SCL, learned
policy, ledger/memory/index update, qualification/promotion, commit or push.
