# NB-Polar Phase 4-P5 specification delta

Phase 4-P5 is the powered paired Tier-Y gate at the X02-recommended dependent-L2
operating point: one synthetic N=256 statistic that asks whether a hard-L1
candidate conditioning penalty is material, using the accepted P4 two-layer
runner in memory.  It is a mechanism discriminator, not held-out real-data
reconciliation.  Implementation tasks live in the companion P5 section of
`tasks.md`; status, acceptance and route disposition are owned by the main
thread, never by the implementing session.

## Requirement: frozen dependent-L2 point and pre-decoder table guard

The gate SHALL run at exactly GF32 polynomial basis (primitive polynomial 37,
alpha 2, natural order), `N=256`, `epsilon1=0.05`, the strong dependent-L2
profile `epsilon2(u1) = 0.02 + 0.36*u1/31` over the high-layer source value
`u1` (mean exactly 0.20), `K1=45`, `K2=140`,
`D1 = sorted(analytic_order(0.05,256)[:45])`,
`D2 = sorted(analytic_order(0.20,256)[:140])`, stream seeds
`2026091470..2026091472` with 128 paired blocks each, and public tag master
`stream_seed + 10000`.  The injected `[Alice,Bob]` table SHALL be
`P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)` with a q=32 marked-erasure
kernel whose per-position erasure probability is the profile function of the
HIGH value, column-normalized to 1 within 1e-12 (asserted, never
renormalized).  Before any decoder call the gate SHALL compute
`p2_maxdiff = max_{u1,u1',b,u2} |P2[u1,b,u2] - P2[u1',b,u2]|` on the derived
`[U1,B,U2]` table and SHALL refuse to decode when it is below 0.30.

## Requirement: paired four-cell table and independent transcript recount

Every planned block SHALL be one `run_two_layer_block` call whose operational
and oracle arms share the block, the disclosures and the stream master; the
per-position `B_low` erasure mask SHALL use `epsilon2(high)` in the frozen draw
order (high, low, `B_high` mask + replacements, `B_low` mask + replacements).
Each pair SHALL be classified into exactly one of `both_exact`,
`oracle_only`, `operational_only` (operational exact and oracle not exact) or
`neither`, disjoint and exhaustive over the 384 planned pairs.  The gate SHALL
require `operational_only == 0`; that cell is structurally impossible when the
L1 candidate is correct because the operational `P2_hat` and oracle `P2_true`
gathers are then bitwise identical and both fresh L2 decodes receive identical
arguments.  Per fully invoked arm the key-dependent disclosure SHALL be
`5*(K1+K2) + 64 = 989` and each tag SHALL consume 2623 public control bits; an
independent literal transcript recount SHALL equal the incremental per-arm and
total totals with zero mismatch.

## Requirement: exact-binomial discriminator and outcome labels

The gate SHALL persist the observed values and the booleans for: oracle exact
`>= 365` of 384; `operational_only == 0`; and the one-sided 95% exact lower
bound `L` solving
`sum_{j=X}^{384} C(384,j) L^j (1-L)^(384-j) = 0.05` by monotone bisection over
`L in [0,1]` with `X` the oracle-only count, computed with stdlib `math` only
in log space, with frozen edge handling `X=0 -> L=0.0` and
`X=384 -> 0.05**(1/384)`.  A binomial interval SHALL NOT be applied to the
difference of the two marginal recovery rates.  The discriminator SHALL pass
iff all three conditions hold; at the frozen 384-pair shape the gate SHALL
return `HARD_L1_CONDITIONING_PENALTY_CANDIDATE` iff every integrity gate and
the discriminator pass, `HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED` iff
integrity passes and the discriminator fails, and otherwise `BLOCKED` with the
failing gate names in frozen order.

## Requirement: frozen CLI, five-file output and bounded scope

The CLI SHALL require `--n`, `--epsilon1`, `--profile`, `--k1`, `--k2`,
`--seeds` (one or more), `--blocks-per-seed` and `--out-dir` with no production
default; it SHALL refuse an existing output root before any decoder call, SHALL
refuse the consumed seeds `2026091200..2026091213`, `2026091314..2026091321`,
`2026091330`, `2026091340`, `2026091341`, `2026091350`, `2026091351`,
`2026091360`, `2026091361`, and SHALL accept the frozen seeds.  The single
attempt SHALL be consumed at the first gate L1 SC call (stream 0, block 0); no
rerun, seed change, table/K/threshold/set change or partial credit is
permitted, and 2 GiB / 3600 s budgets apply.  The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/
paired_penalty_gate/` SHALL be absent before execution and SHALL contain
exactly five compact scalar-only files (`frozen_plan.json`,
`per_block_paired_outcomes.json`, `transcript_accounting.json`,
`aggregate_summary.json`, `report.md`); symbols, labels, disclosed values and
raw seed bits SHALL NOT be persisted.  All integrity gates (pairing coverage;
`p2_maxdiff >= 0.30`; candidate/oracle provenance complete; operational
truth-leak zero; undetected zero; nonfinite zero; resource-abort zero; four
cells disjoint/exhaustive; exact disclosures and zero transcript recount
mismatch; frozen attempt accounting) SHALL be persisted as booleans and SHALL
all pass before any candidate label is emitted.  The scope is synthetic only:
no stored data product, no real frame, no N>256, no scalable or list decoder
and no cross-layer soft path.

## Requirement: bounded claim

The only permitted conclusions are the two registered outcome labels and the
blocker return; a candidate means that the hard-L1 conditioning penalty signal
is material at this single synthetic point.  It SHALL NOT be described as
real-data FER, efficiency, leakage, key rate, qualification or promotion
evidence; operational-arm numbers are interface diagnostics.  An independent
Pre-EXECUTE review SHALL pass before the single attempt, and an independent
Pre-RESULT review SHALL pass before any result or label is published; neither
the run nor the implementing session may accept its own work.
