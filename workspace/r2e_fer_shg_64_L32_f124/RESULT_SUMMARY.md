# RESULT_SUMMARY — r2e-fer-shg-64-L32-f124

状态：operator 整理的数字摘要；Pre-RESULT 独立审查与主线程裁决均**待定**。
数字来源：`results.json`、`part_G2_*.json` / `part_G3_*.json`（64 个）、`run.log`、`EXECUTION_START.txt`、`AUTHORIZATION_RECORD.md`；前驱对照来自 `../r2_fer_shg_64/results.json`（R2）、`../r2b_fer_shg_64_L32_f120/results.json`（R2B）、`../r2d_locate_f_k_g2/`（R2D f1.24_s0380，仅 G2）。Wilson 值直接取 `results.json` 已算好的值，未手算。

## 1. 冻结参数、授权与执行

- 探针/包：`r2e-fer-shg-64-L32-f124`，`r2b-fer-shg-64-L32-f120` 的 delta-successor（合同 `docs/nbpolar/R2E_L32_F124_DELTA_20260929.md`），Tier-Y 一次性，reruns=0。
- 解码：M2 先验 + 原生 SCL（`scl_joint_native.scl_joint_decode_native`，Rust，L=32，top_m=4，CRC-16）；P16 digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`；W_P=200/W_S=500/CIRCULAR/skip=702。
- K：K_total=6657（f_target=1.24），k1=253，k2=6404（k1_share=0.0380；R2D 描述性定位 `workspace/r2d_locate_f_k_g2/` 按预注册规则选中 f1.24_s0380；两会话共用）；SC 保真路径仍用冻结 K1=319/K2=6492。
- 种子：eval_seed=2026092904，tag_master=2026102904。
- 预算：串行；每块 wall ≤300 s、RSS ≤4 GiB、总 wall ≤7200 s。
- 授权：PI 2026-09-29T20:58:51+08:00 聊天逐字授权，记录见 `AUTHORIZATION_RECORD.md`；Pre-EXECUTE：`PRE_EXECUTE_REVIEW.md`（PASS_WITH_COMMENTS）。
- 执行时间：2026-09-29T21:23:00+08:00 开始（`EXECUTION_START.txt`，仅启动行）；结束以 `results.json` mtime 2026-09-29 22:25:41+08:00 与 `run.log` wall=3761.5 s（62.7 min）自洽旁证（21:23:00 + 3761.5 s = 22:25:41.5）；未超 7200 s。
- 解释器：`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`。
- 注意（合同 E1/E4 已声明）：本次为原生 SCL 实现在 R2D 选定 K 点上的测量，不是对 `scl_joint` 的复现；R2 SCL(L=16) 与 R2D 描述性定位只作描述性参考。

## 2. 判定规则逐项应用（只报数字与规则结果）

| 项 | 数值 | 规则结果 |
|---|---|---|
| exact / verify_failed / decode_failed | 61 / 3 / 0 | — |
| D = exact + verify_failed + decode_failed | **64** | — |
| D ≥ 56 ? | 64 ≥ 56 | 是（非 INSUFFICIENT） |
| p̂ = 3/64（非 exact 比例） | 0.046875 | — |
| Wilson 95% CI（z=1.96，k=3，n=64，取自 results.json） | **[0.016069, 0.128999]** | 完整值 [0.016068725432185196, 0.12899860788542522] |
| undetected | **0**（`undetected_block_ids=[]`，`stop_undetected=false`） | 未触发 P-2 STOP |
| fidelity（28 个 EVAL 块 SC 复现 vs per_block_outcomes.jsonl） | 28/28 match，`fidelity_mismatch=0`，`fidelity_compromised=false` | 未触发保真受损 |
| not_started | 0（`not_started_block_ids=[]`） | — |
| resource_abort | 0（`resource_abort_block_ids=[]`） | 每块 wall/RSS 均在预算内 |
| status / error | 64/64 `ok`，error=0 | — |

最终裁决（主线程，2026-09-29，Pre-RESULT PASS 后）：**FER_MEASURED_AT_CONTRACT** —— fidelity_mismatch=0（非≥1），undetected=0（非≥1），D=64≥56（非 INSUFFICIENT）。p̂=3/64=0.046875（exact 61、verify_failed 3、decode_failed 0），Wilson 95% [0.0161,0.1290]（全精度 [0.016068725432185196,0.12899860788542522]），undetected 0；失败层归因 3/3 verify_failed（L2 相关：gbi23 G2 L1错0/L2错84；gbi53 G3 8/8；gbi59 G3 311/11972）、0 decode_failed。

描述性比较（不是判定）："f≈1.24 点在 64 块上与 f≈1.27 点未见可分辨劣化"（依据：本次 Wilson [0.016,0.129] 与 R2 Wilson [0.009,0.107] 有重叠且 p̂=0.047≤0.07；R2：62/64 f≈1.27 L=16 p̂=0.031）。

注：`results.json` 的 `authorization` 字段为脚本写死的占位（"NOT YET GRANTED"），不作授权证据；授权以 `AUTHORIZATION_RECORD.md` 为准。

## 3. 分层表（汇总与分层同表，共四套）

### 3.1 官方口径 `stratum_official` × 会话（exact / verify_failed）

| stratum_official | G2 | G3 | 合计 exact/vf (n) | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|
| A1_CAL_characterization | 8 / 0 | 8 / 0 | 16 / 0 (16) | 0.0 | [0.0, 0.193613] |
| HELDOUT_model_selection | 10 / 0 | 10 / 0 | 20 / 0 (20) | 0.0 | [0.0, 0.161130] |
| EVAL_already_decoded | 13 / 1 | 12 / 2 | 25 / 3 (28) | 0.107143 | [0.037118, 0.271962] |
| **汇总 pooled** | 31 / 1 (32) | 30 / 2 (32) | **61 / 3 (64)** | 0.046875 | [0.016069, 0.128999] |

### 3.2 任务口径 `stratum_task`（三层）× 会话

`never_decoded` = 从未被任何解码器接触的块（含官方 A1_CAL 16 块与官方 HELDOUT 中未参与模型选择的 12 块）；`heldout_model_selection` = 曾参与 NLL 模型选择打分的 8 块（R2 要求单列）；`previously_decoded_eval` = 前驱已解码的 28 个 EVAL 块。

| stratum_task | G2 exact/vf | G3 exact/vf | 合计 exact/vf (n) | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|
| never_decoded | 14 / 0 | 14 / 0 | 28 / 0 (28) | 0.0 | [0.0, 0.120647] |
| heldout_model_selection | 4 / 0 | 4 / 0 | 8 / 0 (8) | 0.0 | [0.0, 0.324416] |
| previously_decoded_eval | 13 / 1 | 12 / 2 | 25 / 3 (28) | 0.107143 | [0.037118, 0.271962] |
| **汇总 pooled** | 31 / 1 | 30 / 2 | **61 / 3 (64)** | 0.046875 | [0.016069, 0.128999] |

### 3.3 选择口径 `stratum_selection`（R2 新增；G2 = selection_touched，G3 = clean）

| stratum_selection | 会话 | exact/vf (n) | p̂ | Wilson 95% CI |
|---|---|---|---|---|
| clean（从未参与 f/k 选择） | G3 | 30 / 2 (32) | 0.0625 | [0.017310, 0.201475] |
| selection_touched（参与 R2D 选择） | G2 | 31 / 1 (32) | 0.03125 | [0.005538, 0.157446] |
| **汇总 pooled** | G2+G3 | **61 / 3 (64)** | 0.046875 | [0.016069, 0.128999] |

clean 层（n=32）**仅描述，主判定为 64 块汇总**（`clean_layer_G3_descriptive` 注记："n=32 descriptive only; the primary judgment is the 64-block pooled result"）。

以上各层 undetected、decode_failed、resource_abort、not_started、error、fidelity_mismatch 均显式为 0。

## 4. f_book（`results.json` `per_session`，运行时用 CAL32 重算）

| 会话 | H_total (bits) | kdb 不含 CRC | kdb 含 CRC-16 | f_book 不含 CRC | f_book 含 CRC |
|---|---|---|---|---|---|
| G2（SHG _1） | 0.8168138204 | 33349 | 33365 | 1.245976 | 1.246574 |
| G3（SHG _2） | 0.8214782076 | 33349 | 33365 | 1.238902 | 1.239496 |

完整重算值：G2 `f_book_no_crc_computed=1.2459763626`、`f_book_with_crc_computed=1.2465741503`；G3 `f_book_no_crc_computed=1.2389016573`、`f_book_with_crc_computed=1.2394960508`。

kdb 为按块常数 = 5·6657+64(tag)（不含 CRC）/ +16（含 CRC）；披露在解码前无条件发生，与解码结果无关。与合同 E1 记账值（33349/33365）及合同 f_book 值一致。

## 5. 失败块逐块表（3 块，均为 verify_failed）

3 块共同特征：`crc_pass=false`、`tag_pass=false`、`decode_failed=false`、`undetected=false`、`l1_survivor_count=32`、`candidates_considered=128`。

前驱列 = 同 `global_block_index` 块在 R2（`scl_joint` L=16、K=6811、f≈1.27）与 R2B（原生 SCL L=32、K=6442、f≈1.20）下的 SCL 结果（描述性，种子/K 不同）；R2D 列 = 同块在 R2D f1.24_s0380（同 K=6657、同原生 SCL L=32，G2 32 块描述性定位）下的结果，仅 G2 有；SC 列 = 本次 SC 保真路径（K1=319/K2=6492，f≈1.27）在该块的结果（EVAL 块为保真门，其余见 §7 基线）。

| gbi | 会话 | 起始帧 | stratum_official | stratum_task | stratum_selection | L1/L2 错符号数 | SCL wall (s) | R2 L=16 f≈1.27 | R2B L=32 f=1.20 | R2D f1.24_s0380 | SC f≈1.27（保真 actual） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23 | G2 | 3038 | EVAL | previously_decoded_eval | selection_touched | 0 / 84 | 37.3 | **verify_failed**（L2 错 78） | **verify_failed**（L2 错 191） | **verify_failed**（L2 错 84） | verify_failed（L2@978） |
| 53 | G3 | 2782 | EVAL | previously_decoded_eval | clean | 8 / 8 | 36.8 | exact | **verify_failed**（L2 错 180） | n/a（G3） | exact |
| 59 | G3 | 3550 | EVAL | previously_decoded_eval | clean | 311 / 11972 | 37.2 | exact | exact | n/a（G3） | exact |

汇总（描述性，不作机理推断）：
- 3 个失败块全部落在 EVAL / previously_decoded_eval 层；A1_CAL、HELDOUT、never_decoded、heldout_model_selection 层 0 失败。
- 相对 R2（失败块 gbi 23、38）的转移：verify_failed→verify_failed 1 块（gbi 23）；verify_failed→exact 1 块（gbi 38）；exact→verify_failed 2 块（gbi 53、59）；exact→exact 60 块。

## 6. gbi 23 单列（R2D 已知难块）

- gbi 23（G2 EVAL 块，帧 3038–3165）是 64 块中唯一 `known_hard_block=true` 的块；**计入所有分母，不排除**。
- 本轮结果：verify_failed（L1 错 0 / L2 错 84，SCL wall 37.3 s，SC 保真 actual 为 verify_failed L2@978，match=true）。
- 历史：R2 verify_failed（L2 78）、R2B verify_failed（L2 191）、R2D f1.24_s0380 verify_failed（L2 84）——在全部配置下均为 L2 失败。

## 7. 描述性对照（**非判定门，不构成显著性结论**；各对照的种子/K/L/实现与本轮不同，只作描述）

1. 前驱 `r2-fer-shg-64`：M2 + `scl_joint` SCL(L=16, top_m=4)，K1=319/K2=6492（K=6811），f_book≈1.268–1.275（含 CRC），种子 2026092801/2026102801：**62/64 exact**（p̂=0.03125，Wilson [0.008612, 0.106975]）。本次 f≈1.24 原生 SCL(L=32)：61/64 exact（p̂=0.046875，Wilson [0.016069, 0.128999]）。f、L、K、种子、实现五者同时不同，此处不归因于任一因素。
2. 前驱 `r2b-fer-shg-64-L32-f120`：M2 + 原生 SCL(L=32, top_m=4)，K_total=6442（k1=302/k2=6140），f_book≈1.20：**50/64 exact**（p̂=0.21875，Wilson [0.135022, 0.334330]）。K、f、种子不同，只作描述。
3. R2D `r2d-locate-f-k-g2` f1.24_s0380（同 K=6657/253/6404、同原生 SCL L=32，仅 G2 32 块，描述性定位，非 claim）：**G2 31/32 exact**，唯一失败为 gbi 23（L2）。本轮 G2 在同 K 下同样 31/32、同样仅 gbi 23 失败（L2 错同为 84）；此为描述性一致，不作复现声称。
4. 36 个非 EVAL 块的 **SC 描述性基线**（K=6811，f≈1.27，SC 解码器，**不可与 f=1.24 的 SCL 直接比较**）：34 exact / 2 verify_failed（gbi 15 [G2, HELDOUT, L2@3402]、gbi 38 [G3, A1_CAL, L2@1967]）。其中 gbi 15、gbi 38 本次 SCL 均为 exact。同一 SC 路径在 28 个 EVAL 块上为 19 exact / 9 verify_failed（与 per_block_outcomes.jsonl 逐块一致，保真 28/28 match）。

## 8. 耗时与资源统计（64 块）

| 指标 | 均值 | 最大 | 最小 |
|---|---|---|---|
| SC wall / 块 (s) | 20.02 | 21.22 | 19.66 |
| SCL(L=32) wall / 块 (s) | 34.67 | 37.34 | 33.87 |
| SC+SCL wall / 块 (s) | 54.69 | 57.16 | 53.74 |
| RSS 峰值 advisory (GiB) | 1.389 | 1.3929 | 1.3883 |

总 wall 3761.5 s；块耗时合计约 3500.1 s（64×54.69），其余约 261 s 为两会话建立。均远低于 300 s/块、4 GiB、7200 s 预算。

## 9. 允许的结论句（仅测量陈述）

> 在 M2 先验 + 原生 SCL（L=32, top_m=4, CRC-16）、K_total=6657（k1=253, k2=6404）、P16 冻结构造下，SHG _1/_2 全会话冻结 64 块池（仅限 2026-01-13 两次 SHG 采集自身条件）测得：exact 61、verify_failed 3、decode_failed 0、undetected 0，D=64，非 exact 比例 p̂=0.046875（Wilson 95% CI [0.016069, 0.128999]）；分层结果见 §3（含 selection 分层：clean G3 30/2、selection_touched G2 31/1，clean 层仅描述）；记账 f_book（含 CRC）G2 为 1.2466、G3 为 1.2395。3 个失败块均为 EVAL 层（gbi 23 L1错0/L2错84、gbi 53 L1错8/L2错8、gbi 59 L1错311/L2错11972），其中 gbi 23 为已知难块（R2/R2B/R2D 全部 L2 失败）。28 个 EVAL 块 SC 保真 28/28 一致。

不得声称：达到任何 FER 目标、优于二元基线、与前驱 L=16/f≈1.27 结果等价、"f 变化导致失败"的因果归因、或任何工作点取舍决定；这些留主线程裁决。

最终裁决：**主线程待定**。

## 10. 执行程序性偏差声明

(a) `run.log` 有 DONE 行但缺 `EXIT=0` 行（setsid/nohup 脱离原 shell 启动所致，命令尾的 `echo EXIT=$?` 未落盘；未手工补写）。完成证据：DONE 行（`n_blocks=64 pooled_D=64 pooled_exact=61 pooled_verify_failed=3 pooled_decode_failed=0 pooled_undetected=0 stop_undetected=False resource_abort=0 fidelity_mismatch=0 wall_s=3761.5`）+ 64/64 part 文件 + `results.json`（182660 B）+ 全文件无 Traceback。
(b) `EXECUTION_START.txt` 只有启动行（2026-09-29T21:23:00+08:00）、无结束行（同因脱离启动，尾部 `date -Is >>` 未落盘）。结束时间以 `results.json` mtime（2026-09-29 22:25:41+08:00）与 wall 3761.5 s 自洽旁证（21:23:00 + 3761.5 s = 22:25:41.5）。

## 11. Caveats

(a) 64 块，Wilson 区间较宽；分层格子更小（如 heldout_model_selection 仅 8 块，clean 层仅 32 块且仅描述）。
(b) 原生 SCL 与前驱 `scl_joint` 为不同实现，且 f、K、L、种子同时变化，与前驱对照仅描述性。
(c) 无同批二元基线对照。
(d) G2 32 块曾参与 R2D f/k 描述性选择，已单列为 selection_touched；G3 32 块为 clean。
(e) 待办：Pre-RESULT 独立审查、主线程裁决、`STATUS.yaml` 更新（当前仍为 `authorized_executing`，本 operator 未改动）。

## 参考

`results.json`（`taxonomy_pooled`、`taxonomy_by_stratum_official`、`taxonomy_by_stratum_task`、`taxonomy_by_stratum_selection`、`clean_layer_G3_descriptive`、`known_hard_block_gbi23`、`per_session`、`timing`）；`part_G2_*.json` / `part_G3_*.json`；`run.log`；`EXECUTION_START.txt`；`AUTHORIZATION_RECORD.md`；`../r2_fer_shg_64/RESULT_SUMMARY.md` 与 `results.json`；`../r2b_fer_shg_64_L32_f120/RESULT_SUMMARY.md` 与 `results.json`；`../r2d_locate_f_k_g2/RESULT_REVIEW.md` 与 `part_f1.24_s0380_*.json`。
