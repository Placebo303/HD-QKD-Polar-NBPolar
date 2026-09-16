# P15 FREEZE — empirical-genie mid-N scaling (implementation only, gate NOT run)

Packet: `NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING` (`TASK_PACKET.md`,
102 lines, frozen contract). Predecessors verified: P13
`ACCEPTED_VALID_NEGATIVE`, P14 `ACCEPTED_VALID_NEGATIVE`. This wave covers
ONLY OpenSpec delta + implementation + tests + freeze docs. The frozen gate
was NEVER executed: reads 0/1, attempts 0/1, result null, reviews pending.

## Mission

Extend the accepted P13/P14 empirical-genie residual curve to N=32768 and
N=65536 with empirical construction and independent DEV only; decide whether
either registered N reaches the planning f=1.3 genie-residual UCB target.
No P12 operational/surrogate retry.

## Frozen two-cell matrix

| N | TRAIN streams (4 blocks each) | DEV streams (4 blocks each) |
|---:|---|---|
| 32768 | 2026091960..1963 | 2026091970..1973 |
| 65536 | 2026091980..1983 | 2026091990..1993 |

Each N holds 16 TRAIN + 16 independent DEV blocks. GF(32), polynomial 37,
alpha 2, chunk_rows=512, target f=1.3. Each block sampled once + decoded
once per layer (L1 true-prefix genie, oracle-conditioned L2 true-prefix
genie). Planned genie calls = 128 (64 blocks x 2 layers, asserted in code
and gates). No decision arm, no tag, no Toeplitz master, no operational
decode.

## Frozen K_total values (computed from the ratified literals)

H = H1+H2 = 0.02428054681872374 + 0.7767572780789994 = 0.8010378248977232;
K_total = floor((1.3*N*H-64)/5) clipped to [0, 2N]; leakage = 5*K+64.

- N=32768: 1.3*32768*H = 34122.929680123176; -64 = 34058.929680123176;
  /5 = 6811.785936024635; floor = **6811**. Leakage = 5*6811+64 = 34119
  <= 34122.929680123176. Pinned under both float64 spellings of H1+H2
  (sum vs EXPECTED_TOTAL literal) by `test_frozen_k_totals_pinned`.
- N=65536: 1.3*65536*H = 68245.85936024635; -64 = 68181.85936024635;
  /5 = 13636.37187204927; floor = **13636**. Leakage = 5*13636+64 = 68244
  <= 68245.85936024635. Pinned the same way.

(K1, K2) per N is chosen at run time by the P13 lexicographic
(TRAIN residual, K1, K2) rule on pooled TRAIN risks; the N-specific order,
allocation and TRAIN residual freeze BEFORE that N's first DEV call and DEV
never changes them.

## Exact verbatim frozen command (NOT executed by this wave)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_mid_n --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 32768 65536 --train-seeds 2026091960 2026091961 2026091962 2026091963 2026091980 2026091981 2026091982 2026091983 --dev-seeds 2026091970 2026091971 2026091972 2026091973 2026091990 2026091991 2026091992 2026091993 --train-blocks-per-stream 4 --dev-blocks-per-stream 4 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate
```

All eleven flags required; no production default. Pre-EXECUTE (independent)
must still check N-to-seed grouping, wall margin, tests and the absent root.

## Output root, five-file schema, checkpointing

Root `empirical_genie_mid_n_gate/` is ABSENT (verified: queue dir holds only
`TASK_PACKET.md`, `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`).
At execution the runner creates EXACTLY these five files BEFORE the content
open and checkpoints THE SAME five files after every completed block:

1. `frozen_plan.json` (frozen point incl. K totals 6811/13636 from literals),
2. `construction_and_allocations.json` (public orders, pooled risks, splits),
3. `per_block_genie_residuals.jsonl` (one scalar record per DEV block),
4. `aggregate_summary.json` (per-N stats, gates, classification, accounting),
5. `report.md` (rendered tables).

Public orders/pooled risks + scalar block stats only. Resources per cell and
per block record: wall, RSS HWM, VmPeak, VmSize.

## Gates and labels

Integrity (12, frozen order): target_population_contract,
two_n_cells_complete, streams_disjoint_frozen,
orders_valid_frozen_before_dev, budget_allocation_reproduced, risks_finite,
zero_genie_exceptions, truth_isolation, no_unregistered_calls,
checkpoint_accounting_consistent, attempt_read_accounting_exact,
resource_limits_met_and_no_abort.

Classification (code implements, main thread adjudicates): any DEV UCB
<= 0.01 returns `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE` plus
the smallest qualifying N; integrity pass with neither UCB <= 0.01 returns
`..._NOT_CONFIRMED`; else `BLOCKED(<earliest>)`. Per-N statistic over all
16 scalar undisclosed-coordinate residuals: mean, sample std, range,
one-sided 95% t-UCB `mean + 1.753050356*std/sqrt(16)` (df=15). Order
stability across the four TRAIN streams + allocation/resources are
diagnostics-only.

## Consumption point, refusal ordering, no-rerun rule

Artifact read 1/1 + attempt 1/1 consumed together at the FIRST NPZ content
open (`load_v25_channel_counts`); module-level reopen guard refuses a second
NPZ-mode call. Refusals BEFORE the open (zero genie calls, no root touched):
absent root, CLI parse, chunk contract (`_minus_block` default-512 check +
value 512), N values != [32768, 65536], bps != 4/4, seed grouping
(8 TRAIN + 8 DEV, 4 per N in N order, distinct, disjoint). Post-open failure
(incl. precondition mismatch with zero genie calls) is BLOCKED with
consumption spent; best-effort BLOCKED stubs only, never a fresh root.
MemoryError over the FULL post-open pipeline preserves partial evidence and
finalizes BLOCKED; a semantic/resource failure is NEVER rerun, and no
N/seed/order/allocation/threshold change or tuning is permitted after open.

## Budgets and frozen environment

2 GiB virtual limit (`ulimit -v 2097152`, RSS guard 2 GiB), 2100 s external
timeout + in-run wall guard 2100 s, single-thread BLAS/OpenMP
(`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`,
`MALLOC_ARENA_MAX=2`).

## Forbidden paths (none accessed by this wave)

No V25 NPZ content open (stat size only, see below); no frozen gate run; no
Model-F/HOLD/raw/real/EVAL/tag/FWHT/APP/SCL paths; no official prior seeds
(all P7-P14 + probe seeds untouched — implementation and tests use only
fresh seeds 2026091770..1785); no N other than 32768/65536; NO decision-arm
implementation of any kind; no P12/P13/P14 code/evidence or old-root
modification; no `results/` or `comparison_bench/outputs_comparison/`
write; no commit/push.

## Proxy boundary

The DEV UCB is a genie union-bound construction proxy: not FER, not a
real-channel result, not proof of any minimum N. Planning f is not
real-channel efficiency. `undetected` has no meaning in this tag-free gate.

## Verification evidence (this wave, implementation only)

- Root absent: queue dir listing shows only the four packet files.
- NPZ stat size only: 25166822 bytes at the frozen counts path (NO open;
  reads/attempts remain 0/1).
- Frozen seeds fresh: `rg 202609196x..199x` outside the four new P15
  files/dirs returns nothing — disjoint from all priors.
- Test seeds fresh: `202609177x/178x` occur only in the new P15 test file.
- HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` recorded; no commit made
  (worktree carries pre-existing unrelated modifications; this wave added
  only its seven allowed files).
- Focused suite: 15/15 in `test_nbpolar_empirical_genie_mid_n.py` green
  (injected data, fresh seeds, temp roots).
- Full NB-Polar suite: 335 passed (320 prior + 15 new P15), zero failures;
  pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
  -m pytest -q -p no:cacheprovider` with fresh /tmp basetemp, 709.88 s.

This document authorizes nothing. Next gate: INDEPENDENT_PRE_EXECUTE.
