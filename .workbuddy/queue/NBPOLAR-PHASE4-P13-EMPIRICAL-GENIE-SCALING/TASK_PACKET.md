# Phase 4-P13 Tier-Y packet — target empirical genie scaling

## Mission

Determine, before any P12 retry, whether the V25 1M TRAIN target model reaches
the planning budget `f<=1.3` at N=4096, 8192 or 16384 when construction and
rate allocation are learned from empirical genie risks rather than a
same-entropy BEC surrogate. This is a model-sampled construction/rate
development gate, not operational FER or real-data qualification.

## P13-01 — Minimal delta and input contract

Add the P13 delta to the existing Phase-4 OpenSpec before implementation. Add
one thin module/CLI `formal_ir/nbpolar/empirical_genie_scaling.py` and focused
injected tests. Reuse accepted P7 loading, floor-1e-15 support, GF(32), packing,
sampling and P11 exact chunked SC. Reuse `genie_conditionals`; do not change
`sc.py`, `prior.py`, the operational decoder, protocol, tags or old roots.

Open the accepted V25 1M TRAIN `channel_counts.npz` exactly once. Artifact read
1/1 and scientific attempt 1/1 are consumed together at that content open.
Require the accepted raw-MLE literals H1/H2/total =
`0.02428054681872374 / 0.7767572780789994 / 0.8010378248977232` within `1e-12`,
floor perturbation <=`1e-9`, no zero Bob column and normalized derived tables.
No Model-F, HOLD, raw frames, real frames or EVAL.

## P13-02 — Frozen matrix and independent split

Use exactly N=`4096,8192,16384`. At every N:

- TRAIN streams: four fresh streams, two blocks each (8 blocks);
- DEV streams: four disjoint fresh streams, eight blocks each (32 blocks);
- sample `B~p_b`, `A~P_floor(A|B)` once per block;
- L1 genie conditionals use true U1 prefix; L2 genie conditionals use true U1
  and true U2 prefix (oracle-conditioned construction only).

Seeds are fixed by N:

| N | TRAIN streams | DEV streams |
|---:|---|---|
| 4096 | 2026091860..1863 | 2026091870..1873 |
| 8192 | 2026091880..1883 | 2026091890..1893 |
| 16384 | 2026091900..1903 | 2026091910..1913 |

Each stream restarts its RNG. No tag or Toeplitz master exists in this gate.

## P13-03 — Construction, allocation and independent DEV residual

For each TRAIN block accumulate coordinate risk contributions
`h_i=-log2 p_i[U_i]` and `e_i=1-max p_i`; pool TRAIN risks per layer. Persist
only the pooled coordinate risks, not per-block metric/risk planes. Order each
layer worst-first by accepted `(e,h,index)` semantics.

Set
`K_total=floor((1.3*N*(H1+H2)-64)/5)`, clipped to `[0,2N]`.
Enumerate all feasible integer splits `(K1,K2)` with `K1+K2=K_total`; select
the lexicographic minimum of `(TRAIN residual e sum, K1, K2)`. Freeze orders,
allocation and TRAIN residual before the first DEV block.

For every DEV block compute the scalar residual
`R=sum(e1[undisclosed empirical-order coords])+sum(e2[undisclosed empirical-order coords])`
for the frozen split. Also compute, from the same DEV genie rows without extra
SC calls, the report-only residual under the P12 same-entropy BEC orders and
their deterministic same-budget allocation. Never select or tune from DEV.

Per N report the 32 DEV `R` values, mean, sample standard deviation, range and
one-sided 95% Student-t upper confidence bound
`mean + 1.695518782*std/sqrt(32)` (df=31). The residual is a genie union-bound
construction proxy; it is not operational FER.

## P13-04 — Decision rule

Integrity gates require: three complete N cells; 8 TRAIN + 32 DEV blocks per
N; disjoint frozen streams; valid orders; exact K budget/allocation replay;
finite risks; zero genie exceptions; truth isolation; no unregistered calls;
checkpoint/accounting consistency; one artifact open; no resource abort.

Scientific classification uses only the empirical arm:

- `TARGET_EMPIRICAL_GENIE_F13_SCALING_CANDIDATE` if at least one registered N
  has the frozen one-sided DEV residual UCB <= `0.01`; record the smallest N.
- `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` if integrity passes but no
  registered N meets that condition.
- `BLOCKED(<earliest integrity/resource gate>)` otherwise.

Do not call this an FER threshold, real-channel result or proof of the minimum
N. BEC results and empirical-minus-BEC differences are report-only.

## P13-05 — Evidence and checkpointing

Target root (must be absent):
`.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/`.

Create exactly five files before the content open, then checkpoint the same
files after every completed block/N; do not create sidecars:

1. `frozen_plan.json`
2. `construction_and_allocations.json`
3. `per_block_genie_residuals.jsonl`
4. `aggregate_summary.json`
5. `report.md`

Persist public orders and scalar block statistics only. Do not persist counts,
sampled symbols, truth vectors, decoder outputs, metric planes or RNG state.
On MemoryError/resource failure, preserve checkpoints, finalize BLOCKED if
possible, and never rerun.

Record per cell wall, RSS HWM, Linux `VmPeak` and `VmSize`. Freeze
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` and
`MALLOC_ARENA_MAX=2`. Use 2 GiB virtual memory and 1800 s external timeout.

## P13-06 — Tests and independent reviews

Focused tests cover: literal tiny genie oracle; empirical order/ties; K budget
and exhaustive split selection; TRAIN/DEV separation; scalar DEV residual;
t-UCB literal; BEC report-only reconstruction; checkpoint resume refusal
(existing root never executes); one-open/one-attempt accounting; MemoryError
classification; no production/raw/HOLD access. Run focused tests plus the
accepted 262-test NB-Polar predecessor suite.

Independent reviewer-go Pre-EXECUTE PASS is mandatory before the NPZ content
open. Independent reviewer-go Pre-RESULT recomputes the three allocations,
per-block residual aggregates/UCBs, classification, resource/accounting and
five-file inventory before operator return. Reviewer findings are trusted;
main-thread acceptance remains separate.

## P13-07 — Frozen command and STOP

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_scaling --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 4096 8192 16384 --train-seeds 2026091860 2026091861 2026091862 2026091863 2026091880 2026091881 2026091882 2026091883 2026091900 2026091901 2026091902 2026091903 --dev-seeds 2026091870 2026091871 2026091872 2026091873 2026091890 2026091891 2026091892 2026091893 2026091910 2026091911 2026091912 2026091913 --train-blocks-per-stream 2 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate
```

All flags are required. Pre-EXECUTE verifies exact N-to-seed grouping, command,
tests and absent root. STOP on ambiguity, failed precondition/review/test,
existing root, exception, nonfinite value, resource failure or integrity
failure. After content open: no repair, rerun, seed/order/allocation/threshold
change or tuning. No commit/push.

Return changed files, tests, both reviews, read/attempt consumption, three
allocations, TRAIN order diagnostics, 32-value DEV summaries and UCBs, BEC
controls, classification, resource records, five-file inventory, unrun stages
and scope boundary.
