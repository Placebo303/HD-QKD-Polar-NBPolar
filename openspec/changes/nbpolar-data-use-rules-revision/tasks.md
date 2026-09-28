# Tasks: NB-Polar Data-Use Rules Revision

Status: **draft — PENDING PI adjudication.** Every box stays unchecked and
every task stays gated until the PI records the T1 ruling. This file grants
no execution, no doc edit, no lock change by itself.

- [x] T1 — **PI adjudication gate (blocks T2-T7).** Rule on:
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

  **PI RULING (2026-09-28, in-chat verbatim: "按建议批准，继续推进"). T1 =
  DECIDED:**
  - **(i)** R1-R5 (`design.md` D7) **adopted as-is**. Placement: `AGENTS.md`
    new subsection under §5/§10 (see `AGENTS.md` "Data-use rules (R1-R5)"),
    plus the durable ledger `docs/nbpolar/DATA_LEDGER.md` (T2).
  - **(ii)** `D-FER-03` **re-adjudicated**: `n = 56`, derived from the
    Wilson-upper bound `p≈0.1771` on the SCL(L=16) 27/28 real-data result
    (`docs/decision-log.md` 2026-09-28 "27/28" entry), `z=1.96`, `w=0.10`
    (`design.md` D6(ii)). This **supersedes** `n=65`; the original `n=65`
    value and its `p=3/14` derivation are **retained, annotated as
    superseded**, not deleted (R2 `tasks.md`/contract T5 carries this
    forward).
  - **(iii)** `D-ACQ-02` and `D-ACQ-03` = SHG `_1`/`_2`, full sessions, **64
    blocks total**. Per session (32 blocks): frames 0-1023 → 8 blocks
    (A1_CAL stratum); frames 1056-2397 → 10 blocks, 62-frame remainder
    unused (CHAR+HELDOUT stratum); frames 2398-4189 → 14 blocks (EVAL
    stratum, already decoded). CAL32 stays 1024-1055 (32f, excluded/
    sacrificed in both sessions). `D-ACQ-05` = scope narrowed to "applies
    only to the two 2026-01-13 SHG acquisitions' own conditions" (`design.md`
    D8). HELDOUT (1838-2397) and the already-decoded EVAL (2398-4189) are
    reported in **separate strata**, never merged into one unstratified FER
    number.
  - **(iv)** Candidate decode configuration for R2 **accepted as candidate**:
    `M2 + SCL(L=16, top_m=4, CRC-16), K1=319/K2=6492, P16` — to be **formally
    frozen before execution** (R2's own T4 still governs the frozen
    contract; this is not itself a freeze).
  - **(v)** D9 `participation_ledger.json` naming issue: **needs a rename/
    annotation fix** (T6) — not a non-issue; the numbers are not wrong, but
    the key name is misleading.

- [x] T2 — Create `docs/nbpolar/DATA_LEDGER.md`: one row per session × frame
  segment, recording use (CAL/CAL32/CHAR/HELDOUT/EVAL/RESERVE/未采集),
  contact type (decoder-free / decoder-touched / model-selection-touched),
  and remainder. Seeds from `workspace/acq_inventory_20260928/REPORT.md`
  §(e)/(g) and `participation_ledger.json`. **Gated on T1(v).**
  Needs user authorization: NO (docs-only, once T1 clears).
  **Done 2026-09-28**: `docs/nbpolar/DATA_LEDGER.md` created (§1-§7: SHG
  `_1`/`_2` per-segment history, `20260112_Type2PPLN_3s`, config-mismatched
  sessions, old P-series, R2 §7 64-block source list).

- [x] T3 — Fix `docs/nbpolar/STATE.md`: (a) `:79` stale "`SECURITY_MODEL` has
  NO CAL/prior term" line — strike or point to `SECURITY_MODEL.md:107-129`
  (`design.md` D2); (b) reconcile the two exhaustion batches at `:81,90`
  with `FUTURE_DIRECTION_PLAN_20260924.md:36-37` (`design.md` D5); (c) where
  "contamination"/"污染" is used as a rationale, relabel per the (B)/(C)
  split (`design.md` D3), only if T1(i) accepts that reading. **Gated on
  T1(i).** Needs user authorization: NO (docs-only, once T1 clears).
  **Done 2026-09-28**: (a) struck-through with pointer to
  `SECURITY_MODEL.md:107-129`; (b) both "ladder 已耗尽" mentions and the
  §0/C5 correction annotated to name the old P-series and point to
  `DATA_LEDGER.md`; (c) the one "污染" occurrence (S11 pairing-window
  finding) annotated to distinguish it from the R1-R5 (B)/(C) reading, since
  it is a distinct physical/technical finding, not a reflow-rationale label;
  §0 new summary bullet appended.

- [x] T4 — Draft an `AGENTS.md` amendment adding R5 (`design.md` D7) as a new
  §5.8 clause, for a *separate* OpenSpec change to apply (this change does
  not edit `AGENTS.md` itself per AGENTS.md §3 "modifies...workflow rules →
  create/update an OpenSpec change first"). **Gated on T1(i).** Needs user
  authorization: NO (drafting only; the actual `AGENTS.md` edit needs its
  own change + PI sign-off).
  **Done 2026-09-28, applied directly**: this change is itself the OpenSpec
  basis for the `AGENTS.md` edit (per the operator's explicit framing in the
  task packet), so §5.8 "Data-use rules (R1-R5)" was written directly into
  `AGENTS.md` rather than drafted for a later change to apply.

- [x] T5 — Revise `openspec/changes/nbpolar-r2-fer-measurement-contract/`:
  update `D-ACQ-02/03/05` rows and ledger per `design.md` D8; add the two
  `n` recomputations (D6) as new candidate rows alongside the existing
  `D-FER-03=65`, explicitly not overwriting it. **Gated on T1(ii)+(iii).**
  Needs user authorization: NO (docs-only, once T1 clears); does not by
  itself freeze the R2 contract (T4/T5/T6 of that change still apply).
  **Done 2026-09-28**: `tasks.md` blocker table + 2026-09-28 update note;
  `design.md` C10/C11 note; `R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`
  C9/C10/C11/C12 pointer notes + §5 ledger rows (D-FER-03 n=65 retained,
  annotated superseded by n=56; D-ACQ-02/03/05 → `DECIDED`);
  `R2_T4_PI_DECISION_CARDS_20260927.md` 卡 1-3 append "已裁决". R2 contract
  itself remains **NOT frozen** (D-FER-04..07, D-ACQ-01/04/06(already
  decided)/07/08 status unchanged except as noted; T3 freeze verdict still
  outstanding).

- [x] T6 — Clarify `workspace/acq_inventory_20260928/participation_ledger.
  json`'s `eval_blocks_per_session_formula` key naming (`design.md` D9) —
  rename or annotate to make clear it counts *additional* post-4190 blocks,
  not the existing 14-block EVAL segment. **Gated on T1(v); skip if T1(v)
  rules this a non-issue.** Needs user authorization: NO (comment/rename
  only; no numeric value changes).
  **Done 2026-09-28**: renamed to `extra_eval_blocks_beyond_existing_14_
  formula` with an added `note` field explaining the semantics; numeric
  values unchanged; JSON validity checked. `workspace/acq_inventory_20260928/`
  (previously untracked, gitignored under `workspace/*`) committed with
  `git add -f` for the first time, per the task packet.

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

**2026-09-28 update**: T1 is ruled (`DECIDED`, PI "按建议批准，继续推进").
T2-T6 are complete (see each task's "Done 2026-09-28" note above) and their
writes to `STATE.md`, `AGENTS.md`, `docs/nbpolar/DATA_LEDGER.md`, the R2
contract documents, and `workspace/acq_inventory_20260928/
participation_ledger.json` are now in effect. T7 remains **NOT AUTHORIZED**
by this change.
