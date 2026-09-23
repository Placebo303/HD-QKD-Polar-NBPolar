# 探索总结报告：NB-Polar 高维原生纠错方向探索（nbpolar-native-highdim-exploration）

> 本报告为 `nbpolar-native-highdim-exploration` 探索套件的最终总结记录（docs-only）。
> 全文为描述性、非 claim 记录：一切探针数值均为 L2-synthetic 或 L3-descriptive 台账值，
> 绝不引用为 real-data FER。数值一律逐字转录自裁决后事实，不重算、不改 rounding。

## 0. 任务与授权记录

- Task identity：本 change 为 EXPLORATION-ONLY（`proposal.md` 状态行 `EXPLORATION_ONLY / PLAN_CANDIDATE`），
  所在仓库 `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`，分支 `codex/nbpolar-phase0`；
  计划验收 T1–T9（docs-only，零执行）提交 `4d5cf034`；
  Step-0 + M6 裁决簿记提交 `d802ff2d`；
  套件执行收口提交 `8eeae0d9`（29 files）；未 push。
- Authorization record（两次逐字用户指令，各自绑定范围记录在对应 packet 的 `STATUS.yaml` authorizations 块）：
  - 2026-09-23 隔夜委派，仅绑定 Step-0 探针：
    「顺着本本 exploration 往下推进，我要睡觉了，希望早上能直接看到你的完整准确诊断的 exploration」，
    记录于 `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/STATUS.yaml`。
  - 全日套件指令，按 packet 逐个绑定 Steps 1–3 + M6 addendum：
    「我的意思是做完全套本项目的方向探索部分」，
    逐字记录于 `NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM`、`NBPOLAR-EXPLORATION-STEP1-SCREENING`、
    `NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER`、`NBPOLAR-EXPLORATION-STEP3-ADJUDICATION` 各自的
    `STATUS.yaml` authorizations（含 main-thread scope binding）。
- Governance summary：每个探针均走同一治理链——freeze（`TASK_PACKET` + `AUTHORIZATION_PROMPT` +
  `STATUS` + 冻结 prereg）→ P0 draft check → 一次测量运行 → 独立 focused numerical review →
  main-thread adjudication。Amendments 共 3 个：
  1. M1 shape（`circular_counts` 1024 cells，residues −512…+511；summaries 位于 `profile.summaries.CIRCULAR`），
     由 P0 draft check 在零写入时捕获；
  2. Step-1 interpreter re-freeze 至 `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`
    （timetagger-venv 缺 pandas，无法导入 formal_ir 包链）；
  3. Step-2 control redefinition（blind-uniform 简并后的 no-injection true-channel baseline 重定义）。
  One-shot 记账：每探针一次测量运行；Step-2 另有一次 gate-failed pre-measurement STOP
 （原 uniform control 下，零输出；amendment 3 下全新执行；从不存在可 rerun 的测量）。

## 1. 冻结不变性声明

- 以下冻结常量全程未动（逐字）：d=1024；N=32768（=128 frames × 256 pairs）；K1=319；K2=6492；
  P16；W_P=200 / W_S=500 / CIRCULAR / skip=702；frame_pairs=256；floor=1e-15；chunk=512；
  bin=200 ps；f(6811)=1.2747449；key_dependent_bits=34,119（=5·(K1+K2)+64，per-row constant）；
  public_control_bits=327,743；undetected 0/42（隔离，永不并入 success/FER）；
  EVAL 14 blocks 2398–4189；RESERVE SHG_1 29 / SHG_2 99 frames；
  never pad/reuse/shrink，COMPLETE-BLOCKS-ONLY else INSUFFICIENT；DEVELOPMENT ≠ confirmation。
- 无冻结文件被触碰；`comparison_bench` / formal_ir 均为只读导入（`comparison_bench/` READ-ONLY，imports only）。

## 2. Step-0 信道勘察（COMPLETE_DESCRIPTIVE）

- 出处：packet `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/`
  （`STATUS.yaml` adjudication 块，label `NBPOLAR_EXPLORATION_STEP0_SURVEY_COMPLETE_DESCRIPTIVE`，
  review `pass_with_comments`）→ 探针根 `workspace/exploration/nbpolar-native-highdim/step0/`
 （`prereg.md` / `results.json` / `notes.md` 三文件，worktree-only）→
  `results.json` keys（`primary_m1` / `abs_delta_distribution` / `period_crossing` /
  `wrap_closure_check` / `bin_occupancy`）→ 决策日志 `docs/decision-log.md` 2026-09-23 Step-0 条目 →
  提交 `d802ff2d`。
- Population：SHG_1 `20260113_SHG_Type2PPLN_3s` CHAR，200,192 pairs，(N) W_P=200，
  MOD CIRCULAR，skip-702，derived offset +50 ps（G1R2 contract）。
- 结果：n0=150,909（75.38%）；|Δ|=1 mass 49,283/200,192 = 0.24617866847826086；
  +1 48,832 vs −1 451（≈108×）；|Δ|≤1（含零 bin，n_tail=0）占满总体 =
  200,192/200,192 = 1.0000（即项目既有记号 delta_mass_le1 所指事实；注意
  results.json 存储键 mass_le1 = 0.24617866847826086 仅指 |Δ|=1，两者同义不同名，
  按 2026-09-23 独立审计 D1 更正标注）；
  n_cross = 45（44+1），rate 2.247842071611253e-04 per symbol；
  wrap closure：circular[−1]=451=450+1，circular[+1]=48,832=48,788+44；
  冻结锚点 44 / 1 / 451 / 48832 / 0 全部匹配；interpreter 为 timetagger venv。

### 2.1 M6 addendum（COMPLETE_DESCRIPTIVE）

- 出处：packet `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM/`
  （`STATUS.yaml` adjudication 块，`rebuilds: 1` 已披露）→
  探针根 `workspace/exploration/nbpolar-native-highdim/step0-m6-addendum/`
 （`results.json` keys `checks` / `occupancy`）→ 决策日志 2026-09-23 套件条目 M6 段。
- 结论：occupancy 为 UNMEASURABLE_FROM_FROZEN_ARTIFACTS——本机无 parquet reader
 （pyarrow / fastparquet / duckdb / polars 均缺，pandas 3.0.2 无 engine）；
  manifest 上下文为 synthetic_d8_ser005、d=8（即使有 reader 也会 fail alphabet/provenance 检查）。
- Rebuilds 1（zero-output makedirs crash，`s0m_run_log.md` 披露）；
  受保护的 step0 根字节未变。

## 3. Step-1 小 q 筛选（COMPLETE_DESCRIPTIVE）

- 出处：packet `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/`
  （`STATUS.yaml` adjudication 块，label `NBPOLAR_EXPLORATION_STEP1_SCREENING_COMPLETE_DESCRIPTIVE`，
  review PASS）→ 探针根 `workspace/exploration/nbpolar-native-highdim/step1/`
 （`results.json` keys `freeze` / `gates` / `population` / `cells`）→
  决策日志 2026-09-23 套件条目 Step-1 段 → 提交 `8eeae0d9`。
- Freeze F1–F8（逐字摘要）：F1 arm A 经只读复用 `comparison_bench.formal_ir.nbpolar`
  的 q-ary polar SC；F2 arm B 为 r-level Gray bit-plane MLC-polar、packet-local binary
  butterfly + Arikan SC、对早解平面 MSD hard conditioning、平面序 0..r-1；
  F3 素多项式 GF(4)=0b111、GF(8)=0b1011、GF(16)=0b10011，alpha=2，两臂共享 reflected Gray；
  F4 通道 P(δ=0)=0.75、P(δ=+1)=0.24、P(δ=−1)=0.005、0.005 均匀分布于其余 q−3 offsets；
  F5 n_sym=128、R∈{0.30,0.40,0.50,0.60}、K_sym={38,51,64,77}、design seed 2026092400；
  F6 筛选 seeds 2026092401..2026092416（16）× 64 blocks/seed = 每 cell 1024 paired blocks，
  跨臂共享 message + noise（paired），numpy default_rng；
  F7 arm-A 设计为 MC genie-SC 后验熵 top-K、arm-B 为诱导二元信道 Bhattacharyya 递归联合 top-(r·K_sym)；
  F8 FER 为 1024 blocks 块错率、f = r·K_sym/(n_sym·H_δ)、逐 cell 报告 per-seed series +
  mean/sample-std/range、paired ΔFER = FER_B − FER_A、无数值阈值（仅定性 bar）。
- Gates：G1 oracle 每 (arm,q) 200/200、0 hard mismatches（tie ≤1e-9，first-divergence 语义）；
  G2 noiseless 20/20；G3 smoke max 0.01953125（5/256）。三处 pre-run build defects 被 gates 在冻结运行前捕获修复。
  Wall 169.4 s。Reviewer 独立复算：144 fresh gate instances、0 hard mismatches，
  全部 cell 统计逐字 exact。
- 全结果表（cell means；H_δ：q4 0.8818511717297366，q8 0.8934608122041734，q16 0.900353370320442）；
  每 q、每 R：f、FER_A mean、FER_B mean、ΔFER mean：
  - q4：R0.30 f0.6733 A0.0000 B0.0107 Δ+0.0107；R0.40 f0.9036 A0.0596 B0.2002 Δ+0.1406；
    R0.50 f1.1340 A0.4189 B0.6719 Δ+0.2529；R0.60 f1.3643 A0.9326 B0.9766 Δ+0.0439。
  - q8：R0.30 f0.9968 0/0 Δ0；R0.40 f1.3378 A0.0000 B0.0107 Δ+0.0107；
    R0.50 f1.6789 A0.0039 B0.0908 Δ+0.0869；R0.60 f2.0199 A0.1270 B0.5371 Δ+0.4102。
  - q16：R0.30 f1.3189 0/0 Δ0；R0.40 f1.7701 A0.0000 B0.0010 Δ+0.0010；
    R0.50 f2.2214 A0.0000 B0.0117 Δ+0.0117；R0.60 f2.6726 A0.0088 B0.1240 Δ+0.1152。
- Reading：cell-mean 层面 12/12 native-symbol SC 优于 Gray bit-plane MSD arm B
  （10/12 严格为正，2 个零为 floor ties）；seed-level nuance：q4 R0.60 有 3/16 negative seeds，
  已 carry；定性 bar 结论：clear separation ⇒ Step 2/3 designs may be frozen next（已满足）。

## 4. Step-2 迁移先验（COMPLETE_DESCRIPTIVE；保留证据的阴性）

- 出处：packet `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/`
  （`STATUS.yaml` adjudication 块 + amendment 3，
  label `NBPOLAR_EXPLORATION_STEP2_PRIOR_TRANSFER_COMPLETE_DESCRIPTIVE`，
  review `pass_with_comments`）→ 探针根 `workspace/exploration/nbpolar-native-highdim/step2/`
 （`results.json` keys `freeze` / `gates` / `cells` / `m2_reference` / `arm_u_redefinition`）→
  决策日志 2026-09-23 套件条目 Step-2 段 → 提交 `8eeae0d9`。
- Amendment-3 背景：blind-uniform 简并——log(1/q) messages 在 `sc_decode` 接口 information-free，
  FER=1.0（成功概率 q^-K）；arm U 重定义为 no-injection true-channel baseline。
  Arm I = 冻结 G1R2 CAL32 triple 0.7562 / 0.2419 / 0.0018 / rest-0 + floor 1e-15（unrenormalized）。
- Gates：G0 recorded unavailability（Step-1 `results.json` 无 info-set 数组）；
  G1a/G1b 每 q 200 实例、0 hard mismatches；G2 20/20；
  G3 smoke（R0.30 两臂 FER < 0.9）。Wall 196.0 s。
  Reviewer 复算：144 fresh gate instances；48/48 series stats exact；
  M2 provenance 对 `G1R2_ADJUDICATION.md` 核验无误。
- 全结果表（cell means）；每 q、每 R：FER_I、FER_U、g_succ mean、g_nll mean：
  - q4：R0.30 0.0840/0.0000 −0.0840 −338.75；R0.40 0.3936/0.0596 −0.3340 −1331.64；
    R0.50 0.6152/0.4189 −0.1963 −2578.54；R0.60 0.9414/0.9326 −0.0088 −5305.54。
  - q8：R0.30 0/0 0 −0.00；R0.40 0/0 0 +0.0006；
    R0.50 0.0713/0.0039 −0.0674 −775.91；R0.60 0.3174/0.1270 −0.1904 −3719.70。
  - q16：R0.30 0/0 0 +0.00；R0.40 0/0 0 +0.00；
    R0.50 0.0010/0.0000 −0.0010 −23.20；R0.60 0.0830/0.0088 −0.0742 −1333.56。
- Reading：每个 discriminating cell 的 cell-mean g_succ ≤ 0；
  floored tail cells 起作用处 g_nll 强负（floor-mishandling 可见）；
  阴性按 design §5 作为证据保留。Seed-level nuances：q4 R0.60 有 3/16 strictly
  positive g_succ seeds（+0.015625 @ seeds 2404/2407/2408；2026-09-23 独立审计 D2
  从原始序列更正，此前 2/16 系评审转述误差）；
  q8 R0.40 g_nll +0.0006 为全零 tie cell 内 floating noise；
  q16 R0.50 range 出现 +0.000127（mean −23.2）。
  边界：仅 synthetic-envelope 证据——M2 real-data 状态 `VALIDATED_AT_FROZEN_CONTRACT` 未动。

## 5. Step-3 纸面复杂度裁决（COMPLETE_DESCRIPTIVE）

- 出处：packet `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP3-ADJUDICATION/`
  （`STATUS.yaml` adjudication 块，verdict PROBE-ONLY，review PASS）→
  探针根 `workspace/exploration/nbpolar-native-highdim/step3/`
 （`results.json` keys `inputs` / `assumptions` / `rows` / `verdict`）→
  决策日志 2026-09-23 套件条目 Step-3 段 → 提交 `8eeae0d9`。
- Assumptions A1–A7（逐字）：A1 rows 为 full-native q=1024 n=32768，
  probe rows 为 CLOSED 集合 GF(32)=32×32 baseline、GF(16)×GF(64)、GF(8)×GF(128)；
  A2 SCL list L=8 full-native / L=1 probe rows，RS-kernel width l=2，iterations N/A；
  A3 每 factor-stage n=32768 symbols，split rows 对两 fields 求和；
  A4 memory 模型为每 row L·q·n float32 values（split rows 对 fields 求和）；
  A5 budget ~20 s/decode（C4 inferred）+ machine rate 1e9 float ops/s effective single-thread；
  A6 reduction paths 仅承认 probe rows 的 L=1，其余一律不计；
  A7 probe-cost bound ≤ 4× A5 decode budget（≤ ~80 s）。
  C4 ~20 s 标注 INFERRED（G2/G3 wall telemetry provenance）。
- Per-row 表（ops_c1 / ops_c2 / seconds / memory / within-budget）：
  - full-native q1024 L8：34.359738368 / 2063.597568 / 268,435,456 values / false。
  - GF(32)=32×32 L1：0.067108864 / 0.51904512 / 2,097,152 / true。
  - GF(16)×GF(64) L1：0.142606336 / 1.08920832 / 2,621,440 / true。
  - GF(8)×GF(128) L1：0.538968064 / 4.07568384 / 4,456,448 / true。
- Verdict：PROBE-ONLY + falsifier（envelope §5：probe 若不能在 bounded cost 下保留 Step-1
  separation signal，则 PROBE-ONLY 不成立）；C1-application-shape robustness（verdict C2-dominated）。

## 6. 套件级方向读数（描述性、非 claim）

- 出处：综合 §2–§5 各 packet adjudication + 决策日志 2026-09-23 套件条目 suite-reading 段；
  本节三条读数均为 L2/L3 台账上的描述性读数，不构成任何 claim。
- 三条读数：(1) 在 ±1-dominated 非对称信道上，native-vs-binarized 轴在小 q 处存在可测量的、
  有利于 native 的信号（Step-1 12/12 cell-mean 分离）；(2) 迁移先验需要 floor-aware formulation——
  当前 floor 规则输给 true-channel baseline（Step-2 kept-evidence 阴性）；
  (3) 纸面上 full native d=1024 约超出 inferred per-decode budget ~100×，
  而 GF(32)-family split probes 均在其内（与 Step-3 PROBE-ONLY 裁决一致）。
- 明确声明：本套件任何地方均无 real-data FER / efficiency / qualification / promotion 表述；
  全部数值为 L2/L3 ledger。

## 7. 产物与持久记录索引（交叉引用表）

- 出处：`exploration-index.md` §8（套件执行 packets 表）→ 各 packet `STATUS.yaml` →
  各探针根 `results.json` / `notes.md` → 决策日志 2026-09-23 三条目 →
  `AGENT_PROJECT_MEMORY.md` 头部 2026-09-23 条目 → 提交 `8eeae0d9`。
  本节表格即该链条的逐探针映射。

| 探针 | Packet dir（committed in `8eeae0d9`） | 探针根 `workspace/exploration/nbpolar-native-highdim/<root>/`（worktree-only，gitignored by design，每根 3 文件） | `results.json` / `notes.md` keys | STATUS adjudication 块 | 决策日志 2026-09-23 条目 | project-memory 2026-09-23 条目 |
|---|---|---|---|---|---|---|
| Step-0 信道勘察 | `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/` | `step0/`（`prereg.md` / `results.json` / `notes.md`） | `primary_m1` / `abs_delta_distribution` / `period_crossing` / `wrap_closure_check` / `bin_occupancy` | `NBPOLAR_EXPLORATION_STEP0_SURVEY_COMPLETE_DESCRIPTIVE`，`pass_with_comments` | Step-0 专条（§2 出处段同） | Step-0 probe result 段 |
| Step-0 M6 addendum | `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM/` | `step0-m6-addendum/`（3 文件同上） | `checks` / `occupancy`（UNMEASURABLE 终端） | `NBPOLAR_EXPLORATION_STEP0M6_ADDENDUM_COMPLETE_DESCRIPTIVE` | 套件条目 M6 段 | Step-0 M6 addendum 段 |
| Step-1 小 q 筛选 | `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/` | `step1/`（3 文件同上） | `freeze` / `gates` / `population` / `cells` | `NBPOLAR_EXPLORATION_STEP1_SCREENING_COMPLETE_DESCRIPTIVE`，PASS | 套件条目 Step-1 段 | Step-1 段 |
| Step-2 迁移先验 | `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/` | `step2/`（3 文件同上） | `freeze` / `gates` / `cells` / `m2_reference` / `arm_u_redefinition` | `NBPOLAR_EXPLORATION_STEP2_PRIOR_TRANSFER_COMPLETE_DESCRIPTIVE`，`pass_with_comments` | 套件条目 Step-2 段 | Step-2 段 |
| Step-3 纸面裁决 | `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP3-ADJUDICATION/` | `step3/`（3 文件同上） | `inputs` / `assumptions` / `rows` / `verdict` | `NBPOLAR_EXPLORATION_STEP3_ADJUDICATION_COMPLETE_DESCRIPTIVE`，PASS | 套件条目 Step-3 段 | Step-3 段 |

- Gitignore OPEN ITEM 注记：探针记录按设计 worktree-only（`workspace/*` gitignore 模式；
  仅 `workspace/probes/*` 有 negation）；未来 packet 决定 durability
  （gitignore negation vs worktree-only + decision-log 记录）——见 `exploration-index.md` §2 与 §8。

## 8. 已知记录性事项与下一道门

- Recorded nuances：Step-1/Step-2 seed-level 差异已分别 carry（§3 q4 R0.60 3/16 negative seeds；
  §4 q4 R0.60 3/16 positive g_succ seeds（audit D2 更正）；q8 R0.40 g_nll floating-noise tie cell（+0.0006）已注明；
  packet typos 在适用处 post-hoc 修正（如 Step-0 run-log attempt 数 4→2 deduped、
  M6 `rebuilds` 0→1 手工对齐，均经 review 确认）；
  reviewer future-packet 建议（machine-readable sweeps、pre-hashes、script-sourced counters）已记录、
  不在本套件执行。
- Next gates（每道门各自 packet + freeze review + 逐字授权）：任何 Tier-Y claim gate；
  floor-aware prior variant probe；Step-1 扩展（soft-MSD arm B、natural-mapping sensitivity）；
  GF(32) split-dimension probe 后续；任何 real-data 执行。
  `tasks.md` 的 O1–O4 仍为 standing unauthorized 清单。

## 9. 非 claim 声明

- 本报告不作任何 FER / efficiency / promotion / qualification / composable-key / security 表述。
- Sim/real ledgers 分离：L2（合成）与 L3（描述性勘察）数值永不并入、永不数值对比、
  永不引用为 L1 real-data FER。
- Tier-X 非 claim（per AGENTS.md §10.4）：本套件一切探针均为 Tier-X（Step-3 为 paper-only tier-N/A），
  无 candidate/accepted token，无 status 变化，无 attempt 消耗可转为 claim 的证据；
  任何 claim-bearing 门均为 Tier-Y，需独立 own packet + freeze + Pre-EXECUTE/Pre-RESULT + 逐字授权。
