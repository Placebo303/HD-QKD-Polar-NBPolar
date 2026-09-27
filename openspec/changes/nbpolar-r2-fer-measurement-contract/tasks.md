# Tasks — nbpolar-r2-fer-measurement-contract

Status: **draft (docs-only).** Ordered T1→T9. T1–T6 are documentation tasks.
T7–T9 are recorded here only to fix their boundary and are **NOT AUTHORIZED**
by this change.

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
| D-ACQ-02 Source list | Which new acquisition sources may supply confirmation blocks | PI / lab contact | PENDING | retrigger=parsed new-source ledger arrival; no source is consumed before T4 |
| D-ACQ-03 Partition quotas | Per-acquisition CAL / CHAR / HELDOUT / EVAL / RESERVE quotas under C11 | PI / lab contact | PENDING | retrigger=T5 quota arithmetic; quotas and acquisition capacity must be fixed before T5 |
| D-ACQ-05 Comparability | Baseline and work-point tolerance/conditions | PI / lab contact | PENDING | retrigger=paired-design item; R2 remains single-method; work-point inputs required |
| D-ACQ-06 Budget | Per-block and total wall/RSS limits and machine/parallelism constraints | PI / lab/operations | PENDING | retrigger=S4 quota-vs-budget reconciliation; conflict is escalated, never traded off |

PI-ready decision cards for the four blockers above (options, consequences, required external fields with units, non-adjudication consequences, owner; **no recommended values and no row state changed**) were prepared on 2026-09-27 at `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md`. Rows remain `PENDING` until the PI adjudicates them.

D-ACQ-04 (Type0) and D-ACQ-08 (session count), as well as D-FER-04..07 and
D-ACQ-01/07, remain `PENDING` because the T4 decision-log entry gives no
row-specific state for them. The session and Type0 questions cross-reference
the four open-input items; this note does not add separate PI decisions.

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

**NOT AUTHORIZED** by this change. Out of scope (see Scope OUT). Recorded only
to fix the boundary: no acquisition command, source, or schedule is approved
here.

- Needs user authorization: **NOT AUTHORIZED**.

## T8 — Decode / measurement execution

**NOT AUTHORIZED** by this change. No decode, no FER measurement, no real-data
or synthetic execution is approved here.

- Needs user authorization: **NOT AUTHORIZED**.

## T9 — Pre-RESULT review / publication of any number

**NOT AUTHORIZED** by this change. No FER value, OPERATOR_RETURN, or
RESULT_SUMMARY may be produced from this change's work.

- Needs user authorization: **NOT AUTHORIZED**.

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
