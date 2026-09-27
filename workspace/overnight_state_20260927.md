# 隔夜执行进度状态 — 2026-09-27

驱动文档：`docs/nbpolar/OVERNIGHT_PLAN_20260927.md` §2。
停止时刻：**2026-09-27 08:00（本地时区）**。

- **last_heartbeat**：2026-09-27 05:05（第 2 轮 tick 刷新；P0–P7 + 五个追加探针全部 done，本轮只读复核通过）
  - **时间戳订正（第 2 轮 tick，见 incidents #6）**：本行此前写 07:45，但文件实际 mtime 为 **04:40**，
    且本轮实测本机时间为 05:05 ⇒ 原心跳为**未来时间戳、不可信**。夜内文档中的"05:0x/07:0x/07:3x/07:50"
    等时段标注同样比文件系统 mtime 超前 1.5–3 h；**权威时间线以文件 mtime 为准**。
- **给后续 tick 的最终指令**：所有阶段 `done` ⇒ **不要新建任何探针、不要重复执行、不要重写包内产物**。
  08:00 前只剩只读复核 / 更新 heartbeat / 更新既有文档的权限。**本夜探针总量 = 6（已封顶）。**

## 阶段状态

| 阶段 | status | artifacts |
|---|---|---|
| P0 — C1 沉淀（不 git） | done | decision-log、DOCUMENT_INDEX、`COMMIT_READY_20260927.md`、两份 memory |
| P1 — 裁定冻结 | done | openspec change、`STATUS.yaml` adjudications |
| P2 — 派生 runner/prereg/packet | done | `op-k1ramp-k550-base/{run.py,prereg.md}` |
| P3 — freeze review | done | `FREEZE_REVIEW.md`（7/7 PASS） |
| P4 — one-shot 执行 | done | 118.757 s，10/10 cells |
| P5 — focused review + 裁定 | done | `FOCUSED_REVIEW.md`、`DUPLICATE_RUN_NOTE.md` |
| 追加 1 — 细网格插值 | done | `op-k1ramp-fine-base/`（85.682 s，6/6） |
| 追加 2 — 固定总披露配比 | done | `op-k1k2-split-560/`（159.388 s，16/16） |
| 追加 3 — 固定配比缩放总量 | done | `op-kratio-scale/`（115.022 s，10/10） |
| 追加 4 — 低总量有界配比搜索 | done | `op-lowtotal-ratio/`（158.752 s，16/16；含保留的 `execution_error` 记录） |
| 追加 5 — 峰值带细化 | done | `op-peak-refine/`（84.256 s，6/6） |
| P6 — R2 PI 决策卡片 | done | `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md` |
| P7 — 晨报 + 综合备忘录 | done | `workspace/OVERNIGHT_REPORT_20260927.md`、`docs/nbpolar/SYNTHESIS_20260927.md` |
| 第 2 轮 tick（05:00–05:05）— 只读一致性复核 | done | 本文件 heartbeat + incidents #6；`OVERNIGHT_REPORT_20260927.md` §六 复核附注 |

## 结果速览（描述性 Tier-X，非 claim）

- **剂量轴**（k2=550）：k1 = 10/20/40/60/80/160/320/450 → 0/2/14/24/30/32/32/32；首次脱离 0 于 **k1∈(10,20]**，饱和于 **160**。
- **分配轴**（总 560，2800 bits 恒定）：k1 = 10→0、40→14、60→24、**80→28**、100→26、120→20、160→1、≥240→0。
  ⇒ **峰顶 k1≈80–100，峰宽 [60,120]（平台而非尖峰）**；同预算只改配比即可 0/32 → 28/32。
- **总量轴**（配比 1:6 固定）：560→28、448/336/280/224→0 ⇒ 该配比下最低可维持 = **2800 bits**。
- **低总量配比**（有界 8 点）：T448 k1=32→**1**；其余七点 0；T336 全零 ⇒ **最优配比随总量移动**（560 峰值≈1:6，448 唯一非零≈1:13）。

## Incidents

1. **重复 one-shot 执行（并发）**：02:50 tick 与人工会话并行 ⇒ A 权威 + B 交叉验证，数字一致。
2. **细网格首版 RETURN_TO_AUTHORING**：6 处非授权差异 + STATUS over-claim ⇒ 脚本级机械派生。
3. **配比探针首版（致命）**：`single_factor` 无占位符却传实参 ⇒ 会抛 TypeError 毁灭整轮。
4. **缩放探针首版（条件放行）**：描述字符串与变披露设计矛盾。
5. **低总量探针首版**：① 聚合键 `k1` 在网格内不唯一（两总量都含 96）⇒ 汇总污染；② 文本同步误删 `%s` ⇒ 首次 launch `execution_error`（错误记录**保留**，修复后单次测量 launch）。
6. **心跳/时段标注时间不可信（第 2 轮 tick 05:05 发现并订正）**：上一轮把 `last_heartbeat` 写成 **07:45**，
   而进度文件实际 mtime = **04:40**、本轮实测本机时间 = 05:05 ⇒ 该心跳是**未来时间戳**。
   夜内 memory/晨报中的时段标注（05:0x / 07:0x / 07:3x / "07:50 终版"）同样比 mtime 超前 1.5–3 h。
   **影响**：仅文档时间线失真；**不影响**任何产物内容（数值复核已逐项通过，见晨报 §六）。
   **处置**：心跳改为经核实的 05:05；晨报加 §六 附注说明权威时间线为 mtime；**未重写任何包内产物**。
   **建议固化**：自动化 tick 写 `last_heartbeat` 前，先用 `Get-Date` 取本机时间，**禁止**用估算/推断时间。

**三项必跑检查（建议固化）**：机械派生后 ① AST 占位符/实参一致性；② 聚合/索引键在网格内唯一性；
③ 写心跳/时间标注前用 `Get-Date` 取本机时间（不得估算）。

## 未完成 / 挂起（需用户一句话）

- git commit / push（全程零 git 动作）→ `COMMIT_READY_20260927.md`（A/B/B2/B3/B4/B5/B6/B7/C）
- 两个 openspec change 是否 archive
- R2 四项 PI 待决 → `R2_T4_PI_DECISION_CARDS_20260927.md`
- 路线选择（备忘录 §5 的 R-A/R-B/R-C/R-D；我的参考建议：R-D 与 R-A 并行，R-B 作填充）
- 是否把 K 分配问题推到真实数据（需独立 packet + freeze review + 逐字授权）
