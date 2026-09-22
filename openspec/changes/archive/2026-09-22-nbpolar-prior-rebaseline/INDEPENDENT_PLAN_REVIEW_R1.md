# Independent plan re-review R1 — `nbpolar-prior-rebaseline` B1/B2 closure (T1 gate)

| Field | Value |
|---|---|
| Reviewer | `reviewer-go` (first-pass, findings only — no edits, no box checks) |
| Session | `ses_f366116deffejUowp78z70xQuH`, 2026-09-22 UTC |
| Repo | `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` |
| Branch | `codex/nbpolar-phase0` (verified: `.git/HEAD` == `ref: refs/heads/codex/nbpolar-phase0`; not switched) |
| Date (UTC) | 2026-09-22 |
| Mode | Read-only docs re-review. No commits, no pushes, no code edits, no test runs, no data reads. Files written: none (this content proposed for `INDEPENDENT_PLAN_REVIEW_R1.md` only). Original `INDEPENDENT_PLAN_REVIEW.md` FAIL record untouched. `tasks.md` checkboxes untouched. |

## Scope statement

Re-review ONLY the B1/B2 fixes in `58e67f80` + `024fa7cb` against the current
`spec.md` / `tasks.md`. Out of scope: re-adjudication of Checks 1/2/3/5,
N1–N7, any code/tests/data on disk, any G1/G2/G3 execution gate,
Pre-EXECUTE/Pre-RESULT, M2 status. Inverted-order context (T2–T8 checked
before T1) remains process context, not re-judged here.

Evidence base (read in full at current HEAD `024fa7cb`):

- `openspec/changes/nbpolar-prior-rebaseline/specs/nbpolar-prior-rebaseline/spec.md` (60 lines)
- `openspec/changes/nbpolar-prior-rebaseline/tasks.md` (78 lines)
- `openspec/changes/nbpolar-prior-rebaseline/proposal.md` (105 lines)
- `openspec/changes/nbpolar-prior-rebaseline/design.md` (133 lines)
- `git show 58e67f80 --stat` + full plan-docs diff; `git show 024fa7cb --stat` + full diff

`58e67f80` touches only the change plan docs + new FAIL record (5 files:
`INDEPENDENT_PLAN_REVIEW.md` new 423 lines, `design.md` +5, `proposal.md`,
`spec.md`, `tasks.md`). `024fa7cb` touches only `proposal.md` + `tasks.md`
(status/T1-closure + Stage-3 mirror line). No `.py`, no test, no data change.

## B1 closure — K-rule contradiction resolved to deferred posture

Original B1: `spec.md` froze constant-total f=1.3 while
`design.md`/`proposal.md`/`tasks.md` deferred fixed-f vs fixed-K_total.

Fix verified (all four documents now say DEFERRED, G2/G3 pinned):

- `spec.md:26-35` — heading renamed from "constant-total K re-split" to
  "deferred K re-split (fixed-f vs fixed-K decision pending)";
  `spec.md:28-30` "fixed-f vs fixed-K_total choice is DEFERRED to a separate
  later preregistered decision (D4, `design.md` D4) — neither branch is frozen
  here; the D4 recomputation record is report-only planning input";
  `spec.md:30-31` "G2/G3 SHALL stay at the frozen allocation K1=319/K2=6492
  regardless"; `spec.md:31-35` selector + disclosure-increase ban +
  H-proportional ban.
- `design.md:54-67` — D4 title "f-vs-K_total choice deferred";
  `design.md:59-63` "Fixed-f and fixed-K_total cannot both hold ... Neither is
  frozen here — the K_total choice is a separate later preregistered decision.
  G2 freezes K1=319/K2=6492 regardless of that choice."
- `proposal.md:36-38` — "f-vs-K_total choice is preregistered separately (D4)
  rather than settled here"; `proposal.md:51-54` S3 "preregistered separately
  (D4, not constant-total by default)".
- `tasks.md:22-26` — T3 "the fixed-K vs fixed-f choice is DECOUPLED and deferred
  to a later preregistered decision (f=1.3 ⇒ K_total 7053/7106; frozen K_total
  ⇒ f=1.2939/1.2952). H-proportional rule banned."

Posture is now four-way identical (deferral wins; constant-total language gone).
Basis: `58e67f80` spec rewrite + heading rename; `024fa7cb` did not alter K
language. B1 CLOSED.

## B2 closure — G4 + Stage-3 set now in durable gates, mirrored in tasks

Original B2: `spec.md` gated only G1+G2+G3, dropping D6's G4 inventory and
Stage-3 measurement prerequisite.

Fix verified:

- `spec.md:51-60` — gates now "G1 + G2 + G3 + G4 (exhaustive public-message
  inventory, Release pattern, with the CAL frames listed; `design.md` D6) +
  the Stage-3 measurement set (preregistered cap, per-block λ decomposition;
  `design.md` D6) before any claim-bearing statement"; `spec.md:59-60` S9 ban
  retained.
- `design.md:79-89` — D6 source requires G1/G2/G3/G4 + S9 ban + Stage-3 set;
  spec text points explicitly to `design.md` D6 (`spec.md:56-58`).
- `tasks.md:27-32` — T4 "G4 follow-up (future, out of this task list): G4 freeze
  + independent review + execution tasks require their own packet and explicit
  user authorization — no G4 work is authorized by this change";
  `tasks.md:50-53` — T8 "G3, G4, and any construction re-derivation need their
  own freezes — explicitly out of this task list";
  `tasks.md:59` (`024fa7cb` addition) — "Stage-3 measurement set (preregistered
  cap, per-block λ decomposition; design.md D6) required before any
  claim-bearing statement — no Stage-3 task is authorized by this change."

Spec adds both missing gates; tasks mirrors with explicit future-packet
deferral + no-authority clause, satisfying the required-change alternative
("add to spec gates ... with matching task coverage"). Merged spec would no
longer permit a claim without inventory/Stage-3. B2 CLOSED.

## Verdict: PASS_WITH_COMMENTS

B1 CLOSED (four-way deferred posture, file:line above). B2 CLOSED (G4 + Stage-3
in spec gates with task mirror, file:line above). No new blocking contradiction
introduced by `58e67f80+024fa7cb`. Two non-blocking comments only (see below);
they do not gate T1.

## Non-blocking comments (do not gate T1)

- C1 (stale note): `tasks.md:14-15` still reads "verdict FAIL, re-review required
  after B1/B2 fixes; T1 stays open" alongside header `tasks.md:5-7` (T1 closed —
  PASS_WITH_COMMENTS) and `tasks.md:16` Done line (re-review PASS_WITH_COMMENTS —
  main-thread acceptance). Retained history is fine; suggest one clarifying
  timestamp ("superseded by Done line below") at next milestone batch.
- C2 (G2 vs G2/G3 pin wording): `spec.md:30-31` pins G2/G3 while `design.md:63`
  pins only G2. Stronger freeze is safe; suggest aligning D4/spec wording at next
  milestone batch.

## Could not determine (out of scope — not verdict-relevant)

- On-disk T2–T4 artifacts, K recomputation, CAL note, freeze configs,
  Pre-EXECUTE/Pre-RESULT outcomes, adjudications: not checked (docs-only brief).
- Checks 1/2/3/5 and N1–N7 re-judgment: not performed (R1 scope is B1/B2 only).
- Any G3/Stage-3 execution matter: not examined.

## Provenance

- `.git/HEAD`: `ref: refs/heads/codex/nbpolar-phase0`, never switched.
- Diffs reviewed: `58e67f80` (T1 revise: B1 defer + B2 strengthen + FAIL record;
  re-review pending) and `024fa7cb` (T1 closed PASS_WITH_COMMENTS + Stage-3
  mirror + main-thread acceptance).
- Files written: none. Original FAIL file unaltered. `tasks.md` boxes unaltered.
  This R1 record is the ONLY new file proposed; creation + T1 adjudication belong
  to the main thread.
