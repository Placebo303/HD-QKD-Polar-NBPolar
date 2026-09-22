# G4_ADJUDICATION — 主线 R2 裁决书（NBPOLAR-M2-PRIOR-G4-INVENTORY）

- **Packet**: `NBPOLAR-M2-PRIOR-G4-INVENTORY`
- **Branch**: `codex/nbpolar-phase0`
- **Change**: `openspec/changes/nbpolar-prior-rebaseline` — D6 gate G4
- **Gate**: R2 主线裁决（仅主线可接受；操作者从不自我接受）

## 1. Verdict（逐字落盘，不增删结论）

**`NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`**

G4 接受 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`；Pre-EXECUTE 门系 build 前真实通过的 transcript
评审（`ses_f36a5ea9affePKdGSOKO6lCXqn`，`PRE_EXECUTE_PASS_WITH_COMMENTS`，10/10 PASS，0 阻断），
本文件为 build 后补记。

## 2. 证据链

1. **Phase 0 + Phase A 回执**：包内 `TASK_PACKET.md` 冻结包 + `STATUS.yaml` `authorizations`
   非空（kai 2026-09-22 verbatim 授权行，Phase A 记录、早于 Pre-EXECUTE 门）+
   `g4_freeze_config.json`（Phase-A 输入清单，TO-FREEZE 全非 null）。
2. **Pre-EXECUTE transcript**：`ses_f36a5ea9affePKdGSOKO6lCXqn`，
   verdict `PRE_EXECUTE_PASS_WITH_COMMENTS`，10/10 PASS，0 阻断；**于 Phase-B 构建
   （2026-09-22 21:52:37）之前作出并返回主线**；补记见本包 `PRE_EXECUTE_REVIEW.md`（record-only）。
3. **Phase-B 回执**：`g4_runs 1 / reruns 0 / rebuilds 0 / wall 0.15s / RSS 0.026GiB`
   （builder 一次完成，exit 0，4 个输出文件全部写出，无 rebuild，远低于冻结预算 300 s / 2 GiB /
   单线程；`sc_calls 0`、`tag_invocations 0`）。
4. **Pre-RESULT transcript**：verdict `PRE_RESULT_PASS_WITH_COMMENTS`（独立 Pre-RESULT 评审
   PASS，先于任何发布/提交）。

## 3. 逐项接受（G4-0 … G4-4）

- **G4-0 前置条件**：接受（分支 `codex/nbpolar-phase0`、输入清单路径存在、
  `g4_freeze_config.json` TO-FREEZE 非 null、授权在 Phase-B 构建前已记入 `STATUS.yaml`）。
- **G4-1 可追溯性**：接受（每行携带可解析 `source_artifact` + `source_locator`；终态零
  `to_freeze` 行）。
- **G4-2 CAL 明细列举**：接受 —— **独立复算 107/107**；**CAL 各 1056 集合相等**
  （SHG `_1`：A1-CAL 1024 + CAL32 32 = 1056；SHG `_2`：A1-CAL + CAL32 = 1056），集合相等检查对源
  `cal_ids*.json` 通过，标签 `sacrificed_excluded_from_denominator`。
- **G4-3 Release 映射与核算**：接受 —— **per-stage recount：key 1,432,998 / public 13,765,206 /
  tags 42** 全部与冻结值 MATCH；**`undetected` 0 隔离**（独立成行，绝不并入 success/FER）。
- **G4-4 计数与无遗漏/无声明**：接受 —— **`none_recorded` 11 行**（缺失字段显式成行，绝不静默）；
  **σ 三处字符串一致**（G3 freeze / G3 adjudication / `docs/decision-log.md` 跨工件字符串比对一致，
  **无任何重导**，仅引用冻结值 `114.43029692866367`）；`row_count` == JSON 行数 == MD 表行数 ==
  counts 求和；无 claim 句（无 FER/效率/资格/提升/可组合密钥声明，不引 S9 作 FER/效率证据）。
- **R1**：独立 Pre-RESULT PASS（`PRE_RESULT_PASS_WITH_COMMENTS`）。
- **R2**：本裁决书 = 主线接受。

## 4. Caveats（记录在案，均不阻断 verdict）

- **C1 行序**：清单行的排列顺序为呈现口径，不承载语义；计数与集合结论不受行序影响。
- **C2 SHG_2 空集未打印**：SHG `_2` 某空集合未被打印输出；空集本身如实为空，未以任何内容替代。
- **C3 locator 约定式**：`source_locator` 采用包内约定式（convention）写法，非任意工具可直接求值
  的表达式；按约定式解读即可解析。
- **C4 累加口径注记仅 STATUS**：`key_bits_sum 2,865,996` / `public_bits_sum 27,530,412` 的口径注记
  目前**仅记录在 `STATUS.yaml`**（`counts_note`）。**重申：2,865,996 / 27,530,412 是 G2+G3 两阶段
  累加值（two-stage row accumulation），不是单阶段、也不是轨道总量（per-stage frozen 值为
  1,432,998 / 13,765,206，G2、G3 各自 MATCH）。**
- **C5 46/47 计数措辞**：涉及 46/47 的计数措辞按 transcript 原文口径记录；数值不改、结论不增删。
- **C6 重复 result 键**：输出/记录中出现重复 `result` 键（YAML/对象层面的重复键现象）；以后出现的
  同名键取值口径以本裁决与 transcript 为准，不据此改动任何已接受数值。
- **C7 rebuilds 键名**：`STATUS.yaml` counters 使用 `rebuilds` 键名，而 TASK_PACKET 冻结 rebuild
  规则文本写作 `rebuild: 1, reason: ...` —— 键名单复数差异记录在案；语义一致（本包 `rebuilds: 0`，
  首次构建即全部写出，无 rebuild 发生）。

## 5. N1 关闭声明

- **N1（Pre-EXECUTE 非阻断注记 N1）—— 主线声明：关闭（CLOSED）。**
- N1 原文内容与上下文见 transcript `ses_f36a5ea9affePKdGSOKO6lCXqn`；本裁决书不复述、不改写，
  不因其推迟或附条件本 verdict。N2、N3 维持非阻断记录状态（见 `PRE_EXECUTE_REVIEW.md` §5）。

## 6. Ladder 效应（STATE.md §4.1，不跳级）

- **M2 状态仍为 `VALIDATED_AT_FROZEN_CONTRACT`**（第 2 横档）——G4 既不提升也不降级 M2。
- 本裁决**仅记录 `READY_FOR_QUALIFICATION` 合取项中的 G4 一项**（该行合取：≥2 独立会话 + 样本量 +
  **G4** + 独立 Pre-RESULT）；其余合取项不由本裁决认定。
- **R2 FER 门、R3 效率门、Stage-3 测量集仍 outstanding**，绝不可被 G4 替代；D6 的 claim-bearing
  陈述在 R2/R3/Stage-3 完成前继续禁止。**不跳级。**

## 7. One-shot 声明（Tier-Y）

- **`g4_runs 1`，`reruns 0`，`rebuilds 0`**：恰好一次完整构建；**无 rerun、无 tuning、无 rebuild、
  无 scope 收窄**。冻结预算与 outcome strings 均在构建前冻结并遵守。

---

*本文件为文档记录：不修改任何既有文件、不推进 `STATUS.yaml`（stage/result/next_gate 由主线另行
裁决后落盘）、不提交、不推送。*
