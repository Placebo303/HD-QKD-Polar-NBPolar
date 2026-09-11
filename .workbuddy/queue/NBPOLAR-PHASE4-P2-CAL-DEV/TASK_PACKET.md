# Heavy task packet — Phase 4-P2 accepted CAL artifact to prior tables

## State

`PLAN_READY_AWAITING_EXPLICIT_AUTHORIZATION`. This packet authorizes nothing
until the user sends `AUTHORIZATION_PROMPT.md` to the execution session and the
session applies exactly that status transition.

P1 is `IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY`. P2 validates the accepted pure
adapter against one already-accepted, read-only Model-F input artifact. It does
not run SC, choose a Polar construction, measure reconciliation, or read raw
parquet/TTBin.

## Mission

Load the accepted sibling artifact exactly once through a new NB-Polar-specific
read-only adapter boundary, independently recalculate every table, and produce
a compact development evidence candidate proving that the P1 formulas, axes,
fallbacks and provenance hold on the real CAL count table.

The decisive output is a validated immutable in-memory/table summary, not a
decoder result. Any mismatch stops before SC and is attributed to artifact
identity, loader/schema, formula, axis, packing, support or provenance.

## Frozen input

Owning sibling checkout, read-only:

```text
D:/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/
  model_f_input.npz              expected 208467 bytes
  model_f_input_summary.json     expected 752 bytes
```

Accepted provenance is documented by the sibling
`docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/
MODEL_F_INPUT_RESULT_ACCEPTANCE_R1.md` and Pre-RESULT R2 review. Expected NPZ
keys are exactly `counts_ab,p_b`; `allow_pickle=False`; counts shape
`(1024,1024)`, axis `[Alice,Bob]`, sum 262144; `p_b` shape `(1024,)`; session
`20260123_1M_600k_0dB`; CAL frames 702..1725; 256 pairs/frame; GF32 poly37;
lambda 137.3823795883264.

The sibling root is a source input only. Never modify it, copy into its
directory, regenerate it, or invoke its historical decoder/producer.

## Pre-execution gate P2-G0

Before reading NPZ/JSON contents:

1. Confirm branch and current P1 accepted status.
2. Confirm exact sibling root and exactly two expected regular filenames.
3. Stat names/sizes only and compare to the expected values above.
4. Confirm no target P2 evidence directory exists.
5. Run the 66-test NB-Polar focused regression and P1 11-test subset.
6. Freeze the exact loader call, output directory, budgets and stop rules.
7. Obtain a real independent reviewer PASS on G0.

If any item fails, return `BLOCKED(P2_G0_<reason>)` without reading artifact
contents. Do not substitute pytest fixtures, D6 temp roots, reconstructed
counts, raw parquet, or another Model-F root.

## Allowed implementation

Add only:

- `formal_ir/nbpolar/prior_artifact.py`: small read-only loader returning a
  frozen record with `counts_ab`, `p_b`, identity and provenance. NumPy +
  stdlib only; `np.load(..., allow_pickle=False)` and the frozen schema.
- `tests/test_nbpolar_prior_artifact.py`: synthetic temporary NPZ/JSON fixtures,
  tampered axis/sum/key/identity cases, no sibling or production path access.
- one P2 diagnostic entrypoint requiring the exact sibling input path and
  writing only to the P2 queue evidence directory.
- minimal `__init__.py` exports only if the loader is a public API.
- packet-local plan, G0 review, result and Pre-RESULT review documents.

Do not import sibling production modules. Reimplement the small schema and
literal formula independently from the accepted P0/P1 contracts.

## Validation matrix

- **P2-T0-01** compile/import without reading the sibling root.
- **P2-T0-02** help/dry-run touches no input content or output.
- **P2-T1-01** exact two-key NPZ; object arrays rejected.
- **P2-T1-02** counts `(1024,1024)`, nonnegative integer-valued, finite, sum
  exactly 262144.
- **P2-T1-03** `p_b` `(1024,)`, finite/nonnegative, sum within 1e-12, equals
  `counts_ab.sum(axis=0)/262144` within 1e-12.
- **P2-T1-04** asymmetric fixture detects `[Bob,Alice]` transpose.
- **P2-T1-05** summary identity matches session/CAL/frame/pairs/axis/packing/
  GF/lambda/status and lists exactly the two artifact files.
- **P2-T1-06** independent literal concentration formula matches P1 within
  maximum absolute 1e-12.
- **P2-T1-07** P1 P1/P2 tables have correct shapes/normalization and match
  independent loops on selected asymmetric slices.
- **P2-T1-08** unseen-B and zero `(U1,B)` fallbacks and exact-zero support are
  counted and match frozen rules.
- **P2-T1-09** exhaustive packing identity over all 1024 labels.
- **P2-T1-10** operational loader accepts no Alice truth vector and exposes
  only `PRIOR_ONLY/FULL_BOB_ONLY` provenance.
- **P2-T1-11** banned per-cell twin and historical decoder imports absent.
- **P2-T1-12** output no-overwrite; tests inject temp roots only.
- **P2-T2-01** full predecessor regression plus new focused tests.
- **P2-T2-02** sole authorized read creates only the two compact outputs below
  and never copies the private count table.

## CAL diagnostic semantics

Report maximum formula and normalization errors, fallback/support counts,
`H(A_high|B)`, `H(A_low|A_high,B)` and their sum in bits/symbol, direct chain
discrepancy, optional CAL-resubstitution CE, wall time and RSS. These are
CAL-only descriptives, never held-out performance. Do not reuse `7.162347` as a
threshold or select floor, K, rate, construction, disclosure or decoder values.

## Output, budget and stop

Target, absent before execution:

```text
.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/cal_prior_validation/
  cal_prior_summary.json
  cal_prior_report.md
```

Refuse an existing root. Budget 300 seconds and peak RSS <2 GiB when
measurable. Stop on schema mismatch, nonfinite output, formula/normalization
error >1e-12, source mutation, output collision or resource limit. No rerun
after an artifact-content attempt without a new main-thread disposition.

## Reviews and forbidden scope

Pre-EXECUTE checks path, two-file identity, target absence, command, tests,
budget, flags and zero decoder/raw-data path. Pre-RESULT independently reloads
and recalculates schema, marginals, formula, fallbacks, entropy and output
semantics; it verifies no count copy and no SC call.

Forbidden: raw parquet/TTBin, CAL regeneration, Model-F fitting/lambda
selection, DEV/EVAL, SC/oracle decode, construction/K, floor selection,
benchmark/protocol/reconciliation, FER/leakage/key rate, Phase 5, sibling or
production-output writes, commit/push and promotion.

## Return

Return `P2_CAL_PRIOR_VALIDATION_CANDIDATE` with full evidence and independent
Pre-RESULT verdict, or `BLOCKED(<single earliest gate>)` with raw output,
content-read attempt count, allowed remedies, later items not run and one
needed decision. Acceptance does not open empirical-prior SC; that is P3.
