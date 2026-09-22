# NB-Polar STATE — READ THIS FIRST（新会话唯一入口）

> 先读本文，再按 `§6 延伸阅读` 顺序展开。细节一律链到源文档，不在此复述。
> 本文件是 selective re-baseline：取代旧计划层叙述，保留已验证实现；旧条目作 provenance 保留。
> 凡 `描述性` = Tier-X / Tier-Y descriptive-only，non-claim，不作 FER/效率/晋级证据。
> **⚠ 2026-09-22 G3（主线 R2 已裁决）**：G3 接受 `NBPOLAR_M2_PRIOR_G3_SUCCESS`；**M2 = `VALIDATED_AT_FROZEN_CONTRACT`**（仅第二级）。三个独立评审真实发生且通过（transcript：Pre-EXECUTE `ses_f37a…` 12/12、DELTA `ses_f379…`、Pre-RESULT `ses_f377…` MAY PROCEED），但断言时未落盘；在盘独立 Pre-RESULT（`PRE_RESULT_REVIEW.md` 8/8）已补。STATUS G3-1 系转录滞后（18:02:14 关闭）。两主线程碰撞产生两条虚假时间断言（F5/F6，维持标注）。`3f5b374a` 的"Pre-EXECUTE 从未执行"系矫枉过正，已纠正（F17）。见 `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_PROCESS_DEVIATION.md`。

## 如果只读三件事

1. **leading-candidate 机制（非收敛根因）**：证据指向 M0 非参数先验的先验/地板处理（零 cell 得概率地板 1e-15；每个落地板的真 −1 delta 约 40.42 bits 伪罚；每 block ~44.7 个真 −1 中仅 ~30.4 落在 TRAIN 零 −1 列；S9 合成 B 11/16 vs A 0/16，描述性，见 §1）——但码率、构造、分配、时间相关均**未排除**；54.8σ 余量仅是理想模型下"无码率 binding 证据"，非证伪。
2. **候选方向（非已采纳基线）**：M2 ±1 先验是 **CANDIDATE 且真实数据检验已出 bounded negative**——SHG `_1` 上 δ-tail 门 FAIL（p̂=0.0050202，U=0.0052879 vs B_tail=2.0e-4，~25× 超预算；±1 前提在新数据上不成立 ⇒ 预定 STOP，不进 G2；`G1_ADJUDICATION.md`）。注意精确口径：**未证伪** M0 地板误定价机制（matched-CAL NLL 差 ~1.95 在两总体可复现），**未证伪** M2 于所有源（冻结 sessions 尾部≈0，但 ladder 已耗尽）；S9 仍不得读作 FER/效率证据。后续已推进：S11 判定该 FAIL 主因是**配对污染**（w=200 CIRCULAR 尾部 = 0）⇒ G1R2（w=200/CIRCULAR）δ-tail PASS、NLL PASS ⇒ **G2 SUCCESS `NBPOLAR_M2_PRIOR_G2_SUCCESS`（B 11/14 vs A2 0/14 严格不重叠）** ⇒ **G3 SUCCESS `NBPOLAR_M2_PRIOR_G3_SUCCESS`（主线 R2 接受；SHG `_2` 独立 session：B 8/14 Wilson [0.3259,0.7862] vs A2 0/14 [0.0,0.2153] 严格不重叠；A1 0/14 描述性无门；undetected 0 隔离；recount 0；tag_master 2026110101 G3 新鲜；一次性 g3_runs 1 reruns 0，wall 858.5 s ≤ 900；126 SC/42 tag）**。M2 在**两个解码门上均已确认**（"CANDIDATE until G3 passes" 条件记于 G2 裁决即 pre-G3 + freeze 门已过）⇒ 按预注册规则 **M2 状态进入 `VALIDATED_AT_FROZEN_CONTRACT`**（仅第二级；R2 FER 门、R3 效率门、G4 均未做，禁止跳级）；残留记录偏差见 `G3_PROCESS_DEVIATION.md`（评审未落盘；G3-1 转录滞后；F5/F6 时间断言假）。**G4（穷尽公共消息清单）仍是 D6 最后一道门**，需自己的 packet + 用户授权。绑定边界：11/14 vs 8/14 是**方向复制、非量级可比**（两个独立 session 各自过自己的 CI 门）；无 FER/效率/资格/composable key 声明；A1 两 session 均 0/14 = 描述性首次测量。
3. **什么都不许动**：无真实数据执行授权；`results/`、`comparison_bench/outputs_comparison/` 禁止覆盖；SCL 锁定；C-P2 B4 未授权。

## §1 三栏结论（描述性除非另注）

| 结论 | 条目（state strings 保持原文） | 源 |
|---|---|---|
| 已建立 | `GF(32) poly37/α2` 代数 + butterfly transform，Phase 1 独立 17/17 | `.workbuddy/queue/NBPOLAR-PHASE1-GF32-TRANSFORM/OPERATOR_RETURN.md:45` |
| 已建立 | log-domain q-ary SC reference decoder vs enumerator oracle ≤1e-12，Phase 2 独立 33/33 | `.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/INDEPENDENT_REVIEW.md:9` |
| 已建立 | Toeplitz-tag verification + disclosure counting + `undetected` isolation | `docs/nbpolar/ROADMAP.md:Phase 5`，`REAL_DATA_FEASIBILITY_STRATEGY.md` |
| 已建立 | 冻结 sessions 的 ±1 经验误差结构：`delta_mass_le1 = 1.0000`，90%/99% effective-support 统计 ≈2（采样 contexts 上，非逐符号精确支撑；描述性） | `docs/nbpolar/MACRO_PLAN_20260921.md:§1` |
| 已建立 | TimeTagger on WSL 可用；`FileReader` auto-follows `.1`（纯离线解析，无需硬件） | `AGENT_PROJECT_MEMORY.md:2026-09-21 intake`，`docs/troubleshooting.md` |
| 未确立（理想模型诊断，非证伪） | rate 在 ML/uniform-input 理想模型下无 binding 证据：冻结 K2 处 54.8σ surplus，predicted FER≈0（描述性）；SC 次优/先验失配/时间相关未排除 | `MACRO_PLAN_20260921.md:§1` |
| 未确立（偏差符号未定，非证伪） | H2 估计偏差小但符号未确立：MM 为加法修正（正确值 0.8026903611/0.8089106006，原 S2 相减写反了符号）；MM +0.29%/+0.25% vs split-half −0.31%/−0.28%，符号相反量级相当（描述性） | `MACRO_PLAN_20260921.md:§1` |
| 已证伪 | "no prior IR on ToA/HD" novelty claim：A1 = Boutros & Soljanin TCOM 2023 | `MACRO_PLAN_20260921.md:§4`，`PAPER_READ_20260921.md` |
| 已证伪 | A3 rate bounds licensed for this project：sufficient-condition 推导 + 5+5-bit 架构 out of scope | `MACRO_PLAN_20260921.md:§6` |
| 结构性担忧（性能未验证） | Gray neighbor-of-zero set = powers of α 是结构性事实；比较译码性能/full MFD verdict 未验证 | `AGENT_PROJECT_MEMORY.md:2026-09-21`，`MACRO_PLAN_20260921.md:§2` |
| 已检验（bounded negative，非证伪机制） | M2 ±1 prior on REAL data（**G1，w=500/LINEAR**）：SHG `_1` δ-tail FAIL（p̂=0.0050202 / U=0.0052879 vs B_tail=2.0e-4；±1 前提不成立 ⇒ NO G2）；NLL PASS 但 matched-32f 近无信息量（Δ=1.950667；1024 帧 incumbent arm A1 永未运行）；M0 稀疏表病理可复现（机制未证伪）；M2 仍 **CANDIDATE**、未验证 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md` |
| 已检验（描述性，契约已换） | **G1R2（w=200/CIRCULAR）**：δ-tail **PASS**（p̂=0，U=1.4986e-5——**S11 推论，非 ±1 前提的新验证**）；NLL PASS（Δ=2.1392）；CAL32 三元组 q0/q+1/q−1/q_rest = 0.7562/0.2419/0.0018/**0**；H_M2=0.8168138 / H_M0=0.6910589。**不得跨契约作优劣比较**（两契约测的是不同窗口/口径群体） | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md` |
| 已检验（描述性） | SHG `_1` δ-mass：tail 0.50%（1005/200,192），**不满足** ≤1 前提；且低于均匀 accidental 预测（普查 w=500 accidental 1.44%）——尾部非纯偶然符合；冻结 sessions 32 帧 CAL q_rest=0.0（尾部≈0）——±1 前提源相关 | `G1_ADJUDICATION.md` §2；`delta_profiles.json` |
| 已检验（bounded Tier-Y gate outcome，非 FER/效率证据） | **G2（w=200/CIRCULAR，SHG `_1` 三臂 one-shot）SUCCESS `NBPOLAR_M2_PRIOR_G2_SUCCESS`**：B（M2，matched 32f）**11/14** exact Wilson [0.5241027623, 0.9242875166] vs A2（M0，matched 32f）**0/14** Wilson [0.0, 0.2153170119]，严格不重叠；A1（M0 incumbent 1024f）0/14 描述性、无门。`undetected` 0/42 隔离；recount mismatch 0；`g2_runs: 1` / `sc_calls_on_protected: 126` / `reruns: 0`；wall 855.1 s / RSS 1.12 GiB。M2 仍 **CANDIDATE**（G3 通过前不变）；无跨契约优劣（vs G1 w=500/LINEAR bounded negative） | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/G2_ADJUDICATION.md` |
| 已检验（bounded Tier-Y gate outcome，非 FER/效率证据） | **G3（w=200/CIRCULAR，SHG `_2` 独立 session 三臂 one-shot）SUCCESS `NBPOLAR_M2_PRIOR_G3_SUCCESS`（主线 R2 接受）**：B（M2，matched 32f）**8/14** exact Wilson [0.3259026690, 0.7861949007]（p̂=0.5714285714）vs A2（M0，matched 32f）**0/14** Wilson [0.0, 0.2153170119]，严格不重叠；A1（M0 incumbent 1024f）0/14 描述性、无门。`undetected` 0/42 隔离；taxonomy {exact 8, verify_failed 34}；recount mismatch 0（tag_master 2026110101 G3-fresh；EVAL_SEED 2026100101）；`g3_runs: 1` / `sc_calls_on_protected: 126` / `reruns: 0`；wall 858.5 s / RSS 1.13 GiB。M2 为两 decode 门确认的 **confirmed candidate**（G2 11/14 + G3 8/14），状态 `VALIDATED_AT_FROZEN_CONTRACT`（仅第二级）；11/14 vs 8/14 不得跨 session 比优劣（仅方向复现）；NLL 域标签按行常量强制（`G3_NLL_DOMAINS`）；残留记录偏差见 `G3_PROCESS_DEVIATION.md`；G4 + OpenSpec archive 未完成 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md` + `G3_PROCESS_DEVIATION.md` |
| 规划输入（report-only，不采纳） | **D4 K-RESPLIT `NBPOLAR_M2_PRIOR_K_RESPLIT_D4_COMPLETE_REPORT_ONLY`**：fixed-f=1.3 ⇒ K_total **6946**（+135 vs 冻结 6811；split 335/6611）；fixed-K：f(6811)=1.2747449 / f(6946)=1.2999641（deviation −3.59e-5，R5）/ f(7020)=1.3137879；冻结 selector 6811→(328,6483) / 7020→(346,6674)。合成 genie 32 calls，`sc_calls_on_protected: 0`。G2/G3 仍冻 319/6492；fixed-f vs fixed-K 为后续 preregistered 决策 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-K-RESPLIT-D4/D4_RECORD.md` |
| 待验证 | FER/reliability/efficiency at any operating point（全项目尚无 FER 阈值） | `MACRO_PLAN_20260921.md:§5 Stage 0` |

## §2 已关闭死路（每条一行，含关闭界）

- P18/P19 0/3：disclosure-route escalation 关闭——L1 已 ~2× over-disclosed（`REAL_DATA_FEASIBILITY_STRATEGY.md`）。
- P20I/J/K：L1 +128/+256/+512 over 9 blocks，zero recovery——L1 加量关闭（memory 2026-09-18 P20K）。
- P19 `l2_plus`（K2 6492→7004，+512）0/3 ⇒ 仅证伪该旧工作点上的单次加量（3 blocks）；"more L2 disclosure" 一般方向未证伪（`REAL_DATA_FEASIBILITY_STRATEGY.md` 保留此限）。
- Route-B axis (i) disclosure placement RETIRED as ceiling-hugging（C-P1；`docs/decision-log.md:5063`）；C-P2 B4 NOT AUTHORIZED（54.8σ 余量为理想模型诊断、非证伪，`MACRO_PLAN_20260921.md:§6`）。
- λ concentration program for target priors：X08 H1 2.0066 vs raw 0.0252，K_total 33285 vs 7020。
- L1 SCL as automatic next phase：P19 true-L1 control also failed（`REAL_DATA_FEASIBILITY_STRATEGY.md:SCL entry gate`）。
- Floor-lift spike discriminator：LLR span < 20 bits 时被强制为零；floor sweep monotonic with no knee（`MACRO_PLAN_20260921.md:§8`）。
- A3/diversity-based representation pivot：表示转向需 S3+S5+S6 联合指向（`MACRO_PLAN_20260921.md:§§5–6`）。
- 任何立足 `20260121_Type2_*` 的"新 session 佐证冻结结果"：they ARE the V25 sources（`MACRO_PLAN_20260921.md:§9 F5`）。

## §3 若采用 ±1 先验的连锁后果（描述性；**pending real-data validation**）

| 改动面 | 后果 |
|---|---|
| CAL | 1024 frames → S8 单次网格描述性 minima ~2–8 frames + margin 得约 8–32（**无保证**：网格单 draw 非单调；理想 iid 下 8192 样本 SE=0.00804/0.00814 bits 已占 H2 ~1.00%/1.01%；`MACRO_PLAN_20260921.md:§9 F2`） |
| Accounting | D3 sacrifice-only 下：incumbent 牺牲 ~8× block；M2 参数计数 reveal ~20 bits 仅为诊断量、**非记账成本**；`docs/SECURITY_MODEL.md` currently has NO CAL/prior term at all（grep verified） |
| Type0 tier insufficiency | **未溶解**：CAL 缺口或可缓解，但 block 完整性与数据质量约束仍在（Type0-500K ≤146 frames；减 32 CAL 后不足 1 block） |
| Data scarcity | 冻结 sessions 上**未解除**：never-decoded 余量 **101 frames（非 261）**；32-frame CAL 后仅剩 69 frames，不足 1 个 128-frame block；P20T 接受语即 "ladder ends by exhaustion" |
| K allocation | 当前 L1 f≈2.00 / L2 f≈1.275 misallocation 必须重推导（`MACRO_PLAN_20260921.md:§2` finding A）；D4 constant-total 不成立：fixed-f 与 fixed-K_total 不可兼得（M2 H_total 下 f=1.3 ⇒ K_total 7053/7106，即 +33/+26；冻 K_total 则 f=1.2939/1.2952），且 G2 冻 K1=319/K2=6492 |
| Construction | P16 order 系旧先验下推导；B-vs-C CI 重叠仅说明二者不可区分，**非安全/等价结论**，重推导必要性未确立（B-vs-C 差 2 blocks，CI 重叠） |
| 总标记 | **以上全系 pending real-data validation（F1 仅合成），在此之前旧约束条目一律不动** |

## §4 当前授权与预算状态

- 授权状态：**G2 已裁决 `NBPOLAR_M2_PRIOR_G2_SUCCESS`（B 11/14 vs A2 0/14 严格不重叠；A1 0/14 描述性）；G3 已裁决 `NBPOLAR_M2_PRIOR_G3_SUCCESS`（主线 R2 接受；SHG `_2` 独立 session 三臂 one-shot；B 8/14 vs A2 0/14 严格不重叠；A1 0/14 描述性；M2 为两门确认的 confirmed candidate，状态 `VALIDATED_AT_FROZEN_CONTRACT` 仅第二级）**——见 `G3_ADJUDICATION.md` + `G3_PROCESS_DEVIATION.md`（残留记录偏差：评审未落盘；G3-1 转录滞后）。D4 已完成 `NBPOLAR_M2_PRIOR_K_RESPLIT_D4_COMPLETE_REPORT_ONLY`（两分支皆不采纳；G2/G3 仍冻 319/6492）。**G1** bounded negative；**G1R2** 描述性完成（δ-tail PASS 系 S11 推论）。**下一门 = G4**（exhaustive public-message inventory，D6 的 last gate）——需自己的 packet + 用户授权，当前无任何 G4 授权；SHG `_2` EVAL 已消耗、RESERVE 99 untouched，SHG `_1` RESERVE 29 untouched。
- 冻结 sessions 真实数据 ladder **已耗尽**：never-decoded 余量 101 frames，32-frame CAL 后剩 69 frames（<1 block）；验证须在 SHG 新采集上跑，并声明保留段做独立确认。
- 冻结中：一切真实数据执行（无授权不读不跑）；`results/`、`comparison_bench/outputs_comparison/` 只加不覆；benchmark/result roots 写入；SCL（5-item conjunction 未满足，锁定）；任何 promotion/qualification/FER claim；C-P2 B4；表示转向。
- 预算：route-B 2/6 used / 4 remaining（`MACRO_PLAN_20260921.md:§6`；1/6 after C-P1 RETIRE at `decision-log.md:5065`；2/6 after C-P2 freeze review at `:5079`）；Tier-X probes non-claim，ledger 按里程碑批量更新（`docs/nbpolar/PROBE_TIER.md`）；re-analysis queue 4/6（剩 Q5 + exhaustion-route decision）。
- Pending PI decisions（2026-09-22 更新：G2+G3 freeze+execute+adjudication 已完成，**route decision post-G1R2** 中 G2/G3 子项已关闭；现 pending = G4 packet 准备（需用户授权）+ 下列）：**route decision post-G1R2**（G2/G3 一次性三臂译码已完成——A1=M0@1024f incumbent / A2=M0@32f 对照 / B=M2@32f，SHG `_1`/`_2` 各 14 blocks，冻结 K1=319/K2=6492 与 P16 构造；G4 需自己的 packet + 用户授权）；K_total 选择（fixed-f vs fixed-K，D4 仍 DEFERRED，G1R2 的 H_M2 暗示 ≈6,946 vs 冻结 7,020，仅规划输入）；σ/`gate_ps=200` 不兼容；accidental-dominated H 可用性；queue 上限处的 exhaustion-route；Type0 source verification。（已决：G1 用 (N) W_P=500/W_S=200；**G1R2 改用 W_P=200 + MOD=CIRCULAR**——后者经 delta 评审，且其"无需改 runner"的原始断言被独立评审否证后已修正。）
- Branch `codex/nbpolar-phase0`；本文件建立时的 last commit `5f9ec273`（provenance，**非**当前 HEAD——当前 HEAD 见 `git log -1`）。

## §4.1 M2 promotion ladder（状态阶梯**定义**；本节不授予任何晋级）

> 2026-09-22 主线裁定，源自 `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` §5，并补入 G3 三态、失败分层口径与 G4。
> **M2 状态（2026-09-22 G3 裁决后）= `VALIDATED_AT_FROZEN_CONTRACT`**（第一道真实数据 decode 门 G2 + 独立 session 门 G3 双过，按本表第一行进入；仅第二级——R2 FER 门、R3 效率门、G4 inventory 均未做，禁止跳级）。晋级依据：pre-G3 的 "CANDIDATE until G3 passes" 规则（记于 G2 裁决）+ `g3_freeze_config.json` 17:00:07 的预注册门。**注意**：本 §4.1 阶梯文档本身写于 decode 后 ≈17:58（主线程 `ses_f3ffe4fc…`），不得引为 pre-decode preregistration；`0851b481` 的替换编辑已被 `3f5b374a` 恢复、本次提交 reaffirm。见 `G3_PROCESS_DEVIATION.md` F10。本表只定义状态的进入条件，不构成授权。

```text
CANDIDATE
  → (G3 预注册门 PASS)                                    VALIDATED_AT_FROZEN_CONTRACT
  → (R2 门过：预注册 FER 口径 + 样本量达标)                 FER_MEASURED_AT_CONTRACT
  → (R3 门过：verification-aware f_eff + 运行时/RSS 上界)   EFFICIENCY_ACCOUNTED
  → (≥2 独立 session 复现 + 样本量 + G4 exhaustive
     public-message inventory + 独立 Pre-RESULT 全过)       READY_FOR_QUALIFICATION
任一 FAIL 或 INCONCLUSIVE：回 CANDIDATE 或 BOUNDED_NEGATIVE。禁止跳级；
禁止用合成 S9 推级；禁止用跨契约（G1 w=500 vs G1R2/G2 w=200）优劣叙事推级。
```

**G3 裁决三态 → 状态串**（**decode 之前**写入 packet，避免裁决夜现编）：

| 结果 | 状态串 |
|---|---|
| PASS —— Wilson-lower(B) > Wilson-upper(A2) | `NBPOLAR_M2_PRIOR_G3_SUCCESS` |
| FAIL / INCONCLUSIVE / premise 层未过（执行干净） | `NBPOLAR_M2_PRIOR_G3_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`，失败层写进**正文**，不另造标签 |
| 执行事故（`resource_abort` / invalid-run） | **不产生**科学状态串；按 freeze 重冻规则，不改状态、不重跑不调参 |

分层定义：**FAIL** = point(B) ≤ point(A2)；**INCONCLUSIVE** = 点估计占优但 Wilson CI 重叠，**或** EVAL < 14 完整块（COMPLETE-BLOCKS-ONLY ⇒ INSUFFICIENT）；**premise 层** = 继承的 `B_tail` / `Δ_min` 门未过。三者都只回 CANDIDATE，M2 不升不降。

> 裁定说明（与路线图建议的两处差异）：(1) 负面标签沿用 G1 家族 `…_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE` 而非路线图的 `…_G3_BOUNDED_NEGATIVE`，以便与 `…_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE` 同族 grep；(2) **不采纳** `…_PREMISE_FAIL` 独立标签——G1 的 δ-tail premise FAIL 本就折进 bounded-negative 标签，G3 保持同一约定，premise 层只在正文分层。

## §5 定位（R1/R2/R3 一句话）

- 对象是 CW time-energy-entanglement ToA 编码的 IR 部分；`600k`/`1p2M` 是数据尺度参数；删除一切"无人在 ToA/高维做过 IR"表述（A1 即该工作）。见 `MACRO_PLAN_20260921.md:§§0,4`。

## 已修正（2026-09-21 review）
- C1：地板定价 ~4e-18/48 bits ⇒ 概率地板 1e-15 / 40.4214 bits（`body.py:141-143`）。
- C2：每 block ~45 真 −1 全被地板 ⇒ 仅 30.3509/44.7185 落在 TRAIN 零 −1 列。
- C3：MM "corrected H2" 0.7980427484/0.8048907456 ⇒ MM 为加法，正确值 0.8026903611/0.8089106006（`body.py:240` 相减写反）。
- C4："±0.3% ⇒ H2 misestimation REFUTED" ⇒ 偏差小但符号未确立（MM 正 vs split-half 负），非证伪。
- C5：never-decoded 余量 "261 frames" ⇒ 101 frames；32-frame CAL 后剩 69 frames（<1 block），冻结 ladder 耗尽。

## §6 延伸阅读（按序）

1. `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md`（R0–R4 执行序：G3 收口 → 可重复 → FER → 效率 → 论文；planning proposal）
2. `docs/nbpolar/MACRO_PLAN_20260921.md` §§0–9（候选结论 S8/S9/S10 F1–F6，2026-09-21 review 已修正）
3. `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md`（当前 route 与 stop rules）
4. `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`（先验契约冻结）
5. `docs/nbpolar/CRITICAL_PATH.md`，`ROADMAP.md`（串行顺序与 phase gates）
6. `docs/nbpolar/PAPER_READ_20260921.md`，`LITERATURE_FIT_CHECK_20260921.md`（文献口径）
7. `docs/decision-log.md` 2026-09-21 条目；`AGENT_PROJECT_MEMORY.md` 最新条目
8. `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/`（**已接受** `NBPOLAR_M2_PRIOR_STAGE1_IMPLEMENTATION_COMPLETE_ACCEPTED`：`prior_m2.py` + T1–T12 测试 + Spec-5 runner + `SECURITY_MODEL.md` CAL note；独立评审 PASS_WITH_COMMENTS 零阻塞；decoder-free、合成 fixture、零数据接触）与 `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/`（**G1 已执行并裁决** `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`：δ-tail FAIL / NLL PASS（近无信息量）；记录 `G1_ADJUDICATION.md`、`FREEZE_REVIEW.md`、`g1_freeze_config.json`；父包 `STATUS.yaml` `g1_outcome`）；并续 `NBPOLAR-S11-SHG-TAIL-NATURE/`（S11：尾部主因是配对污染，far-offset 基线非均匀）、`NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/`（G1R2 描述性 PASS，δ-tail PASS 系 S11 推论）、`NBPOLAR-M2-PRIOR-G2-DECODE/`（**G2 SUCCESS** `NBPOLAR_M2_PRIOR_G2_SUCCESS`）、`NBPOLAR-M2-PRIOR-K-RESPLIT-D4/`（D4 report-only，两分支皆不采纳）、`NBPOLAR-M2-PRIOR-G3-CONFIRM/`（**G3 SUCCESS** `NBPOLAR_M2_PRIOR_G3_SUCCESS`，主线 R2 接受；SHG `_2` 独立 session 确认；`G3_ADJUDICATION.md` + `G3_PROCESS_DEVIATION.md`；三 chat 评审真实通过但未落盘，在盘 Pre-RESULT 8/8；残留偏差见 deviation F5/F6/F15–F17；M2 `VALIDATED_AT_FROZEN_CONTRACT` 仅第二级）。下一步门：**G4 packet 准备**（穷尽公共消息清单，D6 最后一道门；需自己的 packet + 用户授权，未授权前不做任何 G4 工作）。
