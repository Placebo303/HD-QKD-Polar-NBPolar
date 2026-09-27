# NB-Polar 真实数据纠错路线图 — 2026-09-22

- 日期：2026-09-22
- 性质：**规划输入（planning proposal）**。不含执行授权、不含阈值判决、不修改任何科学状态串。
  授权与接受仍走 `WORKBUDDY_LIFECYCLE.md` / Tier-X·Y 规则；状态以 `STATE.md` 为准。
- 目标（唯一主线）：**在真实 ToA 数据上实现可重复、可记账的 NB-Polar（GF(32)）完整块纠错**，
  并推进到 FER / 泄漏 / 净密钥可陈述的“可用纠错”。
- 与既有文档关系：
  - 不取代 `STATE.md`（单入口）、`MACRO_PLAN_20260921.md`（Stage 0–4）、
    `REAL_DATA_FEASIBILITY_STRATEGY.md`（route 与 stop rules）、`ROADMAP.md` / `CRITICAL_PATH.md`（实现史）。
  - 本文件把上述文档 + 2026-09-22 项目评审合成**一条通往“真实纠错”的执行顺序**，
    并写清 gate、交付物、禁止项与 promotion ladder。

---

## §0 定位（对照第一性原则）

`AGENTS.md` §1.1：**高性能纠错算法优先**于包成熟度、审计机器、验证器复杂度。
本路线图的每一项都必须能回答：它如何增加“真实数据完整块纠错”的成功概率、样本量或可陈述性？
答不上来的，进 §6 冻结清单，不占主线带宽。

当前已达成（不是目标本身，是目标的证据阶梯下层）：

| 已有 | 标签 / 位置 | 含义（勿过度解读） |
|---|---|---|
| G2 三臂 one-shot SUCCESS | `NBPOLAR_M2_PRIOR_G2_SUCCESS`（`G2_ADJUDICATION.md`） | SHG `_1`、w=200/CIRCULAR、冻 K1=319/K2=6492：B(M2@32f) **11/14** vs A2(M0@32f) **0/14** 严格 Wilson 不重叠；A1 描述性；`undetected` 0/42 |
| G1R2 描述性 PASS | `NBPOLAR_M2_PRIOR_G1R2_COMPLETE_DESCRIPTIVE` | 窄窗下 δ-tail/NLL 门 PASS；δ-tail PASS 系 S11 推论 |
| G1 bounded negative | `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE` | w=500/LINEAR 上 ±1 前提不成立；**不**证伪机制，**不**证伪 M2 于所有源 |
| M2 状态 | **VALIDATED_AT_FROZEN_CONTRACT** | G3 SUCCESS 后进入（2026-09-22，`G3_ADJUDICATION.md`，仅第二级）；无 FER/效率/晋级主张 |
| 数据 | 冻结 ladder **耗尽** | never-decoded 101 frames → 32f CAL 后 69 &lt; 1 block；仅 SHG 新采集可验证 |
| 缺口 | **全项目无 FER 阈值** | Stage 0 未收口项；Müller eq(11) 要求 FER 进 `f_eff` |

结论：问题已从“能不能在真实数据上纠出完整块”推进到
**“换 session 是否可重复 → FER 多少 → 公开代价多少 → 是否够净密钥”**。

---

## §1 阶段总览（R0–R4）

与 `MACRO_PLAN` Stage 对齐：R0–R1 ≈ Stage 2 收口；R2 ≈ Stage 3 测量集；R3 ≈ 效率与记账；R4 ≈ Stage 4 论文。
Stage 1 零数据电池视作**已基本完成**（S8/S9/S10/S11）；未做的中间地板 probe 等降为可选，不再挡主线。

```text
R0  G3 收口 + 并行准备          [在飞 / 本周可启动准备件]
     │  gate: G3 裁决 + 语义预写
     ▼
R1  状态阶梯与单因子续作        [G3 PASS 分支 / FAIL 分支]
     │  gate: 跨 session 可重复 或 有界诊断收敛
     ▼
R2  扩样本 + FER 测量           [需要新采集 lead time]
     │  gate: 预注册 FER 口径下的样本量达标
     ▼
R3  效率/可用性（λ 分解、降披露、吞吐）
     │  gate: verification-aware f_eff 与运行时上界
     ▼
R4  论文与可辩护“可用纠错”主张
```

**串行纪律（继承 `CRITICAL_PATH.md`）**：后一阶段不得在前一 gate 未过时并行“抢跑”烧受保护数据。
并行允许的只有：文档/合成/Tier-X 零数据件、采集规格、论文骨架、卫生 batch。

---

## §2 R0 — G3 收口与并行准备（立即）

### R0.1 G3-CONFIRM（唯一 authorized 在飞实验）

| 项 | 内容 |
|---|---|
| 包 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/` |
| 范围 | SHG `_2` 独立 session 确认；契约继承 G2（w=200/CIRCULAR、K1=319/K2=6492、P16 构造） |
| 纪律 | **one-shot**：不改窗/MOD/K/seed/阈值；中途不加需求 |
| decode 前 | Pre-EXECUTE + 显式记录授权（文档已要求） |
| 禁止 | 利用 `_2` 做先验拟合/模型选择/窗选择（参与披露已约束） |

**裁决语义预写（G3 执行前写入 packet，避免裁决夜现编）**：

| 结果 | 状态串（建议，主线可改） | 后续 |
|---|---|---|
| PASS（预注册门） | `NBPOLAR_M2_PRIOR_G3_SUCCESS` + M2 → 建议记为 `VALIDATED_AT_FROZEN_CONTRACT`（**仍非 FER/效率/production**） | 进 R1-PASS；启动 R2 样本计划 |
| FAIL（门未过，非运行事故） | `NBPOLAR_M2_PRIOR_G3_BOUNDED_NEGATIVE` 或 `…_PREMISE_FAIL`（按失败层） | 进 R1-FAIL；**不**自动开表示转向 |
| 执行事故 / 预算中止 | `resource_abort` / invalid-run 保留，**不**改科学状态 | 按 freeze 重冻规则，不重跑调参 |

### R0.2 并行准备件（零受保护数据、不占 G3）

按优先级：

1. **FER 口径预注册草稿**（`docs/nbpolar/` 草稿 → 冻结前独立评审）
   - 定义：`exact` / `verify_failed` / `decode_failed` / `resource_abort` / `undetected` 如何进 FER（`undetected` **永不**并入 success/FER）。
   - 目标量级：与 Müller Cascade `FER<0.003`（1000 samples）可比或更严的区间；写明比较对象与 caveat。
   - 样本量下界：达到该 FER 陈述所需的最小 block 数与 CI 规则（Wilson 或预注册替代）。
   - 挂钩：Martínez-Mateo `f_FER` → Müller eq(11)/(13)；`H(q)→` 经验 `H(X|Y)` 替换必须预注册。
2. **`ACQUISITION_SPEC.md` 草稿**（Route C 唯一入口）
   - 目标：支撑 R2 的 FER 样本 + 至少 1 个独立 session 复现。
   - 建议量级（草稿可调，冻结前需 PI 确认）：≥ 50–100 个可组 N=32768 的完整 block（按 128 frames/block 估 frames），噪声/工作点与 SHG 可比或声明差异；Type0 是否纳入单列。
   - 保留段策略：每个 acquisition 预留独立确认段（禁止用尽后“再找块”）。
   - 异常：`.ttbin` primary vs `.1` 主体、`results_*` 目录未读规则，继承 `RAW_DATA_INVENTORY_20260921.md`。
3. **M2 promotion ladder 写入 `STATE.md` 一小节（主线裁定后）** — 见 §5。
4. **卫生 batch 清单**（不执行也可先列文件清单；执行放 milestone，见 §6）。

### R0 交付物

- [ ] G3 裁决记录 + decision-log / memory triage
- [ ] FER 口径预注册（草稿或冻结，取决于是否已够定论）
- [ ] `ACQUISITION_SPEC.md`（草稿 + PI 确认项列表）
- [ ] promotion ladder 5 行（进 `STATE.md`）
- [ ]（可选）最小主张论文 skeleton 标题 + 图表清单（数据仍用已接受描述性结果）

---

## §3 R1 — G3 后：单因子续作 / 有界诊断

### R1-PASS（G3 成功）— 目标：把“可重复”钉死

顺序固定，**一次一个因子**（继承 Stage 2 纪律）：

| 序 | 因子 | 读数 | 备注 |
|---|---|---|---|
| 1 | **扩 block 确认**（同契约、同源余量或新采集首批） | exact 率 + Wilson | 服务 R2 样本，不改算法 |
| 2 | **窗/配对协议固化** | W_P/W_S/MOD 写进协议 | G1 已证源相关；把 w=200/CIRCULAR 从“契约选择”升为协议默认或显式参数 |
| 3 | **L2 域与构造**（仅当 1 出现系统失败） | operational L2 first-error | 注意 G2 Pre-RESULT domain trap：`u1` vs `high` 必须写明 |
| 4 | **fixed-f vs fixed-K** 一次合成拍板（可 Tier-X） | 泄漏/f 叙事单口径 | D4 仍 DEFERRED；避免长期双口径 |
| 5 | **CAL/先验入 λ**（与 R3 重叠，可提前起草） | 记账合同 | M2 卖点只有入账才变成效率数字 |

**闸门**：跨 ≥2 个独立 session 的预注册恢复信号，或等价的扩样本 CI；在此之前 M2 保持
`VALIDATED_AT_FROZEN_CONTRACT`（若 G3 PASS），**不**升 efficiency/production。

### R1-FAIL（G3 未过）— 目标：有界归因，不开新战线

诊断顺序（stop-attribution，继承 `ROADMAP.md`）：

1. 执行完整性（recount、`undetected`、预算、复现）→ 事故 vs 科学 FAIL 分流；
2. 先验/窗/域（δ-tail、q_rest、L2 first-error 域）——对照 G1/G1R2/S11；
3. 构造/顺序（P16 是否与 `_2` 兼容）；
4. **最后才**考虑表示 / SCL / 新码族（且需 S3+S5+S6 联合指向或等价解码证据）。

FAIL 分支同样产出：裁决记录、死路追加（若闭合）、下一候选（richer δ-tail prior 等，见 G1 已列 (i)(ii)(iii)）。

---

## §4 R2–R4 — 测量、效率、论文

### R2 扩样本 + FER（≈ MACRO_PLAN Stage 3）

| 项 | 内容 |
|---|---|
| 前置 | FER 口径已冻结；新采集或 SHG 预留段已按 spec 切开 |
| 输出 | 逐 block：`exact` / `verify_failed` / `decode_failed` / `undetected` / `resource_abort` **分列**；FER 点估计 + CI |
| 禁止 | 小样本外推“FER≈…”；失败帧按 Müller eq(11) 计 **整帧** 泄漏；事后改口径 |
| gate | 预注册最小样本量达标后，才允许写 FER 数字进摘要 |

### R3 效率与可用性（f≤1.3、吞吐、λ）

1. **λ 分解合同**：`leak_IR + t + P_Collision + FER_cluster(k) + CAL_sacrifice + prior_reveal`（诊断 reveal ≠ 记账成本，分开）。
2. **降披露**：仅在 R2 站稳后压向 `f≤1.3`；保留 Phase 6 教训（fixed incremental 曾 negative）。
3. **吞吐/RSS 上界**：继承 G2 预算风格（wall/RSS 预冻结）；优化不得破坏 reference-equivalence。

### R4 论文（≈ Stage 4）

| 时机 | 内容 |
|---|---|
| **G3 裁决后 ≤2 周** | **最小主张 draft**（不必等 R2/R3）：真实 TE-QKD ToA 数据、固定披露预算、先验平滑导致完整块恢复提升、`undetected` 全 0、三臂对照、G3 独立 session。卖点按 R3 文献校准：**真实数据 + 实测经验 P(y\|x) + verification-aware λ**，禁止 “nobody did ToA IR”。 |
| R2 后 | 补 FER 与样本方法 |
| R3 后 | 补 `f_eff` / 吞吐 / 局限性 |

硬里程碑建议写入主线任务板：**“G3 裁决后 2 周内出最小主张 draft”**。

---

## §5 M2 promotion ladder（建议写入 `STATE.md` 的 5 行）

供主线裁定；本文件不改状态：

```text
CANDIDATE
  → (G3 PASS) VALIDATED_AT_FROZEN_CONTRACT     # 可重复真实块恢复；仍无 FER/效率/production
  → (R2 门过)  FER_MEASURED_AT_CONTRACT         # 预注册 FER 口径下有点估计+CI
  → (R3 门过)  EFFICIENCY_ACCOUNTED             # verification-aware f_eff 与运行时上界
  → (独立复现+样本+记账) READY_FOR_QUALIFICATION # 才允许谈 promotion / 净密钥
任一 FAIL：回到 CANDIDATE 或 BOUNDED_NEGATIVE，禁止跳级；禁止用合成 S9 推级。
```

---

## §6 使能件（不挡算法，milestone batch）

对照第一性原则：卫生与流程只在“防错误结论 / 防覆盖数据 / 防跨 checkout 污染”时插队。

| ID | 项 | 建议时机 | 要点 |
|---|---|---|---|
| H1 | 根目录清场 | 下一 milestone commit | v67–v72p* 结果、根下 `test_v*.py`、`tmp_v27r/v28r`、zip、过时 `总体判断.txt` → `docs/archive/` 或 `workspace/legacy/`；执行 `workspace-hygiene-result-archival` |
| H2 | OpenSpec 归档 | 同 H1 | `binary-ldpc-*`、`formal-ir-v35`…`v72p2d7`、`formal-nonbinary-ldpc-*` → `archive/`；活跃集只留 nbpolar + 仍约束行为的 policy change |
| H3 | `formal_ir/` 切包 | 同 H1 或下一代码里程碑 | 新代码只进 `nbpolar/` + `prior_m2.py`；其余 → `legacy/` |
| H4 | 路径 bug | **尽快**（小 PR，可先于 H1） | `pytest.ini` `basetemp` 与 `test_evidence_package.py:27` 的 `D:/Code/HD-QKD_Polar_Comparison/...` 改为本 worktree 相对/`PROJECT_*` |
| H5 | `CURRENT_TASK.md` 砍到 1 页 | 下一 milestone | 只留当前状态 + 下一 gate + 3 条 pointer；旧状态已在 decision-log |
| H6 | decision-log 分卷 | 里程碑后 | 按月/phase + TOC |
| H7 | Tier-X 瘕身检查单 | 写进 `PROBE_TIER.md` 一行 | Tier-X **禁止** Pre-EXECUTE/Pre-RESULT；三行 prereg + `results.json` + focused numerical review |
| H8 | L2 域规范 | 写进 `VALIDATION_GATES.md` | “H-conditioned L2 必须标明 `u1` 或 `high` 域” |

H4 防复发且极小，允许在 G3 期间做；其余 **不得** 挤占 G3/R1 算法带宽。

---

## §7 冻结 / 禁止项（除非本路线图相应 gate 打开）

- 一切未授权真实数据读/跑；`results/`、`comparison_bench/outputs_comparison/` 只加不覆。
- 表示转向、SCL 执行、C-P2 B4、新译码器族 — 仅 R1-FAIL 有界诊断指向且 S3+S5+S6（或等价）联合支持。
- 跨契约优劣叙事（G1 w=500 vs G1R2/G2 w=200）；post-hoc 换窗。
- 用 S9 合成或小样本 11/14 直接写 FER/净密钥/qualification。
- Tier-Y 一次执行上的 rerun / 调参 / 改阈值。

---

## §8 近期执行序（可直接拆 task）

| 序 | 动作 | 类型 | 依赖 |
|---|---|---|---|
| 1 | G3 Phase 0+A 按 packet 收口；decode 前 Pre-EXECUTE | Tier-Y | 在飞 |
| 2 | 写 G3 裁决语义预写进 packet | 文档 | 1 之前 |
| 3 | FER 口径预注册草稿 | 文档 | 可并行 |
| 4 | `ACQUISITION_SPEC.md` 草稿 | 文档 | 可并行 |
| 5 | H4 路径 bug 修复 | 小代码 | 可并行 |
| 6 | G3 裁决 → memory triage + decision-log | 里程碑 | 1 |
| 7 | 最小主张论文 skeleton（2 周内 draft） | 写作 | 6 |
| 8 | promotion ladder 五行进 `STATE.md` | 文档 | 6 |
| 9 | R1 单因子 #1（扩 block）或 R1-FAIL 诊断 | 实验 | 6 + 授权 |
| 10 | H1–H3/H5 卫生 batch | 仓库 | 里程碑 commit |

---

## §9 成功判据（“真实数据纠错”何时算数）

**最小成立（可写会议/短文）**：G3 PASS + 已有 G2 三臂 + 语义完整的 recovery 表（含 `undetected` 隔离）。

**可重复成立（路线图 R1 门）**：≥2 独立 session、预注册契约、CI 不塌。

**可用成立（R2–R3 门）**：预注册 FER 点估计+CI + verification-aware `f_eff` + 运行时/内存上界 + CAL/先验入账。

**可晋级（远期）**：独立复现 + 样本量 + 记账 + 独立 Pre-RESULT 全过；在此之前一切 “production / net key / qualification” 表述禁止。

---

*本文件是规划输入。任何 Stage-B / Tier-Y / 受保护数据动作仍需 freeze + 显式用户授权 + 适用的 Pre-EXECUTE / Pre-RESULT。*
