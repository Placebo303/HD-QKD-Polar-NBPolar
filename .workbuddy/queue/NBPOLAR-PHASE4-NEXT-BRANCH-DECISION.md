# P20 进度审查 + 下一分支决策（主线程，2026-09-19）

- 性质：主线程审查与决策记录（非 packet、非 freeze、无执行授权）。
- 审查对象：P20A→P20R 全链、`H2_ANALYSIS_PLAN.md` / `h2_final_adjudication.md` 裁决、
  `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-PROPOSAL.md`（§16 三候选，DRAFT）、
  P20R `TASK_PACKET.md` §4 账本、`docs/decision-log.md` ~4839–4866、commit `f0e87f4`。
- 结论前置：**现在的绑定约束是人口，不是因子。先定人口规则，再谈 (a)/(b)/(c)。**

## 1. 进度审查结论（到 P20R）

链路（全部 descriptive-only，无 FER/可靠性声明）：

| packet | session / 段 | 结果 | 读数 |
|---|---|---|---|
| P20H–P20K | 1.5M TRAIN-as-DEV | L1 剂量 +128/+256/+512 + P20H λ 校准，全部 0/3 恢复 | L1 披露路线证据闭合（λ 是元凶，X08 定量） |
| P20M | 1.5M VAL 1660..2043 | raw prior：L1 突破（2/3 l1_exact），首错转到 L2；oracle G2 0/3 | λ 闭环 → **L2 成为瓶颈** |
| P20N | 1.5M HOLD 2213..2724 | A 0/4, **B 1/4**, C 0/4, D 1/4；14 失败全 L2 | 首个操作性恢复（α1 alt-L2） |
| P20O | 2M VAL 2187..2826 | A 0/5, **B 2/5**, D 3/5 | 独立 session 复现恢复 |
| P20Q | 2M HOLD 2916..3555 | A 0/5, **B 4/5**, D 4/5 | 最强恢复信号，零披露增量 |
| P20R | 1.5M VAL 余段 2044..2171 | A 0/1, B 0/1, C 0/1, D 0/1 | 见 §2 |

H2 裁决（只读分析，56 行 join）：H2a REFUTED、H2b SUPPORTED（median r_fail 2.2835）、
H2c SUPPORTED（in-X 35/37）、H2d flat、H2e REFUTED-geometry-incoherent（IR-4 池化
in-prefix 66/320 = 0.20625，而 IR-2 median 0.883）。

## 2. 对 P20R 返回的审查意见（两条，需在归档前补正）

**(i) P20R 的"描述性负结果"对 order 因子是不可解释的（block-dominated），不是对 order 的否证。**
P20R 的 A 臂 = α1 构造 + 冻结 order，即 P20N/O/Q 里那个赢的臂（B 1/4→2/5→4/5）。
该臂在本块 0/1，连真值 L1 的 oracle C/D 也 0/1 → 本块在**当前工作点上不可恢复**，
与 order 无关。建议 decision-log L4856 那条补一句（不改判定，只限定可解释范围）：

> The A anchor (α1 + frozen order) and the true-L1 oracle pair also recorded non-exact on
> this block; the result is block-dominated and does NOT discriminate the order factor.

**(ii) 返回中的剩余人口统计漏了两条。** P20R `TASK_PACKET.md` §4 账本（L131–134、L311–314）
明确记载的 never-used 段共 **4 条**，返回只列了 2 条：

| session | 段 | frames | pairs | 返回是否列出 |
|---|---|---|---|---|
| 1.5M VAL | 2172..2212（stub） | 41 | 10,496 | 是 |
| 1.5M HOLD | **2725..2766** | **42** | **10,752** | **否** |
| 2M VAL | **2827..2915** | **89** | **22,784** | **否** |
| 2M HOLD | 3556..3644 | 89 | 22,784 | 是 |

合计 261 frames / 66,816 pairs；在"128 连续帧 / 同 split / 同 session"现行规则下
= **0 个完整 N=32768 块**。但 2M 内部两段合计 178 frames = **1 个完整块 + 50 帧 stub**——
这正是决策空间的关键。

## 3. 会话难度不对称（新证据，影响 population 选择）

真值 L1 oracle 成功率：

- 1.5M：P20M G2 0/3、P20N D 1/4、P20R D 0/1 → **1/8 = 12.5%**
- 2M：P20O D 3/5、P20Q D 4/5 → **7/10 = 70%**

⇒ 1.5M 余段是低信息人群（oracle 天花板 ~12%），2M 是高信息人群（~70%）。
P20R 把最后一个 1.5M 块花在了一个 oracle 都不行的人群上，这是它不可解释的根因。
**后续任何真实数据评估必须优先落在 2M，1.5M 余段（83 帧）应视为不可用。**

## 4. 决策（四项，按优先级）

### D1 — 人口规则（必须先定，二选一）

- **D1-A（推荐）**：授权 **2M 同 session 跨 split 合并**：VAL 余段 2827..2915（89）+ HOLD 余段
  3556..3644 取前 39 帧 → 恰好 1 个 128 帧块（N=32768）；剩余 50 帧 + 1.5M 的 83 帧永久
  never-decoded。代价：修改"块 = 同 split 内连续帧"的惯例（需写 freezing 理由：两者皆非 build、
  皆未消费、同 session 故 S2-i/S2-ii 均满足）。收益：换回 **1 个落在高信息人群上的块**。
- **D1-B**：维持严格不合并 → N=32768 真实数据单因子阶梯**因人口枯竭关闭**。写 closeout；
  后继只能是：新采集，或改设计（N=8192/16384 重开构造 + order 重导 + 新 K 分配 = 重做 P16 量级、
  且跨 N 不可比，需新 OpenSpec change，不是 packet）。

- **D1 执行状态（2026-09-20 用户决定）**：**D1-A 授权** → 唯一 1 块 = VAL 余 2827..2915（89）
  + HOLD 余前 39 帧 3556..3594；P20S 机制探针包已进入冻结；D1-B（严格不合并/closeout）不生效。

### D2 — 若有且仅有 1 块（已成立），做最大信息量机制探针（P20S）

n=1 的恢复计数无判别力（P20R 刚演示过）。把最后一块定义为**最大信息量机制探针**：

- 臂：{α1+冻结 order（锚）、α1+H2 派生的局部尖峰 order、真值 L1 oracle}；
- 记录：对单块放开 IR-5 的 4096 截断，存**全块 32768 位置 hazard 序列**
  （3×32768 float32 ≈ 400 KB，尺寸可忽略）→ 直接回答 H2e 的几何问题（现在只有截断范围 +
  top-16，正是 H2e "incoherent" 的成因）；
- 判定形式：只报几何/覆盖量，不报恢复率、不做阈值投票。

因子内容仍沿用提案排序：**(a) order/position 优先**（H2e 0.20625 唯一直接命中位置集），
但派生准则必须是**局部尖峰**而非平均 hazard（H2a REFUTED）；(b) 有界搜索、(c) 第二构造继续 defer。

### D3 — 并行、零保护数据开销的主线算法工作（现在就开）

`formal_ir/nbpolar/` 下无 SCL 模块（只有 `sc.py`），SCL 自 P20H 起被锁。锁条件
（"真值 L1 的 L2 可恢复 + 有界 list 覆盖缺失候选"）现在**可以在合成数据上判定**：

1. 用 `synthetic.py` / `empirical_channel.py` 复现经验信道结构（含 9.35% 零计数重尾）；
2. 测"真值路径在尖峰深度是否存活于 L=4/8 list" → 直接解锁/否证 SCL 这一唯一未经尝试的杠杆；
3. 同时验证 D2 的局部尖峰 order 规则。

理由（AGENTS.md §1.1）：合成数据无枯竭问题、零保护开销，且 SCL 是唯一能绕开
"披露/K/构造都已探过、失败集中在 L2 尖峰"的路线。

### D4 — 卫生项（低成本，立即办）

- 证据尺寸常设规则：**单证据文件 ≤ ~2 MB 入库；更大的冻结产物放 `workspace/`（git-ignored），
  提交 digest + 摘要行**。终结 P20Q/P20R 的逐次例外。
- 账本更正：把 §2(ii) 的 4 条 never-used 段写回 `AGENT_PROJECT_MEMORY.md` 顶部账本与
  `DOCUMENT_INDEX`。
- `f0e87f4` 建议 push（分支私有、证据已双审；本地单点风险大于外泄风险）。

## 5. 明确不做

- 不做 FER/可靠性/效率/分支优越性判定；不跨 session 合并（1.5M 与 2M 永不相混）；
- 不重跑/调参 P20R，不回看已消费块；不消耗 1.5M stub 与 1.5M HOLD 余段；
- 不在本轮改 α/floor/K/decoder；不启动 (b)/(c)。
