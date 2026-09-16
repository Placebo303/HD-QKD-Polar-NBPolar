# NB-Polar Phase 4-P3 specification delta

Phase 4-P3 qualifies the P1 dense `SymbolMetric` → q-ary SC interface with a
controlled, model-sampled development diagnostic. It is not held-out real-data
reconciliation. Implementation tasks live in the companion P3 section of
`tasks.md`; status and acceptance are owned by the main thread, never by the
implementing session.

## Requirement: model-sampled qualification scope

Stage B SHALL sample `B_full` from the accepted `p_b` and `A_high` from the
accepted `P(A_high|B_full)` table with one explicitly seeded
`empirical_channel.make_rng` stream, SHALL build the operational P1 metric from
Bob and the table only, and SHALL transform Alice high symbols to `U` only for
frozen disclosure maps and scoring. The diagnostic SHALL cover exactly: B1
GF32 N=2 and N=4 with no disclosure and at least 64 blocks each; B2 N=16 and
N=64 with the five preregistered masks M1–M5 (all-but-one, prefix, suffix,
alternating, first N/2 of the accepted Phase 3 `analytic_order(0.05, N)`) and
at least 16 blocks per mask; B3 N=256 with every mask unchanged, 8 blocks per
mask (40 total, within 20–64); B4 metric-only and decode-only timing at
N=64/256/1024; B5 earliest-layer attribution. The run SHALL NOT construct a
new reliability order, choose K, tune disclosures, compare rates, or rerun a
failed seed.

## Requirement: interface gates and separated failure accounting

B1 SHALL compare every SC conditional `res.decision_metrics[i]` at the decoded
prefix `res.u_hat[:i]` against an independent exhaustive oracle and SHALL fail
the interface gate only on: probability max error > 1e-12, finite-entry max
log error > 1e-9, support mismatch > 0, numeric failure > 0, or truth-leak
sentinel > 0. The oracle SHALL remain independent of `sc.py` and `oracle.py`
(no SC recursion, no combine helpers); the literal default path and its 4096
candidate cap SHALL remain unchanged, and the vectorized backend SHALL carry
its own cap. B2/B3 SHALL report `exact`, `impossible`, `other` and
`nonfinite`/`n_nan` (plus `n_initial_error` and wall time for B3) separately
and SHALL never merge impossible/other/nonfinite into exact; `exact` SHALL
mean `u_hat == u_true` and `x_hat == x_true` (accepted Phase 3 semantics).
B3 SHALL have no exact-count threshold; its only hard gates SHALL be zero
crash, zero nonfinite and zero truth leak. B5 SHALL classify every non-exact
executed block at its earliest observable layer into exactly:
`artifact_adapter_support`, `normalization`, `disclosure_contradiction`,
`SC_numeric`, `SC_decision`, `expected_under_disclosure`, `unattributed`;
resource soft-stop blocks SHALL be recorded as `resource_abort` and SHALL NOT
be merged into exact counts or failure attribution.

## Requirement: truth isolation

The operational P1 metric builder SHALL accept Bob and the probability table
only; no Alice/truth/U argument SHALL exist in its signature. Alice truth
SHALL enter only the generator, the disclosed-U map and scoring. A truth-leak
sentinel SHALL adversarially mutate sampled truth copies after metric creation
and SHALL require the metric and the resulting decisions (with already-frozen
disclosed values) to stay bitwise unchanged; violations SHALL be counted in
the compact output and SHALL be 0 for the interface gate.

## Requirement: one-attempt artifact boundary and compact output

Stage B SHALL load the single accepted CAL artifact through the accepted
`prior_artifact.load_prior_artifact` exactly once, with the accepted
`smooth_joint_to_conditional(counts_ab, LAMBDA_STAR)` → `derive_p1` derivation
and `p_b = artifact.p_b`; the probability→log conversion SHALL use the
accepted `prior.probs_to_symbol_metric` (q=32). Exactly one artifact-content
attempt SHALL be consumed at the first artifact-content open and SHALL be
consumed regardless of result. The run SHALL refuse an existing output root
before any artifact open, SHALL create the root only after a successful
artifact load, and SHALL write exactly five compact files
(`frozen_plan.json`, `oracle_records.json`, `stress_and_profile.json`,
`diagnostic_summary.json`, `report.md`) at the end. It SHALL write nothing
under `results/`, `comparison_bench/outputs_comparison/`, the sibling
checkout, or any other location, and SHALL NOT write count tables, symbol
vectors, private rows or per-block raw posterior arrays. The stage SHALL use
the frozen diagnostic seed 2026091316 only and SHALL refuse the banned
predecessor range 2026091200..1213.

## Requirement: bounded claim

The only permitted candidate conclusion is
`EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE`: the accepted CAL-derived P1 metric
is numerically consistent with q-ary SC and an independent tiny oracle under
model-sampled data. It SHALL NOT be described as real-data FER,
reconciliation, leakage, key rate or key-yield evidence, nor as evidence that
one construction/K/disclosure pattern works. An independent Pre-EXECUTE review
SHALL pass before the artifact is read, and an independent Pre-RESULT review
SHALL pass before any result or candidate label is published; neither the run
nor the implementing session may accept its own work.
