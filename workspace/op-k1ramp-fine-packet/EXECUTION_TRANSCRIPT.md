# op-k1ramp-fine-base Tier-X execution transcript — 2026-09-27

## Preflight

- Independent freeze review: **MAY_PROCEED** after a `RETURN_TO_AUTHORING` on the previous
  hand-written draft was resolved by discarding it and regenerating this runner as a
  **mechanical string-level derivative** of the already-frozen
  `workspace/probes/op-k1ramp-k550-base/run.py`.
- Residual non-blocking observations recorded and accepted:
  (a) `run.py` deviations row still reads "disclosed 2800..5000 bits" because it is
  byte-identical to the parent string; for this grid the descriptive range is
  2850..3050 — cosmetic only, the run takes `D = K1_POINTS[k1]["disclosed"]`;
  (b) `run.py` comment writes `HN ≈ 954.18` while the in-run value is `954.1939276637445`.
- Frozen `prereg.md` and `run.py` were **not edited for execution**.
- Target-output absence verified before launch: `results.json` **absent**.
- Read-only runtime dependency unchanged (`qkd_recon.polar_core`, import only).
- One launch only; no fallback point, no tuning, no seed change, no rerun.

## Invocation

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1ramp-fine-base/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-k1ramp-fine-base/run.py
```

- Direct WSL exit code: `0`; stdout `WROTE …/results.json`, `STATUS ok WITHIN True
  CELLS {'expected': 6, 'completed': 6} WALL 85.682`
- stderr: the known WSL localhost/NAT proxy diagnostic only; **no Python traceback**.
- T0 import check printed `IMPORT_OK (20, 40, 60) … 550 (2026092701, 2026092702) 16 600.0
  2026092600 128 …`.

## Result record summary

Single record: `workspace/probes/op-k1ramp-fine-base/results.json`
(`probe_runs=1`, `reruns=0`, `stop_rules_triggered=[]`).

| k1 | disclosed bits | f_actual | operational exact / verify_failed /32 | oracle exact /32 |
|---:|---:|---:|---:|---:|
| 20 | 2850 | 2.986814 | 2 / 30 | 32 |
| 40 | 2950 | 3.091615 | 14 / 18 | 32 |
| 60 | 3050 | 3.196415 | 24 / 8 | 32 |

- Totals: operational `{exact 40, undetected 0, verify_failed 56, decode_failed 0,
  resource_abort 0}`; oracle `{exact 96}`.
- Observed key-dependent bits `[2914, 3014, 3114]` = disclosed + 64.
- Wall `85.682 s` ≤ 600 s; peak RSS `216227840 B` (≈0.201 GiB) ≤ 1 GiB.

Descriptive Tier-X record only. No FER estimate, efficiency, operating-point, security, or
real-data claim follows from these counts.
