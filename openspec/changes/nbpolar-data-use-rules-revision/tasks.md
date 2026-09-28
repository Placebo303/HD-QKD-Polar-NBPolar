# Tasks: NB-Polar Data-Use Rules Revision

Status: **draft — PENDING PI adjudication.** Every box stays unchecked and
every task stays gated until the PI records the T1 ruling. This file grants
no execution, no doc edit, no lock change by itself.

- [ ] T1 — **PI adjudication gate (blocks T2-T7).** Rule on:
  - **(i)** Accept / modify / reject R1-R5 (`design.md` D7) as new standing
    rules (candidate location: `AGENTS.md` new §5.8, or `docs/nbpolar/
    STATE.md` — PI to choose placement).
  - **(ii)** `D-FER-03` (`n=65`): keep as-is, or re-adjudicate against D6(i)
    `n≈14` or D6(ii) `n≈56` (Wilson-upper, recommended by this proposal as
    the more conservative of the two updated values), or a different `p`.
  - **(iii)** `D-ACQ-02/03` replacement (`design.md` D8 source/
    stratification) and `D-ACQ-05` rewording (narrowed to the two 2026-01-13
    SHG conditions) — accept, modify, or reject.
  - **(iv)** Candidate decode configuration for R2 (`M2 + SCL(L=16, top_m=4,
    CRC-16), K1=319/K2=6492, P16`) — accept as a *candidate* (not a frozen
    R2 config; R2's own T4 still adjudicates the frozen contract), or reject.
  - **(v)** Whether the D9 `participation_ledger.json` naming issue needs a
    fix (T6) or is a non-issue.
  - Needs user authorization: **YES — this is the blocking gate.**

- [ ] T2 — Create `docs/nbpolar/DATA_LEDGER.md`: one row per session × frame
  segment, recording use (CAL/CAL32/CHAR/HELDOUT/EVAL/RESERVE/未采集),
  contact type (decoder-free / decoder-touched / model-selection-touched),
  and remainder. Seeds from `workspace/acq_inventory_20260928/REPORT.md`
  §(e)/(g) and `participation_ledger.json`. **Gated on T1(v).**
  Needs user authorization: NO (docs-only, once T1 clears).

- [ ] T3 — Fix `docs/nbpolar/STATE.md`: (a) `:79` stale "`SECURITY_MODEL` has
  NO CAL/prior term" line — strike or point to `SECURITY_MODEL.md:107-129`
  (`design.md` D2); (b) reconcile the two exhaustion batches at `:81,90`
  with `FUTURE_DIRECTION_PLAN_20260924.md:36-37` (`design.md` D5); (c) where
  "contamination"/"污染" is used as a rationale, relabel per the (B)/(C)
  split (`design.md` D3), only if T1(i) accepts that reading. **Gated on
  T1(i).** Needs user authorization: NO (docs-only, once T1 clears).

- [ ] T4 — Draft an `AGENTS.md` amendment adding R5 (`design.md` D7) as a new
  §5.8 clause, for a *separate* OpenSpec change to apply (this change does
  not edit `AGENTS.md` itself per AGENTS.md §3 "modifies...workflow rules →
  create/update an OpenSpec change first"). **Gated on T1(i).** Needs user
  authorization: NO (drafting only; the actual `AGENTS.md` edit needs its
  own change + PI sign-off).

- [ ] T5 — Revise `openspec/changes/nbpolar-r2-fer-measurement-contract/`:
  update `D-ACQ-02/03/05` rows and ledger per `design.md` D8; add the two
  `n` recomputations (D6) as new candidate rows alongside the existing
  `D-FER-03=65`, explicitly not overwriting it. **Gated on T1(ii)+(iii).**
  Needs user authorization: NO (docs-only, once T1 clears); does not by
  itself freeze the R2 contract (T4/T5/T6 of that change still apply).

- [ ] T6 — Clarify `workspace/acq_inventory_20260928/participation_ledger.
  json`'s `eval_blocks_per_session_formula` key naming (`design.md` D9) —
  rename or annotate to make clear it counts *additional* post-4190 blocks,
  not the existing 14-block EVAL segment. **Gated on T1(v); skip if T1(v)
  rules this a non-issue.** Needs user authorization: NO (comment/rename
  only; no numeric value changes).

- [ ] T7 — **NOT AUTHORIZED by this change.** A 64-block R2 execution packet
  (TASK_PACKET.md/PROMPT.md/STATUS.yaml/AUTHORIZATION_PROMPT.md) using the
  T5-revised contract is a separate, later change — it requires its own
  Pre-EXECUTE review and explicit PI authorization, and requires the R2
  contract's own `D-ACQ-02/03/05` and `D-FER-03` rows to reach `DECIDED`
  first (R2 `tasks.md` T4/T5/T6 gates, unchanged by this change).

## Standing rule

No task above writes to `STATE.md`, `AGENTS.md`, the R2 contract document,
or `DATA_LEDGER.md` until T1 is ruled. This change touches only its own
`openspec/changes/nbpolar-data-use-rules-revision/` directory.
