# NB-Polar prior re-baseline specification delta

Supersedes the `nbpolar-phase4-p0` "accepted concentration prior" and
"lifecycle and truth isolation" requirements for all future evidence. The
P0 contract document and all evidence built on it remain historical record.

## Requirement: parametric ±1 prior

The adapter SHALL fit a per-session triple (q0, q_plus1, q_minus1) over
delta ∈ {0,+1,−1} (2 free params/session) and SHALL expand it to the full
model-implied 1024×1024 P(A|B) before the 1e-15 floor and per-B-column
renorm. The nonparametric `counts_ab` raw-MLE table and the
λ-concentration formula SHALL NOT feed new evidence. Pooled (M1) fitting
SHALL require verified shared delay sign across all pooled sources (per
`design.md` D1 M1 candidacy conditions).

## Requirement: sacrificed small CAL

CAL SHALL be exactly 32 sacrificed frames (8192 symbols) per session,
excluded from key denominators and listed in the public-message inventory.
CAL SHALL never fall below 8 frames without a new freeze. Reveal-bits
(~params·log2(n) order-of-magnitude) SHALL be reported as a diagnostic and
SHALL NOT enter λ_total. In-sample key-data estimation of the prior is
forbidden as the default path.

## Requirement: deferred K re-split (fixed-f vs fixed-K decision pending)

The fixed-f vs fixed-K_total choice is DEFERRED to a separate later
preregistered decision (D4, `design.md` D4) — neither branch is frozen here;
the D4 recomputation record is report-only planning input. G2/G3 SHALL stay
at the frozen allocation K1=319/K2=6492 regardless of that choice. When the
later decision fires, (K1,K2) SHALL be re-derived from the M2 tables by the
accepted `select_empirical_split` selector; disclosure increases are
forbidden (P19 `l2_plus` failed 0/3). The H-proportional descriptive split
SHALL NOT select construction K.

## Requirement: construction freeze for first validation

The first real-data M2 packet SHALL reuse the frozen P16 order at
K1=319/K2=6492 (arm-B path). Re-derivation under M2 SHALL require its own
freeze gated on arm-B success.

## Requirement: decoder and verification boundary

`sc.py`, the 64-bit Toeplitz tag, disclosure counting, and `undetected`
isolation (never merged into success/FER) SHALL remain unchanged. The
adapter SHALL preserve `SymbolMetric` shapes, axis contracts, and
tolerances (frozen tolerances per `tasks.md` Acceptance; interfaces per
`design.md` Data-flow change); the oracle gather helper SHALL stay test-local.

## Requirement: validation gates

No FER/efficiency/qualification claim SHALL precede G1 (real-data held-out
NLL replication) + G2 (one-shot Tier-Y decode packet with independent
Pre-EXECUTE/Pre-RESULT reviews) + G3 (independent-session confirmation) +
G4 (exhaustive public-message inventory, Release pattern, with the CAL
frames listed; `design.md` D6) + the Stage-3 measurement set (preregistered
cap, per-block λ decomposition; `design.md` D6) before any claim-bearing
statement. S9 (synthetic, n=16, pro-M2 ground truth) SHALL never be cited as
FER/efficiency evidence.
