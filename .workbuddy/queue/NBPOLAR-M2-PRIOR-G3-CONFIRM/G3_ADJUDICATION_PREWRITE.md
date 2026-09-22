# G3 ADJUDICATION PREWRITE — NBPOLAR-M2-PRIOR-G3-CONFIRM

## §0 Header — purpose, date, no-authorization, no STATUS.yaml write

- **Purpose**: planning/semantics pre-write for the G3 (SHG `_2`, independent-session
  confirmation) verdict. It fixes the adjudication semantics **before** any G3-2 decode
  verdict is improvised, so nobody invents a verdict at night.
- **Date**: 2026-09-22. **Source of truth**: `docs/nbpolar/STATE.md` **§4.1** (the main
  thread's 2026-09-22 ruling). This file reproduces §4.1 faithfully and implements/corrects
  `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` §2 R0.1. Sibling precedents:
  `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/G2_ADJUDICATION.md` (three-state gate,
  `undetected` isolation, disclosure recount) and
  `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md` (negative-label
  precedent; failure layer named in the body).
- **Planning/semantics pre-write — grants NO authorization.** Decode (G3-2) remains gated
  on **G3-1 freeze + Pre-EXECUTE PASS + recorded authorization** (per `TASK_PACKET.md` §
  "Gate"/"Acceptance IDs"/"Stop rules" and `STATUS.yaml` ids G3-0…R2). Nothing in this file
  authorizes any read, run, or decode.
- **STATUS.yaml is NOT modified by this file.** The operator owns
  `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/STATUS.yaml` while in flight (read-only
  source here; do not write). Likewise untouched: `TASK_PACKET.md`, `PROMPT.md`,
  `AUTHORIZATION_PROMPT.md`, `scripts/m2_prior_validation.py`, anything under
  `comparison_bench/`, `src/`, `experiments/`, `tools/`, `results/`,
  `comparison_bench/outputs_comparison/`. No commit, no test run, no SHG `_2` read.

## §1 Three-state verdict table (exact status strings from STATE §4.1)

| Result | Status string |
|---|---|
| PASS — Wilson-lower(B) > Wilson-upper(A2), z = 1.96 | `NBPOLAR_M2_PRIOR_G3_SUCCESS` |
| FAIL / INCONCLUSIVE / premise-layer failure (execution clean) | `NBPOLAR_M2_PRIOR_G3_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`, with the failed layer named in the body, NOT a new label |
| Execution accident (`resource_abort` / invalid-run) | NO scientific label; freeze re-freeze rules apply; no rerun, no tuning |

Notes (STATE §4.1, verbatim in intent): the negative label is the G1-family
`…_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE` (grep-compatible with
`…_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`); there is NO independent `…_PREMISE_FAIL`
label — a premise-layer failure folds into the bounded-negative label with the layer named
in the body, exactly as G1's δ-tail premise FAIL did.

## §2 Layer definitions (each with the deciding arithmetic)

- **FAIL**: point(B) ≤ point(A2).
- **INCONCLUSIVE**: point(B) > point(A2) but Wilson CIs overlap; **or** EVAL yields
  < 14 complete blocks → `COMPLETE-BLOCKS-ONLY` ⇒ `INSUFFICIENT ⇒ INCONCLUSIVE`
  (never pad, never reuse, never shrink N).
- **Premise layer**: inherited `B_tail = 2.0e-4` or `Δ_min = 0.020` gate not met.
- **Denominator** is `g3_blocks` (target 14). **A1 has NO gate** (M0 at its own 1024
  sacrificed frames, descriptive only — recorded if the ledger allows, else dropped and
  recorded).
- Wilson rule: 95%, z = 1.96, same SUCCESS/FAIL/INCONCLUSIVE gate family inherited from
  SHG `_1`'s frozen contract (`contract_inherited_from_SHG_1.gates`).

## §3 Status consequence — every non-PASS leaves M2 at CANDIDATE

- Every non-PASS outcome (FAIL, INCONCLUSIVE, premise-layer failure with clean execution)
  leaves M2 at `CANDIDATE` — no promotion, no demotion; execution accidents change no state.
- The promotion ladder names `VALIDATED_AT_FROZEN_CONTRACT` **only for PASS**:
  `CANDIDATE → (G3 preregistered-gate PASS) VALIDATED_AT_FROZEN_CONTRACT → (R2 gate)
  FER_MEASURED_AT_CONTRACT → (R3 gate) EFFICIENCY_ACCOUNTED → (≥2 independent sessions +
  sample + G4 exhaustive public-message inventory + independent Pre-RESULT all-pass)
  READY_FOR_QUALIFICATION`.
- Quoting STATE §4.1: "禁止跳级 / 禁止用合成 S9 推级 / 禁止跨契约叙事推级"
  (no level-skipping; no promotion off synthetic S9; no promotion off cross-contract
  G1-w=500-vs-G1R2/G2-w=200 superiority narrative). Any FAIL or INCONCLUSIVE returns to
  CANDIDATE or BOUNDED_NEGATIVE.

## §4 What a PASS does NOT establish (discipline copied from G2 §3.3)

A `NBPOLAR_M2_PRIOR_G3_SUCCESS` does NOT establish:

- no FER-as-population estimate;
- no efficiency, qualification, promotion, or composable net-key claim;
- no claim that ±1 is "true" — q_rest = 0 remains a weak statement at a 32-frame CAL
  (zero-observation bound 3/8192 = 3.66e-4);
- no cross-contract superiority vs G1 (w=500/LINEAR bounded negative stands as its own
  bounded negative);
- and M2 is still not promoted until the ladder's later rungs (R2 FER, R3 efficiency,
  ≥2-session replication + G4 inventory + independent Pre-RESULT before
  READY_FOR_QUALIFICATION).

## §5 G3 participation disclosure (in every output)

Every G3 output must carry the participation-disclosure statement. G3's independence is
**decoder/model independence, NOT no-prior-contact independence** — quoting the packet's
recorded wording:

> "G3's independence is **decoder/model independence, NOT no-prior-contact independence**
> — that distinction must be stated in any G3 result."

Full context (packet § "SHG `_2` reservation + participation disclosure"): SHG `_2` is NOT
untouched history — the 2026-09-21 dual-rule census already ran decoder-free alignment
(σ = 114.4 ps), a full pairing grid, and (N)-200 `H_total = 0.816770` on it, and its cells
informed the W_P recommendation. Never done on SHG `_2`: prior fitting, any decoder run,
or M2 model selection. From G1 onward no G1/G2 preview, model selection, window choice or
pairing read touched SHG `_2`; G3's own Phase-A closure is the first permitted contact.

## §6 L2 domain rule (G2 Pre-RESULT diagnostic carried forward)

- Any "H-conditioned L2" / `nll_l2_*` reading MUST state whether conditioning is on the
  polar-transformed `views["u1"]` or the untransformed `high_hat`.
- `oracle_l2_exact` = 0 on all arms in G2 was a **domain mismatch, NOT a decoder fact**:
  the isolated oracle third SC call conditioned on `views["u1"]` (polar-transformed) while
  the frozen operational path conditions L2 on `high_hat` (untransformed high — the domain
  `derive_p2` is built in). Hence `oracle_l2_exact` 0/42 on all arms (even the 11 B-exact
  blocks) and the non-discriminative `nll_l2_trueH`/`nll_l2_candH` pair, while the
  operational hard-L2 path discriminated (B 11/14 vs A1/A2 0/14).
- The gate uses **only the frozen operational path + tag + label**; SUCCESS arithmetic is
  unaffected by the oracle-domain note. No re-derivation or re-run follows from this rule.

## §7 Taxonomy and accounting requirements for the G3 record

- Per-block taxonomy kept separate: `exact` / `verify_failed` / `decode_failed` /
  `resource_abort` / `undetected` (plus `nonfinite` where measured, as in G2).
- **`undetected` never merged into success or FER.** `undetected` = 0 must be isolated and
  reported as its own count (G2 precedent: 0/42 isolated), never folded into the success
  numerator or any FER denominator.
- Disclosure recount must match (G2 precedent: key/public bit totals = per-block × block
  count; tag count from `tag_master`; mismatch 0).
- `reruns: 0` — verdict ⇒ no rerun, no tuning, no seed/threshold/K/window/MOD change.
- Budget 900 s wall / 2 GiB RSS single-threaded (decode phase); `budget_aborted` recorded
  (G2 precedent: per-block wall min/mean/max + total ≤ 900, RSS ≤ 2 GiB,
  `budget_aborted: false`).

## §8 Precedence clause

Where this file and `TASK_PACKET.md` differ, **STATE §4.1 (main-thread ruling) wins**.
Report the difference rather than silently harmonizing — file the discrepancy in the G3-1
freeze review / operator return instead of smoothing it into the packet. (Known corrected
differences at pre-write time are listed in §10-adjacent "known deltas" of the return
cover, not silently merged here.)

## §9 Must be cited by the G3-1 freeze

The G3-1 freeze review **must confirm this file
(`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION_PREWRITE.md`) is present**
before any decode (G3-2). Absence ⇒ G3-1 freeze FAILs; decode stays gated. Cite path +
presence check in the freeze record alongside the Pre-EXECUTE PASS and recorded
authorization.
