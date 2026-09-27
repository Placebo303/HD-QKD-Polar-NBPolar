# R2 待决输入清单（OPEN INPUTS DECISION LIST）— 20260925 — DRAFT

- **性质：DRAFT 规划输入**。不改变任何状态串、不冻结任何数、不含任何 FER/效率/密钥数字主张、不授予任何授权。
- **状态基线（只读引用，不改）**：M2 = `VALIDATED_AT_FROZEN_CONTRACT`；R2 合同 NOT frozen；T5/T6 NOT authorized；T7–T9 NOT AUTHORIZED。
- **依据（只读，未修改任何源文件）**：
  - `openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md:73` 待决表（四项 PENDING 阻塞 T5/T6）与 `tasks.md:57` 边界（T4 门：仅 `DECIDED` 行进冻结正文；T5 阻塞至 T4 完成；不得由 n=65 反推配额/预算；不得写占位冻结数）；
  - `docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`（C10/C11/C12/C13、§0 P1/P2/P6、§5 ledger D-ACQ-02/03/05/06/08、D2 单向）；
  - `docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md`（§2–§10、OPEN DECISIONS D-ACQ-01..08）；
  - `docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md`（R-2 sizing、C9 推导、§8 可比性）；
  - `docs/nbpolar/STATE.md`（G2/G3 包络出处、ladder 耗尽 101 frames）；
  - `docs/decision-log.md` 2026-09-24 条目（Δ/R-a/w/n 裁定 + 四项 PENDING 阻塞 T5/T6 + 禁止反推）。
- **纪律**：不得由 n=65 反推任何配额/预算；不得给推荐数值（下文数值位一律“待填 + 单位”）；T4 裁定前不得写任何冻结字段，不得编造阈值/预算数填槽。

---

## 待决 1 — 新采集实际来源清单（Source list）→ C10（D-ACQ-02）

- **待决项**：哪些 acquisition 源可供应 R2 确认块（SHG 新采清单；候选 Type-II 是否在列另由 D-ACQ-04 定单列与否）。
- **为什么不能在盘上从现有数字推出**：既有 ledger（G2/G3 所用 SHG `_1`/`_2` 解析结果）是**已用旧 session**的确认样本，已消耗（EVAL 已用、RESERVE  untouched 计数已知但属旧源保留段），且受 C10 “decoder 接触过的帧 NEVER 回流”约束，不可复用为新确认样本；跨 session 复用违反 session 独立性；G1（w=500/LINEAR）与 G2/G3（w=200/CIRCULAR）口径不同，不可比（C1）；`RAW_DATA_INVENTORY` 只覆盖旧源普查，未含新采文件。
- **需要 PI 或实验室提供的具体输入（字段级）**：
  - `session_id`（待填，字符串）；
  - `acquisition_date`（待填，日期）；
  - `frame_range_start/end`（待填，帧号；含 dropped/excluded 说明）；
  - `file_format`（待填，如 `<stem>.ttbin` + `.1` 跟随规则确认）；
  - `validation_status`（待填，如 FileReader census 事件数/合并规则沿用声明）；
  - `participation_ledger` 解析结果（待填：接触类型 decoder-free vs decoder、日期、产物 id）。
- **可行的获取途径（谁、什么动作）**：PI 指定源范围；**实验室联络人**提供新采文件清单 + 采集单；decoder-free census 解析后 ledger 落表（planner/coder 不自采、不自定源）。
- **落到 C 哪一条**：**C10**（分支与源、原始文件规则、参与/污染 ledger 永不回流）。
- **Owner**：PI（裁决）/ 实验室联络人（提供清单）。
- **retrigger**：`retrigger=parsed ledger arrival`（tasks.md:73）；T4 前不消耗任何源。
- **若缺失的后果**：D-ACQ-02 保持 PENDING → **阻塞 T5/T6**（tasks.md:57 GATE-T5/T6）；任何提前采集/读取/译码属 T7/T8 越界（NOT AUTHORIZED）。

## 待决 2 — CAL/EVAL/RESERVE 配额（Partition quotas）→ C11（D-ACQ-03；Type0 D-ACQ-04 同条）

- **待决项**：每 acquisition 的段划分规则与帧数配额（CAL / CHAR / HELDOUT / EVAL / RESERVE 五段互斥，记入 reservation-partition 矩阵）。
- **为什么不能在盘上从现有数字推出**：n=65 只给**有效完整块样本量**（C9 由 w 导出的 sizing），不给段划分；EVAL 帧数下限（128×n）是纯算术，未含 §4 开销；G3 模式数字与 32f CAL 先例是**未冻结参考/弱陈述**（caveat (c)：32-frame CAL 下 q_rest=0 是零观测上界，非配额冻结）；ladder 耗尽先例（101 frames → 32f CAL 后 69 < 1 block）只证明须预留，不给出新采配额数。
- **需要 PI 或实验室提供的具体输入（字段级）**：
  - `partition_rule`（待填：按帧数比例 vs 固定帧数，二选一）；
  - `CAL_frames`（待填，单位 frames）；
  - `CHAR_frames`（待填，单位 frames）；
  - `HELDOUT_required`（待填，是/否）+ `HELDOUT_frames`（待填，单位 frames）；
  - `EVAL_frames/blocks`（待填，单位 frames/blocks）；
  - `RESERVE_frames/blocks`（待填，单位 frames/blocks）；
  - `Type0_handling`（D-ACQ-04：不纳入 vs 纳入一律单列，不混算 FER）。
- **可行的获取途径（谁、什么动作）**：PI 裁定划分规则与各段帧数；实验室确认单次采集长度是否容纳该划分；T5 按 D2 纯算术记录（单位与公式），不自裁。
- **落到 C 哪一条**：**C11**（预留段配额、Type0、reservation-partition 矩阵、COMPLETE-BLOCKS-ONLY ⇒ INSUFFICIENT）。
- **Owner**：PI。
- **retrigger**：`retrigger=T5 quota arithmetic; must be fixed before T5`（tasks.md:73）。
- **若缺失的后果**：T5 无法运行（GATE-T5），T6 冻结字段无源可写（GATE-T6 禁写占位）；强行配额 = 自造冻结数，违反 D2 单向与 tasks.md:57 边界；closure 块不足时无 INSUFFICIENT 语义可依。

## 待决 3 — 工作点可比条件（Comparability conditions）→ C12（D-ACQ-05；sessions 子项 C13/D-ACQ-08）

- **待决项**：新采集与哪一基线可比、噪声/工作点差异带、是否需要 ≥2 session。
- **为什么不能在盘上从现有数字推出**：盘上只有**不可比清单**（C1：跨契约 G1 vs G2、合成 S9、G3 n=14 确认样本、`undetected` 口径不一致）与声明制要求（C12：差异必须声明、跨工作点优劣叙事禁止），无可接受差异带数值；对标基线（ locked 二元 Release 的哪一口径）、是否同配对、PIE 分母定义是科学判断，非测量算术；D-ACQ-08（≥2 session 是否同批满足）是路线图 R1 门决策，不在 n=65 内。
- **需要 PI 或实验室提供的具体输入（字段级）**：
  - `baseline_id`（待填：对标的二元 Release 版本/口径）；
  - `same_pairing_required`（待填：是/否；W_P/W_S/MOD/skip 语义说明）；
  - `PIE_denominator_def`（待填，字符串）；
  - `workpoint_params`（实验室提供实测值：亮度/损耗/计数率/符合窗/配对规则，单位随参数）；
  - `tolerance_band`（待填 + 单位，按上条参数逐项）；
  - `sessions_required`（D-ACQ-08，待填：会话数；是否与 R2 同批满足，是/否）。
- **可行的获取途径（谁、什么动作）**：PI 裁定对标基线 + 差异带 + sessions；**实验室联络人**提供新采工作点实测参数（采集单原样记录 token，不解读协议版本）；closure 记录声明制落盘。
- **落到 C 哪一条**：主 **C12**（D-ACQ-05 噪声带/工作点可比性）；sessions 子项 **C13**（D-ACQ-08 ≥2 sessions）。
- **Owner**：PI（裁决）/ 实验室联络人（提供工作点参数）。
- **retrigger**：`retrigger=paired-design item; R2 rows stay single-method until decided`（tasks.md:73）；sessions 子项按 C13。
- **若缺失的后果**：FER 陈述适用域无法限定，任何跨工作点比较违反 C1/C12（优劣叙事禁止）；sessions 未决则 `READY_FOR_QUALIFICATION` 合取项悬空；R2 行保持单方法，不得写配对比较行。

## 待决 4 — 执行预算（Budget numbers）→ C13（D-ACQ-06）

- **待决项**：单块 wall/RSS 上界、总 wall/RSS 上限、机器/并行度约束（含超预算 STOP 语义）。
- **为什么不能在盘上从现有数字推出**：G2/G3 包络（wall ≈855–858 s ≤900 s；RSS ≈1.12–1.13 GiB ≤2 GiB，出处 §0 P6 已闭合：1.12=G2、1.13=G3）合同明标**仅量级参考、未冻结**，不能当作预算数；预算须按 T5 派生配额 + 实际机器约束重定；由 n=65 反推 wall/RSS 须自造解码成本模型，属禁止的反推（decision-log 2026-09-24 + tasks.md:57）；D2 step 4 预算只是对配额的约束，从不是改 w/n 的理由。
- **需要 PI 或实验室提供的具体输入（字段级）**：
  - `wall_per_block`（待填，单位 s）；
  - `rss_per_block`（待填，单位 GiB/MiB）；
  - `wall_total`（待填，单位 s）；
  - `rss_total`（待填，单位 GiB）；
  - `machine_spec`（待填：机器型号/配置）；
  - `parallelism`（待填：并发数/独占与否）；
  - `stop_on_overbudget`（待填：超预算 ⇒ STOP 不调参；其余 STOP 归位目标 C13 待 PI，§0 P2）。
- **可行的获取途径（谁、什么动作）**：PI 冻结预算数；实验室/运维确认机器与并行度；T5 作 S4 配额 vs 预算对账，冲突上报 PI、不权衡。
- **落到 C 哪一条**：**C13**（D-ACQ-06；D2 step 4 预算语义承载处；其余 STOP 占位归位目标亦 C13，§0 P2）。
- **Owner**：PI。
- **retrigger**：`retrigger=S4 quota vs budget reconciliation; conflict is escalated, never traded off`（tasks.md:73）。
- **若缺失的后果**：T5 对账无基准、T6 预算字段不得写占位（GATE-T6）；无预算执行违反 Pre-EXECUTE 门，T8 仍 NOT AUTHORIZED；超预算无 STOP 语义则 Tier-Y one-shot 纪律缺口。

---

## 声明

- 本文件**未填任何数值**（数值位一律“待填 + 单位”；引用的 Δ/R-a/w/n、G2/G3 包络、G3 模式数字均为对已决条目/未冻结参考的**只读引用**，非新冻结）。
- 本文件**未冻结**任何条款（C10/C11/C12/C13 归位待 T4 PI 裁定；T2 写入与 T3 结构评审不受本文件影响）。
- 本文件**未授权**任何执行（T5/T6 仍阻塞；T7 采集/T8 译码/T9 发布仍 NOT AUTHORIZED；`authorizations: []` 不变）。
