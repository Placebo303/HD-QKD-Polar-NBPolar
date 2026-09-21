# NB-Polar Phase 4-P0 specification delta

> **PARTIALLY SUPERSEDED (2026-09-21)** — The following are superseded by
> `openspec/changes/nbpolar-prior-rebaseline/` (±1 parametric prior) for
> all future evidence (the new change's delta supersedes them; this text
> is untouched):
>   - Requirement "accepted concentration prior": the per-Bob-column
>     concentration-formula mandate
>     (`f[a,b]=(counts[a,b]+lambda*p_global[a])/(n_b[b]+lambda)`)
>   - Requirement "lifecycle and truth isolation": only the CAL-fit mandate
>     (CAL 262144 symbols fits counts/`lambda`); the truth-isolation
>     sentences (DEV/EVAL tuning bans, `VAL1726-1729` ban, oracle-helper
>     test-local rule) REMAIN IN FORCE
> Everything else in this document — "axis and packing honesty",
> "decoder-facing tensors", "SymbolMetric object", "validation gates",
> and the truth-isolation sentences above — REMAINS IN FORCE. Retained
> for provenance. Read `docs/nbpolar/STATE.md` first.

## Requirement: accepted concentration prior

The adapter SHALL compute the joint conditional with the per-Bob-column
concentration formula of `design.md` §1
(`p_global[a]`, `n_b[b]`, `f[a,b]=(counts[a,b]+lambda*p_global[a])/(n_b[b]+lambda)`).
Every `[Alice,Bob]` column SHALL sum to 1 within absolute 1e-12. Unseen Bob
columns SHALL equal `p_global`; zero-mass `(U1,B)` slices SHALL be uniform
1/32. The per-cell `counts+lam` twin
(`formal_ir/v72p2d5_gf32_rate_mother.py:build_f_model`,
`prepare_model_f_prior`) SHALL NOT be called for new evidence.

## Requirement: axis and packing honesty

Stored count/probability tables SHALL declare `[Alice,Bob]` vs
`[Bob,Alice]` at every boundary; the adapter SHALL transpose explicitly
where layouts differ (D5 `marginalize_f_to_p1` `[U1,B]` vs D4R2
`P_U1_given_B` `[B,U1]`). Symbol packing SHALL be `low=s&31`,
`high=(s>>5)&31`, `s=low+32*high` with `U1=high`, `U2=low`; it SHALL NOT
use GF(1024) field multiplication.

## Requirement: decoder-facing tensors

The adapter SHALL expose `P1[frame,i,a]=P(A_high=a|B_full)`,
oracle `P2_true[frame,i,a]=P(A_low=a|A_high_true,B_full)` (diagnostic only),
and candidate `P2_hat[frame,i,a]=P(A_low=a|A_high_hat_hard,B_full)`
(executable route), all in natural-U order with joint-Bob conditioning.
`conditioning` SHALL be the explicit `FULL_BOB_ONLY` enum; future context
SHALL require a new freeze.

## Requirement: SymbolMetric object

`SymbolMetric` SHALL be immutable with fields `logp float64[N,q]`,
`conditioning`, `provenance ∈ {PRIOR_ONLY, ORACLE_CONDITIONED,
CANDIDATE_CONDITIONED}`, `symbol_order 0..q-1`, `normalization =
LOGSUMEXP_ZERO`. Probability-to-log conversion SHALL map exact zero to
`-inf` and normalize rows to `logsumexp 0`. Floors SHALL be opt-in via a
separate helper, never silent. No SC conditional SHALL be labelled a
complete APP or fed to the legacy `q @ P` bridge.

## Requirement: lifecycle and truth isolation

CAL (1M, frames 702..1725, 262144 symbols) alone SHALL fit counts/`lambda`.
DEV (`DEV-FUTURE-DISJOINT`) MAY select one preregistered bounded floor and
diagnose candidate-L2. EVAL (`EVAL-SINGLE-USE-DISJOINT`) SHALL tune nothing.
`VAL1726-1729` and any held-out sample SHALL NOT enter construction,
smoothing, floor, or thresholds. Truth SHALL enter only the oracle
diagnostic and scoring; the oracle gather helper SHALL live in the test
file only and SHALL NOT be exported from `nbpolar/`.

## Requirement: validation gates

Gates V-P0-01–V-P0-12 of `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` §6 SHALL
hold with their stated oracles, tolerances (absolute max-error), failure
categories, first diagnostics, and blocking scopes before the claims they
guard. The held-out-CE acceptance threshold (V-P0-11) SHALL be frozen only
from CAL/DEV evidence, never in P0.
