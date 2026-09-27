# R2 采集规格草稿（ACQUISITION_SPEC）— 2026-09-22

- 性质：**规划输入 / planning draft — 不含授权、不冻结阈值、不改变科学状态。**
- 对应路线图 `REAL_DATA_CORRECTION_ROADMAP_20260922.md` §2 R0.2 第 2 项（Route C 唯一入口）。
- 块数**从 FER 草稿的单位与样本规则推导**，不独立选取（§2）；冻结前需 PI 逐项确认（OPEN DECISIONS）。

## §1 目的

支撑 R2 的 FER 样本（预注册口径 + 样本量达标，`STATE.md` §4.1 `FER_MEASURED_AT_CONTRACT`
门）**以及** ≥1 个独立 session 复现。卖点按主线裁定：真实场景真实数据上的可用纠错
（working error correction on real scenario/real data）——**不主张 novelty**
（ToA/HD 先验 IR 存在：Boutros & Soljanin TCOM 2023，PI 已裁定）。

## §2 块数：从 Doc 1 推导，并与 R-3 对账

FER 草稿 §5 在规划点 `p = 3/14` 下导出：w=±0.10 → n≈65；w=±0.08 → n≈100；
w=±0.05 → n≈259。**本规格不另选数字，只承接该推导。**

- **Branch A（R2 执行分支）：50–100 blocks** —— n=65（±0.10）/ n=100（±0.08）恰落路线图
  建议量级内，无矛盾：该分支给出当前工作点的可用 CI，不触及 0.003。
- **Branch B（R3 远期分支）：~1000 blocks** —— `FER < 0.003` 的 rule-of-three 量级
  （3/1000 = 0.003），= 128000 frames；本次采集**不**按此 sizing，记为披露/效率工作
  完成后的条件 aspiration（R-3）。
- 若 PI 选 w=±0.05（n≈259），则超出 50–100：此时执行 Branch A′（~260 blocks），
  由 PI 在 D-ACQ-01 裁定。本草稿如实报告分叉，不替 PI 选边。

**规划约束重申（R-2，大声）：** G2 B 臂 3/14 仅用于 sizing 与期望校准；
禁止 FER-as-population 解读；`11/14` 永不得以 "FER ≈ 0.21" 出现在主张位置。

## §3 每块算术

`128 frames/block × 256 pairs/frame = 32768 symbols = N`（R-1 单位）。
EVAL 帧数 = 128n：n=50 → 6400；n=65 → 8320；n=100 → 12800；n=259 → 33152。
其上另加 §4 开销与 §5 预留段；各 acquisition 实际可组块数**以解析后 ledger 为准**，
本草稿不预断。

## §4 预留段策略（per acquisition）

每个 acquisition 在切块前先切出**独立确认 reserve**（G3 模式的推广）：
CAL / CHAR / HELDOUT / EVAL / RESERVE 互斥且记入 disjointness 矩阵。
**禁止"用尽后再找块"**——冻结 ladder 的耗尽（never-decoded 101 frames → 32f CAL 后
69 < 1 block）是警示先例：EVAL 块数以 closure 时 ledger 为准，不足则记
INSUFFICIENT ⇒ INCONCLUSIVE（COMPLETE-BLOCKS-ONLY），永不垫块/复用/缩 N。

## §5 噪声/工作点可比性

新采集噪声/工作点须与 SHG 可比；**任何差异必须在 closure 记录中声明**
（亮度、损耗、计数率、符合窗、配对规则 W_P=200/CIRCULAR/skip 语义）。
跨工作点的优劣叙事禁止；工作点差异只用于限定 FER 陈述的适用域。

## §6 Type0：显式单列决策

`Type0_nofilter_*` 是否纳入 R2 样本系**独立决策**（D-ACQ-04）：备选 (i) 不纳入；
(ii) 纳入但**单列报告**（不与 SHG 混算 FER）。草稿默认 (i)（不纳入）；
纳入需 PI 明示且一律单列。PI 2026-09-21 已裁定 Type0/SHG 系 source-only 差异、不影响 IR 过程
（见 inventory 修正案），本草稿与之兼容：in-scope ≠ 混算。

## §7 原始文件规则（继承 `RAW_DATA_INVENTORY_20260921.md`）

- `.ttbin` primary vs `.1`：已验证 `FileReader` auto-follows `.1`（01-12  acquisition
  上 Stage-A 确认：读任一文件得同一完整采集 3,836,088 events；串联读则精确翻倍）⇒
  **只读 primary `<stem>.ttbin`**；其余 9 个 acquisition 沿用 census 合并规则，
  未逐个重验（cutter 在 closure 时声明沿用项）。
- `results_*` / 分析副产物：**unread**——仅允许 `ls`/`find` 级名字清点（inventory §2
  "untrusted results present?" 列），永不开内容、永不引用其中数字。
- 路径纪律：新采集只用 POSIX/WSL 路径；Windows 原始路径仅作 provenance。

## §8 测量时长与尺度 token 语义

PI 裁定测量时长 **= 3 s**（与既有 `*_3s_*` 采集一致）。`600k`/`1p2M` 系**宽带噪声 /
最大单计数尺度参数，不是协议身份**（`STATE.md` §5）；采集单须原样记录 token，
不得解读为协议版本。

## §9 参与/污染 ledger

Census 已 decoder-free 接触 SHG `_2`（alignment σ≈114.4 ps、pairing 网格、(N)-200
`H_total`；见 G3 packet §reservation）——G3 的 independence 系 decoder/model
independence，非 no-prior-contact。本次任何已被 census/touch 过的 acquisition
必须进 participation/contamination ledger：接触类型（decoder-free vs decoder）、
日期、产物 id；decoder 接触过的帧永不回流为确认样本。

## §10 预算与 stop 规则

- 预算沿 G2 风格预冻结：单 block wall/RSS 上界 + 总 wall/RSS 上界，冻结时锁定具体数；
  超预算 ⇒ STOP（不调参）。
- Stop：ledger 不足 ⇒ INSUFFICIENT；alignment 复现失配 ⇒ STOP 大声；
  任何 frozen-contract 外的拟合/选窗/选模 ⇒ STOP；歧义 ⇒ STOP 并上报，不猜测。
- Tier-Y 纪律：one-shot、无 rerun/调参/改阈值；decode 前 Pre-EXECUTE + 显式授权；
  结果发布前 Pre-RESULT（`AGENTS.md` §10.3；`PROBE_TIER.md`）。

## OPEN DECISIONS（owner = PI / main thread；本草稿冻结其中任何一项）

| ID | 待决项 | 草稿立场 |
|---|---|---|
| D-ACQ-01 | 执行分支（A: 50–100 / A′: ~260 / B 远期）与目标 n、w | 承接 FER 草稿 §5；默认 A |
| D-ACQ-02 | 采集源清单（SHG 新采 / 候选 Type-II / 数量） | 待定；以 ledger 为准 |
| D-ACQ-03 | 每 acquisition 预留段配额（CAL/CHAR/HELDOUT/RESERVE 帧数） | 参考 G3 模式（1024/32/782/560），未冻结 |
| D-ACQ-04 | Type0 纳入与否及报告方式 | 默认不纳入；纳入需明示且单列 |
| D-ACQ-05 | 噪声/工作点可接受差异带 | 待定；声明制 |
| D-ACQ-06 | 预算数（单块 wall/RSS、总 wall/RSS） | 待定；G2（~20 s/block，total 855.1 s ≤ 900，RSS 1.12 GiB ≤ 2）仅作量级参考 |
| D-ACQ-07 | 配对/构造契约沿用（W_P/W_S/MOD/skip/K1/K2/P16） | 默认继承冻结契约；任何偏离需单独立项 |
| D-ACQ-08 | 独立 session 复现的最低会话数（路线图 R1 门 ≥2） | 待 PI 确认是否与 R2 同批采集满足 |
