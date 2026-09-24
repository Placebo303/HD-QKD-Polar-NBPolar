# T4 决策单（DECISION SHEET）— 2026-09-24 — **DRAFT**

- 性质：**规划输入 DRAFT**。不冻结任何阈值、不授予任何授权、不改变任何状态串、
  不含任何 FER/效率/密钥数字主张。M2 状态保持 `VALIDATED_AT_FROZEN_CONTRACT` 不变；
  `STATE.md`、两份 2026-09-22 草稿、R2 合同草稿、openspec 均不因本文件改变。
- 输入（只读引用，不修改）：`docs/nbpolar/FUTURE_DIRECTION_PLAN_20260924.md`（A2/A3 定义、
  §2 粗算、B0 地板、§3 记分板三级目标提议）；
  `docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md`（C1–C14、§5 15 行 ledger、D2 单向）；
  `openspec/changes/nbpolar-r2-fer-measurement-contract/{proposal,design,tasks}.md`；
  `workspace/probes/a2a3-synth-fcurve/{prereg.md,results.json}`（Tier-X 描述性输入，非证据）；
  `workspace/probes/a2a3-synth-fcurve-n1024/results.json`（Tier-X 描述性输入，非证据，与前任 probe 并列）；
  `workspace/probes/a1a-chain-check/results.json`（链式闭合输入，非证据）。
- **A2/A3 引用纪律（全文件适用）**：既有 Tier-X 观测（A3 operational 192/192 verify_failed；
  A2-SC/A2-SCL8 FER 均值约 0.70–0.83、ΔFER 配对完整，wall 35.27 s）与 A1a 链式闭合
  （B0 地板 f≈1.246/1.265）在本单中**只作为“输入之一、描述性非 claim”**出现，
  用于分辨力量级讨论（§4）与扩样动机说明，**不得当阈值证据、不得驱动 w/n 取值**。
  R2 sizing 的唯一规划点仍是 C9 的 `p=3/14`（R-2 允许的 sizing 用途）。
- T3 状态引用：T3 结构只读评审已回 **STRUCT-PASS**（decision-log 2026-09-24 条目，
  残留 F1–F5 非阻塞）；冻结通过判定在 T4 之后（§8 D3 读法）。
- STATUS 核对时点：两 packet `STATUS.yaml` 状态串与 probe 快照数值的核对时点为 2026-09-24（§4 L105/L110、§10-8/9）。

---

## §1 S0–S9 最小收敛序列（10 步；按序执行，后一步以前一步输出为输入）

| Step | 目标 | Owner | 输入 | 输出 |
|---|---|---|---|---|
| S0 | 范围锁定：确认本单只裁 R2 单方法 FER 测量所需项，强版本外移（§9） | 主线程 | §9 范围表 | S0 范围声明（DECIDED/DEFERRED 边界） |
| S1 | 陈述最小可分辨差异 Δ（不预设数值，只定候选档位见 §4） | PI | §4 档位表 + C9 规划点 | S1 Δ 候选值（进 §3 模板） |
| S2 | 由 Δ 单向导出目标半宽 w（两种读法并列，见 §3；换算式本身仍 PENDING，P5） | PI | S1 Δ + §3 模板 | S2 w（必须等于导出值；不一致按冲突上报，D2） |
| S3 | 由 w 导出样本量 n（正态近似 + Wilson 精确复核，D-FER-01/02/03） | PI（算术由 planner 备） | S2 w + §3 复核式 | S3 n（冻结值） |
| S4 | 由 n 算术导出配额 quota（frames×pairs，T5；128 frames/block） | planner 备算 → PI 认 | S3 n + C10/C11 | S4 quota（纯算术记录） |
| S5 | 预算对账：S4 配额 vs C13 预算（D-ACQ-06）；冲突上报不权衡 | PI | S4 quota + D-ACQ-06 预算数 | S5 通过 / 冲突上报（D-ACQ-06 式升级） |
| S6 | 分支/源/预留/工作点落位（D-ACQ-01/02/03/05、Type0 D-ACQ-04、sessions D-ACQ-08） | PI | C10/C11/C12 + ledger 选项（§2） | S6 DECIDED/DEFERRED 行 |
| S7 | 记账与读数口径落位（D-FER-04/05/07；C6/C7 记为事后约定不测量，D6） | PI | C6/C7/C8 + §2 选项 | S7 DECIDED/DEFERRED 行 |
| S8 | 升级与继承落位：`undetected>0`（D-FER-06）、配对/构造沿用（D-ACQ-07）、Annex 形态（§7）、R-5 处置（§6）、D3 读法确认（§8） | PI | C4/C14 + §6/§7/§8 | S8 DECIDED/DEFERRED 行 |
| S9 | 冻结 verdict：仅 `DECIDED` 行进冻结正文；`DEFERRED` 进 open-decision 表；随后才可 T5/T6 | PI + 独立冻结评审 | S0–S8 全部输出 | S9 冻结通过 / 冻结阻塞（未裁定行清单） |

注：S0 Owner“主线程”指 main thread（范围裁决方），非执行子代理。

---

## §2 15 行 ledger 逐行选项表（状态全 PENDING；本单只给选项，不自裁）

列：`ID | clause | question | Owner | 输入 | 输出 | 选项`。选项字母仅为讨论桩，无推荐效力。

| ID | clause | question | Owner | 输入 | 输出 | 选项 |
|---|---|---|---|---|---|---|
| D-FER-01 | C3 | CI 方法 | PI | G2/G3 Wilson 连续性 | DECIDED/DEFERRED | (a) Wilson z=1.96（草稿立场）；(b) Clopper-Pearson exact（更宽，破可比性）；(c) DEFERRED（retrigger=冻结前） |
| D-FER-02 | C9/D2 | 目标半宽 w | PI | S1 Δ + §3 模板 | DECIDED（必须等于 Δ 导出值） | (a) 取 §3 导出 w；(b) 与导出不一致→按 D2 作冲突上报（非选项值）；(c) DEFERRED（阻塞 S3–S5） |
| D-FER-03 | C9 | 样本量 n | PI | S2 w + Wilson 复核 | DECIDED | (a) 正态近似 + Wilson 复核值（§3 表）；(b) 直接定 Wilson 精确 n（须给出算式）；(c) DEFERRED（阻塞 S4） |
| D-FER-04 | C6 | H(q)→经验 H(X\|Y) 替换口径 | PI | 估计源/样本/偏差处理提案 | DECIDED/DEFERRED/NOT_APPLICABLE | (a) 预注册具体口径进冻结正文；(b) DEFERRED（R2 不启用替换，C6 记约定）；(c) NOT_APPLICABLE（R2 明确不用） |
| D-FER-05 | C7 | f_FER 记账式冻结 | PI | Martínez-Mateo→Müller eq(11)/(13) 指向 | DECIDED/DEFERRED | (a) 冻结记账式（项级待 R3）；(b) DEFERRED（本合同仅记约定不测量，D6） |
| D-FER-06 | C4/C14 | undetected>0 升级规则 | PI | C4 隔离语义 | DECIDED | (a) STOP+上报；(b) 单列记录继续（须写明条件）；(c) DEFERRED（retrigger=首现 undetected 时） |
| D-FER-07 | C8 | per-frame 派生读数允许条件 | PI | R-1 单位（C2） | DECIDED/DEFERRED/NOT_APPLICABLE | (a) 默认不允许（草稿立场）；(b) 允许须预注册的例外条件；(c) NOT_APPLICABLE |
| D-ACQ-01 | C10 | 执行分支 A/A′/B 与目标 n、w | PI | S3 n + §4 档位 | DECIDED | (a) Branch A（50–100）；(b) Branch A′（~260，w=±0.05 时）；(c) Branch B 记 R3 不 sizing |
| D-ACQ-02 | C10 | 采集源清单 | PI | 解析后 ledger | DECIDED/DEFERRED | (a) SHG 新采清单；(b) 候选 Type-II（单列与否见 D-ACQ-04）；(c) DEFERRED（等 ledger） |
| D-ACQ-03 | C11 | 每 acquisition 预留段配额 | PI | G3 模式参考（1024/32/782/560，未冻结） | DECIDED/DEFERRED | (a) 五段具体帧数；(b) DEFERRED（T5 前必须定） |
| D-ACQ-04 | C11 | Type0 纳入与否及报告方式 | PI | source-only 裁定兼容 | DECIDED | (a) 不纳入（草稿默认）；(b) 纳入但一律单列（不混算 FER） |
| D-ACQ-05 | C12 | 噪声/工作点可接受差异带 | PI | SHG 可比基线 | DECIDED/DEFERRED | (a) 差异带数值+声明制；(b) DEFERRED（closure 声明制先行） |
| D-ACQ-06 | C13 | 预算数（单块/总 wall/RSS） | PI | G2/G3 包络（量级参考，未冻结） | DECIDED | (a) 具体预算数；(b) 与 S4 配额冲突→上报 PI（D2 step 4） |
| D-ACQ-07 | C14 | 配对/构造契约沿用 | PI | 冻结契约 W_P/W_S/MOD/skip/K1/K2/P16 | DECIDED | (a) 继承冻结契约；(b) 偏离→单独立项（本单不立项） |
| D-ACQ-08 | C13 | 独立 session 最低会话数（≥2） | PI | 路线图 R1 门 | DECIDED/DEFERRED | (a) ≥2 与 R2 同批满足；(b) DEFERRED（R2 单 session + 后续复现） |

附加待 PI 项（不在 15 行内，T4 一并落位）：最小可分辨差异 Δ 本体；K_total fixed-f vs fixed-K 约定（§5）；
P1（ACQ §8 归位目标=C12）与 P2 其余 STOP 规则（归位目标=C13）占位裁定；w(Δ) 换算式 P5 本体。

---

## §3 Δ→w→n 模板（两种读法并列；换算式 PENDING，本单不自造公式）

- 常数（C9 冻结前沿用）：规划点 `p=3/14`，`pq=33/196≈0.1683673`，`z=1.96`，
  `C=z²·pq≈0.64680`，正态近似 `n≈C/w²`；冻结时以 Wilson 精确式复核（D-FER-01）。
- 读法 R-a（单臂口径）：`w=Δ`（目标半宽直接等于可分辨差异）。
- 读法 R-b（双臂比较口径）：`w=Δ/2`（分辨 Δ 需半宽取半；n 为 R-a 的 4 倍）。
- D2 单向纪律：Δ→w→n→quota；D-FER-02 值必须等于导出 w，不一致作冲突上报，
  永不倒推重述 Δ；预算冲突（D-ACQ-06）同样上报不权衡。

| Δ 候选 | R-a: w=Δ → n≈C/w² | R-b: w=Δ/2 → n≈4C/Δ² | 分支含义 |
|---|---|---|---|
| 0.114 | w=0.114 → **50**（49.8→50） | w=0.057 → **200**（199.1→200） | R-a 落 Branch A 下限；R-b 需 A′/另议 |
| 0.100 | w=0.100 → **65**（64.7→65） | w=0.050 → **259**（258.7→259） | R-a 落 Branch A；R-b 出 Branch A（A′量级） |
| 0.080 | w=0.080 → **≈100**（算术 101→取整 100，沿 C9） | w=0.040 → **≈405**（404.3→405） | R-a 为路线图上限；R-b 远超 R2 量级 |
| 0.050 | w=0.050 → **259**（258.7→259） | w=0.025 → **≈1035**（1034.9→1035） | R-a 已需 Branch A′（PI 另决）；R-b 属 R3 量级 |

Wilson 复核行（冻结时填）：`n_Wilson(Δ,读法,p̂,z)=____`；若与上表差≥5 块，以 Wilson 为准并记录算式。
`COMPLETE-BLOCKS-ONLY`：closure 完整 EVAL 块不足→`INSUFFICIENT`→INCONCLUSIVE，永不垫块/复用/缩 N。

---

## §4 候选 Δ 档位与分辨力讨论（A2/A3 仅描述性输入，非证据）

- 档位沿 C9 四档（0.114/0.100/0.080/0.050），对应 R-a 之 n≈50/65/100/259（§3）。
- R2 适用的现实区间：Branch A（50–100）⇔ R-a 下 Δ∈[0.080,0.114]；
  Δ=0.050（R-a n=259）已出 Branch A，需 Branch A′（PI 另决）；R-b 下全部四档
  n≥200，均出 Branch A——若 PI 采用 R-b 口径，须同步裁定分支与预算（S5/S6）。
- A2/A3 描述性注记（**非 claim、非阈值证据**，仅量级参照）：
  既有合成 Tier-X（F4@q=1024、N=256、seeds 4、16 blocks/cell）观测到配对 ΔFER 均值
  约 +0.17/+0.19（f=1.10）、+0.25/+0.27（f=1.15）、+0.30/+0.28（f=1.20)（A3−A2，
  SC/SCL8 两读法），种子间 sample-std 约 0.14–0.20；A3 operational 192/192 verify_failed。
  **解读禁令**：该量级若视为“待分辨效应”的假想尺度，则 Δ=0.100–0.114 档（R-a）
  在量级上可覆盖之，Δ=0.050 档则远严于所需——但此对照**不构成** Δ 取值的理由：
  合成信道≠真实信道、N=256≠N=32768、A3 当前形态≠R2 被测方法；Δ 仍须由 PI 按真实
  科学问题陈述（S1），不得引用本段作证据。
  N=1024 合成 Tier-X 追加观测（**同样描述性非 claim、非阈值证据**，来源 `workspace/probes/a2a3-synth-fcurve-n1024/results.json`：N=1024、8 seeds×16 blocks×3 f 点、one-shot reruns=0，wall 344.1 s，RSS 368 MiB；冻结门 DP-1..DP-8 已闭合（`workspace/a2a3-exp-packet/STATUS.yaml`，核对时点 2026-09-24））：
  A3 operational 臂 384/384 verify_failed，且 oracle 臂（genie 真高层）同样 384/384——暂仅否定“披露集/高层选择为唯一原因”的解释；究竟是低层码/校验机制还是码率不够，待 a3-op-scan 分离（描述性）；
  A2 FER：f=1.10 SC/SCL8 均 1.0000；f=1.15 为 0.969±0.033 / 0.945±0.052；f=1.20 为 0.953±0.044 / 0.906±0.075——该合成配置（N=256/1024，F4，f≤1.2）下未观测到恢复；
  配对 ΔFER（A3−A2）：f=1.10 为 0；f=1.15 为 +0.031/+0.055；f=1.20 为 +0.047/+0.094（SC/SCL8），随 f 扩大；
  以上合成观测仍不得作为 Δ 取值或阈值证据（解读禁令不变）；A1a 链式闭合（地板 1.246/1.265）注记不变。
  a3-op-scan 追加观测（**同样描述性非 claim、禁作Δ/阈值证据**，来源 `workspace/probes/a3-op-scan/results.json`：Tier-X，N=1024，6 f 点 {1.30,1.40,1.60,1.80,2.20,2.80}×8 seeds×16 blocks=768 块，48/48，wall 658.09 s，RSS 0.36 GiB，reruns=0，status ok）：
  A2-SC FER 均值：f=1.30→0.8125，f=1.40→≈0.5312（约值，截断），f=1.60→≈0.1562（约值，截断），f=1.80→0.0234，f=2.20→0，f=2.80→0（SCL8 同步，对照健康）；
  A3op FER 均值：f=1.30–2.20 全 1.0000，f=2.80→0.9531；
  A3op exact：f≤2.20 合计 0/640，f=2.80 为 6/128（seed 分布 2404×1/2405×1/2407×2/2408×2，其余 4 seeds（2401/02/03/2406）为 0），总计 6/768；
  oracle exact：f=2.20 为 12/128，f=2.80 为 122/128，总计 134/768；
  undetected=0 全局隔离；decode_failed/resource_abort 全零；divergence defined 768/true 759 report-only；
  operational首次成功落在(2.20,2.80]，oracle先行；f≤2.20五点0/640与f=2.80的6/128共同构成‘结构性失败vs码率不够’分离的描述性输入 (非证据)；A2对照健康 (f=2.20/2.80零误)。
- A1a 描述性注记（非证据）：链式闭合确认 B0 地板 f≈1.246（f2=1）/1.265（f2=2）；
  若 R2 目标 f 区间定在地板之上，测量只能复述平凡方案——目标区间归 §9/未来规划，
  本单不裁 f 目标。

---

## §5 K_total fixed-f vs fixed-K（T4“Plus”项）

| Owner | 输入 | 输出 | 选项 |
|---|---|---|---|
| PI | D4 report-only 记录 + decision-log 2026-09-22 两条目 | DECIDED（冻结约定）/ DEFERRED | (a) **fixed-f=1.3**（PI 2026-09-22 已选为未来 rate-freeze 规划方向：K_total **6946**→335/6611，f=1.2999641，偏差 −3.59e-5 即 R5 floor loss；生效仍须独立 rate-freeze 包+评审+授权，此前仅规划方向）；(b) fixed-K（6811→328/6483，f=1.2747449，作规划对照保留）；(c) DEFERRED（G2/G3 仍冻 319/6492，R2 若不涉及重分配可暂缓，但须显式记录） |

约束：冻结 K1/K2 前任何 rebalance 必须声明取 fixed-f 还是 fixed-K（MACRO_PLAN §9 F6）；
预算字面式 `K_total=floor((f·N·H−64)/5)` 中的 H 须用冻结口径（经验 H 替换见 D-FER-04）。

---

## §6 R-5（来源不可得；PI 移除或补定义）

| Owner | 输入 | 输出 | 选项 |
|---|---|---|---|
| PI | 合同 §0 P9（全仓 grep：仅 FER 草稿:6 列举，正文无定义） | DECIDED（移除/补定义）/ DEFERRED | (a) 从红线清单**移除** R-5（§7 映射表同步删行）；(b) **补定义**（须单独立项给出来源与语义，本单不发明）；(c) DEFERRED（retrigger=有源定义出现时；期间 §7 该行保持“来源不可得、待 PI”原样） |

纪律：本合同不虚构 R-5 内容；T3 不以无源红线 auto-FAIL（tasks T3 已固化升级路径）。

---

## §7 Annex 形态（D1：FER 正文 + ACQ Annex A）

| Owner | 输入 | 输出 | 落位 |
|---|---|---|---|
| PI（形态确认） | 两份 2026-09-22 草稿 + D1 | DECIDED（形态） | FER 草稿供**规范正文**；ACQ 草稿**降级为 Annex A**，只供参数不重定义 FER 语义；P1（ACQ §8→目标 C12）、P2 余项 STOP（→目标 C13）为显式占位，裁定前 Annex-only、正文不部分引用；两矩阵相异（C11 reservation-partition vs §4 clause-provenance）不得混同 |

---

## §8 D3 读法（已固化，按此执行；冲突上报主线程）

- 采用读法：design D3「未裁定行 blocks T3」读作**阻塞冻结判定**（T3 在全 PENDING 下
  照常做结构只读评审，可给结构 PASS/FAIL，但不得判冻结通过；冻结通过在 T4 后判定）。
  T3 STRUCT-PASS 已按此标准作出（全 PENDING 下的结构 PASS，非冻结通过）。
- 对立读法（未裁定行阻塞 T3 评审本身，即 T4→T3 改序）属 design/tasks 冲突，
  **上报主线程裁定**，本单/合同不自行改序（合同页首与 §8 第 0 条已载明）。
- Owner/输入/输出：Owner=主线程（冲突裁决）；输入=design D3 + tasks T3 + 合同页首；
  输出=维持现序（T3→T4）或改序指令（若改序，本单 S0–S9 须返工，T3 结论复核）。

---

## §9 强版本范围（建议 R2 取单方法 FER；强版本外移）

| 范围 | 处置 | Owner/输入/输出 |
|---|---|---|
| R2 本体：**单方法 FER**（被测方法 operational 臂；FER 定义 C2 + Wilson C3 + taxonomy/隔离 C4/C5 + 样本配额 C9–C11 + 预算 C13） | T4 冻结 | Owner=PI；输入=C1–C5/C9–C13 + §2 行；输出=冻结正文 |
| 配对方法比较（ΔFER、McNemar 等；H2 原生优势类主张） | **外移**（R2 后续立项或论文项；R2 数据若复用须 ledger 永不回流约束下另裁） | Owner=PI；输入=未来规划 H2；输出=DEFERRED（retrigger=配对设计单独立项） |
| 效率/净密钥（C6/C7 Stage-3 机械、f_eff、PIE_rec、M-usable/competitive/strong） | **外移** R3（本合同仅记约定不测量，D6） | Owner=PI；输入=§3 记分板提议；输出=DEFERRED/NOT_APPLICABLE 于 R2 |
| FER<0.003 / ~1000 blocks（Branch B，R-3） | **外移** R3（C9 边界 + C10 后果已承载，不作 R2 sizing） | Owner=PI；输入=C9/C10；输出=记为 aspiration，不 sizing |
| ≥2 sessions 同批满足（D-ACQ-08 强版本） | 可外移（R2 单 session + 后续复现，或同批满足二选一，见 §2） | Owner=PI；输入=C13/D-ACQ-08；输出=DECIDED/DEFERRED |
| per-frame 派生读数作 claim（D-FER-07 强版本） | 外移或禁止（默认不允许，§2） | Owner=PI；输出=DECIDED（默认禁）/NOT_APPLICABLE |
| 真实数据 f 目标区间重定（f≤1.3→f_eff≤1.20/1.12 类提议） | **外移**（属未来规划 §3/§9 第 2 项，需 OpenSpec/PI 另议，本单不裁） | Owner=PI；输出=本单不裁，记为后续项 |

---

## §10 主线程裁定点清单（本单执行前须逐项裁决或显式 DEFERRED）

1. Δ 本体取值 + w 读法（R-a vs R-b）二选一（S1/S2；阻塞 S3–S5）。
2. K_total 约定（§5 三选一；阻塞任何重分配）。
3. R-5 移除/补定义/DEFERRED（§6）。
4. Annex 形态确认 + P1/P2 占位归位（§7；阻塞 T2 写入）。
5. D3 读法维持现序（§8；若改序返工）。
6. 强版本范围确认（§9；阻塞 S0）。
7. w(Δ) 换算式 P5 本体（冻结时给出显式公式；本单模板只作算术示例）。
8. A2/A3 扩样 packet（`workspace/a2a3-exp-packet/`，STATUS=READY_FOR_EXECUTE，已冻结，freeze ruling 2026-09-24；已执行快照：`workspace/probes/a2a3-synth-fcurve-n1024/results.json` status ok，probe_runs 1，wall 344.05 s）——与本单 §4 无关（扩样为合成 Tier-X，不消耗任何 R2 配额/预算）；与 S0–S9/S9 冻结判定无依赖。
9. A3 工作点诊断 scan（`workspace/a3-scan-packet/`，probe a3-op-scan：同信道/配对/N=1024，只扩 f 网格 [1.30,1.40,1.60,1.80,2.20,2.80]；STATUS=READY_FOR_EXECUTE，已冻结，freeze ruling 2026-09-24，核对时点 2026-09-24）——同为合成 Tier-X，不消耗任何 R2 配额/预算；与 S0–S9/S9 冻结判定无依赖；目的：分离 A3 结构性失败 vs 码率不够；已执行 status ok, 48/48, wall 658.09s (核对时点2026-09-24)。

*本文件为 DRAFT 规划输入：不授权执行、不改变状态、不含数字主张。T4 裁定后由 T2 落表、
T5 算术、T6 空骨架（`authorizations: []`）；T7–T9 仍 NOT AUTHORIZED。*
