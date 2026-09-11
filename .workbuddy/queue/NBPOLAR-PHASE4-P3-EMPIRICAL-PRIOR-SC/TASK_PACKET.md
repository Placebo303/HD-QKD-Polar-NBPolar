# Heavy task packet — Phase 4-P3 empirical-prior SC interface qualification

## Purpose

Qualify the boundary from the accepted Model-F count distribution through the
P1 dense `SymbolMetric` into the accepted q-ary SC decoder. This is a controlled
model-sampled development experiment, not held-out real-data reconciliation.

P3 must answer three linked questions: given Bob symbols and a prior table
derived from the accepted CAL artifact, (1) does SC compute the same q-ary
synthetic-channel conditionals as independent exhaustive calculations on tiny
blocks, (2) is the interface numerically stable across realistic and adversarial
synthetic probability shapes, and (3) where do runtime and memory first become
material as N and the disclosure pattern change? Alice truth must never enter
operational inputs.

This is deliberately a heavy autonomous research packet. The operator should
continue useful synthetic exploration, implementation repair, tests and review
within the frozen boundaries instead of returning after the first working
example. Routine code defects, test defects and documentation inconsistencies
inside the allowed files are owned by the operator. Return BLOCKED only for a
contract conflict, accepted predecessor defect, exhausted artifact attempt,
resource stop, or a scientific ambiguity that changes the frozen experiment.

## Frozen input and attempt

Read only the same accepted sibling artifact once after Pre-EXECUTE PASS:

```text
D:/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/
```

NPZ/JSON sizes 208467/752; exact accepted P2 loader and concentration formula.
Do not use the P2 output summaries as probability tables and do not copy the
count matrix. One P3 artifact-content attempt is consumed on first open.

## Model-sampled source

Build a P3-local generator with frozen semantics:

1. sample `B_full` from accepted `p_b`;
2. sample `A_full` from accepted `P(A|B)` using an explicitly seeded RNG;
3. split `A_high=(A_full>>5)&31`, `A_low=A_full&31`;
4. build P1 metrics `P(A_high|B_full)` using only Bob and the accepted table;
5. transform Alice high symbols to U only for frozen disclosure/scoring.

Alice truth is forbidden from the metric builder, SC likelihood, candidate
selection or construction. It may enter the generator, disclosed-U map and
scoring. Mutating stored Alice truth after metric creation must not change the
metric.

Use new disjoint seeds selected and frozen before sampling. Phase 3 seeds
2026091200..1213 and all earlier official seeds are banned. Unit, TRAIN and
diagnostic seeds must be distinct. There is no EVAL seed in P3.

## Required implementation

- `formal_ir/nbpolar/empirical_channel.py`: accepted-artifact-conditioned
  sampling and P1 metric construction; NumPy + local P1/P2 modules only.
- `formal_ir/nbpolar/empirical_oracle.py`: independent tiny-N exhaustive
  enumeration of `P(U_i | U_<i, B)` from literal `P(A_high|B)` products and the
  dense transform. It must not call SC recursion or reuse SC combine helpers.
- `tests/test_nbpolar_empirical_sc.py`: all tests below, with synthetic small
  tables first and injected artifact objects. Ordinary tests never read the
  sibling root.
- one packet-local P3 diagnostic entrypoint with explicit artifact path, seed,
  N, block count and output path; no defaults to production paths.
- an OpenSpec Phase 4-P3 delta and packet-local plan/reviews/result docs.

The operator may choose internal data structures, vectorization strategy and
test decomposition after comparing at least two plausible implementations.
Keep a concise `EXPLORATION_NOTES.md` recording hypotheses, alternatives tried,
measured evidence, rejected choices and the final reason. Do not build a generic
framework: exploration must directly improve correctness, numerical stability
or measured SC cost.

Do not modify accepted transform/sc/prior/prior_artifact/cal_diagnostic logic
unless an independent oracle proves a defect; such a defect blocks P3 for a
main-thread ruling rather than being patched inside this packet.

## Stage A — deterministic synthetic qualification, no artifact read

- **P3-A01** asymmetric hand table confirms Bob-axis gather and row
  normalization <=1e-12.
- **P3-A02** generator frequencies converge to an asymmetric injected table in
  a fixed large sample with preregistered absolute tolerance; this is a unit
  sanity, not evidence.
- **P3-A03** fixed RNG seed reproduces B/A sequences; distinct seed differs.
- **P3-A04** operational P1 metric signature has no Alice/truth/U argument.
- **P3-A05** Alice-truth mutation changes neither Bob nor P1 metric bitwise.
- **P3-A06** exhaustive oracle agrees with direct enumeration for GF4 N=2/4.
- **P3-A07** q-ary SC conditional probability and log metric agree with the
  independent oracle for every decoded coordinate on GF4 N=2/4 within 1e-12
  probability and 1e-9 log error, including exact-zero support.
- **P3-A08** GF32 N=2 oracle comparison covers one-hot, uniform and asymmetric
  rows; maximum errors use the same thresholds.
- **P3-A09** arbitrary frozen U values, including zero, remain distinguishable
  from undisclosed coordinates.
- **P3-A10** wrong disclosed value with zero conditional support produces the
  accepted impossible-disclosure failure category.
- **P3-A11** no oracle helper is exported from `nbpolar.__init__` or imported by
  the operational channel/SC modules.
- **P3-A12** full predecessor suite plus new tests passes; no sibling content
  access occurs during pytest.

### Stage A2 — autonomous synthetic exploration

Complete all tracks before Pre-EXECUTE review:

- **P3-A13 dual-path likelihood:** implement an operational vectorized P1
  metric path and an independently written literal-loop reference. Compare on
  at least 100 asymmetric injected cases spanning dense, sparse, one-hot and
  exact-zero rows. Maximum normalized probability error <=1e-12 and support
  mismatch 0.
- **P3-A14 representation study:** compare normalized probability and
  normalized natural-log representations at the adapter boundary. Freeze one
  canonical representation and document conversion ownership; do not modify
  the accepted SC public contract.
- **P3-A15 numerical stress:** cover dynamic ranges down to the accepted floor,
  exact zeros, a single surviving symbol, uniform rows and concentrated rows.
  No NaN/+Inf; -Inf is allowed only for true zero support. Scaling a likelihood
  row by a positive constant must not change the decoded decision.
- **P3-A16 transform/interface metamorphism:** for GF4 N=2/4/8 and GF32 N=2,
  compare natural-order transform enumeration, disclosed-coordinate forcing and
  SC conditionals under deterministic permutations of test cases.
- **P3-A17 failure taxonomy:** deliberately produce impossible disclosure,
  malformed normalization, invalid symbol, wrong shape and nonfinite input;
  verify each reaches its specified fail-loud category and never becomes a
  decode failure or success count.
- **P3-A18 complexity baseline:** benchmark metric construction and SC decode
  separately for N={2,4,8,16,64,256,1024} where feasible, using injected tables.
  Record the median of at least 5 calls after one warm-up, peak RSS, array shapes
  and empirical scaling. Skip a size only after the prior size exceeds 120 s or
  RSS reaches 1.5 GiB, and record the exact stop.
- **P3-A19 implementation comparison:** evaluate at least one vectorized path
  against a literal/reference path. Select on exact equivalence, readability and
  measured cost. Retain only the operational path and independent oracle.
- **P3-A20 regression isolation:** prove all Stage A tests run with sibling
  artifact access disabled or replaced by an injected object. Run the full
  accepted predecessor suite once at the milestone.

## Pre-EXECUTE review

Before the one artifact read, freeze:

- exact unit/TRAIN/diagnostic seeds;
- Stage B block sizes and sample counts;
- disclosure patterns and thresholds;
- exact command and absent output root;
- artifact identity and attempt count;
- runtime 3600 s total and RSS <2 GiB; per-case 120 s soft stop;
- truth-isolation and zero raw-data/DEV/EVAL/reconciliation paths.

A real independent reviewer PASS is mandatory. Needs-changes may be repaired
before artifact access. No self-authorization.

## Stage B — one accepted-artifact development diagnostic

After review, load the artifact once and keep all probability tables in memory.
Run in this order:

1. **B1 tiny oracle:** GF32 N=2 and N=4, at least 64 model-sampled blocks each;
   compare every SC conditional to exhaustive oracle. Hard gate: probability
   max error <=1e-12, log max error <=1e-9, support mismatch 0, numeric failure
   0, truth-leak sentinel 0.
2. **B2 disclosure-shape matrix:** for N=16 and N=64, run preregistered masks
   covering all-but-one disclosed, prefix/suffix, alternating and a construction
   order imported unchanged from accepted synthetic Phase 3. Use at least 16
   blocks per shape. Report exact, impossible, other and nonfinite separately.
3. **B3 N=256 bounded sanity:** no exhaustive oracle. Use every preregistered
   mask unchanged, at least 20 and at most 64 blocks total. Report
   initial MAP errors, exact recovery, impossible/other/nan separately and wall
   time. No pass threshold based on exact count; only zero crash/nonfinite/truth
   leak is a hard gate.
4. **B4 resource profile:** repeat metric-only and decode-only timing at
   N={64,256,1024} with the in-memory accepted table and frozen masks. Use at
   least 5 measured calls after warm-up where the 120 s case cap permits.
5. **B5 attribution matrix:** classify each failure at its earliest observable
   layer: artifact/adapter support, normalization, disclosure contradiction,
   SC numeric, SC decision, expected under-disclosure, or `unattributed`.

Do not construct a new reliability order, choose K, tune disclosures, compare
rates or rerun a failed seed. If B3 reveals poor recovery, that is information
for a later construction packet, not permission to tune P3.

## Output

One absent additive root under this packet:

```text
empirical_prior_sc_diagnostic/
  frozen_plan.json
  oracle_records.json
  stress_and_profile.json
  diagnostic_summary.json
  report.md
```

No count table, symbol vectors, private rows or per-block raw posterior arrays
are written. Refuse an existing root. Attempt and seed are consumed regardless
of result.

## Pre-RESULT and acceptance

Independent reviewer recomputes tiny-oracle comparisons, thresholds, support
and failure counts; checks Alice truth isolation, seed separation, disclosure
accounting, absence of raw/private outputs and bounded wording. Pre-RESULT FAIL
blocks candidate solidification.

Allowed candidate conclusion: `EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE`, meaning
the accepted CAL-derived P1 metric is numerically consistent with q-ary SC and
an independent tiny oracle under model-sampled data. It is not real-data FER,
reconciliation, leakage, key rate or evidence that one construction/K works.

## Forbidden

No raw parquet/TTBin, held-out real frames, DEV/EVAL, L2-candidate chain,
adaptive construction, SCL/CRC, protocol, rate adaptation, reconciliation,
benchmark, result roots, Phase 5, sibling writes, commit/push or promotion.

## Return

Return only `EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE` with complete Stage A/B
evidence and independent Pre-RESULT verdict, or `BLOCKED(<single earliest
gate>)` with attempt count, raw failure and later stages not run.
