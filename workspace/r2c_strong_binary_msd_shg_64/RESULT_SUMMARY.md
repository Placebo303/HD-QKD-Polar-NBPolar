# RESULT_SUMMARY — r2c-strong-binary-msd-shg-64

状态：operator 整理的数字摘要；Pre-RESULT 独立审查 **PASS_WITH_COMMENTS**（R7/R8 文字补充已采纳）；主线程裁定见 §9。
数字来源：`results.json`、`part_*.json`（64 个）、`construction_frozen_G2/G3.json`、`lab_readonly_check.json`、`run.log`；NB 对照来自 `../r2_fer_shg_64/`（经 `results.json` 内 `nb_scl_L16_pairing`）。Wilson 值由 operator 按公式独立核算（见 §2 末的核对结果）。

## 1. 冻结参数、授权、执行与构造阶段结果

### 1.1 冻结参数 / 授权 / 执行

- 探针/包：`r2c-strong-binary-msd-shg-64`，最强二元对照臂（硬前缀 MSD + SCL(L=16，无 CRC)，genie-SC 蒙特卡洛构造，逐层 μ_i 码率分配），Tier-Y 一次性，合同 `docs/nbpolar/R2C_STRONG_BINARY_MSD_CONTRACT_20260929.md`（D1–D8 + 修订 E1/E2）。
- 数据：SHG `_1`（G2）/ `_2`（G3）两会话，同一 64 块池（每会话 32 块 × 128 帧）；4 个 f 点 × 64 块 = 256 个块点，全部 status=ok。
- 授权：PI 聊天逐字授权，记录见 `AUTHORIZATION_RECORD.md`；Pre-EXECUTE 审查见 `PRE_EXECUTE_REVIEW.md`。`results.json` 的 `authorization` 字段仅为来源说明，不作授权证据。
- 执行时间：2026-09-29 22:53:58+08:00 开始（`EXECUTION_START.txt`），23:51:06+08:00 结束（EXECUTION_START.txt 第二行）；`run.log`：`DONE lab_unchanged=True stop_undetected=False accounting_consistent=True wall_s=3428.3`，`EXIT=0`。`results.json` timing.wall_s_total=3426.7 s。总预算 21600 s，未超。
- 解释器：`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`（WSL）。

### 1.2 模型与构造阶段（每会话）

**不变性检验（invariance，R 值，阈值 R_max=1.25，均 compatible=True）**

| 会话 | R_marginal | R_resid | marginal_l1 (real / null) | resid_mean (real / null) | null_groups / seed | compatible |
|---|---|---|---|---|---|---|
| G2 | 1.0094 | 1.0638 | 0.2805 / 0.2779 | 0.2797 / 0.2630 | 20 / 20260929 | True |
| G3 | 0.9894 | 1.0382 | 0.2732 / 0.2761 | 0.2727 / 0.2627 | 20 / 20260930 | True |

**D1 pmf 交叉验证选择（8 折，n_used=8192，平局阈值 0.005 nat）**

| 会话 | CV ll/符号 P-M2 | CV ll/符号 P-HIST | P-HIST − P-M2 (nat) | 选中 |
|---|---|---|---|---|
| G2 | -0.566339 | -0.699453 | -0.133114 | **P-M2** |
| G3 | -0.569533 | -0.702646 | -0.133113 | **P-M2** |

两会话 P-M2 的 CV 对数似然均高于 P-HIST（P-HIST 更差 0.133 nat/符号，远大于 0.005 平局阈值），故选 P-M2。

**逐层信道容量 caps_i（bit，10 层）与一致性检查**

| 会话 | L0 | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 |
|---|---|---|---|---|---|---|---|---|---|---|
| G2 | 0.998403 | 0.998403 | 0.996806 | 0.993613 | 0.987226 | 0.974452 | 0.948903 | 0.897807 | 0.795613 | 0.591959 |
| G3 | 0.998393 | 0.998393 | 0.996786 | 0.993573 | 0.987146 | 0.974291 | 0.948582 | 0.897165 | 0.794330 | 0.589862 |

| 会话 | Σcaps | 10 − Σcaps | H_total (bit) | H_total − (10 − Σcaps) | 超过 0.03 bit? |
|---|---|---|---|---|---|
| G2 | 9.183186180 | 0.816813820 | 0.816813820 | 6.550e-15 | False |
| G3 | 9.178521792 | 0.821478208 | 0.821478208 | -2.098e-14 | False |

**F3 点逐层 μ_i（每层独立二分，e_max=2）与信息位数 k_i；设计 Σp̃**

G2：

| 层 | L0 | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 |
|---|---|---|---|---|---|---|---|---|---|---|
| μ_i | 0.0046875 | 0.0046875 | 0.00703125 | 0.009375 | 0.0117188 | 0.0164062 | 0.0304687 | 0.0421875 | 0.0515625 | 0.075 |
| k_i | 32562 | 32562 | 32432 | 32251 | 31965 | 31393 | 30095 | 28036 | 24381 | 16939 |

设计 Σp̃ = 0.015610（设计帧 1024 帧/层的总错误比例之和；F3 单层 e_max=2 约束）；K_frozen（F3 每块披露位）=35064；F3 flags=[]；逐层 bisection flags=全部为空。

G3：

| 层 | L0 | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 |
|---|---|---|---|---|---|---|---|---|---|---|
| μ_i | 0.0046875 | 0.0046875 | 0.0046875 | 0.009375 | 0.0117188 | 0.0164062 | 0.028125 | 0.0421875 | 0.0585937 | 0.075 |
| k_i | 32561 | 32561 | 32509 | 32250 | 31962 | 31387 | 30161 | 28015 | 24108 | 16871 |

设计 Σp̃ = 0.014634（设计帧 1024 帧/层的总错误比例之和；F3 单层 e_max=2 约束）；K_frozen（F3 每块披露位）=35295；F3 flags=[]；逐层 bisection flags=全部为空。

**各点 f_realized 与设计 Σp̃（F1/F2/F4 由 F3 的 μ 形状整体平移得到，`delta_vs_F3_shape`）**

| 点 | f_target | G2 f_realized | G3 f_realized | G2 设计 Σp̃ | G3 设计 Σp̃ | G2 delta_vs_F3 | G3 delta_vs_F3 | flags (G2/G3) |
|---|---|---|---|---|---|---|---|---|
| F1 | 1.2000 / 1.2000 | 1.200021 | 1.200006 | 5.1649 | 5.4332 | -0.01101 | -0.01164 | [] / [] |
| F2 | 1.2753 / 1.2681 | 1.275343 | 1.268101 | 0.0741 | 0.6302 | -0.00304 | -0.00373 | [] / [] |
| F3 | 1.3124 / 1.3136 | 1.312443 | 1.313572 | 0.0156 | 0.0146 | 0.00000 | 0.00000 | [] / [] |
| F4 | 1.4124 / 1.4136 | 1.412460 | 1.413579 | 0.0068 | 0.0049 | 0.00816 | 0.00821 | [] / [] |

F1（f_target=1.20）在设计集上 Σp̃≈5.2/5.4（即设计上就基本必然失败）；F2 的 f_target 取该会话 NB f_book（含 CRC-16，G2 1.2753 / G3 1.2681）；F3 是设计集自洽点（各层设计 e≤2）；F4 = F3 + 0.1。

flag：设计阶段全部 flags 为空。**上沿未验证** 类 flag 在 F3 逐层二分中未触发；但 F3 的 μ 上界取自二分网格（最大 0.15，各层通过），二分再减半一格时，L0–L2 的设计帧出现 3 个错误而不通过（其余层见 trace），见 `construction_frozen_G*.json` 的 `layer_mu_bisection.*.trace`。

## 2. 各 f 点结果（F1/F2/F3/F4）

p̂ = 非 exact 比例 =（verify_failed + decode_failed + undetected）/ D；D = exact + verify_failed + decode_failed + undetected（有效分母）；D≥56 为合同有效性门槛。Wilson 95%（z=1.96）由 operator 独立核算。

### 2.1  F1

| 范围 | f_realized | exact | verify_failed | decode_failed | undetected | D | D≥56? | p̂ | Wilson 95% (独立核算) |
|---|---|---|---|---|---|---|---|---|---|
| G2 | 1.200021 | 0 | 32 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 1.000000 | [0.892817, 1.000000] |
| G3 | 1.200006 | 0 | 32 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 1.000000 | [0.892817, 1.000000] |
| **pooled** | (见两会话) | 0 | 64 | 0 | 0 | 64 | 是 | 1.000000 | [0.943374, 1.000000] |

P-1 分层（`stratum_official` 与 `stratum_task`，与汇总同表；A1_CAL_characterization 与 HELDOUT_model_selection 块在早前工作中触及过模型选择，heldout_model_selection 为 R2 要求单列的 8 块）：

| 分层口径 | 层 | exact | verify_failed | decode_failed | undetected | D | p̂ | Wilson 95% (独立核算) | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| official | A1_CAL_characterization | 0 | 16 | 0 | 0 | 16 | 1.000000 | [0.806387, 1.000000] | A1_CAL 参与过模型选择 |
| official | EVAL_already_decoded | 0 | 28 | 0 | 0 | 28 | 1.000000 | [0.879353, 1.000000] | 前驱已解码 |
| official | HELDOUT_model_selection | 0 | 20 | 0 | 0 | 20 | 1.000000 | [0.838870, 1.000000] | HELDOUT 参与过模型选择（其中 8 块为 NLL 打分块） |
| task | heldout_model_selection | 0 | 8 | 0 | 0 | 8 | 1.000000 | [0.675584, 1.000000] | 参与模型选择（R2 单列） |
| task | never_decoded | 0 | 28 | 0 | 0 | 28 | 1.000000 | [0.879353, 1.000000] |  |
| task | previously_decoded_eval | 0 | 28 | 0 | 0 | 28 | 1.000000 | [0.879353, 1.000000] | 前驱已解码 |
| pooled | 全部 | 0 | 64 | 0 | 0 | 64 | 1.000000 | [0.943374, 1.000000] | 汇总 |

### 2.2  F2

| 范围 | f_realized | exact | verify_failed | decode_failed | undetected | D | D≥56? | p̂ | Wilson 95% (独立核算) |
|---|---|---|---|---|---|---|---|---|---|
| G2 | 1.275343 | 30 | 2 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 0.062500 | [0.017310, 0.201475] |
| G3 | 1.268101 | 16 | 16 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 0.500000 | [0.336306, 0.663694] |
| **pooled** | (见两会话) | 46 | 18 | 0 | 0 | 64 | 是 | 0.281250 | [0.185932, 0.401342] |

P-1 分层（`stratum_official` 与 `stratum_task`，与汇总同表；A1_CAL_characterization 与 HELDOUT_model_selection 块在早前工作中触及过模型选择，heldout_model_selection 为 R2 要求单列的 8 块）：

| 分层口径 | 层 | exact | verify_failed | decode_failed | undetected | D | p̂ | Wilson 95% (独立核算) | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| official | A1_CAL_characterization | 14 | 2 | 0 | 0 | 16 | 0.125000 | [0.034977, 0.360233] | A1_CAL 参与过模型选择 |
| official | EVAL_already_decoded | 20 | 8 | 0 | 0 | 28 | 0.285714 | [0.152538, 0.470596] | 前驱已解码 |
| official | HELDOUT_model_selection | 12 | 8 | 0 | 0 | 20 | 0.400000 | [0.218804, 0.613422] | HELDOUT 参与过模型选择（其中 8 块为 NLL 打分块） |
| task | heldout_model_selection | 5 | 3 | 0 | 0 | 8 | 0.375000 | [0.136842, 0.694262] | 参与模型选择（R2 单列） |
| task | never_decoded | 21 | 7 | 0 | 0 | 28 | 0.250000 | [0.126763, 0.433560] |  |
| task | previously_decoded_eval | 20 | 8 | 0 | 0 | 28 | 0.285714 | [0.152538, 0.470596] | 前驱已解码 |
| pooled | 全部 | 46 | 18 | 0 | 0 | 64 | 0.281250 | [0.185932, 0.401342] | 汇总 |

### 2.3  F3

| 范围 | f_realized | exact | verify_failed | decode_failed | undetected | D | D≥56? | p̂ | Wilson 95% (独立核算) |
|---|---|---|---|---|---|---|---|---|---|
| G2 | 1.312443 | 32 | 0 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 0.000000 | [0.000000, 0.107183] |
| G3 | 1.313572 | 32 | 0 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 0.000000 | [0.000000, 0.107183] |
| **pooled** | (见两会话) | 64 | 0 | 0 | 0 | 64 | 是 | 0.000000 | [0.000000, 0.056626] |

P-1 分层（`stratum_official` 与 `stratum_task`，与汇总同表；A1_CAL_characterization 与 HELDOUT_model_selection 块在早前工作中触及过模型选择，heldout_model_selection 为 R2 要求单列的 8 块）：

| 分层口径 | 层 | exact | verify_failed | decode_failed | undetected | D | p̂ | Wilson 95% (独立核算) | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| official | A1_CAL_characterization | 16 | 0 | 0 | 0 | 16 | 0.000000 | [0.000000, 0.193613] | A1_CAL 参与过模型选择 |
| official | EVAL_already_decoded | 28 | 0 | 0 | 0 | 28 | 0.000000 | [0.000000, 0.120647] | 前驱已解码 |
| official | HELDOUT_model_selection | 20 | 0 | 0 | 0 | 20 | 0.000000 | [0.000000, 0.161130] | HELDOUT 参与过模型选择（其中 8 块为 NLL 打分块） |
| task | heldout_model_selection | 8 | 0 | 0 | 0 | 8 | 0.000000 | [0.000000, 0.324416] | 参与模型选择（R2 单列） |
| task | never_decoded | 28 | 0 | 0 | 0 | 28 | 0.000000 | [0.000000, 0.120647] |  |
| task | previously_decoded_eval | 28 | 0 | 0 | 0 | 28 | 0.000000 | [0.000000, 0.120647] | 前驱已解码 |
| pooled | 全部 | 64 | 0 | 0 | 0 | 64 | 0.000000 | [0.000000, 0.056626] | 汇总 |

### 2.4  F4

| 范围 | f_realized | exact | verify_failed | decode_failed | undetected | D | D≥56? | p̂ | Wilson 95% (独立核算) |
|---|---|---|---|---|---|---|---|---|---|
| G2 | 1.412460 | 32 | 0 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 0.000000 | [0.000000, 0.107183] |
| G3 | 1.413579 | 32 | 0 | 0 | 0 | 32 | —（门槛仅适用 pooled） | 0.000000 | [0.000000, 0.107183] |
| **pooled** | (见两会话) | 64 | 0 | 0 | 0 | 64 | 是 | 0.000000 | [0.000000, 0.056626] |

P-1 分层（`stratum_official` 与 `stratum_task`，与汇总同表；A1_CAL_characterization 与 HELDOUT_model_selection 块在早前工作中触及过模型选择，heldout_model_selection 为 R2 要求单列的 8 块）：

| 分层口径 | 层 | exact | verify_failed | decode_failed | undetected | D | p̂ | Wilson 95% (独立核算) | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| official | A1_CAL_characterization | 16 | 0 | 0 | 0 | 16 | 0.000000 | [0.000000, 0.193613] | A1_CAL 参与过模型选择 |
| official | EVAL_already_decoded | 28 | 0 | 0 | 0 | 28 | 0.000000 | [0.000000, 0.120647] | 前驱已解码 |
| official | HELDOUT_model_selection | 20 | 0 | 0 | 0 | 20 | 0.000000 | [0.000000, 0.161130] | HELDOUT 参与过模型选择（其中 8 块为 NLL 打分块） |
| task | heldout_model_selection | 8 | 0 | 0 | 0 | 8 | 0.000000 | [0.000000, 0.324416] | 参与模型选择（R2 单列） |
| task | never_decoded | 28 | 0 | 0 | 0 | 28 | 0.000000 | [0.000000, 0.120647] |  |
| task | previously_decoded_eval | 28 | 0 | 0 | 0 | 28 | 0.000000 | [0.000000, 0.120647] | 前驱已解码 |
| pooled | 全部 | 64 | 0 | 0 | 0 | 64 | 0.000000 | [0.000000, 0.056626] | 汇总 |

Wilson 独立核算：对本节所有行（含分层）用 `k=非exact, n=D` 重算，与 `results.json` 中 `wilson_95ci` 的 lower/upper 差 <1e-9，且 k 一致：**全部一致**。各层 decode_failed / resource_abort / not_started / error 均为 0，undetected 均为 0（`undetected_block_ids=[]`，`stop_undetected=false`）。

## 3. 失败块归因：逐块首错层分布（`measured_layer_errors`）

首错层 = 该块 MSD 逐层解码中第一个出现符号/比特错误的层（0=L0，…，9=L9）；None = 块 exact。

| 点 | 会话 | n_ok_blocks | 首错层直方图 | 各层出现错误的块数（L0..L9） |
|---|---|---|---|---|
| F1 | G2 | 32 | 0:29, 1:3 | [29, 32, 32, 32, 32, 32, 32, 32, 32, 32] |
| F1 | G3 | 32 | 0:25, 1:6, 2:1 | [25, 31, 32, 32, 32, 32, 32, 32, 32, 32] |
| F2 | G2 | 32 | 2:2, None:30 | [0, 0, 2, 2, 2, 2, 2, 2, 2, 2] |
| F2 | G3 | 32 | 0:5, 1:7, 2:4, None:16 | [5, 12, 16, 16, 16, 16, 16, 16, 16, 16] |
| F3 | G2 | 32 | None:32 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] |
| F3 | G3 | 32 | None:32 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] |
| F4 | G2 | 32 | None:32 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] |
| F4 | G3 | 32 | None:32 | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] |

## 4. 与 NB-SCL(L=16, R2, f≈1.27 实测 62/64) 的逐块配对四格表（仅计数）

配对按 `global_block_index`；NB 侧为 `../r2_fer_shg_64/` 的 SCL(L=16, CRC-16) 结果，二元侧为本次各 f 点；二元 undetected 计入非 exact（本次为 0）；无胜率、无检验。

| 点 | 二元 exact & NB exact | 二元 exact & NB 非 exact | 二元非 exact & NB exact | 二元非 exact & NB 非 exact | n | excluded / frame_range_mismatch |
|---|---|---|---|---|---|---|
| F1 | 0 | 0 | 62 | 2 | 64 | [] / [] |
| F2 | 44 | 2 | 18 | 0 | 64 | [] / [] |
| F3 | 62 | 2 | 0 | 0 | 64 | [] / [] |
| F4 | 62 | 2 | 0 | 0 | 64 | [] / [] |

## 5. 允许的结论句（逐点，仅陈述测量）

- **F1**：在 SHG _1/_2 同一 64 块池上，硬前缀 MSD + SCL(L=16，无 CRC，genie-SC MC 构造，逐层 μ_i 码率分配) 在 f = 1.2000（G2）/ 1.2000（G3） 时块失败率为 64/64 = 1.0000（Wilson 95% [0.943374, 1.000000]），undetected 0。
- **F2**：在 SHG _1/_2 同一 64 块池上，硬前缀 MSD + SCL(L=16，无 CRC，genie-SC MC 构造，逐层 μ_i 码率分配) 在 f = 1.2753（G2）/ 1.2681（G3） 时块失败率为 18/64 = 0.2812（Wilson 95% [0.185932, 0.401342]），undetected 0；分会话 G2 2/32（f=1.2753）、G3 16/32（f=1.2681），会话差异大，设计 Σp̃（G2 0.074 / G3 0.630）亦预示此差异。
- **F3**：在 SHG _1/_2 同一 64 块池上，硬前缀 MSD + SCL(L=16，无 CRC，genie-SC MC 构造，逐层 μ_i 码率分配) 在 f = 1.3124（G2）/ 1.3136（G3） 时块失败率为 0/64 = 0.0000（Wilson 95% [0.000000, 0.056626]），undetected 0。
- **F4**：在 SHG _1/_2 同一 64 块池上，硬前缀 MSD + SCL(L=16，无 CRC，genie-SC MC 构造，逐层 μ_i 码率分配) 在 f = 1.4125（G2）/ 1.4136（G3） 时块失败率为 0/64 = 0.0000（Wilson 95% [0.000000, 0.056626]），undetected 0。

## 6. 描述性对照（仅描述，不构成胜负比较）

- NB-SCL(L=16, R2) 在 f≈1.27（实测）：62/64 exact（失败 2/64，p̂=0.031）。
- 冻结二元基线 R2B-binary（`workspace/r2_binary_baseline_shg_64/`）：f≈4.1–4.8 下失败率 0.61–0.94。
- 合成冒烟（dry_run_realscale，合成信道）：F3 f≈1.35–1.37；本次真实数据 F3 设计自洽点 f_realized≈1.312/1.314。
- 付出的 CRC：NB 侧付 CRC 16 位；二元侧不付 CRC。
- **NB 与二元的 FER 点不同**：NB f≈1.27 处 FER=0.031；二元在 F3（f≈1.31）为 0/64，在 F2（f≈1.27，同 NB f_book）为 18/64。两者 f 不同、CRC 开销口径不同，**不得据此宣称胜负**。

## 7. 局限（Pre-EXECUTE C11，必须随结论一并陈述）

1. F3 是设计集自洽点（设计集上逐层 e≤2），**不是**保证：设计帧之外的真实块可以失败（F2 的 18/64 失败即说明构造点与真实 FER 不可互换）。
2. 设计帧为合成/genie 帧，**不含真实信道的尾部**（真实符号间相关、非平稳等）；不变性检验 R 仅为兼容性检查而非等价证明。
3. μ_i 由设计集选出，存在选择偏差（同一设计集既选 μ 又评估 Σp̃），且逐层二分对噪声敏感（网格粒度 0.0046875）。
4. 解码器为 min-sum，非精确 SPA；未做 CRC 辅助、软前缀、更大列表 L（L>16）等增强；因此 **不得宣称** 本结果为二元理论最优或二元方案的性能上界。
5. A1_CAL / HELDOUT 块早前参与过模型选择（R2 分层已单列，见 §2）。
6. F3/F4 的 0/64 的 Wilson 上界 0.0566 > 0.03，**不能**读作"已证明块失败率 ≤3%"。
7. F2 的 f 与 NB 为同一披露总量口径：二元不付 CRC，F2 目标取 NB 含 CRC 的 f_book（16 位约 0.0006 的 f）。
8. 设计集每层仅 1024 帧，F3 二分的下一格即出现 3 个错误（L0/L1 在 μ=0.00234、L2 在 μ=0.00469），点位粒度粗。
9. 二元达到"块失败约 3%"的 f 仅能给区间：约 1.28 至 ≤1.313，对 NB f≈1.27 的差距约 +0.01 至 +0.04（不可点估）。

## 8. 耗时、内存与 lab 只读核对

- 总 wall：`run.log` 3428.3 s（约 57.1 min）；`results.json` 3426.7 s；构造阶段各任务 wall 之和 423.6 s（8 次设计评估）。
- 单个块点最大 wall（part_*.json 的 points[].wall_s）：1.91 s；单码字最大 wall：0.359 s（限值 codeword_wall_limit_s=2.0 s，参考 0.183 s）。
- RSS：构造任务峰值最大 0.761 GiB，设计任务峰值最大 0.273 GiB；单进程预算 6.0 GiB；rss_over_budget=False。VmHWM of the worker process at task end (a reused pool worker reports its own high-water mark)
- lab 只读核对（`lab_readonly_check.json`）：lab_unchanged=True；使用的 5 个 lab 源文件均 `git_diff_quiet=true`；src 文件数 124 → 124；执行前后 lab 仓库 git status 一致（README.md、docs/README.md、polar_run.py 的既有修改及 v4_bestcfg/ 未跟踪，均为执行前已存在）。引擎库：`_stage/scl_cpp/msd_scl.so`（包内）。
- 并发说明：执行窗口内 `workspace/probes/r2c-layer-diag/`（合成 Tier-X 诊断探针的残留后台作业）仍在写日志至 23:55，可能造成 CPU 争用；码字 wall 远低于限值，未见对结果的影响。
- 块账目：256/256 块点 recorded，全部 status=ok，`block_accounting.consistent=true`；`resource_abort=0`，`not_started=0`。

## 9. 最终裁决

**主线程裁定（2026-09-30，Pre-RESULT PASS_WITH_COMMENTS 后）：MEASURED_AT_CONTRACT。** 四个 f 点全部 D=64、undetected 0、lab 未改动。最强二元臂（硬前缀 MSD + SCL L=16，无 CRC，genie-MC 构造，逐层 μ_i）在 f≈1.31 时 0/64 失败，在 NB 工作点 f≈1.27 时 18/64 失败；NB-Polar（M2+SCL L=16）在 f≈1.27 时 2/64。二元达到约 3% 块失败所需 f 在约 1.28–1.313 之间，NB 领先约 0.01–0.04（不可点估，受本合同局限约束，不宣称二元最优）。相对冻结二元基线（f≈4.1–4.8）差距已大幅缩小。
