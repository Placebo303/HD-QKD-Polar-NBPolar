# Design: NB-Polar prior re-baseline

All evidence below is Tier-X descriptive/non-claim (S8/S9/S10, seeds
20260920/2026092101/2026092117). S9 is synthetic-only with n=16 (wide CIs)
and pro-±1 ground truth by design. Nothing here is FER/efficiency evidence.

## D1 — Prior form: M2 (per-session ±1) is the default

M2 (2 params/session: q0, q±1 over delta ∈ {0,+1,−1}, rest → floor) beats
M0 by 0.0366/0.0442 bits/symbol held-out NLL and is the S9 decode vehicle
(11/16 vs 0/16 paired, frozen P16 construction). M1 (pooled, 2 params
global) matches M2 within −4.55e-05/−1.24e-06 bits — but only while both
sources share delay sign, and S8's M1 subsample rows are per-session refits
(carrying a 0.42%/0.03% pooled-vs-per-session mismatch floor), so "M1 ≈ M2"
does not validate pooled-CAL logistics. M2 isolates per-source
delay/offset risk at identical parametric cost; M3 adds nothing and M4
(2048 params) reproduces M0 bit-for-bit with M0's 1024-frame CAL minimum —
a STRUCTURAL identity (with counts on three positions the per-column
estimator IS the full MLE), which shows only that an UNREGULARISED
per-column estimator does not solve sparsity; it does NOT show that
per-column structure is valueless (a properly shrunk per-column model is
untested).
M1 becomes the candidate only if a CAL must pool sessions whose
per-session frames fall below M2's fitting floor AND all pooled sources
share verified delay sign. M1 is forbidden the moment a delay-−50 (or any
sign-distinct) source enters CAL.

## D2 — CAL size: preregister 32 sacrificed frames per session (candidate budget)

S8 M2 1%-H minima are 7.8/2.0 frames (1p5M/2M) on a single-draw,
non-monotone grid — a first-sub-threshold readout, not a stability proof
(M2-1p5M reads 0.769% at n=2000 but 1.686% at n=5000). CAL=32 frames
(8192 symbols) is a candidate budget with ~4× margin over the worst
observed 8-frame need, at 32768 bits ≈ 0.25× a block (4 bits/symbol
assumed), vs the incumbent 8× — it buys no guaranteed ≤1% H error:
ideal-iid SE at 8192 is already ≈1.0% of H2 and the two SE estimators
disagree ~2.2×. Floor: never below 8 frames without a new
freeze. 0.1% accuracy is neither bought (M2 0.1% hits grid max on 1p5M)
nor required for the decode-validation gate.

## D3 — Accounting: sacrifice the CAL; no λ_prior term; claim scope fixed

Adopt (a) only: the 32-frame CAL is excluded from the key denominator and
recorded per packet. Reveal-bits (~18–22 bits, order-of-magnitude
params·log2(n) bound, NOT a composable proof) are reported as a diagnostic,
never added as a λ_prior term. Release charges 0 bits because it estimates
in-sample — but that imports reuse bias, which Release handles by labeling
(`public_ec_only_not_secure`, `composable_security_claim_flag=0`) rather
than charging; NB-Polar keeps the small CAL because at ~0.25× a block the
cost is negligible and reuse bias is avoided. Claim scope is unchanged: no
composable net-key claim; Müller 2025 eq (11)/(13) with H(q) → empirical
H(X|Y) stays a preregister-before-use rule, never applied post-hoc.

## D4 — K allocation: re-split from the new H1/H2; f-vs-K_total choice deferred

(K1,K2) are re-derived from the
M2 tables via the accepted `select_empirical_split` semantics (16
synthetic TRAIN blocks) — the H-proportional descriptive split in the
S6/S8 tables SHALL NOT select construction K. Fixed-f and fixed-K_total
cannot both hold under M2's H_total: f=1.3 ⇒ K_total 7053/7106 (+33/+26
vs current 7020/7080); freezing K_total ⇒ f=1.2939/1.2952. Neither is
frozen here — the K_total choice is a separate later preregistered
decision. G2 freezes K1=319/K2=6492 regardless of that choice. P19
`l2_plus` (+512 to K2) already failed 0/3, so an increase is falsified and
only rebalancing is a candidate. The old L1-f≈2.00/L2-f≈1.275 mis-split is
expected to move, but the new numbers come from the frozen selector, not
from hand arithmetic on the finding.

## D5 — Construction: keep frozen P16 order for the first packet

S9 arm B (M2 + frozen P16) vs arm C (M2 + rederived) differ by 2 blocks
inside overlapping CIs (0.444–0.858 vs 0.570–0.934) ⇒ re-derivation is
unnecessary for safety, so the first real-data M2 packet reuses the frozen
P16 order (minimal change, arm-B path). The order is then suboptimal for
the new channel (TRAIN residual 0.132 frozen vs 0.0001 rederived) — that
optimality gap is recorded, and re-derivation is deferred to its own
freeze gated on arm-B success, not this change.

## D6 — Validation gates (all must pass before anything claim-bearing)

G1: real-data held-out NLL replication (M2 vs M0, preregistered split and
seed, descriptive). G2: one-shot Tier-Y real-data decode packet at frozen
K1=319/K2=6492 on already-accepted blocks first — independent Pre-EXECUTE
and Pre-RESULT reviews, `undetected` isolated, disclosure recount. G3:
independent-session confirmation before any FER/efficiency reading. G4:
exhaustive public-message inventory (Release pattern) with the CAL frames
listed. S9 must never be cited as FER/efficiency evidence. Stage 3
measurement set (preregistered cap, per-block λ decomposition) is required
before any claim-bearing statement.

## D7 — What stays frozen (do not reopen)

Phase 0–1 (GF32 poly 37, alpha=2, row-vector, natural order, butterfly);
Phase 2 `sc.py` (consumes `logp(N,q)`, agnostic to prior form/labeling);
64-bit Toeplitz tag, disclosure counting, `undetected` isolation; data
registries and frozen-session derived artifacts; P16/P17/P20 accepted
packets and every negative result (P13/P14/P15 NOT_CONFIRMED, P19 0/3
`l2_plus`, M4≡M0, split-rebalance non-recommendation) as history; the
V25-source identity finding; the S2/S4 findings (54.8σ margin as stated;
H2 bias small with sign NOT established — MM ADDS, corrected H2
0.8026903611/0.8089106006, MM +0.29%/+0.25% vs split-half −0.31%/−0.28%
opposite signs and comparable magnitude, so this is NOT a refutation of
H2 misestimation; `2^(H2/SER)` heuristic ban).

## Data-flow change

Old: CAL frames → `counts_ab` (1024×1024) → λ-concentration/`LAMBDA_STAR`
→ 1e-15 floor tables → `derive_p1`/`derive_p2`.
New: CAL frames (32, sacrificed) → per-session (q0,q+,q−) triple →
model-implied full 1024×1024 P(A|B) → 1e-15 floor + per-B-column renorm →
unchanged `derive_p1`/`derive_p2` → unchanged `SymbolMetric logp(N,q)` →
unchanged `sc.py`. Only the estimator box changes; every interface keeps
its shape, axis contract, and tolerance.

## Risk register

R1: S9 ground truth (q_rest=0) is correctly specified for M2 — it ranks
M0-vs-M2 LLR pathology only, not M2 vs other smoothers. R2: n=16 CIs are
wide; G2/G3 exist for this reason. R3: S8 CAL minima are single-draw and
non-monotone; D2's 4× margin covers this. R4: S10 ran on inherited
offset −50, which the PI auto-alignment ruling forbids inheriting — S10
usability maps are conditional until re-paired. R5: all "×a block" ratios
assume 4 bits/symbol net key (unmeasured). R6: pooled-CAL logistics are
untested (S8 `m1_row_note`); D1's M1 conditions guard this.
