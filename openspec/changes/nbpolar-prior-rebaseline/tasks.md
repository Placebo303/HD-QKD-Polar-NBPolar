# Tasks: NB-Polar prior re-baseline

Ownership: main thread owns acceptance; operators report evidence only and
never check their own boxes. No task authorizes production-data execution.

## Plan acceptance (this change)

- [ ] T1: independent review of proposal/design/specs (seven decisions
  explicit, four Supersedes replacements named, D7 frozen list intact).
  Gate: review PASS recorded; else revise-required.
- [x] T2: coder packet — implement the M2 adapter (`prior.py` delta:
  per-session triple → model-implied P(A|B) → floor + renorm) with pure
  synthetic fixtures + independent literal oracle; full predecessor suite
  green. Uses injected arrays and temp roots only; no CAL/artifact reads,
  no SC-from-test invocation. Gate: focused tests + T0 pass.
- [x] T3: coder packet — K re-split via frozen `select_empirical_split` on
  M2 tables; the fixed-K vs fixed-f choice is DECOUPLED and deferred to a
  later preregistered decision (f=1.3 ⇒ K_total 7053/7106; frozen K_total ⇒
  f = 1.2939/1.2952). H-proportional rule banned. Gate: K1/K2 recomputed by
  reviewer from frozen selector.
- [x] T4: docs packet — `SECURITY_MODEL.md` CAL note (32-frame sacrifice,
  reveal-bits diagnostic status, no λ_prior term, claim scope unchanged)
  + public-message inventory skeleton. Gate: main-thread doc review.
- [x] T5: freeze the G1 real-data NLL replication (split, seed, margin,
  descriptive-only label). Gate: Pre-EXECUTE-style freeze review PASS.
  Done 2026-09-21: G1 frozen + executed + adjudicated
  (`NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`, bounded
  negative; T6/T7 blocked, not done).
- [x] T6: freeze the G2 real-data decode packet (frozen K1=319/K2=6492,
  accepted blocks first, one-shot, `undetected` isolation, recount,
  budgets, stop rules). Gate: independent Pre-EXECUTE PASS + explicit
  user authorization pasted in full before any run.
  Done 2026-09-22: G2 frozen + executed + adjudicated
  (`NBPOLAR_M2_PRIOR_G2_SUCCESS`; freeze review PASS after 3 FAIL cycles;
  Pre-EXECUTE PASS; Pre-RESULT PASS_WITH_COMMENTS).
- [x] T7: execute T5/T6 exactly once each per freeze; independent
  Pre-RESULT review before any result is published or committed.
  Gate: Pre-RESULT PASS; FAIL blocks solidification.
  Done 2026-09-22: G2 one-shot executed (g2_runs 1, reruns 0),
  Pre-RESULT PASS_WITH_COMMENTS.
- [x] T8: main-thread adjudication (adopt / revise-required / negative
  record). G3 (independent session) and any construction re-derivation
  need their own freezes — explicitly out of this task list.
  Done 2026-09-22: G1 bounded negative recorded, then G1R2 descriptive
  and G2 adjudicated `NBPOLAR_M2_PRIOR_G2_SUCCESS` (B 11/14 vs A2 0/14,
  strict non-overlap). M2 ADOPTED AS CANDIDATE for G3 — it is NOT
  promoted: it stays CANDIDATE until G3 passes. G3 runs under its own
  packet `NBPOLAR-M2-PRIOR-G3-CONFIRM` (out of this task list).

## Acceptance

- [ ] M2 adapter matches the independent oracle (absolute max-error per
  frozen tolerances); truth-leak sentinels hold; `sc.py` untouched.
- [ ] CAL=32 sacrifice, K re-split, and inventory are recomputable from
  frozen artifacts; no frozen number moved post-hoc.
- [ ] G1/G2 reviews recorded; no FER/efficiency/qualification claim made.
- [x] Memory triage completed at close.
  2026-09-22: G2 SUCCESS entry appended to `AGENT_PROJECT_MEMORY.md`
  (headline + 5 bullets: verdict / contract / status-boundaries /
  diagnostic / procedure). Stage-1, G1, S11 and G1R2 entries already
  present. G3 will get its own triage at its close.

## Small-task note

T1 and T4 are docs-only and small enough to implement directly — the
orchestrator may run them without the full pipeline. T2/T3/T5–T7 are not;
they need frozen packets and independent review.
