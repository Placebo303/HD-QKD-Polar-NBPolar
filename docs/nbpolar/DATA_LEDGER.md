# NB-Polar 数据账本（DATA_LEDGER）— 唯一权威

> 建立日期：2026-09-28（`openspec/changes/nbpolar-data-use-rules-revision` T1
> PI 裁决 "按建议批准，继续推进" 后创建）。**本文件是数据使用状态的唯一权威
> 来源**：任何"需要新采集"的主张，必须先查本文件并计算实际缺口（R5）。本文件
> 随每次数据接触事件（census/统计/选模/解码）追加更新，不回溯删除历史行。

## 规则摘要（R1–R5，全文见 `openspec/changes/nbpolar-data-use-rules-revision/
design.md` D7，PI 已于 2026-09-28 裁决采纳）

- **R1（安全）**：K 坐标/tag/CRC/CAL 牺牲排除已在 `beta_eff`/密钥分母中全额
  记账（`incremental.py:764/711`、`docs/SECURITY_MODEL.md:107-129`）；重新
  解码一个已解码块不产生超出该块自身解码已计的新披露——"解码 ≠ 消耗"。
- **R2（统计）**：一个 FER/效率数字合法当且仅当 (a) 方法与全部参数在见到数据
  前已冻结，(b) 报告完整声明的块集（不得挑块），(c) 无事后调参。参与过任一
  模型选择步骤（如 HELDOUT 的 NLL 打分）的块必须标注并单独分层报告，不得径直
  排除；须附一张"已在真实数据上行使过的选择自由度"表。
- **R3（分段）**：每个会话只切出 CAL32（32 帧，牺牲）；其余帧默认解码可用。
  CHAR/HELDOUT/A1_CAL 只在具体研究比较需要时才划出，并须说明理由；块仍为
  128 帧，任何块不得跨越 CAL32 边界。
- **R4（样本量）**：`n` 随参照 `p` 更新而重算；`n` 可用于反推"所需数据量"，
  但永不用于反推采集**配额政策本身**（`decision-log.md:84` 仍约束配额反推）。
- **R5（流程）**：在断言"需要新采集"之前，先查本账本并计算实际缺口；不得凭
  记忆中过时的 `STATE.md` 陈述断言稀缺。

**主张需新采集前必须先查本账本并算出缺口。**

**数据来源**：`workspace/acq_inventory_20260928/{REPORT.md,configs.json,
frame_census.json,participation_ledger.json}`、`docs/decision-log.md`、
`docs/nbpolar/STATE.md`、`docs/nbpolar/MACRO_PLAN_20260921.md` §9、
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze_config.json`、
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/g3_freeze_config.json`。

---

## §1 SHG `_1`（`20260113_SHG_Type2PPLN_3s`，即 G2 参照会话）

post-skip 总帧数 4219（skip=702，window=200；`frame_census.json` 2026-09-28
复现核对通过，与 `g2_freeze_config.json`/`decision-log.md:143` 完全一致）。

| 段 | 帧区间（post-skip） | 长度 | 用途 | 接触类型 | 使用它的实验/门 | R2 确认资格（新规则） | 剩余 |
|---|---|---|---|---|---|---|---|
| A1_CAL | 0-1023 | 1024 | M0 incumbent 先验拟合 | 参与选模（先验拟合，非解码） | G2 三臂 A1 描述性臂（`decision-log.md` 2026-09-22 G2 条目，A1 0/14 描述性无门） | R3 起默认解码可用；按 R2 须标注"曾用于 M0 拟合"分层报告 | 8 个 128 帧块（stratum=`A1_CAL_characterization`） |
| CAL32 | 1024-1055 | 32 | M2 候选先验拟合（牺牲段） | 统计（先验拟合，牺牲，非解码） | G2 M2 CAL32 三元组拟合（q0/q+1/q−1/q_rest） | **排除**（R3 明文：CAL32 永远排除，不进入任何块池） | 0（按规则排除，非"剩余"） |
| CHAR | 1056-1837 | 782 | δ-tail / NLL 特征化 | 统计/参与选模 | G1R2 δ-tail PASS、NLL PASS 判定 | 与 HELDOUT 合并按 128 帧切块，标注"曾用于特征化"分层报告 | 与 HELDOUT 共 1342 帧 |
| HELDOUT | 1838-2397 | 560 | M0/M2 NLL 打分留出集 | 参与选模 | G1R2/G2 NLL PASS 门 | 与 CHAR 合并共 1342 帧 / 128 = 10.48 → 10 块，余 62 帧不用 | 10 块（stratum=`HELDOUT_model_selection`），62 帧余量弃 |
| EVAL | 2398-4189 | 1792（14×128） | 实际解码评估 | **解码**（SC 全 14 块；SCL(L=16) 描述性全 14 块，本会话 13/14 exact） | G2 SUCCESS 门（B 11/14 vs A2 0/14 严格不重叠）；SCL 描述性合并 27/28（本会话贡献 13/14，仅 G2 block 5 仍 `verify_failed`） | 已解码；按 R1"解码≠消耗"可复用于新描述性/统计目的，须标注"已解码"分层；R2 D-ACQ-02/03 采纳为候选源之一 | 14 块（stratum=`EVAL_already_decoded`） |
| RESERVE | 4190-4218 | 29 | 未用 | **未接触** | 无 | 不足 1 个 128 帧块，不可单独成块 | 29 帧（&lt;128，无法单独使用） |

本会话 R2 候选合计：8（A1_CAL）+ 10（CHAR+HELDOUT，62 帧弃）+ 14（EVAL）= **32 块**
（CAL32 32 帧排除；RESERVE 29 帧不足 1 块，不计入）。

> **2026-09-29 接触记录（`r2-fer-shg-64`，M2+SCL(L=16,top_m=4,CRC-16) 解码）**：
> 本会话 A1_CAL（8 块）、HELDOUT_model_selection（10 块）、
> EVAL_already_decoded（14 块，此前已被 SC/SCL 解码过）三段合计 32 块全部
> 参与本次 R2 FER 测量（`global_block_index` 0–31，session=G2）。A1_CAL/
> HELDOUT 段是**首次**被任何解码器（SC 或 SCL）接触；EVAL 段按 R1"解码≠
> 消耗"复用，不产生新披露。本会话结果 31/32 exact（失败块 `part_G2_23`，即
> 此前的 G2 EVAL block 5，L2 78 错误符号，SC/SCL 两路径均失败）。详见
> `workspace/r2_fer_shg_64/RESULT_SUMMARY.md`、`docs/decision-log.md`
> 2026-09-29 条目。本行不改变本表其余各段"剩余"数字（RESERVE 29 帧仍未
> 接触）。

> 2026-09-29 二元基线接触记录（`r2-binary-baseline-shg-64`）：冻结原生二元 Polar 分层基线（SC 主臂，及后作废的 CA-SCL 副臂）解码了同一 64 块池（G2 32 块 + G3 32 块）在 3 个 margin 点的全部块；无新披露（R1 "解码≠消耗"），未消耗任何 RESERVE 帧。CA-SCL 副臂数据已作废（`workspace/r2_binary_baseline_shg_64/INVALID_CA_SCL.md`）。详见 `RESULT_SUMMARY.md`。

## §2 SHG `_2`（`20260113_SHG_Type2PPLN_3s_2`，即 G3 参照会话）

post-skip 总帧数 4289（skip=702，window=200；`frame_census.json` 2026-09-28
复现核对通过，与 `g3_freeze_config.json`/`decision-log.md:119,:137` 完全一致）。
段结构与 §1 同构（`g3_freeze_config.json` 的 `disjointness_matrix`/`eval_blocks`/
`skip_frames`/`pairing_window_*` 字段与 G2 逐字节相同）；差异仅在 EVAL 段的
SCL 描述性结果（本会话 14/14 全部保持）与 RESERVE 帧数。

| 段 | 帧区间（post-skip） | 长度 | 用途 | 接触类型 | 使用它的实验/门 | R2 确认资格（新规则） | 剩余 |
|---|---|---|---|---|---|---|---|
| A1_CAL | 0-1023 | 1024 | M0 incumbent 先验拟合 | 参与选模 | G3 三臂 A1 描述性臂（0/14 描述性无门） | 同 §1 | 8 块（stratum=`A1_CAL_characterization`） |
| CAL32 | 1024-1055 | 32 | M2 候选先验拟合（牺牲段） | 统计（牺牲） | G3 M2 CAL32 三元组拟合 | **排除** | 0（按规则排除） |
| CHAR | 1056-1837 | 782 | δ-tail / NLL 特征化 | 统计/参与选模 | G1R2/G3 判定 | 同 §1 | 与 HELDOUT 共 1342 帧 |
| HELDOUT | 1838-2397 | 560 | NLL 打分留出集 | 参与选模 | G3 NLL PASS 门 | 同 §1 | 10 块（stratum=`HELDOUT_model_selection`），62 帧弃 |
| EVAL | 2398-4189 | 1792（14×128） | 实际解码评估 | **解码**（SC 全 14 块；SCL(L=16) 描述性全 14 块保持，14/14 exact） | G3 SUCCESS 门（B 8/14 vs A2 0/14 严格不重叠）；SCL 描述性合并（本会话贡献 14/14） | 已解码，同 §1 | 14 块（stratum=`EVAL_already_decoded`） |
| RESERVE | 4190-4288 | 99 | 未用 | **未接触** | 无 | 不足 1 个 128 帧块 | 99 帧（&lt;128，无法单独使用） |

本会话 R2 候选合计：8 + 10 + 14 = **32 块**（CAL32 排除；RESERVE 99 帧不足 1 块，
不计入）。

> **2026-09-29 接触记录（`r2-fer-shg-64`，M2+SCL(L=16,top_m=4,CRC-16) 解码）**：
> 本会话 A1_CAL（8 块）、HELDOUT_model_selection（10 块）、
> EVAL_already_decoded（14 块，此前已被 SC/SCL 解码过）三段合计 32 块全部
> 参与本次 R2 FER 测量（`global_block_index` 32–63，session=G3）。A1_CAL/
> HELDOUT 段是**首次**被任何解码器接触；EVAL 段复用不产生新披露。本会话
> 结果 31/32 exact（失败块 `part_G3_38`，`A1_CAL_characterization`/
> `never_decoded` 块，首次 SCL 观测，无历史对照）。详见
> `workspace/r2_fer_shg_64/RESULT_SUMMARY.md`、`docs/decision-log.md`
> 2026-09-29 条目。本行不改变本表其余各段"剩余"数字（RESERVE 99 帧仍未
> 接触）。

## §3 两会话合计

64 块（32 + 32），见 §7「R2 样本源（64 块）」。CAL32 两会话各 32 帧、合计 64 帧，
始终排除。RESERVE 两会话合计 128 帧（29 + 99），均不足单独成块。

## §4 `20260112_Type2PPLN_3s`（候选，物理不可用）

配置与参照逐字段基本一致（仅 ch1 硬件延迟差 4 ps，可忽略），但窄窗口（W=200）
配对后仅 4782 对，远小于 skip=702 帧所需 179712 对——`chunk_frames` 直接报错，
0 帧、0 块。接触类型：header `getConfiguration()` 读取 + 一次失败的解码链尝试
（`_align_frozen` 通过，`chunk_frames` 报错，未形成任何帧；无先验拟合/统计/
解码）。剩余：**0 块可用**（`insufficient_pairs_for_skip`，物理上不可用作 EVAL
源，非配置问题）。来源：`workspace/acq_inventory_20260928/{REPORT.md §(c)/(f),
frame_census.json,participation_ledger.json}`。

## §5 配置不匹配会话（本次未计帧，仅头文件盘点）

| 会话 | 日期 | 配置差异 vs 参照 | 用途 | 接触类型 | 剩余 |
|---|---|---|---|---|---|
| `20260121_Type2_1-5M_3s` | 2026-01-21 | resolution Standard vs HighResB、normalization True vs False、resolution_rms 2.0 vs 1.5 等（`REPORT.md` §(b)） | V25 冻结经验信道/训练集三源之一（`decision-log.md:5417`，`type2_1p5M_20260121_183806`） | 已消耗（训练，非 EVAL） | 0（已用尽，非 EVAL 候选） |
| `20260121_Type2_1M_3s` | 2026-01-21 | 同上 | V25 三源之一（`type2_1M_20260121_184040`） | 已消耗（训练） | 0 |
| `20260121_Type2_2M_3s` | 2026-01-21 | 同上 | V25 三源之一（`type2_2M_20260121_183657`） | 已消耗（训练） | 0 |
| `20260120_Type0_nofilter_500K_3s` | 2026-01-20 | 同上（Standard/rms 2.0/normalization True，ch1 delay 55 vs 289） | 2026-09-21 `SKIP0_MINIMAL_SIZING_DESCRIPTIVE` census：CAL128 @ w500/w1000 有 2 个 defensible H 格 | 统计（描述性 H，非 CAL/EVAL 消耗） | 未定（配置不匹配，本次未计帧） |
| `20260120_Type0_nofilter_1M_3s` | 2026-01-20 | 同上 | 同一 census，CAL256 @ w500 有 1 个 defensible H 格 | 统计（描述性） | 未定 |
| `20260120_Type0_nofilter_1_5M_3s` | 2026-01-20 | 同上 | 同一 census，无 defensible 格（peak sigma176，覆盖/纯度冲突） | 统计（描述性，非 defensible） | 未定 |
| `20260120_Type0_nofilter_2M_3s` | 2026-01-20 | 同上 | 同一 census，无 defensible 格（peak sigma233） | 统计（描述性，非 defensible） | 未定 |

以上 7 个会话在 2026-09-28 盘点范围内**未被计帧**（按协调者当日追加指示范围
限定：仅对配置一致且未用的候选计帧），因此"剩余"帧数未知；不构成当前 R2 新源
候选（配置是否可放宽需 PI 另行裁决，见 `REPORT.md` §(g) 结尾段——这是采集**电子
学/resolution 模式**层面的不一致，不同于此前 PI 已裁定的"Type0/SHG 只是**光源**
差异、对 IR 过程无影响"那个物理源层面的问题，两者不得混同）。

## §6 旧 P 系列（`20260107`/`20260123`，已真正耗尽）

冻结会话：`20260123_1M_600k_0dB`（1M）、`20260107_PPLN_1p5M`（1.5M）、
`20260123_2M_1p2M_0dB`（2M）（`docs/nbpolar/RAW_DATA_INVENTORY_20260921.md:21-22`；
CAL 段示例 `20260123_1M_600k_0dB` frames 702-1725，`PHASE4_P0_PRIOR_CONTRACT.md:84`）。

| 子段 | 帧区间 | 长度 | 状态 |
|---|---|---|---|
| 1.5M VAL | 2172-2212 | 41 | never-decoded |
| 1.5M HOLD | 2725-2766 | 42 | never-decoded |
| 2M HOLD | 3627-3644 | 18 | never-decoded |

合计 never-decoded 余量 **101 帧**（`MACRO_PLAN_20260921.md:93-96`，2026-09-21
修正，取代此前误记的 261 帧）；32 帧 CAL 后剩 **69 帧**，不足 1 个 128 帧块——
**该批次是真正的物理耗尽**（与下文 SHG RESERVE 29/99 帧"未耗尽、只是在当前
4190 帧固定前缀分段方式下小于一块"性质不同；两者不得混淆——见 `proposal.md`
Finding 4、`design.md` D5）。剩余：**0 块可用**。

---

## §7 R2 样本源（64 块）

采纳 `design.md` D8 + T1 PI 裁决 (iii)：SHG `_1`/`_2` 全会话共 **64 块**，
每会话 32 块：

- 帧 0-1023（A1_CAL，8 块，`stratum=A1_CAL_characterization`，仅用于 M0 拟合
  定征，须标注分层）
- 帧 1056-2397（CHAR+HELDOUT，10 块，余 62 帧不用，
  `stratum=HELDOUT_model_selection`，参与过 NLL 模型选择，须标注分层）
- 帧 2398-4189（EVAL，14 块，`stratum=EVAL_already_decoded`，已按冻结候选
  解码，须标注"已解码"分层）
- CAL32（1024-1055，32 帧）在两会话中都保持**排除**，不计入 64 块

**候选译码配置**（T1 PI 裁决 (iv)，执行前须正式冻结）：M2 先验 + SCL(L=16,
top_m=4, CRC-16) + K1=319/K2=6492 + P16 构造（digest `055c906472dd…faea1b`；`b4defb1e` 为 P16-vs-matched Tier-X 探针的 commit，非 digest），Tier-X focused
review PASS）。

**适用域限定**（T1 PI 裁决 (iii)，即 D-ACQ-05）：结论仅适用于 2026-01-13 两次
SHG 采集自身条件（配置见 `workspace/acq_inventory_20260928/REPORT.md` §(a)/(b)）；
HELDOUT（1838-2397）与已解码的 EVAL（2398-4189）**必须分层报告**，不得合并为
单一未分层 FER 数字（R2 (b)）。

**缺口计算（R5 示例）**：R2 目标样本量 `n=56`（`D-FER-03` 重裁决，见
`docs/decision-log.md` 2026-09-28 条目）。本账本已识别的合格源为 64 块
（本节），**已覆盖** `n=56` 的样本量目标，**无需新采集**即可满足 D-FER-03 的
`n` 下限——这是 R5 流程规则的具体示例：任何"数据不足需新采集"的断言，必须先
对照本节算出实际缺口（此处缺口 = 0）。执行前仍需 R2 自身 T4 完成候选配置的
正式冻结，且仍受 AGENTS.md §10.3 Pre-EXECUTE/Pre-RESULT 门约束；本节不授予
任何执行授权。
