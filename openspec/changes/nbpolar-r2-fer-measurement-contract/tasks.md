# Tasks — nbpolar-r2-fer-measurement-contract

Status: **EXECUTED + ADJUDICATED 2026-09-29** (`r2-fer-shg-64`, main-thread
verdict `FER_MEASURED_AT_CONTRACT`; see `docs/decision-log.md` 2026-09-29
entry and T7/T8/T9 sections below). PENDING-BUDGET (SCL wall) was resolved by
the PI's separate `r2-fer-shg-64` authorization
(`workspace/r2_fer_shg_64/STATUS.yaml` `pi_authorization_2026_09_28`), not by
a change to this file's own frozen D-ACQ-06 row (kept as historical record
below). Prior status line retained below for provenance.

Status (2026-09-28, superseded above): **FROZEN except PENDING-BUDGET (SCL wall)** (2026-09-28, second-round
T4 PI adjudication "按建议批准" + P-1/P-2 + T3/T5/T6; see
`docs/decision-log.md` 2026-09-28 "R2 剩余 8 项待决全部 DECIDED..." entry).
All 15 `§5` ledger rows in `docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`
are now `DECIDED`; T3 structural freeze re-check PASS (see T3 section below);
T5 quota arithmetic complete (16+20+28=64, margin 8); T6 packet skeleton
written with `authorizations: []` (see `T6_PACKET_SKELETON_20260928.md`).
**One open gap**: D-ACQ-06's budget numbers (`wall_per_block=40s`) were
adjudicated under an **SC** cost model; R2's candidate execution path is
**SCL(L=16, top_m=4, CRC-16)**, whose measured per-block cost is on the order
of ~600s — incompatible with the frozen SC-derived number. This is flagged
`PENDING-BUDGET`, not self-adjudicated (see T4 2026-09-28 round-2 update
below). Until the PI supplies an SCL-specific budget ruling, **T7/T8/T9
remain NOT AUTHORIZED** — unchanged by this update; nothing here grants
execution. Ordered T1→T9. T1–T6 are documentation tasks. T7–T9 are recorded
here only to fix their boundary and are **NOT AUTHORIZED** by this change.

---

## T1 — G4 sync citation (already done)

Cite the completed G4 sync as provenance in the merged contract header:
decision-log `docs/decision-log.md`, **2026-09-23** entry "NB-Polar M2-prior
G4 inventory COMPLETE". No G4 re-inventory, no adjudication, no artifact edit.

- Evidence: decision-log entry exists; M2 = `VALIDATED_AT_FROZEN_CONTRACT`.
- Needs user authorization: **NO** (citation of an already-done item).

## T2 — Merge the two drafts into the single contract

Produce the merged preregistered measurement contract implementing D1:
normative body from `FER_DEFINITION_DRAFT_20260922.md`, acquisition draft
demoted to Annex A, clauses C1–C14 instantiated, disjointness matrix filled,
decision ledger table created with every D-FER-01..07 and D-ACQ-01..08 row in
an explicit state per D3 (initially `PENDING`), R-2 string guard verified
(absence of "11/14" / "FER ≈ 0.21" as a claim).

- Needs user authorization: **NO** (docs-only merge).

## T3 — Freeze review of the merged contract

Independent read-only review that: all C1–C14 clauses are present exactly once;
the clause-provenance disjointness matrix shows no conflicting overlap; every
ledger row has an explicit D3 state; no acquisition/decode/run content leaked
in; D6 Stage-3 isolation holds; **draft-red-line → C-ID mapping is total**:
every red line / caveat / hard rule of both drafts maps to exactly one C1–C14
clause — R-1…R-5, FER §6 `undetected` reporting, FER §8 comparability +
abstract/summary ban before `FER_MEASURED_AT_CONTRACT`, Carried caveats
(a)–(d), ACQ §2 derivation, ACQ §4 reservation partition with
COMPLETE-BLOCKS-ONLY ⇒ INSUFFICIENT, ACQ §5 work-point declaration, ACQ §7
raw-file rules, ACQ §9 ledger no-reflow — with **no red line left unmapped**
and none double-specified. FAIL → return to T2.

- **Pass standard (R2-T2-FIX)**: while every ledger row is still `PENDING`,
  T3's PASS is a **structural PASS only** — T3 does not judge freeze-pass; the
  freeze verdict is made after T4 adjudicates (design D3). The T2→T3→T4 order
  is unchanged; a conflicting reading (unadjudicated rows blocking T3 itself,
  i.e. T4→T3) is escalated to the main thread, not silently re-ordered.
- **Escalation, not auto-FAIL**: a listed red line whose definition cannot be
  located anywhere in the repository (currently R-5 → contract §0 P9) is
  reported for PI removal-or-definition; it is not auto-FAILed as a T2 mapping
  gap that T2 alone cannot fix.
- T3 writes nothing: FAIL returns the document to T2; placement/归位 writes
  stay with T2 (doc revision) and PI (T4 adjudication).

- Needs user authorization: **NO** (read-only review).

## T4 — PI adjudicates D-FER / D-ACQ and locks w and n

PI adjudicates the ledger to `DECIDED` / `DEFERRED` / `NOT_APPLICABLE`:

- **D-FER-01..07**: CI method (Wilson z=1.96 vs exact), target half-width **w**,
  sample size **n**, H(X\|Y) substitution, f_FER accounting, `undetected>0`
  escalation, per-frame derivative reading.
- **D-ACQ-01..08**: branch A/A′/B, source list, reserve quotas, Type0
  inclusion, noise band, budget numbers, contract inheritance, ≥2 sessions.
- **Plus**: the minimum discriminable difference (drives D2), and the
  K_total fixed-f vs fixed-K convention.

Only `DECIDED` rows are frozen into the contract body (D3). Blocking gate for T5.

- Needs PI adjudication for the remaining PENDING rows; the partial 2026-09-24
  record does not complete T4. This does not authorize acquisition or execution.

### T4 current status (partial PI adjudication; as of 2026-09-24)

The PI recorded a partial T4 adjudication in `docs/decision-log.md` (2026-09-24
R2 T4 PI adjudication). D-FER-01..03 are explicitly decided and transcribed in
the contract ledger. The same entry identifies four remaining inputs that block
T5/T6: D-ACQ-02/03/05/06. Other rows without an explicit row-level disposition
remain `PENDING`; do not infer their states from the aggregate decision text.
The current K_total remains at G2/G3 (K1=319/K2=6492); this does not freeze a
future rate change. Only `DECIDED` rows enter the frozen body at T4 (see
`tasks.md:57` for the T4 gate).

| Explicit T5/T6 blocker | Question | Owner | State | Retrigger |
|---|---|---|---|---|
| D-ACQ-02 Source list | Which new acquisition sources may supply confirmation blocks | PI / lab contact | **DECIDED 2026-09-28**: SHG `_1`/`_2`, full sessions — see `docs/nbpolar/DATA_LEDGER.md` §7 and `docs/decision-log.md` 2026-09-28 "数据使用规则修订 R1-R5 采纳" entry | closed — no further new-source ledger required for the 64-block candidate pool |
| D-ACQ-03 Partition quotas | Per-acquisition CAL / CHAR / HELDOUT / EVAL / RESERVE quotas under C11 | PI / lab contact | **DECIDED 2026-09-28**: per session (32 blocks) — frames 0-1023 → 8 blocks (`A1_CAL_characterization` stratum); 1056-2397 → 10 blocks, 62-frame remainder unused (`HELDOUT_model_selection` stratum); 2398-4189 → 14 blocks (`EVAL_already_decoded` stratum); CAL32 stays 1024-1055 (32f, excluded). 64 blocks total across both sessions. See `docs/nbpolar/DATA_LEDGER.md` §7. | closed — quota arithmetic (T5) may now proceed on this input |
| D-ACQ-05 Comparability | Baseline and work-point tolerance/conditions | PI / lab contact | **DECIDED 2026-09-28**: scope narrowed to "applies only to the two 2026-01-13 SHG acquisitions' own conditions" (config verified identical, `workspace/acq_inventory_20260928/REPORT.md:26-68`); HELDOUT (1838-2397) and the already-decoded EVAL (2398-4189) are reported in separate strata, not merged. General new-source comparability stays open for any future acquisition. | closed for this candidate pool — see `docs/decision-log.md` 2026-09-28 entry |
| D-ACQ-06 Budget | Per-block and total wall/RSS limits and machine/parallelism constraints | PI / lab/operations | **DECIDED 2026-09-27**: `O-6a ; wall_per_block = 40 s ; rss_per_block = 2 GiB ; wall_total = 5400 s ; machine_spec/parallelism = single-process exclusive on this machine ; stop_on_overbudget = STOP, no tuning` | closed — see `docs/decision-log.md` 2026-09-27 entry |

PI-ready decision cards for the four blockers above (options, consequences, required external fields with units, non-adjudication consequences, owner; **no recommended values and no row state changed**) were prepared on 2026-09-27 at `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md`. Rows remain `PENDING` until the PI adjudicates them.

**2026-09-27 update**: D-ACQ-06 is now `DECIDED` (basis: G3 measured
19.38–20.13 s/block, RSS 1.13 GiB,
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md:45`; full
value and provenance in `docs/decision-log.md` 2026-09-27 "PI 裁决三项" entry
and `R2_T4_PI_DECISION_CARDS_20260927.md` 卡 4 "已裁决" line). D-ACQ-02,
D-ACQ-03, and D-ACQ-05 remain `PENDING`; T5/T6 stay blocked by
GATE-T5/GATE-T6 (`tasks.md:57`) until those three are also decided. This
does not freeze the R2 contract.

**2026-09-28 update**: D-ACQ-02, D-ACQ-03, and D-ACQ-05 are now `DECIDED`
via `openspec/changes/nbpolar-data-use-rules-revision` T1 (PI, "按建议批准，
继续推进") — values transcribed in the blocker table above and in
`docs/nbpolar/DATA_LEDGER.md` §7. All four explicit T5/T6 blockers
(D-ACQ-02/03/05/06) are now `DECIDED`; T5 quota arithmetic may proceed.
This still does not by itself freeze the R2 contract — D-FER-04..07 and
D-ACQ-01/04/07/08 remain `PENDING` (see below) and T3's freeze verdict is
still outstanding. **D-FER-03 note**: the frozen `n=65` value (basis `p=3/14`)
is superseded by a 2026-09-28 re-adjudication to `n=56`, derived from the
Wilson-upper bound `p≈0.1771` on the SCL(L=16) 27/28 real-data result
(`docs/decision-log.md` 2026-09-28 entries "真实数据 G2/G3 B 臂 28 块
SCL(L=16) 描述性合并" and "数据使用规则修订 R1-R5 采纳"); the original `n=65`
and its `p=3/14` derivation are retained below, annotated as superseded, not
deleted.

D-ACQ-04 (Type0) and D-ACQ-08 (session count), as well as D-FER-04..07 and
D-ACQ-01/07, remain `PENDING` because the T4 decision-log entry gives no
row-specific state for them. The session and Type0 questions cross-reference
the four open-input items; this note does not add separate PI decisions.

**2026-09-28 update (round 2 — T4 COMPLETE)**: the PI adjudicated the
remaining 8 rows (D-ACQ-01/04/07/08, D-FER-04/05/06/07) in conversation,
approving the recommended values in
`docs/nbpolar/R2_REMAINING_DECISIONS_20260928.md` verbatim ("按建议批准").
All 15 `§5` ledger rows are now `DECIDED` — see
`docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md` §5 for the
transcribed values and `docs/decision-log.md` 2026-09-28 "R2 剩余 8 项待决全部
DECIDED..." entry for full provenance. Summary:

| ID | Value |
|---|---|
| D-ACQ-01 | O-1a: Branch A, 64-block pool, n=56, w=0.10 |
| D-ACQ-04 | O-4a: Type0 not included |
| D-ACQ-07 | O-7b: construction contract (W_P/W_S/MOD/skip/K1/K2/P16) inherited unchanged from G2/G3; **tag_master newly minted, single, shared across both sessions**: `eval_seed=2026092801` → `tag_master=2026102801` (per the established `tag_master = eval_seed + 10000` convention) |
| D-ACQ-08 | O-8a: the two SHG sessions (`_1`/`_2`) satisfy the ≥2-session roadmap gate; no additional session needed |
| D-FER-04 | O-4a: each session fits its own `H_total` from its own CAL32 triple — G2 (SHG `_1`) `H_total=0.8168138`; G3 (SHG `_2`) `H_total=0.8214782076249098` |
| D-FER-05 | O-5a: adopt the existing `f_book_with_crc` accounting formula (CRC-16 + tag + K-coordinate disclosure, per-session `H_total`), with an explicit statement of its structural difference from Müller eq(11) (this protocol's K-coordinate disclosure is unconditional pre-decode, so `kdb_with_crc` is a per-block constant regardless of outcome — no Müller-style outcome-weighting is needed) |
| D-FER-06 | O-6a: `undetected ≥ 1` ⇒ isolate the block, loud STOP statement, **defer** the `FER_MEASURED_AT_CONTRACT` verdict, escalate to PI |
| D-FER-07 | O-7a: no per-acquisition-frame derived readings reported this round |

**Two additional PI rulings beyond the per-row list** (given in the same
conversation, resolving ambiguity the per-row recommendations did not
themselves adjudicate):

- **P-1** (resolves the D-ACQ-05 "must not merge into a single unstratified
  FER number" ambiguity): a **pooled 64-block FER number is permitted**, but
  the **same table must show the three strata side by side**
  (`A1_CAL_characterization` / `HELDOUT_model_selection` /
  `EVAL_already_decoded`) — never a pooled number alone. The `n=56`
  DECIDED-threshold check uses the **pooled** denominator (D2 step, T5 below).
- **P-2**: if D-FER-06's `undetected ≥ 1` STOP fires, that execution still
  **counts as the one-shot Tier-Y attempt** — it must not be discarded and
  rerun to obtain a "clean" (`undetected=0`) result. Whether to proceed to a
  verdict after PI review, or whether any further measurement is needed, is a
  **separate PI decision**, not something T4/T5/T6 or an execution agent may
  decide unilaterally.

This closes T4 for all 15 ledger rows. See T3/T5/T6 sections below for what
this unblocks.

### T3 — freeze structural re-check (2026-09-28, all rows DECIDED)

With every `§5` ledger row now `DECIDED` (no `PENDING`/`DEFERRED` remaining),
T3's freeze-pass verdict (deferred under R2-T2-FIX pending T4, see T3 task
description below) is now judged:

- C1–C14 clauses present exactly once, disjointness matrix (contract §4) no
  conflicting overlap, R-2 string guard (contract §6), D6 Stage-3 isolation,
  and the draft-red-line → C-ID total mapping (contract §7) — all carried
  forward unchanged from the 2026-09-24 STRUCT-PASS (`docs/decision-log.md`
  2026-09-24 "R2 measurement-contract T3 structural review STRUCT-PASS"
  entry); no new clause conflict was introduced by transcribing the 8 newly
  `DECIDED` values, since each value fills a slot the merged contract already
  reserved for it (§5 rows existed for all 15 IDs since T2).
- **Verdict: structural freeze PASS.** However, the freeze is **not a plain
  `FROZEN`**: D-ACQ-06's budget figures were derived from **SC** timing
  (G3 measured ~19–20 s/block), while R2's candidate decode path is
  **SCL(L=16, top_m=4, CRC-16)**, whose measured per-block cost
  (`workspace/scl-gate-t3-packet/`, `workspace/m2_scl_rescue_g2g3/` timing) is
  on the order of ~600 s/block — roughly 15× the frozen `wall_per_block=40s`.
  This mismatch was not covered by any of the 8 rows just decided and is
  **not self-adjudicated here**. Overall change status is therefore
  **`FROZEN except PENDING-BUDGET (SCL wall)`** (see status line at the top
  of this file). See `T6_PACKET_SKELETON_20260928.md` for the flagged
  suggested values (not frozen).

### T5 — quota arithmetic (2026-09-28)

Applying D2 (difference → w → n → quota) with all inputs now `DECIDED`:

- Source: `docs/nbpolar/DATA_LEDGER.md` §7. Per session: `A1_CAL_characterization`
  8 blocks + `HELDOUT_model_selection` 10 blocks + `EVAL_already_decoded` 14
  blocks = 32 blocks/session.
- Two sessions: `16 + 20 + 28 = 64` blocks total (matches
  `DATA_LEDGER.md:50,70-71,75` "32+32=64" verbatim).
- Against `D-FER-03`'s `n=56`: margin = `64 − 56 = 8` blocks (~12.5%).
- **Threshold reading (per P-1)**: the `n=56` check applies to the **pooled**
  denominator across all three strata (`64 ≥ 56` ⇒ meets threshold). Read
  per-stratum instead, no single stratum reaches 56 (largest is EVAL at 28);
  P-1 explicitly resolves this by mandating the pooled reading for the
  threshold check while still requiring the per-stratum table alongside it.
- No new acquisition is needed (`DATA_LEDGER.md` §7 gap = 0); budget
  constraint check deferred to `PENDING-BUDGET` above (D-ACQ-06 SCL mismatch)
  — T5's arithmetic itself does not depend on the wall-time budget number.

### T6 — Tier-Y packet skeleton (2026-09-28)

Written to `T6_PACKET_SKELETON_20260928.md` in this directory (frozen fields:
execution config, 64-block list, new tag_master/eval_seed, judgment rule,
mandatory report contents; `authorizations: []`, no `AUTHORIZATION_PROMPT.md`
generated — per this task's "deferred by construction" clause below and
proposal Scope OUT). The SCL wall-time budget is recorded there as a flagged
**suggestion**, not a frozen value, pending the PI's supplemental D-ACQ-06
ruling for the SCL path.

### GATE-T5 — quota arithmetic gate

T5 runs only after T4 (see `tasks.md:57`) completes. T5 SHALL NOT write a
placeholder as a frozen number and SHALL NOT start acquisition or decode; it
records difference → w → n → quota arithmetic on T4-decided inputs only.

### GATE-T6 — packet skeleton gate

T6 runs only after T4 and T5 complete. The skeleton keeps
`authorizations: []`; T6 SHALL NOT write a placeholder as a frozen number and
SHALL NOT produce `AUTHORIZATION_PROMPT.md` or any verbatim authorization text.

### BOUNDARY-T7T8 — acquisition/decode boundary

T7 (acquisition) and T8 (decode/measurement) remain **NOT AUTHORIZED** by this
change. No early acquisition, read, or decode is approved here; T9 publishes no
number. Boundary recorded here only to prevent T5/T6 from implying execution.

## T5 — Quota frame arithmetic

Apply D2 in the frozen direction: difference → w → n → **quota**. Compute
frames and pairs from n under the frozen CI convention; check against the C13
budget (D5). Report any difference-vs-budget conflict to the PI instead of
trading it off. Record arithmetic explicitly (units, formulas).

- Needs user authorization: **NO** (arithmetic on PI-decided inputs; blocked until T4).

## T6 — Tier-Y packet skeleton (`authorizations: []`)

Create the packet skeleton with frozen fields (inputs, thresholds, command,
budget, stop rules) and **`authorizations: []`** — empty, hence non-executable.
The skeleton contains no verbatim authorization text and grants nothing.

- **Gate order (fixed)**: T6 runs **only after T4 (PI adjudication) and T5
  (quota arithmetic) are complete**. Every frozen field is written from the
  T4-decided ledger and the T5 arithmetic; **no frozen field may be written
  before T4/T5 complete**, and no threshold/budget number may be invented to
  fill a slot.
- **Deferred by construction**: no `AUTHORIZATION_PROMPT.md` and no verbatim
  authorization text are produced by this change — that artifact is generated
  only later, after an explicit user instruction, and **must not be generated
  now** (Scope OUT: no authorization is granted or implied).

- Needs user authorization: **NO** (skeleton only; empty authorization list by construction).

## T7 — Acquisition run

~~**NOT AUTHORIZED** by this change. Out of scope (see Scope OUT). Recorded only
to fix the boundary: no acquisition command, source, or schedule is approved
here.~~

**[x] 2026-09-29 update — satisfied by substitution, not a new acquisition**:
per the 2026-09-28 PI adjudication (D-ACQ-02/03/08, `docs/decision-log.md`
2026-09-28 "数据使用规则修订 R1-R5 采纳" entry), no new acquisition run was
needed or performed. T7 is closed by **substituting the existing frozen SHG
`_1`/`_2` 64-block pool** (`docs/nbpolar/DATA_LEDGER.md` §7) for a fresh
acquisition — the ledger already showed the gap at 0 (`n=56` target met by
the existing 64 blocks). No raw-data read outside the already-inventoried
sessions occurred.

- Needs user authorization: **NOT AUTHORIZED for a *new* acquisition** (none
  was requested or performed; N/A by substitution).

## T8 — Decode / measurement execution

~~**NOT AUTHORIZED** by this change. No decode, no FER measurement, no real-data
or synthetic execution is approved here.~~

**[x] 2026-09-29 update — executed under separate PI authorization**: the
decode/measurement execution ran as `workspace/r2_fer_shg_64/` under the PI's
explicit verbatim authorization recorded in
`workspace/r2_fer_shg_64/STATUS.yaml` `pi_authorization_2026_09_28` (not this
change's own text) plus independent Pre-EXECUTE round-2 PASS
(`workspace/r2_fer_shg_64/PRE_EXECUTE_REVIEW_R2.md`). Exit code 0, 64/64
blocks `status=="ok"`, `reruns=0`, one-shot. This T8 checkbox records that
the boundary this task fixed has now been crossed **by explicit separate
authorization**, not that this change itself authorized it.

- Needs user authorization: satisfied by the separate PI verbatim
  authorization above (not by this change's text).

## T9 — Pre-RESULT review / publication of any number

~~**NOT AUTHORIZED** by this change. No FER value, OPERATOR_RETURN, or
RESULT_SUMMARY may be produced from this change's work.~~

**[x] 2026-09-29 update — Pre-RESULT PASS + result published**: independent
Pre-RESULT review PASS (`workspace/r2_fer_shg_64/PRE_RESULT_REVIEW.md`,
findings F1–F9, zero discrepancies). Main-thread adjudication:
**`FER_MEASURED_AT_CONTRACT`** (see `docs/decision-log.md` 2026-09-29 entry).
Result published at `workspace/r2_fer_shg_64/RESULT_SUMMARY.md` (pooled +
stratified tables side by side per P-1, selection-freedom table, undetected/
resource_abort explicit 0, f/H side by side, applicable-scope statement,
caveats (a)–(e), one permitted conclusion sentence). This T9 checkbox
records that the boundary this task fixed has now been crossed **by the
separate main-thread Pre-RESULT/adjudication act above**, not that this
change's own text authorized publication.

- Needs user authorization: satisfied by the separate PI authorization +
  independent Pre-RESULT PASS + main-thread adjudication above (not by this
  change's text).

---

## Standing unauthorized items (O-list)

Always out of scope for this change unless a later change explicitly grants
them with verbatim authorization:

- O1 Tier-X / Tier-Y execution of any kind (including "just a smoke run").
- O2 Writes to `results/`, `comparison_bench/outputs_comparison/`, the archive,
   G4 adjudication artifacts, frozen baseline (`src/`, `experiments/`, `tools/`),
   and `docs/nbpolar/STATE.md` rung/ladder state.
- O3 Publication of any FER, efficiency, or secret-key number.
- O4 Git push, branch force-update, or change archival.
