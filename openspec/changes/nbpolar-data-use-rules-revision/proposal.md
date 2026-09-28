# Change Proposal: nbpolar-data-use-rules-revision

Status: ~~draft — PENDING PI adjudication~~ **APPROVED by PI 2026-09-28 (T1 DECIDED)**
Date opened: 2026-09-28
Owner: planner (docs-only; no production code; AGENTS.md §4)
PI authorization to draft: PI in-chat, 2026-09-28, "同意开始"
PI adjudication: 2026-09-28, "按建议批准，继续推进" — T1(i)-(v) all ruled; see `tasks.md`
T1 for the recorded values and `docs/decision-log.md` 2026-09-28 for the full entry.

## Problem

Five verified findings suggest the project's data-reuse rules are stricter
than their own stated reasons require, and one sizing input is stale.

**1. Security accounting already covers K-coordinates, tag and CRC.**
`key_dependent_bits` includes the disclosed-coordinate term and `TAG_BITS`
(`comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py:764`,
`:711`, `DISCLOSED_BITS_PER_COORDINATE` `:167`), flows into `leak`
(`comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py:182`)
and `IRRunResult.leak_EC_actual_bits` (`:228`), which feeds `beta_eff_formula`
(`:202`). CAL32 is excluded from the key denominator as a sacrifice
(`docs/SECURITY_MODEL.md:107-129`). **No file bars reusing already-decoded
data on leakage grounds** — leakage is booked per disclosure event, not per
data-freshness. `docs/nbpolar/STATE.md:79`'s "`SECURITY_MODEL` has NO
CAL/prior term at all" is stale: §107-129 is exactly that accounting note.

**2. The "never reflow" rule's stated reasons are non-leakage.**
`docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md:74-80` (§9, "decoder-touched
frames NEVER reflow") cites no leakage mechanism — its own text frames this
as audit/independence ("G3 的 independence 系 decoder/model independence, 非
no-prior-contact"). `REAL_DATA_FEASIBILITY_STRATEGY.md:113-123` (SCL entry
gate) grounds its five conditions in statistical-selection/evidence-reuse
concerns, also not disclosure. This proposal reads the underlying concern as
(B) statistical selection bias and (C) audit/independence, and flags
"contamination" as label drift from those, not a third security reason.

**3. Segmentation is far EVAL-poorer than the binary baseline, never frozen
as necessarily mutually exclusive.** Binary Polar (N=16384) uses a two-way
train/held-out split on one slice (`D:\Code\HD-QKD_Polar_Release\docs\
POLAR_VS_LDPC_CROSS_REPO_COMPARISON_20260927.md:55` — 812,620 pairs, test
24×16384 symbols; `:91` — `--pool-oos`). *The "~65 blocks/session" figure
could not be reconstructed from lines 55/91/236 — flagged UNVERIFIED, see
`design.md` D3; the qualitative two-way-split point stands.* NB-Polar's own
frozen five-segment cut (`workspace/acq_inventory_20260928/REPORT.md:
141-158`) yields 14 EVAL blocks/session, and its mutual exclusivity is the
current draft's *unadjudicated* choice: `D-ACQ-03` is `PENDING`
(`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:175-186`).

**4. "Exhausted" conflates two non-overlapping batches.** `STATE.md:81,90`
describes the *old* P-series ladder as exhausted (101 frames, 69 after
CAL32). Unrelated to SHG 2026-01-13's own untouched RESERVE (29/99 frames,
`workspace/acq_inventory_20260928/REPORT.md:150,172-173`).
`FUTURE_DIRECTION_PLAN_20260924.md:36-37` already states "数据耗尽是人为造成的"
(each SHG acquisition yields ~33 blocks; throughput, not physics) — never
reconciled against STATE.md's exhaustion language.

**5. Frozen `n=65` was sized on a superseded point estimate.**
`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:135-146` derives `n=65` from
`p=3/14≈0.214` (G2 B-arm, SC-only, pre-SCL). Current point estimate at the
SCL-rescued frozen candidate is **1/28** (`docs/decision-log.md` 2026-09-28
"27/28...G2 block 5 verify_failed" entry). Not recomputed since.
`decision-log.md:84` forbids back-deriving quotas from `n` — not re-deriving
`n` from an updated `p`; both directions computed in `design.md` D6.

## Why

Freezing rules first is cheap; re-litigating after acquisition is expensive.
All five findings point one direction: reuse of already-decoded data is
barred more broadly than its stated rationale supports, while the real
constraint is an unreviewed segmentation choice, not physical scarcity.

## Scope — IN / OUT

IN: this proposal + `design.md` + `tasks.md`; citation-only diagnosis (1-5);
five candidate rules R1-R5 for PI adjudication; an R2 contract amendment
*proposal* (not a frozen edit) covering source/config/D-ACQ-02/03/05; two
n-recomputation results as PI-adjudicable inputs, not frozen values.
OUT: any code change; any Tier-X/Tier-Y execution; any edit to `STATE.md`,
`AGENTS.md`, the R2 contract, or `docs/nbpolar/DATA_LEDGER.md` itself
(`tasks.md` T2-T6 describe, not perform, those edits, gated on T1); any
real-data decode; any FER/efficiency claim.

## Affected specs / inputs (read-only citations, nothing modified)

`comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`,
`comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py`,
`docs/SECURITY_MODEL.md`, `docs/nbpolar/STATE.md`, `docs/nbpolar/
ACQUISITION_SPEC_DRAFT_20260922.md`, `docs/nbpolar/REAL_DATA_FEASIBILITY_
STRATEGY.md`, `docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`,
`docs/nbpolar/FUTURE_DIRECTION_PLAN_20260924.md`, `docs/decision-log.md`,
`workspace/acq_inventory_20260928/{REPORT.md,participation_ledger.json}`,
`openspec/changes/nbpolar-r2-fer-measurement-contract/`,
`openspec/changes/nbpolar-scl-lock-amendment/`.

## PI rulings needed (planning input only; no self-adjudication)

See `tasks.md` T1 for the itemized list with options.
