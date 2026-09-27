# op-kratio-scale Tier-X execution transcript — 2026-09-27

## Preflight

- Independent freeze review: **conditional MAY_PROCEED** — all seven review items PASS with a
  single factual-error string to fix (`disclosed 2800 bits at every split`, which contradicts this
  probe's varying disclosure). Fixed, together with two stale comments, before launch.
- Formatting safety: an AST check over every `... % (...)` site reports **zero** placeholder vs
  argument mismatches (6 sites). This check is now the standing guard after the parent probe's
  fatal `%`-format defect.
- Frozen `prereg.md` and `run.py` were **not edited for execution** (the three string fixes were
  applied and reviewed before launch, not during).
- Target-output absence verified before launch: `results.json` **absent**.
- Read-only runtime dependency unchanged (`qkd_recon.polar_core`, import only).
- One launch only; no resampling, no seed change, no tuning, no rerun.

## Invocation

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-kratio-scale/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-kratio-scale/run.py
```

- Direct WSL exit code: `0`; stdout `WROTE …/results.json`, `STATUS ok WITHIN True CELLS
  {'expected': 10, 'completed': 10} WALL 115.022`
- stderr: the known WSL localhost/NAT proxy diagnostic only; **no Python traceback**.
- T0 import check printed `IMPORT_OK (560, 448, 336, 280, 224) (80, 64, 48, 40, 32) …`.

## Result record summary

Single record: `workspace/probes/op-kratio-scale/results.json`
(`probe_runs=1`, `reruns=0`, `stop_rules_triggered=[]`). Allocation ratio held at `k1:k2 = 1:6`.

| total k | k1 | k2 | disclosed | f_actual | operational exact / verify_failed /32 | oracle exact /32 |
|---:|---:|---:|---:|---:|---:|---:|
| 560 | 80 | 480 | 2800 | 2.934414 | **28 / 4** | 30 |
| 448 | 64 | 384 | 2240 | 2.347531 | 0 / 32 | 0 |
| 336 | 48 | 288 | 1680 | 1.760648 | 0 / 32 | 0 |
| 280 | 40 | 240 | 1400 | 1.467207 | 0 / 32 | 0 |
| 224 | 32 | 192 | 1120 | 1.173766 | 0 / 32 | 0 |

- Totals: operational `{exact 28, undetected 0, verify_failed 132, decode_failed 0,
  resource_abort 0}`; oracle `{exact 30, verify_failed 130}`.
- Observed key-dependent bits `[1184, 1464, 1744, 2304, 2864]` = the five disclosed values + 64.
- Wall `115.022 s` ≤ 600 s; peak RSS `215396352 B` (≈0.201 GiB) ≤ 1 GiB.

Descriptive Tier-X record only. No FER estimate, efficiency, operating point, allocation
recommendation, security, or real-data claim follows from these counts.
