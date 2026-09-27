# Execution transcript — `op-k1-ramp-k550` (P4, one-shot)

## Identity

- **probe_id**: `op-k1-ramp-k550`
- **tier**: X（synthetic-only，descriptive，non-claim）
- **preregistered C command**（逐字执行，`workspace/probes/op-k1-ramp-k550/prereg.md` C 行；仓库根为工作目录）：

```
(from repository root) PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1-ramp-k550/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/probes/op-k1-ramp-k550/run.py
```

- **启动方式**: `wsl.exe -e sh -lc "<上面的 C 命令>"`，工作目录 `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`。
- **预检（强幂等）**: 执行前确认 `workspace/probes/op-k1-ramp-k550/results.json` **不存在**（该目录当时仅含 `prereg.md`、`run.py`）。P3 复核项 ⑦ 亦独立确认。

## Timing

| 项 | 值 |
|---|---|
| started_utc | `2026-09-26T19:01:06Z`（本地 UTC+8 = 2026-09-27 03:01） |
| ended_utc | `2026-09-26T19:03:06Z`（本地 = 2026-09-27 03:03） |
| 直连 exit code | **0** |
| 启动次数 | 1（`reruns=0`） |

## Budget / stop

| 项 | 实测 | 上限 | 判定 |
|---|---:|---:|---|
| wall_s | 118.95575040299445 | 600 | 在预算内 |
| peak_rss_bytes | 215814144（≈0.201 GiB） | 1 GiB | 在预算内 |
| cells | completed 10 / expected 10 | 10 | 全测 |
| `stop_rules_triggered` | `[]` | — | 未触发 |
| `undetected` | 0（所有点、两分支） | 0 ⇒ STOP | 未触发 |

## stdout 摘要（逐字）

```
WROTE /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1-ramp-k550/results.json
{
  "status": "ok",
  "within_budget": true,
  "probe_runs": 1,
  "reruns": 0,
  "cells": { "expected": 10, "completed": 10 },
  "wall_s": 118.95575040299445,
  "peak_rss_bytes": 215814144,
  "stop_rules_triggered": []
}
```

per-point（逐字取自 stdout 的 `per_point:` 段）：

| k1 | k2 | disclosed_bits | f_book（bookkeeping only） | operational exact | operational verify_failed | oracle exact | observed kdb |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 550 | 2800 | 2.9344139789 | 0/32 | 32/32 | 32/32 | 2864 |
| 80 | 550 | 3150 | 3.3013 | 30/32 | 2/32 | 32/32 | 3214 |
| 160 | 550 | 3550 | 3.7204 | 32/32 | 0/32 | 32/32 | 3614 |
| 320 | 550 | 4350 | 4.5589 | 32/32 | 0/32 | 32/32 | 4414 |
| 450 | 550 | 5000 | 5.2401 | 32/32 | 0/32 | 32/32 | 5064 |

合计（逐字）：

```
A3 outcomes(op): {'exact': 126, 'undetected': 0, 'verify_failed': 34, 'decode_failed': 0, 'resource_abort': 0}
A3 outcomes(or): {'exact': 160, 'undetected': 0, 'verify_failed': 0, 'decode_failed': 0, 'resource_abort': 0}
arm=BASE n=10  ... A3op=0.2125 oracle_exact_rate=1.0000
```

## stderr 摘要

```
wsl: 检测到 localhost 代理配置，但未镜像到 WSL。NAT 模式下的 WSL 不支持 localhost 代理。
```

- 该行为 WSL 启动期的 localhost/NAT 代理诊断，**非 Python traceback**（计划 §3 已知噪声）。
- 除该行外 stderr 无其他内容；stdout 中无 traceback。

## 写域清单

- `workspace/probes/op-k1-ramp-k550/results.json`（新建，`WROTE` 一行确认）
- `workspace/probes/op-k1-ramp-k550/.numba_cache/`（作用域内 numba 缓存，T0/导入副作用）

不写 `results/`、不写 `comparison_bench/outputs_comparison/`、不写只读依赖 `/mnt/d/Code/qkd-reconciliation-lab/src`。

## 纪律确认

- 未改参、未换点、未加样、未重跑；`probe_runs=1 / reruns=0`。
- 未触碰任何真实/受保护数据；非 Tier-Y；未在真实块上 decode。
- 所有 k1 点均记录为 **bookkeeping-only dose diagnostic**，不构成效率工作点主张（该裁定留待 P5）。
