# NB-Polar probe tier (Tier X) and decision gates (Tier Y)

This is the compact operator template for the two-tier execution rule in
`AGENTS.md` §10.4. It adds no authorization of its own.

## Two tiers

- **Tier X — probe runs (non-claim).** Cheap synthetic sensitivity work inside
  any authorized packet. It produces planning evidence only: no candidate or
  accepted token, no attempt consumption, no change of scientific status.
- **Tier Y — decision gates (claims).** Claim-bearing execution with explicit
  user authorization, frozen thresholds, one-shot attempt, independent
  Pre-EXECUTE and Pre-RESULT reviews, and main-thread acceptance.

## Tier-X template

1. `prereg.md` — exactly three lines: question | parameters | exact command.
   Parameters (N, models, seeds, masters) freeze here and may not change after
   prereg. A rerun to fix an execution error is allowed; it must be recorded in
   `results.json`.
2. `results.json` — ONE record with per-seed values plus mean, sample standard
   deviation and range; include every execution/rerun log and exact commands.
3. Root discipline — write only under `workspace/probes/<id>/`.
4. No candidate/accepted token, no pass/fail verdict, no attempt accounting,
   no decision-log/index/project-memory update (batch those at milestones).
5. Focused review only — commands, completeness, arithmetic, truth isolation,
   write-scope. Not Pre-EXECUTE/Pre-RESULT.

Forbidden in Tier X: artifact/real-data access, writes outside the probe root,
claim-bearing thresholds, and per-probe ledger updates.

## Tier-Y threshold evidence

A new claim-bearing synthetic threshold must cite prior Tier-X
variance/sensitivity evidence for that point, or state in the freeze that the
frozen sample cannot discriminate the hypothesis.

## Delta-successor fast path

A same-point semantic correction may reuse the unchanged predecessor contract:
one delta document, one independent freeze review, one execution, one Pre-RESULT
review, milestone-batched ledger updates. Everything not listed as changed in
the delta document is inherited.
