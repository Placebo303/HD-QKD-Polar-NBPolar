# Proposal: bounded operational k1 dose ramp at k2=550

## Why

The C1 Tier-X probe (`workspace/probes/l2-singlefactor-c1-k550/`, status
`DESCRIPTIVE_TIER_X_REVIEWED_WITH_LIMITATIONS`) and the earlier `k2-dose-ramp`
together establish a one-directional fact on the F4@q1024 + M2 two-layer GF32
SC path:

- the **oracle** branch is highly sensitive to the L2 information set and can
  reach 64/64 exact (C1 BASE);
- the **operational** branch is `verify_failed` on every measured point so far
  (C1: 0/64 at k1=10, k2=550; `k2-dose-ramp`: 0/32 at every k2 in
  {200,400,700,1024});
- **k1 (the L1 disclosure dose) has never been varied as a single factor in
  this new series** — `K1_FROZEN=10` throughout.

Per `AGENTS.md` §1.1, the informative next action is to locate the **first
breakpoint of the operational path** (is the L1 dose the bottleneck?), rather
than to repeat the already-observed "information set matters" conclusion on the
oracle branch.

## Scope

Prepare one new synthetic-only Tier-X probe: a **bounded 5-point single-factor
k1 dose ramp** at fixed `k2=550`, single arm (BASE).

- `k1 ∈ {10, 80, 160, 320, 450}` (five points, all inside one run).
- `k2 = 550` fixed; no fallback point.
- `d2 = worst_k(H2, 550)` — the same frozen BASE information set as C1.
- `d1 = worst_k(H1, k1)` — recomputed per grid point (the frozen family member
  that follows k1).
- 2 run seeds × 16 blocks = 32 blocks per point; single arm.

The packet reports descriptive counts only, **per k1 point**, plus
`key_dependent_bits` and wall/RSS. One result record, one-shot execution, no
automatic successor.

**k1 is a dose variable, not an efficiency claim.** Every k1 point is recorded
as a *bookkeeping-only dose diagnostic*; no point may be described as an
efficiency operating point.

## Boundaries

- No real/protected data or artifact access. The inherited runner's only
  external code dependency is the read-only `qkd_recon.polar_core` import from
  `/mnt/d/Code/qkd-reconciliation-lab/src`; no writes are made there. No
  original Polar baseline, `results/`, or `comparison_bench/outputs_comparison/`
  writes.
- No FER, efficiency, security, R2-sizing, construction-superiority,
  prior-attribution, or qualification claim. No significance wording and no
  H-label conclusion; probe-local L-H wording only.
- No fallback k1, extra samples, retuning, rerun, or follow-on candidate in
  this change.
- The C1 overlap/non-discriminating design gate is **not applicable** (single
  arm); the `undetected` isolation STOP and the budget STOP are **retained**.
- This change prepares OpenSpec, preregistration, runner, and packet only. The
  user has granted broad synthetic-work authorization; execution still awaits
  main-thread freeze review.
