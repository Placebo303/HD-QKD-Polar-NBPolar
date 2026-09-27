# NB-Polar 隔夜自动执行计划（OVERNIGHT PLAN）— 2026-09-27

> ⚠ 2026-09-27 更正：本文引用的合成两层 GF32 探针（`l2-singlefactor-c1-k550`、`k2-dose-ramp` 等）使用了镜像信道表（table 符号缺陷），其计数不构成匹配译码证据；见 decision-log 2026-09-27。

- **性质**：执行计划 + 冻结清单（本文档本身**不授予执行授权**、不冻结任何状态串、不含任何 FER/效率/密钥数字主张）。
- **制定者**：主线程（本次会话，2026-09-27）。
- **适用窗口**：今晚 ≈8 小时无人值守窗口；每阶段独立完成、可断点续跑。
- **状态基线（只读引用，不改）**：
  M2 = `VALIDATED_AT_FROZEN_CONTRACT`（第 2 级）；R2 合同 **NOT frozen**；
  D-FER-01..03 已由 PI 裁决，D-ACQ-02/03/05/06 **PENDING** ⇒ T5/T6 阻塞、T7/T8/T9 **NOT AUTHORIZED**；
  SCL 锁定；`STATE.md:65` route lock **未解除**。
- **纪律来源**：`AGENTS.md` §3（评审门）§5.6（默认禁跑）§5.7（简洁科研工程）、`docs/nbpolar/PROBE_TIER.md`（Tier-X 模板）、
  `docs/nbpolar/NEXT_L2_PROBE_DESIGN_20260925.md` §4（ACC 判据与有界列表）。

---

## §0 进度快照（写计划时的实测状态）

### §0.1 主线位置

| 线 | 状态 | 证据 |
|---|---|---|
| M2 先验 | `VALIDATED_AT_FROZEN_CONTRACT`（仅第 2 级；R2 FER 门未过） | `docs/nbpolar/STATE.md:§4.1` |
| R2 测量合同 | T1 引注 / T2 合并（draft）/ T3 STRUCT-PASS；**T4 未完整裁决** | `docs/decision-log.md:27`、`openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md:74` |
| L2 构造单因子线（algorithm 线 (b)） | **C1 探针已一次性执行完成（one-shot）并有 focused numerical review** | `workspace/probes/l2-singlefactor-c1-k550/results.json`、`workspace/l2-singlefactor-c1-k550-packet/{STATUS.yaml,EXECUTION_TRANSCRIPT.md,FOCUSED_REVIEW.md}` |
| 路线 option (a) SCL | DEFERRED（未解锁） | `docs/decision-log.md:29` |

### §0.2 今晚最重要的新事实（C1 探针，2026-09-25 17:48–17:50 UTC 执行，one-shot）

- d2 重合 **76/550**，Jaccard **0.07421875**，`identical=false` ⇒ 未触发 ≥495 的 `non_discriminating` 停测门，8/8 cells 全部测量。
- **oracle-L2 读数**：BASE(`worst_k(H2,550)`) **64/64 exact**；C1 CAND(`best_k(H2,550)`) **0/64 exact**；
  per-seed 4/4 方向一致（每 seed 16/16 vs 0/16），配对不一致 `base_only_exact=64 / cand_only_exact=0`。
- **operational 读数（关键）**：两臂均为 **0/64 exact、64/64 `verify_failed`**。
- 隔离项：`undetected=0`、`decode_failed=0`、`resource_abort=0`（四组全零）。
- 预算：wall **99.9065 s** ≤ 200 s；peak RSS **215662592 B (≈0.201 GiB)** ≤ 1 GiB；`probe_runs=1 / reruns=0`。
- 主线程裁定：**仅作为该冻结合成点上的描述性 Tier-X 对照**（C1 是刻意构造的低信息反向对照，**不是改进算法**）；`scientific_acceptance: false`；无 token、无晋级、无自动续命。

### §0.3 由此确立的瓶颈（今晚的科学主题）

C1 + `k2-dose-ramp` 合起来给出一条单向事实：

> 在 F4@q1024 + M2 双层 GF32 SC 路径上，**oracle 分支对 L2 信息集极度敏感且可达 64/64**；
> 但 **operational 分支在所有已测点上恒为 FER=1.0**（C1: 0/64 @ k1=10,k2=550；k2-dose-ramp: k2∈{200,400,700,1024} 全部 0/32）。
> 而 **k1（第一层 L1 披露剂量）在该新系列里从未被当作单因子变量**（`K1_FROZEN=10` 恒定；历史 X05 的 `K1_GRID=[45..112]` 属**旧 nace 系列 K2=140 的 decoder-free 算术重放**，与本机路径不可比）。

⇒ 按 `AGENTS.md` §1.1（高性能纠错为第一原则），今晚唯一值得自动推进的科学动作是：
**定位 operational 路径的第一个断点**（k1 剂量是否为瓶颈），而不是继续在 oracle 分支上重复"信息集很重要"这一已观测结论。

### §0.4 仓库欠账（今晚顺手清零，低成本、零风险）

- 未跟踪（应当commit）：`openspec/changes/nbpolar-l2-c1-k550-probe/`（整个 change，含 proposal/design/tasks）。
- 未跟踪（草稿，需 PI/主线程决定去留）：`docs/nbpolar/{ACQUISITION_SPEC_DRAFT_20260922,FER_DEFINITION_DRAFT_20260922,NEXT_L2_PROBE_DESIGN_20260925,R2_MEASUREMENT_CONTRACT_DRAFT_20260924,R2_OPEN_INPUTS_DECISION_LIST_20260925}.md`。
- 已修改未提交：`AGENT_PROJECT_MEMORY.md`、`docs/nbpolar/{README,REAL_DATA_CORRECTION_ROADMAP_20260922,STATE}.md`、`openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md`。
- 本地 **领先远程多个 commit、未 push**（政策：无明确指示不 push）。
- T0 副作用：`workspace/probes/l2-singlefactor-c1-k550/.numba_cache/`（空的作用域目录，已在 STATUS 记录；**不删除**，保持可追）。

---

## §1 一夜目标 / 非目标

### 目标（按优先级）

- **G1（科学，最高）**：完成一次 **operational k1 剂量单因子 Tier-X 探针**（新 packet、机机派生、one-shot、focused review、主线程描述性裁定），回答"operational 全灭是否由 L1 剂量单点不足解释"。
- **G2（工程/账目）**：把 C1 全流程沉淀为可复现的完整仓库状态（commit + decision-log + index + memory），使 L2 构造线具备完整 provenance。
- **G3（PI 就绪）**：把 R2 T4 的四个 PENDING 做成**明早一句话可裁的决策卡片**（含选项与后果，**不填推荐数值、不代裁**）。

### 非目标（硬禁令，违反即 STOP）

1. **不碰任何真实/受保护数据**：不读 `TypeII_*` 原始数据根、不在真实块上跑 decode、不跑 Tier-Y。`T7/T8/T9` 仍 NOT AUTHORIZED。
2. **不自造 PI 冻结数**：R2 的 source list / quotas / comparability / budget 四个 PENDING **一个数都不填**（`tasks.md:57` 边界）。
3. **不改状态串**：`docs/nbpolar/STATE.md` 的 rung/ladder state、M2 状态、G2/G3 冻结的 K1=319/K2=6492 一律不动。
4. **不 push、不 archive、不解 route lock**（`STATE.md:65`）。archive 决策留到明天主线程。
5. **不写 `results/` 与 `comparison_bench/outputs_comparison/`**；不读 sibling checkout；不改 `src/`、`comparison_bench` 生产语义。
6. **不开放式扫参、不临场换点、不加样、不 rerun**（one-shot，`reruns=0`）。
7. **不用 Tier-X 数字做 R2 sizing 输入、不做显著性措辞、不写 H-label 结论**（只用 probe-local L-H 措辞）。

---

## §2 阶段序列（每阶段可独立续跑；进度写入 `workspace/overnight_state_20260927.md`）

> 约定：**A = 主线程亲自执行**（本环境可用的 subagent 仅 `code-explorer`，只读）；
> **R = 只读独立复核**（`Task(code-explorer)`，显式禁止改文件 + 禁止 grep 全仓乱扫 + 幂等预检，依据 `.workbuddy/memory/2026-09-22.md` 的 subagent 工具纪律）。

### P0 — C1 沉淀（预算 25 min，零风险）
> **git 边界（硬）**：**不 commit、不 push、不 stage**。所有 git 动作本夜一律挂起，交给明早用户明示后再做；本阶段只在 morning report 里产出 **commit-ready 清单**（应 add 的路径 + 建议提交信息）。
- 动作 A：向 `docs/decision-log.md` 追加一条（Decision/Context/Alternatives/Consequences 四段格式）：C1 Tier-X 合成探针 `DESCRIPTIVE_TIER_X_REVIEWED_WITH_LIMITATIONS`（oracle BASE 64/64 vs CAND 0/64；operational 0/64；overlap 76/550；wall 99.9 s / RSS 0.201 GiB；one-shot；**非证据、非 R2 输入、不改状态串**）。
- 动作 A：`docs/nbpolar/DOCUMENT_INDEX.md` 增一行指向 `workspace/l2-singlefactor-c1-k550-packet/FOCUSED_REVIEW.md`。
- 动作 A：写 `.codebuddy/memory/2026-09-27.md` + `.workbuddy/memory/2026-09-27.md`（按 `[decision]/[repo-observed]/[procedure]` 标签书写）。
- 动作 A：撰写 **commit-ready 清单**（仅文本、不执行 git）：`openspec/changes/nbpolar-l2-c1-k550-probe/`（proposal/design/tasks）+ 本阶段新增/修改文档，附建议提交信息；挂起原因写进 morning report。
- **STOP**：任何一步出现对既有文件的非预期覆盖 ⇒ 立即停、diff 存为 `workspace/overnight_state_20260927.md` 的 incident 记录。

### P1 — 下一探针的裁定与冻结（预算 40 min，A）
- 依据 §0.3，主线程作出（并记录在新建 packet 的 `STATUS.yaml` 的 `adjudications:` 段）：
  - **DP-K1（主题）**：选择 `operational k1 dose ramp`，**不**再消耗有界列表 C2/C3/C4（理由：C1 已产生强分离，再重复"信息集敏感性"无新信息；依据 `NEXT_L2_PROBE_DESIGN_20260925.md` §4 ACC-判据 A 的"下一步由主线程决定"条款）。
  - **DP-K2（单点 grid，有界 5 点，一次性在一个 run 内完成）**：`k1 ∈ {10, 80, 160, 320, 450}`，`k2=550` 固定，`base=worst_k(H2,550)`，`d1=worst_k(H1,k1)`（随 k1 变化的冻结族成员）。
  - **DP-K3（样本）**：每点 **2 seeds × 16 blocks = 32 blocks**；单臂（仅 BASE；C1 已证明 BASE 是有效且现行的信息集，本探针变量是 k1 而非 arm）。
  - **DP-K4（种子）**：`design_seed=2026092600`、`DESIGN_MC=128` **沿用不变** ⇒ `d2=worst_k(H2,550)` 与 C1 的 BASE **集合同一**，可与 C1 对齐；run seeds 新取 `2026092701..2026092702`。
  - **DP-K5（预算）**：`wall ≤ 600 s`、`RSS ≤ 1 GiB`，每 32 design 样本与每 block 检查，超界即 `status=incomplete` 停且不调参。
- 派生的冻结数值（**运行内以公式计算为准，此处仅 bookkeeping 参照**，`HN ≈ 954.18`，校验点：k1=10 ⇒ 2800 bits / f_book≈2.9344139789 与 C1 一致）：

  | k1 | disclosed = 5·(k1+550) | f_book（仅记账；非效率点） |
  |---:|---:|---:|
  | 10 | 2800 | ≈2.9344（= C1 锚点） |
  | 80 | 3150 | ≈3.3013 |
  | 160 | 3550 | ≈3.7204（与 k2-dose-ramp 的 3550 点交叉校验一致） |
  | 320 | 4350 | ≈4.5589 |
  | 450 | 5000 | ≈5.2401 |

- **写入禁止**：不得声称任何 k1 点是"效率工作点"；一律写 "bookkeeping-only dose diagnostic"。
- OpenSpec：`openspec/changes/nbpolar-op-k1-ramp-k550/`（`proposal/design/tasks` 三件套），Scope OUT 逐字沿用 C1 change（`nbpolar-l2-c1-k550-probe`）的边界段并加一句 "k1 is a dose variable, not an efficiency claim"。

### P2 — 派生 run.py + prereg + packet（预算 45 min，A）
- **机械派生**自 `workspace/probes/l2-singlefactor-c1-k550/run.py`，仅允许改动：
  ① `K1_FROZEN` → `K1_GRID=(10,80,160,320,450)` 且 `K2_SINGLE=550` 不变；
  ② `d1 = worst_k(H1, k1)` 改为随 grid 逐点计算（`d1_shared` 语义改为 per-config）；
  ③ 标识符 `probe_id`、`SEEDS`、输出/cache 路径；
  ④ 移除 C1 专有的 CAND 臂与 overlap 门（本探针单臂 ⇒ 该门不适用，**但必须保留 `undetected` 隔离 STOP 与预算 STOP**）；
  ⑤ 结果记录按 k1 逐点输出 operational/oracle outcome 计数 + `key_dependent_bits` + wall/RSS。
- **禁止**：改信道、改 prior、改 `toeplitz_master=2026091361`、改 `tl.run_two_layer_block` 调用语义、改外部只读依赖 `qkd_recon.polar_core`（`/mnt/d/Code/qkd-reconciliation-lab/src`，只读导入、零写入）。
- `prereg.md` 必须含 Q/P/C 三行；C 行为 WSL 版本，**路径逐字沿用 C1 的 venv**：
  `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`，并带
  `PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=<probe root>/.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src`。
- packet：`workspace/op-k1-ramp-k550-packet/{TASK_PACKET.md,STATUS.yaml,FREEZE_REVIEW.md}`，`authorizations:` 段记为准据 = "用户已授予的合成工作广泛授权（见 C1 packet STATUS `user_authorization`）+ 本主线程冻结评审通过"，并显式写明 **本包不触碰任何真实数据**。

### P3 — freeze review（预算 25 min，R→A）
- R 独立只读复核（**工具限制**：仅允许读取路径白名单 = 新 packet + 新 probe root + C1 前任 run.py；幂等预检 = 确认目标 `results.json` 不存在）：
  ① C 命令与 prereg 逐字一致；② `K1_GRID`/`K2_SINGLE`/`d1`/`d2` 与 DP-K2/K4 一致；③ `disclosed=5*(k1+k2)` 五点逐一验算；
  ④ 种子与 blocks 与 DP-K3/K4 一致；⑤ 预算与 STOP 规则齐备；⑥ 写域仅新 probe 根；⑦ 目标产物缺失已验证。
- A 汇总为 `FREEZE_REVIEW.md`；**任何一项 FAIL ⇒ 回 P2 修订，不得执行**。

### P4 — one-shot 执行（预算 15 min，A）
- 目标产物缺失检查（强幂等）：新 probe 根的 `results.json` **必须不存在**才发起。
- WSL：`wsl.exe -e sh -lc "<prereg C 命令>"`，工作目录仓库根；一次启动、`reruns=0`。
- 记录 `EXECUTION_TRANSCRIPT.md`：起止 UTC、直连 exit code、stdout 摘要、stderr 摘要（确认无 Python traceback）、被测 cells、wall/RSS（核对 ≤600 s / ≤1 GiB）、STOP 是否触发、写域清单。
- **STOP 规则**：`undetected>0` ⇒ 立即停并隔离；超预算 ⇒ `incomplete` 且不调参；异常 ⇒ 一条记录 + 不重试（无第三条路）。

### P5 — focused numerical review + 主线程裁定（预算 30 min，R→A）
- R 只读复核（不重跑探针）：per-k1 的 operational/oracle 计数重算、合计数与 `disclosed` 逐点核对、tag 排除口径（64-bit tag 不计入 f）、`undetected` 隔离、写域、one-shot。
- A 写 `FOCUSED_REVIEW.md` + 主线程裁定段，**只允许描述性结论句**，并二选一：
  - **存在 k1 断点**（某点起 operational exact > 0）：结论句 = "在 F4@q1024/BASE d2/k2=550 下，operational exact 计数在 k1∈(a,b] 区间首次脱离 0（逐点计数：…），描述性 Tier-X、非 claim"；下一步建议留给明天主线程：**不得当场起第三个 packet**。
  - **五点全 0**：结论句 = "在 k1≤450 的有界 grid 上 operational 仍为 0/32 每点 ⇒ 单靠提高 L1 披露剂量不足以解释 operational 失效（描述性）"；下一步建议：把失败定位推进到 **逐层归因**（L1 vs L2），列为明天的 DP 项，**今晚不做**。
- 更新 `STATUS.yaml`（`result_status`、`execution` 段、`probe_runs/reruns` 计数），追加 decision-log 条目，更新 DOCUMENT_INDEX，写今日 memory；**git commit/push 一律挂起**（同 P0 的 git 边界），只更新 commit-ready 清单。

### P6 — R2 的 PI 就绪决策卡片（预算 40 min，A；纯文档，**不代裁**）
- 新建 `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md`：为 D-ACQ-02（新采集源清单）/ D-ACQ-03（五段配额）/ D-ACQ-05（工作点可比条件）/ D-ACQ-06（机器与预算）各做一张卡，
  每张含：① 待决项的逐字引用；② **可选项**（互斥，标注各自后果）；③ 需要的外部字段清单（含单位）；④ "若 PI 本轮不裁" 的后果；⑤ owner。
- **纪律**：卡中不得出现推荐数值、不得出现 "建议采用 X" 的倾向性措辞；数值位一律 `<待填 · 单位>`。
- 同时更新 `openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md` 的 T4 status 段（只加一行指向决策卡，**不改 PENDING 状态、不写数值**）。

### P7 — morning report（预算 15 min，A，必做）
- 写 `workspace/OVERNIGHT_REPORT_20260927.md`：各阶段状态、产物路径、计数摘要（逐字来自 artifacts）、incidents、未决项、**明天的 3 个 PI 问题**、未完成阶段的原因。
- 更新 TODO 与实际不符项（如阶段未跑完，如实标注，不美化）。

---

## §3 环境事实（冻结，不在今晚重新推导）

- Python：WSL 侧 `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`（**禁止**用系统 python）；主机侧仓库根 `d:\Code\HD-QKD_Polar_Comparison-nbpolar` ↔ WSL `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`。
- 只读运行时依赖：`qkd_recon.polar_core`，`/mnt/d/Code/qkd-reconciliation-lab/src`（仅 `PYTHONPATH` 导入，零写入）。
- 上一执行实测包络：wall ≈ 100 s / 128 blocks（= 64 blocks × 2 臂，k1=10/k2=550）；RSS ≈ 0.21 GiB ⇒ 本夜 160 blocks（5 点 × 32）的 grid 工作量估计 ≈ 2–4 分钟量级，600 s 上限有 3× 以上余量。
- 已知噪声：WSL 启动的 localhost/NAT 诊断（stderr，非 Python traceback），遇之照常记录不中断。
- `wsl.exe -e sh -lc` 需 Windows 用户会话存活 ⇒ **夜间不要关机/注销**（锁屏无妨）。
- 政策：`.codebuddy/memory/**` 与 `.workbuddy/memory/**` **永不 commit**；`.git/index.lock` 若出现 ⇒ 等待自清，**禁止手删**。

---

## §4 PI/用户独占项（明早，不在今夜自动代裁）

| 事项 | 为什么不能自动 | 明早需要的一句话 |
|---|---|---|
| D-ACQ-02 新采集源清单 | 需实验室提供清单，禁止从既有数字反推 | 指定 session_id 清单 |
| D-ACQ-03 五段配额 | 只有 PI 能裁段划分规则与帧数 | 给出 partition_rule + 各段帧数 |
| D-ACQ-05 工作点可比条件 | 科学判断（对标基线/差异带/≥2 sessions） | 给出 baseline_id + tolerance_band + sessions_required |
| D-ACQ-06 执行预算 | 需机器与并行度实测约束 | 给出 machine_spec + parallelism + wall/RSS 上限 |
| 是否 archive `nbpolar-l2-c1-k550-probe` | 归主线程/用户的下一个决策点 | 是/否 |
| 是否 push（本地领先多 commit） | 政策需明确指示 | 是/否 |

---

## §5 自动化驱动约定（用户已确认：**运行到 2026-09-27 08:00 停止**）

- 进度文件：`workspace/overnight_state_20260927.md`（每阶段一行；**停表时间 = 2026-09-27 08:00 本地时区**，此后不再开新阶段）。
- 已有的调度条目（均指向本文件 + 进度文件）：
  1. `NB-Polar 隔夜推进 20260927`（recurring，`FREQ=HOURLY;INTERVAL=1`，`validUntil=2026-09-27T08:00`）；
  2. `NB-Polar 隔夜第1轮 0245`（once，`2026-09-27T02:50`）；
  3. `NB-Polar 隔夜第2轮 0500`（once，`2026-09-27T05:00`）。
- **并发保护**：进度文件含 `last_heartbeat`；若距心跳 < 6 分钟 ⇒ 判定上一轮仍在运行，本轮立即退出且不写入。
- 每轮 tick 行为：① 读本计划 §2 与进度文件；② 取第一个非 `done` 阶段执行；③ 阶段完成即更新该行 + 刷新心跳；④ 遇 §1 硬禁令或任一 STOP ⇒ 写 cause 到 incidents 并退出。
- 幂等：每次执行前验证目标产物缺失；已存在则**不重跑**，直接进入下一阶段。

---

*本文件为隔夜自动执行计划：不含执行授权、不改状态串、不含 FER/效率/密钥主张。所有下级 packet 必须各自通过 freeze review 才可执行。*
