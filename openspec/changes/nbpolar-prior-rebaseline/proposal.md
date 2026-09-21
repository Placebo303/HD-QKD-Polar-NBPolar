# NB-Polar prior re-baseline — proposal

## Status

`PLAN_CANDIDATE / IMPLEMENTATION_NOT_AUTHORIZED / EXECUTE_NOT_AUTHORIZED`.
Branch: `codex/nbpolar-phase0` (verified via `.git/HEAD`).
Planning artifacts only — no production code, no execution authorization.

## Goal

Replace the Phase 4-P0 nonparametric prior layer with a parametric ±1
prior, so the next real-data packet tests the Stage 1 leading hypothesis
instead of the disproven M0 floor regime.

## Problem

S8/S9 (Tier-X, descriptive/non-claim, split seed 20260920) converge on one
root cause: the incumbent M0 nonparametric table prices ~70% of sparse
rare (−1) cells at ~4e-18 after the 1e-15 floor, each costing ~48 bits of
spurious penalty, while a 2-parameter ±1 model prices them at the pooled
rate and wins held-out NLL by 0.037–0.044 bits/symbol (S8) and decodes
11/16 vs 0/16 paired on synthetic N=32768 blocks (S9). The M0 layer also
forces a 1024-frame CAL (≈8× a block of net key) and carries no
prior-estimation term in λ_total.

## Proposal

Adopt the per-session ±1 parametric prior (M2) as the new prior baseline:
CAL drops to a preregistered 32 sacrificed frames per session; K_total
stays on the frozen f=1.3 literal with the (K1,K2) split re-derived from
the new H1/H2 at constant total; the frozen P16 construction order is kept
for the first validation packet; claim scope does not change.

## Supersedes

1. The Phase 4-P0 prior contract (`docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`
   §1): `counts_ab` nonparametric `f[a,b]=(counts+λ·p_global)/(n_b+λ)` with
   `DECODER_FLOOR=1e-15` — replaced by the M2 parametric rule (`design.md`
   D1). Historical evidence built on it stands as record; no future
   evidence may use it.
2. The CAL/DEV/EVAL lifecycle built on it (CAL = 262,144 symbols = 1024
   frames) — replaced by the 32-frame sacrificed CAL (D2).
3. The disclosure K allocation (L1 f≈2.00 over-disclosed, L2 f≈1.275
   under-disclosed, total f≈1.2975) — replaced by the constant-total
   re-split rule from the new H1/H2 (D4).
4. The λ_total accounting with no prior-estimation term — replaced by
   explicit CAL-sacrifice accounting; no λ_prior term is added (D3).

## Scope

In: M2 prior definition, CAL procedure, accounting rule, K re-split rule,
construction freeze decision, validation gates, delta spec, coder task
list, and the `SECURITY_MODEL.md` CAL-note update.
Out: Phase 0–1 field/transform, Phase 2 `sc.py`, verification/accounting
primitives, data registries, frozen-session artifacts, any `.py`
implementation, any execution, any security/composability claim.

## Non-Goals

No decoder, construction, labeling, or protocol change; no FER/efficiency
claim; no reopening of any frozen negative result or accepted packet.

## Impact Scope

`openspec/changes/nbpolar-prior-rebaseline/` (new); future
`comparison_bench/.../formal_ir/nbpolar/prior.py` + focused tests (by coder,
not this change); `docs/SECURITY_MODEL.md` (CAL note only).
`docs/nbpolar/ROADMAP.md`, `CRITICAL_PATH.md`, `MACRO_PLAN_20260921.md`
need follow-up edits — flagged as conflicts below, not edited here.

## Affected specs

New delta `specs/nbpolar-prior-rebaseline/spec.md` superseding the
`nbpolar-phase4-p0` "accepted concentration prior" and "lifecycle"
requirements for all future evidence. Merged `openspec/specs/` carries no
NB-Polar prior requirement, so nothing there is modified.

## Acceptance Criteria

Independent review of this change passes; every §D1–D7 call is explicit;
all four Supersedes items name their replacement; coder tasks are gated
with no production-data execution authorized by this change.

## Source of truth

`docs/nbpolar/MACRO_PLAN_20260921.md` §9, `docs/decision-log.md`
2026-09-21 "Prior form is the converging root cause" entry,
`workspace/probes/nbpolar_s{8,9,10}_*/results.json` (descriptive only),
`docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` (superseded contract).

## Tasks

See `tasks.md`. This proposal authorizes no implementation or execution.
