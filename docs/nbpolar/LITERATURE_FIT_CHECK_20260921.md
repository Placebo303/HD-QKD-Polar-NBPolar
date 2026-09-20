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
| **Kanitschar & Huber 2025**，HD-QKD 分析框架，PRL 135, 010802（P2） | **完全未使用**（零命中） | — | **下调**：纠缠型 HD-QKD（time-/frequency-bin entangled photons），**不能直接套 ToA prepare-and-measure**；仅当其 PM 版框架出现再评估（附录 A.2） | 现有替代：Route A actual-IR finite-key（`CURRENT_MAINLINE.md:88-94`、`tools/security_reports/round2_*`）。NB-Polar 尚未接净密钥；待真实恢复可复现后再引入 |

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

- 不得把 Müller 2025 的二元 BSC 数字外推为 GF32/ToA 证据（`roadmap:246` 已有同样限定）。
- 不得把 blind-LDPC "最终无 frame error" 等同有限预算下的 exact recovery；本仓库
  `undetected` 与 `verify_failed` 必须独立计数（AGENTS.md §5.5）。
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

### Kanitschar & Huber 2025（PRL 135, 010802）— 适用性下调

标题/期刊/DOI 核实无误。**但摘要明确其对象是纠缠型 HD-QKD**（time-/frequency-bin
entangled photons），finite-size 部分在配套另一篇 arXiv（未在此文内）。
→ 对本项目 ToA prepare-and-measure 数据**不能直接套**，前一版报告的"外层密钥率框架"
定位应下调为"待评估：仅当其 PM 版框架出现或自行适配后才可用"。

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

## A.3 Müller 2025 数字：未能核到，处置建议

多次以标题/作者/年份限定检索，SciVerse 全文库**未收录该文正文**，因此用户给出的
`6.7 kbit/s`、`f=1.036 / 1.166`、`446 vs 3.14 messages`、`FER<0.003` **暂时无法用本工具核到**。
处置：在拿到 Wiley OA PDF 原文或用 `read_content` 取得全文前，这些数字在仓库文档中
**必须标为 unverified**，不得进入 claimed-evidence 表格。其**指标体系主张**
（把 error verification、hash、失败帧、额外交互计入 leakage）可安全引用——该主张由摘要
与 CV 站的已知结构支撑，且仓库已有 §2.2 的本土等价物。

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
