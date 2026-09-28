# R2 预注册测量合同（MEASUREMENT_CONTRACT 合并草稿）— 2026-09-24

- **性质**：**草稿 / draft（docs-only merge）——不含授权、不冻结阈值、不改变科学状态、
  不含任何 FER 数字主张。** 本文件是 OpenSpec change
  `openspec/changes/nbpolar-r2-fer-measurement-contract/` 任务 **T2（R2-T2-MERGE）** 的产物。
- **合并依据（design D1）**：`FER_DEFINITION_DRAFT_20260922.md` 提供**规范正文**（FER 定义、
  点估计/CI、`undetected` 隔离、记账公式）；`ACQUISITION_SPEC_DRAFT_20260922.md` **降级为
  Annex A**（源选择、分支、预留段、噪声带、预算），只向本合同供应参数，不重定义 FER 语义。
  两份 2026-09-22 草稿保持原样不改；本文件为 additive 新文件。若合并后与草稿不一致，以本
  合同为准并**上报差异，不静默解决**（proposal「Source of truth」）。
- **Provenance（T1 引用，非新裁定）**：G4 inventory 同步已完成——`docs/decision-log.md`
  **2026-09-23** 条目「NB-Polar M2-prior G4 inventory COMPLETE」；M2 =
  `VALIDATED_AT_FROZEN_CONTRACT`（`docs/nbpolar/STATE.md` §4.1）。本合同仅**引用**该条目。
- **冻结前置条件**：本草稿须经 T3 独立冻结评审（含 draft-red-line → C-ID **总映射验收**，
  见 §7 占位）+ T4 PI 裁定（ledger `DECIDED` 行方可进入冻结正文）+ T5 配额算术，方可冻结。
  **T3 通过标准（R2-T2-FIX 明确；tasks 顺序 T2→T3→T4 不变）**：T3 评审时 §5 ledger 15 行全
  `PENDING`，因此 T3 只做**结构只读评审**（C1–C14 恰一、disjointness 无冲突重叠、
  红线映射总体性、D6 隔离、R-2 guard），其 PASS 是**结构 PASS、不判冻结通过**；冻结通过
  判定在 T4 裁定之后作出。design D3「未裁定行 blocks T3」按**阻塞冻结判定**读
  （design.md D3、tasks.md T3 已同步该通过标准）。若主线程认定其原意为**阻塞 T3 评审
  本身**（即需 T4→T3 改序），属 design/tasks 冲突，**上报主线程裁定**，本文件不自行改序。
  冻结前不得引用为已定口径，不得据此产生任何数字主张。
- **Stage-3 隔离（design D6）**：C1–C14 任何条款不得依赖、引入或部分执行 Stage-3
  （效率/净密钥）机械；C6/C7 仅记为**事后使用的记账约定**，其输入显式标注
  「本合同不测量」。R3 依赖不得回溯进入 R2。

---

## §0 本合并的 PENDING 欠项与归位状态（如实标记；**T3 只读核对、不裁定归属**——归位裁决属 PI（T4），归位写入属 T2）

| # | 欠项 | 状态 | 说明 |
|---|------|------|------|
| P1 | ACQ §8（测量时长 = 3 s、`600k`/`1p2M` 尺度 token 语义） | **RESOLVED — T4 PI placement** | T4 assigns ACQ §8 to C12. Provenance: `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication. |
| P2 | ACQ §10（预算数值与 stop 规则全文） | **RESOLVED — T4 PI placement; budget values still PENDING** | T4 assigns the remaining budget/STOP rules to C13; `ledger 不足 ⇒ INSUFFICIENT` remains in C11; one-shot review discipline remains in this change §8 + AGENTS.md §10.3. Budget values remain PENDING under D-ACQ-06. Provenance: `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication. |
| P3 | FER §5 的 R-3 对账（rule-of-three ↔ `FER < 0.003` aspiration） | **RESOLVED — 已归位（R2-T2-FIX）** | **单一承载处已确定：C9（边界：R3 条件 aspiration 不作 R2 sizing 依据、百块量级不可触及）+ C10（后果：Branch B ~1000 blocks 本次不按其 sizing）**；FER §5 对账小节原文不逐字复制（结论由 C9/C10 承载）。§7 R-3 行只引 C9/C10，「未归位」矛盾表述已删除。R-3 系已决主线裁定，非 PI 新裁项 |
| P4 | 术语映射表（两草稿术语 → 合同术语一一对应） | **PENDING** | 未随合并产出 |
| P5 | w(Δ) 换算式（最小可分辨差异 → 目标半宽 w 的显式公式） | **RESOLVED — T4 PI ruling** | T4 selected R-a and explicitly ruled `w(Δ) = Δ`; with Δ = 0.10, w = 0.10. Provenance: `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication. |
| P6 | RSS 1.13 GiB 出处 | **RESOLVED — 出处已标注（R2-T2-FIX）** | 出处经全仓 grep 核实并已在 C13 显式标注，两处表述已对齐：1.12 GiB = G2（`STATE.md` §1 G2 行「wall 855.1 s / RSS 1.12 GiB」）；**1.13 GiB = G3（`STATE.md` §1 G3 行「wall 858.5 s / RSS 1.13 GiB」，同值见 `docs/decision-log.md` G3 条目「RSS 1.13 GiB ≤ 2」）**。仅出处标注，不冻结任何预算数（数值仍属 D-ACQ-06/T4） |
| P7 | Decision ledger 表 | **PARTIALLY RECONCILED — T4 partial** | All 15 IDs remain present. D-FER-01..03 are transcribed as DECIDED from the explicit PI ruling. The four T5/T6 blockers are D-ACQ-02/03/05/06; other rows with no explicit row-level disposition remain PENDING. See §5 and `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication. |
| P8 | Clause-provenance disjointness 矩阵 | **PENDING** | 表已建并按 design D1 暂填 origin；**无冲突重叠的校验待 T3 只读核对，结论落表属 T2**（见 §4） |
| P9 | R-5（红线编号）来源 | **RESOLVED — removed by T4 PI ruling** | T4 removed R-5 and its mapping row because no source definition exists. The contract does not invent a definition. Provenance: `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication. |

---

## §1 规范条款 C1–C14（normative body）

条款编号与 `design.md` D1 表一一对应；每条**恰好出现一次**（T3 验收项）。

### C1 — 目的、范围、适用性与可比性边界

- 本合同预注册 R2 真实数据 FER 测量的口径、样本量推导链、预留段与预算约束。
- **跨契约 FER 数字不可比**：G1（w=500/LINEAR）vs G2（w=200/CIRCULAR）；合成 S9；
  G3 的 n=14 确认样本；任何 `undetected` 口径不一致的数据。
- Müller `FER < 0.003` 仅**可比且必须同句声明三点 caveat**：不同码族、不同信道、不同披露预算。
- **abstract/summary 禁令**：在 promotion ladder 到达 `FER_MEASURED_AT_CONTRACT` 之前，
  任何 FER 数字不得写入任何 abstract/summary。
- **Carried caveats（进入冻结版 §注，逐字承接 FER 草稿）**：
  - (a) w=200 窗截断总体（timing-truncated population）——任何 rate/效率/泄漏句必带；
  - (b) far-offset accidental 基线是结构化的，非均匀；
  - (c) 32-frame CAL 下 q_rest=0 是弱陈述（零观测上界 3/8192 = 3.66e-4）；
  - (d) L2 域必须声明 `u1`（polar 变换后）vs `high_hat`（未变换 high）——G2 Pre-RESULT domain trap。
- 来源：FER 草稿 §8 + Carried caveats (a)–(d)。

### C2 — 统计单位与 FER 定义

- **统计单位 = reconciliation block（R-1）：N = 32768 symbols = 128 acquisition frames ×
  256 pairs。不是 acquisition frame。**（本条**修正 design.md C1–C14 表 C2 行
  「Unit of analysis (frame)」的上一轮残留笔误**：FER 草稿 §1 R-1 已裁定单位为
  reconciliation block；acquisition frame 是测量切分 artifact，非 reconciliation 单位。
  任何 per-acquisition-frame 读数必须从本单位**显式派生**，不得替代本口径。）
- 形式定义（第 i 个 block 经冻结译码 + Toeplitz tag 判定后落入 §C5 taxonomy）：

```text
FER = (# verify_failed + # decode_failed)
    / (# exact + # verify_failed + # decode_failed)
```

- 分母 = 全部**有效** blocks；`undetected` 永不进入分子或分母（C4）；
  `resource_abort` / invalid-run 从分子分母**同时剔除**，计数另行披露（R-4，见 C5）。
- 来源：FER 草稿 §1/§2。

### C3 — 点估计与 CI（Wilson z=1.96，D-FER-01 已裁定）

- 点估计 `p̂ = FER` 配 **Wilson 95% 区间（z=1.96）**，与 G2/G3 gate 口径连续、跨 gate 可比。
- 备选 Clopper-Pearson exact 更保守、更宽，且破坏与 G2/G3 的 CI 可比性——按 T4 PI
  裁定不采用（**D-FER-01**）。
- 来源：FER 草稿 §4。

### C4 — `undetected` 隔离

- `undetected` **永不并入 success 或 FER**；分母分子均不含；逐 block 表**单列、单独计数**；
  摘要中单独一句话（FER 草稿 §6，R2 gate 要求）。`undetected > 0` 升级规则由 PI 冻结前裁定
  （D-FER-06，见 §5 ledger）。与 AGENTS.md §5.5 一致。
- 来源：FER 草稿 §6。

### C5 — Block-outcome taxonomy（R-4，固定）+ status 分离

| 判定 | FER 处理 | 备注 |
|---|---|---|
| `exact` | 成功（**仅分母**，不进分子） | tag 通过的完整块恢复 |
| `verify_failed` | **失败**（分子 + 分母） | 未恢复，按 eq(11) 计整块泄漏 |
| `decode_failed` | **失败**（分子 + 分母） | 未恢复，同上 |
| `undetected` | **隔离**：单列单计数，永不进入分子或分母 | 见 C4；AGENTS.md §5.5 |
| `resource_abort` / invalid-run | **R-4 双剔除**：从分子、分母**同时剔除**；被剔除的计数**必须披露** | 执行事故，非科学 FAIL |

- **五元 taxonomy**（`exact` / `verify_failed` / `decode_failed` / `undetected` /
  `resource_abort`）在逐 block 表中**分列**报告。
- **run-state 与 method `status` 严格分离**：上表是 *run-state* 语义，直接喂 FER
  分子/分母算术；它**不是**方法报告 `status` 词汇表（`reference`、`stub`、`unavailable`、
  `decode_failed`、`no_verified_success`、`ok` …，AGENTS.md §5.5）。方法 `status` 是
  结果行标签，**永不作为 FER 算术输入**；任何 `status` 值——以及任何 block-outcome 值——
  **不得被静默转写为 `ok`**。
- 来源：FER 草稿 §2/§3/§6（R-4）。

### C6 — `H(X|Y)` 替换口径与强制披露（D-FER-04）

- 任何 `H(q)` → 经验 `H(X|Y)` 替换必须在**冻结时预注册**（估计源、样本、偏差处理），
  事后替换禁止。**本合同不测量该输入**（D6 Stage-3 隔离）。
- 来源：FER 草稿 §7。待 T4 裁定 D-FER-04。

### C7 — `f_FER` / 效率记账：computed f vs stated f、泄漏分解（D-FER-05）

- FER 经 Martínez-Mateo `f_FER` 进入 Müller eq(11)/(13) 的 verification-aware 记账；
  失败 block 按 eq(11) 计整块泄漏。项级合同待 R3；本合同仅记为**约定、不测量**
  （D6 Stage-3 隔离）。待 T4 裁定 D-FER-05。
- 来源：FER 草稿 §7。

### C8 — per-acquisition-frame 派生读数规则（D-FER-07）

- 默认**不允许**以 acquisition frame 为读数单位；例外须预注册。派生读数为**次要、
  non-claim**，不得替代 C2 单位。待 T4 裁定 D-FER-07。
- 来源：FER 草稿 §1（R-1 派生规则）。

### C9 — 样本量 n 与目标半宽 w 的关系（D-FER-02/03；推导而非断言）

- **规划约束 R-2（大声）**：G2 B 臂 **3 failures / 14 attempts** 的结果**仅用于样本量
  sizing 与期望校准**；**禁止** FER-as-population 解读；**禁止**将该结果渲染为
  约 0.21 的 FER 表述出现在任何主张位置（G2 adjudication binding；AGENTS.md §5.5）。
  本合同正文不以 exact-count-over-total 或约 0.21 渲染该结果（R-2 string guard 见 §6）。
- 规划点 `p = 3/14 ≈ 0.214`，`pq ≈ 0.1684`，正态近似 `n ≈ z²·pq / w²`（z=1.96，
  w = 目标半宽；冻结前以 Wilson 精确式复核）：

| 目标半宽 w | 导出 n | 含义 |
|---|---|---|
| ±0.114 | 50 | 路线图下限；CI 宽，仅能分辨大效应 |
| ±0.100 | 65 | `3.8416×0.1684/0.01 ≈ 64.7 → 65` |
| ±0.080 | 100 | `3.8416×0.1684/0.0064 ≈ 101 → ~100`；路线图上限 |
| ±0.050 | 259 | `3.8416×0.1684/0.0025 ≈ 258.7 → 259`；超出 50–100，需 PI 另决 |

- **T4 PI ruling (D-FER-02)**：Δ = 0.10 under the single-method R-a convention and
  `w(Δ) = Δ = 0.10`. The direction remains one-way (difference → w → n → quota);
  this does not choose any acquisition quota.
- **指向说明（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：本表的
  `n=65`（基于 `p=3/14`）已被重新裁决为 **`n=56`**（基于 SCL(L=16) 真实数据
  27/28 结果的 Wilson 上界 `p≈0.1771`，`z=1.96`，`w=0.10`）**替代**；`n=65`
  行**保留、标注被替代**，不删除。详见 `docs/decision-log.md` 2026-09-28
  「数据使用规则修订 R1-R5 采纳」条目与本 change `tasks.md` D-FER-03 note。
- 注：**R-3 边界的唯一承载处 = 本条 C9（后果承载处 = C10 的 Branch B；§0 P3 已归位）**
  ——`FER < 0.003 @ 1000 samples` 系 R3 远期条件 aspiration，**不作 R2 sizing 依据**；
  百块量级在数学上不可触及该量级。FER §5 对账小节原文不逐字复制，其结论由 C9/C10 承载。
- 来源：FER 草稿 §5（R-2 + R-3 边界）；T4 PI values for D-FER-02/03 are recorded in §5.

### C10 — 采集分支、源清单、原始文件规则、参与/污染 ledger（永不回流）

- **分支与源（D-ACQ-01/02）**：Branch A（R2 执行分支，50–100 blocks）/ A′（w=±0.05
  时 ~260 blocks，PI 裁定）/ Branch B（R3 远期 ~1000 blocks，本次不按此 sizing）；
  源清单以解析后 ledger 为准。块数**从 C9 的推导承接，不独立选取**。
  （**R-3 后果的承载条款 = 本条**：`FER < 0.003` 所需 ~1000 blocks 量级仅属 R3，
  本次采集不按其 sizing——与 C9 的「不作 R2 sizing 边界」配套；§7 只引 C9/C10。）
- **原始文件规则（ACQ §7）**：只读 primary `<stem>.ttbin`（已验证 `FileReader`
  auto-follows `.1`；其余沿用 census 合并规则、未逐个重验者在 closure 时声明）；
  `results_*` / 分析副产物仅**名字级清点**（`ls`/`find` 层——**永不开内容、永不引用
  其中数字**）；POSIX/WSL 路径纪律，Windows 原始路径仅 provenance。
- **参与/污染 ledger（ACQ §9）——永不回流**：每个被 census/touch 过的 acquisition
  必须记入 participation/contamination ledger，含接触类型（decoder-free vs decoder）、
  日期、产物 id；**decoder 接触过的帧 NEVER 回流为确认样本（ledger 永不回流，
  §7/§9 双向一致）**。G3 的 independence 系 decoder/model independence，非 no-prior-contact。
- 来源：ACQ Annex A §2/§7/§9 + FER 草稿分支承接。
- **指向说明（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：`D-ACQ-02`
  源清单已裁决 = SHG `_1`/`_2` 全会话（不新增采集源）；"decoder 接触过的帧
  NEVER 回流"读法按新数据使用规则 R1/R2 收窄为——可复用，但须预冻结 + 全块
  报告 + 分层标注（见本 change `design.md` C10/C11 note 与
  `docs/nbpolar/DATA_LEDGER.md` §7）。详见 `tasks.md` D-ACQ-02 行与
  `docs/decision-log.md` 2026-09-28 条目。

### C11 — 预留段配额、Type0、reservation-partition 矩阵、COMPLETE-BLOCKS-ONLY

- **配额策略（D-ACQ-03/04）**：每个 acquisition 在切块前先切出独立确认 reserve
  （G3 模式推广）：**CAL / CHAR / HELDOUT / EVAL / RESERVE 五段互斥**。
- **reservation-partition 矩阵**：五段分配记入该矩阵——与 D4 的 clause-provenance
  disjointness 矩阵（§4）是**两个不同的 artifact、不同 subject**，不得混同。
- **Type0（D-ACQ-04）**：`Type0_nofilter_*` 是否纳入 R2 样本系独立决策；草稿默认
  (i) 不纳入；(ii) 纳入则**一律单列报告**，不与 SHG 混算 FER。in-scope ≠ 混算。
- **COMPLETE-BLOCKS-ONLY**：closure 时 EVAL 完整块不足 ⇒ `INSUFFICIENT` ⇒
  INCONCLUSIVE——**永不垫块、永不复用、永不缩 N**（ladder 耗尽警示先例：never-decoded
  101 frames，32f CAL 后 69 < 1 block）。禁止「用尽后再找块」。
- 来源：ACQ Annex A §4/§6。待 T4 裁定 D-ACQ-03/04。
- **指向说明（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：`D-ACQ-03`
  配额已裁决 = 每会话 32 块（0-1023→8 块 A1_CAL、1056-2397→10 块
  CHAR+HELDOUT 余 62 帧不用、2398-4189→14 块 EVAL），CAL32 仍 1024-1055
  排除；`D-ACQ-04`（Type0）不受影响、仍 PENDING。互斥要求收窄为"CAL32 与
  其余段互斥"（R3）。详见 `tasks.md` D-ACQ-03 行与 `docs/nbpolar/
  DATA_LEDGER.md` §7。

### C12 — 噪声带 / 工作点可比性（D-ACQ-05）

- 新采集噪声/工作点须与 SHG 可比；**任何差异必须在 closure 记录中声明**（亮度、损耗、
  计数率、符合窗、配对规则 W_P=200/CIRCULAR/skip 语义）。跨工作点优劣叙事禁止；
  工作点差异只用于限定 FER 陈述的适用域（声明制）。
- **ACQ §8 placement (P1)**: T4 PI assigned the duration (3 s) and `600k`/`1p2M`
  scale-token semantics (broadband-noise / maximum single-count scale parameters,
  not protocol identity) to C12. Annex A §8 remains the source text. This placement
  does not decide the D-ACQ-05 work-point tolerance or supply its missing lab inputs.
- 来源：ACQ Annex A §5；D-ACQ-05 remains PENDING.
- **指向说明（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：`D-ACQ-05`
  已裁决 = 适用域限定为"仅适用于 2026-01-13 两次 SHG 采集自身条件"（配置逐
  字段核实一致，`workspace/acq_inventory_20260928/REPORT.md:26-68`）；一般
  新采集可比性问题仍 PENDING。详见 `tasks.md` D-ACQ-05 行。

### C13 — 预算、wall/RSS/数据体积、≥2 sessions（D-ACQ-06/08）

- **数据体积单位（D5，冻结）**：128 frames × 256 pairs = **32768 symbols** per block
  （= N，FER 草稿 §1 的 R-1 单位——**不是「pairs」**）。
- 工作参考包络（G2/G3，**仅量级参考、未冻结**）：wall ≈ 855–858 s ≤ 900 s；
  RSS ≈ 1.12–1.13 GiB ≤ 2 GiB。**出处显式标注（§0 P6 已闭合，两处表述对齐）**：
  1.12 GiB = G2（`STATE.md` §1 G2 行「wall 855.1 s / RSS 1.12 GiB」）；
  1.13 GiB = **G3**（`STATE.md` §1 G3 行「wall 858.5 s / RSS 1.13 GiB」，同值见
  `docs/decision-log.md` G3 条目「RSS 1.13 GiB ≤ 2」）；具体预算数 T4 裁定（D-ACQ-06）。
- ≥2 独立 session 复现（路线图 R1 门）是否与 R2 同批满足待 T4 裁定（D-ACQ-08）。
- **预算只是对派生配额的约束（D2 step 4），从来不是冻结后改 w/n 的理由。**
- **ACQ §10 placement (P2)**: T4 PI assigned the remaining budget/STOP rules to C13;
  `ledger 不足 ⇒ INSUFFICIENT` remains in C11; Tier-Y one-shot/Pre-EXECUTE/Pre-RESULT
  discipline remains in this change §8 + AGENTS.md §10.3. Budget values remain PENDING
  under D-ACQ-06; no budget number is frozen by this placement.
- 来源：ACQ Annex A §3/§10 + design D5。

### C14 — 合同继承与 `undetected > 0` 升级（D-FER-06, D-ACQ-07）

- 本合同口径（C1–C14）**继承进后续 change**；配对/构造契约（W_P/W_S/MOD/skip/
  K1/K2/P16）默认继承冻结契约，任何偏离需单独立项（D-ACQ-07）。
  `undetected > 0` 的升级处理由 PI 冻结前裁定（D-FER-06，见 §5 ledger）。
- 来源：FER 草稿 §6 + ACQ Annex A（OPEN DECISIONS）。

---

## §2 D2 — 推导次序：difference → w → n → quota（严格单向）

1. PI 陈述**最小可分辨差异 Δ**（测量必须能分辨的效应量）。
2. **Δ 单向决定目标半宽 w**（C9）。**vs D-FER-02 的排序规则（固定——只有一种：
   difference 单向 supersedes）**：w 是在冻结 CI 约定下**从 Δ 导出**的；PI 作为
   D-FER-02 裁定的值**必须等于**该导出 w。与导出 w 不一致的 D-FER-02 值作为**冲突**
   上报 PI（D-ACQ-06 式升级），**永不通过重述 difference 来调和**。两个输入**不是**
   互相印证关系：difference → w 严格单向，**永不先选 w 再倒推拟合 difference**。
   （T4 PI ruled `w(Δ) = Δ` under R-a；§0 P5。）
3. w 在冻结 CI 约定（Wilson，z=1.96，除非 D-FER-01 改变）下决定**样本量 n**。
4. n 由 T5 纯算术决定**配额**（frames × pairs）。

**没有任何配额是先选好再事后辩护的。** 若导出配额超出 C13 预算，作为
D-ACQ-06 与 discriminable difference 之间的冲突上报 PI，**不静默权衡**。

## §3 D3 — 三态裁定

每项 PI 决定（D-FER-01..07、D-ACQ-01..08）恰好进入一态：
`DECIDED(value)` / `DEFERRED(reason, retrigger)` / `NOT_APPLICABLE(reason)`。
未裁定行**阻塞 T3 的冻结通过判定**（T3 在未裁定状态下仍执行结构只读评审并可给结构
PASS/FAIL，但**不得判冻结通过**——通过标准见页首「冻结前置条件」与 §8 第 0 条；
design/tasks 冲突若有则上报主线程，不在此静默改序）；仅 `DECIDED` 行进入冻结正文，
`DEFERRED` 行进入明确标注的
open-decision 表，`deferred` 项不得被引为已冻结。

---

## §4 Clause-provenance disjointness 矩阵（**PENDING：待 T3 只读核对，结论落表属 T2**）

> 状态 **PENDING**（§0 P8）：origin 列按 design D1 暂填；**「无冲突重叠」的校验尚未作出
> ——由 T3 只读评审核对并报告 PASS/FAIL（FAIL ⇒ 退回 T2）；T3 不写本文件，校验结论
> 落表由 T2 执行**。表中 `PENDING (T3)` 即「待 T3 只读核对」。T2 过程中如发现重叠，
> 上报 PI，不自动解决。
> 本矩阵是 **document 矩阵**，与 C11 的 **reservation-partition 矩阵**
> （CAL/CHAR/HELDOUT/EVAL/RESERVE 互斥）是**两个不同 artifact**（design D4 双矩阵区分）。

| Clause | FER 草稿（normative body） | ACQ 草稿（Annex A） | 冲突重叠校验 |
|---|---|---|---|
| C1 | §8 + caveats (a)–(d) | — | PENDING (T3) |
| C2 | §1/§2 | — | PENDING (T3) |
| C3 | §4 | — | PENDING (T3) |
| C4 | §6 | — | PENDING (T3) |
| C5 | §2/§3/§6 | — | PENDING (T3) |
| C6 | §7 | — | PENDING (T3) |
| C7 | §7 | — | PENDING (T3) |
| C8 | §1 | — | PENDING (T3) |
| C9 | §5 | 承接（§2 不另选数字） | PENDING (T3) |
| C10 | 分支承接 | §2/§7/§9 | PENDING (T3) |
| C11 | — | §4/§6 | PENDING (T3) |
| C12 | — | §5 + §8 placement (T4: P1) | PENDING (T3) |
| C13 | — | §3/§10 placement (T4: P2; budget values remain D-ACQ-06) | PENDING (T3) |
| C14 | §6 | OPEN DECISIONS | PENDING (T3) |
| *（分解承载/占位）* | §5 R-3 对账 → **C9（边界）+ C10（后果）**，已归位 | §8 → **C12**；§10 → **C13**（预算/STOP）+ **C11**（INSUFFICIENT） | T4 placement decisions are recorded in §0; T3 only checks mapping structure |

## §5 Decision ledger（T4 partially adjudicated; T5/T6 remain blocked）

> The 2026-09-24 T4 PI record explicitly decides D-FER-01..03. The four inputs
> explicitly named as blocking T5/T6 are D-ACQ-02/03/05/06. D-FER-04..07 and
> D-ACQ-01/04/07/08 have no row-specific disposition in that record and remain
> PENDING; no state is inferred from aggregate wording. Any PENDING row blocks
> the freeze verdict under D3. The current draft is not frozen. Provenance for
> transcribed decisions: `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication.
> Columns: `ID | clause | question |
> adjudication state | value/rationale | date`。

| ID | clause | question | adjudication state | value/rationale | date |
|---|---|---|---|---|---|
| D-FER-01 | C3 | CI 方法（Wilson z=1.96 vs exact） | `DECIDED` | Wilson 95% CI, z=1.96. PI ruling: decision-log, 2026-09-24 R2 T4. | 2026-09-24 |
| D-FER-02 | C9 / D2 | 目标半宽 w（必须等于 Δ 导出值） | `DECIDED` | Δ=0.10; R-a; `w(Δ)=Δ=0.10`. PI ruling: decision-log, 2026-09-24 R2 T4. | 2026-09-24 |
| D-FER-03 | C9 | 样本量 n（由 w 导出） | `DECIDED` (2026-09-24 value **SUPERSEDED** 2026-09-28) | ~~p=3/14 sizing input; n=65 valid complete blocks (Wilson minimum 63; 65 selected conservatively).~~ **2026-09-28 按新 p 重新裁决 n=56（替代 65）**: Wilson-upper `p≈0.1771` on the SCL(L=16) real-data 27/28 result, `z=1.96`, `w=0.10` (`design.md` D6(ii) of `nbpolar-data-use-rules-revision`); `n=65` retained above as the superseded 2026-09-24 value, not deleted. Report observed intervals without a post-hoc half-width ≤0.10 guarantee. PI rulings: decision-log, 2026-09-24 R2 T4 and 2026-09-28 "数据使用规则修订 R1-R5 采纳". | 2026-09-24; superseded 2026-09-28 |
| D-FER-04 | C6 | `H(q)`→经验 `H(X|Y)` 替换口径 | `PENDING` | — | — |
| D-FER-05 | C7 | `f_FER` 记账式冻结 | `PENDING` | — | — |
| D-FER-06 | C4/C14 | `undetected > 0` 升级规则 | `PENDING` | — | — |
| D-FER-07 | C8 | per-frame 派生读数允许条件 | `PENDING` | — | — |
| D-ACQ-01 | C10 | 执行分支（A / A′ / B）与目标 n、w | `PENDING` | — | — |
| D-ACQ-02 | C10 | 采集源清单 | `DECIDED` | SHG `_1`/`_2`, full sessions (no new acquisition). PI ruling: decision-log, 2026-09-28 "数据使用规则修订 R1-R5 采纳"; values in `docs/nbpolar/DATA_LEDGER.md` §7. | 2026-09-28 |
| D-ACQ-03 | C11 | 每 acquisition 预留段配额 | `DECIDED` | Per session (32 blocks): frames 0-1023 → 8 blocks (`A1_CAL_characterization`); 1056-2397 → 10 blocks, 62f unused (`HELDOUT_model_selection`); 2398-4189 → 14 blocks (`EVAL_already_decoded`); CAL32 stays 1024-1055 (32f, excluded). 64 blocks total. PI ruling: decision-log, 2026-09-28. D-ACQ-04 remains separately PENDING. | 2026-09-28 |
| D-ACQ-04 | C11 | Type0 纳入与否及报告方式 | `PENDING` | — | — |
| D-ACQ-05 | C12 | 噪声/工作点可接受差异带 | `DECIDED` | Scope narrowed to "applies only to the two 2026-01-13 SHG acquisitions' own conditions" (config verified identical, `workspace/acq_inventory_20260928/REPORT.md:26-68`). General new-source comparability remains open for any future acquisition. PI ruling: decision-log, 2026-09-28. D-ACQ-08 remains separately PENDING. | 2026-09-28 |
| D-ACQ-06 | C13 | 预算数（单块 wall/RSS、总 wall/RSS） | `PENDING` | Explicit T5/T6 blocker: PI limits plus lab/operations machine and parallelism inputs required; see Open Inputs item 4. | — |
| D-ACQ-07 | C14 | 配对/构造契约沿用 | `PENDING` | — | — |
| D-ACQ-08 | C13 | 独立 session 最低会话数（≥2） | `PENDING` | — | — |

另：Δ 与 R-a 已由 T4 明确裁定（见 D-FER-02）；K_total remains at the G2/G3 frozen
configuration (`K1=319, K2=6492`); fixed-f=1.3 is only a future rate-change planning
direction and requires its own freeze. These K_total details are outside the 15 D-ID rows.
Provenance: `docs/decision-log.md`, 2026-09-24 R2 T4 PI adjudication.

## §6 R-2 string guard（T2 验证记录）

- Guard 对象：合并稿中**不得**出现将 G2 B 臂结果作为 FER 主张的 exact-count-over-total
  渲染或其约 0.21 的 FER 表述（**sizing 用途不受限**：3/14 规划点见 C9，属 R-2 允许的
  sizing/校准）。guard 采用 grep 复验：上述两个禁止字面串在本文件中**零命中**。
- T2 自检：本文件正文**无任何 FER 数字主张**；
  无 abstract/summary、无测量结果、无授权文本。C9/§1/Annex A 的 3/14、w/n 表均为
  **sizing 推导**，非 FER-as-population 解读。
- 状态：**PENDING T3 复核**（T3 独立 grep 复验）。

## §7 T3 总映射验收占位（draft-red-line → C-ID total mapping）

> T3 独立只读评审在此表**逐项只读核对**并给出 PASS/FAIL 报告（**报告不写入本文件**）；
> 每条红线（复合来源节先拆为原子规则，各原子规则恰好一个承载）映射到**恰好一个** C 条款、
> 无双重规定、无红线遗漏。**FAIL ⇒ 退回 T2 修订；归位/落表等写操作由 T2 执行，归位裁决
> 属 PI（T4）。T3 评审时 §5 ledger 全 `PENDING`，当时的 T3 PASS 仅为结构 PASS、不判冻结通过
> （见页首「冻结前置条件」）。**

| 红线 / caveat / 硬规则 | 映射条款 | T3 验收 |
|---|---|---|
| R-1 单位 = reconciliation block (32768 symbols) | C2 | PENDING |
| R-2 3/14 仅 sizing、禁 FER-as-population | C9 + §6 guard | PENDING |
| R-3 rule-of-three / 0.003 边界 | **C9（不作 R2 sizing 边界）+ C10（Branch B 后果）——唯一承载处，§0 P3 已归位** | PENDING |
| R-4 taxonomy + resource_abort 双剔除 | C5 | PENDING |
| FER §6 `undetected` 分列报告 | C4 (+C5) | PENDING |
| FER §8 可比性 + abstract/summary 禁令 | C1 | PENDING |
| Carried caveats (a)–(d) | C1 | PENDING |
| ACQ §2 推导（块数不独立选取） | C9/C10 | PENDING |
| ACQ §4 reservation partition + COMPLETE-BLOCKS-ONLY ⇒ INSUFFICIENT | C11 | PENDING |
| ACQ §5 工作点声明 | C12 | PENDING |
| ACQ §7 raw-file rules | C10 | PENDING |
| ACQ §9 ledger no-reflow | C10 | PENDING |
| ACQ §8 尺度 token / 时长 | **C12 (T4 PI placement; §0 P1)** | PENDING (T3 review status) |
| ACQ §10 预算与 stop 规则 | **预算/剩余 STOP → C13；`ledger 不足 ⇒ INSUFFICIENT` → C11 (T4 PI placement; §0 P2)** | PENDING (T3 review status) |

## §8 门序与授权后置声明（T3 结构评审 → T4 → T5 → T6）

0. **T3 — 结构只读评审（先于 T4，tasks 顺序不变）**：T3 评审时 §5 ledger 15 行全 `PENDING`
   的当前状态下，T3 只做结构评审（C1–C14 恰一、disjointness 无冲突重叠、红线映射
   总体性、D6 隔离、R-2 guard），**不判冻结通过**；PASS 仅代表结构合格，FAIL ⇒ 退回 T2。
   冻结通过判定在 T4 裁定之后作出（design D3「blocks T3」读作阻塞**冻结判定**；
   若主线程读作阻塞评审本身、需 T4→T3 改序，属 design/tasks 冲突，**上报主线程**）。

1. **T4 — PI 裁定**：adjudicate §5 ledger 至 `DECIDED` / `DEFERRED` /
   `NOT_APPLICABLE`，锁定 w 与 n、Δ、K_total 约定。**阻塞 T5**（planner 不得自裁）。
2. **T5 — 配额算术**：按 D2 冻结方向 difference → w → n → **quota**，纯算术、
   记录单位与公式；与 C13 预算冲突上报 PI，不自行权衡。**阻塞 T6**。
3. **T6 — Tier-Y packet skeleton**：仅在 T4、T5 **均完成后**运行；每个冻结字段写自
   T4 已裁 ledger 与 T5 算术，**T4/T5 完成前不得写任何冻结字段**，不得编造阈值/预算数
   填槽；`authorizations: []` 恒空、不可执行。
4. **授权后置（Scope OUT）**：本 change **不生成** `AUTHORIZATION_PROMPT.md`、不含任何
  逐字授权文本、**不授予任何授权**——该 artifact 只能在日后明确的用户指令下生成，
  现在**不得生成**。T7 采集、T8 译码/测量执行、T9 Pre-RESULT/数字发布均
  **NOT AUTHORIZED**（tasks T7–T9、proposal Scope OUT、O-list O1–O4）。

---

*本文件为 T2 docs-only 合并草稿；additive only。两份 2026-09-22 草稿与
`STATE.md` 均未被修改。T4 PI adjudication is partial: explicit rulings and placements
are recorded in §0/§5/§7; open row states and four T5/T6 blockers remain visible there.
The contract is NOT frozen and no execution is authorized.*
