# NB-Polar 未来方向规划报告 — 2026-09-24

- 性质：**规划输入（planning proposal）**，供 PI 决策。不改任何状态串、不授权任何执行、不含实测 FER 数字主张。
- 依据：项目历史（`STATE.md`、`MACRO_PLAN_20260921.md`、`REAL_DATA_CORRECTION_ROADMAP_20260922.md`、
  `R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`、2026-09-23 探索套件报告、`AGENT_PROJECT_MEMORY.md`、
  兄弟仓库 `HD-QKD_Polar_Release` 的结果文档）+ 本次文献检索（§4、§10）。
- §2 的全部数字都用项目**已冻结**的数值重新算出，公式写在正文里，可以逐条复核；
  标 **[粗算]** 的是尚未跑过代码的推算，§6 Phase A 的第一件事就是核实它们。
- **授权边界（本文件通篇适用）**：凡涉及真实数据的动作（A1b、A4、A5、Phase C 采集、Phase D 全部，
  及 §7 任何真实数据兜底动作（K4））
  一律 **NOT AUTHORIZED**，各自需要逐字授权的 packet + Pre-EXECUTE/Pre-RESULT（AGENTS §3、§10.3）。
  合成探针按现行 AGENTS §10.4 在已授权 packet 内以 Tier-X 运行，输出根 `workspace/probes/<id>/`；
  记分板的任何行**不得**写入 `results/` 或 `comparison_bench/outputs_comparison/`。
- **决策边界**：文中的目标值（f 区间、M 级阈值）、解锁 `scl.py`、改块长 N、样本量、DEV/CONFIRM 切分、
  f_eff 中经验 H(X|Y) 的替换口径，都只是**提议**。它们必须经 OpenSpec / PI / R2-T4 裁定，本文件不自定。
- **计数引用纪律**：遵守 R2 草稿 C1 与 R-2 guard，本文件不引用 G2/G3 的真实成功/失败计数，只定性引用其裁决记录。

---

## §0 一页结论

1. **终点本身清楚，但没有一个可计算的"分数"。** 现在的进度是用状态阶梯
   （`CANDIDATE → VALIDATED_AT_FROZEN_CONTRACT → …`）和一道道门的通过情况来衡量的，
   而不是看性能数字。于是每一步都"合规"，却说不清离终点还有多远。
   **建议定一个北极星指标**：在同一份数据、同一配对规则下，**每个符合事件的净协调比特数
   `PIE_rec`**（沿用 Release 的 public-EC-only 口径，把失败块按 Müller eq(11) 整块计泄漏）
   和**解码吞吐**。之后所有实验都要在这张记分板上落一个点（§3）。
2. **最重要的新发现 [粗算，可立即核实]：当前工作点只和一个平凡方案打平。**
   把冻结的 G1R2 CAL32 三元组做链式分解：H(X|Y)=0.8168 bits/符号里，**0.8013 在标号的
   最低位（LSB）**，只有 **0.0156** 属于 ±1 方向。所以"直接公开全部 LSB（1 bit/符号），
   再用一个小码纠正方向"大约只泄漏 **1.033 bits/符号（f≈1.265）**，而且 FER **[粗算]** 预计接近 0；
   当前 NB-Polar 的冻结披露为 **1.041 bits/符号（f≈1.275）**，而 G2/G3 裁决记录显示在该工作点仍有失败块。
   ⇒ **f 约在 1.24–1.25 以上（取决于方向级开销）的区间，平凡方案就能达到**；
   真正体现纠错能力的是 **f < 1.2**（泄漏低于 1 bit/符号）。
   建议经 R2-T4 / PI 重新讨论"f≤1.3"这一目标区间。
3. **"数据耗尽"是人为造成的。** 每个 3 s 的 SHG 采集约产生 33 个 N=32768 块
   （ledger 4219 帧 ÷ 128），**采 1 分钟约 660 块**。卡住进度的是采集时长和流程，不是物理。
4. **吞吐差了约 224 倍。** 采集约产生 36 万符号/s，解码约 1.61 千符号/s（855.1 s / 42 次 ≈ 20.4 s/块）。
   这决定了"能不能用"，但目前没有任何一项工作针对它。
5. **流程开销已经挤占了算法工作。** 2026-09-15 以来 98 个提交里 61 个是 `docs`；
   核心的 `sc.py`（12.8 KB）和 `scl.py`（12.5 KB，**已实现但锁着**）旁边，
   堆了约 3.5 MB 的一次性 probe 脚本。这违背了 `AGENTS.md` §1.1 第一性原则的原文。
6. **建议路线（12 周，§6）**：A 先建记分板和强基线（2 周；零数据项先做，真实数据项待授权）→ B 在合成的实测信道上
   把 NB-Polar 推进到 f<1.2（CA-SCL、按比特构造、增量披露；4 周）→ C 与实验室并行
   采集几分钟级数据 → D 在真实数据上用数百块测 FER–f 曲线，并在同一数据上与二元基线对比 → E 写论文。
   每个阶段都有**量化的止损条件**（§7）。

---

## §1 诊断：为什么会有"无头苍蝇"的感觉

| 症状 | 证据 | 后果 |
|---|---|---|
| 终点不可计算 | `STATE.md` §4.1 用 5 级状态阶梯衡量进度；R2 合同有 C1–C14、15 行 ledger、T3/T4/T5/T6 门序，至今**一个性能数字都还没产出** | 每一步都合规，但无法判断是否接近终点 |
| 目标 f≤1.3 选错了区间 | §2.1–2.2：f 约 1.24–1.25 ⇔ 泄漏约 1 bit/符号 ⇔ 直接公开 LSB | 在这个区间优化，拿不到"纠错比平凡方案好"的证据 |
| 样本极小 | 真实数据上 M2 一共只解了 28 块（G2、G3 各 14 块，结果见各自裁决记录）；每道门的决策都建立在 n=14 上 | n=14 时 Wilson 区间半宽可达约 ±0.25，只能分辨很大的效应 |
| 数据"耗尽" | 冻结 ladder 剩 101 帧；但 3 s 采集就有 33 块 | 被当成了硬约束，实际上是采集时长问题 |
| 比较对象缺位 | Release 二元 Polar 已在真实数据上跑了 206,402 个验证块，PIE_main 最高约 7（public-EC-only，`POLAR_RECONCILED_RESULT_V3.md`）；NB-Polar 没有在同一数据上产出 PIE | "NB-Polar 更好"无从谈起 |
| 原生高维优势可能是标号造成的 | 2026-09-23 Step-1/1B 的二元臂用的是 **reflected Gray**；自然标号 + LSB 优先 MSD 被列为"未做的扩展" | §2.2：对 ±1 信道，自然标号很可能是二元方案的最强形态 |
| 流程压过算法 | 98 个提交里 61 个 docs；三轮 freeze review FAIL 才换来 G2 的一次运行 | 一个 14 块的实验要花数天治理成本 |

**值得保留的真实成果**（不要因为改路线而丢掉）：
GF(32) 代数与 SC 已由独立 oracle 验证（17/17、33/33）；Toeplitz tag、披露计数、`undetected` 隔离机制；
**M0 地板误定价机制的发现与 M2 修复**——M2 在两个独立 session 的预注册门上都通过了
（`NBPOLAR_M2_PRIOR_G2_SUCCESS`、`NBPOLAR_M2_PRIOR_G3_SUCCESS`，计数见裁决记录），这是项目迄今最硬的正面结果；
S11 配对污染诊断（窗口/MOD 选择对信道形状的影响）。

---

## §2 三个用冻结数字就能算出的事实

### 2.1 真实信道几乎是"一个 BSC + 一个很小的方向问题"[粗算]

输入：G1R2 CAL32 冻结三元组 q0=0.75623、q+1=0.24194、q−1=0.00183、q_rest=0（SHG `_1`，w=200/CIRCULAR）。

对 d=1024 的自然标号，Δ=±1 必然翻转 LSB，Δ=0 不翻转，因此：

```text
P(LSB 不同) = q+1 + q−1 = 0.2438          →  H_LSB = h2(0.2438) = 0.8013
已知 LSB 后，仅剩"奇数误差的方向"：
P(−1 | 奇) = 0.00751                        →  H_dir = 0.2438 · h2(0.00751) = 0.0156
H_LSB + H_dir = 0.8168  ==  冻结 H_M2 = 0.8168138   （链式法则闭合）
```

LSB 与方向确定之后，其余 8 位（包括向 `high` 的进位）**全部确定**，
因此 L1/L2 的 5+5 分层以及"L1 超额披露约 2×"（MACRO_PLAN 发现 A）在这种表示下自然消失。

### 2.2 平凡基线 B0："公开 LSB + 小码纠正方向"[粗算]

| 方案 | 泄漏 bits/符号（含 64-bit tag） | f = 泄漏 / 0.8168 | FER |
|---|---|---|---|
| 当前 NB-Polar（K1+K2=6811 个 GF(32) 符号） | 5·6811/32768 + 64/32768 = **1.0412** | **1.275** | 该工作点仍有失败块（定性，见 G2/G3 裁决；无 FER 主张） |
| B0，第二级 f2=2 | 1 + 2·0.0156 + 0.002 = **1.0331** | **1.265** | **[粗算]** 预计≈0（每块约 60 个 −1 事件，第二级码率约 0.97，Bob 知道哪些位置可疑） |
| B0，第二级 f2=3（保守） | 1.0486 | 1.284 | 更低 |

**解读**：
- **平凡地板在 f 约 1.24–1.25**：纯公开 LSB 对应 1/0.8168 = 1.224，
  再加方向级（f2=1 时 +0.0156）和 tag（+0.002），得 1.246；f2=2 时为 1.265。
  在这个地板之上优化纠错码不产生科学价值。
- **真正的编码区间是 f<1.2**：此时总泄漏低于 1 bit/符号。相对 LSB 平面公开（1 bit）的**节省量**
  （B0 地板 1.0175 + 另计）
  Δ = 1 − 泄漏 = 0.020 / 0.061 / 0.101 bits/符号（f = 1.20 / 1.15 / 1.10）。
  也就是说，LSB 平面要在 BSC(0.244)（H=0.801）上做 Slepian–Wolf 压缩，只比"全部公开"少 0.02–0.10 bits/符号。
  这与 CV-QKD 低 SNR 协调在结构上的类比（§4-C）仅作启发，是否成立由 A2 的合成曲线判定。
- 这也给"原生 q 元是否优于二元"提供了最干净的对照：**自然标号、LSB 优先的 MSD 二元方案**
  （第一级 BSC(0.244)，第二级几乎无熵）很可能是二元一侧的最强形态；
  9-23 的 Gray 二元臂不是它。

> 口径提醒：以上只适用于 w=200/CIRCULAR 截断后的总体（caveat (a)）。更宽的窗口会出现
> |Δ|≥2 尾部（G1 w=500 时尾部 0.50%），LSB 分解不再闭合——正因如此，
> §5 H3"窗口宽度 vs 码强度"才是一个真实存在的科学问题。

### 2.3 数据与吞吐

```text
每 3 s SHG 采集：ledger 4219 帧 × 256 对 = 1,080,064 对  → 33 块（N=32768）
每分钟采集 ≈ 660 块；采集速率 ≈ 360,000 符号/s
当前解码 ≈ 20.4 s/块（G2：855.1 s / 42 次解码） ≈ 1,610 符号/s  → 差约 224×
```

---

## §3 北极星：一张记分板

**所有**实验（合成或真实）最后都只在这张表上落一行，不再用状态串衡量进度：

| 列 | 定义 | 备注 |
|---|---|---|
| data / pairing | 采集 id、W_P、MOD、skip | 不同配对的行**不做优劣比较**，只各自画曲线 |
| method | B0 / 二元自然 MSD / 二元 Gray（Release）/ NB-Polar SC / NB-Polar CA-SCL(L) / … | |
| N, n_blocks | 块长与块数 | 块数不在此独立选取：按 R2 草稿 C9 / D2（difference → w → n）导出；在状态到达 `FER_MEASURED_AT_CONTRACT` 之前，任何 FER 数字不进摘要（C1） |
| output root | 合成行 → `workspace/probes/<id>/`；真实数据行 → 各自授权 packet 冻结的输出根 | 永不写入 `results/`、`comparison_bench/outputs_comparison/` |
| leak bits/sym, f | 成功块平均泄漏（含 tag、CAL 牺牲摊销） | |
| FER + Wilson 95% | `(verify_failed+decode_failed)/有效块`；`undetected` 单列 | 沿用 R2 草稿 C2/C4/C5 语义 |
| f_eff | Müller eq(11)，H(q) 换成经验 H(X\|Y)（口径为提议，见 C6 预注册） | |
| **PIE_rec** | (H_raw·kept − 总泄漏 − 失败块整块) / **总**符合事件 | **分母用总符合数**，这样窄窗丢掉的符合会被计入代价 |
| throughput | 符号/s（单核）、RSS | |

**三级目标（建议值；阈值须经 R2-T4 / OpenSpec 由 PI 定稿，本文件不自定）：**

| 级别 | 条件（同一真实数据、≥2 个 session、块数按 C9 导出） | 可支撑的主张 |
|---|---|---|
| **M-usable** | FER 的 Wilson 上界 ≤ 0.02 **且** f_eff ≤ 1.20 **且** 严格优于 B0 | "真实 ToA 数据上可用的 q 元 Polar 协调"（短文/会议） |
| **M-competitive** | f_eff ≤ 1.12，FER 上界 ≤ 0.01；在同一数据上 PIE_rec ≥ 二元自然 MSD 与 Release | 期刊主结果 |
| **M-strong** | 在配对设计下原生 vs 二元的差异显著；给出窗口宽度–码强度的权衡曲线；吞吐 ≥ 10⁵ 符号/s | 强结论 + 工程可用 |

---

## §4 文献定位：别人做到了哪里，我们的空位在哪

**A. 时间–能量 / ToA 协调（直接竞品）**
- Zhong 等 2015 NJP（`10.1088/1367-2630/17/2/022002`）：Franson 纠缠 HD-QKD 实验，
  "error correction coding that can tolerate high error rates" 是实现 8.7 bits/符合 的四要素之一——
  **真实实验里的协调早已存在**，所以我们的卖点只能是方法 + 口径 + 真实信道刻画。
  [Photon-efficient QKD using time–energy entanglement](https://consensus.app/papers/details/f2d01a7bc17d51d98ed91cc4154d8295/?utm_source=claude_desktop)
- Mitra 等 2023/2024（QIP）：Zhou 等的 MLC 把符号拆成比特层，用二元 LDPC；
  他们提出 NB-MLC(a) + JRDO + IDC，**比既有工作的密钥率提升 40–60%**，且指出二元拆层有误差传播。
  **这是最直接的竞争方法**（NB-LDPC、多级、利用信道信息），但仍基于模型信道。
  [Efficient IR using informed design of NB-LDPC](https://consensus.app/papers/details/c4fa9f2561075c648d877d11aeb3889b/?utm_source=claude_desktop) ·
  [NB-LDPC code design for ET-QKD](https://consensus.app/papers/details/0a5096a4d88559d7b3046fb428627d21/?utm_source=claude_desktop)
- Boutros & Soljanin 2023 TCOM（A1）、Birnie 等 2022 TCOM（A2：死时间让信道**有记忆**，暗计数对 PPM 尤其有害）、
  Yang 等 2019 Asilomar（ET 信道统计 + balanced modulation）。
  [Time-Entanglement QKD: SKR and IR Coding](https://consensus.app/papers/details/2fd317e2e4e951e6a846027fc5ad2777/?utm_source=claude_desktop) ·
  [Information rates with non-ideal detectors](https://consensus.app/papers/details/1e384b0531cb58699a9f793fcda0fdc1/?utm_source=claude_desktop) ·
  [Efficient IR for ET-QKD (Asilomar)](https://consensus.app/papers/details/2a282973c67e53598cafaf63b4fa9afb/?utm_source=claude_desktop)
- Müller 等 2023 QIP：NB-LDPC 与 HD-Cascade 在 **q 元对称信道**上接近 Slepian–Wolf 界——
  仍是 QSC 模型，而我们已经证明真实信道不是 QSC。
  [Efficient IR for HD-QKD](https://consensus.app/papers/details/3df6b8ffb7e55167a6b186cef3e9dcab/?utm_source=claude_desktop)

**B. Polar 码 IR（二元，成熟度的标杆）**
- Yan 等 2018：SCL + 优化结构，比 SC 方案密钥率高 12.8%（2¹⁶，QBER 2%）。
  [Improved polar-code key reconciliation](https://consensus.app/papers/details/cbf8197abe0b5791957ccdbe6d2efa21/?utm_source=claude_desktop)
- Tang 等 2020 SLA：分子块 block-checked SCL + 失败子块补充协调，失败概率 10⁻⁸，f=1.091（128 Mb）。
  [Shannon-limit approached IR](https://consensus.app/papers/details/b6730be565d8570cb385c27da32cd55c/?utm_source=claude_desktop)
- Lee 等 2018：用"虚拟串"让任意密钥也能 CRC 预编码，从而用上 CA-SCL——**正好解决了我们 SCL 需要 CRC 的问题**。
  [Improved reconciliation with polar codes](https://consensus.app/papers/details/ad9199a6ed0f502db3bbc9c1698dc009/?utm_source=claude_desktop)
- 硬件：Guo 2023（15 Mbps）、Liao 2025 FPGA（35 Mbps）——吞吐目标的参照量级。
  [Hardware polar IR](https://consensus.app/papers/details/a515881e3a7752cebac161ddaa0c8624/?utm_source=claude_desktop) ·
  [FPGA polar IR](https://consensus.app/papers/details/fcbe500514995b6b9b06a5161d917272/?utm_source=claude_desktop)
- 盲/速率自适应：Xie 2022（逆编码 + 自适应步长，交互减少至多 38.72%）。
  [Blind polar reconciliation](https://consensus.app/papers/details/d9bdbea580e75e1ea84ba8722af33913/?utm_source=claude_desktop)

**C. 高误码 Slepian–Wolf / 低 SNR 协调的参照（结构类比仅作启发，未证明同构）**
- CV-QKD 的 polar / 速率自适应协调：Cao 2023 PRApplied，FER<10⁻³；Wang 2022 在 polar slice 协调中效率 >95%；
  Wang 2026 的 Polar/LDPC IR-HARQ：每次重传约 2–3 dB 增益，**短块时 Polar 更占优**。
  [Rate-adaptive polar CV-QKD](https://consensus.app/papers/details/b8d4868518d1524dad885c40ff5fd617/?utm_source=claude_desktop) ·
  [Polar slice reconciliation](https://consensus.app/papers/details/10c8321cc27258698cd6485753de5b14/?utm_source=claude_desktop) ·
  [Polar/LDPC IR-HARQ](https://consensus.app/papers/details/6336c60e5eee5bc182284089d6eaad3c/?utm_source=claude_desktop)

**D. 非二元 Polar 本身（我们的算法工具箱）**
- Park & Barg 2013 IT：用 Arıkan 核时，q=2^r 的合成信道极化到 **0,1,…,r bits 的多级容量**，
  而不是只有 0/r 两级 ⇒ **按整符号冻结/披露会浪费码率**。
  [Polar codes for q-ary channels](https://consensus.app/papers/details/716029d3e39351faaa56d6f74dac6c01/?utm_source=claude_desktop)
- Xu 等 2024 ITW / 2025 Entropy：**比特级构造**，每个合成信道承载 i∈[1,q) 个比特，性能显著改善；
  Chen 2022：部分冻结符号里的冻结比特可以用作主动校验位。
  ⇒ 映射到 IR 上就是**部分符号披露**（只公开某些合成符号的若干比特）。
  [Bit-level construction for MR NB polar](https://consensus.app/papers/details/9413c96b21fe57d0b98e7cae44bf73e7/?utm_source=claude_desktop) ·
  [Nonbinary polar with low latency](https://consensus.app/papers/details/1698769ca19458edbdd0548cac79c320/?utm_source=claude_desktop)
- 低复杂度 NB-SCL：arXiv:2607.09257（2026，SR-NBSCL：当前符号足够可靠时不分裂路径 + Rate-1 节点简化）；
  非对称 EMS（2023，`10.1109/istc57237.2023.10273502`）：只计算有竞争力的候选符号。
  **我们的信道每个位置只有 2–3 个候选**，天然适合这类剪枝。（两篇均经 scite 检索到，无 Consensus 链接。）
- 构造：Tal & Vardy 2011；Elkelesh 2019 为给定译码器量身定制的遗传算法构造（**无 CRC 的 SCL 也能达到 CA-SCL 的性能**）；
  PAC 码（Yao 2020：L≥128 的列表译码接近 ML）。
  [How to construct polar codes](https://consensus.app/papers/details/944741d6f442570296b67cc1eb82bdc3/?utm_source=claude_desktop) ·
  [Decoder-tailored polar design](https://consensus.app/papers/details/eb1b7b06c88e5b089717af31827f3368/?utm_source=claude_desktop) ·
  [List decoding of PAC codes](https://consensus.app/papers/details/fc7e6ff097775dabbde81962c211e68e/?utm_source=claude_desktop)
- 源编码 / Slepian–Wolf 的 polar 理论基础：Korada & Urbanke 2010；Arıkan 2012（单调链规则）。
  [Polar codes for Slepian-Wolf](https://consensus.app/papers/details/8001dd73a1055f66ac1ddb91364e201c/?utm_source=claude_desktop)

**空位（可辩护的新意，按强度排序）：**
1. **真实 ToA 符合数据**上的 q 元 Polar 协调，信道取实测经验 P(y|x)，并用 FER-aware 口径完整记账
   ——A/B/C 类文献全部基于模型信道（QSC、Gaussian jitter、BSC）。Müller 2025 的讨论部分明确呼吁这方面的研究
   （`PAPER_READ_20260921.md` §1.1）。
2. **"窗口宽度 vs 码强度"的端到端权衡**：窄窗得到干净信道但丢符合，宽窗保留符合但有尾部。
   A4 Brougham 2016 只提出了问题，没有真实数据上的答案。
3. **原生 q 元 vs 最强二元（自然标号 MSD）在真实 ±1 主导信道上的配对对比**——结论无论正负都能发表。
4. 真实信道**记忆性检验**（块间误差计数的过离散、自相关）——几乎零成本，A2 从理论上预测存在记忆。

---

## §5 三个研究假设（替代现有的状态阶梯）

| 编号 | 假设 | 可证伪读数 | 数据成本 |
|---|---|---|---|
| **H1 可用性**[^hlab] | NB-Polar（CA-SCL + 按实测信道构造 + 增量披露）在真实数据上能达到 f_eff ≤ 1.20 且 FER ≤ 0.02（阈值为提议） | §3 记分板的 M-usable 行 | 合成信道无限量；真实数据块数按 C9 导出（量级上，30 s 采集可提供数百块） |
| **H2 原生优势** | 在相同 f 和 N 下，原生 GF(32) 的 FER 低于**自然标号 LSB 优先 MSD** 的二元 Polar | 同一批块上的配对 ΔFER（McNemar 检验） | 同上 |
| **H3 窗口–码权衡** | 存在一个 W_P > 200，在宽窗加更强的码时 PIE_rec（按总符合计）更高 | PIE_rec–W_P 曲线 | 同一采集重配对，无需新采集 |

[^hlab]: 项目级 H1/H2/H3（本节）与探针局部标签 L-H1/L-H2/L-H3 不混用：后者仅指单个 Tier-X 合成探针内的描述性倾向/排除（非 verdict、非证据），不得当作项目级假设的证实或证伪；历史 `results.json` 数值不动。

H2 为负也不是失败：那样的论文结论是"窄窗配对之后，最优协调本质上是二元的；原生 q 元只在宽窗时才有用"——
这与 H3 合在一起，仍然是一篇完整的论文。

---

## §6 执行路线（12 周，2026-09-28 起）

> 纪律（**按现行规则**）：合成实验按 AGENTS §10.4 在已授权 packet 内以 Tier-X 运行
> （三行 prereg + `results.json` + focused numerical review），输出根 `workspace/probes/<id>/`。
> 真实数据项一律 **NOT AUTHORIZED**，各需逐字授权 packet + Pre-EXECUTE/Pre-RESULT。
> §8 提出的轻量化（如合成实验免 packet、DEV/CONFIRM 两池）只是提议，须经 OpenSpec 修改 AGENTS.md / R2-T4 后才生效。

### Phase A — 记分板与强基线（第 1–2 周；零数据项先做，真实数据项待授权）

| # | 动作 | 交付物 | 完成判据 | 授权状态 |
|---|---|---|---|---|
| A1a | **零数据核实 §2.1–2.2 的粗算**：用冻结的 G1R2 CAL32 三元组复算链式分解；在由三元组生成的合成信道上实现 B0 并测泄漏与 FER | `workspace/probes/<id>/results.json` | 链式分解与 H_M2 的差 < 1%（精确差 2.0e-8；四舍五入版差 1.47e-5；显示 0.8169≠0.8168 系显示精度所致）；B0 的泄漏与合成 FER 落表 | Tier-X（需所在 packet 已授权） |
| A1b | B0 在 SHG DEV 真实数据上运行（块数按 C9 导出，量级 ≥30 块） | 记分板真实行 | 与 A1a 的合成结果一致 | **NOT AUTHORIZED**，需逐字 packet |
| A2 | 二元**自然标号 LSB 优先 MSD** Polar（SC 与 SCL L=8），信道取实测三元组合成 | 合成行：FER–f 曲线，f∈{1.10,1.15,1.20,1.25}，N=2¹⁵（其他 N 须先改冻结常数） | 每点 ≥1000 个合成块 | Tier-X（需所在 packet 已授权） |
| A3 | 当前 NB-Polar（M2 SC）在**同一合成信道**上的 FER–f 曲线 | 同上 | 与 G2/G3 裁决的定性结论一致（交叉校验合成信道是否可信） | Tier-X（需所在 packet 已授权） |
| A4 | Release 二元方案在 SHG 数据上用**同一配对**跑出 PIE_rec | 记分板真实行（输出根由 packet 冻结） | 能与 A1b 放在同一列比较 | **NOT AUTHORIZED**，需逐字 packet |
| A5 | 记忆性检验：每块误差计数的过离散（方差/均值）、跨块自相关 | 一张图 + 一个数字 | — | **NOT AUTHORIZED**（真实数据），需逐字 packet |

**Phase A 决策点**：如果 A2（二元自然 MSD）在所有 f 上都显著好于 A3（NB-Polar SC），
Phase B 必须在 f<1.2 追平它，否则触发 §7 的 K2。

### Phase B — 把 NB-Polar 推进到 f<1.2（第 3–6 周，合成为主）

按预期收益从高到低，一次只改一个因子，每步都在记分板上落点：

| # | 杠杆 | 依据 | 预期 |
|---|---|---|---|
| B1 | **提议解锁 `scl.py`**（SCL 锁定须经 OpenSpec/PI 解除；解除前仅在合成 Tier-X 中使用）+ CRC/虚拟串（Lee 2018）；L∈{4,8,16}；tag 长度按 L 重新标定（Zhou22 eq.7：ε_CRC ≤ L/2^d） | 二元 Polar-IR 的标准做法；代码已存在 | 同 f 下 FER 降一个量级是业界常见幅度（待本项目合成信道验证） |
| B2 | **构造**：在实测三元组信道上做 MC/genie 构造；再做**比特级 / 部分符号披露** | 依据是文献：Park–Barg 的多级极化、Xu 2024/25 的比特级构造——按整符号冻结会浪费码率。S9 arm C 属合成描述性结果、非证据，decision-log :5360/:5362 已否决以其为推荐路线，**不作为本项依据** | 同 FER 下降低 f |
| B3 | **层序与表示**：低位先于高位（进位由条件化消化），或直接取消 5+5 分层 | §2.1：L1 的 H≈0.025，却被披露了约 2× | 省下约 0.02–0.05 bits/符号 |
| B4 | **增量披露 / 盲协议**（AIR/SLA 式，Müller 式按块自适应）：第一轮按目标 f 披露，失败块再按可靠度追加 | 把整块损失变成少量额外泄漏 | 使 FER→≈0，f_eff 仅小幅上升 |
| B5 | **块长**：N=2¹⁷–2¹⁸（采集量已足够，SC 复杂度为 N log N）。N=32768 是冻结常数，改动须经 OpenSpec | 有限长损失随 N 下降 | f 再降 |
| B6 | **吞吐**：±1 稀疏剪枝（每个位置只保留 2–3 个候选，EMS 思路）+ numba/C 实现 | 当前差约 224× | 目标 ≥10⁵ 符号/s |

**Phase B 退出条件（提议阈值，合成、非 claim）**：在合成的实测信道上，NB-Polar 的某个配置达到 **f≤1.20 且合成 FER≤0.01**。
6 周内做不到 ⇒ 触发 §7 的 K1。

### Phase C — 采集（第 1 周提出申请，与 A/B 并行，需要实验室配合；采集与读取属 R2 T7，**NOT AUTHORIZED**）

- 向实验室申请：**同一 SHG 配置采 3–5 段、每段 60 s**，隔天再采一组（独立 session）；
  可选：泵浦功率 2–3 档（噪声工作点）。预计可得约 3,000 块以上。
- 风险：采集越长，时钟漂移越明显 ⇒ 对齐要**分段做**（每 3 s 一段各自对齐，沿用"用本采集自身数据的相关性自动对齐"裁定）。
- 切分：按 R2 草稿 C11，在切块前先切出 CAL / CHAR / HELDOUT / EVAL / RESERVE 五段（互斥），参与/污染 ledger 永不回流（C10）。
  "DEV/CONFIRM 两池"只是供 PI 讨论的简化提议，经 R2-T4 裁定前不采用。

### Phase D — 真实数据测量（第 7–10 周；R2 T8，全部 **NOT AUTHORIZED**，需逐字 packet）

1. 开发段上：用 Phase B 的最优配置扫 3 个 f 点（块数按 C9 导出），得到真实数据的 FER–f 曲线；同时跑 B0 和二元自然 MSD（配对，同一批块）。
2. H3：同一采集在 W_P∈{200,350,500} 下重新配对，画 PIE_rec（按总符合计）–W_P 曲线。
3. EVAL / 确认段：冻结一个配置，在 ≥2 个 session 上**一次性**运行（块数按 C9 导出）→ 这就是 M-usable / M-competitive 的判定数据。
   R2 合同 C1–C14 按 T4 裁定后的冻结版执行。

### Phase E — 论文（第 9–12 周，与 D 部分重叠）

- 论文 1（主）：真实 ToA 纠缠数据上的 q 元 Polar 协调——经验先验（M2 的发现）、FER-aware 记账、与 B0/二元的同数据对比、记忆性检验。
- 论文 2（可选，看 H2/H3 的结果）：窗口宽度–码强度权衡，以及原生 vs 二元在真实信道上的对比。

### 时间表

| 周 | 日期（周一） | 主线 | 并行 | 决策点 |
|---|---|---|---|---|
| 1 | 09-28 | A1a、A2（合成） | C：提交采集申请 | — |
| 2 | 10-05 | A3（合成）；A1b/A4/A5 视授权情况 | C：采集（若获授权） | **D-A**：强基线排序（§6 Phase A 决策点） |
| 3–4 | 10-12 | B1 SCL、B2 构造（合成） | C：按 C11 五段切分 | — |
| 5–6 | 10-26 | B3/B4/B5 | B6 吞吐 | **D-B**：是否达到 f≤1.2 / FER≤0.01（K1） |
| 7–8 | 11-09 | D1 开发段真实数据曲线（需授权） | D2 窗口研究（需授权） | — |
| 9–10 | 11-23 | D3 确认段一次性运行（需授权） | E 论文初稿 | **D-D**：M-usable / M-competitive 判定 |
| 11–12 | 12-07 | E 论文定稿 | 查漏补缺 | 投稿 |

---

## §7 止损 / 转向条件（预先写死，避免事后找理由）

| 编号 | 触发条件 | 动作 |
|---|---|---|
| **K1** | 第 6 周末：合成信道上 NB-Polar 所有配置都无法同时做到 f≤1.20、FER≤0.01 | 目标降到"f≈1.2–1.25 下 FER≈0 且吞吐可用"，论文强调真实信道刻画与记账；不再追求 f |
| **K2** | 第 2/6 周：二元自然 MSD 在同 f、同 N 下 FER 始终不高于 NB-Polar | H2 判负；主线改为"二元自然 MSD + 真实信道"，NB-Polar 作为对照写进论文，不再继续投入原生路线 |
| **K3** | A5 显示显著记忆（过离散 > 2×） | B4 增量披露与分块自适应（Scarinzi 式按块信道估计）优先级提前 |
| **K4** | 第 4 周：实验室无法提供新采集 | 只用尚未被解码器接触过的 SHG 帧（RESERVE 等，受 C10 永不回流约束）和 01-21 三源的开发用途帧；按 C9 重新导出可达的 w，不足则记为 INSUFFICIENT 并在论文中如实说明（C11，永不垫块） |
| **K5** | 吞吐在第 8 周仍 < 10⁴ 符号/s | 论文不作"实时可用"表述，只报测得的吞吐 |

---

## §8 流程瘦身建议（需 PI 同意；保留防错机制，删掉纯仪式）

**保留**（这些能防止错误结论）：
- `undetected` 隔离与分列；评审 FAIL 即阻塞执行或固化（AGENTS §3）。
- 确认段一次性运行，不得重跑调参；参与/污染 ledger 永不回流。
- `results/`、`outputs_comparison/` 只加不覆盖；失败块按整块计泄漏。
- R2 合同的防错核心条款：C1（可比性边界、摘要禁令、caveats (a)–(d)）、C2（FER 定义）、C3（Wilson CI，保证跨门可比）、
  C4/C5（隔离与五元分类）、C9（样本量推导链）、C10（原始文件规则与 ledger 永不回流）、C11（五段互斥、COMPLETE-BLOCKS-ONLY）、C13（预算语义）。

**精简**（全部是提议，须经 OpenSpec 修改 AGENTS.md，或经 R2-T4 裁定后才生效）：
1. 合成实验：在 §10.4 Tier-X 的基础上进一步轻量化，例如一个长期授权的"合成信道 packet"覆盖多次探针，而不是每个探针单独建 packet/STATUS/授权文本。
2. 评审：FAIL 仍按 AGENTS §3 阻塞，不能绕过。可以建议的是**缩小评审范围**，只审会改变数值或科学结论的项
   （阈值、泄漏分解、`undetected`、授权、输出根），把格式和措辞问题留到里程碑批量处理。
3. 用 §3 记分板替代 `STATE.md` 中的状态阶梯和多层状态串；`STATE.md` 压缩到一页：当前最佳记分板行 + 下一个决策点 + 止损条件。
4. R2 测量合同：保留上面列出的防错核心条款；C6/C7/C8/C12/C14 可考虑移入附录。T3/T4/T5/T6 是否合并为一次 PI 会议，由主线程 / PI 决定。
5. 一次性 probe 脚本（约 3.5 MB）移入 `legacy/`，新实验只调用 `sc.py`/`scl.py`/`construction.py`/`prior.py` 这类核心模块。

---

## §9 需要 PI 拍板的 6 件事（建议在一次会议里定完）

1. 是否接受 §3 的北极星指标（PIE_rec 按**总**符合计 + 吞吐）作为唯一进度度量？
2. 是否把目标区间从"f≤1.3"改为"f_eff≤1.20（M-usable）/ ≤1.12（M-competitive）"？（经 R2-T4 / OpenSpec）
3. 是否同意把**二元自然标号 MSD** 和 **B0** 列为必须对比的基线？
4. 能否向实验室申请 3–5 × 60 s 的 SHG 采集（两个 session）？（采集与读取另需逐字授权）
5. 是否就 §8 的轻量化提议（长期合成 packet、评审范围收窄、是否简化 C11 切分）发起 OpenSpec 修改？
6. 是否解锁 `scl.py`（SCL 的 5 项合取锁在 Phase B 中改为以记分板结果判定）？（经 OpenSpec）

另外还有几项同样需经 OpenSpec / PI / R2-T4 裁定、不能由本文件自定：块长 N 的变更、
样本量 n（按 C9 从 Δ 导出，不独立选数）、f_eff 中 H(q)→经验 H(X|Y) 的替换口径（C6，须冻结时预注册）。

---

## §10 参考文献

**项目内已精读**（见 `PAPER_READ_20260921.md`、`LITERATURE_FIT_CHECK_20260921.md`）：
Müller 2025 IET QC（`10.1049/qtc2.70003`）；Zhou 2022 AIR PRApplied 18, 044022；Kanitschar & Huber 2025 PRL 135, 010802；
Boutros & Soljanin 2023 TCOM（`10.1109/TCOMM.2023.3302135`）；Birnie 等 TCOM（`10.1109/TCOMM.2023.3244244`）；
Al-Qahtani 等 arXiv:2608.05432；Martínez-Mateo 等 QIC 15(5-6)；Müller 2024 QIP（`10.1007/s11128-024-04395-w`）；Scarinzi 2025 arXiv:2511.05196。

**本次新检索**（Consensus / scite；链接为检索工具返回的原始地址）：

1. Zhong T. 等 (2015). Photon-efficient QKD using time–energy entanglement with high-dimensional encoding. *New J. Phys.* 17, 022002. `10.1088/1367-2630/17/2/022002` — [link](https://consensus.app/papers/details/f2d01a7bc17d51d98ed91cc4154d8295/?utm_source=claude_desktop)
2. Lee C. 等 (2014). Entanglement-based quantum communication secured by nonlocal dispersion cancellation. *PRA* 90, 062331. `10.1103/physreva.90.062331`
3. Mitra D. 等 (2024). Efficient IR in QKD systems using informed design of non-binary LDPC codes. *QIP*. — [link](https://consensus.app/papers/details/c4fa9f2561075c648d877d11aeb3889b/?utm_source=claude_desktop)
4. Mitra D. 等 (2023). Non-binary LDPC code design for ET-QKD. arXiv. — [link](https://consensus.app/papers/details/0a5096a4d88559d7b3046fb428627d21/?utm_source=claude_desktop)
5. Yang S. 等 (2019). Efficient IR for energy-time entanglement QKD. Asilomar. — [link](https://consensus.app/papers/details/2a282973c67e53598cafaf63b4fa9afb/?utm_source=claude_desktop)
6. Müller R. 等 (2023). Efficient IR for high-dimensional QKD. *QIP*. — [link](https://consensus.app/papers/details/3df6b8ffb7e55167a6b186cef3e9dcab/?utm_source=claude_desktop)
7. Yan S.-L. 等 (2018). An improved polar codes-based key reconciliation for practical QKD. *Chin. J. Electron.* — [link](https://consensus.app/papers/details/cbf8197abe0b5791957ccdbe6d2efa21/?utm_source=claude_desktop)
8. Tang B.-Y. 等 (2020). Shannon-limit approached IR for QKD. *QIP*. — [link](https://consensus.app/papers/details/b6730be565d8570cb385c27da32cd55c/?utm_source=claude_desktop)
9. Tang B.-Y. 等 (2022). Polar-code IR with frozen-bit erasure strategy. *PRA*. — [link](https://consensus.app/papers/details/40457dc01ceb5900abf5ee6d261da0f0/?utm_source=claude_desktop)
10. Lee S. 等 (2018). Improved reconciliation with polar codes in QKD（虚拟串 CRC）. arXiv. — [link](https://consensus.app/papers/details/ad9199a6ed0f502db3bbc9c1698dc009/?utm_source=claude_desktop)
11. Guo J.-B. 等 (2023). Shannon-limited polar IR hardware implementation. *QST*. — [link](https://consensus.app/papers/details/a515881e3a7752cebac161ddaa0c8624/?utm_source=claude_desktop)
12. Liao L. 等 (2025). Efficient FPGA implementation of polar IR. *Sci. Rep.* — [link](https://consensus.app/papers/details/fcbe500514995b6b9b06a5161d917272/?utm_source=claude_desktop)
13. Xie J. 等 (2022). Blind reconciliation based on inverse encoding of polar codes. *QIP*. — [link](https://consensus.app/papers/details/d9bdbea580e75e1ea84ba8722af33913/?utm_source=claude_desktop)
14. Cao Z.-W. 等 (2023). Rate-adaptive polar-coding-based reconciliation for CV-QKD at low SNR. *PRApplied*. — [link](https://consensus.app/papers/details/b8d4868518d1524dad885c40ff5fd617/?utm_source=claude_desktop)
15. Wang X.-Y. 等 (2022). CV-QKD with low-complexity IR（polar slice）. *Opt. Express*. — [link](https://consensus.app/papers/details/10c8321cc27258698cd6485753de5b14/?utm_source=claude_desktop)
16. Wang D. 等 (2026). Rate-compatible Polar/LDPC HARQ reverse reconciliation in CV-QKD. *IEEE OJVT*. — [link](https://consensus.app/papers/details/6336c60e5eee5bc182284089d6eaad3c/?utm_source=claude_desktop)
17. Park W. & Barg A. (2013). Polar codes for q-ary channels, q=2^r. *IEEE TIT*. — [link](https://consensus.app/papers/details/716029d3e39351faaa56d6f74dac6c01/?utm_source=claude_desktop)
18. Xu R. 等 (2025). Bit-level construction for multiplicative-repetition-based NB polar codes. *Entropy*. — [link](https://consensus.app/papers/details/9413c96b21fe57d0b98e7cae44bf73e7/?utm_source=claude_desktop)
19. Chen P. 等 (2022). Nonbinary polar coding with low decoding latency and complexity. — [link](https://consensus.app/papers/details/1698769ca19458edbdd0548cac79c320/?utm_source=claude_desktop)
20. Low-complexity SCL decoding of 2×2-kernel non-binary polar codes (2026). arXiv:2607.09257（scite）。
21. Asymmetrical extended min-sum for SC decoding of NB polar codes (2023). ISTC. `10.1109/istc57237.2023.10273502`（scite）。
22. Rate assignment for multi-level polarised NB polar codes (2016). *IET Commun.* `10.1049/iet-com.2015.0738`（scite）。
23. Tal I. & Vardy A. (2011). How to construct polar codes. *IEEE TIT*. — [link](https://consensus.app/papers/details/944741d6f442570296b67cc1eb82bdc3/?utm_source=claude_desktop)
24. Elkelesh A. 等 (2019). Decoder-tailored polar code design using the genetic algorithm. *IEEE TCOM*. — [link](https://consensus.app/papers/details/eb1b7b06c88e5b089717af31827f3368/?utm_source=claude_desktop)
25. Yao H. 等 (2020). List decoding of Arıkan's PAC codes. *Entropy*. — [link](https://consensus.app/papers/details/fc7e6ff097775dabbde81962c211e68e/?utm_source=claude_desktop)
26. Korada S. B. & Urbanke R. (2010). Polar codes for Slepian-Wolf, Wyner-Ziv, and Gelfand-Pinsker. ITW. — [link](https://consensus.app/papers/details/8001dd73a1055f66ac1ddb91364e201c/?utm_source=claude_desktop)
27. Birnie D. 等 (2022). Information rates with non-ideal photon detectors in TE-QKD. *IEEE TCOM*. — [link](https://consensus.app/papers/details/1e384b0531cb58699a9f793fcda0fdc1/?utm_source=claude_desktop)
28. Boutros J. & Soljanin E. (2023). Time-entanglement QKD: SKR and IR coding. *IEEE TCOM*. — [link](https://consensus.app/papers/details/2fd317e2e4e951e6a846027fc5ad2777/?utm_source=claude_desktop)

**未经本次工具检索、仅作提示**（引用前须补查原文）：多级编码设计准则（Wachsmann, Fischer & Huber 1999, IEEE TIT）——
MSD 下集合划分 / 自然标号优于 Gray，这是 §2.2"自然标号是二元最强形态"这一判断的经典依据。

---

*本文件为规划输入：不授权任何执行，不改变任何科学状态，不含实测 FER 数字主张。§2 的 [粗算] 项在 Phase A1a/A1b 核实之前不得作为结论引用。*
