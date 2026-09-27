# op-peak-refine Tier-X execution transcript — 2026-09-27

## Preflight

- Independent freeze review: **MAY_PROCEED** first round — no dangling names, six formatting sites
  all consistent, differences vs the parent limited to the declared classes, and the aggregation key
  (`k1`) verified unique in this three-point grid (the defect class that broke `op-lowtotal-ratio`).
- Frozen `prereg.md` and `run.py` were **not edited for execution**.
- Target-output absence verified before launch: `results.json` **absent**.
- Read-only runtime dependency unchanged (`qkd_recon.polar_core`, import only).
- One launch only; no resampling, no seed change, no tuning, no rerun.

## Invocation

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-peak-refine/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-peak-refine/run.py
```

- Direct WSL exit code: `0`; stdout `WROTE …/results.json`, `STATUS ok WITHIN True CELLS
  {'expected': 6, 'completed': 6} WALL 84.256`
- stderr: the known WSL localhost/NAT proxy diagnostic only; **no Python traceback**.

## Result record summary

Single record (`probe_runs=1`, `reruns=0`, `stop_rules_triggered=[]`), 96 blocks, total held at
`k1+k2=560` so every point spends 2800 bits (`a3_key_dependent_bits_observed = [2864]`).

| k1 | k2 | disclosed | op exact / verify_failed /32 | oracle exact /32 |
|---:|---:|---:|---:|---:|
| 60 | 500 | 2800 | 24 / 8 | 32 |
| 100 | 460 | 2800 | 26 / 6 | 26 |
| 120 | 440 | 2800 | 20 / 12 | 20 |

- Totals: operational `{exact 70, verify_failed 26}`; oracle `{exact 78, verify_failed 18}`.
- Wall `84.256 s` ≤ 600 s; peak RSS `215613440 B` (≈0.201 GiB) ≤ 1 GiB.

Descriptive Tier-X record only. No FER estimate, efficiency, operating-point, allocation
recommendation, security, or real-data claim follows from these counts.
