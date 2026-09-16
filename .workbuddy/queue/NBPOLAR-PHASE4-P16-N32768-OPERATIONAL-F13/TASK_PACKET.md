# Phase 4-P16 Tier-Y packet — N=32768 operational f=1.3 gate

## Mission

Measure actual two-layer hard-candidate SC recovery at the accepted target
model, N=32768 and planning `f<=1.3`. P15's genie UCB is conservative and is
not an operational outcome. This gate uses empirical construction, a fresh
operational DEV set and 64-bit verification; no BEC arm or adaptive retry.

## P16-01 — Minimal implementation and input

Add a P16 delta to the existing Phase-4 OpenSpec, one thin
`formal_ir/nbpolar/operational_f13.py` runner and focused injected tests. Reuse
P7 loading/support, P13 empirical construction/allocation, P4 two-layer causal
wiring, P5 hard-candidate L2 semantics, P11 chunked SC and P5 protocol/tag
accounting. Do not edit `sc.py`, `prior.py`, accepted modules/evidence or method
adapters.

Open V25 1M TRAIN `channel_counts.npz` exactly once. Artifact read 1/1 and
scientific attempt 1/1 are consumed together at first content open. Recheck
accepted H1/H2/total literals and floor/column guards. No Model-F, HOLD,
raw/real frames or EVAL.

## P16-02 — Frozen construction and DEV

- N=32768, GF(32), polynomial 37, alpha=2, chunk_rows=512, target f=1.3.
- TRAIN streams `2026092000..2026092003`, four blocks each =16 blocks.
- DEV streams `2026092010..2026092017`, eight blocks each =64 blocks.
- TRAIN/DEV streams are disjoint and each stream restarts its RNG.

TRAIN uses P13 true-prefix genie risks for L1 and oracle-conditioned L2. Pool
risks, create empirical worst-first `(e,h,index)` orders, set
`K_total=floor((1.3*N*(H1+H2)-64)/5)`, and exhaustively select `(K1,K2)` by
`(TRAIN residual,K1,K2)`. Freeze construction/allocation before DEV.

For every DEV block sample once, then:

1. disclose true U1 at empirical `order1[:K1]`; run operational L1 SC;
2. build L2 metrics only from Bob and the L1 candidate;
3. disclose true U2 at empirical `order2[:K2]`; restart operational L2 SC;
4. form `label_hat=32*high_hat+low_hat` and invoke one 64-bit Toeplitz tag;
5. classify exactly one of `exact`, `undetected`, `verify_failed`,
   `decode_failed`, `nonfinite`, `resource_abort` with undetected never success.

Alice truth is allowed only for sampling, disclosed values, tag construction
and scoring. No oracle arm, rescue, adaptive advancement or repeated decode.

## P16-03 — Disclosure and verification accounting

Key-dependent bits per fully invoked block are
`5*(K1+K2)+64`; require `(5*K_total+64)/(N*H_total)<=1.3`. Public Toeplitz
control is `10*N+63 = 327743` bits per invoked tag. Master=`DEV seed+10000`,
domain-separated by P16/N/block; never persist raw seed bits. Independently
recount all disclosure/tag/public-control events.

## P16-04 — Gates and labels

Integrity gates require: population contract; construction frozen before DEV;
16 TRAIN +64 DEV blocks; exact stream/call accounting; valid orders and K
replay; f<=1.3; mutually exclusive exhaustive outcomes; truth isolation;
undetected=0; nonfinite=0; no unregistered activity; transcript recount zero;
one artifact open; resource limits and no abort.

Scientific gates require:

- exact >=62/64;
- one-sided 95% Wilson exact-recovery lower bound >=0.90.

The 62/64 threshold has Wilson LB 0.9098711859; 61/64 has 0.8883797144.

- All integrity/scientific gates true returns
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE`.
- Integrity true but either recovery gate false returns
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_NOT_CONFIRMED`.
- Earliest integrity/resource failure returns `BLOCKED(<gate>)`.

## P16-05 — Evidence, resources and review

Absent root:
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/`.
Create exactly five files before content open and checkpoint after every block:
`frozen_plan.json`, `construction_and_allocation.json`,
`per_block_outcomes.jsonl`, `aggregate_summary.json`, `report.md`. Persist
public orders and scalar outcomes only; never counts, sampled/truth vectors,
decoded labels/keys, metric planes or raw tag seeds.

Catch MemoryError over the full post-open pipeline; preserve checkpoints and
never rerun semantic/resource failure. Record wall, RSS HWM, VmPeak/VmSize.
Freeze single-thread BLAS/OpenMP, `MALLOC_ARENA_MAX=2`, 2 GiB virtual memory and
2100 s timeout.

Focused tests cover empirical construction/allocation, causal L1-candidate L2,
truth isolation, every outcome/precedence, tag/domain separation, Wilson
62/61 boundary, disclosure/public accounting, recount, checkpoint refusal,
one-open/attempt and MemoryError. Run focused plus current complete
`test_nbpolar_*.py`; report observed counts.

Independent reviewer-go Pre-EXECUTE PASS is mandatory before content open.
Independent reviewer-go Pre-RESULT recomputes construction, 64 outcomes,
Wilson, disclosure/public accounting, gates, resources and inventory.

## P16-06 — Frozen command and STOP

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13 --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 32768 --train-seeds 2026092000 2026092001 2026092002 2026092003 --train-blocks-per-stream 4 --dev-seeds 2026092010 2026092011 2026092012 2026092013 2026092014 2026092015 2026092016 2026092017 --dev-blocks-per-stream 8 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate
```

All flags required. Pre-EXECUTE checks exact command, seed grouping, predicted
wall margin, tests and absent root. STOP on failed precondition/review/test,
existing root, ambiguity, exception, nonfinite, integrity or resource failure.
After content open: no repair, rerun, N/seed/order/allocation/threshold/tag
change or tuning. No commit/push.

Return changed files, tests, reviews, consumption, construction/allocation,
outcome table, Wilson, disclosure/public accounting, gates, resources,
inventory, unrun stages and scope.

