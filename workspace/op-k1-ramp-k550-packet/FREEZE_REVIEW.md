# Freeze review — `op-k1-ramp-k550` (P3)

- **Date**: 2026-09-27（隔夜第 1 轮 tick）
- **Reviewer**: 独立只读子代理（`code-explorer`），只读白名单 =
  新 probe 根 `workspace/probes/op-k1-ramp-k550/{run.py,prereg.md}` +
  新 packet `workspace/op-k1-ramp-k550-packet/{TASK_PACKET.md,STATUS.yaml}` +
  前任 `workspace/probes/l2-singlefactor-c1-k550/run.py`（仅用于比对派生差异）。
- **工具纪律**：未执行任何被测代码、未写入/修改/删除任何文件、未做全仓 grep/glob 扫描。
- **Verdict**: **FREEZE_REVIEW_PASS**（7/7 项 PASS；4 条 non-blocking 观察项；最小必要修订项：无）

---

## ① C 命令与 prereg 逐字一致 — PASS

`prereg.md` C 行与 `run.py` 的 `INTERPRETER` + `ENV` 拼装结果逐字相同：

- 解释器 `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`
- `PYTHONDONTWRITEBYTECODE=1`
- `NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1-ramp-k550/.numba_cache`
- `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1`
- `PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src`
- 脚本相对路径 `workspace/probes/op-k1-ramp-k550/run.py`（from repository root）

环境变量顺序两侧一致。

## ② `K1_GRID` / `K2_SINGLE` / `d1` / `d2` 与 DP-K2 / DP-K4 一致 — PASS

- `K1_GRID = (10, 80, 160, 320, 450)`；`K2_SINGLE = 550`，无 fallback 分支。
- `d1 = worst_k(H1, c["k1"])` 在 `for c in cfgs` 内**逐点**重算（前任 `d1_shared` 已按 P2 第 2 类改为 per-config）。
- `d2_base = worst_k(H2, K2_SINGLE)` 五点共享。
- `assert D == 5 * (k1 + k2)` 为运行时硬约束。

## ③ 五点 `disclosed = 5*(k1+k2)` 逐一验算 — PASS

| k1 | 5*(k1+550) | `K1_POINTS` 记录 | f_book（bookkeeping only） |
|---:|---:|---:|---:|
| 10 | 2800 | 2800 ✓ | 2.9344139789（C1 锚点 ✓） |
| 80 | 3150 | 3150 ✓ | 3.3013 |
| 160 | 3550 | 3550 ✓ | 3.7204 |
| 320 | 4350 | 4350 ✓ | 4.5589 |
| 450 | 5000 | 5000 ✓ | 5.2401 |

run.py / TASK_PACKET / STATUS.yaml 三处 f_book 一致；运行时以 `5*(k1+k2)/HN` 为权威 `f_actual_a3`。

## ④ 种子与 blocks 与 DP-K3 / DP-K4 一致 — PASS

- `SEEDS = (2026092701, 2026092702)`；`BLOCKS = 16` ⇒ 32 blocks/点，160 blocks 总计；`ARMS = ("BASE",)` 单臂；`expected_cells = 1*2*5 = 10`。
- `DESIGN_SEED = 2026092600`、`DESIGN_MC = 128` 与 C1 **完全相同** ⇒ d2 集与 C1 BASE 同一。
- 与 C1 的差异（seed 数 4→2、wall 200→600 s、K1_GRID、per-config d1、CAND/overlap 门移除）均已登记为 `deviations_from_C1`。

## ⑤ 预算与 STOP 规则齐备 — PASS

- `WALL_LIMIT_S = 600.0`、`RSS_LIMIT = 1*1024**3`。
- 检查点：每 32 design 样本（`m % 32 == 0`）+ 每 block 循环开头 + 收尾复检。
- 超界 ⇒ `stopped=True` ⇒ `status = "incomplete"`，无调参分支。
- `undetected` 隔离 STOP 保留（operational 或 oracle 任一 `undetected` 即 break），5 类 outcome 分列计数，undetected 不并入 exact。
- 异常 ⇒ `status=execution_error` + traceback + `sys.exit(1)`，`reruns=0`，无 retry。
- C1 的 `identical_or_overlap_gte_495` 设计门**仅**因单臂不适用而移除（无 CAND/`best_k`/overlap 残留）；`gates_retained_vs_C1 = [undetected_isolation_stop, budget_stop]`。

## ⑥ 写域仅新 probe 根 — PASS

- `OUT = ROOT + "/workspace/probes/op-k1-ramp-k550/results.json"`
- `NUMBA_CACHE_DIR = ".../workspace/probes/op-k1-ramp-k550/.numba_cache"`
- 全文仅两处 `open(OUT, "w")`；无 `results/` 或 `comparison_bench/outputs_comparison/` 写入；`sys.path.insert` 为只读依赖导入。

## ⑦ 目标产物缺失已验证 — PASS

`workspace/probes/op-k1-ramp-k550/results.json` **不存在**（目录内仅 `prereg.md`、`run.py`），与 `execution_authorized_by_packet: false` 相符。

---

## Non-blocking 观察项

1. 线程数环境变量实际为 **4 个**（OMP/OPENBLAS/MKL/NUMBA_NUM_THREADS），两侧逐字一致；若需第 5 个须由主线程裁定后同步改 prereg 与 run.py，冻结后不得单侧改。
2. `f_book` 的 k1=10 锚点 2.9344139789 为 C1 继承常量，与 2800/HN 在小数第 5 位存在约 2e-5 量级差异；因 f_book 明确为 bookkeeping-only 且运行时以 `f_actual_a3` 为权威，不影响冻结裁定。
3. STOP 原因字符串新 run.py 记为 `"undetected"`（C1 为 `"undetected>0"`），语义一致，属已登记的派生差异。
4. `import os` 与 `logpmf` 未使用（C1 同源遗留），无功能影响。

## 裁定

7/7 PASS，无 FAIL ⇒ **允许 P4 发起 one-shot 执行**（`reruns=0`，执行前再次验证目标产物缺失）。
