# op-k1ramp-k550-base Tier-X execution transcript — 2026-09-27

## Preflight

- Main-thread freeze review: **PASS (MAY_PROCEED, zero blocking)** — see
  this packet's freeze review references below (independent read-only review of
  prereg/run.py/design vs the C1 predecessor).
- Two non-blocking review comments accepted as recorded: HN bookkeeping figure
  is 954.19 (not the 954.18 written in the plan table, a ≤0.001% rounding note);
  `bidx` varies with the k1 index so each point draws a different Toeplitz
  stream — pairing claim (same `(x,y)` per `(seed,block)`) is unaffected.
- Frozen `prereg.md` and `run.py` were **not edited for execution**.
- Target-output absence verified before launch: `results.json` **absent**.
- Read-only runtime dependency unchanged: `qkd_recon.polar_core` via
  `/mnt/d/Code/qkd-reconciliation-lab/src` (import only, zero writes).
- One launch only; no fallback point, no tuning, no seed change, no rerun.

## Invocation

Launched once with `wsl.exe -e sh -lc`, working from the repository root. The
command body is the preregistered C command:

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1ramp-k550-base/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-k1ramp-k550-base/run.py
```

- Direct WSL process exit code: `0`
- Standard output: `WROTE …/workspace/probes/op-k1ramp-k550-base/results.json`,
  `STATUS ok`, `WITHIN True`, `CELLS {'expected': 10, 'completed': 10}`,
  `WALL 118.757`
- Standard error: the known WSL localhost/NAT proxy diagnostic only; **no Python
  traceback**.
- T0 step (before this launch): import-only check printed `IMPORT_OK (10, 80,
  160, 320, 450) 550 (2026092701, 2026092702) 16 600.0 2026092600 128 …`.

## Result record summary

Single record: `workspace/probes/op-k1ramp-k550-base/results.json`
(`probe_runs=1`, `reruns=0`, `stop_rules_triggered=[]`).

| k1 | disclosed bits | f_actual | operational exact / verify_failed /32 | oracle exact /32 |
|---:|---:|---:|---:|---:|
| 10 | 2800 | 2.934414 | 0 / 32 | 32 |
| 80 | 3150 | 3.301216 | 30 / 2 | 32 |
| 160 | 3550 | 3.720418 | 32 / 0 | 32 |
| 320 | 4350 | 4.558822 | 32 / 0 | 32 |
| 450 | 5000 | 5.240025 | 32 / 0 | 32 |

- Totals: operational `{exact 126, undetected 0, verify_failed 34, decode_failed 0,
  resource_abort 0}`; oracle `{exact 160}`.
- Observed key-dependent bits: `[2864, 3214, 3614, 4414, 5064]` = disclosed + 64.
- `oracle_candidate_divergence`: defined 160, true 34 (report-only, no threshold).
- Wall `118.757 s` ≤ 600 s; peak RSS `216719360 B` (≈0.202 GiB) ≤ 1 GiB.
- Stop rules triggered: **none**. Writes confined to the probe result and its
  in-root Numba cache.

Read this as a descriptive Tier-X record only. No FER, efficiency, operating
point, security, or real-data claim follows from these counts.
