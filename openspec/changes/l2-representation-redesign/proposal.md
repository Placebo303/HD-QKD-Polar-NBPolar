# Proposal: L2 Representation & Disclosure-Placement Redesign (Route B — scoping only)

## Status

`SCOPING_ONLY_NO_EXECUTION_AUTHORIZED` — proposal + design + tasks + packet skeleton only.
No implementation, no execution, no authorization granted by this change.

**Placement justification (one line)**: the X14→X17 + G3 closeout records mandate that any
operating-point redesign be a **new top-level OpenSpec change** with its own freeze and
authorization (decision-log 2026-09-20 H2-v2 entry: "any SCL work needs an operating-point
change (new top-level OpenSpec change) and separate authorization"), and Route B is exactly
that redesign — so it lives as its own change dir, not as an amendment of
`scl-synthetic-list-gate` or the Phase-4 umbrella.

## Problem

The NB-Polar real-data track has spent five descriptive single factors (P20N/P20O/P20Q
construction-side, P20R order-side, P20T reduced-N) and the synthetic SCL line has closed as
non-informative (X14→X17 + G3). The binding constraint is now evidenced on both sides:

### 1. Failures concentrate L2 / layer-side (real-data, descriptive only)

- P20M (first genuine out-of-sample 1.5M VAL segment, raw prior, K1=331/K2=6689, true-L1
  oracle): 0/3 operational exact; first errors L2/26, L1/848, L2/31 with L1 exact on the
  breakthrough records — L1 can be fixed, L2 then fails. Prior TRAIN-segment oracle arms had
  been 3/3 exact; out-of-sample they are not.
- P20N (alt-L2 construction, 1.5M HOLD): all 14 failures L2-layer; L1 exact on all 8
  operational records; operational restoration 1/4 (descriptive).
- P20O/P20Q (2M sessions): restoration 2/5 and 4/5 descriptive; P20Q's 12 L2-fail records
  are all natural-index-in-X-prefix but U-domain-out — genuine undisclosed-region SC errors,
  no pinning violation. Zero B−A / D−C disclosure delta.
- P20R (order-side): 0/1 negative, block-dominated — even the true-L1 oracle pair failed the
  block, so the order factor is not discriminated.
- P20T (N=8192, 2M HOLD tail): A/B/O all `verify_failed` with L2 first errors under every
  arm; within-N descriptive only.
- D-series (sibling NB-LDPC history, read-only context): D7-C accepted f=1.0 L2 `0/16 -> 1/16`
  even at oracle — "f=1.0 L2 remains effectively unrecovered"; the G1 L1 discriminator
  recovered only square-only (zero-rate) cells 1/4, 2/4 vs nonzero-rate 0/4, with truth-mass
  ~0.10–0.15 vs ~0.28 needed (V72P2D5 C1 L1 mass 0.096 fails incl. square).

Reading: the L1 estimator cannot supply enough conditioning mass (~0.10–0.15 vs ~0.28
needed), L2 recovers only at near-zero rate, and every real-data failure cluster sits on the
L2/layer side. The L2 model/representation — its channel metric, its prior structure, and
where disclosure is spent — is the binding constraint.

### 2. Disclosure at the current model gives no bite (synthetic, descriptive only)

- X16 (N=32768, K1=334/K2=6746 first-natural forced-correct, d=0.75 diagonal): pooled
  greedy-SC mismatch 0.7690162658691406 vs the applicable no-information ceiling
  (1−6746/32768)×31/32 = 0.76931 — ceiling-hugging (recorded |Δ| 0.00030), G2 0.99919 PASS
  (tables informative; the SC path itself sits at chance).
- G3 (N=16384, K1=167/K2=3373 first-natural, d=0.90): pooled mismatch 0.770302 vs ceiling
  0.769312 → `SCLW_STOP_SANITY_HIGH`, the **second** ceiling-hugging operating point. The
  list arm's path-survival 0.0 at all L is wiring-only (unfrozen stub), not an SCL negative.
- X17 positive control P=0.000 exact 4/4 proves decodability under control conditions only;
  corrected full-scale C ≈ chance (0.76318/0.96103) does not prove sub-threshold — causes
  undistinguished, but at either tested point the SCL-unlock question is unanswerable.

Reading: at first-natural disclosure placement, disclosure AMOUNT is spent
(K2/N ≈ 20.6%) yet produces no measurable bite at either channel strength. Placement and
structure of disclosure — not merely its size — are implicated.

## Why redesign L2 representation / disclosure placement rather than add N (strategy stop rule)

1. **The stop rule is recorded, not chosen here.** The Tier-X re-analysis queue hit its cap
   (Q1–Q4 used, 4/6), which FORCES the exhaustion-route return (operating-point redesign /
   data acquisition / closeout); the user selected operating-point redesign (Route B,
   2026-09-20). This change executes that choice.
2. **Adding N is a proven-pointless axis.** Every scale already tested hugs its own
   no-information ceiling: N=256 (X14 flat, X15 d=0.75 — sharpening the channel moved mismatch
   ~0.0002), N=16384 (G3, d=0.90), N=32768 (X16, d=0.75). Scale × current representation is
   not the binding constraint; re-asking survival at any new N with the same first-natural
   disclosure and the same model repeats the proven-pointless pattern.
3. **The real-data N ladder is exhausted by population, not by verdict.** Zero full N=32768
   blocks remain (133 frames never-decoded); the N=8192 probe consumed the 2M HOLD tail's one
   formable block; nothing formable remains under any authorized rule. A larger-N real-data
   ask has no population and cannot be authorized here.
4. **The X14→X17/G3 closeout consequence names the legitimate axes**: disclosure
   placement/amount, channel strength, or the list-decoding question itself — i.e., the
   representation/placement redesign, exactly this change's scope.

## Scope of this scoping

This change produces ONLY:

1. This `proposal.md` (problem + why-redesign + honest scope).
2. `design.md` (ranked redesign axes; synthetic working-point rules incl. the
   differ-from-all-proven-pointless requirement and ceiling-margin arithmetic; decision
   procedure with per-axis probe budget; gate sequence; SCL-track interaction — every gate
   NOT AUTHORIZED).
3. `tasks.md` (ordered B1..B8 mirroring the gate sequence, all unchecked, all
   `[GATE — NOT AUTHORIZED]`).
4. Packet skeleton `.workbuddy/queue/NBPOLAR-L2-REPRESENTATION-REDESIGN/` with `STATUS.yaml`
   (state `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`, all counters 0) + `SCOPING_NOTES.md`
   (no-contact statement; Q5 activation note with one-line prereg sketch; seed hygiene).
5. Seed/tag hygiene: fresh band 2026092600..2026092619 proposed + grep-verified absent NOW
   (2026-09-20), recorded as reserved-but-unactivated.

## Honest scope (binding)

- Descriptive, synthetic-only scoping. No unlock claim, no redesign claim, no performance
  claim is made by this scoping.
- **Cannot reopen the real-data gate**: no real-data execution, no protected opens (V25
  counts, parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`), no RN/P20 packet revisits;
  the 2M HOLD tail and all never-decoded remainders stay never-decoded.
- No FER / reliability / efficiency / branch-superiority claims inside this scoping.
- No working-point numbers frozen here (design gives selection rules and candidates, freeze
  confirms); no L values, no pruning thresholds, no SCL activation.
- No production-module merge; `sc.py` and all `formal_ir/nbpolar/` existing modules stay
  untouched; disclosure placement/amount is a caller-side truth-injection choice only.
- No inherited NB-LDPC graph route, Cascade route, or binary Polar baseline logic is
  promoted (AGENTS.md §0); the D-series/V-series history is cited as read-only context only.
- Prior rule unchanged: raw-count MLE + 1e-15 floor for target-channel priors; λ stays
  control-arm only (X08 disposition).

## Impact scope

- New: `openspec/changes/l2-representation-redesign/` (proposal/design/tasks).
- New: `.workbuddy/queue/NBPOLAR-L2-REPRESENTATION-REDESIGN/` (STATUS.yaml + SCOPING_NOTES.md).
- Read-only inventory: decision-log tail (X14–X17, G3, Q1–Q4, P20S–P20T, RN entries),
  `NBPOLAR-SCL-SYNTHETIC-GATE/FREEZE_DRAFT.md` §§1–3, X16 packet prereg, AGENT_PROJECT_MEMORY
  L2 evidence lines. No other file created or modified.

## Acceptance criteria (for this scoping)

- [ ] proposal/design/tasks exist under the new change dir and encode the strategy stop rule
      and the honest-scope boundaries above.
- [ ] Design enumerates the redesign axes explicitly, ranks them, and names the
      minimum-delta candidate(s) with the differ-from-all-proven-pointless proof.
- [ ] Design states the ceiling-margin arithmetic requirement (rule + derived candidate band,
      marked PROPOSED, values frozen at freeze).
- [ ] Design states the decision procedure (informativeness/knee rules, per-axis probe budget
      ≤ 2 before forced axis switch, retirement and forced exhaustion-route return).
- [ ] Design states the gate sequence with every gate NOT AUTHORIZED, and the SCL-track
      interaction (SCL stays locked; no automatic promotion).
- [ ] tasks.md B1..B8 all unchecked, all `[GATE — NOT AUTHORIZED]`.
- [ ] Packet skeleton present with locked state + zero counters + no-contact statement.
- [ ] Q5 activation note present in SCOPING_NOTES with a one-line prereg sketch (not a frozen
      prereg).
- [ ] Fresh seed band 2026092600..2026092619 grep-verified absent NOW and recorded
      reserved-but-unactivated.
