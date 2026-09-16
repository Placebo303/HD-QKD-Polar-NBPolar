# NB-Polar Phase 4-P6 specification delta

Phase 4-P6 is the adaptive hard-L1 disclosure gate on top of the accepted P5
dependent-L2 point: one paired synthetic N=256 statistic that asks whether a
worst-first adaptive L1 disclosure ladder `[45,60,72,112]` preserves the static
`K1=112` endpoint's exact recovery while reducing mean key-dependent disclosure
by at least 15%.  It is a mechanism discriminator, not held-out real-data
reconciliation.  X04/X05 Tier-X planning probes are design inputs only; their
roots are read-only and unchanged.  Implementation tasks live in the companion
P6 section of `tasks.md`; status, acceptance and route disposition are owned by
the main thread, never by the implementing session.

## Requirement: frozen dependent-L2 point and nested disclosure schedule

The gate SHALL run at exactly GF32 polynomial basis (primitive polynomial 37,
alpha 2, natural order), `N=256`, `epsilon1=0.05`, the strong dependent-L2
profile `epsilon2(u1) = 0.02 + 0.36*u1/31` over the high-layer source value
`u1` (mean exactly 0.20), the analytic worst-first nested L1 prefixes
`K1 in [45,60,72,112]` with `D1(K1) = sorted(analytic_order(0.05,256)[:K1])`,
the fixed L2 prefix `K2=140` with
`D2 = sorted(analytic_order(0.20,256)[:140])`, stream seeds
`2026091550..2026091554` with 128 common blocks each (640 paired blocks), and
public Toeplitz master `stream_seed + 10000`, domain-separated per arm, block
and level.  The injected `[Alice,Bob]` table SHALL be the accepted
`P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)` strong-profile table
(column-normalized to 1 within 1e-12, asserted, never renormalized) with the
accepted pre-decoder `p2_maxdiff = 0.34875...` floor check.  The sets
`D1(45)`, `D1(60)`, `D1(72)`, `D1(112)` SHALL be exactly nested (each set is a
strict subset of the next) and `D2` SHALL be disclosed once per arm and block.
The frozen budget envelope is 2 GiB and 3600 s; one attempt is consumed at the
first scientific SC call.

## Requirement: static endpoint arm

The static arm SHALL, per block, make one fresh L1 SC call at `K1=112` on the
P1 metric (`PRIOR_ONLY`), one fresh candidate-conditioned L2 SC call at
`K2=140` on the P2 table gathered from Bob and the hard L1 candidate
(`CANDIDATE_CONDITIONED`), assemble the label `low_hat + 32*high_hat`, and emit
exactly one 64-bit Toeplitz verification tag.  Its outcome taxonomy SHALL be
the accepted two-layer one: `exact` (tag pass AND label equal to truth),
`undetected` (tag pass and not exact, never merged with exact),
`verify_failed` (tag mismatch), `decode_failed` (L1 or L2 SC exception or
nonfinite marginals; no tag), `resource_abort`.  The fully invoked static cost
is `5*(112+140)+64 = 1324` key-dependent bits.

## Requirement: adaptive hard-L1 arm

The adaptive arm SHALL, for each one-based stage `j` with `K1_j` in
`[45,60,72,112]`, restart the L1 SC from the ORIGINAL P1 metric with the
cumulative nested `D1(K1_j)` prefix, restart the candidate-conditioned L2 SC
from the ORIGINAL P2 table gathered by the current hard L1 candidate with the
same `D2`, and verify the full 10-bit label with one 64-bit tag under that
stage's level domain.  On tag match the arm SHALL accept and stop (`exact` iff
the label equals truth; tag pass and not exact is `undetected`, never merged
with exact).  On tag mismatch before `K1=112` the arm SHALL emit one public
one-bit feedback, disclose only the next D1 increment and advance; a mismatch at
`K1=112` is `verify_failed`.  A nonterminal `ImpossibleDisclosedValueError`
SHALL produce no candidate, no tag and one public feedback bit and advance; at
the terminal stage `K1=112` it is `decode_failed`.  All other exceptions SHALL
fail closed.  Decoder state, metrics, partial sums, candidate labels and tag
seeds SHALL NEVER be reused between stages (every stage calls a fresh SC on the
original metric).  Alice truth is allowed only for sampling, disclosed values,
tag construction and scoring; it SHALL NOT enter any undisclosed operational
metric, decision or tag seed.

## Requirement: frozen accounting, transcript recount and union bound

Per arm per block at the one-based termination/exhaustion stage `j` with
`K1=K_j`, the key-dependent disclosure SHALL be `5*(K_j+140) +
64*tag_invocations`, realized from actually executed disclosures (the
cumulative L1 prefix `5*K_j`, the once-per-arm/block L2 disclosure `5*140` when
L2 was invoked, and one `64`-bit tag per invocation); public seed bits SHALL be
`2623*tag_invocations`, feedback SHALL be one public bit per invocation, and
public control SHALL be seed bits plus feedback bits.  A decode rejection
(`ImpossibleDisclosedValueError` advance) SHALL create no tag.  The gate SHALL
persist an independent literal recount of the disclosure, tag and feedback
events per arm and in total and SHALL require zero mismatch against the
incremental totals.  The verification union bound SHALL be
`min(1.0, total_tag_invocations * 2^-64)`.

## Requirement: integrity gates, scientific gates and outcome labels

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be: 640/640 paired coverage; exact stream/block
identity; mutually exclusive and exhaustive result buckets for both arms;
exactly nested D1 sets and exactly one D2 disclosure per arm/block;
operational provenance (`PRIOR_ONLY` L1, `CANDIDATE_CONDITIONED` L2) and
truth-isolation sentinel complete; `undetected`, `nonfinite` and
`resource_abort` all zero; transcript recount mismatch zero; tag/feedback/
public-control accounting and union bound exact; wall/RSS within the frozen
limits; and attempt/seed accounting exact.  Scientific gates SHALL be: static
exact `>= 620/640`; adaptive exact equal to static exact; paired
`adaptive_only == 0` and `static_only == 0`; and the exact integer leakage
comparison `100*adaptive_total_key_dependent <= 85*static_total_key_dependent`.
The gate SHALL return `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` iff every
integrity and scientific gate is true,
`ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED` iff integrity passes and any
scientific gate fails, and otherwise `BLOCKED` with
`integrity_all_pass=false` and the failing gate names in frozen order (the
operator maps this to `BLOCKED(<earliest gate>)`).

## Requirement: frozen CLI, five-file output and bounded scope

The CLI SHALL require `--n`, `--epsilon1`, `--profile`, `--k1-levels`,
`--k2`, `--seeds`, `--blocks-per-seed` and `--out-dir` with no production
default; it SHALL refuse an existing output root before ANY decoder call and
SHALL refuse the consumed seeds `2026091200..2026091213`, `2026091314..2026091321`,
`2026091330`, `2026091340`, `2026091341`, `2026091350`, `2026091351`,
`2026091360`, `2026091361`, `2026091400..2026091404`, `2026091410..2026091414`,
`2026091420..2026091424`, `2026091430..2026091434`, `2026091450..2026091452`,
`2026091470..2026091472`, `2026091490..2026091494`, `2026091510..2026091514`,
and SHALL accept the frozen streams `2026091550..2026091554`.  No rerun, seed
change, model/K/threshold change or partial replacement is permitted.  The only
output root
`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
SHALL be absent before execution and SHALL contain exactly five compact
scalar-only files (`frozen_plan.json`, `per_block_paired_outcomes.json`,
`transcript_accounting.json`, `aggregate_summary.json`, `report.md`); symbols,
labels, disclosed values, decoded keys and raw seed bits SHALL NOT be
persisted.  The scope is synthetic only: no stored data product, no real frame,
no N>256, no scalable or list decoder, no cross-layer soft path, no learned
policy, no commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the two registered outcome labels and the
blocker return; a candidate means that the adaptive hard-L1 disclosure schedule
preserves static exact recovery with at least 15% lower key-dependent
disclosure at this single synthetic point.  It SHALL NOT be described as
real-data FER, reconciliation efficiency, leakage, key rate, qualification or
promotion evidence; undetected frames SHALL never be merged with exact frames,
and planning-only `f` is not real-channel efficiency.  An independent
Pre-EXECUTE review SHALL pass before the single attempt, and an independent
Pre-RESULT review SHALL pass before any result or label is published; neither
the run nor the implementing session may accept its own work.
