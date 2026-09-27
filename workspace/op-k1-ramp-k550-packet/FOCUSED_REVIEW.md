# Focused numerical review + main-thread adjudication — `op-k1-ramp-k550` (P5, 2026-09-27)

独立只读复核员（`code-explorer`）结论：**PASS_WITH_COMMENTS**。复核在不重跑探针的前提下，从 `results.json` 的逐块 `records` 独立重算了每点计数并与各聚合层对账。

- 复读取证范围（只读白名单）：`workspace/probes/op-k1-ramp-k550/{results.json,run.py,prereg.md}` +
  `workspace/op-k1-ramp-k550-packet/{EXECUTION_TRANSCRIPT.md,TASK_PACKET.md,STATUS.yaml}`。未执行代码、未写文件、未做全仓扫描。

## 复核结论摘要

1. **per-k1 计数重算 — PASS**：160 条 records 按 32 条一组分为五点（边界已逐一点验）；全局 `verify_failed` 34 条全部位于 operational，`exact` 286 条（含 oracle 160），34+286=320=160×2 分支，无遗漏。与 `per_point`、`per_cell`、`a3_outcomes_*_total` 完全一致。
2. **合计数 — PASS**：operational 五类和 = 160；oracle 五类和 = 160；`cells` 10/10；每点 2 seeds × 16 blocks。
3. **逐点 `disclosed` — PASS_WITH_COMMENTS**：五点 `disclosed_bits` == `5*(k1+550)`（2800/3150/3550/4350/5000）；k1=10 锚点 `f_book=2.9344139789` 与运行时 `f_actual_a3` 精确复现。**Comment**：其余四点 `f_book` 与 disclosed/HN 在第 4 位小数有 ≤1 ulp（≈8e-5）偏差，属 bookkeeping-only 标签，不参与任何运行时计算。
4. **tag 排除口径 — PASS**：`f` 只用 disclosed，全文件无 +64 参与 f；观测 `key_dependent_bits` = 2864/3214/3614/4414/5064 = disclosed+64，五点逐一成立；320 条记录 `tag_invoked` 全 true。
5. **`undetected` 隔离 — PASS**：五点两分支 `undetected` 全 0；正则命中非零 `undetected/decode_failed/resource_abort` 0 次；`stop_rules_triggered: []`。
6. **预算与 one-shot — PASS**：wall 118.95575040299445 s ≤ 600；peak RSS 215814144 B（≈0.201 GiB）≤ 1 GiB；`probe_runs=1 / reruns=0`；`status=ok`；与 transcript 逐字一致。
7. **写域 — PASS**：仅 `workspace/probes/op-k1-ramp-k550/{results.json,.numba_cache/}`；全文 `results/` 与 `outputs_comparison` 0 命中。
8. **描述性事实**：见下表；"首次脱离 0"仅以区间 `(10, 80]` 陈述。

## 逐点计数（描述性）

| k1 | k2 | disclosed_bits | observed kdb (=D+64) | op exact | op verify_failed | op undetected / decode_failed / resource_abort | oracle exact | blocks | seeds |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 550 | 2800 | 2864 | 0/32 | 32/32 | 0 / 0 / 0 | 32/32 | 32 | 2 |
| 80 | 550 | 3150 | 3214 | 30/32 | 2/32 | 0 / 0 / 0 | 32/32 | 32 | 2 |
| 160 | 550 | 3550 | 3614 | 32/32 | 0/32 | 0 / 0 / 0 | 32/32 | 32 | 2 |
| 320 | 550 | 4350 | 4414 | 32/32 | 0/32 | 0 / 0 / 0 | 32/32 | 32 | 2 |
| 450 | 550 | 5000 | 5064 | 32/32 | 0/32 | 0 / 0 / 0 | 32/32 | 32 | 2 |
| **合计** | — | — | — | **126/160** | **34/160** | **0 / 0 / 0** | **160/160** | 160 | — |

补充事实（描述性）：
- k1=10 点复现了 C1 的 operational 全 `verify_failed` 与 oracle 全 exact（此处 0/32 与 32/32；C1 为 0/64 与 64/64），与 C1 BASE 的 d2 集同一性得到一致性确认。
- k1=80 的 2 个 `verify_failed` 均来自 seed `2026092702`（block 4、block 7）；seed `2026092701` 在该点为 0/16。
- `a3_oracle_candidate_divergence`：defined 160 / true 34，report-only，本复核未做因果关联。
- `arms.BASE` 顶层聚合项取 `cfgs[0]`，只代表 k1=10 配置；其余四点须读 `per_point` / `per_cell`。

## 主线程裁定

**结论句（描述性，唯一允许的结论形式）**：

> 在 F4@q1024 / BASE `d2=worst_k(H2,550)` / `k2=550` 下，operational exact 计数在 **k1∈(10, 80]** 区间首次脱离 0（逐点计数：k1=10 → 0/32；k1=80 → 30/32；k1=160 → 32/32；k1=320 → 32/32；k1=450 → 32/32）。**描述性 Tier-X、非 claim。**

**边界（必须一并引述）**：

- 五个点全部是 **bookkeeping-only dose diagnostic**；**任何点都不得称为效率工作点**。k1=160..450 的 32/32 只说明"提高 L1 披露剂量后 operational 不再全灭"，**不等于**在给定 f 下取得效率优势；`f_book` 从 2.93 升到 5.24，泄漏同步上升。
- 网格只有 5 个有界点、每点 32 blocks，`(10, 80]` 是**网格分辨率下的区间**，不是断点定位；不得外推为门限。
- 未做显著性措辞、未写 H-label 结论、未作因果归因；`undetected` 全 0 已隔离。
- 不作 R2 sizing 输入；不产生 candidate/accepted token、不产生晋级、不产生自动续命。

**下一步建议（留给明天主线程，本夜不启动第三个 packet）**：

1. 在 `(10, 80]` 内加密取样以收窄区间（需新 packet + freeze review + 明示授权）。
2. 或转向"剂量—泄漏"权衡面：既然 operational 在 k1≥160 已不再全灭，值得问的是**在哪个剂量—泄漏组合上仍有意义**，而不是继续单因子扫剂量。
3. 把失败定位推进到逐层归因（L1 vs L2）时，须注意本探针已表明 k1=10 的 L1 剂量本身即可导致 operational 全灭。
