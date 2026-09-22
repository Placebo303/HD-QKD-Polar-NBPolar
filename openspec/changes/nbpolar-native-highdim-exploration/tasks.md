# Tasks: native high-dimensional exploration (docs/plan/review only)

Ownership: main thread owns acceptance; operators report evidence only and never check
their own boxes. **No task authorizes code, execution, Tier-X runs, Tier-Y gates,
freezes, or production-data access.** Role rules per AGENTS.md §4: planner writes no
production code; reviewer edits no files; coder never self-accepts.

## Plan acceptance (this change)

- [ ] T1: planner — write the Step-0 survey prereg skeleton (read-only input paths,
  histogram/|Δ|/occupancy/period-crossing definitions, denominators, stop rule).
  Gate: every input path is read-only and non-`.ttbin`; frozen numbers verbatim.
  Needs user authorization: NO (docs only).
- [ ] T2: reviewer-go — independent review of T1 (scope, truth isolation,
  DEVELOPMENT/confirmation boundary, write-root discipline). Output findings only.
  Gate: review PASS else revise-required. Needs user authorization: NO.
- [ ] T3: planner — write the Step-1 small-q screening design (q ∈ {4,8,16} arms A/B,
  matched conditions, FER–f separation metric, Tier-X prereg template, numeric
  no-go condition placeholder for the future freeze). No algorithm selected here.
  Gate: sim/real firewall + stop-loss-as-design present; no run authorized.
  Needs user authorization: NO.
- [ ] T4: reviewer-go — independent review of T3 (Park–Barg/MSD fairness of arm B,
  separation-statistic checkability, post-hoc-tuning guards). Findings only.
  Gate: review PASS else revise-required. Needs user authorization: NO.
- [ ] T5: planner — write the Step-2 transfer-prior design (uniform vs informed init,
  fixed M2-transition reference, gain metric, negative-recording rule, EVAL/RESERVE
  boundary guard). No prior-code change.
  Gate: boundary guard explicit; no confirmation-data consumption path.
  Needs user authorization: NO.
- [ ] T6: planner — write the Step-3 adjudication + GF(32) probe envelope (assumption
  list, ops/memory-vs-budget table skeleton, SCALE/PROBE-ONLY/STOP trifurcation with
  falsifiers, sibling-negative constraints). No implementation.
  Gate: every complexity figure carries its assumption; no code path opened.
  Needs user authorization: NO.
- [ ] T7: coder-doc — assemble the exploration index (steps ↔ designs ↔ future
  write-root map, ledger schema L1/L2/L3, §5.7 minimalism checklist, frozen-number
  recheck table). Docs only; no production code.
  Gate: main-thread doc review; zero edits outside this change directory.
  Needs user authorization: NO.
- [ ] T8: reviewer-go — final independent review of proposal/design/tasks consistency
  (frozen-number invariance, no-delta-spec rationale, Tier-X/Tier-Y division,
  stop-loss checkability, role-rule compliance). Findings only.
  Gate: review PASS else revise-required. Needs user authorization: NO.
- [ ] T9: memory — memory triage at close (durable entries only, no speculative
  content). Gate: triage recorded. Needs user authorization: NO.

## Explicitly out of this task list (each needs its own packet + user authorization)

- O1: any Tier-X probe run (Steps 0–2) — needs its own `prereg.md` freeze + pasted
  full authorization text before execution; writes only to
  `workspace/exploration/nbpolar-native-highdim/<id>/`.
- O2: any Tier-Y decision gate or claim-bearing statement — needs independent
  Pre-EXECUTE + Pre-RESULT reviews and main-thread acceptance.
- O3: any decoder implementation, GF(32) graph work, prior/CAL change, freeze edit,
  or new-data test — each needs its own OpenSpec change.
- O4: Stage-3 re-entry — needs a discriminative-power-restoring design under its
  own freeze (see proposal §Stage-3).

## Small-task note

T1–T9 are all docs/review/memory and small enough to implement directly — the
orchestrator may run them without the full implement pipeline. O1–O4 are not small
and are not authorized here at all.
