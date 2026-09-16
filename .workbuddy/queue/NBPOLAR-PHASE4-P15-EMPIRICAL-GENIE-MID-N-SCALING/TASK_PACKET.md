# Phase 4-P15 Tier-Y packet — empirical-genie mid-N scaling

## Mission

Extend the accepted P13/P14 empirical-genie residual curve to N=32768 and
N=65536. Use empirical construction and independent DEV only; do not retry
P12's operational/BEC profile. Decide whether either registered N reaches the
planning f=1.3 genie-residual UCB target.

## P15-01 — Scope and input

Add a P15 delta to the existing Phase-4 OpenSpec, then one thin
`formal_ir/nbpolar/empirical_genie_mid_n.py` runner and focused injected tests.
Reuse P13 helpers, P7 input/support and P11 chunked SC. Do not edit `sc.py`,
`prior.py`, P13/P14 code/evidence, protocols or tags.

Open V25 1M TRAIN `channel_counts.npz` once through the accepted loader.
Artifact read 1/1 and scientific attempt 1/1 are consumed together at first
content open. Recheck accepted H1/H2/total and floor/column guards. No
Model-F, HOLD, raw/real frames or EVAL.

## P15-02 — Frozen cells

| N | TRAIN streams (4 blocks each) | DEV streams (4 blocks each) |
|---:|---|---|
| 32768 | 2026091960..1963 | 2026091970..1973 |
| 65536 | 2026091980..1983 | 2026091990..1993 |

Each N has 16 TRAIN and 16 independent DEV blocks. GF(32), polynomial 37,
alpha=2, chunk_rows=512, target f=1.3. Each block is sampled once and decoded
once per layer: L1 true-prefix genie, then oracle-conditioned L2 true-prefix
genie. Planned genie calls = 128. No BEC arm, tag, Toeplitz or operational
decode.

## P15-03 — Construction and DEV statistic

At each N pool TRAIN `e_i=1-max p_i` and `h_i=-log2 p_i[U_i]`; construct the
accepted empirical worst-first `(e,h,index)` orders. Set
`K_total=floor((1.3*N*(H1+H2)-64)/5)` and exhaustively select `(K1,K2)` by
P13's lexicographic `(TRAIN residual,K1,K2)` rule. Freeze the N-specific order,
allocation and TRAIN residual before that N's first DEV call. DEV never changes
them.

For each DEV block persist the scalar undisclosed-coordinate genie residual.
Per N report all 16 values, mean, sample std, range and one-sided 95% t-UCB
`mean + 1.753050356*std/sqrt(16)` (df=15). Report order stability across the
four TRAIN streams and allocation/resources as diagnostics only.

## P15-04 — Gates and classification

Integrity requires: two complete N cells; 16 TRAIN+16 DEV blocks per N; 128
genie calls; disjoint streams; valid pre-DEV empirical orders; exact budget/
allocation replay; finite risks; zero genie exceptions/truth violations/
unregistered calls; checkpoint/accounting consistency; one open; no abort.

- Any DEV UCB <=0.01 returns
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE` and the smallest
  qualifying registered N.
- Integrity passes with neither UCB <=0.01 returns
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED`.
- Otherwise return `BLOCKED(<earliest integrity/resource gate>)`.

The UCB is a genie construction proxy, not FER or proof of minimum N.

## P15-05 — Evidence, resources and reviews

Absent root:
`.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/`.
Create exactly five files before content open and checkpoint after every block:
`frozen_plan.json`, `construction_and_allocations.json`,
`per_block_genie_residuals.jsonl`, `aggregate_summary.json`, `report.md`.
Persist public orders/pooled risks and scalar block statistics only.

Catch MemoryError over the full post-open pipeline; preserve partial evidence
and never rerun a semantic/resource failure. Record wall, RSS HWM, VmPeak and
VmSize. Freeze single-thread BLAS/OpenMP, `MALLOC_ARENA_MAX=2`, 2 GiB virtual
memory and 2100 s timeout.

Focused tests cover both N groups, stream separation, order/allocation replay,
df=15 UCB, checkpoint refusal/partial failure, one-open/attempt, MemoryError
and forbidden access. Run focused plus current complete `test_nbpolar_*.py`;
report observed counts. Independent reviewer-go Pre-EXECUTE PASS is mandatory
before content open. Independent reviewer-go Pre-RESULT recomputes allocations,
statistics/UCBs, classification, resources/accounting and inventory.

## P15-06 — Frozen command and STOP

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_mid_n --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 32768 65536 --train-seeds 2026091960 2026091961 2026091962 2026091963 2026091980 2026091981 2026091982 2026091983 --dev-seeds 2026091970 2026091971 2026091972 2026091973 2026091990 2026091991 2026091992 2026091993 --train-blocks-per-stream 4 --dev-blocks-per-stream 4 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate
```

All flags required. Pre-EXECUTE checks N-to-seed grouping, predicted wall
margin, tests and absent root. STOP on failed precondition/review/test,
existing root, ambiguity, exception, nonfinite, integrity or resource failure.
After content open: no repair, rerun, N/seed/order/allocation/threshold change
or tuning. No commit/push.

Return changed files, tests, reviews, consumption, both constructions and DEV
summaries, classification, resources, inventory, unrun stages and scope.
