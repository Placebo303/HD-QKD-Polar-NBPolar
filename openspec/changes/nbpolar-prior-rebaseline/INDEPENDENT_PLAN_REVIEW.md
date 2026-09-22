# Independent plan review — OpenSpec change `nbpolar-prior-rebaseline` (T1 gate)

| Field | Value |
|---|---|
| Reviewer | `reviewer-go` (first-pass, findings only — no edits made to plan documents) |
| Session | `ses_f373c5be0ffetZWN0YtCtTNm9U` (platform-provided session id), 2026-09-22 |
| Repo | `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` |
| Branch | `codex/nbpolar-phase0` (verified: `.git/HEAD` == `ref: refs/heads/codex/nbpolar-phase0`; not switched) |
| Date (UTC) | 2026-09-22 |
| Mode | Read-only docs review. No commits, no pushes, no code edits, no test runs, no data reads. The only filesystem write in this session is this file. G3 execution/records, Pre-EXECUTE/Pre-RESULT matters and M2 status are OUT of scope and were not investigated. |

## Scope statement

T1 — the outstanding independent plan-acceptance review of OpenSpec change
`nbpolar-prior-rebaseline` — while `tasks.md` already shows T2–T8 checked.
This review judges the PLAN documents only (proposal ↔ design ↔ tasks ↔
delta spec) against the five T1 gate criteria quoted below. It does not
re-adjudicate any execution gate, does not verify code/tests/data on disk,
and its verdict cannot retroactively authorize already-executed work
(authorization for any run lives in the separate freeze + user-authorization
records, not in T1). Inverted order (implementation/execution before
plan-acceptance) is recorded as process context in N1, not as a plan-content
FAIL.

Documents read in full (this review's only evidence base):

- `openspec/changes/nbpolar-prior-rebaseline/proposal.md` (98 lines)
- `openspec/changes/nbpolar-prior-rebaseline/design.md` (128 lines)
- `openspec/changes/nbpolar-prior-rebaseline/tasks.md` (67 lines)
- `openspec/changes/nbpolar-prior-rebaseline/specs/nbpolar-prior-rebaseline/spec.md` (51 lines; the only file under `specs/`)
- `openspec/project.md` (project context; architecture/constraints)
- `docs/nbpolar/STATE.md` §4.1 (M2 promotion-ladder ruling, lines 69–96)

Supporting read-only checks: file tree of the change (4 files above);
`openspec/specs/` merged-spec listing (`final-ir-method-selection`,
`formal-ir-methods`); case-insensitive grep for
`prior|nbpolar-phase4-p0|concentration` under `openspec/specs/` (no matches,
consistent with the proposal's "nothing there is modified" statement).

## T1 gate text (quoted verbatim from `tasks.md:8-10`)

> - [ ] T1: independent review of proposal/design/specs (seven decisions
>   explicit, four Supersedes replacements named, D7 frozen list intact).
>   Gate: review PASS recorded; else revise-required.

## Check 1 — Seven decisions explicit — PASS

Looked at: `design.md:7-107` (decision set D1–D7); cross-checked naming in
`proposal.md:32-36,40-52,85-87` and `tasks.md:8-10`.

Finding: all seven decisions are stated with implementer-grade specificity
(numbers, rules, named alternatives, fallback conditions). Named set:

- **D1 — Prior form** (`design.md:7-26`): M2 per-session ±1 (q0, q±1 over
  delta ∈ {0,+1,−1}, rest → floor) is the default, with S8 NLL margins
  (0.0366/0.0442 bits/symbol) and S9 decode vehicle cited; M1/M3/M4
  dispositioned; M1 candidacy conditions explicit (pool only if per-session
  frames below M2 fitting floor AND all pooled sources share verified delay
  sign; forbidden once any sign-distinct source enters CAL). Explicit.
- **D2 — CAL size** (`design.md:28-39`): 32 sacrificed frames/session (8192
  symbols), ~4× margin rationale, 0.25×-block cost at assumed 4 bits/symbol,
  hard floor never below 8 frames without a new freeze, no ≤1%-H-error
  guarantee claimed. Explicit.
- **D3 — Accounting** (`design.md:41-52`): sacrifice-only option (a); CAL
  excluded from key denominator and recorded per packet; reveal-bits
  (~18–22 bits, params·log2(n) bound) diagnostic-only, never a λ_prior term;
  Release 0-bit-charge + labeling rationale; claim scope unchanged
  (Müller 2025 eq (11)/(13) preregister-before-use). Explicit.
- **D4 — K allocation** (`design.md:54-67`): (K1,K2) re-derived from M2
  tables via accepted `select_empirical_split` semantics; H-proportional rule
  banned for construction K; fixed-f vs fixed-K_total BOTH unfrozen here
  (f=1.3 ⇒ K_total 7053/7106; frozen K_total ⇒ f=1.2939/1.2952);
  G2 freezes K1=319/K2=6492; P19 `l2_plus` falsification bounds the
  direction to rebalancing. Explicit (its *content* conflicts with the delta
  spec — that is Check 4 B1, not a Check-1 explicitness failure).
- **D5 — Construction** (`design.md:69-77`): first real-data M2 packet reuses
  frozen P16 order (arm-B path) on S9 arm-B-vs-C indistinguishability (2
  blocks, overlapping CIs); suboptimality gap recorded (TRAIN residual 0.132
  frozen vs 0.0001 rederived); re-derivation deferred to its own freeze gated
  on arm-B success. Explicit.
- **D6 — Validation gates** (`design.md:79-89`): G1 (real-data held-out NLL,
  preregistered split/seed, descriptive), G2 (one-shot Tier-Y decode at
  frozen K1=319/K2=6492, independent Pre-EXECUTE + Pre-RESULT, `undetected`
  isolation, disclosure recount), G3 (independent-session confirmation), G4
  (exhaustive public-message inventory with CAL frames listed), S9
  never-cited-as-evidence rule, Stage-3 measurement set prerequisite. Explicit.
- **D7 — Frozen list** (`design.md:91-107`): enumerated in the D7 section below.
  Explicit.

Verdict: **PASS**. No decision is left to implementer guesswork.

## Check 2 — Four `Supersedes` replacements named — PASS

Looked at: `proposal.md:38-52`.

Finding: each of the four items names BOTH the superseded thing AND its
replacement (with design-section pointer). Named set:

- **S1 — prior contract** (`proposal.md:40-44`): supersedes Phase 4-P0 prior
  contract (`docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` §1,
  `counts_ab` nonparametric `f[a,b]=(counts+λ·p_global)/(n_b+λ)` with
  `DECODER_FLOOR=1e-15`) → replaced by the M2 parametric rule (`design.md`
  D1); history-preservation clause included. Both sides named. Explicit.
- **S2 — CAL/DEV/EVAL lifecycle** (`proposal.md:45-46`): supersedes the
  1024-frame CAL lifecycle (262,144 symbols = 1024 frames) → replaced by the
  32-frame sacrificed CAL (D2). Both sides named. Explicit.
- **S3 — disclosure K allocation** (`proposal.md:47-50`): supersedes the
  mis-split allocation (L1 f≈2.00 over-disclosed, L2 f≈1.275
  under-disclosed, total f≈1.2975) → replaced by the re-split rule from the
  new H1/H2 with the f-vs-K_total choice preregistered separately (D4, not
  constant-total by default). Both sides named. Explicit.
- **S4 — λ_total accounting** (`proposal.md:51-52`): supersedes λ_total
  accounting with no prior-estimation term → replaced by explicit
  CAL-sacrifice accounting with no λ_prior term added (D3). Both sides
  named. Explicit.

Verdict: **PASS**. (S3's "not constant-total by default" parenthetical is
one corner of the Check-4 B1 contradiction — recorded there.)

## Check 3 — D7 frozen list intact — PASS_WITH_COMMENT

Looked at: `design.md:91-107` (D7 source); `proposal.md:56-66` (Scope
In/Out, Non-Goals); `tasks.md:52-53` (acceptance); `spec.md:38-43`
(decoder/verification boundary); `docs/nbpolar/STATE.md:69-96` (§4.1 ladder).

Finding: D7 is fully stated in `design.md:91-107`; no document contradicts,
reopens, or silently modifies any D7 item. The operative freezes are
preserved everywhere they are touched:

- Phase 0–1 / Phase 2 `sc.py` / verification primitives / registries /
  frozen-session artifacts: Out-of-scope in `proposal.md:59-61`,
  `sc.py` untouched in `tasks.md:52-53`, boundary SHALLs in `spec.md:38-43`.
- Accepted packets + negative results as history, never reopened:
  `proposal.md:65-66`, D7 itself.
- Ladder consistency: D6's no-synthetic-promotion / no-claim-before-gates
  rules agree with the STATE §4.1 ruling (`STATE.md:75-84,94`: no skipping,
  no S9 promotion, no cross-contract promotion; M2 stays CANDIDATE until
  gates pass). No conflict.

Comment (non-blocking, N6): the full evidential-history tail of D7 — the
V25-source identity finding, the S2/S4 54.8σ ideal-model qualification
(`design.md:99-103`), the H2 sign/MM-additivity correction
(`design.md:104-106`), the `2^(H2/SER)` heuristic ban (`design.md:107`) —
is not restated in tasks/specs (which cover only the structural freezes).
Absence is not modification, so this is not a FAIL, but the archive would
be sturdier with an explicit "D7 tail incorporated by reference to
`design.md:91-107`" pointer in the delta spec or tasks.

Verdict: **PASS_WITH_COMMENT**.

## Check 4 — Internal consistency — FAIL

Looked at: `proposal.md:32-36,38-52,56-61,70-81,85-87`;
`design.md:54-67,79-89`; `tasks.md:8-48,52-56`;
`spec.md:3-5,25-36,45-51`.

Findings:

- **B1 (blocking): K-rule contradiction — spec freezes what design defers.**
  `spec.md:27-30` ("Requirement: constant-total K re-split") states
  "K_total SHALL stay on the frozen f=1.3 literal" with (K1,K2) re-derived
  "at constant total". `design.md:60-63` states the opposite: "Neither is
  frozen here — the K_total choice is a separate later preregistered
  decision." `proposal.md:32-34,47-50` agrees with design ("preregistered
  separately (D4) rather than settled here"; "not constant-total by
  default"), as does `tasks.md:16-20` ("the fixed-K vs fixed-f choice is
  DECOUPLED and deferred"). Three-against-one: the mergeable delta spec is
  the outlier. Whichever K posture is intended, all four documents must say
  the same thing before archive.
- **B2 (blocking): spec validation gates drop D6's last gate and measurement
  prerequisite.** `design.md:79-89` requires G1+G2+G3+G4 *plus* the Stage-3
  measurement set (preregistered cap, per-block λ decomposition) before any
  claim-bearing statement, and names G4 as the exhaustive public-message
  inventory. `spec.md:45-51` gates only G1+G2+G3 and the S9 ban — G4 and the
  Stage-3 set vanish from the durable requirement. `tasks.md` has no G4
  freeze task either (T4 covers only an inventory *skeleton*,
  `tasks.md:21-23`; T8 explicitly pushes G3/re-derivation freezes out,
  `tasks.md:41-43`, and is silent on G4). The merged spec would therefore
  permit exactly the claim the design forbids (a claim without the
  inventory). Add G4 + Stage-3 set to the spec gates (or explicitly defer
  with a pointer and a corresponding task), and mirror it in tasks.
- Consistent (no finding): affected-specs list — `proposal.md:78-81`
  predicts exactly the delta that exists
  (`specs/nbpolar-prior-rebaseline/spec.md`), and the "nothing in merged
  `openspec/specs/` is modified" claim held on re-check (only
  `final-ir-method-selection`, `formal-ir-methods` present; no prior-content
  matches). Scope boundaries agree (M2/CAL/accounting/K-split/construction/
  gates/delta-spec/coder-tasks/CAL-note in, `proposal.md:56-58`; field/
  transform/`sc.py`/primitives/registries/implementation/execution/claims
  out, `proposal.md:59-61`). Construction numbers agree three-ways
  (K1=319/K2=6492 arm-B: `design.md:63,82-83`; `spec.md:34-35`;
  `tasks.md:29-30`). Task ordering T1→T8 is logical as a plan (review →
  adapt → split → docs → freeze G1 → freeze G2 → execute → adjudicate).
- Task↔spec mapping gaps (folded into B2/N-findings, none standalone
  blocking beyond B2): every spec requirement has a task counterpart
  *except* G4/Stage-3 (B2); every task maps to a plan element. On-disk
  artifact existence (T2 `prior.py`+oracle, T3 recomputation, T4 CAL note,
  T5/T6 freeze configs) was explicitly NOT checked — out of scope for this
  docs-only review (see "Could not determine").

Verdict: **FAIL** (B1 alone forces revise-required; B2 independently does).

## Check 5 — Delta-spec quality — PASS_WITH_COMMENT

Looked at: `spec.md:7-51` (all six requirements).

Finding: each delta reads as a REQUIREMENTS delta — SHALL/SHALL-NOT
normative statements with testable content — not prose or implementation
detail:

- ±1 prior (`spec.md:9-14`): per-session triple, expansion order
  (model-implied P(A|B) *before* 1e-15 floor + per-B-column renorm),
  forbidden legacy inputs, M1 pooling condition. Testable. PASS.
- Sacrificed CAL (`spec.md:18-23`): exact 32 frames (8192 symbols),
  denominator exclusion, inventory listing, 8-frame floor w/o new freeze,
  reveal-bits diagnostic ban from λ_total, in-sample-estimation default ban.
  Testable. PASS.
- K re-split (`spec.md:27-30`): normative and testable as written — but its
  *content* (constant-total f=1.3) contradicts its parent decision (see B1).
  Quality verdict PASS_WITH_COMMENT; consistency verdict FAIL per Check 4.
- Construction freeze (`spec.md:34-36`): frozen P16 order at K1=319/K2=6492,
  re-derivation gated on own freeze + arm-B success. Testable. PASS.
- Decoder/verification boundary (`spec.md:40-43`): unchanged `sc.py`/tag/
  counting/`undetected`-isolation, shape/axis/tolerance preservation,
  test-local oracle helper. Testable. PASS.
- Validation gates (`spec.md:47-51`): G1+G2+G3 precedence + S9 citation ban.
  Testable as process gates — but incomplete vs D6 (see B2).

Precision comments (non-blocking, N4/N5): "verified shared delay sign"
(`spec.md:14`) cites no verification procedure — point to D1/design or the
acceptance procedure; "tolerances" (`spec.md:42`) cites no values/location —
point to the frozen tolerances referenced in `tasks.md:52-53`.

Verdict: **PASS_WITH_COMMENT**.

## Enumerated registers (as required)

### The seven decisions (design.md D1–D7)

1. D1 — Prior form: M2 per-session ±1 default; M1 conditional fallback only
   (`design.md:7-26`).
2. D2 — CAL size: preregistered 32 sacrificed frames/session, floor 8
   (`design.md:28-39`).
3. D3 — Accounting: sacrifice CAL, no λ_prior term, claim scope fixed
   (`design.md:41-52`).
4. D4 — K allocation: re-split from new H1/H2 via `select_empirical_split`;
   f-vs-K_total choice deferred (`design.md:54-67`).
5. D5 — Construction: frozen P16 order for first packet; re-derivation
   deferred (`design.md:69-77`).
6. D6 — Validation gates G1/G2/G3/G4 + S9 ban + Stage-3 set
   (`design.md:79-89`).
7. D7 — Frozen list intact (enumerated below) (`design.md:91-107`).

### The four Supersedes (proposal.md:38-52)

1. P0 prior contract (counts_ab + 1e-15 floor) → M2 parametric rule (D1).
2. 1024-frame CAL lifecycle → 32-frame sacrificed CAL (D2).
3. L1-f≈2.00/L2-f≈1.275/total-f≈1.2975 allocation → H1/H2 re-split with
   separately preregistered f-vs-K_total choice (D4, not constant-total).
4. λ_total without prior term → explicit CAL-sacrifice accounting, no
   λ_prior term (D3).

### D7 frozen list (design.md:91-107)

1. Phase 0–1: GF32 poly 37, alpha=2, row-vector, natural order, butterfly.
2. Phase 2 `sc.py`: consumes `logp(N,q)`, agnostic to prior form/labeling.
3. 64-bit Toeplitz tag, disclosure counting, `undetected` isolation.
4. Data registries and frozen-session derived artifacts.
5. P16/P17/P20 accepted packets as history.
6. Every negative result as history: P13/P14/P15 NOT_CONFIRMED, P19 0/3
   `l2_plus`, M4≡M0 structural identity, split-rebalance non-recommendation.
7. V25-source identity finding.
8. S2/S4 findings: 54.8σ margin as stated — ideal ML/uniform-input
   optimistic bound, NOT a refutation of H-A (rate/finite-length), only an
   absence of binding evidence under the ideal model.
9. H2 bias small with sign NOT established — MM ADDS (corrected H2
   0.8026903611/0.8089106006); MM +0.29%/+0.25% vs split-half −0.31%/−0.28%,
   opposite signs, comparable magnitude — NOT a refutation of H2
   misestimation.
10. `2^(H2/SER)` heuristic ban.

## Findings

### Blocking (must fix for T1 PASS; FAIL = revise-required)

- **B1 — K-rule contradiction between delta spec and design/proposal/tasks.**
  `spec.md:27-30` freezes constant-total f=1.3; `design.md:60-63`,
  `proposal.md:32-34,47-50`, `tasks.md:16-20` defer the fixed-f vs fixed-K
  choice. *Required change:* pick one posture and write it identically in
  all four documents (and adjust T3's gate language to match). If deferral
  wins, the spec requirement must read as deferred (e.g. "K_total SHALL be
  set only by a later preregistered decision; until then G2 stays at
  K1=319/K2=6492") instead of freezing f=1.3.
- **B2 — Durable gates weaker than design gates (G4 + Stage-3 set dropped).**
  `spec.md:45-51` omits the G4 exhaustive public-message inventory
  (`design.md:86-87`) and the Stage-3 measurement-set prerequisite
  (`design.md:87-89`). *Required change:* add both to the spec's validation-
  gates requirement (or explicitly defer each with a pointer), and add the
  corresponding freeze/inventory task(s) to `tasks.md` (T4 currently covers
  only a skeleton, `tasks.md:21-23`).

### Non-blocking (advisory; do not gate T1)

- **N1 — Status-header staleness / inverted-order liability.**
  `proposal.md:5-7` still reads
  `PLAN_CANDIDATE / IMPLEMENTATION_NOT_AUTHORIZED / EXECUTE_NOT_AUTHORIZED`
  / "Planning artifacts only", and `proposal.md:98` / `tasks.md:4` authorize
  no implementation/execution — while `tasks.md:11-48` records T2–T8 checked
  with G1/G2 execution done. *Suggestion:* refresh the status block (or add
  one line) clarifying that implementation/execution authority came from the
  separate coder packets, freeze reviews and user authorizations — not from
  this change — so the archive does not read as self-contradictory. Process
  context only; not a plan-content defect.
- **N2 — "No `.py` implementation" vs coder packets.** `proposal.md:59-61`
  puts "any `.py` implementation" out of scope while `tasks.md:11-20`
  (T2/T3) are implementation packets. *Suggestion:* one clarifying line that
  T2/T3 code lives under separate coder-packet authorization (cf. impact
  scope, `proposal.md:70-72`) rather than in this change.
- **N3 — Affected-specs wording drift.** `proposal.md:78-80` says
  `"accepted concentration prior" and "lifecycle"`; `spec.md:3-5` says
  `"accepted concentration prior" and "lifecycle and truth isolation"`.
  *Suggestion:* align the two strings.
- **N4 — Unpointed "verified shared delay sign".** `spec.md:14` conditions
  M1 pooling on it without citing the verification procedure. *Suggestion:*
  point to `design.md:23-26` (D1) or the acceptance procedure.
- **N5 — Unpointed "tolerances".** `spec.md:42` requires shape/axis/
  tolerance preservation without values. *Suggestion:* point to the frozen
  tolerances cited in `tasks.md:52-53`.
- **N6 — D7 tail incorporated only by reference gap.** See Check 3 comment:
  add a "D7 tail per `design.md:91-107`" pointer in the spec or tasks; no
  duplication needed.
- **N7 — No plan↔record drift asserted.** Within the allowed narrow
  exception (plan document *factually contradicted* by a record): none
  found in the documents read. `tasks.md:41-48` keeps G3 in its own packet
  out of this task list, consistent with brief scope; STATE §4.1 ladder
  (`STATE.md:69-96`) and the plan's gates agree (no synthetic promotion, no
  skipping, no cross-contract comparison). G3 records were not examined, per
  the explicit out-of-scope rule, so no drift finding for or against G3 is
  made here.

## T1 verdict: FAIL (revise-required)

Justification, one line per numbered check:

1. Seven decisions explicit — **PASS** (`design.md:7-107`, all implementable
   as written).
2. Four Supersedes named — **PASS** (`proposal.md:38-52`, both sides named).
3. D7 frozen list intact — **PASS_WITH_COMMENT** (intact, uncontradicted;
   tail-by-reference pointer advised, N6).
4. Internal consistency — **FAIL** (B1 K-rule contradiction; B2 dropped G4/
   Stage-3 gates).
5. Delta-spec quality — **PASS_WITH_COMMENT** (proper SHALL-style testable
   deltas; precision pointers advised, N4/N5).

Single verdict: **FAIL**. The plan is well-formed (Checks 1, 2 pass; 3 and
5 pass with comments) but contains two substantive internal contradictions
that must be reconciled before the change can be accepted and eventually
archived: (B1) the mergeable delta spec freezes the constant-total f=1.3 K
rule that the design, proposal and tasks all defer — exactly one posture
must be written identically in all four documents; (B2) the durable spec
gates omit D6's G4 inventory and Stage-3 measurement prerequisite, which
would leave the archived requirement permitting a claim the design forbids
— both must enter the spec gates (or be explicitly deferred with pointers)
with matching task coverage. Non-blocking items N1–N7 are advisory and must
not hold up re-review once B1/B2 are fixed.

## Could not determine (explicitly out of scope — not verdict-relevant)

- On-disk existence/content of T2–T4 artifacts (`prior.py` delta, oracle
  match, K re-split recomputation, `SECURITY_MODEL.md` CAL note, inventory
  skeleton) and T5–T7 gate satisfaction (focused tests, T0, freeze reviews,
  Pre-EXECUTE/Pre-RESULT outcomes, adjudications): no code, test, or
  execution verification was performed, per the brief.
- Whether merged `openspec/specs/` *should* carry an NB-Polar prior
  requirement in future: only the "nothing there is modified" factual claim
  was checked (holds).
- Any G3/Pre-RESULT/M2-status matter: not examined, per the brief.

## Review provenance

- `.git/HEAD` at review time: `ref: refs/heads/codex/nbpolar-phase0`
  (branch `codex/nbpolar-phase0`, never switched).
- Files read: listed in "Scope statement" with line counts; all findings
  carry `file:line` citations inline.
- Files written: exactly this one —
  `openspec/changes/nbpolar-prior-rebaseline/INDEPENDENT_PLAN_REVIEW.md`.
  No plan document (`tasks.md`, `proposal.md`, `design.md`, `specs/`) or any
  other file was edited. T1 remains `[ ]` for the main thread to adjudicate.

## Operator response to T1 review

Operator (coder-doc subagent, 2026-09-22, branch `codex/nbpolar-phase0`):
B1/B2 fixed per main-thread rulings R-B1/R-B2; N1–N6 addressed as below.
No finding or verdict above was altered; T1 left `[ ]` for re-review.

- **B1** — `specs/nbpolar-prior-rebaseline/spec.md` K requirement rewritten
  to the deferred posture: fixed-f vs fixed-K_total DEFERRED to a later
  preregistered decision (D4, `design.md` D4), D4 record report-only, G2/G3
  SHALL stay at frozen K1=319/K2=6492; future (K1,K2) SHALL come from the
  accepted `select_empirical_split` selector. Heading renamed from
  "constant-total K re-split" to "deferred K re-split". Posture now matches
  `design.md` D4, `proposal.md`, `tasks.md` T3.
- **B2** — `spec.md` validation-gates requirement extended with G4
  (exhaustive public-message inventory with CAL frames listed) and the
  Stage-3 measurement set (preregistered cap, per-block λ decomposition),
  both pointed at `design.md` D6. `tasks.md` T4 extended with the G4
  follow-up row (freeze + review + execution as future tasks requiring
  their own packet and explicit user authorization; no G4 authority
  granted); T8 out-of-list now names G4 alongside G3/re-derivation.
- **N1** — `proposal.md` Status + Tasks sections and `tasks.md` ownership
  header updated: T2–T8 done, T1 open — FAIL, revise-required, re-review
  pending. T1 box NOT ticked.
- **N2** — `proposal.md` Scope-Out "any `.py` implementation" corrected:
  T2/T3 code lives under separate coder-packet authorization, not this
  change's authority.
- **N3** — `proposal.md` Affected-specs aligned to `spec.md` wording:
  "lifecycle and truth isolation".
- **N4** — `spec.md` M1 pooling condition now points to `design.md` D1.
- **N5** — `spec.md` tolerances now point to `tasks.md` Acceptance and
  `design.md` Data-flow change.
- **N6** — `design.md` D7 section gained a by-reference pointer sentence;
  D7 item text untouched (verify: `git diff` on `design.md` shows only the
  added pointer paragraph).
