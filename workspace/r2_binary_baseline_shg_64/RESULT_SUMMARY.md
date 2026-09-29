# RESULT_SUMMARY — r2-binary-baseline-shg-64（仅 SC 主臂；描述性，非 Tier-Y 判定）

状态：SC 主臂 PASS_WITH_COMMENTS（`PRE_RESULT_REVIEW.md`），已发布。CA-SCL 副臂 **INVALID**（`INVALID_CA_SCL.md`），本文不含其任何数字。
数据来源：`results.json`（total_wall_s 5556.4，exit 0，reruns 0）、`PRE_RESULT_REVIEW.md`。

## 结论句（允许的唯一结论表述）
在 SHG `_1`/`_2` 同一 64 块池上，冻结原生二元 Polar 分层基线（独立比特面、SC、N=4096、PW 构造、MC 码率分配）在 f_book≈4.1–4.8 时块失败率为 0.61–0.94；同池 NB-Polar（M2+SCL L=16）在 f_book≈1.27 时失败率为 0.031。

## 1. 三个 margin 点（64 块，失败 = 非 exact；undetected 单独列，未并入）
| sc_margin | pooled exact/fail | 失败率 p̂ | Wilson 95% CI (fail) | f_book_sc G2 / G3 |
|---|---|---|---|---|
| 0.02 | 4 / 60 | 0.9375 | [0.8500, 0.9754] | 4.3325 / 4.1108 |
| 0.08 | 9 / 55 | 0.8594 | [0.7538, 0.9242] | 4.2347 / 4.2502 |
| 0.18 | 25 / 39 | 0.6094 | [0.4869, 0.7194] | 4.8179 / 4.7198 |

### 分 session（fail/32）
| margin | G2 (`_1`) | G3 (`_2`) |
|---|---|---|
| 0.02 | 29/32, 0.906 [0.7578, 0.9676] | 31/32, 0.969 [0.8426, 0.9945] |
| 0.08 | 27/32, 0.844 [0.6825, 0.9314] | 28/32, 0.875 [0.7193, 0.9503] |
| 0.18 | 21/32, 0.656 [0.4831, 0.7959] | 18/32, 0.5625 [0.3933, 0.7183] |

### 分层（stratum_official，fail/n）
| margin | A1_CAL_characterization (16) | HELDOUT_model_selection (20) | EVAL_already_decoded (28) |
|---|---|---|---|
| 0.02 | 15/16 [0.7167, 0.9889] | 19/20 [0.7639, 0.9911] | 26/28 [0.7735, 0.9802] |
| 0.08 | 13/16 [0.5699, 0.9341] | 16/20 [0.5840, 0.9193] | 26/28 [0.7735, 0.9802] |
| 0.18 | 9/16 [0.3318, 0.7690] | 12/20 [0.3866, 0.7812] | 18/28 [0.4583, 0.7929] |

分层（stratum_task，fail/n）：heldout_model_selection(8) 8/8、7/8、5/8；never_decoded(28) 26/28、22/28、16/28；previously_decoded_eval(28) 26/28、26/28、18/28（margin 0.02、0.08、0.18 顺序）。A1_CAL/HELDOUT 曾参与 R2 模型选择，已单列为独立 stratum。

## 2. 对 NB 的 2×2 表（同 64 块，逐块配对；NB 取自 `r2_fer_shg_64` part）
表 A（NB-SC 对 二元-SC，**同译码强度**）：格式 = NB exact&Bin exact / NB exact&Bin fail / NB fail&Bin exact / NB fail&Bin fail
| margin | 表 A | 表 B1（NB-SCL 对 二元-SC；**译码强度不同**：NB 为 SCL L=16 top_m=4 CRC-16 联合双层，二元为 SC，仅描述性） |
|---|---|---|
| 0.02 | 3 / 50 / 1 / 10 | 3 / 59 / 1 / 1 |
| 0.08 | 8 / 45 / 1 / 10 | 8 / 54 / 1 / 1 |
| 0.18 | 21 / 32 / 4 / 7 | 23 / 39 / 2 / 0 |

## 3. f_book_sc 与 H
- f_book_sc（含 64 bit tag，不含 per-layer CRC；NB 的 f_book_with_crc 口径不同）：0.02: G2 4.3325 / G3 4.1108；0.08: 4.2347 / 4.2502；0.18: 4.8179 / 4.7198。
- H(X|Y)：G2 0.8168（h_total_bits；δ 分布熵 0.818）。独立层熵 Σh(BER_i)：G2 2.1006、G3 2.0740，比值 Σh/H ≈ 2.57（G2）/ 2.52（G3）——独立层模型的 f 理论下限。
- 分解（review）：f_book_sc≈4.2 ≈ 2.57（模型下限）+ ≈1.7（N=4096 SC 有限长度差距）。

## 4. block_accounting
expected_blocks=64，contributing=64，error=0，not_started=0，resource_abort=0，no_grid_entries=0，sum_of_categories=64，consistent=true。

## 5. undetected
`undetected=0`（所有 margin、所有 stratum；`stop_undetected=false`，`undetected_ids=[]`）；`decode_failed=0`；tag_pass&!exact=0。undetected 未并入 success/FER。

## 6. Caveats
- (a) 独立层模型的 f 理论下限约为 Σh(BER_i)/H(X|Y)≈2.57；冻结基线不做跨层条件化，因此本结论不代表“条件化多级译码的最优二元方案”。
- (b) 网格只覆盖 f≈4.1–4.8，没有覆盖二元块失败率≈0.03 的区间（margin≥0.2 时最低层 k≤16 使整点被丢弃）。
- (c) f 随 margin 不单调（如 G2 0.02: 4.33 vs 0.08: 4.23），这是 100 帧 MC 校准噪声（赢家诅咒 + 粗档 k 候选）造成的，f(m) 不可当作平滑曲线解读。
- (d) CA-SCL 副臂已作废（`INVALID_CA_SCL.md`），Table B2 / ca_scl_descriptive 全部撤回；表 B1 是 NB-SCL 对二元-SC，译码强度不对等。
- (e) 适用域仅限 2026-01-13 这两次 SHG 采集（D-ACQ-05）。
- 另：A1_CAL/HELDOUT 块曾触及模型选择，已单列；64 块 Wilson CI 较宽。
