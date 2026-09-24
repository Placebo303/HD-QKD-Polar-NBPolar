# Change Proposal: nbpolar-r2-fer-measurement-contract

Status: **draft (docs-only, no execution)**
Date opened: 2026-09-23
Owner: planner-free (docs-only skeleton), PI adjudication reserved
Related active change: `formal-ir-nbpolar-mvp` (M2 = `VALIDATED_AT_FROZEN_CONTRACT`, 2nd rung of the roadmap promotion ladder)

---

## Problem

The NB-Polar M2-prior G4 inventory was adjudicated **PASS** and the M2 state was
promoted to `VALIDATED_AT_FROZEN_CONTRACT` (decision-log `docs/decision-log.md`
entry of **2026-09-23**, "NB-Polar M2-prior G4 inventory COMPLETE"). The next
rung of `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` is **R2: freeze a
preregistered FER measurement contract** before any real-data acquisition or
decode work is planned.

Two R0.2 deliverable drafts exist and have not been reconciled:

- `docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md` (D-FER-01..07 open)
- `docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md` (D-ACQ-01..08 open)

They are non-overlapping in intent but are **two documents, not one contract**.
Until they are merged into a single preregistered contract with the PI's open
decisions adjudicated, we cannot compute a defensible sample size/quota, cannot
build a Tier-Y packet, and cannot claim any FER number. M2 is deliberately
parked at the 2nd rung for this reason.

## Why

- **Reproducibility and non-self-granting acceptance**: a FER number produced
  without a frozen, preregistered definition and sample size is not a claim we
  can defend or archive. Freezing first is the cheapest point to fix semantics.
- **The ladder requires it**: roadmap R2 gate is "measurement contract frozen";
  R3 (efficiency) and any Stage-3 work sit strictly behind it.
- **Single contract beats two drafts**: merging removes the risk of the two
  drafts drifting apart (e.g., frame unit, `undetected` handling, budget
  accounting being specified twice with different wording).

## Scope — IN

1. **C1–C14 contract merge** — reconcile the two drafts into one preregistered
   measurement contract document. The C1–C14 clause list is enumerated in
   `design.md` D1/D4 and instantiated by task T2.
2. **G4 sync, already-done citation** — record/cite the already-completed G4
   sync as evidence (decision-log 2026-09-23 entry). This is a citation task,
   not new adjudication (task T1).
3. **Quota derived from the PI's discriminable difference** — after the PI
   states the minimum discriminable difference, derive the frame/pair quota by
   arithmetic from the frozen CI convention (task T5). No threshold is invented
   by the planner.
4. **Tier-Y packet skeleton with `authorizations: []`** — an empty, non-executable
   packet skeleton only (task T6). It carries no authorization token.

## Scope — OUT (explicit non-goals)

- **Any acquisition, decode, or efficiency measurement run** (real or synthetic).
- **Any Tier-X or Tier-Y authorization** — this change grants none; no verbatim
  authorization text is produced or implied.
- **Any R3 (efficiency) or Stage-3 work**, and any FER/efficiency/secret-key
  **claim or published number**.
- Any change to the frozen original Polar pipeline (`src/`, `experiments/`,
  `tools/`), the `comparison_bench/` wrapper semantics, G4 adjudication results,
  the archive, `results/`, or `comparison_bench/outputs_comparison/`.
- Any modification of `docs/nbpolar/STATE.md` rung/ladder state (M2 stays at the
  2nd rung; only this contract's own artifacts change).
- CI-methodology changes beyond documenting the already-drafted Wilson default
  pending PI adjudication of D-FER-01.

## Affected specs

- **Merged specs under `openspec/specs/` (they DO exist; READ-ONLY; no delta
  added by this change)**: `final-ir-method-selection`, `formal-ir-methods`,
  `nbpolar-prior-rebaseline`. Inherited unchanged as binding constraints:
  `openspec/specs/nbpolar-prior-rebaseline/spec.md` §validation gates
  (:61–70 — no FER/efficiency/qualification claim SHALL precede G1 + G2 + G3 +
  G4 + the Stage-3 measurement set; S9 SHALL never be cited as FER/efficiency
  evidence) and §decoder and verification boundary (:53–59 — the 64-bit
  Toeplitz tag, disclosure counting, and `undetected` isolation SHALL remain
  unchanged). This change adds **no** delta spec to any merged spec.
- **Affected inputs (read-only, cited not modified)**: `openspec/project.md`
  context conventions, the two 2026-09-22 drafts, the roadmap
  `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md`, and the G4 evidence.
- **New artifacts this change creates** (all under
  `openspec/changes/nbpolar-r2-fer-measurement-contract/` plus one merged
  contract document under `docs/nbpolar/`): `proposal.md`, `design.md`,
  `tasks.md`, and the merged `MEASUREMENT_CONTRACT` document from T2.

## Source of truth for this change

`docs/decision-log.md` (2026-09-23 G4 entry) > the two 2026-09-22 drafts >
roadmap R2 gate definition. If drafts and contract disagree after T2, the
merged contract wins and the discrepancy is reported, not silently resolved.

## PI rulings (planning input only — pending PI, non-authorizing)

No execution is authorized by this section; no threshold is frozen; frozen
numbers are unchanged (Δ=0.10, R-a, w=0.10, p=3/14, z=1.96, n=65,
K1=319/K2=6492). Planner does not self-adjudicate; T4 adjudication is reserved
to the PI.

### PI-RULING-ROUTE — single-method FER route

R2 stays a single-method FER contract (operational arm only). Paired-method
comparison (ΔFER/McNemar, H2-class claims), efficiency/net-key (C6/C7 Stage-3),
Branch-B scale, and f-target reset stay out of R2 and move only via a separate
PI decision. This section grants no authorization and changes no state string.

### PI-RULING-NONFREEZE — placeholders are not frozen numbers

T5/T6 placeholders, budget envelopes, and candidate Δ/w/n values remain
planning inputs until T4 marks them `DECIDED`. T5/T6 SHALL NOT write a
placeholder as a frozen number and SHALL NOT start acquisition or decode early.
The binding gate order is T4 (see `tasks.md:57`) → T5 → T6 skeleton.

### PI-RULING-HLABEL — project-level H vs probe-local L-H

Project-level hypotheses (H1/H2/H3 in future planning) SHALL NOT be mixed with
probe-local labels (L-H1/L-H2/L-H3). Tier-X probe conclusion sentences stay
descriptive and non-verdict; historical `results.json` values are unchanged and
only future conclusion-sentence prefixes use L-H.
