# FER 口径预注册草稿 — 2026-09-22

- 性质：**规划输入 / planning draft — 不含授权、不冻结阈值、不改变科学状态。**
- 对应路线图 `REAL_DATA_CORRECTION_ROADMAP_20260922.md` §2 R0.2 第 1 项；服务 promotion ladder
  `FER_MEASURED_AT_CONTRACT`（`STATE.md` §4.1）。冻结前需独立评审 + PI 裁定。
- 主线裁定 R-1…R-5（已决，不重开；下文逐条落实）。

## §1 单位：reconciliation block（R-1）

**FER 的统计单位是 reconciliation block：N = 32768 symbols = 128 acquisition frames × 256 pairs。**

理由有二：(1) 译码器以 block 为单位成功/失败，泄漏按失败 block 整块计入
（Müller eq(11) 对失败帧收整帧泄漏）；(2) "acquisition frame" 是测量切分 artifact，
不是 reconciliation 单位。任何 per-acquisition-frame 读数必须是从本单位**显式派生**的，
不得替代本口径。

## §2 形式定义

设 R2 测量集中第 `i` 个 block 经冻结契约译码 + Toeplitz tag 判定后落入 taxonomy（§3），则：

```text
FER = (# verify_failed + # decode_failed)
    / (# exact + # verify_failed + # decode_failed)
```

分母 = 全部**有效** blocks；`undetected` 永不进入分子或分母（§6）；
`resource_abort` / invalid-run 从分子分母**同时剔除**，计数另行披露（R-4）。

## §3 Taxonomy 映射（R-4，固定）

| 判定 | FER 处理 | 备注 |
|---|---|---|
| `exact` | 成功（分母，非分子） | tag 通过的完整块恢复 |
| `verify_failed` | **失败**（分子+分母） | 未恢复，按 eq(11) 计整块泄漏 |
| `decode_failed` | **失败**（分子+分母） | 未恢复，同上 |
| `undetected` | **隔离：单列单计数，永不并入 success 或 FER** | 见 §6；`AGENTS.md` §5.5 |
| `resource_abort` / invalid-run | **剔除**（分子分母都不进），数量必须披露 | 执行事故，非科学 FAIL |

禁止把任何 `status` 值静默转写为 `ok`。

## §4 CI 规则：Wilson z=1.96

点估计 `p̂ = FER` 配 **Wilson 95% 区间（z=1.96）**，与 G2/G3 gate 口径连续，
跨 gate 可比。备选 Clopper-Pearson exact：更保守、更宽，
且破坏与 G2/G3 的 CI 可比性——故不采用，除非 PI 在冻结时另行裁定（见 D-FER-01）。

## §5 样本量：推导，不是断言（R-2 + R-3）

**规划约束（R-2，大声）：** 冻结契约 SHG `_1` 上 G2 B 臂 **3 failures / 14 attempts
（11 exact / 3 verify_failed）仅用于样本量规划与期望校准；明确禁止作 FER-as-population
解读；`11/14` 永不得以 "FER ≈ 0.21" 出现在任何主张位置。**（G2 adjudication binding；
`AGENTS.md` §5.5。）

取规划点 `p = 3/14 ≈ 0.214`，`pq ≈ 0.1684`，正态近似 `n ≈ z²·pq / w²`（z=1.96，
w = 目标半宽；冻结前以 Wilson 精确式复核）：

| 目标半宽 w | 导出 n | 含义 |
|---|---|---|
| ±0.114 | 50 | 路线图下限；CI 宽，仅能分辨大效应 |
| ±0.100 | 65 | `3.8416×0.1684/0.01 ≈ 64.7 → 65` |
| ±0.080 | 100 | `3.8416×0.1684/0.0064 ≈ 101 → ~100`；路线图上限 |
| ±0.050 | 259 | `3.8416×0.1684/0.0025 ≈ 258.7 → 259`；超出 50–100，需 PI 另决 |

**R-3 对账（`FER < 0.003 @ 1000 samples` 系 R3 远期 aspiration，不作 R2 sizing 依据）：**
rule of three：零失败上界 ≈ 3/n，`3/1000 = 0.003` ⇒ 该量级需 ~1000 blocks
（= 128000 frames），与 50–100 block 采集矛盾。故 R2 按**当前工作点实测 FER 的可用 CI**
sizing；`FER < 0.003` 记为披露/效率工作完成后的 R3 条件 aspiration。
参考：0/100 的 Wilson 上界仅 ≈ 0.037（`0.038416/1.038416`），0/50 仅 ≈ 0.071——
百块量级在数学上就不可能触及 0.003。

## §6 `undetected` 报告

逐 block 表单列：`exact / verify_failed / decode_failed / undetected / resource_abort`
**分列**（R2 gate 要求）；`undetected` 拥有自己的列与计数，摘要中单独一句话，
永不并入 success 或 FER。`undetected > 0` 时如何升级处理，冻结前由 PI 裁定（D-FER-06）。

## §7 泄漏挂钩

FER 经 Martínez-Mateo `f_FER` 进入 Müller eq(11)/(13) 的 verification-aware 记账；
失败 block 按 eq(11) 计整块泄漏。任何 `H(q)` → 经验 `H(X|Y)` 替换必须在冻结时
**预注册**（估计源、样本、偏差处理），事后替换禁止。

## §8 FER 数字可比 / 不可比

- 可比（带 caveat）：Müller Cascade `FER < 0.003`——必须同句声明三点差异：
  不同码族、不同信道、不同披露预算。
- 不可比：跨契约（G1 w=500/LINEAR vs G2 w=200/CIRCULAR）；合成 S9；G3 的 n=14 确认样本；
  任何 `undetected` 口径不一致的数据。
- **在 `FER_MEASURED_AT_CONTRACT` 到达前，任何 FER 数字不得写入 abstract/summary。**

## OPEN DECISIONS（owner = PI / main thread；本草稿冻结其中任何一项）

| ID | 待决项 | 草稿立场 |
|---|---|---|
| D-FER-01 | CI 方法最终冻结（Wilson vs exact） | 推荐 Wilson z=1.96（与 G2/G3 连续） |
| D-FER-02 | 目标半宽 w | 给出 ±0.10/±0.08/±0.05 三档推导，不推荐冻结值 |
| D-FER-03 | 最小样本量 n（由 w 导出） | n≈65/100/259（§5）；冻结时锁定 |
| D-FER-04 | `H(q)`→经验 `H(X|Y)` 替换口径 | 必须预注册；具体估计子待定 |
| D-FER-05 | `f_FER` 记账式冻结 | 指向 Martínez-Mateo→Müller eq(11)/(13)，项级合同待 R3 |
| D-FER-06 | `undetected > 0` 升级规则 | 待定 |
| D-FER-07 | per-acquisition-frame 派生读数允许条件 | 默认不允许；例外需预注册 |

## Carried caveats（进入冻结版 §注）

(a) w=200 窗截断总体（timing-truncated population）——任何 rate/效率/泄漏句必带；
(b) far-offset accidental 基线是结构化的，非均匀；(c) 32-frame CAL 下 q_rest=0 是弱陈述
（零观测上界 3/8192 = 3.66e-4）；(d) L2 域必须声明 `u1`（polar 变换后）vs `high_hat`
（未变换 high）——G2 Pre-RESULT domain trap。
