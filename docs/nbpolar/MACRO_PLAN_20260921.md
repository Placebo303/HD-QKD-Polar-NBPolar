# NB-Polar Macro Plan — 2026-09-21（PI 裁定 + S2/S4 判别式 + 新数据入库后的修订路线）

- 日期：2026-09-21
- 性质：项目级宏观未来计划（macro-level future plan）。本文件只记录已裁定事项、
  已完成的零数据判别结果、新发现、入库数据与修订后的分阶段路线；不含执行授权、
  不含 FER/效率阈值判决、不含受保护数据。
- 引用源：`docs/decision-log.md:5135(b)`（被澄清取代的 caution）、
  `docs/nbpolar/RAW_DATA_INVENTORY_20260921.md` +
  `workspace/data_intake_20260921/inventory.json`（新采集入库）、
  `workspace/probes/nbpolar_s2s4_zero_data_discriminators/`（S2/S4 判别式 probe）。
- 叙述语言为中文；所有标识符 / 状态串 / 英文技术术语保持原文不动。

---

## §0 边界与本次定位（PI 2026-09-21 裁定）

以下三条逐字记录为 PI 裁定（rulings）：

- (R1) 数据是**时间-能量纠缠**；本项目的对象是 **CW 高维到达时间（ToA）编码的信息协调（IR）部分**。它与下游安全协议无关，也与是否使用偏振无关。Alice/Bob 定位等价，与是哪一路无关。
- (R2) `600k` / `1p2M` 指的是**宽谱噪声量或最高 single 计数等数据尺度参数**，不是协议身份。
- (R3) PI 明确知道**已有人在 ToA/高维上做过 IR**。因此**删除**任何形式的"无人在 ToA/高维做过 IR"表述。可辩护的卖点是：**在真实场景、真实数据下实现可用的纠错**。

Consequences：`docs/decision-log.md:5135(b)` 记录的四个 blanks 中，三个（Alice/Bob assignment、
same-vs-separate acquisition、`600k`/`1p2M`）在 IR 轴上现为 non-observables，
对 formal IR 陈述不需要 confirmation；Franson 一项降格为物理层 provenance note，
不进入 IR claims。

---

## §1 已证伪 / 已成立（S2/S4 判别式，2026-09-21）

来源 probe：`workspace/probes/nbpolar_s2s4_zero_data_discriminators/`（Tier-X、
non-claim、decoder-free、zero protected reads）。

| 假说 | 判决 | 关键数字 |
|---|---|---|
| H-A 码率/有限长 | **REFUTED** | 冻结 K2=6689 处余量 **54.8σ**，预测 FER≈0；要翻转需 V 放大 **555×**；达到 FER=0.01 所需 ΔK2 = **−1382**（即已过剩 1382 符号 = K2 的 20.7%） |
| H-B 强形式（H2 被估错） | **REFUTED** | 估计噪声仅 **±0.3%**（MM +0.29%/+0.25%；split-half −0.31%/−0.28%，seed 20260920） |
| H-B 弱形式（地板尖峰杀死 SC 路径） | **SUPPORTED** | 地板命中 **99.77%/99.75%**；地板→主体 LLR 跨度 **48.8 bits**；Laplace-α1 把地板 1e-15→~2e-3 |
| H-C（A3 ±1 前提） | **前提成立** | `delta_mass_le1 = 1.0000`（两个 session，线性与环形）；后验支撑 median=p90=p99=max=**2.0**；H2=0.8004 ≈ h2(SER)=h2(0.2468)=0.8062 |

明确记录：早期的启发式 `2^(H2/SER) ≈ 9`（"errors are 3–4 bins wide"）已被直接测量 **REFUTED**，
不得再用；它是 residue-space artifact。

---

## §2 两个新发现（零数据成本）

### 发现 A — 披露在两层之间分错，总量是对的

| session | L1 f | L2 f | 合计 f | L1 多余 | L2 缺口 |
|---|---|---|---|---|---|
| 1M | 2.005 | 1.275 | 1.297 | +112 | −126 |
| 1p5M | 2.004 | 1.275 | 1.297 | +116 | −130 |
| 2M | 1.986 | 1.276 | 1.298 | +115 | −129 |

总量与 f=1.3 Shannon 在 ~13 symbols 内相符。但 **P19 `l2_plus` 已经把 K2 从 6492 移到 7004
（+512），结果 0/3**，所以"增加 L2 披露"的方向已被证伪；总量不变的 rebalance（+130 给 L2）
严格弱于已经失败的尝试。记录为 **finding，不推荐实验**。它解释了 P20I/J/K（L1 上 +128/+256/+512
⇒ zero recovery），因为 L1 本来就已 ~2× over-disclosed。

### 发现 B — 自然标号下 A3 的 MFD 定义不适用

±1 跳跃映射到 GF(32) 域差（XOR）的汉明重量，0..31 循环全枚举：natural 分布
{1:16/32, 2:8/32, 3:4/32, 4:2/32, 5:2/32}，**均值 1.9375**；Gray 分布 {1:32/32}，
**均值 1.0000**。A3 Definition 2 原文 *"Thanks to the Gray code, the neighbor of zero has a
unit Hamming weight"* 把单位重量作为**定义前提**。⇒ 不换 Gray，A3 的 MFD 判据对我们无定义。
Gray 只改标号：代数不变、`sc.py` 对标号不感知、协议账目不变。

---

## §3 数据：新采集入库（解除"只剩约 2 block"死结）

入库规模：10 acquisitions / 20 ttbin 文件 / **333.1 MiB** 总量。
Type-II-labeled：**6 acq / 220.5 MiB**（`20260112_Type2PPLN_3s` 16.1 MiB；
`20260113_SHG_Type2PPLN_3s` 56.6 MiB；`20260113_SHG_Type2PPLN_3s_2` 57.3 MiB；
`20260121_Type2_1-5M` 29.6 MiB；`20260121_Type2_1M` 21.0 MiB；
`20260121_Type2_2M` 39.9 MiB）。Type0：**4 acq / 112.5 MiB**
（`20260120_Type0_nofilter_500K` 12.6、`1M` 22.2、`1_5M` 31.9、`2M` 45.7 MiB），
标记为 **`TYPE0_SOURCE_UNVERIFIED_NEEDS_PI_CONFIRMATION`** —— 不假设可用于冻结的 ToA pipeline。
10 个全部 `NOT_REGISTERED`、`LIKELY_NEW_SESSION`（日期 01-12/13/20/21 vs 已有 01-07/23）。
来源：`docs/nbpolar/RAW_DATA_INVENTORY_20260921.md` +
`workspace/data_intake_20260921/inventory.json`。

未决异常：(a) 每个 primary `.ttbin` 都很小（8–21 KiB），而其 `.1` 兄弟文件承载主体 ——
需确认 primary 是否仅为 header/index；(b) `Type2_1M_2026-01-21` 携带 100+ `results_*` 目录；
按 PI 指示**一律未读**（仅列出名称）。

影响：此前的绑定约束（never-decoded 余量 = 1.5M VAL 2172-2212、1.5M HOLD 2725-2766、
2M VAL 2827-2915、2M HOLD 3556-3644 = 261 frames / 66,816 pairs ≈ **2 blocks of 128 frames**）
**解除**。真实数据不再需要为方法开发而定量配给；它可以重新作为 confirmation sample。
普查补充（2026-09-21）：Type0 四个采集在继承 tier 下无 H，PI 质疑该 tier 的统计必要性；最小-CAL 描述性复算（skip-0，CAL128/256/512，preregistered）救回 3 个 cell（500K w500/w1000 CAL128 H≈0.86/0.98；1M w500 CAL256 H≈0.94），1.5M/2M 因峰宽-纯度冲突在任何尺寸下均不可辩护，最小尺寸 H 仅为描述性、不可与冻结三源比较（见决策日志同日条目）。

---

## §4 定位（按 R3 重写）

- **DELETE**：任何形式的"无人在 ToA/高维做过 IR"。A1 = Boutros & Soljanin,
  IEEE Trans. Commun. 2023, `10.1109/TCOMM.2023.3302135` 正是该工作。
- **Main claim（采用措辞）**：现有 TE-QKD 协调工作（A1/A2/A3）建立在 **Gaussian jitter +
  iid + memoryless** 的模型/仿真之上。我们在**真实 CW 时间-能量纠缠 ToA 符合数据**上给出
  q-ary（GF(32)）Polar 协调的实测结果：信道取实测经验 P(y|x)（而非 QSC/BSC），显式检验无记忆假设，
  按 verification-aware λ_total 完整核算，并报告实测 FER、交互轮次与吞吐。
- **现在即可成立的最小主张**（不必等表示问题解决，建议立刻写）：在**固定披露预算、零披露增量**下，
  仅改变经验先验的平滑方式（alt-L2 Laplace-α1），完整块恢复从 **A 0/14 提升到 B 7/14**，
  跨两个独立 session 复现（P20N 1/4、P20O 2/5、P20Q 4/5），`undetected` 全程 0 隔离，
  完整性闸门全绿。
- **KH25**：维持 A 级，但**只作为我们实测 λ_EC 的外层净密钥接收端**；IR 轴按 R1 为 no-input
  （双重依据：原文显式排除 + PI 裁定）。必须连带引用 finite-size companion arXiv:2505.03874，
  且不得单独用于声称净密钥安全。

---

## §5 修订后的路线（四阶段）

- **Stage 0 收口与定位**（零数据）：记录 R1–R3；全库删除"无人做过"；收窄 PAPER_READ；
  预注册 **FER 目标与口径**（目前全项目无 FER 阈值，而按 Müller eq(11) 失败帧泄漏整帧，
  FER 以 1/H(X|Y) 权重进 f_eff —— FER 不是免费的）。
- **Stage 1 零数据判别电池**（decoder-free / CAL-only）：S1 δ-mass ✅已完成；S2 dispersion
  ✅已完成；S3 MFD（冻结集可读，`AVAILABLE_ZERO_COST`）；S4 支撑/地板 ✅已完成；
  **S5 bounded search diagnostic ✅已完成**；
  **S6 地板抬升筛选（FLOOR_1e-6 / 1e-9 / 1e-15 × 1p5M/2M，held-out split seed 20260920）✅已完成
  （Tier-X、non-claim；见 §8）**；
  **S8 参数先验形式（M0 非参数 vs M1/M2/M3 ±1 参数 vs M4 逐列，held-out NLL + CAL 网格）✅已完成
  （Tier-X、non-claim；见 §9）**；
  **S9 先验-译码器相关性（N=32768 合成信道三臂解码 A 0/16 vs B 11/16 vs C 13/16，paired design）
  ✅已完成（Tier-X、non-claim、synthetic-only；见 §9）**；
  **S10 Type0 窗口细化（grid {200,…,500}、offset −50，28 格全 INSUFFICIENT、无 H 发射）
  ✅已完成（Tier-X、non-claim；见 §9——"1.5M/2M 任何尺寸不可辩护"更正为仅窗口可用性层面的 1.5M 例外）**；
  下一个零数据项：**中间地板 probe（FLOOR_1e-7 / 1e-8）**，映射尖峰消失与 H1 膨胀之间是否存在 knee
 （§8 动机）。闸门：只选一个胜出方向进入 Stage 2，不允许多头并进。
 **2026-09-21 修订：先验形式问题现为 Stage 1 首要假设（leading hypothesis）**—— S8/S9 共同指向
 M0 地板对稀疏 rare cell 的误定价（见 §9 F1–F2）；中间地板 probe 仍可跑，但不再是闸门唯一的候选项。
- **Stage 2 单因子执行**：**首选先验/地板/支撑线**（唯一有实证支持的：7/14 vs 0/14，现由 S9 合成证据加强为“先验形式是收敛根因”—— M2 ±1 先验在冻结 P16 构造下落点 11/16 vs M0 0/16 paired）；
  次选 MFD/Gray 标号臂；**不推荐** split-rebalance（已被 P19 l2_plus 间接证伪）与 C-P2（见 §6）。
  表示转向仅当 S3+S5+S6 共同指向。
 **2026-09-21 修订：下一个真实数据 packet 应优先检验 M2 先验**（冻结 K1=319/K2=6492、
 已接受 block 先行，见 §9 F6）—— 在真实数据验证确认 S9 方向之前，不得把 S9 读作 FER/效率证据。
  Caveat（§8 方法学警告）：当前尖峰统计**不能**区分任何 LLR 跨度 < 20 bits 的规则
  （阈值 `median + 20 bits` 在跨度 < 20 时恒为零）—— 未来任何地板 probe 必须以 held-out NLL
  为主要读数，或采用跨度无关的尖峰定义。
- **Stage 3 真实数据可行性与测量集**：预注册披露上限 → 逐 block 输出
  exact/undetected/verify_failed/decode_failed 分列（§5.5 `undetected` 绝不并入）、FER、
  交互轮次、吞吐、RSS、逐 block λ 分解（B1→Müller eq 11/13，H(q)→经验 H(X|Y) 的替换
  **必须预注册，禁止事后回填**）+ 记忆/iid 检验。
- **Stage 4 论文**。

---

## §6 授权决定

- **C-P2 B4：NOT AUTHORIZED**（route 预算 2/6 已用，剩 4/6）。依据三条：(1) dispersion 显示冻结
  K2 有 54.8σ 余量、预测 FER≈0 ⇒ L2 量非约束；(2) C-P2 冻结文本为 N=16384、K1=167 固定、
  变 K2'，测的正是那个过剩旋钮；(3) 新发现缺陷是两层分配比，C-P2 不测。NOT a rejection of
  axis (ii) forever — re-freeze required if Stage 1 later shows the amount axis is binding.
  `next_gate` remains `C_P2_B4_IMPLEMENTATION_PENDING_USER` but with this rationale recorded.
- **A3 Corollary 1 代入**：做，但**降格**为带三条 caveat 的设计视角记录（渐近 diversity 斜率非 FER；
  Corollary 3 的 `R_c ≤ 1 − log2q/m` 由充分条件 `L < d_Hmin` 推出，非 iff；
  两层 5+5 bit 架构下原文明确称部分重量枚举"cannot lead to a general condition"）。
  **不占 Tier-X 4/6，不占 route-B 2/6**（纯算术，对已冻结常数运算，不构成 probe）。
  **不得作为表示转向触发条件。**
- 算术存档：L = 16384（按层 32768）；t ≤ 3375–3506；硬判决界 `R_c ≤ 1 − 2·5/10 = 0`；
  软判决界 `R_c ≤ 1 − 5/10 = 0.5`；实际 R = 0.784–0.794，两界皆在界外。逆问题：软判决界在
  R=0.79 下允许的最大 q = **4**；q=32 所需 m ≥ 24（d = 2^24 bin）**不可达**。

---

## §7 剩余风险

- Stage 1 可能全部 inconclusive ⇒ 不应继续烧数据（因新数据入库，此风险已大幅下降）。
- λ 代码路径残留：`per_session_calibration.py` 保留 λ 程序、`empirical_diagnostic.py` 仍引用
  `LAMBDA_STAR`；disposition 为 raw+floor。
- 表示转向的历史陷阱：V67/V68/V69/V70 每次都以 `successor: new_representation` 收尾且都没产出
  解码器证据。**Stage 1 闸门必须由 S5/S6 这类能看到解码结果的判据把住。**
- Type0 源未验证。
- 全项目无 FER 阈值。

---

---

## §8 S6 地板抬升筛选（2026-09-21）与一个方法学警告

来源 probe：`workspace/probes/nbpolar_s6_floor_lift_prior/`（Tier-X、non-claim、
decoder-free、held-out split seed 20260920；`results.json` 在盘、gitignored）。
各 variant × session 结果：

| variant × session | spikes | H1 | H2 | H_total | held-out NLL | LLR span floor→max |
|---|---|---|---|---|---|---|
| FLOOR_1e-6 × 1p5M | 0 | 0.04138 | 0.80515 | 0.84654 | **0.83970** | 19.93 |
| FLOOR_1e-6 × 2M | 0 | 0.04184 | 0.81168 | 0.85352 | **0.84881** | 19.92 |
| FLOOR_1e-9 × 1p5M | 181 | 0.02523 | 0.80037 | 0.82560 | 0.84673 | （incumbent-like） |
| FLOOR_1e-9 × 2M | 294 | 0.02569 | 0.80691 | 0.83259 | 0.85782 | — |
| **FLOOR_1e-15（incumbent）× 1p5M** | 181 | 0.02520 | 0.80037 | 0.82557 | 0.86374 | 49.83 |
| **FLOOR_1e-15 × 2M** | 294 | 0.02566 | 0.80690 | 0.83256 | 0.87878 | 49.81 |

正确性闸门：S6 运行把 incumbent 行相对 S5 **逐比特复现**（H1 差 0.0 / 6.9e-18，
H2 差 4.4e-16 / 1.1e-16，NLL 精确相等，尖峰数 181 / 294 精确相等，
split 尺寸 212904 / 212056 与 280309 / 279563 精确相等）⇒ pipeline 可信。

> **方法学警告（本节最重要的的一行）：`FLOOR_1e-6` 的"零尖峰"是阈值算术的必然结果，
> 不是拟合质量的改善。**尖峰判据是 `surprisal > median + 20 bits`；而 FLOOR_1e-6 把 LLR
> 跨度压缩到 **19.93 / 19.92 bits < 20**，因此**没有任何符号可能超过阈值** —— 零尖峰是被强制的，
> 不是挣来的。同样的论证适用于 LAPLACE_α1（跨度 4.6–9.0 bits，同样 < 20）。
> **⇒ 对任何 LLR 跨度 < 20 bits 的规则，spike 计数不携带信息；只有 held-out NLL 是独立证据。**
> FLOOR_1e-6 在两个 session 上 NLL 均为最优（0.8397 / 0.8488），这才是它真正有用的证据。

Tradeoff（显式记录，不并成一个"优胜者"）：

- FLOOR_1e-6：零尖峰（强制）+ NLL 最优，代价 H1 0.0252→0.0414 / 0.0257→0.0418
 （**+64% / +63%**），H_total +0.0210 bits/symbol（两个 session 相同），
 披露 +179 / +178 符号 = **+895 / +890 bits**。
- 对比 LAPLACE_α1 的 H1 破坏（0.025 → 4.70，**+185×**）：地板抬升以**两个数量级更小的 H1
 代价**买到同样的零尖峰结果。
- FLOOR_1e-9：H1 保持不动，但**100% 尖峰保留**（181 / 294）。
- **测试网格上不存在同时满足（零尖峰 AND H1 不变）的点。**
- 注意：由于 K_total 都由同一 f=1.3 预算字面式推导，两个 variant 的 f 都 ≈1.297–1.298；
 1e-6 的真实代价是**同样的 f 买到更少的净密钥**（H_total 上升）。

披露表（描述性，H-proportional split —— **不是**已接受的 `select_empirical_split` 语义）：

| variant × session | K_total | ΔK vs frozen | Δbits |
|---|---|---|---|
| 1e-6 × 1p5M | 7199 | +179 | +895 |
| 1e-6 × 2M | 7258 | +178 | +890 |
| 1e-9 / 1e-15 × 1p5M | 7021 / 7020 | +1 / 0 | +5 / 0 |
| 1e-9 / 1e-15 × 2M | 7080 / 7080 | 0 / 0 | 0 / 0 |

大声记录 caveat：H-proportional split 给出 214/6806 与 218/6862，而 session 冻结值为
331/6689 与 334/6746 —— **L1/L2 切分正是该描述性规则与已接受语义分歧最显著之处**，
因此这些 K 值不得用于任何 construction 决策。

下一步 Tier-X（推荐，non-claim）：1e-9（尖峰完整保留）与 1e-6（零尖峰、H1 +64%）之间空隙很大
⇒ **中间地板 probe（1e-7、1e-8）**，映射尖峰消失先于 H1 膨胀的 knee 是否存在。
**仅凭此证据，不得把 FLOOR_1e-6 提升为任何真实数据 construction 决策。**

> 方法学裁定（PI 2026-09-21，普查 R1）：配对前必须用本采集自身数据的 correlation
> 做自动对齐（`peak_to_bg >= 10` 接受），永不继承 01-21 V25 的 `-50/+50/+50`
> 延时与 sigma 门限；此举使配对不受 ps-vs-0.1ps 单位歧义影响（详见 decision-log 同日条目）。

---

*本文件为宏观计划记录，不含执行授权、不含阈值判决、不含受保护数据。C-P2 与 Stage 2/3 的任何
执行仍需独立的 freeze + 显式用户授权。*
- 窄规则（N）H 普查：60 格中 32 个 FULL H（(N)-200：SHG 0.8173/0.8168，01-21 为 0.8215/0.7997/0.8313，对照冻结参考仅列数字不断言）；干净＋FULL＋无偏可用格存在（01-21 w≤2000十二格 ＋ SHG w=500/1000四格；SHG w=200 高斯覆盖 0.92 略偏）。

---

## §9 先验形式：本轮收敛结论与建议方向（2026-09-21，S8/S9/S10，Tier-X 描述性）

本轮所有 probe 指向同一个根因：**非参数经验先验（`counts_ab` raw-count MLE + 1e-15 floor，
即 incumbent P7 规则）对稀疏 rare cell 误定价**—— 不是码率、不是披露量、不是构造。
完整记录见 `docs/decision-log.md` 同日"Prior form is the converging root cause"条目；证据在盘、
gitignored（`workspace/probes/nbpolar_s8_parametric_prior/results.json`、
`workspace/probes/nbpolar_s9_decoder_prior_relevance/results.json`、
`workspace/probes/nbpolar_s10_window_refine/results.json`）。

- **F1 — S9：±1 参数先验在表格先验全败处解码（合成、描述性）**：N=32768、GF32×GF32 F03、
  冻结 P16 构造、匹配 K1=319/K2=6492、16 个共享 EVAL block、64-bit Toeplitz tag、模型采样合成、
  零真实数据。A（M0 表格 + 冻结 P16）**0/16**，CI (0.000, 0.194)；B（M2 ±1 参数 + 冻结 P16）
  **11/16**，CI (0.444, 0.858)；C（M2 ±1 参数 + M2 重推导构造）13/16，CI (0.570, 0.934)。
  Paired：A-vs-B 为 B-only 11 / A-only 0 / 皆非 5；B-vs-C 为 C-only 2 / B-only 0（CI 重叠 ⇒
  为安全无需重推导构造）。**机制**：TRAIN 每列 ~256 样本；真值 −1 率 0.00136 ⇒ ~70% 的 M0 列
  零 −1 事件，1e-15 floor 经列归一后定价 ~4e-18，而 M2  pooled 拟合定价 0.00147；
  每 EVAL block ~45 个真 −1 delta，每个令 M0 付出约 48 bits 伪罚。预算：N=32768 下每次 SC
  调用约 6 s；三臂运行峰值约 0.96 GB。**Caveat（逐字）**：synthetic only；16 blocks（wide CIs）；
  ground truth was pro-M2 by design（exact ±1 support）；arm A 0/16 特指稀疏 rare cell 上的
  raw-MLE-plus-floor。Descriptive only—— no FER/efficiency/qualification claim。
- **F2 — S8：±1 先验在拟合、数据量、账目三项同时更优**：held-out NLL（split-A 拟合 /
  split-B 评分，seed 20260920）：M0 0.8637/0.8788（2436/2635 参数）；
  **M1 pooled ±1（2 参数）0.8272/0.8345**；M2 按 session ±1 同值；M3 +边界上下文同值；
  M4 逐 Bob 列 ±1（2048 参数）与 M0 逐比特相等。参数先验胜 incumbent 0.037–0.044 bits/symbol
  （消灭死格 floor 尖峰）。1% H 精度最小 CAL：incumbent 1024 frames（0.1% 在网格上永不到）；
  **M1 约 2–4 frames；M2 约 2–8 frames**。先验代价 vs 每 block 净密钥（4 bits/symbol）：
  incumbent 牺牲 262144 symbols ≈ 8× block / 2× 四 block packet；
  **M2 牺牲约 2,000–8,000 bits ≈ 0.015–0.06× block；reveal 约 20 bits ≈ 1.5e-4× block**。
  M4 与 M0 同等昂贵—— 跳过。M1 ≈ M2（gap 约 1e-5 bits 量级，精确值 −4.55e-05 / −1.24e-06）；
  若 delay −50 源进入 CAL 需重验。
- **F3 — 先验估计账目缺口确认，Release 呈现可复制模式**：`docs/SECURITY_MODEL.md` 对
  CAL/prior/calibration 零提及（大小写敏感 grep 零命中）；采用的 λ_total 契约（Müller eq 11/13）
  无先验估计项。冻结 Release 基线无此问题，因其无此对象：译码器只收**参数化 per-bit-plane BSC**
  （1 标量，LLR `±log((1−p)/p)`）；唯一 q×q 条件表是 MAP-sanity 诊断（译码器永不加载）；
  信道参数在密钥数据上 in-sample 估计（无 CAL 对象）；主 claim 限域
  `public_ec_only_not_secure` + `composable_security_claim_flag=0` + 穷尽 fail-closed 公开消息清单。
  **Release 的单参数每平面信道即参数先验模式。**可复制模式：(1) 译码器只收参数化信道；
  (2) in-sample 估计（Release，须标注复用偏差并限域）或保留小 CAL 并计费——
  NB-Polar 取后者（约 8–32 frames：代价可忽略且避开复用偏差）；(3) 穷尽公开消息清单 + fail-closed；
  (4) 限域声明。
- **F4 — S10：Type0 窗口细化（更正一处过 claim）**：grid {200,…,500}、offset −50。
  **500K 自 w=250 起可用；1M 自 w=300 起可用；1.5M 在 w=350–400 有可用窄缝**
 （coverage 0.953–0.977，accidental 0.041–0.047）；**2M 无可用窗口**
 （w=450 coverage 0.946 而 accidental 已 0.075；w=500 coverage 0.968 但 accidental 0.082）。
  **此前"1.5M/2M 任何尺寸不可救"对 1.5M 被推翻**—— 其所需窗口（1.96σ = 345）恰落入旧网格空隙。
  但 28 格全 tier-INSUFFICIENT（最优 558 frames vs 1342 REDUCED 门限），故无 H 发射——
  有效结果，非失败。注意 S10 "usable"（coverage+accidental）与 minimal-sizing "defensible"
  （另需 SE ≤ 1.5%）是不同门限，无矛盾。
- **F5 — 三个 `20260121_Type2_*` 采集即 V25 三源（确认）**：
  `docs/hd-qkd-ir-roadmap-review-20260823.md:21` "V25 | 三源 `type2_2026-01-21` 经验信道"；
  时间戳 184040 / 183806 / 183657 与三个目录精确匹配。其普查 H ≈ 0.80 与冻结参考重合不是独立佐证——
  是同一数据经另一估计路径。**真正新增可用数据是 SHG 对（H 0.817，coverage 0.92）加上 ±1 先验解锁的部分。**
- **F6 — 战略后果**：若采用 ±1 先验，CAL 需求自 1024 frames 降至约 8–32 frames。
  这一改动同时溶解：Type0 tier 不足（S10）、先验估计算目缺口（F3）、以及驱动整个 10 采集入库的
  数据稀缺约束。记为建议方向，显式标注 **pending real-data validation**（F1 仅合成）。

**对 §5 的后果**：先验形式问题现为 Stage 1 首要假设；下一个真实数据 packet 应优先检验 M2 先验
（冻结 K1=319/K2=6492、已接受 block 先行），S9 在真实数据验证前不得读作 FER/效率证据。
