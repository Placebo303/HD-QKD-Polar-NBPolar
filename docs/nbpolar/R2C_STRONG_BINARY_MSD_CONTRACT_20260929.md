# R2C 最强二元对照臂合同（条件化 MSD 硬前缀 + SCL）— 2026-09-29

> 状态：**DRAFT / PREPARED，未授权执行**。本文只冻结设计与实现任务清单；不实现驱动、不执行。
> 执行前须：(1) 实现完成并通过 T0–T2 测试；(2) 独立 Pre-EXECUTE 审查 PASS；(3) PI 对 §12 裁决点逐项回复并在
> `AUTHORIZATION_PROMPT.md` 上授权。任何真实数据接触（含 CAL32 读取）都属于执行的一部分，本阶段不做。
> 前置：R2（NB-Polar，p̂=0.03125）与 R2B（冻结原生二元基线，f_book≈4.1–4.8 时块失败率 0.61–0.94，
> 见 `R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` 与 `workspace/r2_binary_baseline_shg_64/`）。

## 0. 目的与结论限定

R2B 的二元基线是"独立比特面 + PW 序 + N=4096 + SC"，Pre-RESULT 审查指出其 f 下限 2.57 是模型（无跨层条件化）所致，
不能代表"二元方案的能力"。本合同构建 **"硬前缀条件化 MSD + SCL(无 CRC)，冻结位取 Alice 真值，DE 构造"** 的最强可行二元臂，
在**同一 64 块池**上与 NB-Polar 做公平对比。

**唯一允许的结论句型**："在 SHG `_1`/`_2` 同一 64 块池上，硬前缀 MSD + SCL(L=…，无 CRC，DE 构造，全局 margin 码率分配)
在 f=… 时块失败率为 …"。**不得**宣称这是二元方案的理论最优（未做：软前缀/多假设前缀、CRC 辅助 SCL、逐层 FER 均衡分配、
更大 L、联合迭代）。适用域仅限 2026-01-13 两次 SHG 采集。

## 1. 复用组件核对（逐条，行号取自 lab `b9f74ab` 工作区）

| 前置证据 | 核对结果 |
|---|---|
| 表形状 `(2^i, d)`，仅自然二进制、d 为 2 的幂 | 属实：`msd_conditional.py:78-82`（`llr[i]` 形状 `(2**i,d)`）、`:160-166`（`d` 须 2 幂，counts 须 `(d,d)`）。本项目 d=1024、A 为原始整数的自然二进制位，满足。 |
| scl_cpp 只返回最优一条路径、无 CRC | 属实：`scl_fast.py:162-201`（返回 `u_hat, path_metrics, stats`，单路径）；`msd_scl.cpp:407-415` 取最小 pm。 |
| `decode_batch` 接收 `frozen_values` | 属实：`scl_fast.py:162-178`、`_prepare` `:154-157`（形状 `(frames,N)`，二值）；C++ 冻结分支读 `frozen_row[pos]`（`msd_scl.cpp:329`）。**R2B 的 CA-SCL 失败即是传了全 0 冻结值**——本合同必须传 `u_full` 在冻结位上的真值（lab `polar_run.py:~180-186` 同此做法）。 |
| rate_allocation 的 MC 用 BSC+全零冻结位，不适用 | 属实（`rate_allocation.py:1-20,41-58`，`bsc_llr`）。本合同**不用**该模块，自建"条件信道合成设计集"MC（§5）。 |
| polar_run.py:156-219 在测试帧上选 k | 属实：`polar_run.py:~156-208` 用 test 帧 `a_t,b_t` 的解码结果 `chosen=(ks,…)` 选 k（`alive` 累计也在测试帧上）。**本合同禁止此做法**，k 仅由 CAL32 派生量决定（§5）。 |
| 导入 scl_fast 会把 .so 写进 lab 目录 | 属实：`scl_fast.py:27-29,44-68`（`CPP_DIR = <lab>/src/qkd_recon/scl_cpp`，`build_library` 在其下编译）；`polar_core.py` 的 `@njit(cache=True)` 还会写 numba 缓存/`__pycache__`。措施见 §11 L-1。 |
| lab HEAD b9f74ab，工作区有未提交改动 | 属实（`git status`：`README.md`、`docs/README.md`、`experiments/polar_vs_ldpc_fair_2026-01-07/polar_run.py` 已改，`v4_bestcfg/` 未跟踪）。**本合同 import 的 4 个模块（`msd_conditional`、`scl_fast`、`polar_core`、`de_frozen` 及 `scl_cpp/msd_scl.cpp`）无未提交改动**；`polar_run.py` 有改动，故只作只读行为参照（§11 T2-c），不 import。执行时记录 5 个文件的 sha/`git diff --stat` 作为 provenance。 |
| 补充发现 | `scl_fast.py` 无 `decode_batch_frozen`（R2B 复核提到的那个属 Release 仓库 wrapper）；lab 里 `decode_batch(…, frozen_values, …)` 本身已是 genie 冻结值接口，无需别的入口。`de_frozen.de_llr_populations_from_root`（`de_frozen.py:105-128`）支持任意对称根，`_MAX_POPULATION_VALUES=8e7`（N=32768 时 m≤2441）。 |

**关键数据事实（设计约束）**：CAL32 = 32 帧 × 256 对 = **8192 个符号**（`G1_FRAME_PAIRS=256`）。1024×1024 联合表有 10⁶ 个格，
逐前缀分组表（layer 9 有 512×1024 格）在 8192 样本下完全不可估计——**joint 版不可行，无论残差检验结果如何**（§3）。

## 2. 数据（冻结）

- 复用 `workspace/r2_fer_shg_64/run.py` 的 `build_session_blocks`、`_reproduce_session_context`（按文件路径 import，不改写），
  得 G2/G3 各 32 块，`d=1024`，块内 32768 符号（128 帧×256），10 个比特平面，layer 0=MSB（shift=9），LSB 最后；
  与 `_extract_real_layer_bers`/NB 的 `A=32·U1+U2` 是同一原生整数的不同拆分。
- 逐块 `frame_start/frame_end` 与 R2 part 记录核对，不一致则显式列出。
- 建表/构造/选 k **仅用本 session 的 CAL32**（帧 1024–1055，`g2_cal_ids(ARM)`）；EVAL/HELDOUT/A1_CAL 不得用于任何设计步骤。
  两个 session 各自独立建表（不跨 session 共享）。
- R1–R5：无新披露类别（"解码≠消耗"）；不新划段；沿用 64 块分层；R4 不反推配额；R5 缺口=0（DATA_LEDGER §7）。

## 3. 信道模型：shift 版 vs joint 版（冻结规则）

**设计决定：joint 版被数据量排除（§1 末），主模型为 shift-invariant（差分域）模型。** 仍须检验循环移位不变性以决定"是否可用"，
阈值冻结如下（全部只用 CAL32）：

1. **残差检验（带噪声基线）**：计算 `shift_model_residual(counts_cal, 1024)['resid_mean']`（记 r_real）；同时从拟合的差分 pmf
   合成 20 组各 8192 样本（a 均匀、`b=(a+δ) mod 1024`）得 r_null 均值。判据 **R = r_real / r_null ≤ 1.25** 视为"与循环模型相容"
   （8192 样本下裸残差被采样噪声主导，故必须相对零假设基线，不能用绝对阈值）。
2. **边缘均匀性**：`marginal_uniformity_l1` 也做同样的相对零假设比较（≤1.25×null）。
3. **R>1.25 或边缘不均匀 ⇒ 不自行降级**：模型不相容，没有更好的 joint 替代（数据量不足），本合同 **STOP 并交 PI**（§12-D2）。
4. **差分 pmf 的来源（在两个候选中用 CAL32 内部 8 折交叉验证对数似然择优，冻结）**：
   - P-M2：NB 侧同一 CAL32 的 M2 拟合联合 `fit['joint']`（`fit_g2_arm`，参数 q0/q+1/q−1/q_rest），经 `difference_pmf` 投影为 1-D pmf——
     **与 NB 使用同一信息量**，方差最低；
   - P-HIST：`smooth_difference_counts(delta_counts, 1024, α=1.0)`（lab 的 polar_run 默认；α=1 相当于 1024 个伪计数占 8192 的 12.5%，偏差大）。
   - 选每符号 CV 对数似然较高者；差值 <0.005 nat/符号则取 P-M2（与 NB 对等优先）。两者均记录入结果。
   `fit['joint']` 是否为循环结构（M2 的 ±1 三元组是差分域参数，预期是）由实现者在 T0 验证；若不是循环结构，则 P-M2 投影会失真，
   直接取 P-HIST 并报告。
5. 表构建：`build_msd_llr_tables_shift` 的 `smoothing_mode="diff_pmf"`；α 对 P-M2 取 0（pmf 已参数化，无稀疏格），对 P-HIST 取 1.0；`clip=30`（lab 默认）。
6. 每层条件容量 `caps_i` 用同一 pmf 的 `conditional_capacities`（差分 pmf 重建的联合矩阵上计算，取 `conditional_mi_bits`），Σcaps_i=I(A;B)（模型）。

## 4. 码长与构造

- **每层 N=32768（n_log=15）**：与 NB 块长一致，一个块每层恰 1 个码字，10 个码字/块；有限长度损失最小（R2B 的 N=4096 造成约 1.76 的 f 差距）。
  lab 引擎：`msd_scl.cpp` 对 n 仅要求 2 的幂（`:270-274`，`ilog2_pow2`），紧凑引擎内存 ≈ 3n 窗口×2L 路径，N=32768/L=16 约几十 MB，**无引擎限制**；
  lab 的 benchmark 只测到 n_log=14，故 n_log=15 正确性由 T0/T2 的小规模等价核对 + 一次 N=32768 计时/合成 FER 冒烟保证（不是理论保证）。
  因不需要 2×16384 备选，不存在披露差异；若 T0 计时/内存失败才回退 2×16384（此时每层 2 码字、冻结位总数不变，仅 SCL 每码字统计独立性不同——
  块 FER 记账仍以整块为单位，披露分子不变。回退须 PI 知情，非自动）。
- **构造：DE，不用 PW**（PW 在 N=16384 的 BEC 上已被 lab 证明崩溃，`de_frozen.py` 模块头）。DE 根分布逐层来自 **CAL32 模型的条件信道**：
  从 §3 的 pmf 合成 M_root=4096 个 (a,b,prefix)，计算 layer-i 的条件 LLR `L`，取符号对齐 `L·(1−2a_i)`（满足 `de_frozen` 的对称/全零码字约定），
  作为 `de_llr_populations_from_root(root, n_log=15, n_samples=1024, seed=20260929)` 的根。每层一个序，`de_order_from_population`（Bhattacharyya 统计）。
  种群 N×m=32768×1024=3.4e7 ≤ 8e7 上限；峰值内存估算 ~1.5–2 GiB（多份 float64 副本），DE 单层预计数十秒~分钟。
  已知局限：m=1024 的 MC DE 对 32768 个子信道排序有噪声；这是"最强"上的一个可改进项，非阻塞（报告 DE 序种子敏感性：T2 里用第二个种子重排，报告两序的信息集重合度，仅描述）。
- DE 输入**不含任何测试块信息**。冻结位集合 = 该层 DE 序中最不可靠的 N−k_i 个位置。

## 5. 逐层码率 k_i（禁止测试块选择）

**参数化**：全局 margin μ：`k_i(μ)=floor(N·max(0, caps_i − μ))`；`k_i<MIN_K=16`（lab 的 `min_k`）时该层整层披露（k_i=0，冻结 N 位）。
全局 margin 是 lab/R2B 同款单旋钮，不做逐层 FER 均衡（已知次优，列为 C 阶段之外的改进项，§12-D5）。

**f 与 μ 的对应（确定性，无 MC）**：`K_frozen(μ)=Σ_i (N−k_i(μ))`，`f(μ)=(K_frozen(μ)+64)/(H_total·N)`，H_total 用 R2 结果的 NB 侧 CAL32 拟合值
（G2 0.8168138204133305；G3 0.8214782076249098；直接取自 `r2_fer_shg_64` 的 `h_total_bits`，不重拟合）。对给定目标 f 二分求 μ（两 session 各自解出）。

**f 网格（冻结，4 点）**：
- **F1**：f=1.20（与 A 实验 L=32 点对齐）；
- **F2**：f=目标 NB `f_book_with_crc`：G2 1.268 / G3 1.275（按 session，两点取 R2 结果的实测值，与 NB-L16 对齐；二元不付 CRC，16 比特≈0.0006 的 f，忽略并在表里注明）；
- **F3**：**二元自身的"块 FER≈0.03 所需 f"点**，由设计集 MC 求得（下）；
- **F4**：F3 + 0.10（斜率括号点，仅描述）。

**F3 的设计集 MC（只用 CAL32 派生的合成数据）**：
1. 合成设计帧：从 §3 的 pmf 采样 M_design 个整块（a 均匀，b=(a+δ) mod 1024），`u=polar_encode(bit_i)`。设计集与 CAL32 真实符号无一一对应，完全由 CAL32 拟合模型生成，不含任何测试块信息。
2. 各层独立评估（前缀取**真值**，即"前层全对"的设计假设；这给块 FER 的近似下界模型，实际硬前缀链的误差传播由 §6 的测试块直接测出，并在结果里对比设计预测与实测）：layer-i 的码字以 `decode_batch(L)`，冻结位传真值，成功=解码 `a_hat` 全对（比较整 k 个信息位或等价地 `polar_encode(u_hat)==a_bits`）。
3. 块 FER 设计估计 `Σ_i p̃_i`，p̃_i=(e_i+0.5)/(M_design+1)（rule-of-three 型平滑，防 0 错误低估）；**M_design=256 帧/层/评估点**。
4. 选 F3：对 μ 二分（4 次评估，取使 `Σp̃_i ≤ 0.03` 的最大 μ 即最小 f；判据用平滑点估计，不用 Wilson 上界——上界在 M=256 下恒 >0.03 会把 F3 推到无意义的高 f）。F1/F2/F4 也各做 1 次设计集评估，得设计预测 FER 供事后对比（不据此改 k）。
5. 局限声明：M_design=256 下每层 FER 量级 0.003 不可分辨，`Σp̃_i` 的下限 ≈10×0.5/257≈0.019，故 F3 只能粗定位（±0.1 量级的 f）；F4 用于括号。若 PI 想要更精准的 F3，需加 M_design（耗时线性增长，§10）。

k_i 只由 μ、caps_i（CAL32 模型）决定；测试块**不参与**任何 k/序/μ/f 选择。

## 6. 译码（冻结）

- SCL：`MsdSclDecoder.decode_batch(llr, mask, frozen_values, n_log=15, list_size=L, engine="compact")`。**主 L=16**（与 NB-SCL L=16 对等）。
  L=32（与 A 实验 L=32 点对齐）为 PI 可选项（§12-D3），若选则设计集 MC 也用 L=32（设计-译码一致）。
- 逐层顺序 0→9：layer-i 的 LLR = `conditional_llr(tables, i, bob_symbols, prefix_from_bits(decoded_bits,i))`；prefix 用**已译码的硬比特**（硬前缀）；
  冻结位值 = Alice 真值 `u_full[frozen_idx]`（披露值，计入 f 分子）；LLR 转 float32 由 wrapper 处理。
- **前层出错时**：继续按真实协议行为译码后续层（前缀含错、不做 genie 纠正、不早停），最终块判定按整块比对。理由：真实系统无逐层校验，
  只有块末 tag；早停会使后续层统计有偏且省的时间很少（解码总量小，§10）。记录 `first_error_layer` 供诊断；层内成功=该层 `a_hat` 与真值全等。
- 被整层披露的层（k_i=0）：该层直接取 Alice 披露值作为 `a_hat`（不译码），计入前缀，披露 N 位。**全部披露的层照计入分子**。
- **CRC**：本合同不加 CRC（C 阶段可选项）。对等性差异：NB 用 CRC-16 做 SCL 路径选择，二元臂是纯路径度量最优路径（无 CRC 消歧）；
  CRC 在 SCL 中通常能挽回 L 内路径排序误选的一部分失败，故二元臂在译码强度上**略弱于** NB（结论句里必须写明"无 CRC"）。
  若日后加 CRC，须采用"信息位内嵌"且把 16 比特/码字计入分子，并解决"CRC 占用真实数据位"问题（R2B 的教训），另立合同。
- 块验证：块末 64-bit Toeplitz tag（复用 R2B 的 `verification.py` 路径，tag_bits=NB 侧 `chain.tag_bits`=64，对整块 a_hat 32768 符号计算，seed 由 session/block 派生，
  与 R2/R2B 同一约定，实现者逐字核对）。

## 7. f 记账

`f = (Σ_i N_frozen_i + 64) / (H_total · 32768)`（tag 64/块，无 CRC；层被整层披露也计入，`N_frozen_i=N−k_i`，整层披露为 N）。
H_total 沿用 NB 侧同 session CAL32 值。**不同方法泄漏只在分解口径一致时才比较**：结果里逐层列 `k_i`、`N_frozen_i`、`caps_i`、`Σcaps` 与 `(10−Σcaps)` 对 H_total 的差（模型自洽检查，期望 <0.03 bit）。

## 8. 判定与报告

- 成功 = 整块 32768 符号逐符号全等 (`exact`) 且 tag 通过；`undetected = tag 通过 AND NOT exact`，**单列不并入 FER**（任一出现 ⇒ 列 block id，该 f 点判定搁置，不 STOP 其它点）。
- 报告：每个 f 点、每个 session、pooled 的 exact/fail、p̂、Wilson 95% CI（z=1.96）；`stratum_official`（A1_CAL/HELDOUT/EVAL）+ `stratum_task` 分层表，
  P-1（沿用 R2：允许 64 块汇总数字，同表必须分层展示三层；`n=56` 以跨层汇总分母为准）；`stratum` 中 A1_CAL/HELDOUT 块须标注（R2）。
- **逐块配对四格表**：每个 f 点 × {二元 SCL(L=16) vs NB-SCL(L=16)（读 `r2_fer_shg_64/part_*.json`，不重跑 NB）}，按 `(session, global_block_index)` 匹配并核对 frame 区间；undetected 归"非 exact"格，另列。只报计数，不算胜率。
  **与 A 实验 L=32 的对照**：A 实验（`eff-sweep-native`，合成 N=32768、native SCL，FER≤~0.05 @ f≈1.20 (L=32)）是**合成 Tier-X 数据、无逐块对应**，故 L=32 对照只能是"二元 L=32 真实块 FER vs NB-SCL L=32 合成 FER 的描述性并列"，
  **不做四格表**；真正的 NB L=32 真实块配对需要 NB 侧另跑（超范围，§12-D3）。
- 描述性，不设"谁胜"门槛；不得写"二元不如 NB"或反之的一般性结论。

## 9. R1–R5 与合同纪律

one-shot：reruns=0（仅实现缺陷可重启一次并记独立 attempt）；f 网格规则、μ 二分规则、M_design、种子、L、判据在 Pre-EXECUTE 通过后冻结。
新增输出只在 `workspace/r2c_strong_binary_msd/`（additive，已存在 `results.json` 或任何 `part_*.json` 则拒绝运行）。R2B 的 `results/`、`part_*` 不动。
Pre-EXECUTE / Pre-RESULT 独立审查按 AGENTS.md §10.3；Pre-RESULT 须复核 undetected 隔离、逐层披露分解、per-session 与分层、tag 计入、f 分子含整层披露。

## 10. 预算与耗时估计

外推：lab 报 N=16384、L=8 约 0.04 s/帧。SCL 单帧成本 ∝ N·log N·L 量级（+分叉拷贝），N×2、L×2 ⇒ 约 ×4.4 ⇒ **≈0.18 s/码字（L=16, N=32768）**，
合理区间 0.15–0.5 s（**未实测，T0 必须先测**；本仓库 NB native SCL 在 N=32768、L=16 报 ~19 s/块作参照，那是 GF(32) 双层，不可直接套）。

| 阶段 | 计算量 | 估计（0.18 s/码字，串行） |
|---|---|---|
| DE 构造（2 session × 10 层） | 每层 32768×1024 种群 15 级 | 约 10–30 min（内存 ~2 GiB） |
| 设计集 MC（F3 二分 4 次 + F1/F2/F4 各 1 次 = 7 次评估）×10 层×256 帧×2 session | 7×10×256×2=35 840 码字 | ≈ 1.8 h |
| 测试块解码：64 块 × 4 f 点 × 10 层 | 2560 码字 | ≈ 8 min |
| 合计（L=16） | | **≈ 2.5–3 h 串行；若 0.5 s/码字则 ≈ 6 h** |
| L=32 追加（若选） | 设计集 + 测试 ≈ ×2 | +≈ 4–5 h 串行 |

机器 20 核：设计集评估各层/各 f 点相互独立，可多进程并行（实现者用 `multiprocessing` 进程池，每进程独占一个 decoder 对象；lab 文档称 decoder 无静态可变状态）→ 实际 wall ≈ 0.5–1 h。
**预算冻结**：总 wall ≤ 6 h（含并行则远低于）、RSS ≤ 6 GiB/进程（DE 峰值）、每码字 wall 监控（超 T0 计时的 5× 记 resource_abort，不静默丢弃）。
超预算：停止启动新工作，已完成 f 点保留，未完成点标 `not_started`，不调参不砍点。one-shot；需 PI 授权 + Pre-EXECUTE。

## 11. 实现任务清单（供后续 coder，均为受冻结参数约束的操作性任务）

驱动路径：`workspace/r2c_strong_binary_msd/run.py`（+ 各 `_test_*.py`），仅写该目录。

**L-1 lab 只读保护（scientifically necessary：lab 是他人/独立仓库，且其工作区脏）**
- 运行前设 `PYTHONDONTWRITEBYTECODE=1`、`NUMBA_CACHE_DIR=<stage>/numba_cache`（在 import lab 模块之前）；`sys.path` 指向 `D:\Code\qkd-reconciliation-lab\src`（WSL: `/mnt/d/...`）。
- 复制 `msd_scl.cpp` 到 `<stage>/scl_cpp/`，import 后、构造 `MsdSclDecoder` 前赋 `scl_fast.CPP_DIR=stage`、`scl_fast.CPP_SOURCE=stage/msd_scl.cpp`（`build_library` 用这两个全局，`scl_fast.py:44-68`）；在 WSL 下编译 `.so` 到 stage。
- import `qkd_recon` 包的 `__init__.py` 副作用未核对——T0 中确认；若有写盘则改为 importlib 按文件加载子模块。
- 运行前后各记录 `git -C <lab> status --porcelain` 与 lab `src/` 下文件 (path,size,mtime) 快照，二者必须相同（否则 fail）；记录 5 个被用文件的 `git diff --quiet` 状态与 sha（provenance，不是锁）。
- 不 import 已被改动的 `polar_run.py`；不在 lab 目录写任何东西。

**T0（结构/微数学）**：(a) `qkd_recon` import 与 stage 编译成功且 lab 无新增文件；(b) `fit['joint']` 是否循环结构；(c) N=32768/L=16 单码字计时+RSS；(d) 比特平面顺序、`prefix_from_bits` 的 MSB 优先与 `conditional_llr` 的 LLR 符号约定（LLR>0 ⇒ bit=0）和 numpy 手算一致。
**T1（单元）**：
 - (a) **暴力枚举对照**：N=8/16（n_log=3/4），k≤8，随机 LLR，genie 冻结值；`L ≥ 2^k` 的 `decode_batch` 结果 == 对全部 2^k 消息 ML 枚举（`Σ log(1+exp(∓llr))` 路径度量最小者），且 pm 一致；L=16 与 SCL 数值参考（`polar_core.scl_decode_batch`，同语义 numba）在小 N 上逐位一致。
 - (b) 冻结值≠0 的用例：证明传全 0 冻结值会失败（R2B 的 bug 回归）而传真值成功。
 - (c) 全披露层、k<MIN_K 层、μ 二分边界（`K_frozen(μ)` 单调）单元测试；`f(μ)` 记账公式手算核对（整层披露照计）。
 - (d) DE 根符号对齐：BSC 根上 `de_llr_populations_from_root` 与 `de_llr_populations` 的 `pe` 排序高度一致（Kendall/重合度阈值由测试者预注册）。
**T2（合成端到端 + lab 一致性）**：
 - (a) 小规模（d=16 或 64，N=1024）合成信道上全链路（建表→DE→k→SCL→tag→f 记账）自洽：预测 f 与手算一致，块成功率与设计集预测量级一致；
 - (b) 无测试块泄漏检查：驱动 AST/运行时断言 —— k/μ/序/f 计算函数不接收 test 块参数（函数签名 + 测试里传毒化的 test 数据不改变输出）；
 - (c) **与 lab polar_run 的一致性抽查**：在 lab 自带示例数据（`scripts/make_sample_data.py` 或 lab `data/` 内小数据，**只读**）上，用本驱动的逐层管线和 lab `polar_run.py` 的层循环逻辑（读其代码、独立复现，不 import 已改动的文件）在**相同表、相同 k、相同帧**上逐层 `u_hat` 比较，期望逐位一致；
 - (d) N=32768/L=16 的一次合成冒烟：低 f（如 1.6）下块成功、高 f 下失败，趋势合理。
**T3（里程碑）**：整个 fake-runner 全流程 + strict replay；两 session 的 `--dry-run` 只用合成数据。

驱动接口要点：输入 = R2 的两个 `_reproduce_session_context`；输出 = `part_<session>_<idx>.json`（每 f 点每块：`exact`、`tag_pass`、`first_error_layer`、逐层 `k_i`/`err`）+ `construction_frozen_<session>.json`（pmf 来源、CV 分数、R 比值、caps、μ 二分轨迹、设计预测 FER、各层 DE 序摘要/哈希）+ `results.json`（含 §8 全部表与 `block_accounting`）。生产运行入口须显式确认，测试入口显式注入 fake runner（AGENTS §10.1-8）。

## 12. 需要 PI 裁决的点

| # | 问题 | 选项 | 推荐 |
|---|---|---|---|
| **D1** | 差分 pmf 来源：P-M2（与 NB 同信息量的参数化拟合）vs P-HIST（原始直方图+平滑）| (a) CAL32 内 CV 择优、平局取 P-M2（本稿）；(b) 强制 P-M2；(c) 强制 P-HIST | **(a)**。理由：8192 样本下直方图方差大，但 M2 若欠拟合真实尾部会损失；CV 是纯 CAL32 的客观判据 |
| **D2** | 不变性检验失败时（R>1.25）怎么办 | (a) STOP 交 PI（本稿）；(b) 自动改用 P-HIST 并报告 | **(a)**。joint 版在 8192 样本下不可行，无可降级的"更好模型"，自动改用会掩盖模型失配 |
| **D3** | 是否做 L=32，以及是否需要 NB-SCL L=32 的真实块配对 | (a) 只做 L=16（本稿，耗时最短）；(b) 加二元 L=32（+≈4–5 h 串行），与 A 合成值描述性并列；(c) 再另立 NB L=32 真实 64 块（NB 侧新一轮执行，超出本合同） | **(a) 先做，若 F3 落点显示 L=16 已 ≤ NB 则不需 L=32；否则再议 (b)**。因 D3(c) 涉及 NB 新执行，须独立合同 |
| **D4** | 加 CRC（提升二元 SCL 强度、对等 NB 的 CRC-16）| (a) 本合同不加，列 C 阶段（本稿）；(b) 现在加，"信息位内嵌"设计 | **(a)**。CRC 需先解决"占用真实数据位/源编码语义"（R2B 教训），且在 SW 语义下 CRC 只能作路径选择而不能作码字的一部分；单独设计 |
| **D5** | 码率分配：全局 margin（本稿）vs 逐层 FER 均衡分配（更强）| (a) 全局 margin；(b) 逐层带目标 FER 的分配（需更多设计集 MC，耗时 ×3–5）| **(a)**，并在结论里写明"未做逐层均衡"。若 F3 结果显示二元 f 远高于 NB，再以 (b) 作后续以验证"是分配问题还是本质差距" |
| **D6** | 设计集 M_design=256 精度有限（F3 只能粗定位）| (a) 256（本稿）；(b) 1024（设计集耗时 ×4，≈7 h 串行/1–2 h 并行）| **(a) 起步 + 并行**；F3 粗定位配合 F4 括号足以描述曲线，需要精细 f* 再单独加 |
| **D7** | 预算：6 h wall（含并行余量）、RSS 6 GiB/进程 | 同意/调整 | 同意；T0 实测计时后可能下调 |
| **D8** | 回退：N=32768 若 lab 引擎 T0 失败，是否可回退 2×16384 | (a) 回退需 PI 知情（本稿）；(b) 授权自动回退 | **(a)**（预计不会触发）|

## 13. 未验证/实现者须先核对的假设（非阻塞，已列为 T0）

1. `fit['joint']` 的循环结构及其 `difference_pmf` 投影是否保留 M2 信息（§3.4）；
2. `import qkd_recon` 的包级副作用（§11 L-1）；
3. `polar_encode`（lab）与 NB/R2B 的位序约定不必一致——本驱动只在 lab 自身编码/解码闭环内使用它，二元 a 比特直接来自原始整数的位；
4. lab 的 `decode_batch` 对 `mask`/`frozen` 的 uint8 约定与自然序信息位（`info_mask_from_order`，DE 序需反转成"reliable-first"再取前 k——`de_order_from_population` 已返回 reliable-first）；
5. "P-1" 的准确含义按 R2 §9.2 处理（汇总数字+三层分层同表）；实现者逐字对照 `R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:423`。
