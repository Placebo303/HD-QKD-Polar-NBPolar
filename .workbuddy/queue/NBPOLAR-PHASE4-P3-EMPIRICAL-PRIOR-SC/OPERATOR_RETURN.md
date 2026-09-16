# Operator return — NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC (candidate)

Candidate label: `EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE`. This is **not** an
acceptance and not a performance claim. Acceptance, thresholds, and scientific
conclusions remain owned by the main thread.

## Mission

Qualify the boundary from the accepted Model-F count distribution through the
accepted P1 dense `SymbolMetric` into the accepted q-ary SC decoder, under
model-sampled synthetic data only. One artifact-content attempt total.

## Stage A / A2 evidence (synthetic only, artifact never read)

- Deterministic synthetic qualification (P3-A01–A12 plus packing/derivation
  parity): focused file green; full predecessor suite green (final state:
  8-file predecessor suite 120 passed).
- A13/A19 dual-path P1 metric: vectorized operational vs independent
  literal-loop reference, 100 injected asymmetric cases × 2 shapes → max abs
  err 0.0, support mismatch 0 (gate ≤1e-12); production-shape parity vs accepted
  `prior.build_p1_metrics` bitwise 0.0.
- A14 representation: canonical normalized natural-log at the adapter boundary,
  conversion owned by the adapter via accepted `prior.probs_to_symbol_metric`
  (q=32); SC public contract unchanged.
- A15 numerical stress: no NaN/+Inf; `-Inf` exactly the zero mask; positive
  per-row rescaling preserves the decoded decision bitwise.
- A16 metamorphism: butterfly-vs-dense transform (GF4 N=2/4/8, GF32 N=2) 0
  mismatches; Bob-batch permutation equivariance and disclosed-coordinate order
  irrelevance.
- A17 failure taxonomy: each forced case reached its specified fail-loud
  category; nothing degraded into a decode count.
- A18 complexity baseline (injected tables): metric/decode separated, shapes
  `(N,32)`; no size skipped under the frozen stop rule.
- A20 regression isolation: ordinary tests use injected tables and never touch
  the sibling artifact.

## Stage B evidence

### Frozen command (exact 3-line block; executed once, no rerun)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_diagnostic --mode stageb --npz /mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz --summary /mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json --seed 2026091316 --out .workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic
```

### Run result summary

| case | result |
|---|---|
| B1 N=2 | 64/64 executed; exact 8; max_prob_err 1.11e-15; max_log_err 2.22e-15; gates PASS |
| B1 N=4 | 64/64 executed; exact 1; max_prob_err 7.77e-16; max_log_err 5.33e-15; oracle wall 11.075 s; gates PASS |
| B2 | 160/160 executed; exact 31; other 129; impossible 0; nonfinite 0 |
| B3 | 40/40 executed; exact 8; other 32; `n_initial_error` 40; nonfinite 0 |
| B4 | medians (metric/decode): N=64 3.80e-5 / 0.007757 s; N=256 4.31e-5 / 0.034487 s; N=1024 1.179e-4 / 0.167530 s; shapes [N,32]; `disclosed_value_source` true_U; complete |
| B5 | `SC_decision` 119 + `expected_under_disclosure` 161 = 280 = executed 328 − exact 48; all other categories 0 |

Run wall 17.645 s; peak RSS 0.2329 GiB; `truth_leak_violations` 0;
`resource_abort` 0; all 6 hard gates true; `hard_gates_pass` true.
Tests: focused file 32 passed; 8-file predecessor suite 120 passed.

### Attempts / seeds accounting

- Artifact-content attempts allowed 1; **consumed 1/1** at the first artifact
  content open (`frozen_plan.json` → `attempt_accounting.consumed_at_write = 1`,
  `consumed_on = "first artifact content open"`).
- Stage B diagnostic seed **2026091316** used and consumed.
- Unit seed 2026091314 and TRAIN seed 2026091315 recorded as **not used**.
  No EVAL seed exists in P3.

### Review verdicts

- **Pre-EXECUTE (R0)**: `NEEDS_CHANGES` — one blocking item F-1: freeze-v2 §4's
  B5 attribution precedence text was the reverse of the implemented
  `classify_stageb_failure` for the last three categories. Repaired
  **docs-only** by ratifying the implemented classifier semantics (no frozen
  value changed, no code logic changed).
- **Pre-EXECUTE (R1)**: `PASS` — F-1, NB-1, NB-2 closed; NB-4 resolved by the
  hard-gate mapping paragraph; no frozen value drift; plan cleared for its
  single authorized execution subject to main-thread authorization.
- **Pre-RESULT**: `PASS_WITH_COMMENTS` — no blocking issues; all scientific
  gates, counts, isolation and wording checks pass. Three non-blocking
  comments in substance:
  1. B2 per-case `n_nan` alias: B3 cases carry both `n_nonfinite` and `n_nan`,
     B2 cases carry only `n_nonfinite`. This matches freeze §4 verbatim; the
     NaN/nonfinite count is present and 0 for both; a schema note only, no
     count or gate affected.
  2. `attempt_accounting` key name: records `consumed_at_write: 1` plus
     `consumed_on`, with no key literally named `consumed`; value and semantics
     match the requirement.
  3. Bounded-note wording: `report.md`'s closing note lists FER, reconciliation,
     leakage, key rate and construction/K but not the word "performance" that
     `frozen_plan.json`'s `no_claim_note` includes; the B4 timing medians are
     the frozen resource profile, not a performance claim, so no correction is
     required.

## Output files (exactly 5, no extras)

| file | bytes |
|---|---|
| `frozen_plan.json` | 3560 |
| `oracle_records.json` | 1612 |
| `stress_and_profile.json` | 2435 |
| `diagnostic_summary.json` | 21529 |
| `report.md` | 3331 |

Root: `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/`

## Bounded scope

The candidate label is an interface-consistency statement only: the
accepted-CAL-derived P1 metric is numerically consistent with q-ary SC and an
independent tiny oracle under model-sampled data. It is **not** real-data FER,
reconciliation, leakage, key-rate, construction/K or performance evidence, and
does not show that any one construction or K works.

## Forbidden-writes confirmation

No writes to the sibling artifact root, `results/`, or
`comparison_bench/outputs_comparison/`; the accepted artifact was read only
through the accepted loader. Only the five files above were written (single
absent output root, one attempt). No code change, no commit, no push; HEAD
remains `ab173f2a`.

## Environment note (informational only)

Concurrent sibling D7-H writes existed at 01:08:36–01:08:54, i.e. before this
run's window; the frozen artifact root
`.../v72p2d5_model_f_input/20260907_r1/` itself is untouched. This is recorded
for provenance only and is not part of this packet's run.

## Later stages

None. The only remaining gate is main-thread acceptance (with the Pre-RESULT
review already recorded). No Phase 5, no promotion, no commit/push.
