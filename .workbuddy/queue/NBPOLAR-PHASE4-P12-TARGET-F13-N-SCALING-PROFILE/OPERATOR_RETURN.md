# P12 operator return — BLOCKED(resource_limits_met_and_no_abort) (terminal)

Packet: `NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE` (Tier-Y).
Closeout label (unpersisted — no output root exists to persist it):

```
BLOCKED(resource_limits_met_and_no_abort)
```

This packet is TERMINAL. The single authorized run was executed exactly once
and resource-aborted (exit 1). No rerun/repair is permitted; any successor
would need NEW authorization.

## 1. Mission

Measure whether target-model recovery improves with N when every point is
held to the actual leakage budget `f<=1.3`, using N-specific BEC-surrogate
construction and the accepted operational two-layer hard-L1 SC. Development
profile only: not qualification and not an empirical-order scaling claim.
Six N rows (256/4096/16384/65536/131072/262144), exactly 128 blocks
(64/32/16/8/4/4), streams 2026091820..2026091825 (masters +10000).

## 2. Implementation / test summary (Wave A, unaffected by the run)

- Thin core+CLI `formal_ir/nbpolar/target_n_scaling.py` reusing accepted P7
  floor/support/preconditions, P11 chunked SC (`chunk_rows=512`, called not
  changed), P8 two-layer hard-candidate/Toeplitz/accounting; no accepted
  module edited. Details: `P12_IMPLEMENTATION_NOTES.md`.
- Focused suite 23/23 green; combined NB-Polar suite 285/285 green with the
  pinned interpreter (Python 3.12.3, NumPy 2.5.3), fresh basetemps.
- Frozen six-N allocations pinned by `test_frozen_six_allocations_pinned`
  (K_total 40/840/3399/13636/27285/54583; all `f<=1.3`); full table in
  `P12_FREEZE.md` §2.

## 3. Pre-run checks

- Independent Pre-EXECUTE review: **PASS** (`PRE_EXECUTE_REVIEW.md`).
- Output root `target_f13_n_scaling/` verified ABSENT before launch.
- Frozen command byte-verified against `TASK_PACKET.md` P12-06 /
  `P12_FREEZE.md` §3 (nine required flags; "13-flag" wording adjudicated
  cosmetic in the Pre-EXECUTE review §7(a)).

## 4. Exact frozen command (run ONCE)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 256 4096 16384 65536 131072 262144 --stream-seeds 2026091820 2026091821 2026091822 2026091823 2026091824 2026091825 --blocks 64 32 16 8 4 4 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling
```

Execution window: 20:53:45 → 21:12:37 (~1107–1132 s wall, within the 1800 s
budget). Exit code: **1**. stdout: **empty** (`/tmp/p12_gate_stdout.txt`,
0 B, never written).

## 5. Full verbatim stderr (transcribed from /tmp/p12_gate_stderr.txt, 1731 B; /tmp is transient so preserved here)

```
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py", line 1955, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py", line 1921, in main
    run = run_target_n_scaling(
          ^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py", line 1330, in run_target_n_scaling
    arm = run_scale_arm(
          ^^^^^^^^^^^^^^
  File "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py", line 774, in run_scale_arm
    p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py", line 319, in probs_to_symbol_metric
    return SymbolMetric(
           ^^^^^^^^^^^^^
  File "<string>", line 8, in __init__
  File "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py", line 255, in __post_init__
    mat = arr.astype(np.float64, copy=True)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
numpy._core._exceptions._ArrayMemoryError: Unable to allocate 64.0 MiB for an array with shape (262144, 32) and data type float64
```

## 6. Failure classification

- RESOURCE abort (memory), earliest failed gate
  `resource_limits_met_and_no_abort`; not a semantic mismatch, precondition
  failure, or pre-open refusal (deep-execution traceback + ~18.5 min wall
  prove the run passed the content open, preconditions, allocation, and
  ~124 smaller-N blocks into the N=262144 arm).
- Uncaught because `_ArrayMemoryError` subclasses `MemoryError`, which is
  outside the runner's caught `(ValueError, FileExistsError, OSError)`
  (lines 1932–1934) → exit 1 with empty stdout instead of the exit-0
  fail-closed `resource_abort`-record path. Failing site
  (`target_n_scaling.py:774`, L2 candidate metric) sits OUTSIDE both SC
  try-guards.
- Independent Pre-RESULT review verdict:
  **CONFIRMED_SINGLE_RESOURCE_ABORT** (`PRE_RESULT_REVIEW.md`) — exactly one
  execution, no retry, null artifacts verified, closeout label
  `BLOCKED(resource_limits_met_and_no_abort)`.

## 7. Consumption

Artifact read 1/1 + attempt 1/1 SPENT together at the first NPZ content
open (proven by deep-execution traceback). No reopen/rerun. `STATUS.yaml`
now records `artifact_reads_used: 1, attempts_used: 1`.

## 8. Null-artifact statement

- NO output root created: `target_f13_n_scaling/` still absent (end-only
  writes at runner lines 1631–1646 explain zero outputs — nothing is
  persisted until after the execution loop).
- NO label persisted anywhere on disk (no `aggregate_summary.json`); the
  stderr traceback above plus `PRE_RESULT_REVIEW.md` are the record.
- ~124 smaller-N blocks of in-memory progress lost (no per-cell
  checkpointing — the X12 lesson not applied here).
- No writes to `results/`, `comparison_bench/outputs_comparison/`, or any
  old root; HEAD unchanged; no test/artifact modification by the run.

## 9. Mechanism note (descriptive only, no repair plan)

Per-block coexisting 64 MiB (N,32) float64 planes plus
astype/log/full_like temporaries on the N=262144 path (L1 gather →
`probs_to_symbol_metric` chain; candidate-L2 gather → same chain, the
observed failure being the `SymbolMetric` copy at `prior.py:255`);
`chunk_rows=512` bounds only the SC `_minus_block` interior, not the metric
path; `ulimit -v 2097152` (2 GiB address space).

## 10. Reviews

- Independent Pre-EXECUTE: **PASS** (before the run).
- Independent Pre-RESULT: **CONFIRMED_SINGLE_RESOURCE_ABORT** (after the
  run; failure accounting confirmed).

## 11. Bounded scope

Synthetic V25-1M-TRAIN model-sampled development profile only. No
held-out/real FER, efficiency, key-rate, scaling, qualification, or
promotion claim either way. Recovery trend/first-success would have been
report-only.

## 12. Terminal statement

No rerun, no repair, no frozen-value change. The packet ends here as
`BLOCKED(resource_limits_met_and_no_abort)` with consumption 1/1 + 1/1
spent. A successor packet, if any, needs NEW authorization (recorded here
only as a fact about this packet's terminal state, not proposed as an
action). No OpenSpec box checked. No code/artifact/old-root touched. No
commit/push. The NPZ was not touched by this closeout.
