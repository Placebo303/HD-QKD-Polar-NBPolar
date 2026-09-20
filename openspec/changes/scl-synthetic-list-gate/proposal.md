# Proposal: SCL Synthetic List Gate (scoping only)

## Status

`SCOPING_ONLY_NO_EXECUTION_AUTHORIZED` — design + tasks + packet skeleton only.
No implementation, no execution, no authorization granted by this change.

## Problem

The NB-Polar track is SC-only. The frozen greedy SC (`comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py`,
`sc_decode`, L=1) is the sole decoder, and the synthetic SCL-coverability line X14 -> X17
has closed as non-informative **at the tested operating points** (decision-log 2026-09-20
milestone + H2-v2 entries). The exact recorded ceilings:

- X14 (N=256, flat Dirichlet, K2_synth=52 undisclosed): pooled greedy-SC mismatch
  6946/7168 = 0.96903, vs chance 31/32 = 0.96875 (delta +0.00028). Q1 spike survival
  0.0 in every bin x L cell (reviewer: structural — spike = low-mass truth ranked by
  same-row mass). Q2 both arms at K/N = 52/256 (void).
- X15 (N=256, 0.75-diagonal structured channel, undisclosed): pooled mismatch
  0.9686279296875 (7935/8192), G1 [0.15, 0.90] violated -> `X15_STOP_SANITY_G1`.
  Sharpening the channel (0.75 diagonal vs recorded real f_max 0.3392 from X06 context)
  moved mismatch by ~0.0002 vs X14: channel structure moved nothing at the undisclosed point.
- X16 (N=32768, replayed 2M disclosure K1=334/K2=6746, X15-diagonal kept): pooled mismatch
  0.7690162658691406 vs derived no-information ceiling (1-6746/32768)*31/32 = 0.76931
  -> `X16_STOP_SANITY_G1_HIGH`. G2 0.99919 PASS (tables informative, SC path at chance).
- X17 (metric-feed audit): H-a probe-side U/X truth confusion confirmed and code-localized
  (X16 body.py:420 misnames X-domain high/low as u-truth; :448-449 feeds X values as U
  known_values; :465 scores U-output vs X-truth; production `two_layer.py:629-634` correct
  and untouched). Positive control P = 0.000 exact 4/4 in [0.00, 0.05] proves decodability
  under control conditions ONLY (not working-point evidence). Corrected full-scale C still
  at chance (focused review: 0.76318/0.96103; descriptive only). Qualified closeout: C at
  chance does NOT prove sub-threshold; causes undistinguished; synthetic-vs-real structure
  mismatch open (X17 FOCUSED_REVIEW adjudications 6/7 + citation guardrail).

So: greedy SC has no demonstrated correction handle at the probed synthetic points, the
decoder-free ranking machinery is vindicated (G2/P), and the question "does a small list
contain the true path at frozen-hazard spikes" is still unanswered anywhere informative.
That is the exact gap a separately-gated SCL track must fill — synthetically first.

## Why a list

Literature (bounded survey `.workbuddy/queue/LITERATURE-SCL-QARY-POLAR-SURVEY.md`, 10 papers +
2 abstract companions) says SCL-unlock is the literature-consistent move: q-ary SCL typically
needs smaller L than binary (Yuan & Steiner 2018 GF256 at L/4; Abbasi N=8192 GF16/L=8 ~=
GF4/L=32 ~= repetition/L=128), and reliability-gated splitting/pruning is a published winning
family (Zhang 2016 split-reduced; Chen 2017 critical-set; Peng 2021 IPSS-SCL; Yuan pruned-tree).
But the survey also records hard gaps: zero GF(32)-polar-SCL points, zero N>=8192 q-ary points
outside AWGN/low-rate, zero heavy-tail/QKD-channel SCL studies, zero frozen-hazard phenomena
in print. No survey line is unlock evidence. The X14-style survival measurement stays the hard
gate (survey section 7 adjudication). A list is worth building **only** if a synthetic working
point first shows SC-vs-list separation; otherwise it repeats the proven-pointless re-asks.

## Scope of this scoping

This change produces ONLY:

1. This `proposal.md` (problem + why-list + honest scope).
2. `design.md` (synthetic working-point design, list interface placeholder, L-ladder decision
   procedure, survival-gate restatement, rebuild-vs-reuse split, gate sequence — every gate
   marked NOT AUTHORIZED).
3. `tasks.md` (ordered S1..Sn mirroring the gate sequence, all unchecked, all
   `[GATE -- NOT AUTHORIZED]`).
4. Packet skeleton `.workbuddy/queue/NBPOLAR-SCL-SYNTHETIC-GATE/` with `STATUS.yaml`
   (state `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`, all counters 0) + `SCOPING_NOTES.md`
   (no-contact statement; SCL locked; RN scope untouched).
5. Seed/tag hygiene: fresh ranges proposed + grep-verified absent NOW, recorded as
   reserved-but-unactivated.

## Honest scope (binding)

- Descriptive, synthetic-only scoping. No unlock claim is made by this scoping.
- No real-data execution, no protected opens (V25 counts, parquet/pairs, 1M/1.5M/2M content,
  `raw_prior_*.npz`), no production-module merge, no `formal_ir/nbpolar/` edits (`sc.py`
  stays untouched).
- No FER / reliability / efficiency / branch-superiority claims inside this scoping.
- No L values frozen here; no pruning thresholds frozen here; no working-point numbers frozen
  here (design gives the selection rule, not the values).
- No literature-precedent claim for the frozen-hazard signal (novel per survey section 7).

## Recorded rules encoded (not re-litigated)

1. SCL is a SEPARATE project from RN and all accepted packets; SCL stays locked until this
   track passes its own gates.
2. First step is a SYNTHETIC working point that distinguishes SC vs list gains; only then is
   an L-ladder decided, with L values re-justified from that working point — never inherited
   from the survey's L in {4, 8, 32} (survey section 7 adjudication; those values are
   non-binding context).
3. X14-style true-path top-L survival at frozen-hazard spikes stays a hard gate for any
   SCL-unlock claim.
4. Spike-local reliability gating is a published family, but our frozen-hazard signal is
   novel (IR-4 top-16 in-prefix 0/48 has no published analogue) — no precedent claims.
5. No real-data execution, no production-module merge, no unlock/FER/reliability/efficiency
   claims inside the scoping.

## Impact scope

- New: `openspec/changes/scl-synthetic-list-gate/` (proposal/design/tasks).
- New: `.workbuddy/queue/NBPOLAR-SCL-SYNTHETIC-GATE/` (STATUS.yaml + SCOPING_NOTES.md).
- Read-only inventory: `sc.py` interface, survey sections 4-7, X14-X17 packets + probe roots,
  decision-log tail (closeout batch). No other files created or modified.

## Acceptance criteria (for this scoping)

- [ ] proposal/design/tasks exist under the new change dir and encode all five recorded rules.
- [ ] Design states a working-point selection rule that provably differs from X14-X16 configs.
- [ ] List interface described as a new module alongside frozen `sc.py` (no `sc.py` change).
- [ ] L-ladder procedure derives L from working-point measurements; survey L marked non-binding.
- [ ] Survival gate restated verbatim-compatible with X14 definitions.
- [ ] Packet skeleton present with locked state + zero counters + no-contact statement.
- [ ] Fresh seed ranges grep-verified absent NOW and recorded reserved-but-unactivated.
