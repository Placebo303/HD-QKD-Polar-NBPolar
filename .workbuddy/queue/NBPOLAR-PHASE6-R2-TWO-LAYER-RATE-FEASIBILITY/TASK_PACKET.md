# Heavy task packet — Phase 6-R2 two-layer rate feasibility

## Mission

Determine whether the NB-Polar route can reach `f<=1.3` under explicit
two-layer BEC surrogate assumptions, identify the resulting target-N band, and
close the audit gap between the roadmap's oracle/candidate L2 paths and the
SC executions actually performed.

## Acceptance IDs

- R2-A01 full-precision H1/H2 inputs and source provenance are frozen.
- R2-A02 recurrence matches an independent literal oracle on tiny N.
- R2-A03 N256/epsilon0.05 gives K43 under the registered union-bound rule.
- R2-A04 N=2^8..2^18 is complete for every source and FER allocation.
- R2-A05 K1/K2, tag bits, nH and f recount exactly.
- R2-A06 first-N meeting f<=1.3 is reported per sensitivity axis.
- R2-A07 oracle-L2 and candidate-L2 execution coverage is evidenced by code/docs.
- R2-A08 BEC results are labelled surrogate estimates, never rigorous bounds.
- R2-A09 Phase 7/scalable-decoder/empirical-construction prerequisites are a
  decision output, not implemented work.
- R2-A10 focused tests, independent result review and memory triage pass.

## Allowed files

Add one small decoder-free analysis module and focused test file; update this
OpenSpec/queue plus CURRENT_TASK, decision log, document index and project
memory. Reuse accepted entropy constants from their existing provenance.

## Stop rules

STOP on ambiguous entropy provenance, failure of the K43 calibration,
disagreement between implementations, nonfinite values, or incomplete
sensitivity axes. Return the earliest blocker without adjusting a formula,
FER budget or input after seeing results.

## Forbidden

No SC decoder call, artifact/parquet/TTBin read, new synthetic block sampling,
old evidence modification, attempt/seed consumption, empirical-channel claim,
FWHT/scalable decoder, SCL/Phase7, real data, qualification, promotion,
commit or push.
