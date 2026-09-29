# NB-Polar 收尾任务包（CLOSURE_PACKET_20260930）

> 接手方：一个独立 Claude session（执行 + 起草 + 组织审查）。发出方：主 session（2026-09-30）。
> 本包是**封闭**任务：三个工作项 W1–W3 + 收口 W4，全部是**案头工作**（整理已有结果、记账、写报告、仓库清理），**不解码、不读原始数据**。
> 凡本包没写到的情况 → 停下问 PI，不要自行发挥。回复 PI 一律用中文。

---

## 0. 给接手 session 的开场指令（PI 直接粘贴这段即可）

> 请严格按 `docs/nbpolar/CLOSURE_PACKET_20260930.md` 执行，从 §1 读起，按 W1→W2→W3→W4 顺序做完，最后按 §8 的格式回报我。中途只有 §7 列出的情况才停下问我。

---

## 1. 背景（只需知道这些）

NB-Polar 项目的目标：为真实 HD-QKD 数据找到并验证高性能信息协调（IR）算法。截至 2026-09-30，**核心结论已在真实数据上测完**：

| 测量 | 方案 | f_book（含 CRC，G2/G3） | 块失败（64 块） | 结果目录 |
|---|---|---|---|---|
| R2（**主工作点**） | NB-Polar：M2 先验 + SCL(L=16, top_m=4, CRC-16)，K1=319/K2=6492 | 1.2753 / 1.2681 | **2/64**（gbi23 G2、gbi38 G3），Wilson [0.0086, 0.1070] | `workspace/r2_fer_shg_64/` |
| R2E（备选点） | 同上但原生 SCL L=32，K=6657（k1=253,k2=6404） | 1.2466 / 1.2395 | 3/64，Wilson [0.016, 0.129] | `workspace/r2e_fer_shg_64_L32_f124/` |
| R2B（不可用点） | 原生 SCL L=32，K=6442 | 1.2064 / 1.1996 | 14/64，Wilson [0.135, 0.334] | `workspace/r2b_fer_shg_64_L32_f120/` |
| R2D（G2 定位，描述性） | 6 配置 f∈{1.22,1.24,1.26} | — | 见 RESULT_REVIEW | `workspace/r2d_locate_f_k_g2/` |
| 冻结二元基线 | 独立比特面 SC，N=4096 | 4.1–4.8 | 失败率 0.61–0.94 | `workspace/r2_binary_baseline_shg_64/` |
| R2C 最强二元 | 硬前缀 MSD + SCL L=16，无 CRC，genie-MC 构造，逐层 μ_i | 1.20 / ≈1.27 / ≈1.31 / ≈1.41 | 64/64、18/64、0/64、0/64 | `workspace/r2c_strong_binary_msd_shg_64/` |

PI 已决定（2026-09-30）：**保持 f≈1.27（R2，L=16）为主工作点**。M2 当前状态 = `FER_MEASURED_AT_CONTRACT`（第 3 级）。下一级是 `EFFICIENCY_ACCOUNTED`（R3 效率门：verification-aware f_eff + 运行时/RSS 上界）。

必读（只读这些）：`AGENTS.md` §3、§5、§10.3；`docs/nbpolar/STATE.md` §0 前 40 行与 §4.1 阶梯图；`docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` §1 与 "R3 效率与可用性" 小节；上表各目录的 `RESULT_SUMMARY.md`。

---

## 2. 硬性规则（违反任何一条 = 停下）

1. **不解码、不读 `.ttbin`、不跑任何 `run.py`**。本包只用已提交的 `results.json` / `part_*.json` / `RESULT_SUMMARY.md` 等文件。
2. **不改任何已有结果目录内的文件**（`workspace/r2*/`、`workspace/probes/`），只新增本包规定的文件。
3. **不改**冻结基线 `src/`、`experiments/`、`tools/` 的内容；不写 `results/`、`comparison_bench/outputs_comparison/`；`D:\Code\qkd-reconciliation-lab` 只读（本包不需要碰它）。
4. **不改 M2 状态串**（STATE.md 里的 `FER_MEASURED_AT_CONTRACT` 等）。是否晋级 `EFFICIENCY_ACCOUNTED` 只由 PI 在你回报后决定。
5. **不 push**，不安装任何包，不删除任何文件（包括 `.git/index.lock`）。
6. **禁止在 Git Bash 里用 `python3 -` / `python -` / `py -` 加 heredoc 或管道喂 Python**：在这台 Windows 机器上它会卡死并空转一个 CPU 核数小时。需要算数时：把脚本写成文件（放 scratchpad 或本包指定目录），然后用
   ```
   MSYS_NO_PATHCONV=1 wsl.exe -e /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/<脚本相对路径>
   ```
   运行（路径必须是 `/mnt/d/...` 或 `/mnt/c/...` 形式）。给子代理的 prompt 里也必须写上这一条。
7. 子代理一律 `model: "sonnet"`；审查子代理必须**只读**（不改文件、不做 git 写操作）。
8. 数字只能从文件里取或按本包公式算，**不得凭记忆或"合理估计"填数**。本包 §3 给出的"预期值"只用于核对，你必须从文件重算并以文件为准；若与预期值差 > 1e-4，停下报告。
9. 所有新文档用中文写；文件编码 UTF-8、行尾 LF。

---

## 3. W1 — R3 效率记账（verification-aware f_eff + 运行时/RSS 上界）

**产出**：`docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md`（主文档）+ `workspace/closure_20260930/r3_accounting.py`（计算脚本）+ `workspace/closure_20260930/r3_accounting.json`（脚本输出）。

### 3.1 固定参数（主线程冻结，不得改）

- 工作点：R2（`workspace/r2_fer_shg_64/`），N = 32768 符号/块，q = 1024（每符号 10 bit），两层 GF(32)，K1 = 319，K2 = 6492，CRC 16 bit，Toeplitz tag 64 bit。
- H_total（每会话自己的 CAL32 拟合，取自 R2 `results.json`）：G2 = 0.8168138204133305，G3 = 0.8214782076249098。
- 每块公开披露比特：`D_blk = 5·(K1+K2) + 16 + 64`（5 = log2(32)，每个 GF(32) 冻结坐标 5 bit）。
- 失败块：块的全部披露照付，且该块不产出密钥（按整块损失计）。

### 3.2 要计算的量（每会话 G2、G3 各一份，外加 pooled）

| 符号 | 公式 | 预期值（仅供核对） |
|---|---|---|
| D_blk | 5·(319+6492)+16+64 | 34135 |
| D_blk_noCRC | 5·(319+6492)+64 | 34119 |
| f_book | D_blk / (H_total·N) | G2 1.275343，G3 1.268101 |
| f_book_noCRC | D_blk_noCRC / (H_total·N) | G2 ≈1.27475，G3 ≈1.26751 |
| p̂（块失败率） | 非 exact 块数 / D（从 R2 `part_*.json` 逐块数：`scl.exact==false` 或 status≠ok 计失败；undetected 单列） | G2 1/32，G3 1/32，pooled 2/64 |
| Wilson 95% | z=1.96 标准 Wilson 区间 | pooled [0.008612, 0.106975]；每会话 1/32 ≈ [0.0055, 0.157] |
| **f_eff**（点） | f_book / (1 − p̂) | G2 ≈1.3165，G3 ≈1.3090 |
| **f_eff_upper** | f_book / (1 − Wilson 上界)（pooled 上界与每会话上界各算一次） | pooled 上界下 G2 ≈1.428，G3 ≈1.420 |
| λ_cal（CAL 牺牲比例） | 32 / (32 + 4096)，4096 = 每会话进入 64 块池的帧数（32 块 × 128 帧） | 0.00775 |
| ε_tag | 2^-64（每块 tag 碰撞概率上界） | 5.4e-20 |

**λ 分解表**（roadmap R3 第 1 条）：主文档必须逐项列出下表每一行，写明"计入 f / 计入产出比例 / 可忽略"与理由：

| 项 | 处理 | 说明 |
|---|---|---|
| leak_IR = 5·(K1+K2) | 计入 f | 冻结坐标披露 |
| CRC 16 bit | 计入 f（f_book）；另报 noCRC 值 | 选路用，非安全项 |
| tag 64 bit | 计入 f | 验证用 |
| P_collision (ε_tag) | 安全参数，不计入 f | ≤2^-64/块 |
| FER（整块损失） | 计入 f_eff | 失败块披露已付、无产出 |
| CAL_sacrifice | 计入产出比例 λ_cal，不计入 f | CAL32 公开牺牲 |
| prior_reveal（M2 参数） | 可忽略（0） | M2 由已公开的 CAL32 拟合，不额外泄漏 |
| undetected | 单列，本次 0/64 | 不并入成功或 FER |

### 3.3 运行时 / RSS 上界

从下列文件取数（不要重跑），写成一张表：

| 来源 | 实现 | 数据 | 取什么 |
|---|---|---|---|
| `workspace/r2_fer_shg_64/results.json`（每块 `wall_scl_s`、`wall_sc_s`、`rss_gib_peak_advisory`） | scl_joint（Python/numba 参考实现），L=16 | 真实 | SCL 每块均值/最大、RSS 最大 |
| `workspace/r2e_fer_shg_64_L32_f124/part_*.json` 与 `workspace/r2b_fer_shg_64_L32_f120/part_*.json`（每块 SCL 耗时与 RSS 字段） | 原生 Rust SCL，**L=32** | 真实 | SCL 每块均值/最大、RSS 最大 |
| `workspace/probes/eff-sweep-native/results.json` 以及 `git show --stat 8fcc9119` 的提交说明 | 原生 Rust SCL，L=16 与 L=32 | 合成 | 每块耗时 |

必须写出的结论（按实际数字填）：
- **主工作点（原生 L=16）的运行时上界**：用真实数据上**原生 L=32** 的每块 SCL 最大耗时作为上界。论证：同一原生代码，L=16 的列表宽度是 L=32 的一半，每块工作量严格更少；且原生实现与 scl_joint 按"等价标准 B"判定等价（证据 commit 8fcc9119、36025662）。必须标注"**由论证得到的上界，非 L=16 真实数据实测**"。
- 吞吐 = 32768 / 每块耗时（符号/s），给出：上界对应的保守吞吐、合成 L=16 典型吞吐、scl_joint 参考实现吞吐（约 60 符号/s，即 STATE 里的旧数）。
- SC 路径（约 21 s/块）只是保真检查，运行时不需要，**不计入**工作点运行时，但要在表里单列说明。
- 硬件：WSL 8 核，原生默认线程数；RSS 取最大值。

### 3.4 描述性对照（同一记账口径，仅描述）

用同样公式给 R2E、R2C（F2、F3）算 f_book 与 f_eff（点 + Wilson 上界），与 R2 并表。注明：二元（R2C）不付 CRC；R2C F3 的 0/64 的 Wilson 上界是 0.0566，f_eff_upper 必须用它算；NB 与二元 FER 点不同，不得据此宣称胜负。

### 3.5 R3 门判定（主线程提出的判定标准；最终晋级由 PI 决定）

`EFFICIENCY_ACCOUNTED` 的判定是**完整性**判定，不是性能阈值：
- (a) §3.2 表中每个量都有公式、数值、文件来源（文件路径 + 字段名）；
- (b) λ 分解表逐项有处理方式与理由；
- (c) §3.3 运行时/RSS 表完整，且上界的论证写明；
- (d) 独立审查（§3.6）PASS 或 PASS_WITH_COMMENTS。

四项全满足 → 主文档末尾写"**R3 记账完成，建议 PI 批准 M2 晋级 EFFICIENCY_ACCOUNTED**"；任一不满足 → 写"R3 记账未完成，缺：…"。
另写一句**描述性**对照 roadmap 的 `f≤1.3` 期望：f_book 满足（≈1.27），f_eff 点值不满足（≈1.31–1.32），f_eff 上界更高——如实写，不作为门槛。

### 3.6 W1 独立审查

起一个只读 Sonnet 子代理（prompt 里写上 §2 第 6 条），要求它：从 R2 / R2E / R2B / R2C 的 part 文件**独立重算** §3.2–§3.4 的每个数，核对主文档与 `r3_accounting.json`；核对 λ 表处理方式是否与 §3.2 一致；核对运行时上界论证；给出 PASS / PASS_WITH_COMMENTS / FAIL。
- FAIL 且问题在措辞或算术 → 修文档/脚本后重审（最多 2 轮）；
- FAIL 指向数据本身或规则冲突 → 停，报 PI。
把审查结论写入 `workspace/closure_20260930/R3_REVIEW.md`。

---

## 4. W2 — 总报告

**产出**：`docs/nbpolar/NBPOLAR_FINAL_REPORT_20260930.md`。

结构（章节名照抄，内容按实际文件填，所有数字注明来源目录）：

1. **一句话结论**（≤3 句）：NB-Polar（M2+SCL L=16）在两次 SHG 真实采集的 64 块上 f_book≈1.27、块失败 2/64、undetected 0；同池最强二元方案需 f≈1.28–1.31 才达到同等失败水平；冻结二元基线需 f≈4.1–4.8。
2. **数据与协议**：SHG `_1`/`_2`（2026-01-13 两次采集）、64 块池定义（`docs/nbpolar/DATA_LEDGER.md` §7）、CAL32、数据使用规则 R1–R5（`AGENTS.md` §5.8）、块长 N=32768、配对参数 W_P=200/W_S=500/CIRCULAR/skip=702、P16 构造。
3. **方法**：M2 ±1 参数化先验；两层 GF(32) NB-Polar；SCL 联合两层解码 + CRC-16（top_m=4）；Toeplitz 64 bit tag；原生 Rust 实现与等价标准 B。
4. **主结果**：§1 表格的 R2 行 + 分层表（从 `workspace/r2_fer_shg_64/RESULT_SUMMARY.md` 抄）。
5. **效率边界**：f–失败率表（R2B f≈1.20 → 14/64；R2E f≈1.24 → 3/64；R2 f≈1.27 → 2/64），以及 R2D 的 G2 定位表；失败几乎全在第二层（L2）；gbi23 为跨四轮失败的难块。
6. **与二元方案对比**：冻结二元基线、R2C 最强二元四个 f 点、与 NB 的逐块配对四格表（从 R2C RESULT_SUMMARY §4 抄）；R2C 构造阶段要点（genie-MC 替代采样 DE 的原因，引 `workspace/probes/r2c-layer-diag/`）。
7. **效率记账与运行时**：引用 W1 主文档的结论与表。
8. **工作点决定**：PI 2026-09-30 保持 f≈1.27/L=16，理由（两点 FER 不可区分；净密钥产出对 FER 更敏感；L=32 开销约翻倍）。
9. **局限（必须全部列出）**：适用域仅两次同日 SHG 采集；64 块 CI 宽（上界 0.107）；R2C 未做 CRC/软前缀/更大 L，不代表二元上限；R2C 设计帧不含真实尾部、μ_i 选择偏差；吞吐远未实时；gbi23 未归因；G2 块参与过 R2D 选点（R2E 已分层报告）；净密钥产出未计算（需 Eve 信息量估计）。
10. **可复现性**：每个测量的目录、提交号（用 `git log --oneline -- <目录>` 查）、解释器、种子。
11. **未做 / 后续候选**：二元 CRC 路径选择（C 阶段）；L2 构造/先验改进；净密钥产出比较；更多独立会话；实时化。

规则：只陈述已裁定结果；不新增任何未经审查的结论；"领先"只能写区间（NB 领先约 0.01–0.04 的 f），不得写成点值或"显著"。

**W2 独立审查**：起只读 Sonnet 子代理，逐条核对报告中每个数字与来源文件一致、局限是否全部列出、有无超范围表述；结论写入 `workspace/closure_20260930/REPORT_REVIEW.md`。FAIL 处理同 §3.6。

---

## 5. W3 — 仓库清理

逐项做，每项做完在 `workspace/closure_20260930/HYGIENE_LOG.md` 记一行（做了什么 / 结果）。

1. **原生编译产物加入 .gitignore**。先读 `.gitignore`，在末尾追加（已存在的行不要重复）：
   ```
   # native build outputs (rebuilt by build_rust.sh / build_cpp.sh)
   comparison_bench/src/comparison_bench/formal_ir/nbpolar/_native/*.so
   comparison_bench/src/comparison_bench/formal_ir/nbpolar/_native/*.dll
   comparison_bench/src/comparison_bench/formal_ir/nbpolar/_native/rust_kernels/target/
   src/reconciliation/cpp_polar/ca_scl.so
   ```
   然后 `git status --short` 确认这些文件不再显示为 `??`。**不要删除这些文件本身。**
2. **遗留改动 `workspace/r2_binary_baseline_shg_64/_test_aggregation.py`**：`git diff` 查看。
   - 若只**新增**测试用例（无删除行），用 `/home/karel_303/.venvs/timetagger/bin/python -m pytest -p no:cacheprovider <该文件>`（经 `wsl.exe -e`）运行；通过 → 提交（消息：`test(nbpolar): binary baseline aggregation test additions (recovered stray edit)`）；
   - 其他任何情况（有删除、测试失败、无法运行）→ 不提交、不还原，在 HYGIENE_LOG 与回报里说明。
3. **STATE.md 旧吞吐数字**：STATE.md 第 23 行附近的"吞吐约 60 符号/s"是 scl_joint 参考实现的数字。**不要改原文**，在该段落末尾追加一行：`> （2026-09-30 注：约 60 符号/s 为 scl_joint 参考实现；原生实现见 docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md。）`
4. **已知与本包无关的先存改动**：`comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`、`workspace/pytest-evidence-test/**`——**不碰、不提交**。
5. 不归档任何 OpenSpec change，不改 `openspec/`。

---

## 6. W4 — 收口

1. **STATE.md §0**：在最靠上的 "R2C … 主线程裁定" 段落之后追加一段 `> **收尾（2026-09-30）**：`，3–5 行：R3 记账结论（W1 末尾那句）、总报告路径、仓库清理摘要、待 PI 决定的事项（见 §8）。**不改状态串。**
2. **docs/decision-log.md**：先读文件，在 `## Decisions` 标题下**最前面**插入 `## 2026-09-30 NB-Polar 收尾：R3 效率记账 + 总报告 + 仓库清理`，4–6 行要点（数字要与 W1/W2 文档一致）。
3. **AGENT_PROJECT_MEMORY.md**：在文件最前面插入一个 `## 2026-09-30 NB-Polar closure` 小节，3–5 条，每条注明来源文件（格式参照文件里已有的 2026-09-29 R2E 小节）。
4. **提交**（`workspace/` 被 gitignore，新文件须 `-f`）：
   ```
   git add docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md docs/nbpolar/NBPOLAR_FINAL_REPORT_20260930.md docs/nbpolar/STATE.md docs/decision-log.md AGENT_PROJECT_MEMORY.md .gitignore
   git add -f workspace/closure_20260930/
   git commit -m "nbpolar: closure — R3 efficiency accounting, final report, repo hygiene"
   ```
   提交消息末尾按当前会话给出的署名规则添加署名行。若报 `.git/index.lock` 存在：等 30 秒重试，最多 3 次；仍存在 → 问 PI，不删除锁文件。
5. 不 push。

---

## 7. 必须停下来问 PI 的情形

- 任何数字与 §3.2 预期值差 > 1e-4，或文件里找不到所需字段。
- 需要解码、读原始数据、安装包、改已有结果目录才能继续。
- 审查 FAIL 指向数据或规则冲突，或同一审查 FAIL 两轮。
- R2 的 part 文件显示 undetected ≥ 1 或失败块不是 gbi23/gbi38（与已裁定结果冲突）。
- 本包没写到的任何情况。

---

## 8. 回报格式（中文，简短）

1. **R3 记账**：一张表（G2/G3/pooled 的 f_book、f_eff 点值、f_eff 上界、λ_cal），运行时上界与吞吐各一句，审查结论一句，末尾结论句（"建议批准晋级" 或 "未完成，缺…"）。
2. **总报告**：路径 + 一句话结论 + 审查结论。
3. **清理**：HYGIENE_LOG 摘要（每项一行）。
4. **提交号**。
5. **请 PI 决定**（只提问，不自行决定）：
   - (a) 是否批准 M2 晋级 `EFFICIENCY_ACCOUNTED`？
   - (b) 是否 push 到远端？
   - (c) G2/G3（同日两次采集）是否算作 `READY_FOR_QUALIFICATION` 要求的"≥2 独立 session"？
   - (d) 后续研究方向是否启动（二元 CRC 对照 / L2 改进 / 净密钥产出比较）？
