# R2 二元 Polar 基线对比合同 — 2026-09-29

> 状态：**PREPARED，未授权执行**。本合同本身不授权、不裁定、不执行任何真实数据
> 操作。执行前须：(1) 独立 reviewer 对本合同 + `workspace/r2_binary_baseline_shg_64/`
> 执行包做 Pre-EXECUTE 审查 PASS；(2) PI 在 `AUTHORIZATION_PROMPT.md` 上给出逐字
> 授权。PI 原话（见 §8）已给出"起草合同，reviewer核查后可以直接开始"的方向性授权，
> 但这**不等于** Pre-EXECUTE 本身的通过，也不等于对本合同冻结的具体数字（f 网格、
> 预算数字）的逐项确认——那些仍按 AGENTS.md §10.3 走独立审查。

## 0. 背景与目的

`workspace/r2_fer_shg_64/`（NB-Polar M2+SCL(L=16) R2 测量，`FER_MEASURED_AT_CONTRACT`，
2026-09-29 主线程裁定）在 SHG `_1`/`_2` 全会话冻结 64 块池
（`docs/nbpolar/DATA_LEDGER.md` §7）上测得 p̂=0.03125（Wilson 95% CI
[0.008612, 0.106975]），undetected=0，f_book_with_crc≈1.268–1.275。该结果**没有
同批二元基线对照**（`workspace/r2_fer_shg_64/RESULT_SUMMARY.md` §7(a) 已明确记录
此 caveat）。本合同的目的是补上这一对照：在**完全相同的 64 块池**（同样的配对/
切帧/符号序列）上，用**本仓库冻结的二元 Polar 分层译码器**（`src/`、`experiments/`
下的原生实现，非 sibling `HD-QKD_Polar_Release` 仓库 `low_dim_opt/` 的改进版）做
一次并列描述性对比，不设"谁胜"门槛。

## 1. 二元冻结基线摸底结果（附文件:行证据）

| 项目 | 结论 | 证据 |
|---|---|---|
| 原生符号维度 | **d=1024**（10 bit/symbol），与 NB-Polar 的 GF(32) 两层框架是对**同一个原生整数**的两种不同拆分：NB-Polar `A = 32*U1 + U2`；二元基线 `A` 的 10 个独立比特面。不是粗粒化/降维关系。 | `scripts/m2_prior_validation.py:341-343,952-953`（符号映射 `(b_A % 1024, b_B % 1024)`）；`:662`（`A = 32*U1 + U2` 打包公式）；`:1024-1025`（`build_counts_1024`，(1024,1024) 联合计数）；`experiments/run_real_polar_max_pie.py` `_extract_real_layer_bers`（对 d=1024 逐位拆层）|
| 构造方法 | **极化权重（Polarization Weight, β=2^0.25）固定可靠度序**，**非 DE、非 genie-aided、非信道自适应**。`src/`、`experiments/` 下从未实现 DE。 | `src/reconciliation/real_polar_sc_rescue.py:27-39`（`_polar_weight_order`）；对照 sibling 仓库文档 `HD-QKD_Polar_Release/docs/POLAR_VS_LDPC_CROSS_REPO_COMPARISON_20260927.md` §1.1（明确记录该仓库 `low_dim_opt` 生产配置才用 DE/O1b-2 joint order，`src/`/`experiments/` 本身没有） |
| 每层 rate 分配 | 逐层**独立**（无跨层条件化/MSD-conditional），按该层原始边际 BER 估计容量上限 `1-H2(BER)`，减一个安全 margin，用 Monte-Carlo FER 校准（memoryless BSC(p=BER) 模型）搜索最大可行 k。margin 是基线自身暴露的单一全局旋钮（CLI `--sc-margin`/`--scl-margins`）。 | `experiments/run_real_polar_max_pie.py:595-651`（`_try_layer_sc`/`_try_layer_scl`）、`:457-505`（`_simulate_layer_sc_fer_early`）、`:1040-1041`（`--sc-margin`/`--scl-margins` CLI）|
| 译码器 | **SC**（numba 精确译码，`polar_sc_decode`/`polar_sc_decode_with_frozen`）与**CA-SCL**（C++，list size **硬编码 L=4**，CRC-16 内部路径选择）。原生 N 只有 {1024, 2048, 4096} 三选一。 | `src/reconciliation/real_polar_sc_rescue.py:83-134`；`src/reconciliation/cpp_polar/main.cpp:14`（`constexpr int kListSize = 4;`）、`:52-60`（`check_crc16`，CRC 在 C++ 内部做候选选择）；`experiments/run_real_polar_max_pie.py:1055-1057`（`--N` choices=[1024,2048,4096]）|
| 验证/记账 | 逐块 Toeplitz 式 universal-hash tag（`src/reconciliation/verification.py`），种子由 `point_id`/`layer_id`/`block_index` 的 SHA-256 派生，**tag_bits 可配置**（非固定 64）。 | `src/reconciliation/verification.py`（全文件，尤其 `universal_hash_tag`/`verification_transcript`）|
| 关键发现：CA-SCL 的 CRC 是"消息编码式"，不是"源编码式" | C++ 译码器内部对**组装出的完整 info 向量**（按升序位置排列）做 CRC-16 校验来做候选选择——这要求发送端把 info 向量最后 16 个（升序）位置**真正填成** CRC(前面的信息位)，而不是这些位置原有的真实测量比特。这是`run_real_polar_max_pie.py` 自己为"合成消息 FER 校准"设计的协议，**直接套用到真实数据的源编码式对齐（Slepian-Wolf 语义）会覆盖/牺牲 16 个真实比特位**。SC 路径没有这个问题（单路径判决，不需要 CRC 消歧）。 | `src/reconciliation/cpp_polar/main.cpp:213-237`（`check_crc16(info_bits)` 内部选路）；`experiments/run_real_polar_max_pie.py:647-699`（`_simulate_layer_scl_fer_early`，`_crc16_append` 把 CRC 编入 info 向量后再编码——合成消息场景的原始设计意图）|

**裁定（本合同自行按"最贴近基线原生做法"原则决定，非阻塞项）**：
1. **主对比臂 = SC**（`polar_sc_decode_with_frozen`）+ 逐块 Toeplitz tag 验证
   （复用 `verification.py`，tag_bits 与 NB-Polar 侧 `chain.tag_bits` 取相同值，
   保证两臂验证开销可比）。SC 是单路径判决，不需要覆盖任何真实数据位，是对
   "源编码式"二元 Polar 协调的最直接、无副作用的复用。
2. **副臂 = CA-SCL(L=4, CRC-16)，仅描述性**，不建立独立的 block-level accept/tag。
   逐 codeword 报告"消息位精确匹配率"，泄漏记账中明示每 codeword 16 bit 的
   CRC 开销（真实数据位被覆盖，不算作已协调内容）。此为本合同对"复用冻结二元
   译码器时的协议适配代价"的显式披露，不隐藏。

## 2. 32768 符号 → 二元码映射方案

- 逐块 32768 个 d=1024 符号 → 10 个独立比特面（layer_idx=0 为 MSB/shift=9，
  layer_9 为 LSB/shift=0，与 `_extract_real_layer_bers` 逐字节一致）。
- 每个比特面 32768 bit → 切成 **8 个 N=4096 码字**（32768/4096=8；N=4096 是
  基线三选一中最大的一个，"最贴近原生、单位披露开销最低"）。
- 每块合计 10×8 = **80 个二元 Polar 码字**。
- 与 NB-Polar 的关系：两种方法消费**完全相同**的 `frames_a`/`frames_b` 原始
  整数数组（同一次 `chunk_frames` 调用产物，本合同的驱动通过**按文件路径 import**
  `workspace/r2_fer_shg_64/run.py` 的 `_reproduce_session_context`/
  `build_session_blocks` 复用，而非重新实现，从代码路径上保证逐符号相同，
  并逐块做 SHA-256 哈希记录作为证据，见 §4）。

## 3. 冻结配置

| 项 | 值 |
|---|---|
| 原生维度 | d=1024（10 层） |
| 每层码长 N | 4096（`n_log=12`） |
| 每层码字数/块 | 8（80 码字/块） |
| 构造 | 极化权重序，β=2^0.25（`_polar_weight_order`，逐层相同，与 BER 无关） |
| 每层 rate 搜索 | `_build_candidates` + `_simulate_layer_sc_fer_early`，FER 门限 0.05，Monte-Carlo 帧数 **100/候选**（见 §3.1，从初稿的 4000 下调） |
| 构造用数据 | **仅 CAL32**（帧 1024–1055，与 NB-Polar 同一 arm=`B_M2_32f_candidate`），不得用 EVAL/HELDOUT/A1_CAL |
| 主译码器 | SC（`polar_sc_decode_with_frozen`），单路径，genie frozen values = Alice 真实 u 域披露值 |
| 副译码器（描述性） | CA-SCL，L=4（C++ 硬编码），CRC-16（消息编码式，覆盖 16 个真实位/码字） |
| 验证 | 逐块 Toeplitz universal-hash tag，tag_bits = NB-Polar 侧 `chain.tag_bits`（运行时读取，非硬编码） |
| f 网格 | 不超过 4 个点，从**短候选清单** `sc_margin ∈ {0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.30}`（7 点，非细网格扫描，见 §3.1）中选取：(a) 与 NB-Polar `f_book_with_crc`（≈1.268–1.275，会话相关）最接近的一点；(b) 在"每层均可行（FER<0.05）"的可用候选集合中再取跨度两端 + 中点，最多凑够 4 点。margin 是基线自身暴露的单一全局旋钮，对 10 层统一施加。 |
| 泄漏记账 | SC 臂：`kdb_sc = Σ_layer 8*(4096-k_layer) + tag_bits`；CA-SCL 臂（描述性）：`kdb_scl = kdb_sc + 16*Σ_layer[k_layer>16]*8`（每可用层每码字 16 bit CRC 开销）。`f = kdb / (H_total_bits × 32768)`，**H_total_bits 与 NB-Polar 同一 session 的 CAL32 拟合值完全相同**（G2: 0.8168138204133305；G3: 0.8214782076249098；直接复用 `workspace/r2_fer_shg_64` 侧已计算的 `h_total_bits`，不重新拟合）。 |

### 3.1 重要发现：冻结 SC 译码器是 O(N² log N)，而非 O(N log N) — 已据此下调搜索规模

`src/reconciliation/real_polar_sc_rescue.py:90-134`（`polar_sc_decode_with_frozen`）
在**每一个**叶子位置（N 个位置之一）都重新跑一遍**全部** n=log2(N) 层的
`_encoding_step` 部分和回传（每层 O(N)），而不是标准 SC 译码器的增量式
O(N log N) 实现。实测（`_selfcheck_sc_timing.py`，JIT 预热后，post-JIT）：

| N | 单次译码耗时 |
|---|---|
| 256 | 0.244 ms |
| 1024 | 4.420 ms |
| 4096 | **80.771 ms** |

缩放比 4096/1024=4×N → 耗时比 80.771/4.420≈18.3×，与 O(N² log N) 预测的
4²×log(4096)/log(1024)=16×1.2=19.2× 吻合（O(N log N) 只会预测 ~4.8×）。

**后果**：本合同初稿的 `CALIB_N_FRAMES=4000` + `sc_margin` 细网格
（[0,0.30] 步长 0.01，31 点）在 N=4096 下，构造搜索单会话预计耗时
**上百 CPU 小时**（31 margins × 10 层 × 最多 ~8 候选 × 4000 帧 ×
80.8ms ≈ 280 小时量级），已通过一次真实尝试证实不可行（该尝试在 N=4096、
CALIB_N_FRAMES=300、6 margin 的更保守设置下运行 >8 分钟仍未完成，被手动
终止）。

**修正（已落实于 §3 冻结配置与 `run.py`）**：
1. `CALIB_N_FRAMES` 由 4000 降为 **100** — 这不是任意让步，而是**基线自身
   `experiments/run_real_polar_max_pie.py` 的 `--frames` CLI 默认值本身
   就是 100**，比"发明一个更大的数字换取统计精度"更贴近"复用基线原生
   做法"的原则。
2. `sc_margin` 由细网格扫描改为**短候选清单**（7 点），呼应基线自身
   `--scl-margins` 默认 `"0.02,0.05"`（一个短的手选列表，不是细扫描）的
   风格。
3. 修正后单会话构造搜索预计耗时量级：7 margins × 10 层 × 最多 ~8 候选 ×
   100 帧 × 80.8ms ≈ **75 分钟**（最坏情形，无早停；早停机制
   `_simulate_layer_sc_fer_early` 的 `max_err_allowed` 早退出对明显不可行
   候选会显著更快）。已用合成烟雾测试（`_smoke_synthetic.py`，N=256 覆写）
   端到端跑通该搜索逻辑，5.6 秒内完成并通过全部自检（构造/SC 译码/tag/
   记账自洽性）。
4. 全量 64 块 × 最多 4 网格点的**实际解码**成本（非构造搜索）：每块每网格
   点 80 码字 × 80.8ms ≈ 6.5s（SC 臂）；64 块 × 4 网格点 × 6.5s ≈ 28 分钟
   总计——远低于 §6 预算的 4 小时，说明 §6 的每块预算数字是充分保守的，
   真正的成本瓶颈是构造搜索（已修正），不是逐块解码本身。

## 4. 口径表（NB-Polar vs 二元基线）

| 维度 | NB-Polar（`r2-fer-shg-64`，已测量） | 二元基线（本合同） |
|---|---|---|
| 数据/配对/切帧 | SHG `_1`/`_2`，W_P=200/W_S=500/CIRCULAR/skip=702 | **完全相同**（同一 `chunk_frames` 调用，按文件路径 import 复用，逐块 SHA-256 核对） |
| 符号 x/y | GF(32) two-layer `A=32·U1+U2` | 同一 d=1024 原始整数，10 独立比特面 |
| H(X\|Y) | 每 session CAL32 拟合（G2 0.8168138 / G3 0.8214782） | **同一数值**，直接复用 |
| f 分子 | K1/K2 冻结位披露 + tag + CRC-16（每块一次） | 冻结位披露（每 codeword）+ tag（每块一次）[+ CRC-16 每 codeword，仅 CA-SCL 副臂] |
| 块单位 | 32768 符号/块，64 块池 | 同一 64 块池 |
| 成功判定 | 整块逐符号全对 = `exact` | 同一定义：`a_hat_sym` 与真实符号数组逐符号全等 |
| undetected | `accepted AND NOT exact`，单列不并入 FER | 同一定义，单列 |
| 分层 | `stratum_official`（A1_CAL/HELDOUT/EVAL）+ `stratum_task` | 复用同一 64 块的两套分层标签（同一 block 元数据，import 复用） |
| 译码器 | M2 先验 + SCL(L=16,top_m=4,CRC-16) 联合两层 | SC（主）+ CA-SCL(L=4,CRC-16)（副，描述性） |
| 构造用数据 | 仅 CAL32 | 仅 CAL32 |
| 验证 | Toeplitz tag（`chain.toeplitz_tag`） | Toeplitz universal-hash tag（`verification.py`，同 tag_bits） |

### 4.1 译码器强度对等性（主线程要求，2026-09-29 补）

两侧各有两个译码器，强度并不对等，逐项说明，避免读者把不同强度的数字混着比：

| 对比 | 译码器 | 强度关系 | 在结果中的角色 |
|---|---|---|---|
| **表 A**：NB-SC vs 二元-SC | NB 侧 `run_g2_block` 内部的 SC 描述性基线（`sc_descriptive`/`fidelity.actual`）对二元侧 `polar_sc_decode_with_frozen` | **同强度**：两者都是单路径、无 list、genie frozen-values 的 SC 译码 | **主比较**——唯一"公平"的头对头对照，两侧都不需要额外记账假设 |
| **表 B1**：NB-SCL(L=16) vs 二元-SC | NB 侧 M2+SCL(L=16,top_m=4,CRC-16) 联合两层对二元侧 SC（L=1，无 list） | **不同译码强度**（NB 侧 list size 16 远大于二元侧的 1） | 仅描述性参考，**不得**读作"二元不如 NB-Polar"——差异里混有 list size 的贡献，不是纯粹的编码方案差异 |
| **表 B2**：NB-SCL(L=16) vs 二元-CA-SCL（消息位代理） | NB 侧同上对二元侧 CA-SCL(L=4,CRC-16) 的 `all_applicable_msg_exact`（该块每个码字的**消息位**——不含 16 bit CRC 槽——全部精确匹配） | **不同译码强度**（L=16 vs L=4）**且不同判定口径**（NB 侧是整块逐符号判定；二元 CA-SCL 侧的"代理"指标从未尝试还原 CRC 槽位的 16 个真实比特，二者不是同一件事） | 仅描述性参考，双重警示：既不对等译码强度，也不是真正的整块精确判定 |

**结论限定**（并入 §5 判定规则）：本合同的**唯一**"公平对照"是表 A（同为 SC、同为单路径、无 list）。表 B1/B2 只用于展示"用更强的联合两层 SCL(L=16) 能多解出多少块"这一描述性事实，不构成对二元 Polar 编码方案本身劣于 NB-Polar 的判定——若要做真正对等的强度对比，需要在二元侧实现一个不牺牲真实数据位的、L 可比的 list 译码协议，这超出本合同范围（`TASK_PACKET.md` D_BIN_PRIMARY_ARM）。

## 5. 判定与报告规则

- **不设"谁胜"门槛**。只做描述性对比统计：两臂在同一 64 块上的 pooled FER、
  Wilson 95% CI（z=1.96），以及 `stratum_official`/`stratum_task` 分层表（格式
  与 `r2_fer_shg_64/RESULT_SUMMARY.md` 一致）。
- **逐块配对四格表**：对每个 f 网格点，生成 §4.1 定义的表 A（NB-SC vs 二元-SC，
  **唯一的同强度主比较**）、表 B1（NB-SCL(L=16) vs 二元-SC）、表 B2（NB-SCL(L=16)
  vs 二元-CA-SCL 消息位代理），逐块按 `(session, global_block_index)` 匹配、
  以 `frame_start`/`frame_end` 逐块核验确系同一块（两侧均从同一个 import 的
  `build_session_blocks` 派生，理论上不应出现不一致；一旦出现不一致须显式列出，
  不静默丢弃）。四格表只报计数，不计算任何"胜率"统计量，不作为判定依据。
  NB 侧数据只读取 `workspace/r2_fer_shg_64/` 已提交的 `part_*.json`，不重跑
  NB 解码。**undetected 归入四格表的"非 exact"格**（不单列一格）；
  `stop_undetected` 是全局标志（扫描全部块×全部网格点，`undetected_ids` 带
  `sc_margin`），不针对单个表。
- **结论限定范围**：任何结论必须显式声明"仅适用于 2026-01-13 两次 SHG
  `Type2PPLN_3s` 采集自身条件，仅适用于本合同冻结的 N=4096/PW 构造/SC 主译码器/
  该 f 网格点"，不得外推到其他数据、其他码长选择、或 sibling 仓库
  `low_dim_opt` 的改进构造（DE/O1b-2/MSD-conditional）。
- CA-SCL 副臂的数字**只能作为描述性参考**，不得与 NB-Polar 的 SCL(L=16) 数字
  直接比较列胜负（不同 L、不同 CRC 语义、且 CA-SCL 副臂本身牺牲 16 bit/codeword
  真实数据位）。
- undetected≥1（任一臂、任一网格点）⇒ 单列 block id，不并入该臂该网格点的 FER
  分母/分子，且该 f 网格点的判定保持"描述性搁置"（不因 undetected 而 STOP 全部
  网格点）。
- 保真度：由于二元侧复用与 NB-Polar 完全相同的会话重建代码路径（import，非
  重新实现），不存在"保真核对失配"这一风险类别（无独立实现可能产生分歧）；
  仍逐块记录 SHA-256 作为可追溯证据。

## 6. 预算

- 全量 64 块 × 最多 4 个 f 网格点：总 wall ≤ **4 小时**（比 `r2_fer_shg_64` 的
  3 小时宽，因为要在每块上多跑最多 4 个网格点，而非 1 个）。按 §3.1 的实测
  时序：构造搜索 **每 session ~75 分钟量级**（最坏情形，无早停）**× 2
  session ≈ 150 分钟**，加上逐块解码 ~28 分钟量级（64 块全部），**合计
  ≈178 分钟 ≈ 3.0 小时**，仍低于 4 小时预算但留有的余量比"75 分钟"这个
  单会话数字看起来的要窄——该预算数字仍然够用，但不是"随便宽松"，
  Pre-EXECUTE 复核应留意这一点（2026-09-29 Pre-EXECUTE 第一轮 C2 意见：
  早先文档把 75 分钟误当作两个 session 合计的量级，此处已更正为单会话
  数字并给出合计）。
- **执行方式：串行单进程**（Pre-EXECUTE 第二轮 F4 后如实表述：代码里没有 fork/并行，
  没有父进程强杀；早先"8 路并行""120 s margin 硬终止"的说法已删除，对应常量
  `MAX_PARALLEL`/`HARD_TERMINATE_MARGIN_S` 和 `multiprocessing` 导入已从 `run.py` 移除）。
- **总 wall 检查（代码内，4 h）**：`main()` 开始计时（`_now()` 单调钟）；每个 session 的
  construction 开始前检查一次，每块开始前检查一次；一旦超过 `BUDGET_WALL_S_TOTAL`，
  不再启动任何新工作——尚未开始的块写 `status="not_started_total_wall_budget"` 的
  part 记录（不含 grid 结果，含检查点/已用时间），正在跑的块允许跑完。not_started 的块
  不进 D，但在 `results.json` 的 `block_accounting`/`not_started_block_ids` 中单独计数；
  若某网格点的 pooled D<56 则该点标 INSUFFICIENT（D-FER-03，仅为描述性标注）。
- **每块 wall ≤ 1200 s**：从块开始累计计时，每个网格点开始前检查，超限则该块剩余
  网格点记 `resource_abort_wall_mid_grid`（不是"每网格点各 1200 s"）。
- **RSS ≤ 4 GiB**（本任务书面授权指定，宽于 `r2_fer_shg_64` 的 2 GiB，因为要同时持有
  SC+CA-SCL 两个译码路径 + 多网格点中间结果）。
- **两遍执行顺序（主线程裁定 D_BIN_TWO_PASS）**：
  - **第 1 遍（主臂）**：两个 session 各做 construction，然后对全部 64 块 × 选定的 f
    网格点**只跑 SC 主臂**（含逐块 tag 判定）。总 wall 检查在每个 session 的 construction
    前和每块前；超限的处理如上（not_started）。
  - **第 2 遍（副臂，描述性）**：第 1 遍结束后，只要总 wall 还有余量，再对第 1 遍状态为 ok
    的块 × 网格点跑 CA-SCL 副臂；**每块开始前**检查总 wall，超限后该块（及其后所有块）的
    CA-SCL 条目记 `ca_scl_not_started_total_wall_budget`（写入独立的 `scl_part_*.json`，
    不改动第 1 遍的 `part_*.json`）。该标记**不影响** SC 主臂的 D、分层统计和表 A/B1。
  - 理由：串行预计耗时可能触及 4 h（见下），若像原来那样每块 SC+CA-SCL 交错执行，4 h 检查
    会按块截断，连主臂的块也跑不全；两遍顺序保证"总 wall 不够时，被牺牲的是描述性副臂，
    而不是主臂的样本量"。
  - 汇总、表 A、表 B1 **只依赖 SC 主臂**；表 B2（NB-SCL vs 二元-CA-SCL 消息位代理）只统计
    CA-SCL 已跑完的块，`table_B2_coverage` 写明纳入了多少块 / 共匹配多少块；每个网格点的
    `ca_scl_descriptive` 报告 `coverage`（已完成条目数 / SC-ok 条目数）和 not_started 条目数。
- **串行预计耗时**：construction 约 151 min（每 session 约 75 min 最坏情形 × 2）+ SC
  解码约 28 min（第 1 遍合计约 3.0 h），另加 CA-SCL 副臂（第 2 遍；C++，L=4，**未实测**；
  粗估每码字约 0.05–0.2 s、全量 20480 个码字约 15–70 min）⇒ 合计约 3.3–4.2 h；上限一端
  会在第 2 遍触及 4 h 检查，此时**只有 CA-SCL 副臂被截断**（第 1 遍已完整，除非 construction/
  SC 自身就超时，此时后段块记 not_started，若因此 D<56 则该网格点报 INSUFFICIENT）。
- RSS 检查（Pre-EXECUTE 第一轮 C1 后）：`run.py` 常量 `BUDGET_RSS_GIB_PER_BLOCK=4.0`，
  每个网格点解码后读一次 `/proc/self/status` 的 VmHWM；超限则该条目记为
  `resource_abort_rss_post_decode`（不进 D，计入 resource_abort，字段保留供审计）。
  **该读数是整个 worker 进程自启动以来的峰值，不是单个网格点的增量**，因此是
  "检查点处的事后记录"，不证明超限一定由该网格点造成；`undetected` 的扫描不受
  此状态影响（安全信号不被预算状态掩盖）。
- **PENDING-BUDGET（继承自 `r2_fer_shg_64` 的同类未决事项）**：以上数字是本
  operator 按"预算不足会导致每块 resource_abort"的同一论证方式给出的估计值，
  非已裁定的 D-ACQ-06 类正式预算行。需 Pre-EXECUTE reviewer 与 PI 在授权文本中
  确认或调整。
- **`--dry-run-one` 功能保留但本次执行不先跑**（主线程裁定 C5：dry-run 自身要做
  约 75 min 的 construction 且结果随后丢弃；有了代码内总 wall 硬检查，就不需要先靠
  dry-run 预判是否超时；见 `STATUS.yaml` `dry_run_plan`）。如日后运行 dry-run（1 块×
  全部网格点，仅测时，不计入 `results.json`），其用的块固定为 G2 `global_block_index=0`（帧 0–127，A1_CAL_characterization/
  never_decoded）；其全部输出（construction + part）写入子目录 `dry_run/`，
  标注 `dry_run=true`、"不计入结果"；正式全量运行**重新解码**这一块并写入顶层
  `part_G2_00.json`，construction 也重新构建，绝不读取/复用 `dry_run/` 下任何文件。

## 7. STOP 规则

- 任一块任一网格点触发 `resource_abort_*` ⇒ 记录该 (block, margin) 状态，
  不静默丢弃；继续其余组合。
- 总 wall 预算（4 h，代码内检查）耗尽 ⇒ 停止启动任何新工作（新 session 的
  construction、第 1 遍新块、第 2 遍新块）；第 1 遍未启动的块记
  `status="not_started_total_wall_budget"`，不进 D，单独计数（`block_accounting`）；
  第 2 遍未跑的 CA-SCL 条目记 `ca_scl_not_started_total_wall_budget`（不影响 SC 主臂的
  D 和表 A/B1；表 B2 只统计已跑完的块并标明覆盖数）；正在跑的块允许跑完。不调参、不砍网格点。
- 块级 `error:*`（含块中途异常）⇒ 记入 `error_block_ids`，该块不进任何分类统计；
  `results.json` 核对 `64 = contributing + error + not_started + resource_abort
  (+ no_grid_entries，应为 0)`，不成立则 `block_accounting.consistent=false`。
- undetected≥1（任一维度）⇒ 单列，STOP 该 f 点的"判定"（描述性搁置，非终止
  整个测量）。
- CA-SCL 库首次调用触发的自建（`cpp_polar/ca_scl.so`）失败 ⇒ 副臂整体跳过
  （stderr 提示，`ca_scl_descriptive.n_codewords_applicable=0`），SC 主臂不受影响、不 STOP。
- 正式全量运行启动前 `results.json` 已存在，或顶层已存在任何 `part_*.json`（一个
  即触发）⇒ `_fail` 拒绝运行（additive-only；代码强制，`_test_f3_guard.py` 覆盖）。
  `dry_run/` 下的文件不计入此检查。

## 8. 一次性执行规则（one-shot）

- `reruns=0`；仅允许因实现缺陷（非参数/网格/预算不满意）重启一次，且必须记录
  为独立 attempt，不静默覆盖。
- 网格点（sc_margin 集合）、CAL32-only 构造范围、FER 门限（0.05）、
  CALIB_N_FRAMES（100）等在 Pre-EXECUTE 通过后**冻结**，执行期间不得因结果
  不理想而调整。
- 本次测量为**描述性对比**（非 NB-Polar 侧 R2 那样的 Tier-Y 决策门），但仍遵循
  one-shot 纪律，因为它消费同一批已受保护的真实数据块。

## 9. R1–R5 适用说明

- **R1（安全）**：本合同不产生对 CAL32/EVAL/HELDOUT/A1_CAL 帧边界之外的任何新
  接触；"解码≠消耗"（R1）适用——EVAL 段块被二元基线重新解码不构成新的数据消耗
  或新披露类别之外的风险（新披露仅是二元侧自身产生的 frozen-bit/tag/CRC，已在
  §3/§4 记账）。
- **R2（统计）**：本合同的方法与全部参数（构造、f 网格、决策器选择、FER 门限）
  在触碰 EVAL/HELDOUT 数据前，仅用 CAL32 冻结；报告完整声明的 64 块集，不挑块；
  参与过模型选择步骤的块（HELDOUT_model_selection）继续按 NB-Polar 侧已建立的
  分层标注，不得径直排除。
- **R3（分段）**：不新划任何段；CAL32（1024–1055）继续排除出块池；复用
  DATA_LEDGER.md §7 的同一 64 块边界，不重新切块。
- **R4（样本量）**：`n=64` 沿用已确认覆盖 `n=56`（D-FER-03）的样本量结论，本
  合同不重新做样本量反推，也不用于反推采集配额政策。
- **R5（流程）**：本合同不主张"需要新采集"；执行前已核对 DATA_LEDGER.md §7，
  确认 64 块池已足够覆盖本次对比需求，无缺口。

## 10. PI 授权原话（2026-09-29）

> "按建议起草对比合同，reviewer核查合同后可以直接开始。"

以及随附的口径建议（数据/配对复用、二元方法选择、效率 f 记账、成功判定、
比较方式）已逐条采纳，落实于 §1–§6。此授权是**方向性**授权（"起草合同"+
"reviewer核查后可以直接开始"），**不豁免** AGENTS.md §10.3 的独立 Pre-EXECUTE
审查，也不构成对本合同 §6 预算数字、§3 f 网格具体搜索范围的逐项 PI 确认——这些
仍需在 `AUTHORIZATION_PROMPT.md` 的最终授权文本中逐字确认或调整（Pre-EXECUTE
reviewer 核查通过后，由 PI 在该文本上签字/确认即视为"可以直接开始"的落实）。

## 11. 未决/待主线程裁定的点

无阻塞项。以下为本 operator 已按"最贴近基线原生做法"原则自行裁定、供主线程
知悉（非阻塞）：
- SC 为主臂、CA-SCL 为描述性副臂（§1 裁定 1/2）——如主线程认为应反过来（CA-SCL
  为主臂），需要先解决"CRC 覆盖真实数据位"的协议设计问题（本合同未设计该方案）。
- 每层 N=4096（三选一中最大值）而非 1024/2048——如主线程希望改用更小 N（更多
  码字/层但每码字开销占比更高），是数值层面的可调项，不改变本合同其余结构。
- f 网格候选为 7 点短清单 `{0.02,0.05,0.08,0.12,0.18,0.25,0.30}`（§3.1，已取代
  初稿的 [0,0.30] step 0.01 细网格）；执行 `--dry-run-one` 之后若发现该清单不能覆盖
  f≈1.27 附近的可用点，需要主线程决定是否扩充清单（非阻塞，但会改变实际网格点数值）。

## 执行与裁定结果（2026-09-29 追加）

- 执行：`workspace/r2_binary_baseline_shg_64/`，两遍串行（pass1 SC 主臂 2314.9 s，pass2 CA-SCL 副臂 3240.6 s，总 5556.4 s），exit 0，reruns 0，64 块全部 contributing。
- 独立 Pre-RESULT 审查（`PRE_RESULT_REVIEW.md`）：SC 主臂 PASS_WITH_COMMENTS；CA-SCL 副臂 FAIL（`run.py:377-404` 用 `decode_batch` 把冻结位当 0）。
- 主线程裁定：SC 主臂发布（`RESULT_SUMMARY.md`）；CA-SCL 副臂作废（`INVALID_CA_SCL.md`），表 B2 与 ca_scl_descriptive 撤回，是否修复重跑须 PI 另行裁决。
- 允许的结论句：在 SHG `_1`/`_2` 同一 64 块池上，冻结原生二元 Polar 分层基线（独立比特面、SC、N=4096、PW 构造、MC 码率分配）在 f_book≈4.1–4.8 时块失败率为 0.61–0.94；同池 NB-Polar（M2+SCL L=16）在 f_book≈1.27 时失败率为 0.031。
- caveats：独立层 f 下限≈2.57，冻结基线无跨层条件化；网格 f≈4.1–4.8 未覆盖块失败率≈0.03；f(m) 非单调属 MC 噪声；适用域仅限 2026-01-13 两次 SHG 采集。
