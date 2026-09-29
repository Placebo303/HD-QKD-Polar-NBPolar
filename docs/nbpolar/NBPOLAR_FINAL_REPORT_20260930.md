# NB-Polar 总报告（2026-09-30）

> 工作项 W2（`docs/nbpolar/CLOSURE_PACKET_20260930.md` §4）。本报告纯属案头整理：
> 只用已提交的 `results.json` / `part_*.json` / `RESULT_SUMMARY.md` / `RESULT_REVIEW.md`
> 等文件，**不解码、不读原始数据、不跑任何 `run.py`**；未改动任何已有结果目录；
> M2 状态串未改动。只陈述已裁定结果，不新增任何未经审查的结论。
> 每个数字后注明来源目录/文件。报告中文，UTF-8，行尾 LF。

## 1. 一句话结论

NB-Polar（M2 先验 + SCL L=16，`workspace/r2_fer_shg_64/`）在两次 SHG 真实采集的 64 块上
f_book≈1.27、块失败 2/64、undetected 0；同池最强二元方案（`workspace/r2c_strong_binary_msd_shg_64/`）
达到同等失败水平约需 f≈1.28–1.31；冻结二元基线（`workspace/r2_binary_baseline_shg_64/`）需 f≈4.1–4.8。

## 2. 数据与协议

- 两次采集：SHG `_1`（即 G2 参照会话，`20260113_SHG_Type2PPLN_3s`）与 SHG `_2`
  （即 G3 参照会话，`20260113_SHG_Type2PPLN_3s_2`），均为 2026-01-13 采集。
  来源：`docs/nbpolar/DATA_LEDGER.md` §1–§2。
- 64 块池定义（来源：`docs/nbpolar/DATA_LEDGER.md` §7）：每会话 32 块，
  帧 0–1023（A1_CAL，8 块，`stratum=A1_CAL_characterization`）+
  帧 1056–2397（CHAR+HELDOUT，10 块，余 62 帧不用，`stratum=HELDOUT_model_selection`）+
  帧 2398–4189（EVAL，14 块，`stratum=EVAL_already_decoded`）；
  CAL32（帧 1024–1055，每会话 32 帧）两会话都保持排除，不计入 64 块。
- CAL32：每会话 32 帧公开牺牲，用于 M2 候选先验拟合（q0/q+1/q−1/q_rest 三元组），
  永不进入块池。来源：`docs/nbpolar/DATA_LEDGER.md` §1–§2。
- 数据使用规则 R1–R5（来源：`AGENTS.md` §5.8，全文见
  `openspec/changes/nbpolar-data-use-rules-revision/design.md` D7）：
  R1 解码≠消耗（重解码已解码块不产生新披露）；R2 统计合法性（参数预冻结、
  完整块集、无事后调参，参与过模型选择的块须分层报告）；R3 每会话只牺牲 CAL32，
  块仍为 128 帧；R4 样本量规则；R5 断言需新采集前先查账本算缺口
  （R2 目标 n=56，64 块已覆盖，缺口为 0）。
- 块长 N=32768 符号/块，q=1024（每符号 10 bit）。来源：
  `docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md` §1、
  `workspace/r2_fer_shg_64/RESULT_SUMMARY.md`。
- 配对参数 W_P=200 / W_S=500 / CIRCULAR / skip=702；P16 冻结构造，
  digest 全文 `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`。
  来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` 首段、
  `workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §1。

## 3. 方法

- M2 ±1 参数化先验：由各会话已公开的 CAL32 拟合（q0/q+1/q−1/q_rest 三元组），
  不额外泄漏。来源：`docs/nbpolar/DATA_LEDGER.md` §1、
  `docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md` §3（prior_reveal 行）。
- 两层 GF(32) NB-Polar，K1=319 / K2=6492（K=6811）。
  来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` 首段。
- SCL 联合两层解码 + CRC-16（L=16，top_m=4）；Toeplitz 64 bit tag 验证。
  来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` 首段、
  `docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md` §1
  （tag 64 bit 来源：`workspace/r2c_strong_binary_msd_shg_64/results.json`
  `per_point.F2.per_session.G2.tag_bits=64`）。
- 实现：R2 主工作点为 scl_joint（Python/numba 参考实现）；R2B/R2E 为原生 Rust
  SCL 实现，原生实现与 scl_joint 按"等价标准 B"判定等价
  （证据 commit `8fcc9119` 判定线、`36025662` 配套 Cargo.lock）。
  来源：`docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md` §4。

## 4. 主结果

R2（主工作点，来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` 全文，
数字逐字取自该目录 `results.json`）：

| 会话 | H_total (bits) | f_book（含 CRC-16） | f_book（不含 CRC） |
|---|---|---|---|
| G2（SHG `_1`） | 0.8168138204133305 | 1.2753426830727925 | 1.2747448953789544 |
| G3（SHG `_2`） | 0.8214782076249098 | 1.268101234613064 | 1.2675068411824560 |

（`kdb_no_crc=34119`，`kdb_with_crc=34135`；披露在解码前无条件发生。）

汇总（pooled，`taxonomy_pooled`）：

| n_blocks | D | exact | verify_failed | decode_failed | undetected | resource_abort | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|---|---|---|
| 64 | 64 | 62 | 2 | 0 | **0** | **0** | 0.03125 | [0.00861196, 0.10697494] |

分层表 `stratum_task`：

| stratum_task | n_blocks | D | exact | verify_failed | undetected | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|---|---|
| never_decoded | 28 | 28 | 27 | 1 | 0 | 0.035714 | [0.006332, 0.177126] |
| heldout_model_selection | 8 | 8 | 8 | 0 | 0 | 0.0 | [0.0, 0.324416] |
| previously_decoded_eval | 28 | 28 | 27 | 1 | 0 | 0.035714 | [0.006332, 0.177126] |

分层表 `stratum_official`：

| stratum_official | n_blocks | D | exact | verify_failed | undetected | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|---|---|
| A1_CAL_characterization | 16 | 16 | 15 | 1 | 0 | 0.0625 | [0.011119, 0.283293] |
| HELDOUT_model_selection | 20 | 20 | 20 | 0 | 0 | 0.0 | [0.0, 0.161130] |
| EVAL_already_decoded | 28 | 28 | 27 | 1 | 0 | 0.035714 | [0.006332, 0.177126] |

分会话：G2 31/32（失败 `part_G2_23.json`，即原 G2 EVAL block 5，
`first_error_coordinate=978` / `first_error_layer=L2`）；
G3 31/32（失败 `part_G3_38.json`，`never_decoded`/A1_CAL 块，首次 SCL 观测）。
undetected 与 resource_abort 在全部维度均为显式 0。
主线程裁定（2026-09-29）：独立 Pre-RESULT 审查 PASS，
D=64≥56、undetected=0、fidelity_compromised=false ⇒ `FER_MEASURED_AT_CONTRACT`。

## 5. 效率边界

f–失败率表（同一 64 块池三轮 NB 测量；f 为含 CRC 的 f_book）：

| 测量 | 配置 | f_book G2 / G3 | exact | 失败 | p̂ | Wilson 95% | 来源目录 |
|---|---|---|---|---|---|---|---|
| R2B | 原生 SCL L=32，K_total=6442（k1=302/k2=6140） | 1.206410 / 1.199560 | 50/64 | 14/64 | 0.21875 | [0.135022, 0.334330] | `workspace/r2b_fer_shg_64_L32_f120/` |
| R2E | 原生 SCL L=32，K_total=6657（k1=253/k2=6404） | 1.2465741503 / 1.2394960508 | 61/64 | 3/64 | 0.046875 | [0.01606873, 0.12899861] | `workspace/r2e_fer_shg_64_L32_f124/` |
| R2 | scl_joint L=16，K1=319/K2=6492 | 1.2753426830727925 / 1.268101234613064 | 62/64 | 2/64 | 0.03125 | [0.00861196, 0.10697494] | `workspace/r2_fer_shg_64/` |

R2D 的 G2 定位表（描述性，非 claim；来源：
`workspace/r2d_locate_f_k_g2/RESULT_REVIEW.md`；G2 32 块，原生 SCL L=32）：

| 配置 | exact/vf | 失败 Wilson 95% | 失败 gbi（层） |
|---|---|---|---|
| f1.22_s0469 | 27/5 | [0.069,0.318] | 7,8,11,23,30（L2） |
| f1.22_s0380 | 27/5 | [0.069,0.318] | 7,8,23（L2）；26,27（L1） |
| f1.24_s0469 | 30/2 | [0.017,0.202] | 8,23（L2） |
| f1.24_s0380 | 31/1 | [0.006,0.157] | 23（L2） |
| f1.26_s0469 | 31/1 | [0.006,0.157] | 23（L2） |
| f1.26_s0380 | 31/1 | [0.006,0.157] | 23（L2） |

（undetected 0；预注册规则机械选中 f1.24_s0380，
K_total=6657/k1=253/k2=6404，f_book_with_crc(G2)=1.2466。）

层归因：R2B 的 14 个失败块 14/14 为 L2 错（L1 错 0），
来源：`workspace/r2b_fer_shg_64_L32_f120/RESULT_SUMMARY.md` §5；
R2E 的 3 个失败块均为 verify_failed 且 L2 相关
（gbi23 G2：L1 错 0 / L2 错 84；gbi53 G3：8/8；gbi59 G3：311/11972），
来源：`workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §2–§5；
R2 的 gbi23 首错层为 L2（L2 错 78 符号），gbi38 在 R2 下 verify_failed
（按同块 R2B 前驱对照：L2 错 68），来源：
`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` §1.4、
`workspace/r2b_fer_shg_64_L32_f120/RESULT_SUMMARY.md` §5。

gbi23（G2 EVAL 块，帧 3038–3165）为跨四轮失败的难块：
R2 verify_failed（L2 错 78）、R2B verify_failed（L2 错 191）、
R2D f1.24_s0380 verify_failed（L2 错 84）、R2E verify_failed（L2 错 84），
在全部配置下均为 L2 失败；计入所有分母，不排除。
来源：`workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §5–§6、
`workspace/r2d_locate_f_k_g2/RESULT_REVIEW.md`。

## 6. 与二元方案对比

### 6.1 冻结二元基线（仅 SC 主臂；CA-SCL 副臂 INVALID）

来源：`workspace/r2_binary_baseline_shg_64/RESULT_SUMMARY.md`
（SC 主臂 Pre-RESULT PASS_WITH_COMMENTS 已发布；
CA-SCL 副臂因 `decode_batch` 把冻结位当 0 的实现缺陷已作废，
见该目录 `INVALID_CA_SCL.md`）。

允许的结论句（照抄）："在 SHG `_1`/`_2` 同一 64 块池上，冻结原生二元 Polar
分层基线（独立比特面、SC、N=4096、PW 构造、MC 码率分配）在 f_book≈4.1–4.8
时块失败率为 0.61–0.94；同池 NB-Polar（M2+SCL L=16）在 f_book≈1.27 时
失败率为 0.031。"

三个 margin 点（64 块，失败 = 非 exact；undetected 均为 0，未并入）：

| sc_margin | pooled exact/fail | 失败率 p̂ | Wilson 95% CI | f_book_sc G2 / G3 |
|---|---|---|---|---|
| 0.02 | 4 / 60 | 0.9375 | [0.8500, 0.9754] | 4.3325 / 4.1108 |
| 0.08 | 9 / 55 | 0.8594 | [0.7538, 0.9242] | 4.2347 / 4.2502 |
| 0.18 | 25 / 39 | 0.6094 | [0.4869, 0.7194] | 4.8179 / 4.7198 |

对 NB 的 2×2 表（同 64 块逐块配对；格式 = NB exact&Bin exact /
NB exact&Bin fail / NB fail&Bin exact / NB fail&Bin fail）：

| margin | 表 A（NB-SC 对二元-SC，同译码强度） | 表 B1（NB-SCL 对二元-SC，译码强度不同，仅描述性） |
|---|---|---|
| 0.02 | 3 / 50 / 1 / 10 | 3 / 59 / 1 / 1 |
| 0.08 | 8 / 45 / 1 / 10 | 8 / 54 / 1 / 1 |
| 0.18 | 21 / 32 / 4 / 7 | 23 / 39 / 2 / 0 |

基线自身的已裁定 caveats：独立层模型的 f 理论下限约为 Σh(BER_i)/H(X|Y)≈2.57
（G2 2.57 / G3 2.52），冻结基线不做跨层条件化，故不代表条件化多级译码的最优二元方案；
网格只覆盖 f≈4.1–4.8，未覆盖二元块失败率≈0.03 的区间。

### 6.2 R2C 最强二元（硬前缀 MSD + SCL L=16，无 CRC）

配置（来源：`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §1）：
硬前缀 MSD + SCL（L=16，无 CRC），genie-SC 蒙特卡洛构造，逐层 μ_i 码率分配；
同一 64 块池；4 个 f 点 × 64 块 = 256 个块点全部 status=ok；
主线程裁定（2026-09-30，Pre-RESULT PASS_WITH_COMMENTS 后）：MEASURED_AT_CONTRACT。

四个 f 点（f 为 f_realized；exact 计数；undetected 均为 0）：

| 点 | f G2 / G3 | G2 exact | G3 exact | pooled exact（失败） | p̂ | pooled Wilson 95% |
|---|---|---|---|---|---|---|
| F1 | 1.200021 / 1.200006 | 0/32 | 0/32 | 0/64（64/64 失败） | 1.0000 | [0.943374, 1.000000] |
| F2 | 1.275343 / 1.268101 | 30/32 | 16/32 | 46/64（18/64 失败） | 0.2812 | [0.185932, 0.401342] |
| F3 | 1.312443 / 1.313572 | 32/32 | 32/32 | 64/64（0/64 失败） | 0.0000 | [0.000000, 0.056626] |
| F4 | 1.412460 / 1.413579 | 32/32 | 32/32 | 64/64（0/64 失败） | 0.0000 | [0.000000, 0.056626] |

（F2 的 f 取该会话 NB f_book 含 CRC 值，G2 1.275343 / G3 1.268101，
二元侧不付 CRC；F3 为设计集自洽点，K_frozen 每块披露位 G2 35064 / G3 35295；
二元达到约 3% 块失败所需 f 仅能给区间：约 1.28 至 ≤1.313，
对 NB f≈1.27 的差距约 +0.01 至 +0.04，不可点估。）

与 NB-SCL（L=16，R2 实测 62/64）的逐块配对四格表（仅计数；
按 `global_block_index` 配对；列 = 二元 exact&NB exact /
二元 exact&NB 非 exact / 二元非 exact&NB exact / 二元非 exact&NB 非 exact；
n=64；**只抄表，不给胜率、不做检验**）：

| 点 | 二元 exact & NB exact | 二元 exact & NB 非 exact | 二元非 exact & NB exact | 二元非 exact & NB 非 exact |
|---|---|---|---|---|
| F1 | 0 | 0 | 62 | 2 |
| F2 | 44 | 2 | 18 | 0 |
| F3 | 62 | 2 | 0 | 0 |
| F4 | 62 | 2 | 0 | 0 |

来源：`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §4。

### 6.3 R2C 构造阶段要点

- 不变性检验（R 值，阈值 R_max=1.25）：G2 R_marginal=1.0094 / R_resid=1.0638，
  G3 0.9894 / 1.0382，均为 compatible=True。
- D1 pmf 交叉验证（8 折，n_used=8192，平局阈值 0.005 nat）：两会话 P-M2 的 CV
  对数似然均高于 P-HIST（P-HIST 更差约 0.133 nat/符号），故选中 P-M2。
- **genie-MC 替代采样 DE 的原因**：PI 修订 E1 批准 §4 构造由采样 DE（m=1024）
  改为 genie-SC Monte Carlo 构造（仅用 CAL32 拟合模型合成帧，真前缀/真 u，
  每层 4096 帧，与译码器同一 min-sum f 节点，按 Z=mean(exp(−s/2)) 升序排序），
  原因：采样 DE 在稀有事件路径上塌缩，把 Pe 0.1–0.4 的位判为完美。
  来源：`docs/nbpolar/R2C_STRONG_BINARY_MSD_CONTRACT_20260929.md` 引言 E1 段；
  诊断依据为合成 Tier-X 探针 `workspace/probes/r2c-layer-diag/`
  （prereg 问题：R2C 硬前缀 MSD+SCL(L=16) 在合成 M2-like 信道上 LSB 侧层 8/9
  为何在大 margin μ 下仍失败；对比 (b) 项即 DE m=1024/4096/16384 与
  genie-MC（min-sum，1024 帧）信息集 + 同 k 下 FER）。
- E2 码率分配由全局 margin 改为逐层 μ_i：每层按设计集控制失败率
  （F3 点逐层 μ_i 与 k_i 见 R2C RESULT_SUMMARY §1.2；F1/F2/F4 由 F3 的 μ 形状
  整体平移得到）；F3 为设计集自洽点（设计集上逐层 e≤2，设计 Σp̃ G2 0.015610 /
  G3 0.014634），不是正确性保证。
- NB 与二元的 FER 点不同（NB f≈1.27 处 2/64；二元 F2 同 f 处 18/64、
  F3 f≈1.31 处 0/64），且 CRC 开销口径不同（NB 侧付 CRC 16 位，二元侧不付），
  **不得据此宣称胜负**，亦不得宣称本结果为二元理论最优或二元性能上界
  （未做 CRC 辅助、软前缀、更大 L 等增强）。

## 7. 效率记账与运行时

本节引用 W1 主文档 `docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md`
的结论与表（全部数字由该文档配套脚本
`workspace/closure_20260930/r3_accounting.py` 从文件重算，
输出 `workspace/closure_20260930/r3_accounting.json`，22/22 核对通过）。

R2 主工作点记账（D_blk=34135，D_blk_noCRC=34119；失败块披露照付、
整块损失，故 f_eff = f_book/(1−p̂)）：

| 符号 | G2 | G3 |
|---|---|---|
| f_book（含 CRC） | 1.2753426830727925 | 1.268101234613064 |
| f_book（不含 CRC） | 1.2747448953789544 | 1.267506841182456 |
| p̂ | 0.03125（1/32，gbi23） | 0.03125（1/32，gbi38） |
| Wilson 95% | [0.00553772, 0.15744608] | 同左 |
| **f_eff（点）** | 1.3164827696235277 | 1.309007726052195 |
| **f_eff_upper（pooled 上界下）** | 1.428115221527847 | 1.4200063242812413 |
| **f_eff_upper（每会话上界下）** | 1.5136629831965038 | 1.505068342223768 |

（pooled Wilson [0.00861196, 0.10697494]；undetected 0/64 单列；
ε_tag = 2^-64 = 5.421010862427522e-20/块，属安全参数不计入 f；
λ_cal = 32/(32+4096) = 0.007751937984496124，计入产出比例、不计入 f；
λ 分解表逐项处理见主文档 §3。）

运行时 / RSS（从文件取数，不重跑）：

| 来源 | 实现 / 数据 | 每块 SCL 耗时（均值/最大） | RSS 峰值（最大） |
|---|---|---|---|
| `workspace/r2_fer_shg_64/results.json` | scl_joint 参考实现，L=16，真实 | 530.42 / 554.23 s | 0.5767 GiB |
| `workspace/r2e_fer_shg_64_L32_f124/part_*.json` | 原生 Rust SCL，L=32，真实 | 34.67 / 37.34 s | 1.3929 GiB |
| `workspace/r2b_fer_shg_64_L32_f120/part_*.json` | 原生 Rust SCL，L=32，真实 | 35.32 / 39.38 s | 1.3876 GiB |
| `workspace/probes/eff-sweep-native/results.json` | 原生 Rust SCL，L=16，合成 | 均值 21.87 s（f=1.25 点）/ 最大 26.53 s | —（探针未记 RSS） |

- **主工作点（原生 L=16）运行时上界：39.37917227298021 s/块**
  （取真实数据上原生 L=32 的每块 SCL 最大耗时，即 R2B 最大值；
  论证：同一原生代码 L=16 列表宽度减半、每块工作量严格更少，
  且原生实现与 scl_joint 按等价标准 B 等价）。
  **本上界由论证得到，非 L=16 真实数据实测。**
- 吞吐（32768 / 每块耗时）：上界对应的保守吞吐 832.1150016269786 符号/s；
  合成 L=16 典型吞吐 1498.3827219970024 符号/s；
  scl_joint 参考实现吞吐 61.777180124958065 符号/s（即 STATE.md §0 旧数"约 60 符号/s"）。
- SC 路径（R2 均值约 20.45 s/块）只是保真检查，不计入工作点运行时。
- 描述性对照（同一记账口径，仅描述）：R2E f_eff 点 G2 1.2868 / G3 1.3221；
  R2C F2 f_eff 点 G2 1.3604 / G3 2.5362，F3 f_eff 点 G2 1.3124 / G3 1.3136
  （F3 pooled 0/64 的 Wilson 上界 0.0566 即用于其 f_eff_upper 的值）；
  NB 与二元 FER 点不同，不得据此宣称胜负。详见主文档 §5。
- 对 roadmap `f≤1.3` 期望的描述性对照（非门槛）：f_book 满足期望
  （G2 1.2753426830727925、G3 1.268101234613064，均 ≤1.3）；
  f_eff 点值不满足（G2 1.3164827696235277、G3 1.309007726052195，均 >1.3）；
  f_eff 上界更高。如实记录，不作为 R3 门槛。
- R3 门判定（四项完整性判定）：(a) 公式/数值/文件来源完整、(b) λ 分解表
  逐项完整、(c) 运行时/RSS 表与上界论证完整、(d) 独立审查
  **PASS**（`workspace/closure_20260930/R3_REVIEW.md`：独立重算逐位一致，
  BLOCKER 0 / MAJOR 0 / MINOR 2）。四项全满足 ⇒
  **R3 记账完成，建议 PI 批准 M2 晋级 EFFICIENCY_ACCOUNTED**
  （是否晋级由 PI 决定；本报告不自行晋级）。

## 8. 工作点决定

PI 2026-09-30 决定：**保持 f≈1.27（R2，L=16）为主工作点**；
f≈1.24 / L=32（R2E）记为已测备选点。
来源：`docs/nbpolar/STATE.md` §0（"PI 2026-09-30：保持 f≈1.27（L=16）为主工作点；
f≈1.24/L=32 记为已测备选点"）、
`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §9 末（同句裁定）。

理由三点：(1) 两点 FER 不可区分——R2E f≈1.24 处 p̂=0.047、
Wilson [0.016, 0.129]，与 R2 f≈1.27 处 Wilson [0.009, 0.107] 有重叠
（来源：`workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §2
"f≈1.24 点在 64 块上与 f≈1.27 点未见可分辨劣化"）；
(2) 净密钥产出对 FER 更敏感（f≈1.24 的披露节省约 0.03 的 f，
不及 FER 从 0.031 升至 0.047 在 f_eff 中的放大）；
(3) L=32 开销约翻倍（原生 L=32 真实每块约 35 s vs L=16 合成约 22 s；
R2B/R2E 与合成探针对照，来源：R3 主文档 §4 表）。

## 9. 局限

- L1：适用域仅限 2026-01-13 两次 SHG 采集自身条件（D-ACQ-05），
  不外推到其他光源/采集配置。
  来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` §6、
  `docs/nbpolar/DATA_LEDGER.md` §7。
- L2：64 块样本的 Wilson 95% CI 较宽（pooled 上界 0.107），
  样本量刚过 D-FER-03 的 n=56 门槛（margin 8 块），不宜读作精确 FER 估计。
  来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` §7(d)。
- L3：R2C 未做 CRC 辅助、软前缀、更大列表 L（L>16）等增强，
  因此不得宣称本结果为二元理论最优或二元方案的性能上界。
  来源：`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §7 第 4 条。
- L4：R2C 设计帧为合成/genie 帧，不含真实信道的尾部
  （真实符号间相关、非平稳等）；不变性检验 R 仅为兼容性检查而非等价证明。
  来源：`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §7 第 2 条。
- L5：R2C 的 μ_i 由设计集选出，存在选择偏差（同一设计集既选 μ 又评估 Σp̃），
  且逐层二分对噪声敏感（网格粒度 0.0046875）；设计集每层仅 1024 帧，
  F3 二分的下一格即出现 3 个错误，点位粒度粗。
  来源：`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §7 第 3、8 条。
- L6：吞吐远未实时——scl_joint 参考实现约 60 符号/s；
  原生 L=16 论证上界对应保守吞吐约 832 符号/s，远不能满足实时 QKD 后处理速率要求。
  来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` §7(e)、R3 主文档 §4。
- L7：gbi23 难块未归因（在 R2/R2B/R2D/R2E 全部配置下均为 L2 失败，
  L2 错 78–191 符号，不随 f 改善；机理推断未做）。
  来源：`workspace/r2d_locate_f_k_g2/RESULT_REVIEW.md`、
  `workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §6。
- L8：G2 32 块参与过 R2D f/k 描述性选择，在正式测量中标为
  selection_touched 分层；R2E 已分层报告（clean G3 30/2 仅描述，
  主判定为 64 块汇总）。
  来源：`workspace/r2d_locate_f_k_g2/RESULT_REVIEW.md`、
  `workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §3.3。
- L9：净密钥产出未计算（需 Eve 信息量估计；f_eff 只是披露侧记账，
  不是净密钥比较）。
  来源：`docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` §1（R3→R4 阶梯）、
  R3 主文档 §7（仅对照 f≤1.3 期望，不作净密钥主张）。
- 附加已裁定 caveats（一并陈述）：R2C F3/F4 的 0/64 的 Wilson 上界 0.0566 > 0.03，
  不能读作"已证明块失败率 ≤3%"（R2C RESULT_SUMMARY §7 第 6 条）；
  R2 只有 SCL 一臂、A1_CAL 与 HELDOUT 块是首次 SCL 观测、
  本次执行预算为本次专用确认（R2 RESULT_SUMMARY §7(a)(b)(c)）。

## 10. 可复现性

解释器（各目录一致）：`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`。
来源：`workspace/r2_fer_shg_64/RESULT_SUMMARY.md`（经 R3 主文档 §4 引用其 timing）、
`workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md` §1、
`workspace/r2b_fer_shg_64_L32_f120/RESULT_SUMMARY.md` §1、
`workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md` §1.1、
`workspace/r2d_locate_f_k_g2/STATUS.yaml`（interpreter 字段）、
`workspace/r2_binary_baseline_shg_64/EXECUTION_TRANSCRIPT.md`。

| 测量 | 目录 | 提交号（`git log --oneline -- <目录>` 首条） | 种子（取自各目录文件） |
|---|---|---|---|
| R2 | `workspace/r2_fer_shg_64/` | `8eb442ec` | `results.json:frozen_params.eval_seed_shared=2026092801`、`tag_master_shared=2026102801` |
| R2E | `workspace/r2e_fer_shg_64_L32_f124/` | `94ff1eda`（执行；包准备 `56668c45`） | `RESULT_SUMMARY.md` §1：eval_seed=2026092904、tag_master=2026102904 |
| R2B | `workspace/r2b_fer_shg_64_L32_f120/` | `5cc2c490`（执行；包准备 `03dcd172`） | `RESULT_SUMMARY.md` §1：eval_seed=2026092902、tag_master=2026102902 |
| R2D | `workspace/r2d_locate_f_k_g2/` | `10760628`（执行；授权 `0bd3d1c4`） | `AUTHORIZATION_RECORD.md`/`STATUS.yaml`：seed=2026092903 |
| R2C | `workspace/r2c_strong_binary_msd_shg_64/` | `af31b162`（执行；实现 `c2647d17`） | `construction_frozen_G2/G3.json` + `results.json`：null_seed G2=20260929 / G3=20260930（不变性检验 null_groups=20）；其余设计冻结见 `construction_frozen_G*.json` |
| 冻结二元基线 | `workspace/r2_binary_baseline_shg_64/` | `87e8082f` | `results.json` 中未见种子字段（SC 确定性路径；复现以该目录 `run.py` + `construction_frozen_*.json` 为准） |
| R3 记账 | `docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md` + `workspace/closure_20260930/` | 本报告提交时随 W4 一并提交（任务包 commit `89f3a0ef`） | 无新种子（纯重算；输入种子即上表各行） |

## 11. 未做 / 后续候选

- 二元 CRC 路径选择（C 阶段）：R2C 未做 CRC 辅助 SCL，
  后续可在二元臂上加 CRC 路径选择后再比较。
- L2 构造/先验改进：失败几乎全在 L2；gbi23 难块未归因；
  L2 构造与 M2 先验的改进是主要算法杠杆。
- 净密钥产出比较：需 Eve 信息量估计，f_eff 记账完成后才可进入。
- 更多独立会话：适用域仅两次同日 SHG 采集；
  是否算作"≥2 独立 session"待 PI 裁定（见收尾回报 §8 问题 (c)）。
- 实时化：吞吐远未实时，原生实现优化与运行时上界收紧。
