# Phase 4-X11 Tier-X packet — hybrid FWHT end-to-end SC probe

## Mission

Measure whether an exact-semantics hybrid minus-node produces end-to-end SC
equivalence and useful scaling: FWHT only for all-finite, bounded-dynamic-range
rows; accepted direct `_minus_block` for every other row. This fills the one
missing X10 fact before any production/Tier-Y optimization gate.

## X11-01 — Write and claim boundary

Write only:

- `workspace/probes/nbpolar_x11_hybrid_fwht_endtoend/prereg.md`
- `workspace/probes/nbpolar_x11_hybrid_fwht_endtoend/results.json`

Freeze the three-line preregistration (question; exact parameters; exact
command) with the full stdlib+NumPy body embedded before the first measured
call. No production/test/OpenSpec/ledger/memory/index edits. No artifact,
evidence-root, official seed, raw/held-out/real/EVAL data, tag, or scientific
decoder gate. No attempt, threshold, winner, candidate, or acceptance.

## X11-02 — Frozen hybrid semantics

Reuse the X10 FWHT formula with GF(32) primitive polynomial 37, alpha=2,
float64, the accepted `_combination_index`, the frozen butterfly operation
order, and inverse scale `1/32`. A row is FWHT-eligible only when both input rows are
entirely finite and each row's `max-min <= 20.0` in natural-log units. Process
eligible rows with rowwise-max-stabilized FWHT. Process every ineligible row
with the accepted direct `_minus_block`, without modifying or approximating it.
Reassemble original row order, then use the accepted normalization.

For eligible rows, if any raw inverse-FWHT convolution value is `<=0`, or if
the produced row is nonfinite, discard that FWHT row and recompute it with the
direct reference. Record this numerical-safety fallback separately. Thus the
hybrid must never manufacture or delete exact support.

For the probe only, temporarily monkeypatch the imported module's
`_minus_block` while calling `sc_decode`, restore it in `finally`, and verify
the module function identity is restored. Do not copy or edit `sc.py`.

## X11-03 — Frozen inputs and timing

Probe-only seed `2026091760`. N values `[64,256,1024,4096,16384]`. For each N,
generate three normalized input regimes:

- `moderate`: logits uniform [-12,0];
- `mixed`: alternate rows uniform [-12,0] and [-80,0];
- `wide`: logits uniform [-120,0].

Use exactly one frozen metric block per `(N,regime)`. Run direct and hybrid on
the same block, with 1 untimed warmup for N<=1024 and no warmup above N=1024.
Then collect exactly 5 timed repetitions per implementation for N<=4096 and 3
for N=16384, alternating which implementation runs first. No known/disclosed
coordinates in the timing matrix.

Add deterministic semantic controls at N=64:

1. all-finite moderate metrics with 16 disclosed coordinates;
2. finite wide metrics with the same disclosures;
3. metrics containing registered `-inf` entries but at least one finite value
   per row, using disclosures selected only from direct-positive support;
4. an impossible disclosed-value case that must raise the same accepted
   exception in direct and hybrid modes.
5. the X10 near-tie/ramp structure plus an exact-tie control; require the
   accepted smallest-symbol tie behavior in both modes and report the entire
   32-symbol score ordering.

## X11-04 — Required record

For every timing cell persist raw durations, medians, direct/hybrid ratio,
`u_hat` and `x_hat` mismatch counts, decision argmax mismatches, maximum finite
decision-log-metric error, support mismatches, status/exception parity, and
hybrid counters: total minus calls/rows, eligible rows, dynamic-range fallback,
nonfinite-input fallback, numerical-safety fallback, and direct rows.

Also report aggregates by N/regime, fraction of rows actually using FWHT,
module-identity restoration, execution count/errors/reruns, wall/RSS, and the
X10 inherited kernel assumptions. Timing is descriptive; do not define a
speed threshold or claim a winner.

## X11-05 — Independent focused review

Obtain independent `reviewer-go` review in the return message, not a third
file. It independently reconstructs at least one moderate, mixed, wide and
nonfinite control; checks direct/hybrid output and exception parity; recomputes
fallback fractions/timing medians; confirms function restoration and two-file
write scope; and confirms zero forbidden access. Its reported checks are
trusted by the main thread.

One execution-error rerun is allowed only with the same frozen parameters,
seed and semantics, with both attempts recorded. STOP if exact-support parity
cannot be preserved, monkeypatch restoration fails, external input is needed,
or any production edit is required. Resource limits: 2 GiB virtual memory and
1800 s wall. No commit/push.

## Return contract

Return `X11 complete` or a concrete blocker. Include two-file inventory,
execution accounting, semantic-control results, worst end-to-end discrepancies,
FWHT/fallback fractions, timing table through N=16384, independent review, and
a recommendation for or against a Tier-Y `sc_fast` implementation gate.
