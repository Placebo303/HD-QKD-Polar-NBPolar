# NB-Polar STATE — READ THIS FIRST（新会话唯一入口）

> 先读本文，再按 `§6 延伸阅读` 顺序展开。细节一律链到源文档，不在此复述。
> 本文件是 selective re-baseline：取代旧计划层叙述，保留已验证实现；旧条目作 provenance 保留。
> 凡 `描述性` = Tier-X / Tier-Y descriptive-only，non-claim，不作 FER/效率/晋级证据。
> **⚠ 2026-09-22 G3（主线 R2 已裁决）**：G3 接受 `NBPOLAR_M2_PRIOR_G3_SUCCESS`；~~**M2 = `VALIDATED_AT_FROZEN_CONTRACT`**（仅第二级）~~ ~~**（2026-09-29 晋级：M2 = `FER_MEASURED_AT_CONTRACT`，第 3 级，见下方 §0 2026-09-29 与 §4.1）**~~ **（2026-09-30 PI 批准晋级：M2 = `EFFICIENCY_ACCOUNTED`，第 4 级，见下方 §0 2026-09-30 PI 裁定与 §4.1）**。三个独立评审真实发生且通过（transcript：Pre-EXECUTE `ses_f37a…` 12/12、DELTA `ses_f379…`、Pre-RESULT `ses_f377…` MAY PROCEED），但断言时未落盘；在盘独立 Pre-RESULT（`PRE_RESULT_REVIEW.md` 8/8）已补。STATUS G3-1 系转录滞后（18:02:14 关闭）。两主线程碰撞产生两条虚假时间断言（F5/F6，维持标注）。`3f5b374a` 的"Pre-EXECUTE 从未执行"系矫枉过正，已纠正（F17）。见 `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_PROCESS_DEVIATION.md`。

## §0 2026-09-29 更新（R2 FER 门过，主线程裁定）

> **R2 测量 `r2-fer-shg-64` 主线程裁定（2026-09-29）**：独立 Pre-RESULT 审查
> **PASS**（`workspace/r2_fer_shg_64/PRE_RESULT_REVIEW.md`）。按冻结判定规则：
> `D=64≥56`、`undetected=0`、`fidelity_compromised=false` ⇒ 裁定
> **`FER_MEASURED_AT_CONTRACT`**。**M2 状态由 `VALIDATED_AT_FROZEN_CONTRACT`
> （第 2 级）晋级为 `FER_MEASURED_AT_CONTRACT`（第 3 级）**。配置：M2 +
> SCL(L=16, top_m=4, CRC-16)，K1=319/K2=6492，P16 digest
> `055c906472dd…faea1b`；SHG `_1`/`_2` 全会话冻结 64 块池；pooled
> `p̂=0.03125`，Wilson 95% CI `[0.008612, 0.106975]`；分层 `stratum_task`
> 27/28、8/8、27/28，`stratum_official` 15/16、20/20、27/28；`undetected=0`、
> `resource_abort=0`；记账 `f_book`（含 CRC）G2=1.275343/G3=1.268101。
> 适用域仅限 2026-01-13 两次 SHG 采集自身条件（D-ACQ-05）。Caveats：(a) 仅
> SCL 一臂，无同批二元基线对照；(b) A1_CAL/HELDOUT 是首次 SCL 观测；(c) 本次
> 预算数字是本次执行专用确认，非 D-ACQ-06 一般性重裁；(d) 64 块 CI 较宽
> （上界 0.107）；(e) 吞吐约 60 符号/s，远不满足实时。下一门 = **R3**（效率
> 门：verification-aware f_eff + 运行时/RSS 上界），尚未开始，本次不晋级到
> R3 或更高级。详见 `docs/decision-log.md` 2026-09-29 条目、
> `workspace/r2_fer_shg_64/RESULT_SUMMARY.md`。
> （2026-09-30 注：约 60 符号/s 为 scl_joint 参考实现；原生实现见 docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md。）

> **二元基线 `r2-binary-baseline-shg-64` 主线程裁定（2026-09-29）**：SC 主臂 PASS_WITH_COMMENTS 已发布；CA-SCL 副臂 FAIL/INVALID（`decode_batch` 把冻结位当 0 的实现缺陷）。结论句：在 SHG `_1`/`_2` 同一 64 块池上，冻结原生二元 Polar 分层基线（独立比特面、SC、N=4096、PW 构造、MC 码率分配）在 f_book≈4.1–4.8 时块失败率为 0.61–0.94；同池 NB-Polar（M2+SCL L=16）在 f_book≈1.27 时失败率为 0.031。
> caveats：独立层模型 f 下限≈2.57、网格未覆盖块失败率≈0.03 区间、f(m) 非单调属 MC 噪声、适用域仅限两次 SHG。下一步候选：修复 CA-SCL 后仅重跑 pass2（须 PI 授权）或另立条件化 MSD 合同；见 `docs/decision-log.md`、`workspace/r2_binary_baseline_shg_64/RESULT_SUMMARY.md`。

> **R2B `r2b-fer-shg-64-L32-f120` 主线程裁定（2026-09-29）**：同一 64 块池，M2 + 原生 SCL(L=32)，K_total=6442（f_book≈1.20）：50/64 exact，p̂=0.219（Wilson [0.135, 0.334]），undetected 0，14/14 失败为 L2。Pre-RESULT PASS_WITH_COMMENTS。**f≈1.20 不是可用工作点**；合成 Tier-X 同点 p̂=0.031，真实点估计约 7 倍。M2 状态不变（`FER_MEASURED_AT_CONTRACT` 仍以 f≈1.27、L=16 的 R2 为准）。R2C（最强二元 MSD+SCL）合同 D1–D8 已批准，实现中。见 `workspace/r2b_fer_shg_64_L32_f120/RESULT_SUMMARY.md`。

> **R2E `r2e-fer-shg-64-L32-f124` 主线程裁定（2026-09-29）**：R2D 选定 K 点（K_total=6657，f_book≈1.24）的正式 Tier-Y 测量，M2 + 原生 SCL(L=32)：61/64 exact，p̂=0.047（Wilson [0.016,0.129]），undetected 0；3/3 失败为 verify_failed（L2：gbi23 G2 已知难块 0/84、gbi53 G3 8/8、gbi59 G3 311/11972）。Pre-RESULT 独立审查 PASS（R1–R9；`run.log` 缺 EXIT 行以 DONE+64parts+`results.json`+零Traceback 实质替代，未手工补写）。分层：EVAL 25/3，其余层 0 失败；selection 分层 clean-G3 30/2 仅描述，主判定为 64 块汇总。描述性：与 R2 f≈1.27 点未见可分辨劣化。M2 状态不变（`FER_MEASURED_AT_CONTRACT` 仍以 f≈1.27、L=16 的 R2 为准）；工作点是否从 f≈1.27 换到 f≈1.24 由 PI 决定。见 `workspace/r2e_fer_shg_64_L32_f124/RESULT_SUMMARY.md`。
> **PI 2026-09-30：保持 f≈1.27（L=16）为主工作点**；f≈1.24/L=32 记为已测备选点。

> **R2C `r2c-strong-binary-msd-shg-64` 主线程裁定（2026-09-30）**：最强二元臂（硬前缀 MSD + SCL L=16，无 CRC，genie-MC 构造，逐层 μ_i）同一 64 块池：f=1.20 0/64 exact；f≈1.27（NB 同披露量）46/64（G2 30/32、G3 16/32）；f≈1.31 64/64；f≈1.41 64/64；undetected 0。Pre-RESULT PASS_WITH_COMMENTS。二元约 3% 块失败所需 f 在 1.28–1.313，**NB-Polar 领先约 0.01–0.04**（不可点估；二元未做 CRC/软前缀/更大 L，不宣称最优）。见 `workspace/r2c_strong_binary_msd_shg_64/RESULT_SUMMARY.md`。

> **收尾（2026-09-30）**：R3 效率记账完成——f_book G2 1.275343 / G3 1.268101，f_eff 点值 G2 ≈1.3165 / G3 ≈1.3090（pooled 上界 G2 ≈1.428 / G3 ≈1.420），
> 运行时上界 39.38 s/块（原生 L=32 最大值论证，非 L=16 实测），独立审查 PASS
> （见 `docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md`）。总报告 `docs/nbpolar/NBPOLAR_FINAL_REPORT_20260930.md`（11 章，独立审查 PASS）。
> 仓库清理：`.gitignore` 追加 4 条原生编译产物规则；其余先存改动（stat 脏内容无变化的测试文件、pytest 证据、测试夹具）一律不碰不提交。
> **PI 2026-09-30 裁定：批准 M2 晋级 `EFFICIENCY_ACCOUNTED`（第 4 级）**。依据：R3 门四项完整性（(a)§3.2 每量有公式/数值/文件来源；(b)λ 分解表逐项；(c)运行时/RSS 表完整且上界论证写明；(d)独立审查 PASS）全满足。**晋级不代表 f≤1.3**：f_book≈1.27；计入块失败后 f_eff≈1.31–1.32；按 95% 置信区间上界 f_eff_upper≈1.42–1.43。三档并列，不得只引其中一档。`READY_FOR_QUALIFICATION` 仍不满足：64 块远不足路线图目标约 1000 块（FER<0.003）；G2/G3 是否算 ≥2 独立会话暂不裁定（同日同装置，独立性偏弱；建议未来做一次不同日期采集）。后续方向：先做净密钥产出比较（已完成，见 `docs/nbpolar/NET_SECRET_KEY_COMPARISON_20260930.md`）。

## §0 2026-09-27 更新（合成 Tier-X，描述性）

> **⚠ 已撤回（2026-09-27 补充）**：下方 C1–C3 三条结论已撤回。根因是合成两层 GF32 探针本地内联的先验表构造符号写反（`table[a,b]=pmf[(a-b)%Q]`，应为 `pmf[(b-a)%Q]`），把镜像信道喂给了译码器；详见 `docs/decision-log.md` 2026-09-27「合成两层 GF32 探针 table 符号缺陷确认」条目。**真实数据 M2 状态不受影响**（`prior_m2.py` 拟合/展开路径与本缺陷无关）。

> **符号修正后重跑（2026-09-27，描述性 Tier-X，`DESCRIPTIVE_TIER_X_REVIEWED`，独立 FOCUSED_REVIEW 双 PASS）**：`op-fix-n1024-alloc`（N=1024，设计 H1+H2=0.931679）与 `op-fix-n32k-alloc`（N=32768，设计 H1+H2=0.931629）均对齐信道真值 `H_F4=0.931830`。用修正表，N=32768 在 `f_book=1.30` 时 operational exact 在占比 14% 处升至 13/16，而真实数据占比 4.7%（319/6811）处 operational 仍为 0/16（oracle 同点 16/16）——本合成信道下低占比处失效的是 L1 译码层；`f_book=1.15` 在全部四个占比上 operational 均为 0/16；N=1024 网格上 operational 峰值占比随 `f` 增大右移。边界：合成 F4 尾部质量非零（`p_delta_rest=0.005` 分散于 1021 符号），真实 G1R2 CAL32 `q_rest=0`，占比最优点**不可**外推到真实冻结口径 K1=319/K2=6492；无 FER/效率/R2 sizing/晋级主张。详见 `docs/decision-log.md` 2026-09-27「符号修正后重跑分配网格」条目，`workspace/op-fix-n1024-alloc-packet/FOCUSED_REVIEW.md`，`workspace/op-fix-n32k-alloc-packet/FOCUSED_REVIEW.md`。

> 全部为合成域 Tier-X、non-claim；不改任何状态串，不作 FER/效率/晋级/R2 sizing 输入。汇总见 `docs/nbpolar/SYNTHESIS_20260927.md`。

- **范围**：六个合成 Tier-X 探针（C1 + k1 剂量粗/细网格 + 固定总量配比 + 固定配比缩放 + 低总量配比 + 峰带细化），F4@q1024、N=1024、每点 32 blocks、各自 one-shot。
- （已撤回）**C1**：k1=10 时 operational 0/32 而 oracle 32/32 ⇒ operational 全灭的一阶原因是 **L1 披露不足**，不是 L2 信息集。
- （已撤回）**C2**：固定总量 560（2800 bits，f_book≈2.93）下，仅改 k1/k2 配比即可使 operational 从 0/32 升至 28/32；峰值为平台，k1≈80–100 最高，宽约 k1∈[60,120]。
- （已撤回）**C3**：最优配比随总量移动；总量 448 最高仅 1/32，总量 336 全零。
- **⚠ 主线程 caveat（新，重要）**：合成 N=1024 比真实 N=32768 短 32×；N=1024 下 f≈2.93 的地板很可能由**有限码长损失**主导，因此 C3 / SYNTHESIS §4 的"仅靠重分配到不了 f≈1.27"**不得**套用到真实区间——真实 G2/G3 已在 f≈1.275 取得 11/14 与 8/14。N=32768 合成配比跟进探针进行中（id `op-n32k-ratio`）。
- **描述性对照**：真实 K1 占比 = 319/6811 ≈ 4.7%，合成峰带 k1 占比 ≈ 14–18%（仅描述，不构成推荐，不外推）。
- **状态不变**：M2 = `VALIDATED_AT_FROZEN_CONTRACT`；R2 合同**未冻结**（D-ACQ-02/03/05/06 仍 PENDING，决策卡见 `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md`）；冻结 K1/K2 = 319/6492 不变；SCL 锁定。

> **N=32768 分配网格补充探针（2026-09-27，描述性 Tier-X，`op-n32k-fine-f4` PASS / `op-n32k-matched` PASS_WITH_COMMENTS）**：F4 细网格 `op-n32k-fine-f4`（占比 11/14/17%）operational exact/16 —— f1.20: 2/1/0，f1.25: 6/10/1（oracle 8/1/0、15/10/1）。真实匹配信道 `op-n32k-matched`（信道=真实 G1R2 CAL32 三元组 p0=0.7562/p(δ=-1)=0.2419/p(+1)=0.0018，H=0.81651；占比 2/4.69/9/14%）operational exact/16 —— f1.15: 0/1/0/0，f1.20: 0/10/0/0，f1.30: 0/13/14/4（oracle 5/1/0/0、14/13/0/0、16/16/14/4；另有 25 个隔离的 `decode_failed`，零似然冲突，未使用 floor）。描述性观察：真实占比 4.69% 在 f≈1.20–1.30 已接近该网格最优（13/16 vs 全局最优 14/16）；匹配信道 f≈1.30 的 13–14/16 与真实 G2/G3 在 f≈1.275 的 11/14、8/14 方向一致（跨域对照，非幅值可比）；分配杠杆在 f≤1.20 未达到 M-usable FER≤0.02 目标（SC 最优仅 10/16 于 f1.20）。规划含义（非结论）：下一杠杆是译码器强度（SCL），修正案另行起草中。详见 `docs/decision-log.md` 2026-09-27「N=32768 分配网格补充探针」条目，`workspace/op-n32k-fine-f4-packet/FOCUSED_REVIEW.md`，`workspace/op-n32k-matched-packet/FOCUSED_REVIEW.md`。

> **PI 裁决（2026-09-27，落盘见 `docs/decision-log.md` 同日"PI 裁决三项"条目）**：SCL 锁对**合成 Tier-X 门**部分解除（按 `openspec/changes/nbpolar-scl-lock-amendment/` 修订，T1 DECIDED：CRC-16 计入披露、L∈{4,8,16}、M=4 联合候选实现约束、工作点 `G1R2-matched@q1024` f_book≈1.20 / k1 份额 4.69%，16 blocks）；**真实数据 SCL 仍锁定**（design D5 不变）。R2 测量合同 D-ACQ-06（执行预算）已 DECIDED（`wall_per_block=40s`/`rss_per_block=2GiB`/`wall_total=5400s`/本机单进程独占，超预算 STOP 不调参）；D-ACQ-02/03/05 仍 PENDING，R2 合同**仍未冻结**。另授权一项只读 G2/G3 逐块记录分层失败归因分析（Analysis B，不读原始数据、不解码）。以上均不改 M2 状态串、不改冻结 K1=319/K2=6492。

> **SCL 合成门 T2/T3 执行结果（2026-09-27，Tier-X，独立 focused review PASS_WITH_COMMENTS，`workspace/scl-gate-t3-packet/FOCUSED_REVIEW.md`）**：T2 新模块 `scl_joint.py`（CRC-16 联合 M=4 两层 SCL）+ 聚焦测试 22 passed。T3 在 `G1R2-matched@q1024`（N=32768，f_book≈1.20）两点各 16 blocks：A 点（k1 份额 4.69%）SC 10/16 → SCL/oracle 在 L16 均 16/16 ⇒ 按 T1 判定线 **unlock-for-real-data-candidate**（L1 主导情形）；B 点（k1 份额 9%）SC 0/16 → SCL/oracle 在 L16 均 7/16（逐块完全相同）⇒ **list-decoding-insufficient**（L2 主导情形）。全部 `undetected=0`、`decode_failed=0`。真实数据 G2/G3 失败块 8/9 为纯 L2（对应 B 类而非 A 类）⇒ **T5（真实数据 Tier-Y 骨架）暂缓，不自动准备**。详见 `docs/decision-log.md` 2026-09-27「SCL 合成门 T3 执行结果与主线程裁决」条目。不改 M2 状态串、不改冻结 K1=319/K2=6492、R2 仍未冻结、真实数据 SCL 仍锁定（D5）。

> **真实数据 G2/G3 B 臂失败块 SCL 重解（2026-09-28，PI 授权，描述性诊断，Pre-EXECUTE `PASS_WITH_COMMENTS` / Pre-RESULT `PASS`）**：`workspace/m2_scl_rescue_g2g3/` 对 SC 冻结路径下失败的 9 个真实数据 B 臂块（G2 3 个 + G3 6 个）跑 CRC-16 辅助 joint SCL(L=16, top_m=4) 重解。9/9 块保真性核对（SC 复现 vs `per_block_outcomes.jsonl` 五字段）全部一致。救回 8/9（G2 2/3、G3 6/6，G2 block 5 仍失败，L2 有 78 个错误符号），`undetected=0`。**结论仅限**："在 SC 冻结路径下失败的 9 个真实数据 B 臂块中，CRC-16 辅助 joint SCL(L=16, top_m=4) 对同批失败块重解，救回 8/9（G2 2/3、G3 6/6），undetected=0；SCL 是否会保持或破坏 SC 原本成功的 19 个块，本次未在真实数据上测试，不作声称。" 不改 M2/G2/G3 状态串、不改冻结 K1=319/K2=6492、R2 仍未冻结、真实数据 SCL 仍不是已采纳基线（design D5 不变）。详见 `docs/decision-log.md` 2026-09-28「真实数据 G2/G3 B 臂失败块 SCL 重解（描述性诊断，PI 授权）」条目。

> **真实数据 B 臂 28 块 SCL(L=16) 合并结果（2026-09-28，PI 授权"19 块也跑"，描述性诊断，Pre-EXECUTE `PASS` / Pre-RESULT `PASS`）**：`workspace/m2_scl_check_g2g3_success/` 对 SC 冻结路径下**成功**的 19 个真实数据 B 臂块（G2 11 个 + G3 8 个）跑同一 CRC-16 辅助 joint SCL(L=16, top_m=4) 做保真性保持检查，19/19 块保真核对全部通过（`preserved_exact=19`、`broken=0`、`undetected=0`）。与前驱包（`workspace/m2_scl_rescue_g2g3/`，commit `326594ca`，救回失败块 8/9）合并后，28 个真实数据 B 臂块（G2 14 + G3 14）在 SCL(L=16) 下合计 **27/28 exact**（G2 13/14、G3 14/14），仅 G2 block 5 仍 `verify_failed`（该块在 SC 与 SCL 两条路径下均失败，L2 有 78 个错误符号），`undetected=0`；对照同 28 块在 SC 下为 19/28（G2 11/14、G3 8/14）。**边界（不得外推）**：这不是 FER 门、不是 R2 结果、不是晋级依据；M2/G2/G3 状态串、冻结 K1=319/K2=6492 均未改动；R2 仍未冻结（D-ACQ-02/03/05 PENDING）；真实数据 SCL 仍不是已采纳基线（design D5 不变）。详见 `docs/decision-log.md` 2026-09-28「真实数据 G2/G3 B 臂 28 块 SCL(L=16) 描述性合并：27/28（PI 授权）」条目。

> **数据使用规则修订 R1–R5 采纳（2026-09-28，PI 裁决 "按建议批准，继续推进"，T1 DECIDED）**：`openspec/changes/nbpolar-data-use-rules-revision/` 完成 T1 PI 裁决——(i) 采纳 R1–R5 为标准规则（安全记账已覆盖 K/tag/CRC/CAL 牺牲、decoder-touched 帧重用不产生新披露；统计口径要求分层报告选模参与情况；分段默认仅排除 CAL32；样本量随 `p` 重算；断言新采集前先查账本）；(ii) `D-FER-03` 重裁为 `n=56`（Wilson 上界 `p≈0.1771`，取代 `n=65`，原值保留注明被替代）；(iii) `D-ACQ-02/03` = SHG `_1`/`_2` 全会话 64 块（A1_CAL 8 + CHAR/HELDOUT 10 + EVAL 14，per session），`D-ACQ-05` 适用域限定两次 SHG 采集自身条件；(iv) R2 候选译码配置 = M2 + SCL(L=16,top_m=4,CRC-16) + K1=319/K2=6492 + P16，执行前须正式冻结；(v) `participation_ledger.json` 字段命名需澄清。新建唯一权威账本 `docs/nbpolar/DATA_LEDGER.md`；`AGENTS.md` 新增 "Data-use rules (R1-R5)" 小节。**不改变** M2/G2/G3 状态串、不改变冻结 K1=319/K2=6492、R2 合同仍未冻结（D-FER-04..07、D-ACQ-01/04/06/07/08 等行仍 PENDING）、T7/T8/T9 仍 NOT AUTHORIZED。详见 `docs/decision-log.md` 2026-09-28「数据使用规则修订 R1-R5 采纳（T1 DECIDED，PI 裁决）」条目。

> **R2 测量合同 T4 全部完成 + T3/T5/T6（2026-09-28，PI 裁决"按建议批准"）**：`openspec/changes/nbpolar-r2-fer-measurement-contract/` 剩余 8 行（D-ACQ-01/04/07/08、D-FER-04/05/06/07）全部按 `R2_REMAINING_DECISIONS_20260928.md` 推荐值裁定 `DECIDED`，另加两项 PI 补充裁决 **P-1**（允许给出 64 块汇总 FER，但须与三层分列表同表并存）与 **P-2**（`undetected≥1` 触发的 STOP 仍计入本次 one-shot 预算，不得为求干净结果而重跑）。§5 ledger 15 行全 `DECIDED`；T3 结构性冻结复核 PASS；T5 配额算术完成（16+20+28=64，余量 8，跨层汇总门槛按 P-1 读法达标）；T6 packet skeleton 写入 `openspec/changes/nbpolar-r2-fer-measurement-contract/T6_PACKET_SKELETON_20260928.md`（`authorizations: []`，未生成 `AUTHORIZATION_PROMPT.md`）。**整体状态 = `FROZEN except PENDING-BUDGET (SCL wall)`**：D-ACQ-06 的预算数字是按 SC 口径裁定（40 s/块），R2 候选路径 SCL(L=16) 实测约 600 s/块，两者不兼容，未自行裁定，标记待 PI 补充裁决。**不改变** M2/G2/G3 状态串、不改变冻结 K1=319/K2=6492；T7/T8/T9 仍 **NOT AUTHORIZED**（与预算是否补充裁决无关）。详见 `docs/decision-log.md` 2026-09-28「R2 剩余 8 项待决全部 DECIDED...」条目。

## 如果只读三件事

1. **leading-candidate 机制（非收敛根因）**：证据指向 M0 非参数先验的先验/地板处理（零 cell 得概率地板 1e-15；每个落地板的真 −1 delta 约 40.42 bits 伪罚；每 block ~44.7 个真 −1 中仅 ~30.4 落在 TRAIN 零 −1 列；S9 合成 B 11/16 vs A 0/16，描述性，见 §1）——但码率、构造、分配、时间相关均**未排除**；54.8σ 余量仅是理想模型下"无码率 binding 证据"，非证伪。
2. **候选方向（非已采纳基线）**：M2 ±1 先验是 **CANDIDATE 且真实数据检验已出 bounded negative**——SHG `_1` 上 δ-tail 门 FAIL（p̂=0.0050202，U=0.0052879 vs B_tail=2.0e-4，~25× 超预算；±1 前提在新数据上不成立 ⇒ 预定 STOP，不进 G2；`G1_ADJUDICATION.md`）。注意精确口径：**未证伪** M0 地板误定价机制（matched-CAL NLL 差 ~1.95 在两总体可复现），**未证伪** M2 于所有源（冻结 sessions 尾部≈0，但 ladder 已耗尽）；S9 仍不得读作 FER/效率证据。后续已推进：S11 判定该 FAIL 主因是**配对污染**（w=200 CIRCULAR 尾部 = 0；**标注，2026-09-28**：此处"污染"指 S11 的配对窗口截断这一技术/物理判定，与 `nbpolar-data-use-rules-revision` R1–R5 项下"decoder-touched frame 永不回流"规则的既述理由——(B) 统计选择偏差 / (C) 审计独立性，`design.md` D3——不是同一概念，不应混同）⇒ G1R2（w=200/CIRCULAR）δ-tail PASS、NLL PASS ⇒ **G2 SUCCESS `NBPOLAR_M2_PRIOR_G2_SUCCESS`（B 11/14 vs A2 0/14 严格不重叠）** ⇒ **G3 SUCCESS `NBPOLAR_M2_PRIOR_G3_SUCCESS`（主线 R2 接受；SHG `_2` 独立 session：B 8/14 Wilson [0.3259,0.7862] vs A2 0/14 [0.0,0.2153] 严格不重叠；A1 0/14 描述性无门；undetected 0 隔离；recount 0；tag_master 2026110101 G3 新鲜；一次性 g3_runs 1 reruns 0，wall 858.5 s ≤ 900；126 SC/42 tag）**。M2 在**两个解码门上均已确认**（"CANDIDATE until G3 passes" 条件记于 G2 裁决即 pre-G3 + freeze 门已过）⇒ 按预注册规则 **M2 状态进入 `VALIDATED_AT_FROZEN_CONTRACT`**（仅第二级；R2 FER 门、R3 效率门仍未做；G4 已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`）——M2 不变 `VALIDATED_AT_FROZEN_CONTRACT`，仅 `READY_FOR_QUALIFICATION` 合取项之一，下一门 = R2 测量合同冻结，禁止跳级）；残留记录偏差见 `G3_PROCESS_DEVIATION.md`（评审未落盘；G3-1 转录滞后；F5/F6 时间断言假）。**G4（穷尽公共消息清单）已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`）**；M2 不变 `VALIDATED_AT_FROZEN_CONTRACT`，仅 `READY_FOR_QUALIFICATION` 合取项之一，下一门 = R2 测量合同冻结。绑定边界：11/14 vs 8/14 是**方向复制、非量级可比**（两个独立 session 各自过自己的 CI 门）；无 FER/效率/资格/composable key 声明；A1 两 session 均 0/14 = 描述性首次测量。
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
| 已检验（bounded Tier-Y gate outcome，非 FER/效率证据） | **G3（w=200/CIRCULAR，SHG `_2` 独立 session 三臂 one-shot）SUCCESS `NBPOLAR_M2_PRIOR_G3_SUCCESS`（主线 R2 接受）**：B（M2，matched 32f）**8/14** exact Wilson [0.3259026690, 0.7861949007]（p̂=0.5714285714）vs A2（M0，matched 32f）**0/14** Wilson [0.0, 0.2153170119]，严格不重叠；A1（M0 incumbent 1024f）0/14 描述性、无门。`undetected` 0/42 隔离；taxonomy {exact 8, verify_failed 34}；recount mismatch 0（tag_master 2026110101 G3-fresh；EVAL_SEED 2026100101）；`g3_runs: 1` / `sc_calls_on_protected: 126` / `reruns: 0`；wall 858.5 s / RSS 1.13 GiB。M2 为两 decode 门确认的 **confirmed candidate**（G2 11/14 + G3 8/14），状态 `VALIDATED_AT_FROZEN_CONTRACT`（仅第二级）；11/14 vs 8/14 不得跨 session 比优劣（仅方向复现）；NLL 域标签按行常量强制（`G3_NLL_DOMAINS`）；残留记录偏差见 `G3_PROCESS_DEVIATION.md`；OpenSpec archive done (2026-09-22), G4 complete `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE` (`G4_ADJUDICATION.md`; M2 unchanged `VALIDATED_AT_FROZEN_CONTRACT`; only one `READY_FOR_QUALIFICATION` conjunct; next gate = R2 measurement-contract freeze) | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md` + `G3_PROCESS_DEVIATION.md` |
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
| Accounting | D3 sacrifice-only 下：incumbent 牺牲 ~8× block；M2 参数计数 reveal ~20 bits 仅为诊断量、**非记账成本**；~~`docs/SECURITY_MODEL.md` currently has NO CAL/prior term at all（grep verified）~~ **【2026-09-21 陈述已陈旧，2026-09-28 更正】**：`docs/SECURITY_MODEL.md:107-129`（"NB-Polar M2 CAL / prior accounting"节）已明确给出 CAL 牺牲-排除记账，本行上半句的 grep 结论未在该节加入后重验，见 `docs/nbpolar/DATA_LEDGER.md` R1 摘要与 `openspec/changes/nbpolar-data-use-rules-revision/design.md` D2 |
| Type0 tier insufficiency | **未溶解**：CAL 缺口或可缓解，但 block 完整性与数据质量约束仍在（Type0-500K ≤146 frames；减 32 CAL 后不足 1 block） |
| Data scarcity | 冻结 sessions 上**未解除**：never-decoded 余量 **101 frames（非 261）**；32-frame CAL 后仅剩 69 frames，不足 1 个 128-frame block；P20T 接受语即 "ladder ends by exhaustion"（**此处"冻结 sessions"specifically 指旧 P 系列 20260107/20260123 三源，非 SHG 2026-01-13 `_1`/`_2`；后者 RESERVE 29/99 帧未耗尽，逐段历史见 `docs/nbpolar/DATA_LEDGER.md` §1/§2/§6**） |
| K allocation | 当前 L1 f≈2.00 / L2 f≈1.275 misallocation 必须重推导（`MACRO_PLAN_20260921.md:§2` finding A）；D4 constant-total 不成立：fixed-f 与 fixed-K_total 不可兼得（M2 H_total 下 f=1.3 ⇒ K_total 7053/7106，即 +33/+26；冻 K_total 则 f=1.2939/1.2952），且 G2 冻 K1=319/K2=6492 |
| Construction | P16 order 系旧先验下推导；B-vs-C CI 重叠仅说明二者不可区分，**非安全/等价结论**，重推导必要性未确立（B-vs-C 差 2 blocks，CI 重叠） |
| 总标记 | **以上全系 pending real-data validation（F1 仅合成），在此之前旧约束条目一律不动** |

## §4 当前授权与预算状态

- 授权状态：**G2 已裁决 `NBPOLAR_M2_PRIOR_G2_SUCCESS`（B 11/14 vs A2 0/14 严格不重叠；A1 0/14 描述性）；G3 已裁决 `NBPOLAR_M2_PRIOR_G3_SUCCESS`（主线 R2 接受；SHG `_2` 独立 session 三臂 one-shot；B 8/14 vs A2 0/14 严格不重叠；A1 0/14 描述性；M2 为两门确认的 confirmed candidate，状态 `VALIDATED_AT_FROZEN_CONTRACT` 仅第二级）**——见 `G3_ADJUDICATION.md` + `G3_PROCESS_DEVIATION.md`（残留记录偏差：评审未落盘；G3-1 转录滞后）。D4 已完成 `NBPOLAR_M2_PRIOR_K_RESPLIT_D4_COMPLETE_REPORT_ONLY`（两分支皆不采纳；G2/G3 仍冻 319/6492）。**G1** bounded negative；**G1R2** 描述性完成（δ-tail PASS 系 S11 推论）。**下一门 = R2 测量合同冻结**（G4 已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`）；M2 不变 `VALIDATED_AT_FROZEN_CONTRACT`；仅 `READY_FOR_QUALIFICATION` 合取项之一；R2/R3/Stage-3 仍 outstanding）；SHG `_2` EVAL 已消耗、RESERVE 99 untouched，SHG `_1` RESERVE 29 untouched。
- 探索线（2026-09-23）：`nbpolar-native-highdim-exploration` 套件执行完成并归档（`openspec/changes/archive/2026-09-23-nbpolar-native-highdim-exploration/`）：Steps 0–3 + Step-1B 共六个探针，各自 freeze + 聚焦数值评审 + 主线程裁决。PI 结论（有前提的肯定）：在冻结合成 F4 信道（±1 主导非对称）、q∈{4,8,16}、n_sym=128、所测码率下，原生 q 元 Polar SC 平均 FER 低于本次实现的比特平面二元 Polar 方案；二元臂升级为软信息携带 MSD 后差距仍在 10/12 测试点（2 平）；生产 min-sum 二元基线 12/12 落后。候选性能优势，L2 合成台账；无真实数据 FER/效率/净密钥断言；O1–O4 后续门未授权。不影响 M2 主线状态（G4 已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`）；M2 不变 `VALIDATED_AT_FROZEN_CONTRACT`；下一门 = R2 测量合同冻结）。
- 冻结 sessions 真实数据 ladder **已耗尽**：never-decoded 余量 101 frames，32-frame CAL 后剩 69 frames（<1 block）；验证须在 SHG 新采集上跑，并声明保留段做独立确认。（**"须新采集"括注，2026-09-28**：这里的"冻结 sessions"指旧 P 系列 20260107/20260123，其 101 帧 never-decoded 余量是真正的物理耗尽；SHG `_1`/`_2` 的 RESERVE 29/99 帧本身也不足 1 block，但按 `nbpolar-data-use-rules-revision` T1 裁决 R3/R5，两会话另有 64 块可用作 R2 确认样本源（A1_CAL/CHAR+HELDOUT/EVAL 分层复用），并非需要新采集——先查 `docs/nbpolar/DATA_LEDGER.md` 算缺口，不得混同两批次。）
- 冻结中：一切真实数据执行（无授权不读不跑）；`results/`、`comparison_bench/outputs_comparison/` 只加不覆；benchmark/result roots 写入；SCL（5-item conjunction 未满足，锁定）（2026-09-27 修订：合成门见 `nbpolar-scl-lock-amendment`；真实数据仍锁定）；任何 promotion/qualification/FER claim；C-P2 B4；表示转向。
- 预算：route-B 2/6 used / 4 remaining（`MACRO_PLAN_20260921.md:§6`；1/6 after C-P1 RETIRE at `decision-log.md:5065`；2/6 after C-P2 freeze review at `:5079`）；Tier-X probes non-claim，ledger 按里程碑批量更新（`docs/nbpolar/PROBE_TIER.md`）；re-analysis queue 4/6（剩 Q5 + exhaustion-route decision）。
- Pending PI decisions（2026-09-22 更新：G2+G3 freeze+execute+adjudication 已完成，**route decision post-G1R2** 中 G2/G3 子项已关闭；现 pending = R2 测量合同冻结决策 + 下列）：**route decision post-G1R2**（G2/G3 一次性三臂译码已完成——A1=M0@1024f incumbent / A2=M0@32f 对照 / B=M2@32f，SHG `_1`/`_2` 各 14 blocks，冻结 K1=319/K2=6492 与 P16 构造；G4 已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`），下一门 = R2 测量合同冻结）；K_total 选择（fixed-f vs fixed-K，D4 仍 DEFERRED，G1R2 的 H_M2 暗示 ≈6,946 vs 冻结 7,020，仅规划输入）；σ/`gate_ps=200` 不兼容；accidental-dominated H 可用性；queue 上限处的 exhaustion-route；Type0 source verification。（已决：G1 用 (N) W_P=500/W_S=200；**G1R2 改用 W_P=200 + MOD=CIRCULAR**——后者经 delta 评审，且其"无需改 runner"的原始断言被独立评审否证后已修正。）
- Branch `codex/nbpolar-phase0`；本文件建立时的 last commit `5f9ec273`（provenance，**非**当前 HEAD——当前 HEAD 见 `git log -1`）。

## §4.1 M2 promotion ladder（状态阶梯**定义**；本节不授予任何晋级）

> 2026-09-22 主线裁定，源自 `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` §5，并补入 G3 三态、失败分层口径与 G4。
> ~~**M2 状态（2026-09-22 G3 裁决后）= `VALIDATED_AT_FROZEN_CONTRACT`**~~ ~~**（2026-09-29 晋级：R2 门过，M2 = `FER_MEASURED_AT_CONTRACT`，第 3 级，见下方阶梯图与 `docs/decision-log.md` 2026-09-29 条目）**~~ **（2026-09-30 PI 批准晋级：R3 门过，M2 = `EFFICIENCY_ACCOUNTED`，第 4 级，见下方阶梯图与 `docs/decision-log.md` 2026-09-30 PI 裁定条目）**（第一道真实数据 decode 门 G2 + 独立 session 门 G3 双过，按本表第一行进入；2026-09-29 时仅第二级（R2 FER 门、R3 效率门当时仍未做；2026-09-30 两门均过，M2 已处第 4 级），G4 inventory 已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`；仅 `READY_FOR_QUALIFICATION` 合取项之一），禁止跳级）。晋级依据：pre-G3 的 "CANDIDATE until G3 passes" 规则（记于 G2 裁决）+ `g3_freeze_config.json` 17:00:07 的预注册门。**注意**：本 §4.1 阶梯文档本身写于 decode 后 ≈17:58（主线程 `ses_f3ffe4fc…`），不得引为 pre-decode preregistration；`0851b481` 的替换编辑已被 `3f5b374a` 恢复、本次提交 reaffirm。见 `G3_PROCESS_DEVIATION.md` F10。本表只定义状态的进入条件，不构成授权。

```text
CANDIDATE
  → (G3 预注册门 PASS)                                    VALIDATED_AT_FROZEN_CONTRACT
  → (R2 门过：预注册 FER 口径 + 样本量达标)                 FER_MEASURED_AT_CONTRACT   ← R2 门过（2026-09-29，r2-fer-shg-64）
  → (R3 门过：verification-aware f_eff + 运行时/RSS 上界)   EFFICIENCY_ACCOUNTED       ← R3 门过（2026-09-30，PI 批准晋级）：M2 现处于本级
  → (≥2 独立 session 复现 + 样本量 + G4 exhaustive
     public-message inventory + 独立 Pre-RESULT 全过)       READY_FOR_QUALIFICATION
任一 FAIL 或 INCONCLUSIVE：回 CANDIDATE 或 BOUNDED_NEGATIVE。禁止跳级；
禁止用合成 S9 推级；禁止用跨契约（G1 w=500 vs G1R2/G2 w=200）优劣叙事推级。
```

> **2026-09-30 注**：`READY_FOR_QUALIFICATION` 仍不满足——样本量 64 块远不足路线图目标约 1000 块（FER<0.003）；G2/G3 是否算 ≥2 独立会话暂不裁定（同日同装置，独立性偏弱）；建议未来为冲这一级做一次不同日期采集。另：**晋级 `EFFICIENCY_ACCOUNTED` 不代表 f≤1.3**（f_book≈1.27 / f_eff≈1.31–1.32 / 95% CI 上界≈1.42–1.43，三档并列）。

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
- C5：never-decoded 余量 "261 frames" ⇒ 101 frames；32-frame CAL 后剩 69 frames（<1 block），冻结 ladder 耗尽（旧 P 系列 20260107/20260123；见 `docs/nbpolar/DATA_LEDGER.md` §6）。

## §6 延伸阅读（按序）

1. `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md`（R0–R4 执行序：G3 收口 → 可重复 → FER → 效率 → 论文；planning proposal）
2. `docs/nbpolar/MACRO_PLAN_20260921.md` §§0–9（候选结论 S8/S9/S10 F1–F6，2026-09-21 review 已修正）
3. `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md`（当前 route 与 stop rules）
4. `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`（先验契约冻结）
5. `docs/nbpolar/CRITICAL_PATH.md`，`ROADMAP.md`（串行顺序与 phase gates）
6. `docs/nbpolar/PAPER_READ_20260921.md`，`LITERATURE_FIT_CHECK_20260921.md`（文献口径）
7. `docs/decision-log.md` 2026-09-21 条目；`AGENT_PROJECT_MEMORY.md` 最新条目
8. `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/`（**已接受** `NBPOLAR_M2_PRIOR_STAGE1_IMPLEMENTATION_COMPLETE_ACCEPTED`：`prior_m2.py` + T1–T12 测试 + Spec-5 runner + `SECURITY_MODEL.md` CAL note；独立评审 PASS_WITH_COMMENTS 零阻塞；decoder-free、合成 fixture、零数据接触）与 `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/`（**G1 已执行并裁决** `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`：δ-tail FAIL / NLL PASS（近无信息量）；记录 `G1_ADJUDICATION.md`、`FREEZE_REVIEW.md`、`g1_freeze_config.json`；父包 `STATUS.yaml` `g1_outcome`）；并续 `NBPOLAR-S11-SHG-TAIL-NATURE/`（S11：尾部主因是配对污染，far-offset 基线非均匀）、`NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/`（G1R2 描述性 PASS，δ-tail PASS 系 S11 推论）、`NBPOLAR-M2-PRIOR-G2-DECODE/`（**G2 SUCCESS** `NBPOLAR_M2_PRIOR_G2_SUCCESS`）、`NBPOLAR-M2-PRIOR-K-RESPLIT-D4/`（D4 report-only，两分支皆不采纳）、`NBPOLAR-M2-PRIOR-G3-CONFIRM/`（**G3 SUCCESS** `NBPOLAR_M2_PRIOR_G3_SUCCESS`，主线 R2 接受；SHG `_2` 独立 session 确认；`G3_ADJUDICATION.md` + `G3_PROCESS_DEVIATION.md`；三 chat 评审真实通过但未落盘，在盘 Pre-RESULT 8/8；残留偏差见 deviation F5/F6/F15–F17；M2 `VALIDATED_AT_FROZEN_CONTRACT` 仅第二级）。下一步门：**R2 测量合同冻结**（G4 已裁决 `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`（`G4_ADJUDICATION.md`）；M2 不变 `VALIDATED_AT_FROZEN_CONTRACT`；仅 `READY_FOR_QUALIFICATION` 合取项之一；R2/R3/Stage-3 仍 outstanding）。
