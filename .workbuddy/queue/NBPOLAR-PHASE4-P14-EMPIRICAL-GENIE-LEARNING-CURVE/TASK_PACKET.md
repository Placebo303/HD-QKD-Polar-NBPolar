# Phase 4-P14 Tier-Y packet — empirical-genie construction learning curve

## Mission

At P13's N=16384 point, determine whether failure to reach the f=1.3 residual
target was materially caused by constructing from only eight TRAIN blocks.
Build nested 8/16/32/64/128-block constructions and evaluate all five on the
same independent 32 DEV blocks. This is a model-sampled genie construction
diagnostic, not operational FER or real-data qualification.

## P14-01 — Minimal delta and input

Add a P14 delta to the existing Phase-4 OpenSpec first. Add one thin
`formal_ir/nbpolar/empirical_genie_learning_curve.py` runner and focused
injected tests, reusing P13 helpers and accepted P7/P11 contracts. Do not edit
`sc.py`, `prior.py`, P13 code/evidence, decoder semantics, protocol or tags.

Open V25 1M TRAIN `channel_counts.npz` exactly once with the accepted P7
floor-1e-15 contract. Artifact read 1/1 and scientific attempt 1/1 are consumed
together at first content open. Recheck accepted H1/H2/total literals and
floor/column guards before the first genie call. No Model-F, HOLD, raw/real
frames or EVAL.

## P14-02 — Frozen matrix

- N=16384; GF(32), polynomial 37, alpha=2, chunk_rows=512; target f=1.3.
- TRAIN streams `2026091930..2026091937`, 16 blocks each = 128 blocks.
- DEV streams `2026091940..2026091943`, 8 blocks each = 32 blocks.
- Stream-major TRAIN order: seed ascending, then block index ascending.
- Nested prefix sizes B=`8,16,32,64,128` from that one TRAIN sequence.
- Each TRAIN block is decoded once per layer; accumulated risks serve every
  applicable prefix. Each DEV block is decoded once per layer and its genie
  rows score all five frozen constructions. Planned genie calls = 320.

Sampling, L1 true-prefix genie and oracle-conditioned L2 genie are exactly P13.
No tag, Toeplitz call or operational decode.

## P14-03 — Construction and independent evaluation

For each B, pool TRAIN `e_i=1-max p_i` and `h_i=-log2 p_i[U_i]`, form accepted
worst-first `(e,h,index)` orders, and set
`K_total=floor((1.3*N*(H1+H2)-64)/5)`. Exhaustively select `(K1,K2)` by P13's
lexicographic `(TRAIN residual,K1,K2)` rule. Freeze all five constructions
before the first DEV call.

For each DEV block/B persist the scalar undisclosed-coordinate residual. Report
32-value mean, sample std, range and one-sided t-UCB with the frozen df=31
factor `1.695518782`. Also report paired `R_B-R_8` and adjacent differences
with mean/std/UCB. Never select or tune from DEV.

Report-only: pairwise order Spearman/top-K overlap, allocation movement and DEV
improved/tied/regressed counts. P13 B=8 is historical reference only; do not
merge its different-seed blocks or require equality.

## P14-04 — Gates and classification

Integrity requires: one complete N cell; 128 TRAIN + 32 DEV blocks; 320 genie
calls; exact nested prefixes; disjoint streams; five valid pre-DEV
orders/allocations; finite values; zero genie exceptions/truth violations/
unregistered calls; checkpoint/accounting consistency; one open; no abort.

- B=128 DEV UCB <=0.01 returns
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE`.
- Integrity passes but UCB >0.01 returns
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`.
- Earliest integrity/resource failure returns `BLOCKED(<gate>)`.

Other prefixes diagnose learning only. Main thread chooses more TRAIN,
regularization or larger N after a NOT_CONFIRMED return.

## P14-05 — Evidence, resources and reviews

Absent target root:
`.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/`.
Create exactly five files before content open and checkpoint the same files
after every block: `frozen_plan.json`, `learning_curve_constructions.json`,
`per_block_genie_residuals.jsonl`, `aggregate_summary.json`, `report.md`.
Persist pooled risks/public orders and scalar block statistics only.

Catch/classify MemoryError around the full post-open pipeline; preserve
checkpoints and never rerun semantic/resource failure. Record wall, RSS HWM,
VmPeak and VmSize. Freeze single-thread BLAS/OpenMP and `MALLOC_ARENA_MAX=2`,
2 GiB virtual memory, timeout 1800 s.

Focused tests cover nested accumulation/no repeated calls, order/K replay,
five-way DEV scoring, paired UCB, stream separation, checkpoint refusal,
one-open/attempt, MemoryError and forbidden access. Run focused plus current
complete `test_nbpolar_*.py`; report observed counts.

Independent reviewer-go Pre-EXECUTE PASS is required before content open.
Independent reviewer-go Pre-RESULT recomputes prefixes, constructions,
statistics, classification, accounting/resources and inventory.

## P14-06 — Frozen command and STOP

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_learning_curve --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 16384 --train-seeds 2026091930 2026091931 2026091932 2026091933 2026091934 2026091935 2026091936 2026091937 --train-blocks-per-stream 16 --prefix-blocks 8 16 32 64 128 --dev-seeds 2026091940 2026091941 2026091942 2026091943 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate
```

All flags required. Pre-EXECUTE checks exact command/grouping, tests and absent
root. STOP on failed precondition/review/test, existing root, ambiguity,
exception, nonfinite, integrity or resource failure. After content open: no
repair, rerun, seed/prefix/order/allocation/threshold change or tuning. No
commit/push.

Return changed files, tests, reviews, consumption, five constructions, DEV and
paired summaries, classification, resources, inventory, unrun stages and scope.
