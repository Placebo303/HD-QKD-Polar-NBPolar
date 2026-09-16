# Phase 4-P12 Tier-Y packet — target-population f=1.3 N-scaling profile

## Mission

Measure whether target-model recovery improves with N when every point is held
to the actual leakage budget `f<=1.3`. Use N-specific BEC-surrogate construction
and the accepted operational two-layer hard-L1 SC. This is a development
profile, not qualification or an empirical-order scaling claim.

## P12-01 — Scope and input

Add a P12 OpenSpec delta before code. Implement the thin core+CLI
`formal_ir/nbpolar/target_n_scaling.py` and focused injected tests. Reuse the
accepted P7 floor/support, P11 chunked SC, two-layer conditioning, buckets,
64-bit tag and accounting; do not change their behavior.

Open V25 1M TRAIN `channel_counts.npz` exactly once through the accepted loader.
Use columnwise MLE, floor `<1e-15`, renormalize; `A=32*U1+U2`; GF(32)
polynomial 37, alpha=2. Raw-MLE H1/H2/total must match
`0.02428054681872374 / 0.7767572780789994 / 0.8010378248977232` within `1e-12`;
floor perturbation <=`1e-9`. Read 1/1 and attempt 1/1 are consumed together at
the first NPZ content open. No reopen/rerun/tuning.

## P12-02 — Frozen f budget, construction and allocation

For each N set
`K_total=floor((1.3*N*(H1+H2)-64)/5)`, clipped to `[0,2N]`, and use the entire
budget. Therefore `leakage=5*K_total+64 <= 1.3*N*H`.

For each layer compute N-specific BEC reliabilities with float64
`z-=2z-z^2`, `z+=z^2`, starting at `epsilon_l=H_l/5`. Stable descending order
uses coordinate index as tie-breaker. Enumerate every feasible integer K1,
with K2=K_total-K1, and minimize lexicographically:

1. sum of undisclosed L1 and L2 reliabilities;
2. K1;
3. K2.

Freeze all K/order/residual values before the first SC call. These are analytic
BEC orders; P7's N=256 empirical order is not reused or extrapolated.

## P12-03 — Frozen execution matrix

| N | seed | blocks |
|---:|---:|---:|
| 256 | 2026091820 | 64 |
| 4096 | 2026091821 | 32 |
| 16384 | 2026091822 | 16 |
| 65536 | 2026091823 | 8 |
| 131072 | 2026091824 | 4 |
| 262144 | 2026091825 | 4 |

Exactly 128 blocks. Master=`seed+10000`, domain-separated by P12/N/layer/block.
For each block sample B~p_b and A from the frozen conditional model once, run
L1, build candidate-conditioned L2 metrics, run L2, reconstruct the label and
invoke one tag. No comparator, oracle, adaptive retry or repeated block.

## P12-04 — Evidence

Absent root:
`.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling/`

Create exactly five files: `frozen_plan.json`, `allocation_and_orders.json`,
`per_block_outcomes.json`, `aggregate_summary.json`, `report.md`. Persist public
orders and scalar outcomes only—never sampled symbols, decoded keys, metrics,
raw counts or raw tag seeds.

Per N report K/residual/leakage/f and tag-free f; exact/verify_failed/
decode_failed/undetected/nonfinite/resource_abort; exact fraction and two-sided
95% Clopper-Pearson interval; wall/RSS; key/public/tag accounting and literal
recount.

## P12-05 — Gates and reviews

Hard gates are integrity/completion only: six registered N rows; 128 attempted
blocks; exact reproduction of budget/allocation/orders; `f<=1.3`; mutually
exclusive exhaustive buckets with undetected never success; truth isolation;
finite/exact accounting and recount; no unregistered activity; no resource
abort. There is deliberately no recovery threshold because large-N samples are
too small for qualification.

All gates true returns `TARGET_F13_N_SCALING_PROFILE_CANDIDATE`; earliest
integrity/resource failure returns `BLOCKED(<gate>)`. Recovery trend and first
observed success are report-only.

Tests cover budget floors, K feasibility/ties, literal BEC recurrence/order,
f/accounting, axes, causal two-layer wiring, buckets/truth, tag/recount,
Clopper-Pearson edges, absent root and no production access. Run focused plus
the accepted 262-test predecessor suite. Independent reviewer-go Pre-EXECUTE
PASS is required before content open; Pre-RESULT independently recomputes all
allocations, outcomes, intervals, accounting and gates before return.

## P12-06 — Frozen command

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 256 4096 16384 65536 131072 262144 --stream-seeds 2026091820 2026091821 2026091822 2026091823 2026091824 2026091825 --blocks 64 32 16 8 4 4 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling
```

Every flag is required; no production default. Pre-EXECUTE confirms exact
command equivalence and the absent root.

## P12-07 — STOP and boundaries

STOP on failed precondition/test/review, existing root, ambiguity, resource or
integrity failure. After content open do not repair, rerun or change any frozen
value. Forbidden: Model-F/raw/held-out/real/EVAL; empirical large-N learning;
adaptive work; other N; FWHT/APP/SCL; FER/efficiency/key-rate qualification or
promotion; old-root modification; commit/push.

Return candidate or blocker with changed files, tests, reviews, read/attempt
accounting, six allocations, per-N outcomes/intervals/wall/RSS, f/accounting,
gates, five-file inventory, unrun stages and scope.
