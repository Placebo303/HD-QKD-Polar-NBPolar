# op-k1k2-split-560 Tier-X execution transcript — 2026-09-27

## Preflight

- Independent freeze review: **MAY_PROCEED** after one `RETURN_TO_AUTHORING` round
  (F1 fatal `%`-format mismatch, F2 contradictory `a3_split_rule`, F3 description range).
  All three fixed; a static AST check of the final file reports **zero** placeholder/argument
  mismatches (6 formatting sites).
- Non-blocking carry-overs accepted: header comment still names the parent runner;
  `frozen_params.k2_single = 550` is an inherited literal with no run semantics under the split
  grid; `d2_base = None` is a dead assignment kept for structural parity.
- Frozen `prereg.md` and `run.py` were **not edited for execution**.
- Target-output absence verified before launch: `results.json` **absent**.
- Read-only runtime dependency unchanged (`qkd_recon.polar_core`, import only).
- One launch only; no resampling, no seed change, no tuning, no rerun.

## Invocation

```sh
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1k2-split-560/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-k1k2-split-560/run.py
```

- Direct WSL exit code: `0`; stdout `WROTE …/results.json`, `STATUS ok WITHIN True CELLS
  {'expected': 16, 'completed': 16} WALL 159.388`
- stderr: the known WSL localhost/NAT proxy diagnostic only; **no Python traceback**.
- T0 import check printed `IMPORT_OK 560 8 (2026092701, 2026092702)`.

## Result record summary

Single record: `workspace/probes/op-k1k2-split-560/results.json`
(`probe_runs=1`, `reruns=0`, `stop_rules_triggered=[]`). Every point spends
**2800 bits** (`5*(k1+k2)` with `k1+k2=560`) and therefore has the identical
`f_actual = 2.93441397898595`.

| k1 | k2 | disclosed | f_actual | operational exact / verify_failed /32 | oracle exact /32 |
|---:|---:|---:|---:|---:|---:|
| 10 | 550 | 2800 | 2.934414 | 0 / 32 | 32 |
| 40 | 520 | 2800 | 2.934414 | 14 / 18 | 32 |
| 80 | 480 | 2800 | 2.934414 | **28 / 4** | 30 |
| 160 | 400 | 2800 | 2.934414 | 1 / 31 | 1 |
| 240 | 320 | 2800 | 2.934414 | 0 / 32 | 0 |
| 320 | 240 | 2800 | 2.934414 | 0 / 32 | 0 |
| 400 | 160 | 2800 | 2.934414 | 0 / 32 | 0 |
| 480 | 80 | 2800 | 2.934414 | 0 / 32 | 0 |

- Totals: operational `{exact 43, undetected 0, verify_failed 213, decode_failed 0,
  resource_abort 0}`; oracle `{exact 95, verify_failed 161}`.
- Observed key-dependent bits: `[2864]` — a single value, i.e. 2800 + 64 at every point,
  confirming the constant-disclosure design.
- Wall `159.388 s` ≤ 600 s; peak RSS `215060480 B` (≈0.200 GiB) ≤ 1 GiB.

Descriptive Tier-X record only. No FER estimate, efficiency, operating-point, allocation
recommendation, security, or real-data claim follows from these counts.
