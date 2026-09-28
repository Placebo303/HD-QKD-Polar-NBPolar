# R2 T4 PI 决策卡片 — 2026-09-27（**不含任何推荐数值，不代裁**）

- **性质**：为 `openspec/changes/nbpolar-r2-fer-measurement-contract` 的 T4 阶段准备**一句话可裁**的输入卡。
- **纪律（绑定）**：本文件**不填任何数值位**；所有待填位置一律写作 `<待填 · 单位>`。
  不出现 "建议采用 / 推荐 / 应当选" 之类倾向性措辞；不引用任何 Tier-X 数字作为 sizing 依据
  （`tasks.md:57` 边界）；不改变任何 `PENDING` 状态；不授予任何授权。
- **来源（只读引用）**：`openspec/changes/nbpolar-r2-fer-measurement-contract/{tasks.md:74-95,design.md:142-143}`、
  `docs/nbpolar/R2_OPEN_INPUTS_DECISION_LIST_20260925.md`、同 change 的 `tasks.md:85-90` 阻塞表。
- **已决背景（不变）**：D-FER-01..03 已 PI 裁决（Δ=0.10 / R-a / w=0.10 / p=3/14 / z=1.96 / n=65）；
  K_total 仍为 G2/G3 的 K1=319/K2=6492；R2 合同 **NOT frozen**；T5/T6 阻塞；T7/T8/T9 NOT AUTHORIZED。

---

## 卡 1 — D-ACQ-02：新采集源清单 → C10

**① 待决项原文**（`R2_OPEN_INPUTS_DECISION_LIST_20260925.md:18`）
> 哪些 acquisition 源可供应 R2 确认块（SHG 新采清单；候选 Type-II 是否在列另由 D-ACQ-04 定单列与否）。

**② 可选项（互斥）**

| 选项 | 含义 | 后果 |
|---|---|---|
| O-2a | 只列入明确指定的新采 session 清单 | 范围最小、污染 ledger 最易闭合；源数量可能不足 n=65 |
| O-2b | 新采清单 + Type-II 单列（不混算 FER） | 样本池更大；须额外维护单列口径与不混算约束 |
| O-2c | 暂不列源，保持 PENDING 到实验室清单到达 | T5/T6 维持阻塞，R2 合同继续不可冻结 |

**③ 需要的外部字段（含单位）**：`session_id`（字符串）｜`acquisition_date`（日期）｜
`frame_range_start/end`（帧号，含 dropped/excluded 说明）｜`file_format`（如 `<stem>.ttbin` + `.1` 跟随规则确认）｜
`validation_status`（FileReader census 事件数 / 合并规则沿用声明）｜
`participation_ledger` 解析结果（接触类型 decoder-free vs decoder、日期、产物 id）

**④ 若本轮不裁**：D-ACQ-02 保持 PENDING → 阻塞 T5/T6（`tasks.md:57` GATE-T5/GATE-T6）。
**⑤ Owner / retrigger**：PI（裁决）/ 实验室联络人（提供清单）；`retrigger=parsed new-source ledger arrival; no source is consumed before T4`。

**已裁决（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：`D-ACQ-02 = SHG _1/_2 全会话`（不新增采集源）；值与出处见 `tasks.md` 阻塞表与 `docs/nbpolar/DATA_LEDGER.md` §7。

---

## 卡 2 — D-ACQ-03：五段分区配额 → C11（含 Type0 的 D-ACQ-04）

**① 待决项原文**（`:35`）
> 每 acquisition 的段划分规则与帧数配额（CAL / CHAR / HELDOUT / EVAL / RESERVE 五段互斥，记入 reservation-partition 矩阵）。

**② 可选项（互斥）**

| 选项 | 含义 | 后果 |
|---|---|---|
| O-3a | 按帧数比例划分 | 跨不同长度的采集可迁移；需确认每段的比例值来源 |
| O-3b | 固定帧数划分 | 各段绝对量稳定；需确认单次采集长度能容纳该划分 |
| O-3c | 维持 PENDING，待采集容量确认后再裁 | T5 配额算术无源可写，T6 不得写占位 |

**③ 需要的外部字段（含单位）**：`partition_rule`（O-3a / O-3b 二选一）｜`CAL_frames`（frames）｜
`CHAR_frames`（frames）｜`HELDOUT_required`（是/否）+ `HELDOUT_frames`（frames）｜
`EVAL_frames/blocks`（frames / blocks）｜`RESERVE_frames/blocks`（frames / blocks）｜
`Type0_handling`（D-ACQ-04：不纳入 vs 纳入一律单列，不混算 FER）

**④ 若本轮不裁**：T5 无法运行；closure 块不足时无 `COMPLETE-BLOCKS-ONLY ⇒ INSUFFICIENT` 语义可依。
**⑤ Owner / retrigger**：PI；`retrigger=T5 quota arithmetic; must be fixed before T5`。

**已裁决（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：每会话 32 块（0-1023→8 块 A1_CAL、1056-2397→10 块 CHAR+HELDOUT 余 62 帧不用、2398-4189→14 块 EVAL），CAL32 仍 1024-1055 排除；`Type0_handling` 未变（D-ACQ-04 仍 PENDING）。值与出处见 `tasks.md` 阻塞表与 `docs/nbpolar/DATA_LEDGER.md` §7。

---

## 卡 3 — D-ACQ-05：工作点可比性 → C12（sessions 子项 → C13 / D-ACQ-08）

**① 待决项原文**（`:53`）
> 新采集与哪一基线可比、噪声/工作点差异带、是否需要 ≥2 session。

**② 可选项（互斥）**

| 选项 | 含义 | 后果 |
|---|---|---|
| O-5a | 与单一指定基线口径对齐，差异带逐参数声明 | FER 陈述适用域可限定；跨工作点优劣叙事仍禁止 |
| O-5b | 不指定基线，只做单方法 FER 陈述 | 适用域最窄；与既有二元结果的关系无法表述 |
| O-5c | 维持 PENDING | `READY_FOR_QUALIFICATION` 的 sessions 合取项继续悬空 |

**③ 需要的外部字段（含单位）**：`baseline_id`（对标的二元 Release 版本/口径）｜
`same_pairing_required`（是/否；含 W_P/W_S/MOD/skip 语义说明，W_P 单位 ps）｜
`PIE_denominator_def`（字符串）｜`workpoint_params`（亮度/损耗/计数率/符合窗/配对规则，单位随参数）｜
`tolerance_band`（逐参数待填 + 单位）｜`sessions_required`（会话数；是否与 R2 同批满足，是/否）

**④ 若本轮不裁**：FER 陈述适用域无法限定；任何跨工作点比较违反 C1/C12。
**⑤ Owner / retrigger**：PI（裁决）/ 实验室联络人（提供工作点参数）；
`retrigger=paired-design item; R2 rows stay single-method until decided`。

**已裁决（2026-09-28，`nbpolar-data-use-rules-revision` T1）**：适用域限定为
"仅适用于 2026-01-13 两次 SHG 采集自身条件"（配置逐字段核实一致，
`workspace/acq_inventory_20260928/REPORT.md:26-68`）；`sessions_required`
等一般新采集可比性问题仍 PENDING（本裁决不含新采集）。值与出处见 `tasks.md`
阻塞表与 `docs/nbpolar/DATA_LEDGER.md` §7。

---

## 卡 4 — D-ACQ-06：执行预算 → C13

**① 待决项原文**（`:70`）
> 单块 wall/RSS 上界、总 wall/RSS 上限、机器/并行度约束（含超预算 STOP 语义）。

**② 可选项（互斥）**

| 选项 | 含义 | 后果 |
|---|---|---|
| O-6a | 冻结单块 + 总量双上限，并定义超预算 STOP（不调参） | T5 可对账、T6 可写预算字段；需机器实测约束 |
| O-6b | 只冻结单块上限，总量待 T5 对账后再定 | T6 总量字段留空，须显式标注未冻结 |
| O-6c | 维持 PENDING | T5 对账无基准；无预算执行违反 Pre-EXECUTE 门 |

**③ 需要的外部字段（含单位）**：`wall_per_block`（s）｜`rss_per_block`（GiB 或 MiB）｜
`wall_total`（s）｜`rss_total`（GiB）｜`machine_spec`（机器型号/配置）｜
`parallelism`（并发数 / 是否独占）｜`stop_on_overbudget`（超预算 ⇒ STOP 不调参）

**④ 若本轮不裁**：T5 对账无基准；T6 预算字段不得写占位；T8 仍 NOT AUTHORIZED。
**⑤ Owner / retrigger**：PI（冻结预算数）/ 实验室与运维（确认机器与并行度）；
`retrigger=S4 quota vs budget reconciliation; conflict is escalated, never traded off`。

**已裁决（2026-09-27）**：`D-ACQ-06 = O-6a ; wall_per_block = 40 s ; rss_per_block = 2 GiB ; wall_total = 5400 s ; machine_spec/parallelism = 本机单进程独占 ; 超预算即 STOP 不调参`（依据：G3 实测单臂单块 19.38–20.13 s、RSS 1.13 GiB，`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md:45`；详见 `docs/decision-log.md` 2026-09-27 条目）。D-ACQ-02/03/05 仍 PENDING，R2 合同仍未冻结。

---

## 明早最短裁定格式（PI 只需逐项填一行）

```
D-ACQ-02 = O-2? ; session_id 清单 = <待填>
D-ACQ-03 = O-3? ; partition_rule = <待填> ; 各段帧数 = <待填 · frames>
D-ACQ-05 = O-5? ; baseline_id = <待填> ; tolerance_band = <待填 + 单位> ; sessions_required = <待填>
D-ACQ-06 = O-6? ; wall_per_block = <待填 · s> ; rss_per_block = <待填 · GiB> ; wall_total = <待填 · s> ; machine_spec/parallelism = <待填>
```

*本文件为规划输入卡片：未裁任何一行、未填任何数值、未授予任何授权。*
