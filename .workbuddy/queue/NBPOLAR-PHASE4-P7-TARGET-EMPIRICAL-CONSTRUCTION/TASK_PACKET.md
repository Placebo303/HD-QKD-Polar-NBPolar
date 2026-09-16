# Phase 4-P7 Tier-Y packet — target-population empirical construction

## Objective

Build and execute one target-population, model-sampled NB-Polar development
gate using the V25 1M TRAIN counts—not the rejected-for-this-purpose Model-F
CAL artifact. Test whether pooled empirical genie orders support reliable
two-layer hard-candidate SC at a conservative fixed disclosure point.

Claim scope is narrow: a construction/protocol development signal for the
frozen V25 TRAIN empirical distribution at N=256. It is not held-out or real
frame FER, efficiency, key rate, scaling, qualification or promotion.

## P7-01 — OpenSpec and allowed implementation

Before behavior changes, add a Phase 4-P7 delta and tasks to the existing
`formal-ir-nbpolar-phase4-p0` OpenSpec change. Then add only the smallest:

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_construction.py`;
- its package export if needed;
- `comparison_bench/tests/test_nbpolar_target_construction.py`;
- packet freeze/implementation/review/result documents and milestone ledgers.

Reuse accepted GF32, transform, genie, SC, P1/P2 derivation, two-layer label,
Toeplitz verification and outcome/accounting code. Do not edit `sc.py`, prior
semantics, previous construction/protocol modules, baseline code or old roots.

## P7-02 — Frozen target input and support rule

Load exactly source `1M` through accepted `load_v25_channel_counts(path)` from:

`/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`

Expected file size is 25,166,822 bytes. The accepted key/loader resolves the
1M TRAIN count matrix as `[Alice,Bob]`, shape `[1024,1024]`. One artifact read
and one scientific attempt are allowed; both are consumed at the first NPZ
content open. Keep counts in memory and do not reopen the file. Do not read
Model-F, held-out pairs, raw parquet or TTBin.

Construct `P(A|B)` by column-normalizing the raw counts, replacing every cell
probability below `1e-15` by `1e-15`, then renormalizing each Bob column. This
is the only support rule. No lambda, global backoff, tuning, floor scan or
held-out fitting is permitted. Derive `p_b` from column totals and derive P1/P2
with accepted `A=32*U1+U2` semantics.

Before any genie/SC call, require:

- no zero Bob column;
- p_b normalization and conditional-table column error <=1e-12;
- H1 within 1e-12 of `0.02428054681872374`;
- H2 within 1e-12 of `0.7767572780789994`;
- total within 1e-12 of `0.8010378248977232`;
- floor-induced total-entropy change relative to raw MLE <=1e-9.

Failure is `BLOCKED(target_population_contract)` with no decoder/genie call.

## P7-03 — Frozen construction and evaluation

- GF32 polynomial 37, alpha 2, natural order, N=256.
- TRAIN construction streams `2026091650..2026091652`, 256 blocks each.
- DEV streams `2026091660..2026091664`, 128 common blocks each: 640 blocks.
- Toeplitz master per DEV stream is `stream+10000`, domain-separated by
  arm/block.
- Sample `B~p_b`, then `A~P_floor(A|B)`; high=`A//32`, low=`A%32`.
- TRAIN and DEV streams are disjoint. No EVAL exists.

For L1 and oracle-conditioned L2 separately, use accepted
`genie_conditionals` to accumulate error and entropy sufficient statistics per
TRAIN stream and pooled across all three. Freeze each pooled worst-first order
before DEV. Require every order be a permutation and minimum pairwise
TRAIN-order Spearman >=0.95 for each layer.

Build BEC analytic control orders from `epsilon_l=H_l/5`. Their rank/top-K
differences are report-only and never select the empirical order.

On every DEV block run two paired protocol arms:

1. empirical: pooled empirical L1 order K1=45, then candidate-conditioned L2
   using pooled empirical oracle-L2 construction order K2=140;
2. BEC control: BEC L1 order K1=45, then candidate-conditioned L2 using BEC L2
   order K2=140.

Each arm restarts SC by layer, reconstructs the 10-bit label and invokes one
64-bit Toeplitz verification tag. Alice truth enters only sampling, disclosed
values, tag construction and scoring. It must not enter operational metrics,
undisclosed decisions or candidate labels.

## P7-04 — Tests

Cover floor/renormalization and exact entropy reconstruction; axes/packing;
zero-column refusal; model sampler frequencies on tiny injected tables;
per-stream and pooled construction; order freeze before DEV; empirical/BEC arm
separation; candidate-conditioned L2 truth isolation; outcome buckets;
disclosure/tag accounting and recount; no artifact/production invocation from
tests. Test seeds must differ from frozen streams.

Run focused tests and the full accepted 217-test NB-Polar predecessor suite.

## P7-05 — Freeze, reviews and execution

Freeze the exact command, constants and absent output root in `P7_FREEZE.md`.
An independent reviewer-go must PASS Pre-EXECUTE, including source identity,
support formula, entropy literals, streams, thresholds, truth boundary, tests,
resource limits and target absence.

Frozen output root:

`.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`

It must be absent before execution and contain exactly:
`frozen_plan.json`, `construction_orders.json`, `per_block_paired_outcomes.json`,
`aggregate_summary.json`, `report.md`.

Exact WSL command:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_construction --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --n 256 --floor 1e-15 --train-seeds 2026091650 2026091651 2026091652 --train-blocks 256 --dev-seeds 2026091660 2026091661 2026091662 2026091663 2026091664 --dev-blocks 128 --k1 45 --k2 140 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate
```

Limits: 2 GiB and 3600 seconds. No retry, seed/order/K/floor/threshold change or
partial replacement after content open.

## P7-06 — Frozen gates and labels

Integrity gates:

- target input/support/entropy preconditions in P7-02 all true;
- 3x256 TRAIN and 5x128 DEV coverage complete and disjoint;
- orders frozen before DEV, permutations valid, provenance correct;
- 640/640 arm pairing, buckets mutually exclusive/exhaustive;
- truth-leak, undetected, nonfinite and resource_abort all zero;
- disclosure is exactly `5*(45+140)+64=989` key-dependent bits per fully
  invoked arm; public seed/control and transcript recount exact;
- attempt/read accounting exact and resource limits met.

Scientific gates:

- minimum pairwise TRAIN-order Spearman >=0.95 for L1 and L2;
- empirical arm exact >=620/640;
- empirical one-sided 95% Wilson exact-recovery lower bound >=0.95.

BEC-control exact counts, empirical-vs-BEC paired cells, rank correlations and
top-K overlaps are report-only. No gate requires empirical to beat BEC.

All gates true returns `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`. Integrity
true but a scientific gate false returns
`TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED`. Integrity failure returns
`BLOCKED(<earliest gate>)`. Report per-stream results, all buckets, paired
cells, construction stability, disclosure, planning-only f, wall and RSS.

Before publication, an independent reviewer-go Pre-RESULT review must
recompute input entropies, construction statistics, outcomes, Wilson bound,
accounting and every gate from the five artifacts. Reviewer evidence is trusted
under AGENTS.md section 4.1; main-thread acceptance remains separate.

## Stop and boundary rules

STOP and preserve the failure root on Pre-EXECUTE failure, target presence,
input/entropy mismatch, command/test error, resource breach, truth leak or any
integrity failure. Do not fix and rerun.

Forbidden: Model-F artifact, raw/held-out/real frames, EVAL, N>256, adaptive
schedule retuning, APP/SCL/FWHT, production benchmark, efficiency/key-rate/
qualification/promotion claim, old-root modification, commit or push.

