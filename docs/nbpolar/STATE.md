# NB-Polar STATE — READ THIS FIRST（新会话唯一入口）

> 先读本文，再按 `§6 延伸阅读` 顺序展开。细节一律链到源文档，不在此复述。
> 本文件是 selective re-baseline：取代旧计划层叙述，保留已验证实现；旧条目作 provenance 保留。
> 凡 `描述性` = Tier-X / Tier-Y descriptive-only，non-claim，不作 FER/效率/晋级证据。

## 如果只读三件事

1. **根因已收敛**：plateau 不是码率/披露量/构造，而是 M0 非参数先验把稀疏 rare cell 定价到 ~4e-18（每个真 −1 delta 约 48 bits 伪罚）；S9 合成 B 11/16 vs A 0/16（描述性，见 §1）。
2. **唯一在前方向**：在冻结 K1/K2 上用真实数据检验 M2 ±1 先验（已接受 block 先行）；S9 在真实验证前不得读作 FER/效率证据。
3. **什么都不许动**：无真实数据执行授权；`results/`、`comparison_bench/outputs_comparison/` 禁止覆盖；SCL 锁定；C-P2 B4 未授权。

## §1 三栏结论（描述性除非另注）

| 结论 | 条目（state strings 保持原文） | 源 |
|---|---|---|
| 已建立 | `GF(32) poly37/α2` 代数 + butterfly transform，Phase 1 独立 17/17 | `.workbuddy/queue/NBPOLAR-PHASE1-GF32-TRANSFORM/OPERATOR_RETURN.md:45` |
| 已建立 | log-domain q-ary SC reference decoder vs enumerator oracle ≤1e-12，Phase 2 独立 33/33 | `.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/INDEPENDENT_REVIEW.md:9` |
| 已建立 | Toeplitz-tag verification + disclosure counting + `undetected` isolation | `docs/nbpolar/ROADMAP.md:Phase 5`，`REAL_DATA_FEASIBILITY_STRATEGY.md` |
| 已建立 | 冻结 sessions 的 ±1 经验误差结构：`delta_mass_le1 = 1.0000`，posterior support 2.0（描述性） | `docs/nbpolar/MACRO_PLAN_20260921.md:§1` |
| 已建立 | TimeTagger on WSL 可用；`FileReader` auto-follows `.1`（纯离线解析，无需硬件） | `AGENT_PROJECT_MEMORY.md:2026-09-21 intake`，`docs/troubleshooting.md` |
| 已证伪 | rate/finite-length 是 plateau 主因：冻结 K2 处 54.8σ surplus，predicted FER≈0（描述性） | `MACRO_PLAN_20260921.md:§1` |
| 已证伪 | H2 misestimation：two estimators ±0.3%（描述性） | `MACRO_PLAN_20260921.md:§1` |
| 已证伪 | "no prior IR on ToA/HD" novelty claim：A1 = Boutros & Soljanin TCOM 2023 | `MACRO_PLAN_20260921.md:§4`，`PAPER_READ_20260921.md` |
| 已证伪 | A3 rate bounds licensed for this project：sufficient-condition 推导 + 5+5-bit 架构 out of scope | `MACRO_PLAN_20260921.md:§6` |
| 已证伪 | Gray labeling as MFD fix：Gray neighbor-of-zero set = powers of α = polar generator rows 产物 ⇒ 结构性 WORSE | `AGENT_PROJECT_MEMORY.md:2026-09-21`，`MACRO_PLAN_20260921.md:§2` |
| 待验证 | ±1 parametric prior on REAL data（S9 仅合成 16 blocks，pro-±1 ground truth；描述性） | `MACRO_PLAN_20260921.md:§9 F1` |
| 待验证 | SHG/Type0 sources 是否也有 δ-mass ≤1 | `MACRO_PLAN_20260921.md:§9 F4–F5` |
| 待验证 | FER/reliability/efficiency at any operating point（全项目尚无 FER 阈值） | `MACRO_PLAN_20260921.md:§5 Stage 0` |

## §2 已关闭死路（每条一行，含关闭界）

- P18/P19 0/3：disclosure-route escalation 关闭——L1 已 ~2× over-disclosed（`REAL_DATA_FEASIBILITY_STRATEGY.md`）。
- P20I/J/K：L1 +128/+256/+512 over 9 blocks，zero recovery——L1 加量关闭（memory 2026-09-18 P20K）。
- P19 `l2_plus`（K2 6492→7004，+512）0/3 ⇒ "more L2 disclosure" falsified。
- Route-B axis (i) disclosure placement RETIRED as ceiling-hugging（C-P1；`docs/decision-log.md:5063`）；C-P2 B4 NOT AUTHORIZED（54.8σ surplus 旋钮，`MACRO_PLAN_20260921.md:§6`）。
- λ concentration program for target priors：X08 H1 2.0066 vs raw 0.0252，K_total 33285 vs 7020。
- L1 SCL as automatic next phase：P19 true-L1 control also failed（`REAL_DATA_FEASIBILITY_STRATEGY.md:SCL entry gate`）。
- Floor-lift spike discriminator：LLR span < 20 bits 时被强制为零；floor sweep monotonic with no knee（`MACRO_PLAN_20260921.md:§8`）。
- A3/diversity-based representation pivot：表示转向需 S3+S5+S6 联合指向（`MACRO_PLAN_20260921.md:§§5–6`）。
- 任何立足 `20260121_Type2_*` 的"新 session 佐证冻结结果"：they ARE the V25 sources（`MACRO_PLAN_20260921.md:§9 F5`）。

## §3 若采用 ±1 先验的连锁后果（描述性；**pending real-data validation**）

| 改动面 | 后果 |
|---|---|
| CAL | 1024 frames → ~8–32（S8 1% minima ~2–8 frames + margin；`MACRO_PLAN_20260921.md:§9 F2`） |
| Accounting | prior cost ~8× block → reveal ~20 bits；`docs/SECURITY_MODEL.md` currently has NO CAL/prior term at all（grep verified） |
| Type0 tier insufficiency | S10 全 INSUFFICIENT ⇒ dissolved（Type0 已有 ≥144 frames ≥ 新 CAL 需求） |
| Data scarcity | 10-acquisition intake 的动因 ⇒ dissolved |
| K allocation | 当前 L1 f≈2.00 / L2 f≈1.275 misallocation 必须重推导（`MACRO_PLAN_20260921.md:§2` finding A） |
| Construction | P16 order 系旧先验下推导；S9：为安全无需重推导，但 order suboptimal（B-vs-C 差 2 blocks，CI 重叠） |
| 总标记 | **以上全系 pending real-data validation（F1 仅合成），在此之前旧约束条目一律不动** |

## §4 当前授权与预算状态

- 授权中：下一个真实数据 packet 优先检验 M2 先验（冻结 K1=319/K2=6492，已接受 block 先行）——仍需独立 freeze + 显式用户授权（`MACRO_PLAN_20260921.md:§§5,9`）。
- 冻结中：一切真实数据执行（无授权不读不跑）；`results/`、`comparison_bench/outputs_comparison/` 只加不覆；benchmark/result roots 写入；SCL（5-item conjunction 未满足，锁定）；任何 promotion/qualification/FER claim；C-P2 B4；表示转向。
- 预算：route-B 2/6 used / 4 remaining（`MACRO_PLAN_20260921.md:§6`）；Tier-X probes non-claim，ledger 按里程碑批量更新（`docs/nbpolar/PROBE_TIER.md`）；re-analysis queue 4/6（剩 Q5 + exhaustion-route decision）。
- Pending PI decisions：pairing-rule contract（W vs N + window）；σ/`gate_ps=200` 不兼容；accidental-dominated H 可用性；queue 上限处的 exhaustion-route（redesign/acquisition/closeout）；(N)-H window/gate contract；Type0 source verification。
- Branch `codex/nbpolar-phase0`；本文件前 last commit `5f9ec273`。

## §5 定位（R1/R2/R3 一句话）

- 对象是 CW time-energy-entanglement ToA 编码的 IR 部分；`600k`/`1p2M` 是数据尺度参数；删除一切"无人在 ToA/高维做过 IR"表述（A1 即该工作）。见 `MACRO_PLAN_20260921.md:§§0,4`。

## §6 延伸阅读（按序）

1. `docs/nbpolar/MACRO_PLAN_20260921.md` §§0–9（收敛结论 S8/S9/S10 F1–F6）
2. `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md`（当前 route 与 stop rules）
3. `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`（先验契约冻结）
4. `docs/nbpolar/CRITICAL_PATH.md`，`ROADMAP.md`（串行顺序与 phase gates）
5. `docs/nbpolar/PAPER_READ_20260921.md`，`LITERATURE_FIT_CHECK_20260921.md`（文献口径）
6. `docs/decision-log.md` 2026-09-21 条目；`AGENT_PROJECT_MEMORY.md` 最新条目
