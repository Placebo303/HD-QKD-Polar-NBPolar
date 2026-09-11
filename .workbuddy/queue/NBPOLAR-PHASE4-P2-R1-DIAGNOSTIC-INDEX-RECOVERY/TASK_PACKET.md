# Heavy task packet — P2-R1 diagnostic-index recovery

## Mission and predecessor

Recover only the diagnostic indexing defect from P2 attempt 1. Preserve the
accepted P1 adapter, P2 loader, sibling input and all old evidence. Attempt 1
stays consumed and the original P2 target remains absent.

```text
f3 shape = [U1,B,U2] = (32,1024,32)
wrong     = f3[u1,:,nz_b]
required  = f3[u1,nz_b,:]     -> (n_nonzero_B,32)
weights   = p_b[nz_b,None]     -> (n_nonzero_B,1)
```

This recovery may not revise entropy definitions, smoothing, lambda, input,
thresholds or output schema.

## Required implementation

1. Persist the formerly ad-hoc CAL diagnostic as a small explicit module or
   packet-scoped entrypoint; shell-only scientific calculation is not evidence.
2. Replace only the wrong axis selection with the frozen Bob-axis expression.
3. Use `[U1,B,U2]` in the contract and `nz_b` as the variable name.
4. Preserve loader code unless an existing test fails independently.

## Mandatory pre-read tests

- **R1-T0-01** compile/import/help without sibling content access.
- **R1-T1-01** reproduce the old expression's wrong shape on `(32,7,32)` with
  an asymmetric mask selecting exactly 3 of 7 Bob states.
- **R1-T1-02** corrected selection is `(3,32)` and every element matches an
  explicit coordinate lookup.
- **R1-T1-03** weighted conditional entropy matches a three-loop oracle over
  `u1,b,u2` within 1e-12.
- **R1-T1-04** simultaneous Bob-axis/weight permutation is invariant 1e-12.
- **R1-T1-05** zero-weight Bob states cannot affect the result; zero total
  weight fails loudly.
- **R1-T1-06** one-hot P2 gives 0 bits and uniform P2 gives exactly 5 bits.
- **R1-T1-07** P1+P2 chain identity matches direct joint entropy on a small
  asymmetric distribution within 1e-12.
- **R1-T1-08** tests enter no CAL, decoder, Model-F, raw-data or output path.
- **R1-T2-01** new focused tests and all 79 predecessor tests pass.

Do not rely on square 32-valued axes or an all-true mask; they can hide the
transpose.

## Fresh Pre-EXECUTE gate

A real independent reviewer inspects the corrected expression, asymmetric
tests, unchanged loader, same sibling stat, consumed predecessor attempt,
absent target, command, budget and flags. PASS authorizes one new P2-R1 content
attempt. Self-review does not.

## Authorized read after PASS

Read only:

```text
D:/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/
```

Expected NPZ/JSON sizes remain 208467/752. Do not copy counts or regenerate
input. One attempt may create only:

```text
.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/cal_prior_validation/
  cal_prior_summary.json
  cal_prior_report.md
```

The attempt is consumed at first content open. Refuse an existing target.
Budget remains 300 seconds / <2 GiB. No rerun or alternate root.

## Result checks and scope

Reapply all P2 schema/formula/normalization/fallback/support gates. Independently
recompute P1 entropy, L2 conditional entropy and chain discrepancy. Require
finite values, formula/normalization error <=1e-12, chain discrepancy <=1e-10,
two compact outputs and no private count copy. Results are CAL-resubstitution
descriptions only.

Forbidden: parquet/TTBin, CAL regeneration, lambda/floor change, Model-F fit,
SC/oracle decode, construction/K, DEV/EVAL, benchmark, reconciliation,
FER/leakage/key-rate, P3, sibling/production writes, commit/push or promotion.

Return only `P2_R1_CAL_PRIOR_VALIDATION_CANDIDATE` with one attempt and
independent Pre-RESULT verdict, or `BLOCKED(<single earliest gate>)`. Acceptance
does not open P3.
