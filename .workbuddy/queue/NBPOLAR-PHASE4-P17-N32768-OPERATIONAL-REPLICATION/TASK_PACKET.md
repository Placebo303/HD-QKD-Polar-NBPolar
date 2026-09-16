# Phase 4-P17 Tier-Y delta — N=32768 operational replication

## Mission

Resolve P16's zero-count-margin result with an independent 128-block
replication at exactly the same target model, N, construction, disclosure and
protocol. Do not retrain, retune or pool P16 observations into the decision.

## P17-01 — Frozen predecessor and minimal delta

Add a P17 delta to the Phase-4 OpenSpec and one thin
`formal_ir/nbpolar/operational_f13_replication.py` runner plus focused injected
tests. Reuse P16 operational helpers without changing accepted code.

Before the NPZ content open, read P16's accepted
`construction_and_allocation.json` and verify: N=32768, K_total=6811,
K1=319, K2=6492, valid L1/L2 permutations and canonical construction digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`.
P16 remains immutable. A mismatch stops before any attempt.

Open V25 1M TRAIN `channel_counts.npz` once with the P7 floor-1e-15 contract.
Artifact read 1/1 and scientific attempt 1/1 are consumed together at first
content open. Recheck population/entropy/floor guards. No TRAIN or genie call.

## P17-02 — Frozen replication

- N=32768; K1=319/K2=6492; exact P16 orders; chunk_rows=512.
- DEV streams `2026092030..2026092037`, 16 blocks each =128 blocks.
- Each stream restarts its RNG; all streams are fresh relative to P16.
- Toeplitz master=`stream+10000`, domain-separated by P17/N/block.

For each sampled block execute exactly the P16 operational path: disclosed L1
SC, candidate-conditioned L2 metric and restarted disclosed L2 SC, reconstructed
10-bit label, one 64-bit tag, then one mutually exclusive outcome. No oracle,
comparator, rescue, retry, adaptive disclosure or second tag.

Alice truth may enter only sampling, disclosed values, tag construction and
scoring. Persist no private vectors, labels, metrics or raw seed bits.

## P17-03 — Accounting and independent decision

Every fully invoked block has key-dependent disclosure 34119 bits and public
control 327743 bits; planning f remains <=1.3. Independently recount L1/L2/tag
events and totals.

Integrity requires: predecessor construction identity; target population;
128/128 coverage with exact stream grouping; 256 operational SC calls; 128
tags; exhaustive mutually exclusive buckets; undetected/nonfinite/truth-leak
zero; exact disclosure/recount; one NPZ open; no unregistered activity or
resource abort.

Scientific gates, using P17's 128 blocks only:

- exact >=121/128;
- one-sided 95% Wilson exact-recovery LB >=0.90.

The frozen boundary is 121/128 -> LB 0.9021084760; P16's 62/64 is historical
report-only context and contributes zero observations to these gates.

- All gates true:
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`.
- Integrity true but recovery false:
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_NOT_CONFIRMED`.
- Integrity/resource failure: `BLOCKED(<earliest gate>)`.

## P17-04 — Evidence and resources

Absent root:
`.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/`.
Create exactly five files before content open and checkpoint after every block:
`frozen_plan.json`, `predecessor_construction_identity.json`,
`per_block_outcomes.jsonl`, `aggregate_summary.json`, `report.md`.
Persist construction identity/scalars and per-block scalar outcomes only.

Catch MemoryError around the whole post-open pipeline; preserve checkpoints and
never rerun semantic/resource failure. Record wall, RSS HWM, VmPeak/VmSize.
Freeze single-thread BLAS/OpenMP, `MALLOC_ARENA_MAX=2`, 2 GiB virtual memory and
2400 s timeout.

Focused tests cover predecessor identity/tamper refusal, zero TRAIN/genie calls,
P16 operational parity, all outcomes, Wilson 121/120 boundary, disclosure/tag
recount, fresh streams, checkpoint refusal, one-open/attempt and MemoryError.
Run focused plus current complete `test_nbpolar_*.py`; report observed counts.

Independent reviewer-go Pre-EXECUTE PASS is mandatory before content open.
Independent reviewer-go Pre-RESULT independently recounts 128 outcomes,
Wilson/classification, accounting, predecessor identity, resources and five
files. Main-thread acceptance remains separate.

## P17-05 — Frozen command and STOP

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2400 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13_replication --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-seeds 2026092030 2026092031 2026092032 2026092033 2026092034 2026092035 2026092036 2026092037 --dev-blocks-per-stream 16 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate
```

All flags required. Pre-EXECUTE checks predecessor identity, exact command,
fresh seeds, predicted resource margin, tests and absent root. STOP on any
failed precondition/review/test, existing root, ambiguity, exception,
nonfinite, integrity or resource failure. After content open: no repair,
rerun, seed/construction/K/threshold/tag change or tuning. No commit/push.

Return changed files, tests, reviews, read/attempt use, construction identity,
128-block outcomes, Wilson/count margin, accounting, gates, resources,
inventory, unrun stages and scope.
