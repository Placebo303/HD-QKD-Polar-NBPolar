# RESULT_SUMMARY — r2b-fer-shg-64-L32-f120

状态：operator 整理的数字摘要；Pre-RESULT 独立审查 **PASS_WITH_COMMENTS**（C1–C3 已采纳修改）；主线程裁决见 §2 末。
数字来源：`results.json`、`part_*.json`（64 个）、`run.log`；前驱对照来自 `../r2_fer_shg_64/part_*.json`。Wilson 值由 operator 按公式独立核算，与 `results.json` 逐位一致。

## 1. 冻结参数、授权与执行

- 探针/包：`r2b-fer-shg-64-L32-f120`，`r2-fer-shg-64` 的 delta-successor（合同 `docs/nbpolar/R2B_L32_F120_DELTA_20260929.md`），Tier-Y 一次性，reruns=0。
- 解码：M2 先验 + 原生 SCL（`scl_joint_native.scl_joint_decode_native`，Rust，L=32，top_m=4，CRC-16）；P16 digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`；W_P=200/W_S=500/CIRCULAR/skip=702。
- K：K_total=6442（f=1.20），k1=302，k2=6140（两会话共用）；SC 保真路径仍用冻结 K1=319/K2=6492。
- 种子：eval_seed=2026092902，tag_master=2026102902。
- 预算：串行；每块 wall ≤300 s、RSS ≤4 GiB、总 wall ≤7200 s。
- 授权：PI 2026-09-29 聊天逐字授权，记录见 `AUTHORIZATION_RECORD.md`；Pre-EXECUTE：`PRE_EXECUTE_REVIEW.md`（PASS_WITH_COMMENTS）。
- 执行时间：2026-09-29 15:06:33+08:00 开始（`EXECUTION_START.txt`），约 16:09:36+08:00 结束；`run.log`：EXIT=0，**wall = 3782.5 s**（约 63.0 min，含两次会话建立），未超 7200 s。
- 解释器：`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`。
- 注意（合同 D2 已声明）：本次为原生 SCL 实现的测量，不是对 `scl_joint` 的复现；前驱 SCL(L=16) 只作描述性参考。

## 2. 判定规则逐项应用（只报数字与规则结果）

| 项 | 数值 | 规则结果 |
|---|---|---|
| exact / verify_failed / decode_failed | 50 / 14 / 0 | — |
| D = exact + verify_failed + decode_failed | **64** | — |
| D ≥ 56 ? | 64 ≥ 56 | 是（非 INSUFFICIENT） |
| p̂ = 14/64（非 exact 比例） | 0.21875 | — |
| Wilson 95% CI（z=1.96，k=14，n=64） | **[0.135022, 0.334330]** | 核算：中心 (p+z²/2n)/(1+z²/n)=0.2350，半宽 0.0997 |
| undetected | **0**（`undetected_block_ids=[]`，`stop_undetected=false`） | 未触发 P-2 STOP |
| fidelity（28 个 EVAL 块 SC 复现 vs per_block_outcomes.jsonl） | 28/28 match，`fidelity_mismatch=0`，`fidelity_compromised=false` | 未触发保真受损 |
| not_started | 0 | — |
| resource_abort | 0 | 每块 wall/RSS 均在预算内 |
| status / error | 64/64 `ok`，error=0 | — |

最终裁决（主线程，2026-09-29，Pre-RESULT PASS_WITH_COMMENTS 后）：**FER_MEASURED_AT_CONTRACT** —— M2 + 原生 SCL(L=32) 在 f_book≈1.20 下真实 64 块块失败率 p̂=0.219（Wilson [0.135, 0.334]），undetected 0；失败 14/14 为 L2。该点**不**构成可用工作点（相对 f≈1.27 的 p̂=0.031 明显劣化）。

注：`results.json` 的 `authorization` 字段为脚本写死的占位（"NOT YET GRANTED"），不作授权证据；授权以 `AUTHORIZATION_RECORD.md` 为准。

## 3. P-1 分层表（汇总与分层同表）

### 3.1 官方口径 `stratum_official` × 会话（exact / verify_failed）

| stratum_official | G2 | G3 | 合计 exact/vf (n) | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|
| A1_CAL_characterization | 6 / 2 | 5 / 3 | 11 / 5 (16) | 0.3125 | [0.141644, 0.555961] |
| HELDOUT_model_selection | 8 / 2 | 7 / 3 | 15 / 5 (20) | 0.25 | [0.111860, 0.468705] |
| EVAL_already_decoded | 12 / 2 | 12 / 2 | 24 / 4 (28) | 0.142857 | [0.056989, 0.314902] |
| **汇总 pooled** | 26 / 6 (32) | 24 / 8 (32) | **50 / 14 (64)** | 0.21875 | [0.135022, 0.334330] |

### 3.2 任务口径 `stratum_task`（三层）× 会话

`never_decoded` = 从未被任何解码器接触的块（含官方 A1_CAL 16 块与官方 HELDOUT 中未参与模型选择的 12 块）；`heldout_model_selection` = 曾参与 NLL 模型选择打分的 8 块（R2 要求单列）；`previously_decoded_eval` = 前驱已解码的 28 个 EVAL 块。

| stratum_task | G2 exact/vf | G3 exact/vf | 合计 exact/vf (n) | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|
| never_decoded | 10 / 4 | 10 / 4 | 20 / 8 (28) | 0.285714 | [0.152538, 0.470596] |
| heldout_model_selection | 4 / 0 | 2 / 2 | 6 / 2 (8) | 0.25 | [0.071478, 0.590730] |
| previously_decoded_eval | 12 / 2 | 12 / 2 | 24 / 4 (28) | 0.142857 | [0.056989, 0.314902] |
| **汇总 pooled** | 26 / 6 | 24 / 8 | **50 / 14 (64)** | 0.21875 | [0.135022, 0.334330] |

以上各层 undetected、decode_failed、resource_abort、not_started 均显式为 0。

## 4. f_book（`results.json` `per_session`，运行时用 CAL32 重算）

| 会话 | H_total (bits) | kdb 不含 CRC | kdb 含 CRC-16 | f_book 不含 CRC | f_book 含 CRC |
|---|---|---|---|---|---|
| G2（SHG _1） | 0.8168138204 | 32274 | 32290 | 1.205813 | 1.206410 |
| G3（SHG _2） | 0.8214782076 | 32274 | 32290 | 1.198966 | 1.199560 |

kdb 为按块常数 = 5·6442+64(tag)（不含 CRC）/ +16（含 CRC）；披露在解码前无条件发生，与解码结果无关。与合同 D1 预算值一致。

## 5. 失败块逐块表（14 块，均为 verify_failed）

所有 14 块共同特征：`crc_pass=false`、`tag_pass=false`、`decode_failed=false`、`undetected=false`、`l1_error_symbols_scl=0`、`l1_survivor_count=32`、`candidates_considered=128`。层归因取自 SCL 最终输出候选的符号错误数：**L1 错 0 / L2 错 14**。

前驱列 = `../r2_fer_shg_64/` 同 `global_block_index` 块在 L=16、f≈1.27 下的 SCL 结果（描述性）；SC 列 = 本次 SC 路径（K1=319/K2=6492，f≈1.27）在该块的结果（EVAL 块为保真路径，其余为描述性）。

| gbi | 会话 | 起始帧 | stratum_official | stratum_task | L2 错符号数 | SCL wall (s) | 前驱 L=16 f≈1.27 | SC f≈1.27（首错坐标） |
|---|---|---|---|---|---|---|---|---|
| 2 | G2 | 256 | A1_CAL | never_decoded | 20 | 39.0 | exact | exact |
| 7 | G2 | 896 | A1_CAL | never_decoded | 46 | 38.3 | exact | exact |
| 8 | G2 | 1056 | HELDOUT | never_decoded | 94 | 39.4 | exact | exact |
| 11 | G2 | 1440 | HELDOUT | never_decoded | 1174 | 37.3 | exact | exact |
| 23 | G2 | 3038 | EVAL | previously_decoded_eval | 191 | 39.3 | **verify_failed**（L2 错 78） | verify_failed（L2, 978） |
| 30 | G2 | 3934 | EVAL | previously_decoded_eval | 50 | 37.3 | exact | verify_failed（L2, 2000） |
| 34 | G3 | 256 | A1_CAL | never_decoded | 12 | 37.0 | exact | exact |
| 38 | G3 | 768 | A1_CAL | never_decoded | 20 | 36.9 | **verify_failed**（L2 错 68） | verify_failed（L2, 1967） |
| 39 | G3 | 896 | A1_CAL | never_decoded | 20 | 36.9 | exact | exact |
| 45 | G3 | 1696 | HELDOUT | never_decoded | 20 | 37.0 | exact | exact |
| 46 | G3 | 1824 | HELDOUT | heldout_model_selection | 12 | 36.9 | exact | exact |
| 49 | G3 | 2208 | HELDOUT | heldout_model_selection | 1092 | 37.2 | exact | exact |
| 53 | G3 | 2782 | EVAL | previously_decoded_eval | 180 | 36.7 | exact | exact |
| 62 | G3 | 3934 | EVAL | previously_decoded_eval | 2831 | 37.0 | exact | exact |

汇总：
- 层归因：L1 错 0 / L2 错 14。
- 对同块前驱（L=16, f≈1.27）：14 个失败块中 **2 块**（gbi 23、38）前驱也失败；**12 块**前驱为 exact。反向（前驱失败而本次 exact）0 块。转移矩阵（前驱 → 本次）：exact→exact 50，exact→verify_failed 12，verify_failed→verify_failed 2，verify_failed→exact 0。
- 失败块 L2 错符号数分两类：12–191（11 块）与 1092–2831（3 块：gbi 11、49、62）。此为描述性观察，不作机理推断。

## 6. 描述性对照（**非保真门，不构成显著性结论**；对照 1 的 f/L/实现均不同；对照 2 同为原生 SCL、L=32、名义 f=1.20，但信道/数据、样本量与 K 略有差异——合成 K_total=6421、k1=301、k2=6120，f_book_with_crc=1.2005）

1. 前驱 `r2-fer-shg-64`：M2 + `scl_joint` SCL(L=16, top_m=4)，K1=319/K2=6492（K=6811），f_book≈1.268–1.275（含 CRC）：**62/64 exact**（p̂=0.03125，Wilson [0.008612, 0.106975]）。本次 f≈1.20：50/64 exact（p̂=0.21875，Wilson [0.135022, 0.334330]）。f、L、实现三者同时不同，此处不归因于任一因素。
2. 合成 Tier-X `eff-sweep-native`（commit 281bde83，`workspace/probes/eff-sweep-native/results.json`，G1R2 匹配信道，N=32768，32 块/点，原生 SCL，非 claim 探针，H=0.8165）：
   - L=32，f=1.20（含 CRC 1.2005）：31/32 exact，FER=0.03125，Wilson [0.005538, 0.157443]；
   - L=32，f=1.18：FER=0.0625（2/32）；f=1.15：FER=0.375（12/32）；
   - L=16，f=1.20：FER=0.09375（3/32）；f=1.25：0.03125（1/32）；
   - 合成 SC 参考（f=1.20）：FER=0.375（12/32）。
   - 真实数据 L=32/f≈1.20：p̂=0.21875，是合成同点估计 0.03125 的约 7 倍；两个 Wilson 区间（真实 [0.135, 0.334]，合成 [0.0055, 0.157]）仅在 0.135–0.157 之间轻微重叠。即真实点估计高于合成点估计；本文件只报差距，不归因（合成探针 n=32，其自身 review 已注明统计力度有限）。
3. 36 个非 EVAL 块的 **SC 描述性基线**（K=6811，f≈1.27，SC 解码器，**不可与 f=1.20 的 SCL 直接比较**）：34 exact / 2 verify_failed（gbi 15 [G2, HELDOUT, L2@3402]、gbi 38 [G3, A1_CAL, L2@1967]）。其中 gbi 15 本次 SCL 为 exact，gbi 38 本次 SCL 仍失败。同一 SC 路径在 28 个 EVAL 块上为 19 exact / 9 verify_failed（与 per_block_outcomes.jsonl 逐块一致）。

## 7. 耗时与资源统计（64 块）

| 指标 | 均值 | 最大 | 最小 |
|---|---|---|---|
| SC wall / 块 (s) | 20.06 | 21.23 | 19.76 |
| SCL(L=32) wall / 块 (s) | 35.32 | 39.38 | 33.79 |
| SC+SCL wall / 块 (s) | 55.39 | 60.08 | 53.61 |
| RSS 峰值 advisory (GiB) | 1.387 | 1.388 | 1.386 |

总 wall 3782.5 s；块耗时合计约 3545 s（64×55.39），其余约 237 s 为会话建立。均远低于 300 s/块、4 GiB、7200 s 预算。

## 8. 允许的结论句（仅测量陈述）

> 在 M2 先验 + 原生 SCL（L=32, top_m=4, CRC-16）、K_total=6442（k1=302, k2=6140）、P16 冻结构造下，SHG _1/_2 全会话冻结 64 块池（仅限 2026-01-13 两次 SHG 采集自身条件）测得：exact 50、verify_failed 14、decode_failed 0、undetected 0，D=64，非 exact 比例 p̂=0.21875（Wilson 95% CI [0.135022, 0.334330]）；分层结果见 §3；记账 f_book（含 CRC）G2 为 1.2064、G3 为 1.1996。14 个失败块均为 L2 错（L1 错 0）。28 个 EVAL 块 SC 保真 28/28 一致。

不得声称：达到任何 FER 目标、优于二元基线、与前驱 L=16/f≈1.27 结果等价、"f 降低导致失败"的因果归因、或合成 Tier-X 对真实数据预测有效；这些留主线程裁决。

## 9. Caveats

(a) 64 块，Wilson 区间较宽；分层格子更小（如 heldout_model_selection 仅 8 块）。
(b) 原生 SCL 与前驱 `scl_joint` 为不同实现，且 f、L 同时变化，与前驱对照仅描述性。
(c) 无同批二元基线对照。
(d) `never_decoded` 与 HELDOUT 块上的 SCL 为首次观测；`heldout_model_selection` 8 块曾参与模型选择，已单列。
(e) 待办：Pre-RESULT 独立审查、主线程裁决、`STATUS.yaml` 更新（当前仍为 `authorized_executing`，本 operator 未改动）。

## 参考

`results.json`（`taxonomy_pooled`、`taxonomy_by_stratum_official`、`taxonomy_by_stratum_task`、`per_session`、`timing`）；`part_*.json`；`run.log`；`AUTHORIZATION_RECORD.md`；`../r2_fer_shg_64/RESULT_SUMMARY.md` 与 `part_*.json`；`../probes/eff-sweep-native/results.json`。
