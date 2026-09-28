# Design — nbpolar-r2-fer-measurement-contract

Status: **draft (docs-only)**
Decisions D1–D7 below are planner proposals; none of them preempts the PI's
adjudication in task T4.

---

## D1 — Single contract; acquisition draft demoted to Annex

The two R0.2 drafts are merged into **one** preregistered measurement contract:

- `FER_DEFINITION_DRAFT_20260922.md` provides the **normative body** (FER
  definition, estimate, CI, `undetected` isolation, accounting formulas).
- `ACQUISITION_SPEC_DRAFT_20260922.md` is **demoted to Annex A** (source
  selection, branch choice, reserve quotas, noise band, budget). It supplies
  parameters the contract consumes; it does not redefine FER semantics.

Rationale: one document removes double-specification drift; the acquisition
annex remains reviewable as a self-contained unit while no longer competing as
a second normative source.

### C1–C14 merged clause list (instantiated by T2)

| ID | Clause | Origin |
|----|--------|--------|
| C1 | Purpose, scope, applicability **and comparability boundary (FER §8)**: cross-contract FER numbers are **incomparable** (G1 w=500/LINEAR vs G2 w=200/CIRCULAR; synthetic S9; G3's n=14 confirmation sample; any data with an inconsistent `undetected` convention); Müller `FER < 0.003` is comparable only with the same-sentence three-point caveat (different code family, different channel, different disclosure budget); **before `FER_MEASURED_AT_CONTRACT` is reached, no FER number may appear in any abstract/summary**; Carried caveats (a)–(d) (w=200 truncation of the population; structured far-offset accidental baseline; q_rest=0 weak-statement bound 3/8192; L2 domain `u1` vs `high_hat`) are copied verbatim into the frozen contract notes | FER draft §8 + Carried caveats (a)–(d) |
| C2 | Unit of analysis (frame) and FER definition | FER draft |
| C3 | Primary point estimate + Wilson CI (z=1.96) pending D-FER-01 | FER draft |
| C4 | `undetected` isolation: never merged into success/FER, reported per-source | FER draft |
| C5 | Block-outcome taxonomy per FER §3 (R-4, fixed): `exact` (success — denominator only, not numerator), `verify_failed` (**failure** — numerator + denominator), `decode_failed` (**failure** — numerator + denominator), `undetected` (isolated — never enters numerator or denominator, own column and count per §6), `resource_abort` / invalid-run (**excluded from BOTH numerator and denominator; the excluded counts MUST be disclosed** — execution incident, not a scientific FAIL). Method `status` vocabulary is kept separate from this run-state taxonomy (see C5 note below) | FER draft §2/§3/§6 (R-4) |
| C6 | H(X\|Y) substitution convention and mandatory disclosure (D-FER-04) | FER draft |
| C7 | f_FER / efficiency accounting: computed f vs stated f, leakage decomposition (D-FER-05) | FER draft |
| C8 | Per-frame derivative reading rule — secondary, non-claim (D-FER-07) | FER draft |
| C9 | Sample size n and target half-width w relation (D-FER-02/03) | FER draft |
| C10 | Acquisition branch A / A′ / B and source list (D-ACQ-01/02); **raw-file rules (ACQ §7)**: read only primary `<stem>.ttbin` (FileReader auto-follows `.1`; un-reverified census carry-overs declared at closure), `results_*`/analysis by-products are name-inventoried only (`ls`/`find` level — never opened, never cited), POSIX/WSL path discipline (Windows paths provenance only); **participation/contamination ledger (ACQ §9)**: every census/touched acquisition recorded with contact type (decoder-free vs decoder), date, artifact id, and **decoder-touched frames NEVER reflow into a confirmation sample** | ACQ annex §2/§7/§9 |
| C11 | Reserve quota strategy and Type0 inclusion (D-ACQ-03/04); **per-acquisition reservation partition (ACQ §4)**: CAL / CHAR / HELDOUT / EVAL / RESERVE are mutually exclusive and recorded in the **`reservation-partition matrix`** (explicitly distinct from the D4 clause-provenance disjointness matrix — two different artifacts); **COMPLETE-BLOCKS-ONLY**: at closure, insufficient complete EVAL blocks ⇒ `INSUFFICIENT` ⇒ INCONCLUSIVE — never pad, never reuse, never shrink N (ladder-exhaustion precedent: 69 < 1 block after 32f CAL) | ACQ annex §4/§6 |
| C12 | Noise band definition (D-ACQ-05) | ACQ annex |
| C13 | Budget numbers, wall/RSS/data volume, ≥2 sessions (D-ACQ-06/08) | ACQ annex |
| C14 | Contract inheritance into later changes + `undetected>0` escalation (D-FER-06, D-ACQ-07) | both |

**C10/C11 note (2026-09-28, `nbpolar-data-use-rules-revision` T1 DECIDED)**:
from 2026-09-28, C10's "decoder-touched frames NEVER reflow into a
confirmation sample" is read under the new data-use rules (R1-R5,
`openspec/changes/nbpolar-data-use-rules-revision/design.md` D7) as: a
decoder-touched block **may** be used again, but only under R2's discipline —
pre-frozen method/parameters, full declared block set, no post-hoc tuning,
and mandatory stratum labeling for any block that touched decoding or model
selection (e.g. the `EVAL_already_decoded` / `HELDOUT_model_selection`
strata in `docs/nbpolar/DATA_LEDGER.md` §7). Security bookkeeping continues
to follow R1: reuse of an already-decoded block adds no disclosure beyond
what that block's own decode already counted toward `beta_eff`/the key
denominator (D1 of that change). This does not itself freeze D-ACQ-02/03 —
see `tasks.md` for the transcribed `DECIDED` values — and does not change
C4's `undetected` isolation or C5's taxonomy.

**C5 note (run-state vs method status, kept strictly apart)**: the taxonomy in
C5 is *run-state* semantics feeding the FER numerator/denominator arithmetic.
It is **not** the method reporting `status` vocabulary (`reference`, `stub`,
`unavailable`, `decode_failed`, `no_verified_success`, `ok`, … per AGENTS.md
§5.5). A method `status` is a result-row label, never an input to the FER
arithmetic, and no `status` value — and no block-outcome value — may be
silently converted to `ok` (AGENTS.md §5.5).

## D2 — Order of derivation: difference → w → n → quota

The chain is strictly one-directional and cannot be inverted by convenience:

1. PI states the **minimum discriminable difference** (the effect size the
   measurement must be able to resolve).
2. Difference fixes the **target CI half-width w** (C9, D-FER-02/03).
   **Ordering rule vs D-FER-02 (fixed — one kind only: difference
   unilaterally supersedes)**: w is *derived from* the discriminable
   difference under the frozen CI convention; the value PI adjudicates as
   D-FER-02 MUST equal that derived w. A D-FER-02 value inconsistent with the
   derived w is reported back to the PI as a conflict (D-ACQ-06-style
   escalation), never reconciled by re-stating the difference. The two inputs
   are **not** mutually-confirming: difference → w is strictly one-way, and
   w is never chosen first and the difference fitted to it afterwards.
3. w fixes the **sample size n** under the frozen CI convention (Wilson,
   z=1.96 unless D-FER-01 changes it).
4. n fixes the **quota** (frames × pairs) by plain arithmetic in T5.

No quota is chosen first and justified afterwards. If the derived quota exceeds
the C13 budget, that is reported to the PI as a conflict between D-ACQ-06 and
the discriminable difference — not silently traded off.

## D3 — Three-state adjudication mirroring G3

Every PI decision (D-FER-01..07, D-ACQ-01..08) is adjudicated into exactly one
of three states, mirroring the accepted G3/G4 pattern:

- `DECIDED(value)` — a concrete value/convention is locked.
- `DEFERRED(reason, retrigger)` — carried with an explicit retrigger condition;
  deferred items cannot be cited as frozen.
- `NOT_APPLICABLE(reason)` — ruled out of this contract's scope.

A decision left in an unadjudicated state blocks the **freeze verdict** that
T3's review underwrites: with every ledger row still unadjudicated (15 rows
`PENDING` at the T2 hand-off), T3 still performs its read-only **structural**
review and may pass or fail it, but **cannot judge freeze-pass** — freeze-pass
is judged after T4 adjudicates. (Pass standard clarified in R2-T2-FIX to
reconcile D3 with the T2→T3→T4 order in `tasks.md`; the alternative reading —
unadjudicated rows blocking T3 itself, i.e. a T4→T3 reorder — is a design/tasks
conflict escalated to the main thread, not resolved here.) Only
`DECIDED` entries appear in the frozen contract body; `DEFERRED` entries appear
in a clearly marked open-decision table.

## D4 — Disjointness matrix + ledger table

Two structural checks guard the merge:

- **Clause-provenance disjointness matrix (C1–C14 × source draft)**: shows
  which clause is normative from which source, and proves no clause is
  specified twice with conflicting wording. This is a *document* matrix and is
  explicitly **distinct** from the ACQ §4 **`reservation-partition matrix`**
  (CAL/CHAR/HELDOUT/EVAL/RESERVE mutual exclusion, carried in C11) — the two
  matrices are different artifacts with different subjects. Any overlap found
  during T2 is escalated to the PI, not auto-resolved.
- **Decision ledger table**: one row per D-FER-*/D-ACQ-* ID with columns
  `ID | clause | question | adjudication state | value/rationale | date`.
  This ledger is the authoritative record of D3 states and is the artifact T3
  freeze review inspects.

## D5 — Budget

Hard budget referenced from C13 / D-ACQ-06, using the accepted G2/G3 execution
envelope as the working reference: wall ≈ 855–858 s ≤ 900 s, RSS ≈ 1.12–1.13 GiB
≤ 2 GiB, data volume 128 frames × 256 pairs = 32768 **symbols** per block
(= N, the R-1 unit of FER draft §1 — not "pairs").

Planning constraint **R-2**: the G2 B-arm result 3/14 (p ≈ 0.214) may be used
**only for sizing**. The strings "11/14" and any rendering of it as
"FER ≈ 0.21" must never appear as a FER claim anywhere in this contract.

Budget is a *constraint on the derived quota* (D2 step 4), never a reason to
change w or n after freeze.

## D6 — Stage-3 isolation

Nothing in C1–C14 may depend on, import, or partially execute Stage-3
(efficiency / secret-key-yield) machinery. Efficiency-related formulas (C6, C7)
are documented as *accounting conventions to be used later*, with their inputs
explicitly marked "not measured by this contract". This keeps the FER contract
independently freezable and prevents an R3 dependency from back-dating into R2.

## D7 — G4 sync citation

G4 inventory sync is **already complete** (decision-log `docs/decision-log.md`,
2026-09-23 entry: "NB-Polar M2-prior G4 inventory COMPLETE"). This change only
**cites** that entry as provenance in the merged contract header (task T1). No
re-inventory, re-adjudication, or G4 artifact edit is in scope.

## D8 — T4 pending gate (planner proposal; PI adjudication reserved)

All rows are `PENDING` until T4 adjudicates; none is a frozen value; no
execution is authorized. Frozen numbers are unchanged (Δ=0.10, R-a, w=0.10,
p=3/14, z=1.96, n=65, K1=319/K2=6492).

| ID | Topic | State | Owner | Retrigger / note |
|---|---|---|---|---|
| PI-RULING-T4-SCOPE-DELTA | T4 scope + minimum discriminable difference Δ (D2 chain Δ→w→n→quota) | PENDING | PI | retrigger=freeze verdict before T5; Δ states the scientific question, never fitted to w afterwards |
| PI-RULING-KTOTAL | K_total fixed-f vs fixed-K convention (§5) | PENDING | PI | retrigger=any rebalance; G2/G3 stay frozen at K1=319/K2=6492 until decided |
| PI-RULING-R-5 | R-5 removal-or-definition (T4 sheet §6) | PENDING | PI | retrigger=a sourced definition appears; this contract invents no R-5 content |
| PI-RULING-ANNEX | Annex morphology (FER body + ACQ Annex A; P1/P2 placeholders Annex-only) | PENDING | PI | retrigger=T2 write; no partial citation into the normative body before decision |
| PI-RULING-D3 | D3 reading: unadjudicated rows block the freeze verdict, not T3 itself | PENDING | PI | retrigger=T4; `docs/nbpolar/STATE.md:65` freeze (real-data execution, SCL lock, promotion/qualification) is NOT auto-lifted by Tier-X probes |
| PI-RULING-STRONG | Strong-version scope stays out of R2 (paired comparison, efficiency, Branch B, ≥2-session batch, per-frame claim, f-target reset) | PENDING | PI | retrigger=separate item; recorded as DEFERRED/NOT_APPLICABLE, not sized here |
| PI-RULING-MEM | Ledger/memory updates batched at milestones (no per-probe durable writes) | PENDING | PI | retrigger=milestone review; Tier-X probes stay descriptive-only |
| PI-RULING-PENDING | General pending gate: only `DECIDED` rows enter the frozen body | PENDING | PI | retrigger=T4 adjudication; freeze-pass judged after T4, per D3 |

No R-5 mapping row is present in this design. R-5 stays pending PI
removal-or-definition; the T3 total-mapping check reports it for PI action
instead of auto-failing T2 or inventing its content.

## Non-goals of this design

No new statistics machinery beyond the drafted Wilson default; no automation of
quota computation beyond explicit arithmetic in T5; no schema/verifier
infrastructure (research-code engineering policy applies).
