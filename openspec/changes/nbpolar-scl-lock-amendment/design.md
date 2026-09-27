# Design: SCL Lock Amendment (proposal only — nothing authorized)

Status: **APPROVED by PI 2026-09-27 (T1 DECIDED)** — `tasks.md` T1 records
the PI's ruling on (i)-(v) below (D2 option (iii), CRC=16 bits, L∈{4,8,16},
D4 outcome bands as proposed) plus the main-thread's M=4 joint-candidate
implementation constraint. D1-D7 below remain the descriptive design record;
D5 (real-data separation) is unchanged and still binding.

~~Status: **draft — PENDING PI adjudication; grants no authorization; SCL
remains locked until PI approves.** Every decision below is a planner
proposal for the PI to accept, modify, or reject; none is frozen here.~~
(superseded 2026-09-27)

## D1 — Current lock, item-by-item status (as measured, verbatim-compatible)

| Item | Text (`REAL_DATA_FEASIBILITY_STRATEGY.md:117-121`) | Status | Evidence |
|---|---|---|---|
| (a) | true-L1-conditioned L2 recoverable at frozen candidate | **NOT MET (M0-era)** | P19 `true_l1_control` (oracle L1, K2=6492) 0/3 (`REAL_DATA_FEASIBILITY_STRATEGY.md:47`) |
| (b) | hard L1 is a material failure source | **NOT MET (M0-era)** | P20I/J/K +L1 disclosure variants recovered zero blocks (`docs/nbpolar/ROADMAP.md:21`, `docs/nbpolar/MACRO_PLAN_20260921.md:59`) |
| (c) | small preregistered list contains true L1 often enough | **UNKNOWN** | never measured at an informative point; `scl-synthetic-list-gate` G1-G6 all `NOT AUTHORIZED` |
| (d) | joint scoring, one coherent probability model, no evidence reuse | **NOT MET** | `scl.py` is single-layer (one `field`), no CRC, no joint L1+L2 metric |
| (e) | list width 1 == accepted SC | **MET** | `scl.py` docstring: "`L=1` reproduces `sc_decode` bit-identically" |

(a)/(b) were measured under the **M0 prior**, before the M2 rebaseline. They
are not re-litigated by this proposal, only flagged as measured-under-a-
superseded-prior — see D2.

## D2 — Why (a)/(b) are stale under M2

M0-era P19/P20 diagnostics used the pre-rebaseline prior. Under the current
**M2 prior**, the same real-data contract (K1=319, K2=6492, frozen since G2)
produced:

- G2: 11/14 blocks recovered (`.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/G2_ADJUDICATION.md`)
- G3: 8/14 blocks recovered on an independent confirmation sample
  (`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md`)

This does not itself satisfy (a) or (b) — no true-L1-control diagnostic has
been re-run under M2 — but it means the M0-era 0/3 cannot be cited as current
evidence that hard L1 is immaterial or that L1-conditioned L2 is unrecoverable.
**Proposed PI options**: (i) require a true-L1-control re-run under M2 before
any SCL discussion continues, (ii) accept the synthetic gate below as a
parallel, faster-turnaround substitute for (a)/(b), or (iii) both, in either
order. This design does not pick an option.

## D3 — The new synthetic separating point (`op-n32k-matched`)

`workspace/probes/op-n32k-matched/results.json` (Tier-X, one-shot,
`FOCUSED_REVIEW` `PASS_WITH_COMMENTS`), channel = `G1R2-matched@q1024`
(delta pmf fit from the real CAL32 G1R2 triple, `sign_fix` already the
correct `table[a,b]=pmf[(b-a)%Q]` convention — **not** one of the 15
2026-09-27 `INVALIDATED_BY_TABLE_SIGN_DEFECT_20260927` entries):

| f_book target | k1 share | operational exact | oracle exact |
|---|---|---|---|
| ≈1.15 | 0.02 – 0.14 | 0/16 across all four shares | 0–5/16 |
| ≈1.20 | 0.0469 | **10/16** | **13/16** |
| ≈1.30 | 0.0469 | **13/16** | 16/16 |

This is the first point in this project's synthetic record where SC and
oracle separate on a channel matched to real-data statistics — the exact
prerequisite `scl-synthetic-list-gate` design §(a) asked for and never
reached. It is still descriptive Tier-X: no FER/efficiency/reliability claim,
and it sits far below the M-usable bar (FER Wilson-upper ≤0.02 **and**
f_eff ≤1.20, `FUTURE_DIRECTION_PLAN_20260924.md:139-144`) — SC's best point in
this grid (f≈1.20-1.30) is not close to that bar.

## D4 — Proposed replacement gate (values are PI-adjudicable, not frozen)

Replace lock items (a)/(b) with a scoreboard-style Tier-X measurement:

- **Channel**: unchanged `G1R2-matched@q1024`, N=32768, explicit `1e-15`
  floor carried per the A2 review comment on `op-n32k-matched`.
- **Working point**: f_book=1.20, k1 share=4.69% (`T6421_k1_301_k2_6120`) —
  the point already showing the largest non-degenerate SC/oracle gap (10/16
  vs 13/16) without being at either ceiling or floor.
- **Decoder**: `scl_decode` (existing interface, unmodified signature) with
  L ∈ {4, 8, 16} — **proposed** ladder, not re-derived from a survival curve
  here; PI may require the `scl-synthetic-list-gate` design §(b) ladder
  procedure instead before freezing L.
- **CRC**: a CRC-aided path-selection tie-breaker added on top of the
  existing path-metric ranking. CRC length is a PI decision (design proposes
  16 bits as a starting anchor, counted as disclosure toward `f_book`,
  consistent with C10-style disclosure accounting in
  `nbpolar-r2-fer-measurement-contract`). No CRC value is frozen by this
  design.
- **Joint L1+L2 scoring**: extends the current single-`field` `scl_decode`
  to score both layers under one coherent probability model in a single path
  metric (satisfies (d)); this requires a new code path, not a parameter —
  implementation is task T2, gated on PI acceptance of this proposal, not
  authorized here.
- **L=1 identity**: retained as a mandatory regression check (satisfies (e)).

### Pre-written decision outcomes (frozen at freeze time if PI accepts)

| Outcome | Condition | Consequence |
|---|---|---|
| Unlock-for-real-data-candidate | L=16 operational ≥ 15/16 at f≈1.20, oracle-consistent (no operational-exceeds-oracle anomaly) | SCL becomes a real-data **candidate**; still requires its own Tier-Y freeze (D5) before any real-data touch |
| List-decoding insufficient | L=16 operational ≤ 12/16 | Close this gate; pivot effort to L2 construction/N per the standing L2-first route |
| In-between | 12/16 < L=16 operational < 15/16 | One bounded follow-up (more blocks at the same point, same L-ladder) — no tuning, no parameter change |

These bands are proposed, not frozen; PI may adjust the numeric edges.

## D5 — Real-data Tier-Y separation (unchanged)

Nothing in D3/D4 authorizes any real-data SCL use. A real-data SCL attempt
remains its own Tier-Y decision gate: explicit user authorization, frozen
thresholds, one-shot attempt, independent Pre-EXECUTE and Pre-RESULT review,
main-thread acceptance (AGENTS.md §10.4). This amendment, even if the PI
accepts it in full, produces at most a synthetic "candidate" signal — never
a real-data authorization.

## D6 — Relation to `scl-synthetic-list-gate`

This amendment does not replace `scl-synthetic-list-gate`; it proposes a
**concrete instantiation** of its unreached gate sequence (G0 proposal exists,
G1-G6 never authorized) using the working point that design's own §(a) rule
required. If the PI accepts this amendment, `scl-synthetic-list-gate`'s G1
(freeze review) is the next applicable step for D4's frozen values, not a
new, separate track.

## D7 — What this design explicitly does not decide

No CRC length, no final L-ladder, no numeric outcome-band edges, no
acceptance of the M0-vs-M2 (a)/(b) re-measurement question (D2), and no
lifting of the current lock. All remain PI decisions per `tasks.md` T1.
