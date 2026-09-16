# P15 operator return — empirical-genie mid-N scaling (Tier-Y single gate, negative)

Packet: `NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING`.
Result: `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` (valid
scientific negative; not a candidate, not blocked). Main-thread acceptance
is pending; this return is not an acceptance.

## 1. Mission

Extend the accepted P13/P14 empirical-genie residual curve to mid-N
(N=32768 and N=65536) under empirical construction with independent DEV
only; decide whether either registered N reaches the planning f=1.3
genie-residual UCB target. No P12 operational/BEC retry, no BEC arm by
design.

## 2. Implementation and tests (frozen, unchanged by this wave)

- Thin runner
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_mid_n.py`
  reusing accepted P13 genie helpers, P7 input/support/preconditions, P12/P13
  f-budget helper, and P11 chunked SC (`chunk_rows=512`); no decision arm,
  tag, or Toeplitz master. Details: packet `P15_FREEZE.md` +
  `P15_IMPLEMENTATION_NOTES.md`.
- Focused suite
  `comparison_bench/tests/test_nbpolar_empirical_genie_mid_n.py`: 15/15
  green (injected data, fresh seeds, temp roots). Full NB-Polar suite:
  335 passed (320 prior + 15 P15), zero failures.

## 3. Pre-run checks

- Independent Pre-EXECUTE review: **PASS** (`PRE_EXECUTE_REVIEW.md`).
  STATUS at review time read 0/1 with result null; gate root
  `empirical_genie_mid_n_gate/` absent; NPZ stat size 25166822 bytes
  (content never opened by the review).
- No code/artifact/old-root change; no OpenSpec box checked; no commit/push.

## 4. Exact command (executed once)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_mid_n --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 32768 65536 --train-seeds 2026091960 2026091961 2026091962 2026091963 2026091980 2026091981 2026091982 2026091983 --dev-seeds 2026091970 2026091971 2026091972 2026091973 2026091990 2026091991 2026091992 2026091993 --train-blocks-per-stream 4 --dev-blocks-per-stream 4 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate
```

Exit 0, stderr empty, total wall 1620.511243 s (within the 2100 s budget).

## 5. Preconditions (7/7 true)

V25 1M TRAIN NPZ 25166822 B read once (size/mtime 2026-08-19 unchanged).
H1 0.024280546818678802 vs 0.02428054681872374 (d=4.49e-14); H2 exact;
total …6782 vs …7232 (d=4.51e-14); floored total 0.8010378249492791; floor
change 5.1600945738528026e-11 ≤ 1e-9; column dev 1.1357581541915351e-13;
p_b sum 1.0.

## 6. Consumption (1/1 spent, no rerun)

Artifact reads 1/1, attempts 1/1, opens 1, reopen false, retries 0, genie
calls 128/128, dev_block_count 32, provenance_violations 0. No reopen, no
retry, no rerun. TRAIN 16+16 blocks used_l1/l2 16 per N, impossible 0,
block errors 0.

## 7. Allocations + TRAIN diagnostics

- N=32768: K_total 6811 (K1 314 / K2 6497), TRAIN residual
  1.1128237904570182e-06, f 1.2998502888173578, leakage 34119.
- N=65536: K_total 13636 (K1 607 / K2 13029), TRAIN residual
  1.1015630768662632e-10, f 1.2999645814656315, leakage 68244.
- freeze_sha per cell persisted; orders lengths N; frozen_before_first_dev
  true; per-N agg↔construction cross-checks identical.
- N-to-seed grouping exact (1960..63→32768 TRAIN, 1970..73→32768 DEV,
  1980..83→65536 TRAIN, 1990..93→65536 DEV); TRAIN∩DEV ∅ within and
  across N; TRAIN/DEV sets disjoint across N.

## 8. DEV per-N table (n=16 each, t-factor 1.753050356, df=15)

| N | mean | std | min | max | UCB | UCB≤0.01 |
|---:|---|---|---|---|---|---|
| 32768 | 0.019146193040229846 | 0.03822701382375279 | 4.452207734151337e-06 | 0.1247046397723417 | 0.035899663088366535 | False |
| 65536 | 0.028768524223564552 | 0.10806211430369776 | 2.4939197373896604e-09 | 0.43377941496412364 | 0.07612810621111707 | False |

df=31 factor absent. candidate_ns [], smallest_candidate_n null.

## 9. Order stability (diagnostic-only, transcribed without interpretation)

`diagnostic_only: true`; excluded from freeze SHA and every gate.
N=32768 L1 ~0.9956–0.9975 / L2 ~0.9982–0.9991; N=65536 L1 ~0.9974–0.9979 /
L2 ~0.9986–0.9987 (full quad values in `aggregate_summary.json` /
Pre-RESULT §5).

## 10. Resources

| N | wall_s | rss_hwm_B | VmPeak_KiB | VmSize_KiB |
|---:|---|---|---|---|
| 32768 | 569.717255 | 593866752 | 811928 | 693720 |
| 65536 | 1050.793743 | 1033293824 | 1241560 | 1025752 |

Total wall 1620.511243 s (cell sum + 2.45e-4 s finalize); peak RSS
1033293824 B = 0.48×2GiB; VmPeak max 1241560 KiB ≤ 2097152 KiB.
Checkpoint/accounting consistent (five files on disk, jsonl 32 lines ==
32 DEV records).

## 11. Gates

12/12 integrity gates true, failing list empty (see Pre-RESULT §6 for the
recomputed table). Independent Pre-RESULT review: **PASS** (numbers
bit-exact; two non-blocking notes: the argmin-shortcut summation-noise
note confirming the ≥1e-9 binding, and this STATUS sync). Tests re-run
green: 15 focused + 335 NB-Polar.

## 12. Classification derivation

Integrity 12/12 true but NEITHER registered N meets UCB≤0.01
(0.035899663088366535 and 0.07612810621111707, both > 0.01), so
`TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` is uniquely
correct: not a candidate (no UCB ≤ 0.01), not blocked (all gates true).

## 13. Bounded scope

Genie union-bound construction proxy only; not operational FER, not a
real-channel result, not proof of any minimum N. No BEC arm by design.
N=65536 DEV mean (0.0288) exceeds N=32768 DEV mean (0.0191), reported
neutrally with no improvement claim. No qualification, promotion,
efficiency, key-rate, or scaling claim either way.

## 14. Unrun stages and closeout

None unrun: single gate executed once; reads/attempts 1/1 spent; no
rerun permitted. Next gate: main-thread acceptance. No OpenSpec box
checked; no code/artifact/old-root change; no commit/push; NPZ untouched
beyond the single authorized content open.

Evidence: this packet dir (`TASK_PACKET.md`, `STATUS.yaml`, `P15_FREEZE.md`,
`P15_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md`,
`PRE_RESULT_REVIEW.md`, `OPERATOR_RETURN.md`) + output root
`empirical_genie_mid_n_gate/` (five files:
`frozen_plan.json`, `construction_and_allocations.json`,
`per_block_genie_residuals.jsonl`, `aggregate_summary.json`, `report.md`).
