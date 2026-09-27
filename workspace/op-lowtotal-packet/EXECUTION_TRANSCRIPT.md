# op-lowtotal-ratio Tier-X execution transcript — 2026-09-27

## Preflight

- Independent freeze review: `RETURN_TO_AUTHORING` on two findings, both fixed before launch:
  - **FAIL-A (data integrity)**: `points` aggregation keyed on `r["k1"]`, but `k1=96` appears at
    both totals, so two of eight points would have aggregated four seed-rows instead of two and
    reported `delta_complete=False` while `status` still read `ok`. Fixed to key on `f_label`.
  - **FAIL-B (stale text)**: `a3_split_rule` still described the parent's fixed 1:6 total-scale
    design. Fixed.
- Formatting safety: AST placeholder/argument check reported zero mismatches (6 sites) at the time
  of review; by then the `single_factor` and `a3_split_rule` strings carried the correct counts.
- Frozen `prereg.md` and `run.py` were **not edited during execution**.
- Target-output absence verified before launch: `results.json` **absent**.

## First launch — implementation defect, recorded not hidden

The first launch raised

```
TypeError: %d format: a real number is required, not list   (run.py:396)
```

Root cause: the FAIL-B text fix replaced a substring that had contained the `%s` placeholder,
leaving two placeholders against three arguments. This is the **third** string-formatting defect
of the night on mechanically derived runners — see the incident note below.

Disposition, following the repository precedent recorded in `.workbuddy/memory/2026-09-22.md`
(patch + first run is not a Tier-Y rerun when **no verdict or outcome existed to tune against**):

- No measurement, no count, and no verdict existed (`status=execution_error`, no `records`,
  no `points`), so nothing was observed and nothing could be tuned against.
- The error record was **preserved**, not deleted:
  `workspace/probes/op-lowtotal-ratio/results.execution_error_attempt1.json`.
- The defect was fixed by restoring the `%s` placeholder; the AST check then reported
  3 placeholders / 3 arguments at line 396.
- The corrected runner was launched **once**. This second launch is the measurement launch.

## Measurement invocation (second launch)

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-lowtotal-ratio/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-lowtotal-ratio/run.py
```

- Direct WSL exit code: `0`; stdout `WROTE …/results.json`, `STATUS ok WITHIN True CELLS
  {'expected': 16, 'completed': 16} WALL 158.752`
- stderr: the known WSL localhost/NAT proxy diagnostic only; **no Python traceback**.

## Result record summary

Single record: `workspace/probes/op-lowtotal-ratio/results.json`
(`probe_runs=1`, `reruns=0`, `stop_rules_triggered=[]`, 256 blocks).

| total | k1 | k2 | disclosed | op exact / verify_failed | oracle exact |
|---:|---:|---:|---:|---:|---:|
| 448 | 32 | 416 | 2240 | **1 / 31** | 5 |
| 448 | 64 | 384 | 2240 | 0 / 32 | 0 |
| 448 | 96 | 352 | 2240 | 0 / 32 | 0 |
| 448 | 128 | 320 | 2240 | 0 / 32 | 0 |
| 336 | 24 | 312 | 1680 | 0 / 32 | 0 |
| 336 | 48 | 288 | 1680 | 0 / 32 | 0 |
| 336 | 72 | 264 | 1680 | 0 / 32 | 0 |
| 336 | 96 | 240 | 1680 | 0 / 32 | 0 |

- Totals: operational `{exact 1, verify_failed 255}`; oracle `{exact 5, verify_failed 251}`.
- `a3_key_dependent_bits_observed = [1744, 2304]` = 1680+64 and 2240+64.
- Wall `158.752 s` ≤ 600 s; peak RSS `215760896 B` (≈0.201 GiB) ≤ 1 GiB.
- Every point reports `summaries.a3_op_fer.n = 2`, confirming the aggregation fix.

Descriptive Tier-X record only. No FER estimate, efficiency, operating-point, allocation
recommendation, security, or real-data claim follows from these counts.
