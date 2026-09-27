# 下一 L2 探针设计（NEXT L2 PROBE）— 2026-09-25 — **DRAFT**

- 性质：**规划输入 DRAFT**。不冻结任何阈值/参数/种子，不授予任何执行授权，
  不改变任何状态串，不含任何 FER/效率/密钥数字主张，不作 R2 sizing 输入。
- 输入（只读引用，不修改）：
  `workspace/probes/l2-singlefactor-k200/{prereg.md,results.json}`（Tier-X，已冻结执行完，非 claim）；
  `workspace/probes/k2-dose-ramp/results.json`（Tier-X，量级参照，非阈值证据）；
  `workspace/probes/oracle-l2-fulldisclosure/results.json`（通路 sanity，非证据）；
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/construction.py:99`
  `disclosure_order_from_stats(e,h)`（冻结生产排序函数）；
  `docs/nbpolar/T4_DECISION_SHEET_20260924.md` §4（L-H 标签纪律、k2-ramp 描述性段）；
  `docs/nbpolar/PROBE_TIER.md`（Tier-X 模板）；`docs/nbpolar/STATE.md` §4（冻结/预算）。
- 标签纪律：本文件探针局部倾向/排除一律记 `L-H1/L-H2/L-H3`（单探针内描述性形态，
  非 verdict、非证据）；项目级 `H1/H2/H3` 不受本文件任何语句证实或证伪。

## Goal / Non-Goals / Impact Scope

- **Goal**：为“`l2-singlefactor-k200` 效力不足之后，下一步如何做出有判别力的
  L2 构造单因子探针”给出可冻结的 Tier-X 合成设计（另起 packet），只解决两个
  效力问题：对比度（低重合 BASE vs CAND）与非地板工作点。
- **Non-Goals**：不裁决构造排序优劣；不证实/证伪项目级 H2；不解锁 SCL；
  不升级为 R2/高维优势 claim；不重跑本次探针；不做任何真实数据动作。
- **Impact Scope**：仅新建本文档 + 未来新 packet（`workspace/probes/<new-id>/` +
  `workspace/<new-packet>/`）。不改 `results/`、`comparison_bench/outputs_comparison/`、
  `src/`、`STATE.md`、任何已冻结 `results.json`/`prereg.md`、任何状态串。

---

## §1 本次结论边界（`l2-singlefactor-k200`，冻结数原文引用）

冻结执行快照（`results.json`，status=`ok`，`probe_runs=1`，`reruns=0`，
`wall=71.23 s`，`RSS≈204 MiB`，one-shot 已耗尽）：

- 五固定：N=1024 / F4@q1024 与 M2 先验 / run seeds `2026092401..2026092402` /
  k2=200（`disclosed=1050 bits`，`f_book≈1.10041`，tag excluded）/
  SC-oracle 解码器不变 / `toeplitz_master=2026091361`。
- 一换 d2：BASE=`worst_k(H2,200)`（`L2-BASE-P16-FROZEN`）vs
  CAND=`sorted(disclosure_order_from_stats(e2,h2)[:200])`（`L2-CAND-PRODORDER-01`，
  e-first，`construction.py:99` 冻结函数；`H2`=行 Shannon 熵，`h`=真值处交叉熵，二者不等）。
- 读数（描述性，非 claim）：
  BASE 与 CAND oracle-L2 exact 均 **0/32**（per-seed 各 0/16）；
  operational k1=10 两臂 FER 均 **1.0**（`verify_failed` 32/32）；
  `undetected=0` 全局隔离（永不并入 success/FER）；`decode_failed`/`resource_abort` 均为 0。
- 设计阶段强制读数：d2 两集重合 **199/200**（`Jaccard≈0.990`，`identical=false`），仅差 1 位。

结论边界（reviewer 判定原文转述，主线程已接受）：

1. **检验效力≈0**：在仅 1 位差异 + k2=200 地板点（两臂 oracle 0/32，方差为 0）
   下，本探针只能支持“在这 1 位差异 + 该地板点下无可辨分离”这一描述性陈述。
2. **不得下构造排序无效结论**：e-first vs H-first 是否等价/无效，本次无权回答。
3. **不得单独归因 L-H1**：PI 归因收紧要求仍有效——operational 与 oracle 两臂
   同失败 ⇒ 先验失配不是可单独归因的解释；不得把探针倾向写成已证实/证伪
   项目级 H2（`FUTURE_DIRECTION_PLAN §5`）。
4. 可陈述的只有：per-seed 计数（0/16 × 2 seeds × 2 臂）、合计（0/32 × 2 臂）、
   重合度（199/200，Jaccard≈0.990）、预算与 one-shot 状态。禁止显著性措辞、
   禁止 Wilson CI、禁止记分板行、禁止 R2 sizing 输入。
5. 历史 `results.json` 数值不动；本文件任何“下一步”设想不得回写为本次探针的结论。

---

## §2 下一探针设计（Tier-X 合成，另起 packet）

总约束：synthetic-only Tier-X（`AGENTS.md` §10.4 + `PROBE_TIER.md`）；
输出根仅 `workspace/probes/<new-id>/`（`prereg.md` 三行 + 单一 `results.json`）；
配对复用（同一 `(seed,block)` 的 `(x,y)` 跨两臂复用）；`undetected` 隔离永不并入；
`reruns=0` one-shot；focused numerical review，不做 Pre-EXECUTE/Pre-RESULT；
不消耗 R2 配额/预算；禁写 `results/`、`outputs_comparison/`、`src/`、`STATE.md`；
禁读 sibling checkout；无真实/artifact 数据。

### §2a 对比度：如何做出低重合的 BASE vs CAND 对

问题：本次 `e-first[:200]` 与 `worst_k(H2,200)` 重合 199/200。
在同一批 MC 行、同一预算下，e 与 H2 的 top-200 几乎同序 ⇒ 该 CAND 无对比度。
下一探针必须先过“设计阶段重合度门”再谈测量：`prereg` 强制要求先产出
`d2_overlap_count / Jaccard / identical`，`identical=true` 则记
`non_discriminating` 并在测量前停止（仍属一次运行、一条记录，不调参不换构造）；
新增建议门：`overlap ≥ 180/200`（Jaccard ≥ ~0.82）即判对比度不足，停止测量、
如实上报（阈值本身待 §6 DP-N1 裁定，本文件只提议）。

候选方案（全部“不得手写新排序”；只能用冻结函数或已冻结规则；
若必须新规则则单列为“发明”，见本节末）：

| ID | BASE | CAND（取 top-k 的全序来源） | 冻结依据 | 重合度预估方式（执行前算，不动手调） |
|---|---|---|---|---|
| C1（推荐首选） | `worst_k(H2,200)` 不变 | `best_k(H2,200)`（H2 升序前 200，即披露价值最低集；反向对照） | `worst_k`/`best_k` 均为已冻结 probe-local 规则（k2-ramp/dose 系列同族） | 设计阶段直接算 `\|BASE∩CAND\|` 与 Jaccard；预期接近 0（两端对立），若仍高则说明 H2 分布病态，探针停测即本身就是发现 |
| C2 | 同上 | `disclosure_order_from_stats(e2,h2)[N-200:]` 的 sorted 集（e-last 200，即 e 序尾部） | 同一冻结函数 `construction.py:99`，仅取尾部（调用方切片位置变化，无新排序逻辑） | 同上直接算重合度；预期低重合（头 vs 尾）；若头尾仍高重合，停测上报 |
| C3 | 同上 | `disclosure_order_from_stats(h2,e2)[:200]`（h-first：交换 e/h 主次键；注意这**不是**新排序函数，只是同一冻结函数换参顺序） | 冻结函数签名 `(e,h)` 允许任意两个同长向量；`h2`/`e2` 均为同一批 MC 行已产出量 | 同上直接算；预期中等偏低重合（主键 changed）；是否足够判别由重合度门裁定 |
| C4（边界对照） | 同上 | 固定伪随机 200 集（`default_rng([design_seed, 0xCA9D])` 置换 `arange(N)` 取前 200；与信道无关的零信息对照） | 非排序函数，无需冻结排序语义；随机集生成规则写死在 prereg，种子冻结 | 重合度期望 `200·200/1024 ≈ 39`（超几何均值），Jaccard 期望约 `39/361 ≈ 0.108`；实测值设计阶段直接算 |

说明：

- C1–C3 的重合度**不是模型预测**，而是“设计阶段强制读数”：用同一批
  design MC 行（`design_seed`、`DESIGN_MC` 冻结值待新 packet 裁定，不得沿用旧值作默认）
  实际算出两集交集后才决定是否进入测量。预估方式 = 直接计数，无需功效公式。
- C4 的 `≈39` 只是超几何均值（`E=200²/1024`），用于判断实测重合是否异常，
  不作阈值证据、不驱动工作点。
- 禁止项：操作员不得手写任何新的 `(e,h)→order` 组合逻辑（如加权和、乘积、
  分位数混合）；不得复制 `disclosure_order_from_stats` 实现到 probe 脚本，
  必须只读导入冻结路径。
- **“发明”单列（需 PI 裁定，默认不采用）**：
  I-1：任何 `α·e + β·h` 或 `e^a·h^b` 混合排序；I-2：按 `h−H2` 差值排序；
  I-3：按 plane 分层抽样的混合集。以上任一若被 PI 选中，须单独立项说明语义、
  冻结权重，并在 `cand_def.declaration` 中标 `INVENTED-NOT-FROZEN`，不得与
  C1–C4 混批执行。

### §2b 非地板工作点：k2=200 无方差即无判别力

冻结参照（`k2-dose-ramp`，`status=ok`，128 块，`wall=97.17 s`，`RSS≈207 MiB`）：

- `disclosed={1050,2050,3550,5170}` bits，`f_book≈{1.10041,2.14841,3.72042,5.41819}`；
- oracle exact 率：k2=200 为 **0/32**（per-seed 各 0/16），k2=400 为 **2/32**
  （per-seed 各 1/16），k2=700/1024 各 **32/32**（per-seed 各 16/16）；
- operational 四点均为 0/32（FER 1.0 平坦）；`undetected=0`；以上皆描述性，
  禁作 Δ/阈值证据（`T4_DECISION_SHEET` §4）。

论证：

1. 地板点无方差即无判别力：k2=200 两臂 oracle 均为 0/32 ⇒ 臂间差恒为 0，
   样本标准差 0、范围 [0,0]。在该点上无论 d2 差异多大（即使 0 重合），
   oracle 读数都无法分离 ⇒ 该点对“构造排序”问题的信息量为零。
   （限定：该“无论差异多大/信息量为零”判断只在本次观测的两集（重合 199/200）
   语境下成立；PI 2026-09-25 裁定：0/32 是这批样本的观测，不得外推为
   “信息集差异足够大时仍无法分离”，若信息集差异足够大，地板结论未必成立。）
   本次恰叠加了“1 位差异 + 地板点”双重效力杀手。
2. 饱和点同样无判别力：k2=700/1024 oracle 32/32 ⇒ 差亦恒为 0（天花板）。
   （限定：该判断只在本次观测的两集（重合 199/200）语境下成立；
   PI 2026-09-25 裁定：32/32 是这批样本的观测，若信息集差异足够大，
   天花板结论未必成立。）
3. 唯一有方差的已测点是 **k2=400（2/32，per-seed 各 1/16）**：非 0 非饱和，
   是当前唯一观测到 oracle 成功的剂量点。判别力要求“基线非平凡”
   （基线成功率严格位于 (0,1) 内），否则任何对比都是 0−0 或 1−1。
4. 结论（PI 2026-09-25 裁定，替换原 k2=400 单点 + 备用点方案）：
   PI 2026-09-25 裁定：下一探针选 k2=550 单点，无备用点；披露 2800 bits，
   f_book≈2.93441，仅用于机制诊断。k2=550 是依据 400 与 700 两端读数选的
   未测插值点，不得预称“非地板点”，不得作为实用效率点。
   若 k2=550 仍落在地板或天花板（两臂全 0 或全成功），如实结束本次探针，
   不临场改点或加样。原“k2=400 单点（`disclosed=2050 bits`，
   `f_book≈2.14841`）+ 备用点 500 或 550 二选一、上限 2 点”方案作废；
   PI 裁定无备用点；备用点是否启用不再待裁，不得在执行中自行加码。
   （依据注记：k2=400 仍是当前唯一已观测到 oracle 非零方差的已测点
   （2/32，per-seed 各 1/16），k2=700/1024 为 32/32，两端读数仅作选点量级依据。）
5. 禁止把 k2-ramp 的 2/32 读作“400 点保证有分离”：它是另一 packet 的描述性
   输入（不同 d2 定义、不同设计种子语境），仅作工作点选择的量级依据。

---

## §3 种子数/块数的最小可行估计（定性，不编造功率分析）

- 不做事项：不编造显著性水平 α、功效 1−β、正态近似 n 公式；Tier-X 禁止
  Wilson CI 与显著性措辞（`PROBE_TIER.md`）。
- 定性论证（只给下界直觉，不给保证）：
  - k2=200 地板：无论多少块，期望观测差为 0（0/32 的外推是描述性外推，
    非断言）。加块不增加判别力 ⇒ 不得在 200 点上“扩样补效力”。
  - k2=400 量级：基线约 2/32 ≈ 6%。若两臂真差为“几个百分点”量级，
    则每组几十块内大概率观测到全零差（`0.94^32 ≈ 14%` 全零概率量级的心算参照，
    非功效声明）。因此**每组 <32 块不具备观测非零差异的现实机会**；
    最小可行起点为 **2 seeds × 16 blocks = 32 块/臂**（沿用前任配对结构），
    上限 **4 seeds × 16 blocks = 64 块/臂**（预算内，见下）。
  - 若 32 块/臂下两臂仍全零（0/32 vs 0/32），结论仍是“在该点无可辨分离”，
    不得追补种子/块数（one-shot 纪律）。
- 预算约束（沿用前任包络，待新 packet 冻结）：
  `wall ≤ 200 s` 且 `RSS ≤ 1 GiB`（前任实测：singlefactor 71 s/204 MiB；
  k2-ramp 97 s/207 MiB；oracle 全披露 53 s）。64 块/臂 × 2 臂 × 2 解码臂
  （oracle + operational k1=10 次要列）的量级与前任同阶，预计不超界；
  每块 + 每 32 design 样本检查，超界即停 `status=incomplete`，不调参。
- 最终种子数/块数由 §6 DP-N3 裁定（二选一：32/臂 或 64/臂），冻结后不得改。

---

## §4 判读规则（ACC 判据；预注册，描述性，非显著性检验）

以下判据写入新 packet 的 `prereg.md`（Q/P/C），`results.json` 只报告计数组，
不写 verdict 词。

- 主要读数：oracle-L2 exact 率（per-seed 计数 + 合计 + 均值/样本标准差(n−1)/范围）。
  次要读数：operational k1=10 单列（同结构报告，不作 claim）。
  强制读数：`d2_overlap_count / Jaccard / identical`（设计阶段，测量前）。
  隔离读数：`undetected`（>0 则 STOP+上报，永不并入）；`decode_failed`/
  `resource_abort` 记 incident。
- **ACC-判据 A（有可辨分离，描述性）**：两臂合计 exact 计数不等
  （`ΣBASE ≠ ΣCAND`），**且** per-seed 方向一致
  （获胜臂在 ≥2/2 seeds（若 2 seeds）或 ≥3/4 seeds（若 4 seeds）上分别领先），
  **且**重合度门已过（`overlap < 180/200`）。此时允许的结论句仅为：
  “在 <k2 点>、<CAND-ID>、<32 或 64 块/臂> 下观测到可辨分离（BASE a/b vs CAND c/d，
  per-seed …），描述性 Tier-X 非 claim”。下一步：由主线程决定是否把该 CAND
  形态送入固定构造有界列表（见下），不得直接推荐构造、不升级 R2。
- **ACC-判据 B（仍无分离，描述性）**：合计相等（最可能 0/32 vs 0/32 或低计数持平），
  或 per-seed 方向不一致。此时允许的结论句仅为：
  “在 <k2 点>、<CAND-ID> 下仍无可辨分离（…），描述性”。下一步：
  按 PI 指示考虑**固定构造有界列表搜索**（见下），禁止开放式扫参、禁止换工作点追测。
- **固定构造有界列表搜索（预注册上限与顺序，禁开放式扫参）**：
  候选池固定为 §2a 的 {C1, C2, C3, C4}（顺序 C1→C2→C3→C4），上限 **2 个 CAND**
  （即至多再起 2 个 Tier-X packet，每个单 CAND vs 同一 BASE，同 k2 点、同预算、
  同 one-shot）。已测的 `L2-CAND-PRODORDER-01` 不重测；C1 若在本次下一探针中
  已用则从列表除名。列表耗尽仍无分离 ⇒ 停止 L2 单因子线，按 PI 指示转回
  主线（R2 合同冻结），不得自发开 L2-SCL/新信道/新 N。
- 禁止事项：任何 p 值、显著性星号、“优于基线”、“构造无效”、“先验归因”、
  “高维优势”措辞一律禁止出现在 `results.json` 与结论句中。

---

## §5 明确不做什么

1. 不解锁 SCL（PI 已裁；`STATE.md` §4 冻结中；`scl.py` 锁定，5-item conjunction 未满足）。
2. 不下构造排序无效/等价结论（本次与下次探针皆无此权力；B-vs-C CI 重叠类比仅说明不可区分，非等价结论）。
3. 不单独归因 L-H1（两臂同失败 ⇒ 先验失配非单独解释；PI 归因收紧要求持续有效）。
4. 不升级为 R2/高维优势 claim（Tier-X 永不进记分板摘要、不作 R2 sizing 输入；
   `FUTURE_DIRECTION_PLAN §5` 的 H2 需配对 ΔFER + McNemar，另立项）。
5. 不重跑本次探针（`l2-singlefactor-k200` one-shot 已耗尽；`reruns=0`；任何重跑提议须 PI 另裁，本文件不授权）。
6. 不读不跑真实数据；不碰 `results/`、`outputs_comparison/`；不改任何冻结数与状态串。

---

## §6 主线程裁定点清单（稳定 ID；本文件执行前须逐项裁决或显式 DEFERRED）

| ID | 问题 | Owner | 输入 | 输出 |
|---|---|---|---|---|
| DP-N1 | CAND 形态与对比度门：选 C1–C4 中哪一个（仅 1 个）进下一 packet；重合度停止门是否采用 `overlap ≥ 180/200` | PI | §2a 表 + `construction.py:99` 冻结函数 | DECIDED（CAND-ID + 门值）/ DEFERRED（阻塞冻结） |
| DP-N2 | 工作点：k2=550 单点，无备用点（PI 2026-09-25 已裁定；原 k2=400 + 备用 500/550 方案作废） | PI | §2b k2-ramp 描述性段 | 已裁定：k2=550 单点，无备用点（PI 2026-09-25）；披露 2800 bits，f_book≈2.93441，仅用于机制诊断 |
| DP-N3 | 样本量：32/臂（2×16）或 64/臂（4×16）二选一；种子值冻结 | PI | §3 定性论证 + 预算包络 | DECIDED（seeds + blocks）/ DEFERRED |
| DP-N4 | ACC 判据措辞冻结（§4 A/B 两条 + 有界列表上限 2 + 顺序 C1→C4） | PI | §4 | DECIDED / DEFERRED |
| DP-N5 | 新 packet 授权：packet 名、输出根、预算（wall/RSS）、one-shot、读写域、禁止 SCL 重申 | 主线程 | §2 总约束 + §5 | READY_FOR_EXECUTE 或 NOT AUTHORIZED |
| DP-N6 | “发明” I-1/I-2/I-3 是否立项（默认否；选中则单独立项 + `INVENTED-NOT-FROZEN` 标记） | PI | §2a 发明单列 | DECIDED（否/单独立项）/ DEFERRED |

---

## Tasks（coder/operator 任务清单；须冻结后才可执行）

1. [ ] 主线程裁定 DP-N1–DP-N6（全部 DECIDED 或显式 DEFERRED；有 DEFERRED 则阻塞冻结）。
2. [ ] 另起 packet：`workspace/<new-packet>/STATUS.yaml` + `TASK_PACKET.md` +
   `PROMPT.md` + `AUTHORIZATION_PROMPT.md`（授权文本逐字可粘贴；SCL 锁定重申；读写域；one-shot）。
3. [ ] 写 `workspace/probes/<new-id>/prereg.md`（Q/P/C 三行；五固定改写为新 k2 点；
   CAND 定义写死；重合度门；ACC-判据 A/B 原文；预算与 STOP 规则）。
4. [ ] 执行（一次性，`reruns=0`）：先产出设计阶段重合度读数 → 门控 → 测量 →
   单一 `results.json`（per-seed 计数/均值/样本标准差/范围 + overlap + incidents + wall/RSS）。
5. [ ] Focused numerical review（命令、完整性、算术、truth 隔离、写域；非 Pre-EXECUTE/Pre-RESULT）。
6. [ ] 主线程按 §4 判据写描述性结论句；落下一步（有界列表下一个 CAND 或停线回主线）；
   里程碑批量更新 ledger/memory（per-probe 不更新）。

**Acceptance Criteria**：`prereg.md` 与 `results.json` 齐套；重合度读数先行；
计数与 §4 判据逐字对应；无显著性/verdict/claim 措辞；`undetected` 隔离；
写域仅新 probe 根；状态串零改动；预算内；one-shot 记录完整。

---

*本文件为 DRAFT 规划输入：未执行、未冻结、未授权。不改变任何状态串与冻结数。*
