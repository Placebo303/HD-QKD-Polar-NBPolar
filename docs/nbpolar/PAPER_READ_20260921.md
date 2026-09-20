# PAPER_READ_20260921 — 三篇 PDF 原文精读与 NB-Polar 开放问题映射

- 日期：2026-09-21
- 执行者：coder-fast (taste instance, `step-5-preview`)
- 范围：**只读**三份本地 PDF，提取原文证据。未复制 PDF 入仓库、未提交、未运行 decoder、
  未打开受保护数据、未修改任何仓库文件（本文件为唯一新增文件）。
- 提取方法：本地 `pypdf` 6.19.0（`/tmp/opencode/pdfx`）逐页 `extract_text()`。
  引文为**逐字**，仅对 PDF 文本抽取产生的连字（`ﬁ`→`fi`、`ﬀ`→`ff`）与丢空格做最小归一；
  每条引文标注期刊页码（= PDF 页，三篇的 printed page 与 PDF page 均一一对应）。
- 引用格式：`[论文简称, 期刊页 p.N / PDF 页 p.N, 章节]`。

三篇：

| 简称 | 全文 | 载体 |
|---|---|---|
| **KH25** | Kanitschar & Huber, *Practical Framework for Analyzing High-Dimensional Quantum Key Distribution Setups* | Phys. Rev. Lett. **135**, 010802 (2025), 6 页 |
| **Zhou22** | H. Zhou *et al.*, *Appending Information Reconciliation for Quantum Key Distribution* (AIR) | Phys. Rev. Applied **18**, 044022 (2022), 10 页 |
| **Müller25** | R. Müller *et al.*, *Performance of Cascade and LDPC Codes for Information Reconciliation on Industrial Quantum Key Distribution Systems* | IET Quantum Communication 2025; **6**:e70003, 16 页 |

---

> **协议身份注记（2026-09-21 更正）**：本项目 HD-QKD 数据为 **entanglement-based、符合测量（coincidence-detected）**——Type-II SPDC 时频/时间-能量纠缠光子对（数据根 `TypeII_776.1nm_3s`；A/B 两硬件通道经 `_pair_nearest_unique` 配对，`src/qkd_io/ttbin_pipeline.py` 配对调用 :420、`coincidence_rate_hz` :422），**不是 prepare-and-measure**。time-bin 层 = 高维到达时间编码（`SECURITY_MODEL.md:28`），偏振层 = BBM92 型（`SECURITY_MODEL.md:29`），PIE = 每符合比特数（`SECURITY_MODEL.md:11-13`）。凡本文件旧稿中把本项目数据称作 "ToA prepare-and-measure" 的判定均为协议身份误述，已按本注记更正（详见 §3.1 与 `LITERATURE_FIT_CHECK_20260921.md` 附录 D）。

## 0. 结论速览

| 论文 | 头条判定 | 一句话理由 |
|---|---|---|
| **Müller25** | **RELEVANT**（记账口径 + 自适应披露机制） | 唯一给出"逐帧、按译码器置信度决定披露哪些位 + 每轮披露多少"的具体规则；并给出把 EV/hash/失败帧/聚类计入泄漏的完整公式。但其数字全部是**binary BSC**，不得外推为 GF(32) 证据。 |
| **Zhou22 (AIR)** | **RELEVANT**（嵌套披露的同构原型） | "gradually disclosing the bit values of the polarized channels with high error probability" 的**确切机制**在此：按极化信道错误概率降序取前缀，逐轮追加；但披露量与位置是**按 (n, QBER) 预共享、离线优化**的，不是逐块自适应。 |
| **KH25** | **RELEVANT（A 级，仅密钥率/安全外层）／ IR 轴 NO INPUT（论文显式排除）** | 纠缠型 HD-QKD 密钥率框架；其演示系统测 ToA(T_T)、报告 bits-per-coincidence，与本项目偏振层(BBM92)+time-bin 到达时间层逐字同构（公式见 §3.1）⇒ 密钥率/安全外层直接适用。但明确把 IR（H(X|Y) 项，"purely classical … we focus on the first term"）排除 ⇒ IR/disclosure/decoder 无输入，λ_EC 是其外生输入（互补）；finite-size 在配套 arXiv:2505.03874，引用须连带。 |

Müller25 四个待核数字：**全部核实为真**，但其中两个的**指代对象与仓库此前的理解有偏差**（见 §1.3）。

---

## 1. Müller 2025（IET Quantum Communication 6:e70003）

### 1.1 (a) 主张与信道/数据假设

**主张**：在"贴近工业实际"的条件下比较 Cascade 与 LDPC+blind 协议的 IR 性能，并引入把
error-verification 成本计入的效率指标。

> "In this study, we analyse, simulate, optimise and compare the performance of two prevalent
> algorithms used for information reconciliation: Cascade and LDPC codes in combination with the
> blind protocol. We focus on their applicability in practical and industrial settings, operating
> in realistic and application-close conditions. The results are further validated through
> evaluation on a live industrial QKD system."
> — 摘要, p.1

**数据来源分层（关键，回答 real vs simulated）**：

> "The simulations conducted in Sections 3.1–3.3 are based on data collected from an industrial
> QKD system. In Section 3.4, we evaluate the performance of LDPC codes and Cascade on the system
> in a live test."
> — §3, p.6

- §3.1–3.3：用工业系统采集的数据驱动，但 **Fig. 2 明确写 "The results shown are simulated,
  assuming a binary symmetric channel."**（Fig. 2 caption, p.7）。
- §3.4：**真实 live 系统**，连续约 27 h。
- 系统本身（§2.4, p.5）：

> "The QKD protocol implemented is a prepare-and-measure 2-dimensional three-state BB84 protocol,
> using the 1-decoy state method. … The three possible quantum states are prepared by Alice and
> encoded using a time-bin encoding scheme."

即：**binary、time-bin、prepare-and-measure**，10 dB 量子信道 + 40 km 经典光纤。
**字母表大小为 2**——这是本文明文的边界，任何 GF(32)/q-ary 外推都越界。

**信道假设（对我们是重要的"反面"论据）**：

> "The quantum channel is assumed to behave like a depolarising channel when no eavesdropping is
> taking place, such that the channel can be accurately represented by a substitute channel where
> x and y are correlated as a binary symmetric channel. This holds as errors are typically
> uncorrelated and symmetric."
> — §2.1, p.2

**最重要的自限性声明（Discussion，p.13–14）**——这是本项目"经验 P(y|x)"路线最有力的立项引文：

> "It is worth reiterating that our analysis assumes the channel to follow the correlations of a
> binary symmetric channel; that is, locally, in each of the EC frames, we assume symmetric
> transmission probabilities and a constant QBER, such that the behaviour is iid. How well the
> actual channels of QKD devices follow these assumptions is still not well researched (to the best
> of our knowledge, the only mention of a channel model so far is in the case of a
> high-dimensional energy-time entanglement setup [65, 66]; a mixture of a uniform and Gaussian
> distribution is proposed as a channel model). … we encourage future work that looks into the
> issue, in particular its impact on the efficiency measure itself and the implications of
> channels that are not memoryless."

### 1.2 (b) 与 IR 相关的具体数字（逐字 + 位置）

| 量 | 逐字引文 | 位置 |
|---|---|---|
| 效率定义 | "f = leakIR / nH(X\|Y)"（式 4） | §2.1, p.3 |
| FER 感知效率（引自家族，非本文原创） | "f_FER = (1 − FER)f + FER/H(p)"（式 5）；"With probability FER, the error correction fails and we consider **the whole n bits of the frame to be leaked**." | §2.1, p.3 |
| Cascade 消息数（仿真） | "Despite the relatively high number of messages required for the efficient version of Cascade (**between 400 and 700 for a frame of size 2^16**), the decline in throughput is only around 60% going from 1 ms to a 5 ms latency on a serial execution." | §3.1, p.6 |
| LDPC 码集 / 译码器 | "n1 = 1944, n2 = 4000 and n3 = 2^16 … We use the sum-product algorithm (SPA) decoder with **50 decoding iterations** and a step size **α = 1** for the blind protocol." | §3.1, p.6 |
| QBER 失配稳健性 | "for a mismatch of less than 3%, the efficiency is still below 1.1, f < 1.1. It is often advantageous to **overestimate** the QBER, as **underestimation has a higher penalty**." | §3.2, p.9 |
| 消息数对失配的敏感性 | "Overestimation by **half a percent** at a true QBER of 2% results in an increase in the number of messages sent by **more than 50%** already." | §3.2, p.9 |
| **FER < 0.003** | "We found no significant impact on the frame error rate; that is, the frame error rate of Cascade stayed **below 0.003** (evaluated on 1000 samples) for both perfect match and any other tested mismatch between q and q̂. **There were no frame errors for the blind protocol.**" | §3.2, p.10 |
| EV 新指标 | "f_eff = (1 − FER_cluster − P_Collision)f + (FER_cluster + P_Collision)/H(q) + t/(nH(q))"（式 11）；"FER_cluster = 1 − (1 − FER)^k"（式 12，k = 聚类帧数） | §3.3, p.10–11 |
| EV 参数取值 | "The best effective efficiency f_eff reached by those values can also be seen in Figure 9 with **t = 50** and **P_Collision = 10^−10**." | §3.3, p.11 |
| 失败帧计账 | "In the case of failure, that is, a frame error or a hash collision, **all n bits are assumed to be leaked to adhere to security**. Every time t bits are leaked due to the error verification." | §3.3, p.11 |
| blind 无错是设计使然 | "Per design, the blind protocol **does not allow for frame errors**, as it will always converge by revealing more and more symbols; only a syndrome error can lead to a frame error." | §3.3, p.12 |
| live 系统吞吐 | "During the experiment, the throughput of the **raw data acquisition stage**, that is, frame size over time of acquisition and sifting, was around **6.7 kbit/s**." | §3.4, p.12 |
| 帧结构 | "On average, with dependency on the acquisition rate, **8.5 EC frames constitute 1 full frame**." | §3.4, p.12 |
| live 平均效率 | "The mean efficiencies of Cascade and LDPC are **f_Cascade = 1.036** and **f_LDPC = 1.166**, respectively. The mean numbers of messages are **446 and 3.14**." | §3.4, p.12 |
| Discussion 极端消息数 | "Cascade … being penalised with a large number of messages required if the QBER is overestimated (**more than 3000 messages per frame**). LDPC codes follow a similar pattern for the number of messages but **stay below 100 messages per frame**." | §4, p.13 |
| blind 效率恶化 | "the blind protocol can rise **up to 3** for a similar range"（QBER 失配至 4%） | §4, p.12 |
| f → 原始密钥消耗 | "going from f = 1.0 to f = 1.4 results in a **3%** increase in raw key consumption due to leakage during information reconciliation at 1% QBER, but for the same efficiency jump results in **16%** more raw key consumption at a QBER of 8%." | §4, p.13 |
| 聚类最优规模 | "with **more than 40 frames clustered together** being optimal in some cases" | §5, p.14 |

**没有出现的数字**：全文**没有任何 polar 码的 IR 结果**；polar 仅在 §1 (p.2) 作为
"other methods … approaches based on polar codes [29–33], nonbinary codes [34, 35]"一句带过。
**没有 q-ary / GF(q) / alphabet > 2 的任何实验或仿真**。**没有 list decoding / SCL**。

### 1.3 (c) Müller25 四个待核数字：核实结果

| 待核数字 | 判定 | 原文逐字 | 位置 | 指代对象（关键） |
|---|---|---|---|---|
| `6.7 kbit/s` | **VERIFIED** | "the throughput of the **raw data acquisition stage**, that is, frame size over time of acquisition and sifting, was around **6.7 kbit/s**" | §3.4, p.12 | **不是 IR 吞吐**，是采集+筛选阶段的原始数据速率。仓库若当"IR/后处理吞吐"引用即错。 |
| `f=1.036 / 1.166` | **VERIFIED** | "The mean efficiencies of Cascade and LDPC are **f_Cascade = 1.036** and **f_LDPC = 1.166**" | §3.4, p.12 | live 系统上 **2^16 帧**的平均 f（Cascade 优于 blind-LDPC）。**不是**仿真值、不是大帧值、不是 q-ary。 |
| `446 vs 3.14 messages` | **VERIFIED** | "The mean numbers of messages are **446 and 3.14**" | §3.4, p.12 | 同上 live 实验，Cascade=446、LDPC(blind)=3.14，**每 EC 帧**的平均消息数。注意与 Discussion 的 ">3000 messages per frame"（QBER 高估时的仿真极端值）不矛盾——后者是失配压力测试。 |
| `FER<0.003` | **VERIFIED** | "the frame error rate of Cascade stayed **below 0.003** (evaluated on 1000 samples)" | §3.2, p.10 | **Cascade 的 FER**，QBER 失配仿真，1000 个样本。**不是** LDPC 的——blind LDPC 明确 "There were no frame errors for the blind protocol"（同页）且 "does not allow for frame errors … by design"（p.12）。 |

⇒ 四个数字**全部在原文中，指代明确**。仓库 `docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md`
附录 A.3 的 `unverified` 标记可据此作废（该文件附录 C.1 已自行核到，本次为第二次独立核实，
结论一致）。

**两个必须保留的限定**：
1. `f=1.036/1.166`、`446/3.14`、`6.7 kbit/s` 全部来自 **binary BSC + 2D BB84** 系统；
   AGENTS.md §5.5 与 `roadmap:246` 均禁止外推为 GF(32)/ToA 证据。
2. blind-LDPC 的"零 frame error"是**协议设计使然**（不断揭示直到成功），
   **不等于有限披露预算下的 exact recovery**；本仓库 `undetected` / `verify_failed`
   必须独立计数（AGENTS.md §5.5）。

### 1.4 (c 续) 记账主张（leakage 分解）——本次精读的完整清单

Müller25 的记账是三层递进，本次确认其**确切公式与原文取值**：

1. **IR 泄漏（式 4, p.3）**：`f = leakIR / (nH(X|Y))`；blind 协议下
   `leakIR = ceil(n(1 − R_i,adapted)) + k_revealed`（式 10, p.5）——
   **明确把"揭示的密钥比特数"与 syndrome 并列计入泄漏**。
2. **FER 感知（式 5, p.3，引自 [13,15]）**：失败帧按**整帧 n 比特泄漏**计
   （效率等价 `1/H(p)`）。
3. **IR+EV 合并的新指标（式 11/13, p.10–11）**：
   `nH(q)·f_eff = (1 − FER_cluster − P_Collision)·leakIR + n(FER_cluster + P_Collision) + t`
   —— 三项分别是：成功时的 syndrome/reveal 泄漏、**失败帧整帧**、**EV tag 比特 t**；
   另加 hash 碰撞概率 `P_Collision`。原文取值 `t = 50` bits、`P_Collision = 10^−10`。
4. **聚类验证（§3.3, p.11）**：把多个 EC 帧合成 clustered frame 做**一次** EV 以摊薄 tag 成本；
   `FER_cluster = 1 − (1 − FER)^k`；并评估 "allowing for a **repeat request** for failed frames"
   （p.12），"with more than 40 frames clustered together being optimal in some cases"（p.14）。
5. **失败帧的连锁效应**：live 实验中 "The spikes of the EC frames of Cascade are due to failed
   frames and consequential repetition of the algorithm and **doubling of the leaked
   information**."（§3.4, p.12）——即重试成本是**乘性**的，不是加性。

---

## 2. Zhou 2022 AIR（Phys. Rev. Applied 18, 044022）

### 2.1 (a) 主张与数据假设

**主张**：用极化码 + "逐步揭示高错误概率极化信道的比特值"同时拿到高效率与超低失败概率。

> "In this paper, we propose an appending information reconciliation (AIR) scheme based on polar
> codes, which achieves high efficiency and ultralow failure probability simultaneously, by
> **gradually disclosing the bit values of the polarized channels with high error probability**."
> — 摘要, p.1

**数据假设——全部是仿真 BSC，没有真实 sifted key**：

> "Definition 3. (K_A^s, K_B^s) = Rand(n, E_μ) is defined as randomly generating key string K_A^s
> and K_B^s with length of n and QBER of E_μ."
> — §III.D, p.5

Algorithm 1 (p.5) 的失败概率 `p = ecnt/t` 也是在这类合成数据上测的。
§IV.D 的 secure-key-rate 估计则是**借用他人 BBM92 系统参数**（Table II, p.7：
`e_pol = 2%, DCR = 200 cps, t_cc = 140 ps, t/Δ1 = 140 ps, f_AIR = 1.046, f_c = 1.200`），
属于**建模外推**，不是实测 SKR。⇒ 与 Müller25 一样：binary、BSC、QBER 参数化。

### 2.2 (b) 具体数字（逐字 + 位置）

| 量 | 逐字 | 位置 |
|---|---|---|
| 头条效率 | "the efficiency of the proposed AIR scheme is **1.046**, when the block size is **1 Gb** and the quantum bit error rate of **0.02**" | 摘要, p.1；§IV.C, p.7；结论, p.7 |
| 失败概率 | "with the **overall failure probability around 10^−8**, especially when performed with smaller block sizes" | 摘要, p.1；§IV.C, p.6 |
| 平均轮次 | "The average execution round number is **less than 2** when R_m ≤ 4. Thus, we suggest that **R_m ≤ 4**" | §IV.B, p.6 |
| 参数表 | "n 2^16–2^30；E_μ 0.01 ∼ 0.12；R_m 2 ∼ 6；ε_Rm 10^−8；**d 64**；Decoder **SCL**；**L 16**" | Table I, p.6 |
| 相对 SLA | "the efficiency, achieved by the AIR scheme with **n = 256 Kb**, is comparable to the efficiency of the previous SLA scheme, which has to be performed with **4 times larger block size**" | §IV.C, p.7 |
| SKR 提升 | "the secure key rate of QKD systems performed with the AIR scheme can be **increased by at least 30%** than the previous QKD systems with the efficiency of 1.2" | §IV.D, p.7 |
| 平均执行轮次表 | Table III：全部落在 **1.30–1.92** 区间（n=2^16…2^27, QBER 0.01–0.12） | 附录 A, p.8 |
| 效率表 | Table IV：n=2^27/QBER 0.02 → **1.056**；n=2^16/QBER 0.02 → 1.190；n=2^27/QBER 0.12 → 1.031 | 附录 A, p.8 |
| 参照系 | Cascade "efficiency of 1.03 … with around **14 interactive rounds**"；Jouguet 2014 "efficiency of **1.12** with the failure probability ε = 0.1 and the block size of **16 Mb**"；Yan 2018 SCL "decreased the ε to **10^−3** with the block size of **1 Mb**"；Tang 2021 SLA "decreased the ε to **10^−8** and the efficiency is improved to **1.091** with the IR block size of **128 Mb**" | §I, p.1–2 |

**⚠ 内部不一致（本次精读新发现，引用时须注意）**：Table I 与附录 A 的仿真/分析只到
**n = 2^27**（Table IV 最大行 2^27，f=1.056 @QBER 0.02），而摘要/结论宣称的
**1.046 @ 1 Gb（=2^30）并未在附录 A 的任何表中给出**。因此 `1.046` 应理解为按式 (15)
向更大块长的**外推/估计值**，而非表格化实测值。仓库若引 `1.046`，建议同时引 Table IV 的
`1.056 @ 2^27` 作为可核的下界锚点。

### 2.3 (d) "gradually disclosing" 的确切机制 —— 直接回答披露位置/数量问题

**是嵌套/增量披露，且与 NB-Polar 的 `D0 ⊂ D1 ⊂ …` 结构同构。** 机制分三层：

**(1) 位置（placement）：按极化信道错误概率降序取前缀。**

> "In polar codes, individual n copies of BDMCs are polarized to the q noisy channels (frozen
> bits) and n − q error-free channels (information bits). The locations of the frozen bits,
> defined as the frozen vector V, can be determined by selecting the q channels with the **high
> maximum-likelihood decoding-error probability** [29]."
> — §II.B, p.2

> "Definition 1. (P_e, W) = Descend(P_e) is defined as **sorting the error probability vector P_e
> in descending order** and recording the corresponding locations into the vector W."
> — §III.D, p.5

> "V_1 = W[0 : q_1], V_i = W[q_{i−1}, q_i], where (q_i, ε_i) ∈ B_opt and 2 ≤ i ≤ R_m"
> — Algorithm 1, 第 12 行, p.5

⇒ 第 i 轮披露的坐标集 = 全局错误概率排序中的第 `q_{i−1}+1 … q_i` 名，即**严格嵌套前缀**
（越坏的坐标越早披露）。这正对应 NB-Polar nested disclosure 的"最差坐标先披露"，
只不过排序依据是 **Tal–Vardy 设计期解析误差概率**（degrading/upgrading quantizations）：

> "Given the block size n and the QBER E_μ, the upper bound of error probability P_i^e in the ith
> polarized channel can be calculated by the degrading and upgrading quantizations [29]."
> — §III.D, p.5

**(2) 每轮披露"什么"：披露这些坐标上的真实码字比特值（不是校验位）。**

> "Step 1. Alice appends the syndrome S_i by **picking up the bit values from U** with the
> optimized frozen vector V_i, described as S_i = Index_select(U, V_i)."
> — §III.B, p.3

> "Step 3. Bob updates the integrated syndrome string S_D, by **replacing the bit values**,
> indicated by the frozen vector V_i, with the corresponding value of S_i. … S_D is initialized
> to {−1}^n."
> — §III.B, p.3

⇒ Bob 侧维护一个 `{-1}^n` 的"已知/未知"掩码，每轮把新揭示的坐标从 unknown 翻成 known，
再用 SCL 解码。这与本仓库 `nbpolar/incremental.py` 的已知坐标集合语义一致。

**(3) 每轮披露"多少"（amount）：离线优化 + 预共享，不是逐块自适应。**

> "First of all, the frozen vector library for given different n and E_μ should be **preshared**
> between Alice and Bob."
> — §III, p.3

> "Definition 4. B_opt = Opti_Effic(B, R_m, q, ε_Rm) is defined as finding out the optimal B …
> which results in the efficiency f **closest to the Shannon limit** with Eq. (15)."
> — §III.D, p.5

> "According to Eq. (5), the decoding failure probability will be decreased with the larger size
> of the frozen bits. Thus, given the maximum interactive round number R_m, the frozen vector used
> in each round can be optimized."
> — §III.D, p.5

Algorithm 1 (p.5) 的量化规则：初始 `α = ⌈nH_2(E_μ)⌉`（即 Shannon 极限比特数），
步长 `β`（Fig. 2 用 `β = 300`，块长 1 Mb、E_μ=0.02、L=16，冻结向量长度 1.60×10^5 … 1.95×10^5），
实测失败概率 `p = ecnt/t`，末轮 `q = n − max{i | Σ_j P_e[n−j] ≤ ε_Rm}`。
**每轮的 ε_i 是显式分配的一级预算**（`B_opt` 的优化变量），
本仓库目前只在 outcome 里统计失败，未做预算分配——这是可搬点。

**逐块自适应只发生在"何时停"，不在"披露多少"**：

> "Step 5. Bob returns the flag value σ to Alice. Step 6. If σ = 1, the IR procedure will end …
> If σ = 0 and i = R_m, the IR procedure is failed."
> — §III.B, p.3（σ 由 CRC(U′) ⊕ T 决定）

> "The appended length of frozen vector in each round will be **decreased with larger R_m**, which
> results in leaking less extra key information to eavesdroppers when correcting errors in the
> sifted keys."
> — §IV.A, p.6

**(4) 泄漏记账包含 CRC 标签**（这一点与 Müller25 的 `t` 项同构）：

> "f = ( d + Σ_{i=1}^{R_m} m_i ) / ( n H_2(E_μ) )"（式 15）
> — §III.C.3, p.5（d = CRC tag 长度，Table I 取 64）

---

## 3. Kanitschar & Huber 2025（PRL 135, 010802）

### 3.1 (e) 是否适用于本项目（entanglement-based 符合测量 HD-QKD）？

**判定：AXIS-SPLIT（按轴拆分）。本项目数据是 Type-II SPDC 时间-能量纠缠光子对的符合测量（见文件顶部协议身份注记），KH25 演示系统正是同类结构：**
- **密钥率/安全外层 = RELEVANT（A 级）**：演示态 |Ψ₁⟩=|DD⟩⊗(1/√d)Σ_k|kk⟩ 的 ToA(T_T) 测量 + bits-per-coincidence 与本项目偏振层(BBM92)+time-bin 到达时间层逐字同构；"works generically … requiring only partial information about the density matrix" 可由实测统计驱动（无需完整层析）；噪声模型 "only for demonstration … do not rely on any particular noise model" 可换为经验 P(y|x)。
- **IR/disclosure/decoder = NO INPUT**：本文明确把 IR（H(X|Y) 项）排除在研究范围外，对 disclosure placement/amount 与译码器选择无输入；我们的 λ_EC 是它的外生输入（互补，非竞争）。

**协议前提是纠缠源，不是 P&M**：

> "(1) state generation: photon source distributes **entangled quantum states ρ_AB** to Alice and
> Bob; (2) measurement: Alice and Bob randomly and independently decide to measure either in their
> computational bases … or in one of the test bases …"
> — Protocol, p.2

**ToA 只以"纠缠态上的测量设置"出现，不是 P&M 编码**：

> "we demonstrate our method for a typical high-dimensional temporal entanglement setup … where a
> source prepares a d-dimensional state |Ψ_1⟩ = |DD⟩ ⊗ (1/√d)Σ_{k=0}^{d−1}|kk⟩ and Alice and Bob
> either measure the **time of arrival (ToA)**, denoted as T_T, or the temporal superposition of
> (not necessarily) neighboring time bins (T_SUP), denoted as S_S."
> — Demonstration and results, p.3

**IR 被显式排除**：

> "The Devetak-Winter formula R_∞ = H(X|E) − H(X|Y) quantifies the asymptotic key rate … Since the
> **second term is purely classical and can be directly calculated from Alice's and Bob's data, we
> focus on the first term**, which can be lower bounded by the min-entropy…"
> — Key rate calculation, p.2

⇒ 本文**没有任何** IR/leakage/f/block length/N 的数字；对 NB-Polar 的 disclosure 轴无输入。

### 3.2 本文实际内容与数字（供引用）

| 项 | 逐字/数值 | 位置 |
|---|---|---|
| 方法 | "we rewrite the Devetak-Winter formula for the secure key rate as a semidefinite program (SDP) … Instead of solving the resulting SDP directly, we derive its **dual** … the main remaining task is finding the **largest eigenvalue** of a set of parametrized matrices" | 摘要 p.1；引言 p.2 |
| 平台无关性声明 | "Our method works **generically and independently of the physical platform**, requiring only partial information about the density matrix." | p.3 |
| 噪声模型（仅演示用） | "we assume an isotropic noise model, ρ = v|Ψ_1⟩⟨Ψ_1| + [(1 − v)/d^2]·1_{d^2}, although we want to emphasize that this is **only for demonstration purposes and we do not rely on any particular noise model**." | p.4 |
| 维度与可视度门限 | d = 4, 8, 16；"v^SS_min = 0.849, **v^KH_min = 0.806**, v^D_min = 0.902"（本文 / Sheridan-Scarani / Doda et al.） | Fig. 1, p.4 |
| 密钥率尺度 | Fig. 1 纵轴 "Asymptotic Key Rate (bits per coincidence event)"，最大约 4 bits/事件 | p.4 |
| subspace postselection | "the asymptotic key rates for the protocol including subspace postselection, employing l subspaces of dimension D (s.t. d = l × D), is simply given by the **weighted average** of l full space protocols of dimension D" | p.2（引 [23] Thm 1） |
| postselection 数值 | Fig. 2：d = 64，Subspace Dim = 2/4/8/16；d = 16；Full Space | p.5 |

### 3.3 finite-key / composition 框架？

**不在本文内，仅指向配套篇**：

> "In our accompanying work, (F. Kanitschar and M. Huber, Composable finite-size security of
> high-dimensional quantum key distribution protocols), available on arXiv, we show how our
> findings can be used to establish **finite-size security against coherent attacks** for general
> HD-QKD protocols both in the **fixed- and variable-length** scenario."
> — 摘要, p.1

> "Beyond asymptotic key rates, our method extends to the finite-size regime. In our companion
> paper [40], we establish finite-size security against both collective and coherent attacks in
> HD-QKD and show convergence to the asymptotic rates presented here. Moreover, we demonstrate the
> versatility of our method by establishing the security of **variable-length** HD-QKD protocols…"
> — p.5；[40] = arXiv:2505.03874

⇒ 若将来要引 finite-key/composition，**必须连带引 arXiv:2505.03874**，且仍限于纠缠型协议；
本仓库现有的替代是 Route A actual-IR finite-key（`docs/CURRENT_MAINLINE.md`）。

---

## 4. Relevance to NB-Polar open questions（映射到 route-B 轴与 SCL）

轴定义（本 checkout 现有术语）：
**(i) placement** = 披露哪些坐标；**(ii) amount** = 每轮/每块披露多少；
**(iii) L2 model** = 用什么模型给出坐标级错误先验；**SCL** = q-ary 列表译码是否必需。

### 4.1 逐篇映射表

| 发现 | 轴 | 对我们的意义 | 强度 |
|---|---|---|---|
| Zhou22：位置 = `Descend(P_e)` 前缀，最差极化信道先披露 | **(i) placement** | 与 NB-Polar nested disclosure 同构；给"按坐标级误差概率降序"提供了**已发表的先例**，但我们的 `P_e` 应来自经验 `P(y|x)`（L2），不是 Tal–Vardy 解析值 | **直接可用（结构）** |
| Zhou22：每轮量 `q_i` 由 `Opti_Effic` 离线优化、按 `(n, E_μ)` 预共享 | **(ii) amount** | 证实"逐轮预算可优化"；但同时说明 **AIR 不做逐块自适应预算**——我们的差异化正在此处 | 结构可用，量不可搬 |
| Zhou22：每轮 `ε_i` 显式分配、末轮 `ε_Rm` 冻结 | **(ii) amount** | 失败概率作为**一级可分配预算**；本仓库当前只在 outcome 统计，未分配 | **缺口，可搬** |
| Zhou22：`f` 分子含 CRC tag 长度 `d`（式 15） | 记账 | 与 Müller25 的 `t` 项同构；V57 `leak = 5*m + 64` 已是同构实现 | 已本土化 |
| Zhou22：SCL + L=16 + CRC，总失败 ~10^−8；`ε_CRC ≤ L/2^d`（式 7） | **SCL** | 唯一的 SCL 定量证据；**警告：CRC 漏检界随列表规模 L 线性增长**——我们若上 q-ary SCL，tag 长度必须按 L 重算，不能沿用 L=1 的 tag | **直接警告，须纳入 SCL gate** |
| Zhou22：`R ≤ 2`（R_m ≤ 4），`R_m > 4` 只有边际收益 | **(ii) amount** | 支持把嵌套层数压在少量层（仓库现为 layer 1/2/1.5M/2M 分层），层数不是免费的 | 设计先验 |
| Müller25：blind 协议逐帧按 BP 后验置信度选揭示位；每轮量 `v = ⌈n(0.028 − 0.02R)·α⌉` | **(i)+(ii) 同时** | **三篇中唯一具体的"逐块自适应披露位置 + 数量"规则**。译码器软信息驱动披露——正是 L2 模型在 polar 上应扮演的角色 | **最强的机制对照** |
| Müller25：`leakIR = ceil(n(1−R_i,adapted)) + k_revealed`（式 10） | 记账 | 揭示比特与 syndrome 并列计入，与我们的 `key_dependent_bits_total` 一致 | 已本土化 |
| Müller25：`f_eff`（式 11/13）含 `t`、`FER_cluster`、`P_Collision`；失败帧整帧计 | 记账 | 我们缺 **failed-frame 成本**与**额外交互轮次**两项；Müller 给了现成公式，`H(q)` 换成经验 `H(X|Y)` 即可 | **缺口，可搬（须先写 decomposition contract）** |
| Müller25：聚类验证 + 单次重传，"more than 40 frames clustered together being optimal" | 记账/协议 | 我们当前"每帧一个独立 Toeplitz tag"；聚类 + 一次重传可能更省，且是纯协议层改动，**不消耗受保护数据人口** | **低成本候选** |
| Müller25：`q̂_{i+1} = q_i`（用上一帧真实 QBER 估下一帧），且存在最优估计块长（≈50000） | **(ii) amount** 的前身 | 这是"逐块驱动"的最近先例，但**驱动量是 QBER，不是信道容量 C̄**；且 binary BSC | 部分相关 |
| Müller25：QBER 低估惩罚 > 高估；blind 在失配 4% 时 f 可 > 2.5 | 风险 | 我们若按块改预算，必须偏保守（高估误差率方向） | 设计先验 |
| Müller25：BSC/iid 假设"still not well researched"，呼吁研究非无记忆信道**对效率指标本身**的影响 | 全局 | 本项目"经验 P(y|x) + verification-aware f_eff"路线的最强立项引文 | **立项引文** |
| KH25：IR 项被显式排除；纠缠型协议；finite-size 在配套篇 | — | **NOT-APPLICABLE**：对 placement/amount/L2/SCL 四轴**均无输入**；仅可作为未来"外层净密钥框架"的待评估引用，且必须附"纠缠型 + finite-size 见 [40]"限定 | 无 |

### 4.2 对三个开放问题的直接回答

**(i) 逐块自适应披露预算，由实测信道容量 C̄ 驱动而非全局 QBER？**

- **三篇都没有做 capacity-driven 预算。** Zhou22 的预算索引是 `(n, E_μ)` 的全局 QBER，
  且离线预共享；Müller25 的驱动量是上一帧真实 QBER（`q̂_{i+1} = q_i`），不是容量。
- 最接近的两条可搬机制：
  1. Müller25 的**逐帧、译码器置信度驱动**的揭示位选择（blind 协议 §2.3）——
     证明"每帧自适应选择披露位置"在工业系统上可行且有效（live f_LDPC = 1.166）。
  2. Müller25 的**最优估计块长**结论（"≈50000 … of similar order as the frame size used for
     information reconciliation", p.14）——支持"用与 IR 相同的帧做参数估计"。
- "按块平均信道容量 C̄ 胜过高估/平均 QBER"这一具体结论**不在这三篇里**（它属于
  Scarinzi 2025，本仓库 `docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md` 附录 A.2 已核到并
  记录）。本报告不代为转称其为这三篇的结论。

**(ii) 在我们的工作点上，list decoding / SCL 是否要紧？**

- **只有 Zhou22 提供定量证据**：SCL(L=16) + CRC(64) + R_m=4 在 binary BSC 上达到
  总失败 ~10^−8、f=1.046（外推）/1.056（n=2^27 表值）。
- **两条对 SCL gate 的直接约束**：
  1. `ε_CRC ≤ L/2^d`（式 7, p.3）——**CRC/tag 的漏检界随列表规模 L 线性增长**。
     我们的 q-ary tag 预算不能按 L=1 冻结后直接用于 L∈{4,8}。
  2. AIR 的失败概率控制**主要来自 appending 轮次**（把失败从 `ε` 压到 `ε_Rm=10^−8`），
     SCL 只是基础译码器；即"低失败"不等于"SCL 的功劳"。
- Müller25 与 KH25 **完全不涉及 polar / SCL**（Müller25 仅在 §1 一句带过 polar codes）。
- 结论：**这三篇都不能把 SCL 的收益转移到 GF(32)/ToA 工作点**；SCL 解锁仍须先过
  本仓库自设的 `scl-synthetic-list-gate`（`docs/nbpolar/ROADMAP.md` Phase 7）。

**(iii) 披露的 placement / amount（哪些位置、披露多少）？**

- **placement**：Zhou22 给出明确规则——**按坐标级（极化信道）错误概率降序取嵌套前缀**，
  最差的最先披露；这是三篇中唯一的 placement 规则，且与 NB-Polar nested disclosure 同构。
- **amount**：两篇给出两类规则，且**互相补充**：
  - Zhou22（离线/全局）：`q_i` 由 `Opti_Effic` 在给定 `(n, E_μ, R_m, ε_Rm)` 下优化，
    预共享；逐块只自适应"停在哪一轮"。
  - Müller25（在线/逐帧）：`v = ⌈n·(0.028 − 0.02R)·α⌉` 比特/轮，
    位置取 BP 后验绝对值最小的那些位，直到解码成功 / 全揭示 / 泄漏预算耗尽。
- **对我们最直接的结论**：一个可检验的设计假设是——**用 L2 模型给出的坐标级误差概率排序
  决定 placement（Zhou 式），用逐块实测的困难度决定 amount（Müller 式）**。
  这两条在三篇文献中**从未被合并**，是 NB-Polar 的空白位。

### 4.3 明确"不适用于我们"的清单（防止过度引用）

1. **KH25 的全部内容**（SDP 对偶、matrix completion、subspace postselection、v_min）都是
   纠缠型 HD-QKD 的**密钥率上界**工具，与 IR/disclosure/译码无关。**不得**用于声称我们数据的
   净密钥安全性，也**不得**作为 placement/amount/L2/SCL 的论据。
2. **Müller25 的所有数字**（6.7 kbit/s、1.036/1.166、446/3.14、FER<0.003、3000/100 消息、
   t=50、10^−10）都是 **binary BSC / 2D BB84**；引用必须带此限定（AGENTS.md §5.5）。
3. **Müller25 的 `f_LDPC = 1.166` 不是"LDPC 极限"**，而是 blind 协议 + 2^16 码 + SPA50 + α=1
   的一个具体配置；原文自己说 symmetric blind 能更好但代价是 Alice 算力（§2.3, p.4）。
4. **Zhou22 的 1.046 @ 1 Gb 是外推值**，附录 A 表只到 2^27（1.056）；引用时并列给出。
5. **Zhou22 的"实验结果"全部在 `Rand(n, E_μ)` 合成 BSC 上**；§IV.D 的 SKR 是借用他人
   BBM92 参数的估计，不是实测。
6. **三篇都没有 q-ary / GF(q) / alphabet > 2 的任何 IR 结果**；Müller25 提到 nonbinary codes
   仅此一句（§1, p.2，引 [34,35] = Kasai 2010 与 Müller 2023）。
7. 证据独立性（承 `LITERATURE_FIT_CHECK_20260921.md` §6）：Müller25 ↔ Müller24 ↔ Zahidy24
   同组；Zhou22 ↔ Tang21 SLA 同组——组内不得互相"交叉印证"。

### 4.4 由本次精读触发的最低成本动作建议（供 main thread 裁定，未执行）

1. 作废 `LITERATURE_FIT_CHECK_20260921.md` 附录 A.3 的 `unverified` 标记（本次为第二次独立
   核实，四数字全真，指代已明确到节/页）。
2. `λ_total` 契约并列引用：**Martínez-Mateo 2014 (`f_FER`) → Müller25 式 (11)/(13)**，
   并补 `t`、`P_Collision`、`FER_cluster(k)` 三项；推广到 q-ary 时 `H(q)` → 经验 `H(X|Y)`。
3. SCL gate  prereg 中显式加入 **tag 长度随 L 重标定**（源自 Zhou22 式 7 的 `L/2^d`）。
4. 新增协议层候选（零数据消耗）：**聚类验证 + 允许一次重传**（Müller25 §3.3）。
5. 设计假设登记：**placement 用 L2 误差概率降序（Zhou22 式）+ amount 用逐块困难度
   （Müller25 式）** 的合并，在三篇文献中无先例，属 NB-Polar 创新位。

---

*本文件为文献精读记录，不含任何执行结论、不含受保护数据、未修改仓库既有文件。*
