# 论文推荐 vs 仓库实际：适用性 / 可复用性 / 已使用与归档状态（2026-09-21）

范围：仅核对本 checkout（`HD-QKD_Polar_Comparison-nbpolar`，NB-Polar 主线）的实际
文件、代码、OpenSpec 与决策记录。NB-LDPC 历史属隔壁 Comparison checkout 所有，本
checkout 内的 V8/V53/V57 等内容按 AGENTS.md §0 视为继承的只读资产。

## 0. 一句话结论

1. **三类建议里，仓库已各自有本土等价物**：经验信道（V25/V57 per-layer 经验
   \(P(a|b)\)）、\(f_{\mathrm{eff}}\)（V57 `leak=5*m+64` 已含 verification tag）、
   rateless/增量冗余（V53 conditional-HARQ Δm=8、NB-Polar nested disclosure +
   `incremental.py`）。**缺的不是"从零引进"，而是统一口径与闭合自适应回路。**
2. **真正未使用、且成本最低的增量是 Scarinzi 2025 那条线**（分块信道估计 + 按块
   重算披露预算）——仓库已把"预算与 \(H\) 脱钩"列为已知风险，且可零新数据读取起步。
3. **Zahidy 2024 / Ogrodnik 2025 / Kanitschar-Huber 2025 / Zhou 2022 AIR 全仓零命中**，
   属全新引用；但它们都落在"净密钥与系统效应"外层，按仓库门禁应在 NB-Polar 出现
   可复现真实恢复之后再引入，不能提前当 IR 证据。

---

## 1. 逐篇核对表

| 论文 | 仓库状态 | 关键证据位置 | 适用性 | 建议动作（含门禁） |
|---|---|---|---|---|
| **Müller 2025**，industrial Cascade/LDPC，DOI `10.1049/qtc2.70003`（P0） | **已引用、未精读、未落地为统一指标**。survey 标 "flagged for reading"；roadmap 已给定位结论 | `docs/nonbinary-ldpc-efficiency-roadmap-survey.md:33`；`docs/hd-qkd-ir-performance-roadmap-20260824.md:246`（"支持保留 R4 系统级基线及 verification/leakage 成本，但 binary/BSC 长帧结果不是 GF32 证据"） | 高，但**只作为记账口径依据**，不得外推其二元数字 | 不新开算法线；做"λ 分解契约"文档级 change：把 failed-frame 成本与额外交互轮次并入现有 \(f_{\mathrm{eff}}\) |
| **Müller 2024**，NB-LDPC + HD-Cascade，DOI `10.1007/s11128-024-04395-w` / arXiv:2307.02225（P0） | **已使用且已验收**：V8 参考复现（复现 Table 1，q=4 R=0.75 门限 0.069；V8-60 公式更正；独立 reviewer-go 接受，A12 blocked 已解除）。**HD-Cascade 未实现** | `openspec/changes/formal-nonbinary-ldpc-v8-reference-reproduction/`（`evidence/v8_muller2024_table1_extract.txt`、`v8_independent_review_acceptance.json`、`v8_60_correction_evidence.json`）；`comparison_bench/src/comparison_bench/formal_ir/nonbinary_v8_mcde.py:607` | 复现已完成，非新工作量；QSC 假设已被本仓库证伪 | 若再立项 HD-Cascade，按 roadmap §8 的既有四条指标走（exact FER/false accept、总公开 leakage、轮次/延迟/吞吐、净 key-rate）——**这四条与建议完全一致，已提前定义** |
| **Tarable 2024**，rateless protograph LDPC（P0） | **仅文献引用，未实现**；true protograph/MET 在 V23 被判"未实现" | `docs/hd-qkd-ir-performance-roadmap-20260824.md:240`；`docs/nbldpc-v35-successor-plan-20260824.md:67`；`docs/nbldpc-v19-v23-review-summary-20260816.md:49-64` | 中；**当前非主线** | NB-LDPC 侧受 D5/D6 STOPPED 与 R1d 暂停约束（`roadmap §12`）。NB-Polar 侧已有更便宜的等价物（下节），不建议此刻引入 protograph |
| **Scarinzi 2025**，satellite downlink rateless 码率选择，arXiv:2511.05196（P0） | **完全未使用**（全仓 `satellite/downlink/2511.05196/Scarinzi` 零命中） | — | **最高**：与仓库已有风险直接咬合 | 立"分块信道估计 + 按块重算预算"探针；先用已冻结 counts，零新受保护数据读取 |
| **Zhou 2022 AIR**（PRApplied 18, 044022）/ **Tang 2021 SLA**（P1） | AIR **零命中**；SLA 已引用为效率标杆 | SLA：`docs/nonbinary-ldpc-efficiency-roadmap-survey.md:30`（f=1.055–1.091，大块 DV-QKD 标杆） | 中；精神已本土化 | NB-Polar 的 nested disclosure + restart-from-scratch（`ROADMAP` Phase 6、`CRITICAL_PATH` step 9、`nbpolar/incremental.py`）已是 AIR 式渐进揭示。缺口是 SCL 自 P20H 锁死；须先过 `scl-synthetic-list-gate` |
| **Zahidy 2024**，multicore fiber 4D，DOI `10.1038/s41467-024-45876-x`（P1） | **未使用**（仅作为 Müller 2024 共同作者出现在 V8 证据中） | `evidence/v8_muller2024_table1_extract.txt:13`、`v8_literature_provenance.json` | 低-中：系统/探测器效应，非 IR 证据 | 仅作"非 IR 因素上限"引用；**其 f=1.06 必须标为系统建模参数，不得标为实测协调效率**（与 AGENTS.md §5.5 一致） |
| **Ogrodnik 2025**，resource-efficient detection，arXiv:2412.16782（P1） | **完全未使用**（零命中） | — | 中：jitter/色散/时间窗重叠对 ToA 净收益的约束 | 与本项目 ToA 映射强相关；建议在写净密钥讨论时作为"编码收益可被探测资源吞掉"的引用 |
| **Kanitschar & Huber 2025**，HD-QKD 分析框架，PRL 135, 010802（原 P2） | **完全未使用**（零命中） | — | **⬆ 上调为 A 级、直接适用**（原判"PM 不可套"**错误**，见附录 D）：其演示系统逐字为"high-dimensional **temporal entanglement** setup"且测量 **ToA (T_T)** 与 T_SUP，与本仓库 time-bin 层 + BBM92 偏振层结构一致。**但它显式排除 IR**（\\(H(X\|Y)\\) 项"purely classical"），故只作外层密钥率框架，与我们的 \\(\\lambda_{EC}\\) 互补 | 优先级由 P2 升为 A；finite-size 须连带引配套 [40]。**已由附录 D 修正** |

---

## 2. 建议的"三点改动"对照仓库现状

### 2.1 全局 QSER → 经验信道 \(\hat P(y|x)\)

**已具备（比建议更强）**：

- 经验条件分布已入主链：`load_v25_channel_counts` + `SUPPORT_RULE`（counts/列和 +
  1e-15 floor，无 λ、无回退），见 `.codebuddy/memory/2026-09-19.md`；
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13.py:219-225`。
- 分层/分源信道重表征已完成：V57 per-layer Laplace（`v57_channel_recharacterization.py:435`，
  `H1/H2/H_hier` per source 1M/1.5M/2M），结论 `PREDICTIVE_MODEL_NOT_STABLE` / `DECODE_FORBIDDEN`。
- QSC 失效已量化：经验 \(H(\mathrm{diff})=0.547\) bits/symbol vs QSC(p=0.20) 模型熵
  2.722（`docs/nonbinary-ldpc-efficiency-roadmap-survey.md:16-17, 57`）。

**缺口**：

- 粒度只到 source/session 与 layer，**没有 block 级 QSER**，也没有由时间偏移/抖动/边界
  距离生成的逐符号 soft information。
- 已知风险未解决：**绝对 bit 预算（34119）跨 session 冻结，未按 session 自身 \(H\) 重算**
  （`.codebuddy/memory/2026-09-19.md`）。这正是 Scarinzi 类自适应要闭合的回路。

### 2.2 verification-aware \(\lambda_{\mathrm{total}}\) 与 \(f_{\mathrm{eff}}\)

**已具备**：

- \(f_{\mathrm{eff}}\) 已存在，但不是建议的完全版。V57 口径：
  `f_eff = leak/(N*H)`，`leak = 5*m_total + 64`（syndrome + 64-bit tag），
  见 `v57_channel_recharacterization.json:15`、`v57_channel_recharacterization.py:435`。
- NB-Polar 方法层已分项记账：`key_dependent_bits_total`、`public_control_bits_total`、
  `verification_invocations`、`feedback_control_invocations`、`runtime_s`、
  `throughput_input/output_bits_per_s`、`beta_eff_empirical`，
  见 `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py:184-239`。
- outcome 已严格分流：`exact / undetected / verify_failed / decode_failed / resource_abort`，
  且 AGENTS.md §5.5 禁止把 `undetected` 并入 success/FER。

**缺口**：

- 未把 **failed-frame 成本** 与 **额外交互轮次** 计入 \(\lambda_{\mathrm{total}}\)；
- 跨方法统一口径被现存规则挡住：`AGENT_PROJECT_MEMORY.md:2300`
  "leakage 分解语义不一致时不得跨方法比较" → 要统一 \(f_{\mathrm{eff}}\) 必须先写
  decomposition contract，否则违反既有规则；
- 当前冻结预算 `f=1.29985 / leakage 34119`（N=32768）。一旦按建议并入 failed-frame
  与轮次成本，该数字会上升——需重新 prereg，不能事后补记。

### 2.3 固定 GF32 vs rateless 分支并列

**已具备（本土等价物）**：

- NB-LDPC 侧：`formal_ir/v53_rate_adaptive_l2_heldout_confirm.py` =
  "nested rate-adaptive L2 heldout confirm (**conditional HARQ**) Δm=8"，45 blocks paired，
  descriptive only —— 这就是增量冗余/rateless 的近亲，已实现且有执行包。
- NB-Polar 侧：`nbpolar/incremental.py` + `methods/nbpolar_incremental.py` 已实现嵌套披露
  \(D_0\subset D_1\subset\dots\)、逐层 reject-advance（`decode_rejected_continue_count`）、
  feedback 控制位与 tag 调用计数；`adaptive_l1.py` / `adaptive_l1_revalidate.py` 对应已冻结的
  **P6 adaptive hard-L1** 证据根。
- 分组符号映射对照臂有基础设施：`methods/qldpc_reference.py`（q=4/8 已跑过）、
  历史 `leakage_decomposition.json` 含 q16（f≈3.016）与 q1024 n128（f≈7.245）。

**缺口 / 阻塞**：

- HD-Cascade 未实现，且按 `roadmap §8` 不进当前周期、不与 D7 争预算；
- q-ary SCL 自 P20H 锁死，解锁需先过合成信道 `scl-synthetic-list-gate`；
- 受保护数据人口是硬约束：可用 never-used 段仅 261f/66816 pairs，现行
  "128 连续帧/同 split/同 session" 规则下 = **0 个完整 N=32768 块**；2M 内部合并可得唯一 1 块。
  → 任何"多分支并列比较"都受此人口上限约束，必须先解决评估人口，否则统计力度不足
  （现状已是 1/4、5 块 / 20 records 的 descriptive 级别）。

---

## 3. "不建议作为核心证据"清单的仓库一致性核对

| 项 | 仓库现状 | 判定 |
|---|---|---|
| Mao 等 570 Mbps / f=1.038（已撤稿） | 仓库引用的是 **另一篇** Mao, Qiao & Li, *Entropy* 23, 1440 (2021)，用于 syndrome reuse / 少交互轮次（`docs/v34-formal-execution-er1-closeout-20260824.md:101-104`）；撤稿那篇（s11082）零命中 | **无需处理**，现有引用不受影响 |
| 115.8 Mbps 高速 QKD（Nature Photonics s41566-023-01166-4） | 零命中 | **无需处理** |
| "zero information leakage" 多项式插值协调 | 零命中（仓库内 `zero_leakage` 仅指 V45/V46 的对照臂"零额外泄漏"语义） | **无需处理** |
| 高维系统论文里的 f=1.06 / f=1.1 | 未被当作实测 IR 证据；AGENTS.md §5.5 与 §5.5 语义规则已禁止把估计值当实测 | 与建议**一致**，保持 |

---

## 4. 建议落地顺序（受当前门禁约束）

当前真实授权状态：P20O Stage A 完成 + Pre-EXECUTE PASS，**Stage B 待授权**；SCL 锁死；
NB-LDPC 主线 D7（decoder certification → easy-regime → bidirectional oracle → schedule），
R1d 冻结暂停。

1. **零成本先行**（不读新受保护数据、不动 decoder）：
   - 在已冻结 counts / `calibrated_prior.npz` 上做 **block 级 QSER 与分块经验 \(H\)** 的描述性
     扫描，直接检验"全局 QSER vs 分块"差异（对应建议第一点 + Scarinzi）。
   - **自适应量决策（Scarinzi 2025 原文）**：用**按块平均信道容量 \(\bar C\)**（等价于
     block-wise \(H(X|Y)\)），**不是**按块平均 QBER / 平均 QSER——原文为
     *"initializing rateless code selection based on the mean channel capacity of
     each block consistently outperforms using the mean QBER"*（胜出的是平均信道容量，
     平均 QBER 是被打败的基线）。开放问题：块级平均与逐符号 soft information 的等效性
     必须在**本项目经验信道 regime** 内探测验证，未探测前不得把"可省逐符号 soft info"
     当工程收益转移（no transfer without a probe）。
   - 写 **λ 分解契约**文档 change：定义 \(\lambda_{\mathrm{total}}\) 四项与 \(f_{\mathrm{eff}}\) 分母，
     明确 failed-frame 与轮次如何计入，并声明 V57 旧 \(f_{\mathrm{eff}}\) 与新口径的关系。
2. **指标层落地**（仅工程/文档，无 claim-bearing 执行）：把 `nbpolar_incremental` 已有的
   `feedback_control_bits` / `tag_invocations` / `runtime_s` 聚合成统一报告列，先在既有
   P6/P20 已冻结证据根上**只读重算**，验证口径可重算再谈新实验。
3. **自适应闭环**（需新授权）：按块 \(H\) 重算披露预算，取代跨 session 冻结的 34119。
   这是当前性价比最高的算法改动，且直接回应已登记风险。
4. **并列分支比较**（人口问题先解）：在解决 never-used 段人口约束后，再做
   固定 GF32 / 分组映射 / 增量冗余 / HD-Cascade 的同批配对比较；HD-Cascade 需独立立项。
5. **净密钥外层**（最后）：接 Kanitschar 类框架与 Route A finite-key，引用 Zahidy/Ogrodnik
   作为系统/探测效应上限；不得把文献 \(f\) 当实测。

## 5. 引用与表述红线（复用仓库既有规则）

- Müller 2025 的数字（6.7 kbit/s、f=1.036/1.166、446 vs 3.14 messages、
  FER<0.003）已由用户提供 PDF 逐字核实（附录 C.1），可进入 claimed-evidence
  表格；但它们仍是**二元/BSC 长帧**结果——不得外推为 GF32/ToA 证据
  （`roadmap:246` 已有同样限定），只可作为记账口径依据。
- blind-LDPC "最终无 frame error" 是 *by design*（原文逐字，见附录 C.1：
  *"The blind protocol has no frame errors by design"*），**永远不得**等同有限
  预算下的 exact recovery；本仓库 `undetected` 与 `verify_failed` 必须独立计数
  （AGENTS.md §5.5）。
- Zahidy 2024 的 \(f_{\mathrm{err},4D}=1.06\) 是 *estimated*（引用他人 Cascade 结果，
  分母为二元化熵 \(H_{4D}(\phi_Z)\)）——**禁止**标注为实测 reconciliation
  efficiency；这是 AGENTS.md §5.5 的教科书案例（原文见附录 A.2）。
- Ogrodnik 2025 的 key rate 必须连带 *simplistic* 限定：Talbot 色散探测引入
  mode-dependent detection efficiency mismatch，*violates the assumptions of the
  standard proof* → 不是合规净密钥，不得作为 net key-rate 引用（原文见附录 A.2）。
- 跨方法泄漏比较必须先统一分解语义（`AGENT_PROJECT_MEMORY.md:2300`）。
- 任何真实数据/昂贵/decoder 执行前仍须走 Pre-EXECUTE 与 Pre-RESULT 双重评审（AGENTS.md §3）。

## 6. 证据独立性登记（evidence-independence register）

以下三组文献**不是互相独立的证据**。规则：**组内论文不得作为相互印证
（mutually corroborating）的引用**；surface reference count ≠ independent-evidence
count——结论强度只按独立证据数计。

| 组 | 成员 | 非独立关联 |
|---|---|---|
| G1 | Scarinzi 2025 ↔ Tarable 2024 | 共同作者 Marco Ferrari |
| G2 | Zhou 2022 AIR ↔ Tang 2021 SLA | 共同作者 Bang-Ying Tang / Bo Liu（同组延续） |
| G3 | Müller 2024 ↔ Müller 2025 ↔ Zahidy 2024 | 同一合作组（DTU + CNR/UNIFI：Müller、Zahidy、Vagniluca、De Lazzari、Zavatta 等） |

执行口径：

1. 组内多条引用只记**一条**独立证据；声称"多条独立证据支持"必须引入组外文献。
2. 任何"多篇文献一致表明 X"的表述，先查本表；若成员同组，改写为单来源主张并注明组号。
3. 需要组内数字时（如 Müller 2024/2025 的效率口径），可引用为同一来源的多次测量，
   不得表述为独立复现或交叉验证。

---

# 附录 A：SciVerse 原文核对（2026-09-21）

方法：按 DOI 精确过滤 `search_papers` + 限定 `doc_id` 的 `semantic_search` +
`read_content` 读原文片段。以下每条都标注了核对到的原文出处。

## A.1 元数据订正（必须改）

| 项 | 用户提供 / 仓库现状 | SciVerse 核对结果 |
|---|---|---|
| **Tarable 2024 DOI** | 用户给 `10418979`；仓库 `roadmap:240` 引 TQE 网站链接 | **正确 DOI = `10.1109/TQE.2024.3361810`**，IEEE Trans. Quantum Engineering 2024。`10418979` 只是 Xplore document ID，不能当 DOI 引用。建议仓库换成 DOI |
| **Ogrodnik 2025** | 用户引 arXiv:2412.16782 | 两者都对；**期刊版为 Optica Quantum 2025, `10.1364/opticaq.560373`**（有全文可核）。引用期刊版更稳 |
| **Tang SLA 年份** | 用户标 2021；仓库标 arXiv 2020 | 均正确：arXiv `2003.03713`(2020) + 期刊版 Quantum Inf. Process. 2021, `10.1007/s11128-020-02919-8` |
| **Müller 2025** | DOI `10.1049/qtc2.70003` | 标题/期刊（IET Quantum Communication）/年份/作者全部吻合。作者 8 人：Ronny Müller, De Lazzari, Chirici, Vagniluca, Oxenløwe, Forchhammer, Zavatta, Bacco。CC-BY OA。**但 SciVerse 未收录全文** |

## A.2 关键结论的原文核实（含 4 处对用户表述的修正）

### Müller 2024（NB-LDPC + HD-Cascade）— 原文已读

- **QSC 假设原文**（`doc bcb3e9cf…`, offset 5405）：
  *"We assume that the quantum channel can be accurately represented by a substitute
  channel where x and y are correlated as a q-ary symmetric channel since errors are
  typically uncorrelated and symmetric."*
  → 仓库"QSC 假设 vs 结构化经验信道"的判断**完全成立**。
- **HD-Cascade 效率**（offset 39574）：
  *"mean efficiencies of f_HD-Cascade = 1.06, 1.07, 1.12 compared to
  f_Cascade = 1.22, 1.36, 1.65 for q = 4, 8, 32"*；practical 版 f = 1.07/1.08 (q=4/16)。
- **q=32 净密钥收益**（同一段，原文逐字）：
  *"For q = 32, an increase of more than 10% in secret key rate over all QBER values and
  an additional 2.5 dB in tolerable channel loss is achievable **according to our
  simulation results**."*
  → 用户"模拟净密钥收益 >10%"准确，且原文自带 simulation 限定 ✓。
- **NB-LDPC 交互**（offset 44945）：*"usually below 10 syndromes per frame using the
  blind scheme"* ✓。
- **⚠ 修正 1**：*"the number of messages required seems to **decrease** with increasing
  dimension"* — HD-Cascade 的消息数随维数**下降**，与"高维必然更费交互"的直觉相反。
  仓库若引用 HD-Cascade 的"交互代价"，必须按这条写。
- **⚠ 修正 2（重要）**：该文**没有任何自有真实数据**。HD-Cascade 全部在 QSC 上评估
  （q=4/8/32, QBER 1%–20%）；所谓"4 维实验"只是 *"Using the setup parameters of a recent
  experimental implementation of 4-dimensional QKD [52]"* —— **借用他人实验的系统参数做
  SKR 外推**。前一版报告写的"有限真实 q=4 子集"应下调为"借用他人 4D 系统参数"。
  ⇒ 本仓库"真实 ToA 数据 + 经验信道"相对该文的差异化边界，比原先认定的还要大。

### Scarinzi 2025（satellite downlink）— 原文已读

- 存在且为真：Thomas Scarinzi, Davide Orsucci, **Marco Ferrari**, Luca Barletta；
  2025-11-07（SciVerse 收录载体为 DLR elib）。
- **⚠ 修正 3（偏差最大）**：用户写的"用瞬时 QBER/LLR 选 rateless LDPC 码率"。原文实际：
  *"we found that initializing **rateless code selection based on the mean channel
  capacity of each block** consistently outperforms using the mean QBER."*
  → 胜出的是**按块平均信道容量**，平均 QBER 是**被它打败的基线**。落到本项目：应选
  "按块 \(\bar C\)"（等价版的 block-wise QSER / \(H(X|Y)\)）而非"按块平均 QSER"作为自适应量。
- **用户判断正确的一条**：block-average LLR 与 full LLR 等效。原文：
  *"strategies 2 and 3 yield identical rates for each block and significantly outperform
  strategy 1 … either retaining full LLR information or, more efficiently, by tracking
  only block-wise averages of the signal, decoy, and vacuum states."*
  → 对 ToA 数据的直接含义：**可能不需要逐符号 soft information，块级平均即可**。这能显著
  降低 §2.1 中"逐符号 soft info"缺口的工程量。
- **⚠ 修正 4（证据独立性）**：作者 Marco Ferrari 同时是 Tarable 2024 的作者
  → Scarinzi 2025 与 Tarable 2024 **不是独立证据**，不能当作两条互相印证的文献。
- 收益量级：*"increasing the secret key length (SKL) by nearly 3%"*（仿真，BB84 decoy-state）。

### Zahidy 2024（multicore fiber 4D）— 原文已读，是 AGENTS.md §5.5 的教科书案例

- SKR 数字核实（offset 5313）：*"final secret key rate (SKR) of 51.5 kbps through a
  52-km long multicore fiber link exhibiting 22 dB of channel loss, deployed in the city
  of L'Aquila"* ✓ 用户数字准确。
- **f = 1.06 的性质（offset 22509，原文逐字）**：
  *"we **estimated** for the 4D states an error reconciliation efficiency
  f_err,4D = λ_EC/(n_Z·H_4D(φ_Z)) = 1.06, which is in line with the most recent results
  reported in the literature for the measured QBER values adopting the original cascade
  error correction protocol[39]."*
  → **完全证实用户判断**：是 *estimated*，且引用他人 Cascade 结果；分母是二元化的
  \(H_{4D}\)，不是本文协调器实例产出。应当作为"系统密钥率建模参数，非实测协调效率"
  的标准引用范例写进 §5 红线。
- 作者名单含 Ronny Müller、Vagniluca、De Lazzari、Zavatta
  → 与 Müller 2024/2025 同一合作组（DTU + CNR/UNIFI）。

### Ogrodnik 2025（resource-efficient detection）— 原文已读

- 实验维度：*"experimentally-obtained simplistic key rates for the two-dimensional and
  four-dimensional case"* → **实验只到 4D**；更高维（含 d=8）为
  *"numerical simulation of detection error rate for a range of detection timing jitter
  values, and for range of dimensions"*（Fig. 5a）→ 用户"d=8 主要为仿真"**正确** ✓。
- **⚠ 必须保留的限定**：*"To avoid confusion we will call them the **simplistic key
  rates**"* —— 因为 Talbot 色散探测引入 **mode-dependent detection efficiency
  mismatch**，*violates the assumptions of the standard proof*。
  → 引用其 SKR 必须连带"simplistic"限定，不能当合规净密钥。
- 与 ToA 直接相关：符号 70 ps、间隔 279 ps、DCM 导致 *"interference fringes overlap …
  resulting in imperfect distinction and in an increased QBER"*
  → 时间窗重叠抬高 QBER，正是本项目 ToA 映射要量的效应。

### Kanitschar & Huber 2025（PRL 135, 010802）— 适用性：经附录 D 上调为 A 级、直接适用

标题/期刊/DOI 核实无误。**但摘要明确其对象是纠缠型 HD-QKD**（time-/frequency-bin
entangled photons），finite-size 部分在配套另一篇 arXiv（未在此文内）。
~~→ 对本项目 ToA prepare-and-measure 数据**不能直接套**，前一版报告的"外层密钥率框架"
定位应下调为"待评估"。~~

**⚠ 本条判定已被附录 D 推翻（2026-09-21 更正）**：本项目数据**不是** prepare-and-measure，
而是 Type-II SPDC 时间-能量纠缠光子对的符合测量（`SECURITY_MODEL.md:11,28-29,49`；
`TypeII_776.1nm_3s`；`coincidence_rate_hz`）。KH25 的演示系统正是同一结构，故**直接适用**。
保留的限定只有两条：①它显式排除 IR；②finite-size 在配套 [40]。

### Zhou 2022 AIR / Tang 2021 SLA

- AIR：PRApplied 18, 044022 ✓；摘要核实 *"overall failure probability around 10^-8 …
  efficiency … 1.046 when the block size is 1 Gb and the QBER of 0.02"* ✓，
  且机制为 *"gradually disclosing the bit values of the polarized channels with high
  error probability"* → 与 NB-Polar nested disclosure 的对应关系成立 ✓。
- SLA：f=1.091 @128 Mb、f=1.055 @1 Gb/QBER 0.02、fail prob 10^-8 ✓ 仓库引用准确。
- **证据独立性**：AIR 作者含 Bang-Ying Tang，SLA 首作者也是他，两组共享 Bo Liu
  → **AIR 与 SLA 是同组延续，不是独立证据**。

### 撤稿项核实

- `10.1007/s11082-024-07829-y` = **Retraction Note**，原文 *"High performance
  reconciliation for practical quantum key distribution systems"* 已被撤；
  理由：*"compromised peer-review processes, inappropriate references, and being out of
  scope for the journal"*（部分作者不同意撤稿）。
  → **完全证实**用户"570 Mbps / f=1.038 不应作为吞吐基准"。
- **新增风险提示**：该撤稿篇的 arXiv 版本 **`arXiv:2101.12565`** 在库中仍可被检索到原文，
  引用时须显式排除；本仓库当前引用的是 **Mao, Qiao & Li, Entropy 23, 1440 (2021)
  （syndrome reuse / 少交互轮次）**，属不同文献，**不受影响** ✓。
- 另注：SciVerse 同时命中"high throughput and low cost LDPC reconciliation"（Qi Han 等，
  60 Mbps / f≈1.1，2019）可作为**未撤稿**的 CPU 吞吐替代锚点，避免误用 570 Mbps。

## A.3 Müller 2025 数字：OBSOLETE（已被 C.1 取代）

**本节原结论作废**：当时因 SciVerse 未收录该文正文而把 `6.7 kbit/s`、
`f=1.036 / 1.166`、`446 vs 3.14 messages`、`FER<0.003` 标为 unverified。
现用户已提供 Wiley OA PDF，`pdftotext -layout` 全文逐字核对完成——**这些数字
全部 verified（见附录 C.1）**，原文引文与所在节次均已记录。原先的
`unverified` 标记**不再适用**，不得再以"未核实"为由拒绝这些数字进入
claimed-evidence 表格；但其使用仍受 §5 红线约束（二元/BSC 长帧结果，不得外推
GF32/ToA）。该文的指标体系主张（式 11/13 的 \(f_{\mathrm{eff}}\)）见 C.1，
§2.2 契约可直接引用，无需自行发明。

## A.4 由核对触发的仓库改动清单

1. `docs/hd-qkd-ir-performance-roadmap-20260824.md:240` — Tarable 链接换成 DOI
   `10.1109/TQE.2024.3361810`。
2. `docs/nonbinary-ldpc-efficiency-roadmap-survey.md:27` — Müller 2024 条目补注：
   "无自有真实数据；4D 结论系借用他人实验参数外推（[52]），QSC 仿真"。
3. §5 红线补两条：
   - Zahidy 2024 的 f_err,4D=1.06 是 *estimated* + 引用他人 Cascade，禁止标为实测；
   - Ogrodnik 2025 的 key rate 必须连带 *simplistic* 限定。
4. 引用独立性登记：Scarinzi↔Tarable（Ferrari）、AIR↔SLA（Tang/Bo Liu）、
   Müller 2024↔2025↔Zahidy 2024（同一合作组）——三组内部不得互相"交叉印证"。
5. 新增：Scarinzi 结论应把自适应量从"平均 QSER"改为"**按块平均信道容量 \(\bar C\)**"；且先测"块级平均 vs 逐符号 soft info"是否等效（若等效可省大工程量）。
6. 补引（可选、未撤稿）：Treeviriyanupab & Zhang, Entropy 26(1):53 (2024) 已在本仓库
   survey 引用，其"syndrome QBER 估计 + rate-adaptive + 子块确认"与 Scarinzi 同类且更早，
   可直接作为"自适应 + verification 一体化"的协议样板，无需新增 Scarinzi 即可覆盖部分收益。

---

# 附录 B：补充检索到的高价值文献（2026-09-21）

前两节的论文清单**遗漏了一整条更贴切的文献线**。本轮用 SciVerse（全文库 + 元数据）与
arXiv/网页交叉检索，找到以下候选。按对本项目的价值分级；\\(^\* \\) 标记**与本项目 ToA
数据模型同源**的工作——这些此前在本仓库**零命中**。

## B.1 A 级：与本项目 ToA 数据模型同源（此前完全遗漏，优先读）

| # | 文献 | 出处 | 全文可获取性 |
|---|---|---|---|
| A1\\(^\*\\) | Boutros & Soljanin, *Time-Entanglement QKD: Secret Key Rates and Information Reconciliation Coding* | **IEEE Trans. Commun. 2023, `10.1109/TCOMM.2023.3302135`**；arXiv:2301.00486 | SciVerse 双版本全文：期刊 `doc=c3dd8f6b…`、arXiv `doc=3c80338e…` |
| A2\\(^\*\\) | Birnie, Cheng & Soljanin, *Information Rates With Non Ideal Photon Detectors in Time-Entanglement Based QKD* | **IEEE Trans. Commun. 2023, `10.1109/TCOMM.2023.3244244`**；arXiv:2207.04146 | SciVerse 有 arXiv 全文 `doc=750870a4…` |
| A3\\(^\*\\) | Al-Qahtani, Li & Boutros, *Diversity in Coded TE-QKD Channels: Achieving Infinite Diversity out of Finite System Resources* | arXiv:2608.05432（2026-08-05，54 页，拟投 IEEE 期刊） | **SciVerse 无全文**；arXiv HTML/PDF 免费，**本文已读取 HTML 主体** |
| A4\\(^\*\\) | Brougham, Wildfeuer, Barnett & Gauthier, *The information of high-dimensional time-bin encoded photons* | EPJ D (2016) | SciVerse 有全文 `doc=1076b1fa…`（DOI 待补） |
| A5\\(^\*\\) | Soljanin & Dolecek, *QKD based on time-entangled photons and its key-rate promise* | arXiv:2303.xxxx（2023，综述/入口） | SciVerse 有全文 `doc=163a6b16…` |

**为什么是 A 级**：A1 的数据模型与本项目**逐字同构**——
*"Alice and Bob extract the raw key bits from the (identical) **arrival times** of
entangled photon pairs by time-binning … retain only the frames with a single occupied
bin … as in **PPM modulation** … practical photon detectors suffer from **time jitter
errors** … constructs codes for information reconciliation to approach these rates"*。
这是目前找到的唯一一篇把 arrival-time → bin → frame → PPM-like symbol → jitter → IR
编码设计串在一起的工作；关键词含 **soft-decision decoding**。

**A3 是本轮最有理论价值的一篇（已读原文）**，其核心结果可直接搬来约束我们的设计：

1. **信道模型与我们的假设一致**：\\(\\tilde X=U+Z_1,\\ \\tilde Y=U+Z_2\\)，\\(Z\\sim\\mathcal N(0,\\sigma^2)\\)
   Gaussian jitter，\\(U\\sim\\mathrm{Unif}[0,N[\\), \\(\\hat X=\\lfloor X\\rfloor\\), \\(N=2^m\\) bins,
   **Gray labeling**，每光子 \\(m\\) bits。
2. **两条分离的错误机制（Proposition 1）**：
   - 单 bin 跳：\\(p_{ij}=\\sigma/\\sqrt\\pi=\\Theta(\\gamma^{-1/2})\\)，diversity \\(=1/2\\)；
   - 多 bin 跳 \\(|i-j|\\ge 2\\)：\\(\\mathcal O(e^{-\\gamma/4})\\)，**diversity \\(=\\infty\\)**。
   → 从理论上证明 **ToA 信道的主导错误是"跨边界 ±1 bin"**，且高度结构化。
   这与本仓库观测到的"99.3% 非零差分 < 128"是同一现象的不同尺度**同构**证据。
3. **可搬用的设计定理（含非二元码）**：
   - 代数/硬判决译码：无穷 diversity ⟺ **\\(L=n\\log_2 q/m\\le t\\)**（Corollary 1 明确覆盖
     \\(\\mathbb F_q\\), char 2 ⇒ **含 GF(32)**）；\\(L\\)=每码字光子数，\\(t\\)=纠错半径。
   - 软判决译码：无穷 diversity ⟺ 码是 **MFD deficient**（Definition 3/4：不存在完全由
     "零的邻居标签"构成的非零码字）。**MFD 性质依赖 \\(m\\) 与 Gray labeling**。
   - 码率上界：\\(R_c\\le 1-2\\log_2 q/m\\)；**软判决的码率惩罚是代数译码的一半**。
   → 对本项目：\\(q=32\\)（\\(\\log_2 q=5\\)）、\\(m=10\\) bits/symbol，可直接代入检验
     现有冻结配置落在哪一侧。
   - **"软协调比硬判决更容易达到无穷 diversity 且码率惩罚减半"** —— 直接支持我们走
     soft / q-ary 路线而非硬判决，是此前仓库文档里缺的一条理论依据。
4. **他们的空白 = 我们的创新位**：A3 只评估了 Golay / RS / BCH / RM，**没有 NB-LDPC、
   没有 Polar**。在他们的 diversity/MFD 框架下，**NB-Polar 是空白**。
5. **他们的简化 = 我们的差异化**：A3 明确假设 *"independent detector jitters …
   the induced channel is **memoryless**"*，并 *"does not take into account the sleeping
   phase of a detector after receiving a photon"*。而 A2 恰恰证明 **detector downtime
   引入记忆**（Markov 链模型）+ **dark counts 对 PPM 尤其有害**。
   ⇒ "真实 ToA 信道有记忆 + 非均匀"这一论断现在有了正面（A2）与反面（A3 简化）两侧的
   文献支撑，比仓库现有表述更硬。

**A2 的额外价值**：提供 *"tooling for experimentalists to predict their systems'
achievable secret key rate **given the detector specifications**"* —— 可直接用于我们
写"编码收益可被探测资源吞掉"一节，替代对 Zahidy/Ogrodnik 的间接引用。

**A4 的 ROI 判据**：原文提出 *"whether it is better to **increase the width of the
time-bins** or to **correct the jitter errors using a reconciliation protocol**"*，
并给出含 jitter 的互信息计算 —— 这正是本项目"bin 宽度 vs IR 投入"取舍的现成框架。

## B.2 B 级：verification/FER-aware leakage 的**原始出处**（比 Müller 2025 更早、更正式）

| # | 文献 | 出处 | 可获取性 |
|---|---|---|---|
| B1 | Martínez-Mateo, Pacher, Peev, Ciurana & Martín, *Demystifying the Information Reconciliation Protocol Cascade* | **Quantum Inf. Comput. 15(5-6), `10.26421/qic15.5-6-6`**；arXiv:1407.3257 | SciVerse 全文 `doc=cd7fe814…`（被引 81，FWCI 8.9） |
| B2 | Elkouss, Martínez-Mateo & Martín, *Key Reconciliation for High Performance QKD* | Sci. Rep. 3:1576 (2013) | SciVerse 全文 `doc=74f6420d…` |
| B3 | Pacher, Martín, Martínez-Mateo & Grabenweger, *An IR Protocol for Secret-Key Agreement with Small Leakage* (ISIT 2015) | ISIT 2015 | SciVerse 全文 `doc=ddc10771…` |

**B1 原文逐字（这正是用户建议的 \\(f_{\\mathrm{eff}}\\) 的原型，2014 年）**：

> *"Up to now, efficiency and frame error rate have been considered separately. We have
> also seen that this can be dangerous, since **it does not make sense to have a very high
> efficiency when actually many frames are discarded because of a high frame error rate**.
> Hence, a better measure of the quality of the protocol would be a **modified efficiency
> that takes into account the frame error rate**."*

> \\(\\mathrm{leak}_{EC}=(1-\\varepsilon_{EC})(1-R)+\\varepsilon_{EC}\\)，且说明 *"we
> implicitly assume that **the entire frame is disclosed when the reconciliation procedure
> fails**, or equivalently that in case of error frames are discarded"*。

⇒ **结论修正**：§2.2 要立 \\(\\lambda_{\\mathrm{total}}\\) 契约时，除 Müller 2025 外
**应并列引用 B1（2014）作为公式原型**——它给出了"失败帧按整帧披露计"的明确约定，
正好是本仓库当前缺失的那一项的现成定义，且可核全文。

## B.3 C 级：NB-Polar 近亲（SCL 解锁 / Phase 7 前需要）

| # | 文献 | 价值 | 可获取性 |
|---|---|---|---|
| C1 | Choi & Tao, *High-throughput split-tree architecture for nonbinary SCL polar decoder* (2022) | GF(256)、(128,64)、split-tree + skimming、28nm，**26.1 Mb/s**，比直接映射快 10.3× —— NB-Polar SCL 的**吞吐/资源上界对照** | SciVerse 全文 `doc=20f37e33…` |
| C2 | Yuan & Steiner, *Construction and decoding algorithms for polar codes based on 2×2 non-binary kernels* (2018) | **2×2 GF(q) 核选择**（最大极化 + MC）+ BP/SC/SCL(pruned tree) —— 与我们 Phase 0 冻结的 \\(F_\\alpha=\\begin{bmatrix}1&0\\\\ \\alpha&1\\end{bmatrix}\\) **直接对应，仓库未引过** | SciVerse 全文 `doc=d437c2dd…` |
| C3 | Falk, Bauch & Nissen, *On channel codes for short underwater messages* (Information 2020) | NB polar q=3/5/7 + **GF(q) CRC** + SCL；强调 q-ary source 无 bit↔symbol 转换损失 —— "NB-Polar + 校验标签"的现成实验参照 | SciVerse 全文 `doc=9ec23f2a…` |
| C4 | Mitra, Shreekumar, Tauz, Sarihan, Wong & Dolecek, *Efficient IR … informed design of NB-LDPC codes*, QIP 2024, `10.1007/s11128-024-04343-8` | **NB-MLC(a)** + **JRDO**（用 QKD 信道信息联合优化码率与度分布）+ **IDC**；针对 energy-time/ToA 类协议 | 仓库 `survey:39` **已引用**，建议升格为核心方法参考 |

## B.4 需要你手动下载的清单（SciVerse 全文库未收录 / 被反爬拦截）

| 文献 | 状态 | 建议获取路径 |
|---|---|---|
| **Müller 2025**（IET, `10.1049/qtc2.70003`） | SciVerse 无全文；Wiley pdfdirect **403**；DOAJ **被 Cloudflare 挡** | CC-BY OA，用浏览器直接开 `https://onlinelibrary.wiley.com/doi/10.1049/qtc2.70003`；或机构库 `https://hdl.handle.net/2158/1435592`。**下到后给我，我即可核对 6.7 kbit/s / f=1.036·1.166 / 446 vs 3.14 / FER<0.003** |
| **Zhou 2022 AIR**（`10.1103/PhysRevApplied.18.044022`） | SciVerse 有元数据+摘要，**正文非 OA** | APS 订阅；或查作者机构库/ResearchGate |
| **Kanitschar & Huber 2025**（`10.1103/PhysRevLett.135.010802`） | SciVerse 无全文；APS 页面标 CC-BY | `https://link.aps.org/pdf/10.1103/PhysRevLett.135.010802`（CC-BY）+ 配套 finite-size 篇（arXiv） |
| **A4 Brougham 2016**（EPJ D） | SciVerse 有全文但**未返回 DOI** | 需按标题在 EPJ D 站定位；可能付费 |
| **A3 arXiv:2608.05432** | **已通过 arXiv HTML 读到主体**（定理/引理完整） | 若需图表与 Section VI 数值表，下 `https://arxiv.org/pdf/2608.05432` |

## B.5 由附录 B 触发的建议动作（按成本从低到高）

1. **零成本**：把 A1/A2/A3 三篇写入"信道非 QSC、可能有记忆"的论证链，替代目前仅靠
   仓库内部观测（`H(\\mathrm{diff})=0.547\\) vs QSC 2.722）的单点证据。
2. **零成本**：\\(\\lambda_{\\mathrm{total}}\\) 契约并列引用 **B1(2014)** 的
   \\(\\mathrm{leak}_{EC}=(1-\\varepsilon_{EC})(1-R)+\\varepsilon_{EC}\\) 作为"失败帧整帧
   计入"的现成约定，直接补上 §2.2 的缺口。
3. **低成本（纯算术，不读新数据）**：把 A3 的 Corollary 1 条件
   \\(L=n\\log_2 q/m\\le t\\) 与 \\(R_c\\le1-2\\log_2 q/m\\) 代入当前冻结配置
   （\\(q=32,\\ m=10,\\ N=32768\\)），算出我们落在哪一侧、以及"若要达到无穷 diversity
   需要多少光子每码字"。这是一个**不消耗受保护数据人口**的设计可行性判断。
4. **新增因子**：A3 的 **MFD 性质依赖 Gray labeling 与 \\(m\\)** —— 这是一个仓库从未
   考虑的构造因子，与当前 H2（order/position）因子筛选可能同源，建议作为
   "construction order" 的**理论先验**而非再一轮盲搜。
5. **引用纪律更新**：A1/A2/A3 同属 Soljanin–Boutros 组，C4（Mitra/Dolecek）与 A5
   （Soljanin–Dolecek）亦有交叉 ⇒ 附录 A.4 的"不独立证据组"需从 3 组扩到 4 组。

---

# 附录 C：用户提供的三篇 PDF 原文核实（2026-09-21）

方法：`pdftotext -layout` 提取全文后逐段核对。**附录 A 中标为 unverified 的数字现已
全部核实**，并发现该文贡献比原先认定的更可直接搬用。

## C.1 Müller 2025（IET Quantum Commun. 2025, `10.1049/qtc2.70003`）

### 用户给出的数字：全部准确 ✓

| 量 | 用户表述 | 原文（逐字） | 位置 |
|---|---|---|---|
| 采集时长 | 27 小时 | *"Data was taken continuously for around **27 h** and processed in…"* | 节 3.4 |
| 采集速率 | 约 6.7 kbit/s | *"size over time of acquisition and sifting, was around **6.7 kbit/s**"* | 节 3.4 |
| Cascade 效率 | \\(f=1.036\\) | *"The mean efficiencies of Cascade and LDPC are **f_Cascade = 1.036** and **f_LDPC = 1.166**, respectively."* | 节 3.4 |
| LDPC 效率 | \\(f=1.166\\) | 同上 | 节 3.4 |
| 消息次数 | 446 vs 3.14 | *"The mean numbers of messages are **446 and 3.14**."* | 节 3.4 |
| Cascade FER | <0.003 | *"the frame error rate of Cascade stayed **below 0.003** (evaluated on 1000 samples)"* | 节 3.2 |
| blind LDPC 无错 | 协议内持续揭示直至成功 | *"The blind protocol has **no frame errors by design** apart from syndrome errors, which we did not encounter in this experiment."* | 节 3.4 |

⇒ **用户"不要把 blind LDPC 最终无 frame error 等同于有限预算下的 exact recovery"的
警告，被原文逐字证实**（*by design*）。

### 该文的真实贡献：两级 verification-aware 指标（此前只知其一）

**（a）\\(f_{\\mathrm{FER}}\\)（式 5）** —— 引自 [13,15]，即本附录 B1（Martínez-Mateo 2014）家族：

\\[f_{\\mathrm{FER}}=(1-\\mathrm{FER})\\,f+\\frac{\\mathrm{FER}}{H(p)}\\]

原文解释：*"With probability FER, the error correction fails and we consider **the whole
n bits of the frame to be leaked**. This corresponds to an efficiency of
\\(n/(nH(p))=1/H(p)\\)."*

**（b）\\(f_{\\mathrm{eff}}\\)（式 11 / 13）—— 本文自己提出的新指标**，正是用户建议的
\\(\\lambda_{\\mathrm{total}}\\) 的**精确原版**：

\\[f_{\\mathrm{eff}}=(1-\\mathrm{FER_{cluster}}-P_{\\mathrm{Collision}})\\,f
+\\frac{\\mathrm{FER_{cluster}}+P_{\\mathrm{Collision}}}{H(q)}
+\\frac{t}{n\\,H(q)}\\]

等价地（式 13，乘以 \\(nH(q)\\) 后即为**每帧期望泄漏比特数**）：

\\[nH(q)\\,f_{\\mathrm{eff}}
=(1-\\mathrm{FER_{cluster}}-P_{\\mathrm{Collision}})\\,\\underbrace{\\mathrm{leak_{IR}}}_{\\text{syndrome/reveal}}
+\\underbrace{n(\\mathrm{FER_{cluster}}+P_{\\mathrm{Collision}})}_{\\text{失败帧整帧}}
+\\underbrace{t}_{\\text{验证 tag}}\\]

其中 \\(\\mathrm{FER_{cluster}}=1-(1-\\mathrm{FER})^{k}\\)（\\(k\\)=聚类帧数），
\\(t\\)=EV tag 比特数，\\(P_{\\mathrm{Collision}}\\)=hash 碰撞导致的 EV 失败概率。
原文取值：\\(t=50\\) bits、\\(P_{\\mathrm{Collision}}=10^{-10}\\)。
失败时 *"**all n bits are assumed to be leaked to adhere to security**"*。

⇒ **结论修订（重要）**：§2.2 的 \\(\\lambda_{\\mathrm{total}}\\) 契约**不需要自己发明**，
可直接引用式 (11)/(13) 并注明"推广到 q-ary 时 \\(H(q)\\) 换为经验 \\(H(X|Y)\\)"。
引用链应为：**B1(2014, \\(f_{\\mathrm{FER}}\\)) → Müller 2025(式 11, \\(f_{\\mathrm{eff}}\\))**。

### 可直接搬用的第二个机制：聚类验证 + 允许一次重传

- 单帧验证 vs **多帧聚类后一次验证**（clustered verification）可显著降低 tag 泄漏；
- 还评估了 *"allowing for a **repeat request** for failed frames"*，
  且 *"with **more than 40 frames clustered together being optimal in some cases"*。
⇒ 本仓库 NB-Polar 当前是"每帧一个独立 Toeplitz tag"（`CRITICAL_PATH` step 8、
  `ROADMAP` Phase 5），**Müller 的结果提示"聚类 + 单次重传"可能更省**，
  且这是纯协议层改动，不消耗受保护数据人口。

### 本项目立项依据（该文自己写出的呼吁，最强证据）

原文 Discussion 逐字：

> *"It is worth reiterating that our analysis assumes the channel to follow the
> correlations of a **binary symmetric channel**; that is, locally, in each of the EC
> frames, we assume symmetric transmission probabilities and a constant QBER, such that
> the behaviour is **iid**. **How well the actual channels of QKD devices follow these
> assumptions is still not well researched** (to the best of our knowledge, the only
> mention of a channel model so far is in the case of a **high-dimensional energy-time
> entanglement setup [65, 66]**; a mixture of a uniform and Gaussian distribution is
> proposed as a channel model). … we encourage future work that looks into the issue,
> in particular its impact on **the efficiency measure itself** and the implications of
> channels that are **not memoryless**."*

⇒ 高维 IR 领域当前*唯一*被提及的信道模型案例就是**高维能量-时间纠缠**（我们这类数据），
且作者明确呼吁研究非无记忆信道**对效率指标本身的影响**。这是本项目"经验 \\(P(y|x)\\) +
verification-aware \\(f_{\\mathrm{eff}}\\)"路线最有力的立项引文。

### 其他

- f→净密钥的换算（Figure 11）：*"going from f = 1.0 to f = 1.4 results in a **3%**
  increase in raw key consumption … at 1% QBER, but … **16%** more raw key consumption
  at a QBER of 8%"* —— 可用于论证"效率指标必须在对应 QBER 区间上评估"。
- 参考文献 [27] = Mao, Q. Li, Qi, Guo, *High Throughput and Low Cost LDPC…*
  （即 60 Mbps 那篇，**非被撤稿的 570 Mbps 篇**）→ 该文引用链安全。

## C.2 Zhou 等 AIR（Phys. Rev. Applied 18, 044022 (2022)）

| 量 | 原文 | 状态 |
|---|---|---|
| 效率 | *"the efficiency of the proposed AIR scheme is **1.046**, when the block size is **1 Gb** and the quantum bit error rate of **0.02**"* | ✓ 与摘要一致 |
| 整体失败概率 | *"overall failure probability around \\(10^{-8}\\)"*；实验设定 \\(\\varepsilon_{R_m}=10^{-8}\\) | ✓ |
| 机制 | *"gradually disclosing the bit values of the polarized channels with high error probability"* | ✓ 与 NB-Polar nested disclosure 同构 |
| 实验参数表 | QBER 2%、200 cps、140 ps（双端抖动）、\\(f=1.046\\)、1.200 | 新增，可用于对照 |
| 相对 SLA | *"comparable to the efficiency of the previous SLA scheme, which has to be performed with **4 times larger block size**"* | 新增 |

⇒ 对 NB-Polar 的可搬点：**"渐进揭示高错误概率坐标 + 明确的 \\(\\varepsilon\\) 预算分配
（逐轮 \\(\\varepsilon_i\\)）"**，对应我们 Phase 6 的 nested disclosure；且他们把
failure probability 作为**可分配的一级预算**，本仓库目前只在 outcome 里统计，未做预算分配。

## C.3 Kanitschar & Huber（Phys. Rev. Lett. 135, 010802 (2025)）

原文确认三点（附录 A 原判的适用性下调已由附录 D 推翻、上调为 A 级，见下方更正）：

1. 对象是**纠缠型** HD-QKD：*"paradigmatic high-dimensional systems of **time- or
   frequency-bin entangled photons**"*；方法为 SDP 对偶 + entanglement-witness 启发的
   对角化算子 + **matrix completion**。
2. **finite-size 不在本文**：*"In our **companion paper [40]**, we show how our findings
   can be used to establish finite-size security against coherent attacks"*
   ⇒ 若要 finite-key，必须连带引 [40]（Kanitschar & Huber, *Composable finite-size
   security of HD-QKD protocols*, arXiv）。
3. 本文不含 prepare-and-measure / ToA 探测器的具体建模。

~~⇒ 对本项目 **prepare-and-measure ToA** 数据不可直接套；定位维持"外层框架、待评估"，
且**不得**用于声称我们数据的净密钥安全性。~~

**⚠ 本段已被附录 D 推翻**。更正后的定位：

- **物理层/密钥率外层：直接适用**（我们的数据就是时频纠缠 ToA，见附录 D 证据链）；
- **IR 轴：不覆盖**（原文显式把 \\(H(X|Y)\\) 排除在范围外）⇒ 我们的 \\(\\lambda_{EC}\\)
  恰恰是它的外生输入，**互补而非竞争**；
- **finite-size：须连带引配套 [40]**（本文无）；
- 仍**不得**单独用本文声称我们数据的净密钥安全性——需与我们自己的 \\(\\lambda_{EC}\\)
  及 [40] 的 finite-size 项组合后才成立。

## C.4 由附录 C 触发的改动

1. **附录 A.3 作废**：Müller 2025 数字已核实，删除 `unverified` 标记，改为
   "已核（见附录 C.1）"。
2. **§2.2 契约改为直接引用式 (11)/(13)**，并补 `t`（tag 比特）、
   `P_Collision`、`FER_cluster`（含聚类 k）三项；引用链 B1(2014) → Müller 2025(式 11)。
3. **新增协议层候选**：聚类验证 + 允许一次重传（纯协议改动，零数据消耗）。
4. **立项引文**：使用 C.1 末段 Müller 关于 BSC/iid 假设与非无记忆信道的呼吁原文。
5. ~~Kanitschar 若引用，必须附注"纠缠型 + finite-size 见配套 [40]"。~~
   → 见附录 D：**适用性判定已被推翻并上调**，该项改为"直接适用 + 附注 IR 不在其范围、
   finite-size 见 [40]"。

---

# 附录 D：数据性质核实与 KH25 适用性更正（2026-09-21）

**起因**：用户指出"我们就是时频纠缠测到的到达时间"。经核，附录 A.2 / C.3 中
"本项目是 prepare-and-measure，故 Kanitschar & Huber 2025 不可直接套"的判定
**是错的**。本附录给出证据链与更正。

## D.1 本项目数据性质的仓库证据链（结论：纠缠型，非 P&M）

| 证据 | 位置 | 含义 |
|---|---|---|
| *"PIE measures … per detected photon **coincidence**"* | `docs/SECURITY_MODEL.md:11-13` | **符合计数** = 纠缠光子对探测，非 P&M 脉冲 |
| *"**Time-bin layer**: High-dimensional **arrival-time** encoding"* | `SECURITY_MODEL.md:28` | 高维到达时间编码 |
| *"**Polarization layer**: Additional binary key register (**BBM92-type**)"* | `SECURITY_MODEL.md:29` | **BBM92 是纠缠型协议**（EK/BBM92），不是 BB84 类 P&M |
| *"**Zhong-like** security aggregation"* | `SECURITY_MODEL.md:49-56` | Zhong et al. 2015 = *Photon-efficient QKD using **time-energy entanglement** with HD encoding*, NJP 17, 022002 |
| 引用 Zhong 2015（time-energy entanglement） | `SECURITY_MODEL.md:101`、`RESULTS_INTERPRETATION.md:133` | 物理层基础文献 |
| 数据根 `TypeII_776.1nm_3s` | `AGENT_PROJECT_MEMORY.md:2222`、`ir-method-comparison-state:50,64` | **Type-II SPDC** = 产生纠缠光子对的经典方案 |
| 字段 `coincidence_rate_hz` | `research_cycles/V62P0/v62_polar_reference.json:653` | 符合率 |
| session 名 `type2_1M / 1p5M / 2M` | `AGENT_PROJECT_MEMORY.md:1099-1101` | 同上 |
| *"PIE measures … per detected photon coincidence"* + \\(\\log_2 d\\) bits/coincidence | `RESULTS_INTERPRETATION.md:11-21,76` | 每光子对携带多比特（纠缠特征） |

⇒ **本项目 = Type-II SPDC 时间-能量/时频纠缠光子对的符合测量；Alice/Bob 各测到达时间；
高维 time-bin 层（\\(d\\) 至 1024）+ 偏振层（BBM92 型）。属 entanglement-based HD-QKD
（DO-QKD / TE-QKD 类）。**

## D.2 KH25 与本项目结构的逐字对应（决定性）

KH25 演示系统原文（`docs/nbpolar/PAPER_READ_20260921.md:293-296` 已摘录）：

> *"we demonstrate our method for a typical **high-dimensional temporal entanglement
> setup** … where a source prepares a d-dimensional state
> \\(|\\Psi_1\\rangle=|DD\\rangle\\otimes\\frac{1}{\\sqrt d}\\sum_{k=0}^{d-1}|kk\\rangle\\)
> and Alice and Bob either measure the **time of arrival (ToA)**, denoted as \\(T_T\\),
> or the temporal superposition of (not necessarily) neighboring time bins (\\(T_{\\rm SUP}\\))."*

对照：

| KH25 演示系统 | 本项目 |
|---|---|
| \\(|DD\\rangle\\)（偏振直积/偏振层） | 偏振层，**BBM92-type**（`SECURITY_MODEL.md:29`） |
| \\(\\frac1{\\sqrt d}\\sum_k\|kk\\rangle\\)（时间-bin 最大纠缠） | time-bin 层，高维 arrival-time（`SECURITY_MODEL.md:28`） |
| 测量 \\(T_T\\)（ToA） | **到达时间**测量，本仓库全部数据 |
| 测量 \\(T_{\\rm SUP}\\)（相邻 bin 叠加） | 对应本项目"相位/叠加基"类测量与混淆矩阵的非对角结构 |

⇒ **结构一致**：偏振层 ⊗ 时间-bin 纠缠，测量 ToA 与叠加基。KH25 是为**这类系统**写的。

另两条对我们有利的原文（同文件:313-314）：

- *"Our method works **generically and independently of the physical platform**,
  requiring only **partial information about the density matrix**."*
  ⇒ 只需密度矩阵**部分信息** + matrix completion ⇒ **可直接用我们的实测统计驱动**，
  不必做完整层析。这正是"从实测统计到可计算 HD 密钥率"的接口。
- *"we assume an isotropic noise model … although … this is **only for demonstration
  purposes and we do not rely on any particular noise model**."*
  ⇒ 噪声模型可换成我们的经验 \\(P(y|x)\\)，不受 isotropic 限制。

## D.3 更正后的 KH25 定位

| 维度 | 原判（错） | 更正后 |
|---|---|---|
| 物理层/密钥率外层 | "不可直接套，待评估" | **直接适用**（结构一致，见 D.2） |
| IR 轴 | — （未区分） | **不覆盖**：原文显式 \\(H(X\|Y)\\) 是 *"purely classical … we focus on the first term"* ⇒ 我们的 \\(\\lambda_{EC}\\) 是其**外生输入**，互补 |
| finite-size | "需评估" | **在配套 [40]**（*Composable finite-size security of HD-QKD*），引用须连带 |
| 优先级 | P2 | **A 级**（与 A1/A2/A3 同级） |

## D.4 连带更正：A1/A2/A3 的定位也要升级（风险提示）

由于我们的数据就是 TE-QKD，则 Boutros & Soljanin 那条线**不再是"同源参考/旁证"，
而是同一问题的主流直接文献**。这带来两处必须改的表述风险：

1. **不能再说"没有人在 ToA/高维上做过 IR"** —— A1 (TCOM 2023) 就是做这个的，且 A3
   (2026) 进一步给了 diversity 理论。
2. **创新位必须精确为**（建议的措辞）：
   > 现有 TE-QKD 协调工作（A1/A2/A3）均建立在 **Gaussian jitter + iid + memoryless**
   > 的模型/仿真之上（A3 明确 *"the induced … channel is memoryless under the adopted
   > model"*，且不含 detector dead-time）。本项目的差异在于：使用**真实 Type-II SPDC
   > ToA 数据**、采用**经验 \\(P(y|x)\\)** 取代 QSC/BSC、显式检验**有记忆**假设（A2 的
   > Markov 模型），并把 **verification-aware \\(\\lambda_{\\rm total}\\)、实测 FER、
   > 交互轮次、吞吐/资源**同时计入后比较净密钥。
3. A3 的 Corollary 1（含 GF(q), char 2）与 \\(R_c\\le1-2\\log_2q/m\\) 可直接代入
   \\(q=32,\\ m=10\\) 检验 —— 这是**零数据消耗**的设计可行性判断，建议立即做。

## D.5 应补引的物理层基础文献（本轮调研此前遗漏）

**Zhong, Zhou, et al., *Photon-efficient quantum key distribution using time-energy
entanglement with high-dimensional encoding*, New J. Phys. 17, 022002 (2015)**
—— 已被 `SECURITY_MODEL.md:101` 与 `RESULTS_INTERPRETATION.md:133` 引用，是本项目
"每符合多比特"这一核心特征的原始出处。**此前三轮调研均未把它纳入文献表，属遗漏**，
应补入并作为物理层锚点。
