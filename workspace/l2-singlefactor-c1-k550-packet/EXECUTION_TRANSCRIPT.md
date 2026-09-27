# C1 Tier-X execution transcript — 2026-09-26

## Preflight

- Main-thread freeze review: PASS, `workspace/l2-singlefactor-c1-k550-packet/FREEZE_REVIEW.md`.
- Branch: `codex/nbpolar-phase0`.
- `workspace/probes/l2-singlefactor-c1-k550/results.json` was absent before launch.
- Frozen `prereg.md` and `run.py` were not edited for execution. The reviewed runner dependency is read-only `qkd_recon.polar_core` via `/mnt/d/Code/qkd-reconciliation-lab/src`.
- One launch only; no fallback, tuning, seed change, or rerun.

## Invocation

Launched once with `wsl.exe -e sh -lc`, working from the repository root. The command body below is the preregistered C command:

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/l2-singlefactor-c1-k550/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/l2-singlefactor-c1-k550/run.py
```

- Start UTC: `2026-09-25T17:48:46.7838389+00:00`
- End UTC: `2026-09-25T17:50:27.7161041+00:00`
- Direct WSL process exit code: `0`
- Standard output: runner reported `WROTE /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/l2-singlefactor-c1-k550/results.json`; final status `ok`, `within_budget=true`, `probe_runs=1`, `reruns=0`, and 8/8 cells completed.
- Standard error: one WSL startup diagnostic about localhost/WSL2 NAT was emitted and rendered with replacement/NUL characters by PowerShell; no Python traceback or runner error was present.

## Result record summary

The single record is `workspace/probes/l2-singlefactor-c1-k550/results.json`. It reports design overlap `76/550`, Jaccard `0.07421875`, `identical=false`, so the preregistered premeasurement stop did not trigger. The runner measured all 8 cells.

| Seed | BASE oracle exact / verify-failed | CAND oracle exact / verify-failed | BASE operational verify-failed | CAND operational verify-failed |
|---|---:|---:|---:|---:|
| 2026092601 | 16 / 0 | 0 / 16 | 16 | 16 |
| 2026092602 | 16 / 0 | 0 / 16 | 16 | 16 |
| 2026092603 | 16 / 0 | 0 / 16 | 16 | 16 |
| 2026092604 | 16 / 0 | 0 / 16 | 16 | 16 |

Across 64 paired blocks, oracle discordance was `base_only_exact=64`, `cand_only_exact=0`. Operational totals were 64 `verify_failed` per arm. Across both arms and both decoder modes, `undetected=0`, `decode_failed=0`, and `resource_abort=0`.

- Runner-reported wall time: `99.90650193498004 s` (limit 200 s).
- Peak RSS: `215662592 bytes` (limit 1 GiB).
- Stop rules triggered: none. `results.json` reports `within_budget=true`.
- Writes from execution were confined to the probe result and its in-root Numba cache.

This is a descriptive Tier-X record pending focused numerical review. No scientific acceptance or claim promotion is made here.
