# R3 效率记账（verification-aware f_eff + 运行时/RSS 上界，2026-09-30）

> 工作项 W1（`docs/nbpolar/CLOSURE_PACKET_20260930.md` §3）。本案纯属案头记账：
> 只读已提交的 `results.json` / `part_*.json` / `RESULT_SUMMARY.md`，
> **不解码、不读原始数据、不跑任何 `run.py`**；未改动任何已有结果目录。
> 全部数字由 `workspace/closure_20260930/r3_accounting.py` 从文件重算，
> 输出 `workspace/closure_20260930/r3_accounting.json`（22/22 核对通过）。
> M2 状态串未改动；是否晋级 `EFFICIENCY_ACCOUNTED` 由 PI 决定（见 §8）。

## 1. 固定参数（冻结）与文件来源

| 参数 | 值 | 文件来源（路径 + 字段） |
|---|---|---|
| N（符号/块） | 32768 | `workspace/r2_fer_shg_64/results.json:frozen_params.n` |
| K1 / K2 | 319 / 6492 | 同上 `frozen_params.k1` / `frozen_params.k2` |
| L / top_m | 16 / 4 | 同上 `frozen_params.list_width_L` / `frozen_params.top_m` |
| CRC | 16 bit | 同上 `frozen_params.crc_bits_extra`（各块 `blocks[].scl.crc_bits=16` 一致） |
| Toeplitz tag | 64 bit | `workspace/r2c_strong_binary_msd_shg_64/results.json:per_point.F2.per_session.G2.tag_bits=64` |
| H_total G2 | 0.8168138204133305 | `workspace/r2_fer_shg_64/results.json:per_session.G2.h_total_bits` |
| H_total G3 | 0.8214782076249098 | `workspace/r2_fer_shg_64/results.json:per_session.G3.h_total_bits` |
| 构造 digest | `055c906472dd…faea1b` | `workspace/r2_fer_shg_64/results.json:frozen_params.construction_digest` |

## 2. R2 主工作点记账（每会话 + pooled）

记账规则：失败块的全部披露照付、该块不产出密钥（整块损失），故
`f_eff = f_book / (1 − p̂)`；`f_eff_upper = f_book / (1 − Wilson 上界)`。
失败计数口径：从 `part_*.json` 逐块数，`scl.exact==false` 或 `status!="ok"` 计失败；
`undetected`（`scl.undetected==true`）单列，不并入成功或 FER。

| 符号 | 公式 | G2 | G3 | pooled | 文件来源 |
|---|---|---|---|---|---|
| D_blk | 5·(319+6492)+16+64 | 34135 | 34135 | — | `r3_accounting.py` 按冻结参数算；`results.json:per_session.<G>.kdb_with_crc=34135` 一致 |
| D_blk_noCRC | 5·(319+6492)+64 | 34119 | 34119 | — | 同上（`kdb_no_crc=34119` 一致） |
| f_book | D_blk/(H_total·N) | 1.2753426830727925 | 1.268101234613064 | — | H 取 `results.json:per_session.<G>.h_total_bits`；与同文件 `f_book_with_crc_computed` 逐位一致 |
| f_book_noCRC | D_blk_noCRC/(H_total·N) | 1.2747448953789544 | 1.267506841182456 | — | 同上；与 `f_book_no_crc_computed` 逐位一致 |
| 失败块 | 逐块数 | 1/32（gbi23） | 1/32（gbi38） | 2/64 | `workspace/r2_fer_shg_64/part_G2_*.json` / `part_G3_*.json`（`scl.exact` + `status`）；与 `results.json:taxonomy_pooled`（exact 62、verify_failed 2）一致 |
| p̂ | 失败数/D | 0.03125 | 0.03125 | 0.03125 | 同上 |
| Wilson 95%（z=1.96） | 标准 Wilson | [0.005537717362550945, 0.15744607800372734] | 同左 | [0.00861195771251659, 0.10697493882294247] | 自算；pooled 与 `results.json:taxonomy_pooled.wilson_95ci` 逐位一致 |
| **f_eff（点）** | f_book/(1−p̂) | 1.3164827696235277 | 1.309007726052195 | — | 由本表 f_book、p̂ 算出 |
| **f_eff_upper（每会话上界）** | f_book/(1−会话 Wilson 上界) | 1.5136629831965038 | 1.505068342223768 | — | 由本表 f_book、会话 Wilson 上界算出 |
| **f_eff_upper（pooled 上界）** | f_book/(1−pooled Wilson 上界) | 1.428115221527847 | 1.4200063242812413 | — | 由本表 f_book、pooled Wilson 上界算出 |
| undetected | 单列 | 0/32 | 0/32 | 0/64 | part 文件 `scl.undetected` 全 false；`results.json:undetected_block_ids=[]` |

失败块核对（§7）：G2 仅 `global_block_index=23`（`verify_failed=true`，L2），
G3 仅 `global_block_index=38`（同），与已裁定（gbi23 G2、gbi38 G3）一致；
`resource_abort_block_ids=[]`。

## 3. λ 分解表（roadmap R3 第 1 条，逐项）

| 项 | 处理 | 理由 |
|---|---|---|
| leak_IR = 5·(K1+K2) = 34055 bit | 计入 f | 两层 GF(32) 冻结坐标披露，每坐标 5 bit，主披露项 |
| CRC 16 bit | 计入 f（f_book）；另报 noCRC 值（§2） | 选路用（top_m=4 联合选路），非安全项；差值仅约 0.0006 的 f |
| tag 64 bit | 计入 f | Toeplitz 64 bit 验证标签公开传输，属披露 |
| P_collision（ε_tag = 2^-64 = 5.421010862427522e-20/块） | 安全参数，不计入 f | 碰撞概率上界，非披露比特；来源：冻结参数（tag 64 bit） |
| FER（整块损失） | 计入 f_eff | 失败块披露已付、无产出，按 `f_book/(1−p̂)` 整块损失计（§2） |
| CAL_sacrifice（λ_cal = 32/(32+4096) = 0.007751937984496124） | 计入产出比例，不计入 f | 每会话 CAL32（32 帧）公开牺牲；分母 4096 = 每会话 64 块池帧数（32 块×128 帧）；来源 `docs/nbpolar/DATA_LEDGER.md` §7（CAL32 32 帧/会话排除在块池外） |
| prior_reveal（M2 参数） | 可忽略（0） | M2 由已公开的 CAL32 拟合（`per_session` 先验来源），不额外泄漏 |
| undetected | 单列，本次 0/64 | 不并入成功或 FER；来源 §2 本表末行 |

## 4. 运行时 / RSS 上界（从文件取数，不重跑）

| 来源 | 实现 / 数据 | 每块 SCL 耗时（均值/最大/最小） | RSS 峰值（最大） |
|---|---|---|---|
| `workspace/r2_fer_shg_64/results.json:blocks[].resources` | scl_joint（Python/numba 参考实现），L=16，真实 | 530.4223976186586 / 554.2258405709872 / 513.925687149982 s | 0.5767021179199219 GiB |
| `workspace/r2e_fer_shg_64_L32_f124/part_*.json:resources` | 原生 Rust SCL，L=32，真实 | 34.66503497585836 / 37.3413404020248 / 33.86912867100909 s | 1.3928718566894531 GiB |
| `workspace/r2b_fer_shg_64_L32_f120/part_*.json:resources` | 原生 Rust SCL，L=32，真实 | 35.32372793347167 / 39.37917227298021 / 33.78551158506889 s | 1.3876495361328125 GiB |
| `workspace/probes/eff-sweep-native/results.json:points`（合成，threads=4，H=0.8165136251536648） | 原生 Rust SCL，L=16，合成 | f=1.25 点：均值 21.86891207363078 / 最大 26.528139255940914 s（n=32，31/32 exact；L=16 各点均值 21.87–23.65 s、最大 26.47–27.85 s） | —（探针未记 RSS） |
| 同上 | 原生 Rust SCL，L=32，合成 | 均值约 39.36–41.30 s、最大 41.54–54.00 s | — |

SC 路径单列（保真检查，不计入工作点运行时）：
R2 `blocks[].resources.wall_sc_s` 均值 20.446992475825027 s（最大 21.880754095036536 s）；
合成探针内 SC 参考点（f=1.2，n=32）均值约 18.86 s/块。

**主工作点（原生 L=16）运行时上界：39.37917227298021 s/块**
（取真实数据上原生 L=32 的每块 SCL 最大耗时，即 R2B 最大值）。
论证：(1) 同一原生代码，L=16 列表宽度是 L=32 的一半，每块工作量严格更少，
故 L=32 在真实数据上的最大耗时是 L=16 在真实数据上耗时的上界；
(2) 原生实现与 scl_joint 按"等价标准 B"判定等价（证据 commit `8fcc9119`
判定线：除 exact 平局外决策等价 + FER 等价；`36025662` 配套 Cargo.lock）。
**本上界由论证得到，非 L=16 真实数据实测。**
硬件：WSL 8 核（任务包给定）；原生为默认线程数
（R2E/R2B `results.json:frozen_params.decoder="…default native threads"`）；
合成探针 `threads=4`（`results.json:threads` 字段）；RSS 取最大值
（三者最大为 R2E 的 1.3928718566894531 GiB）。

吞吐 = 32768 / 每块耗时（符号/s），三项：

| 口径 | 每块耗时 | 吞吐 |
|---|---|---|
| 上界对应的保守吞吐（原生 L=16，论证上界） | 39.37917227298021 s | 832.1150016269786 符号/s |
| 合成 L=16 典型吞吐（f=1.25 点均值；最大耗时对应 1235.2166762944628 符号/s） | 21.86891207363078 s | 1498.3827219970024 符号/s |
| scl_joint 参考实现吞吐（R2 均值；即 STATE.md §0 的旧数"约 60 符号/s"） | 530.4223976186586 s | 61.777180124958065 符号/s |

## 5. 描述性对照（同一记账口径，仅描述）

### 5.1 R2E（NB-Polar，原生 L=32，K=6657即k1=253/k2=6404，D_blk=33365，CRC+tag 口径同 R2）

来源：`workspace/r2e_fer_shg_64_L32_f124/results.json`
（`frozen_params`、`per_session.<G>.h_total_bits`/`f_book_with_crc_computed`）
与 `part_*.json` 逐块计数（口径同 §2）。

| 会话 | f_book（自算 / 文件值） | 失败 | p̂ | Wilson 95% | f_eff（点） | f_eff_upper（会话上界） |
|---|---|---|---|---|---|---|
| G2 | 1.2465741503068324 / 1.2465741503068324（逐位一致） | 1/32 | 0.03125 | [0.005537717362550945, 0.15744607800372734] | 1.286786219671569 | 1.479518542093199 |
| G3 | 1.239496050765047 / 1.239496050765047（逐位一致） | 2/32 | 0.0625 | [0.017310203195157234, 0.2014746724800358] | 1.3221291208160502 | 1.5522313545327815 |

pooled 3/64，Wilson [0.016068725432185196, 0.12899860788542522]
（`results.json:taxonomy_pooled`），undetected 0/64。

### 5.2 R2C 最强二元（硬前缀 MSD + SCL L=16，无 CRC，tag 64 bit；F2 = NB 同披露量点）

来源：`workspace/r2c_strong_binary_msd_shg_64/results.json:per_point.<F>.per_session.<G>.f_realized`
（取作 f_book）与同结构 `taxonomy` 的 exact 计数；
`RESULT_SUMMARY.md` 结论节（"NB 侧付 CRC 16 位，二元侧不付 CRC"；F2/G2/G3 f 与失败数；"不得据此宣称胜负"）。

| 点 | 会话 | f（f_realized） | K_frozen | 失败 | p̂ | Wilson 95% | f_eff（点） | f_eff_upper（会话上界） | f_eff_upper（pooled 上界） |
|---|---|---|---|---|---|---|---|---|---|
| F2 | G2 | 1.2753426830727925（与 NB G2 f_book 逐位相等，设计使然） | 34071 | 2/32 | 0.0625 | [0.017310203195157234, 0.2014746724800358] | 1.3603655286109786 | 1.5971223943938175 | 2.1303346519321322 |
| F2 | G3 | 1.268101234613064 | 34071 | 16/32 | 0.5 | [0.33630614316859386, 0.6636938568314061] | 2.536202469226128 | 3.770675202853346 | 2.1182385237395343 |
| F3 | G2 | 1.3124428818216216 | 35064 | 0/32 | 0.0 | [0.0, 0.1071827150573635] | 1.3124428818216216 | 1.4700016497843074 | 1.3912222658029645 |
| F3 | G3 | 1.3135723320545871 | 35295 | 0/32 | 0.0 | [0.0, 0.1071827150573635] | 1.3135723320545871 | 1.4712666905177403 | 1.3924195112861637 |

F2 pooled 18/64，Wilson [0.18593226105484584, 0.40134162399503504]；
F3 pooled 0/64，Wilson [0.0, 0.056626022971156334]（上界 0.0566 即用于 f_eff_upper 的值）。
**NB 与二元 FER 点不同（NB f≈1.27 处 2/64；二元 F2 同 f 处 18/64、F3 f≈1.31 处 0/64），
且 CRC 开销口径不同，不得据此宣称胜负。**

## 6. 数值核对说明（与 §3.2 预期值的偏差披露）

`r3_accounting.json:expected_checks` 共 22 项，全部通过。其中 20 项为
1e-4 容差内直接通过（D_blk/D_blk_noCRC 精确相等；H 与冻结值逐位一致；
f_book 差 ≤3.2e-7；f_book_noCRC 差 ≤5.2e-6；p̂ 精确相等；
pooled Wilson 差 ≤6.2e-8；f_eff 差 ≤1.8e-5；λ_cal 差约 1.9e-6；
ε_tag 差约 2.1e-22；R2C F3 pooled Wilson 上界差约 2.6e-5）。
以下两项因**预期值印刷精度不足**改按印刷精度做舍入一致性核对
（主线程 2026-09-30 裁决批准；数值本身未作任何改动，如实记录完整小数，
不隐藏）：

(a) `f_eff_upper_pooled_G2`：计算值 1.428115221527847，预期 `≈1.428`，
字面差 0.000115221527847（> 1e-4，曾触发停下、当即上报并获裁决）。
论证：(1) 公式与输入为
`f_book_G2 / (1 − Wilson_pooled_upper) = 1.2753426830727925 / (1 − 0.10697493882294247) = 1.428115221527847`；
(2) 预期值只印 3 位小数，其自身隐含精度为 ±5e-4，比 1e-4 判据本身更粗，
把全精度计算值与低精度预期值在 1e-4 容差下比较，判据本身不适用；
(3) 两个输入都已逐位核对通过：`f_book_G2` 与
`results.json:per_session.G2.f_book_with_crc_computed` 一致（差 3e-7），
pooled Wilson 上界 `0.10697493882294247` 与
`results.json:taxonomy_pooled.wilson_95ci.upper` 逐位一致；
(4) 同公式在 G3 上得 1.4200063242812413，对预期 `≈1.420` 精确吻合，
证明公式与口径无误。处置：舍入到 3 位 == 1.428，通过。

(b) 每会话 Wilson `≈[0.0055, 0.157]`：计算值
[0.005537717362550945, 0.15744607800372734]，上界字面差约 4.5e-4，
但舍入到印刷精度（下界 4 位、上界 3 位）得 [0.0055, 0.157]，完全一致；
偏差源于预期值印刷精度不足，非数据或公式问题（pooled Wilson
印到 6 位小数即可在 1e-4 下直接通过即为旁证）。处置：舍入一致，通过。

## 7. 对 roadmap `f≤1.3` 期望的描述性对照（非门槛）

f_book 满足期望（G2 1.2753426830727925、G3 1.268101234613064，均 ≤1.3）；
f_eff 点值不满足（G2 1.3164827696235277、G3 1.309007726052195，均 >1.3）；
f_eff 上界更高（pooled 上界下 G2 1.428115221527847、G3 1.4200063242812413；
每会话上界下约 1.51）。如实记录，**不作为 R3 门槛**。

## 8. R3 门暂定判定

(a) §2 每个量有公式、数值、文件来源——已满足；
(b) §3 λ 分解表逐项有处理方式与理由——已满足；
(c) §4 运行时/RSS 表完整、上界论证写明——已满足；
(d) §3.6 独立审查——**已回填：PASS**（`workspace/closure_20260930/R3_REVIEW.md`）。

独立审查（只读 Sonnet 子代理）从 64 个 `part_G*.json` 逐块自数、自算
Wilson / f / 吞吐，与主文档及 `r3_accounting.json` 逐位一致：R2 失败块确为
G2 仅 gbi23、G3 仅 gbi38，`undetected=0/64`；`D_blk=34135`、f_book
1.2753426830727925 / 1.268101234613064 与文件值逐位相等；pooled Wilson
[0.00861196, 0.10697494] 与 `taxonomy_pooled.wilson_95ci` 逐位一致；运行时上界
取 R2B 原生 L=32 最大 39.379 s（> R2E 最大 37.34 s，保守取大正确）；吞吐三项
832.12 / 1498.38 / 61.78 符号/s 算术正确；R2C F3 pooled 0/64 上界确为 0.0566
且已用于 f_eff_upper。问题清单 BLOCKER 0 / MAJOR 0 / MINOR 2（合成 L=32 只给
范围、RSS 只列最大——均为汇总呈现，明细在 `r3_accounting.json` 可追溯，不需返工）。

(a)(b)(c)(d) 四项全部满足：
**R3 记账完成，建议 PI 批准 M2 晋级 EFFICIENCY_ACCOUNTED**。
