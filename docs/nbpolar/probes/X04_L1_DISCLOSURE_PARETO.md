# X04 — L1 disclosure Pareto probe (Tier X)

Question: at the accepted dependent-L2 synthetic point, how much additional
L1 disclosure is required to remove the hard-L1 bottleneck, and is a later
adaptive L1 ladder worth implementing before any soft-APP/SCL work?

## Frozen design

- GF32, polynomial 37, alpha 2, natural SC order, N=256.
- `epsilon1=0.05`; strong dependent profile
  `epsilon2(u1)=0.02+0.36*u1/31`; fixed `K2=140`.
- Worst-first L1 disclosure prefixes at
  `K1 in [45, 52, 60, 72, 88, 112]`. Every larger set must be an exact nested
  extension of the preceding set from the same analytic order.
- Five fresh probe-only streams `2026091510..2026091514`, 128 common blocks per
  stream. Public tag master is `stream+10000`.
- Reuse the accepted P5/X03b sampler, P1/P2 construction, L2 hard-candidate
  conditioning, tag verification and outcome taxonomy unchanged.
- For every shared block and K1, run:
  1. `hard`: L1 candidate-conditioned L2 and final label
     `low_hat_hard + 32*high_hat`;
  2. `oracle-L2-control`: the same decoded L1 candidate and L1 disclosure, but
     L2 conditioned on `high_true` with final label
     `low_hat_oracle + 32*high_true`.

Alice truth is permitted only for disclosed values, scoring, sampling and the
explicit oracle control. It must not enter the hard arm's undisclosed L1
metric/decision, L2 metric/decision, label or tag decision.

## Required measurements

Persist one scalar record per `(stream, block, K1)` with K1, L1 exact flag,
hard/oracle outcome and exact flags, paired cell, L1/L2 disclosure bits,
tag/public-control counts, truth-isolation flags and resource/error class.
Persist no symbol vectors, decoded vectors, labels, tags or raw seed material.

Report per stream and pooled for every K1:

- L1 exact, hard end-to-end exact and oracle-control exact counts/rates;
- hard-vs-oracle four-cell table;
- among blocks wrong at K1=45, the cumulative number first recovered at each
  later K1; assert this first-recovery histogram is disjoint and exhaustive;
- regressions between adjacent nested K1 values (report, do not hide);
- key-dependent disclosure per fully invoked arm
  `5*(K1+140)+64`, plus total/mean disclosure;
- planning-only `f_surrogate = disclosed_bits/(256*(H1+H2))` using the exact
  frozen strong-model entropy derived by the same table code; label it neither
  real-channel efficiency nor project qualification evidence;
- undetected, nonfinite, decode failure, resource abort, transcript recount and
  truth-isolation violations;
- wall time and peak RSS when available.

Do not choose a winner or threshold. The intended downstream decision is only
whether the measured Pareto curve supports (a) a hard-L1 adaptive disclosure
ladder, or (b) skipping hard-L1 refinement and opening a separately specified
soft/list hypothesis.

## Execution and review contract

Before any decoder call, write `prereg.md` containing the full executable body.
Write exactly `prereg.md` and `results.json` under
`workspace/probes/nbpolar_x04_l1_disclosure_pareto/`. One execution is planned;
record any execution error and do not change the frozen grid/model/streams in a
retry.

An independent reviewer-go focused review must recompute all aggregates and
accounting from scalar records, verify nested disclosure sets, reconstruct one
complete stream, and audit the hard/oracle truth boundary. Its reported checks
are trusted under AGENTS.md section 4.1.

This is Tier X: no threshold, pass/fail, candidate/accepted token, scientific
attempt, production edit, artifact/real data, old-root modification,
APP/SCL/FWHT, qualification/promotion, per-probe decision-log/index/memory
update, commit or push.
