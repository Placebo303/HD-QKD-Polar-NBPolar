# Change Proposal: nbpolar-scl-lock-amendment

Status: **APPROVED by PI 2026-09-27 (T1 DECIDED)** — see `tasks.md` T1 for
the ruling (i)-(v), the M=4 joint-candidate implementation constraint, and
`docs/decision-log.md` 2026-09-27 "PI 裁决三项" entry. The synthetic
scoreboard gate replaces lock items (a)/(b) for the **synthetic Tier-X scope
only**; real-data SCL use stays locked (D5, unchanged).

~~Status: **draft — PENDING PI adjudication; grants no authorization; SCL
remains locked until PI approves**~~ (superseded 2026-09-27)

## Problem

The SCL entry gate (`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md:113-123`)
requires all five conjunctive items before L1 SCL may start: (a) true-L1-
conditioned L2 recoverable at the frozen candidate; (b) hard L1 is a material
failure source; (c) a small preregistered list contains true L1 often enough;
(d) joint scoring, one coherent probability model, no evidence reuse; (e) list
width 1 == accepted SC.

Measured status (detail + citations in `design.md` D1): **(a)/(b) NOT MET**
under the M0-era P19/P20 diagnostics (0/3 with true L1 disclosed; +L1
disclosure variants recovered zero blocks); **(c) UNKNOWN** (never measured
at an informative point); **(d) NOT MET** (`scl.py` is single-layer, no CRC,
no joint L1+L2 metric); **(e) MET** (`scl.py` documents `L=1` as bit-identical
to `sc_decode`). The `scl-synthetic-list-gate` design's own prerequisite — a
synthetic point where SC and list separate — was never reached (G0 only;
G1-G6 `NOT AUTHORIZED`).

## Why amend

The (a)/(b) measurements are M0-era. Under the current **M2 prior**, the same
K1=319/K2=6492 contract recovers 11/14 (G2) and 8/14 (G3) blocks — a
materially different regime than the M0-era 0/3 (design D2). They should not
be treated as settled under M2 without re-measurement.

A synthetic SC-vs-oracle separating point that the `scl-synthetic-list-gate`
design required but never reached now exists:
`workspace/probes/op-n32k-matched/results.json` (Tier-X, `FOCUSED_REVIEW`
`PASS_WITH_COMMENTS`), channel matched to the real G1R2 CAL32 triple,
N=32768. At f_book≈1.20, k1 share 4.69%: operational 10/16, oracle 13/16; at
f_book≈1.30, same share: operational 13/16 (design D3). Still far below the
proposed M-usable bar (FER Wilson-upper ≤0.02 **and** f_eff ≤1.20).

A 2026-09-27 defect (`docs/decision-log.md`, "合成两层 GF32 探针 table 符号缺陷
确认") withdrew 15 earlier Tier-X synthetic two-layer results as
`INVALIDATED_BY_TABLE_SIGN_DEFECT_20260927`. Real-data M2 is unaffected.
`op-n32k-matched` is **not** in the withdrawn list — its `sign_fix` field is
already the correct convention — so the separating-point evidence stands.

## Proposed replacement gate (for PI to accept, modify, or reject)

Replace (a)/(b) with a synthetic scoreboard gate
(`FUTURE_DIRECTION_PLAN_20260924.md:345`) on the matched channel (explicit
1e-15 floor), N=32768, f_book=1.20, k1 share 4.69%: SCL with L ∈ {4,8,16},
CRC-aided (length fixed in `design.md` D4, counted as disclosure), joint
L1+L2 path metric under one coherent probability model (satisfies d), L=1
identity retained (satisfies e). Pre-written outcomes (design D4):
unlock-for-real-data-candidate if L=16 operational ≥15/16 at f≈1.20,
oracle-consistent; list-decoding-insufficient if L=16 ≤12/16 (pivot to
construction/N); otherwise one bounded follow-up, no tuning. Real-data SCL
use stays a separate Tier-Y gate with its own freeze and authorization.

## Scope — IN / OUT

IN: this proposal + `design.md` + `tasks.md`; citation-only account of (a)-(e)
status, M0→M2 context, the separating point, and the sign-defect scope note;
a concrete, PI-adjudicable replacement-gate design — proposed, not frozen.
OUT: any code change to `scl.py` or any other production module; any
execution (Tier-X or Tier-Y), synthetic or real; any removal or weakening of
the current lock text before PI adjudication; any real-data acquisition,
decode, or FER/efficiency claim.

## Affected specs / inputs (read-only citations, nothing modified)

`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md:113-123`;
`openspec/changes/scl-synthetic-list-gate/`; `.../formal_ir/nbpolar/scl.py`;
G2/G3 adjudications; `op-n32k-matched` probe + `FOCUSED_REVIEW`;
`docs/nbpolar/FUTURE_DIRECTION_PLAN_20260924.md:139-144,345`;
`docs/decision-log.md` 2026-09-27 sign-defect entry.

## PI rulings needed (planning input only; no self-adjudication)

Accept / modify / reject the replacement gate; CRC length; the L ∈ {4,8,16}
ladder; the pre-written outcome thresholds; whether (a)/(b) should be
re-measured under M2 before or instead of the synthetic gate.
