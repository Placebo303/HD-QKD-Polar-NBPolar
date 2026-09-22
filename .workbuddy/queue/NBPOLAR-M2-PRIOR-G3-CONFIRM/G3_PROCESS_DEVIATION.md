# G3 过程偏差记录 / G3 Process Deviation Record（2026-09-22）

性质 = 过程偏差记录 / process deviation record。**纯追加，不修改任何既有记录；本文件不授权任何事。**本文件记录主线 R2 裁定（见 §R2）。
状态快照（主线 R2 2026-09-22 裁定后）：**G3 = 已接受 `NBPOLAR_M2_PRIOR_G3_SUCCESS`；M2 = `VALIDATED_AT_FROZEN_CONTRACT`**（仅第二级）。
依据 = app-server transcript 证据（三个真实 reviewer-go session，见 §2T）+ 在盘独立 Pre-RESULT（`PRE_RESULT_REVIEW.md`，`ses_f376e04ceffenAuTYaqlppawX6`，PASS_WITH_COMMENTS 8/8）+ 本线程主线 R2 复核。原只读审计（`ses_f376e04ceffenAuTYaqlppawX6` 两次调用）的 mtime 事实成立，但其 `PRE_EXECUTE_MISSING` 结论被 transcript 证据推翻（见 §2）。
审计对象 = G3 Tier-Y one-shot decode（SHG `_2`，`NBPOLAR-M2-PRIOR-G3-CONFIRM`）。

## §1 Ground-truth timeline（时间 | 事件 | 证据来源）

| 时间 | 事件 | 证据来源 |
|---|---|---|
| 16:59:19 | input bootstrap `input/g3_freeze_config.json` 写入 | mtime `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/input/g3_freeze_config.json` |
| 17:00:07 | packet 副本 `g3_freeze_config.json` 生成：closure-only、decoder-free；census repro σ = `114.43029692866367` ps bit-exact | mtime packet `g3_freeze_config.json`；审计记录 |
| 17:09:43 | `AUTHORIZATION_PROMPT.md` 被修改（operator 填入授权行 + 3 行 `# Audit note:`） | mtime packet `AUTHORIZATION_PROMPT.md` |
| 17:17:02 | `scripts/m2_prior_validation.py` 最后修改 | mtime（freeze 17:00 之后） |
| 17:20:04 | `comparison_bench/tests/test_nbpolar_m2_g3_confirm.py` 最后修改 | mtime（freeze 17:00 之后） |
| ≈17:35:55–17:50:13 | **THE DECODE RAN 并完成**：输出簇 mtime 17:50:13.789–.798；wall 858.499 s ⇒ 起始 ≈17:35:55 | mtime `per_block_outcomes.jsonl` / `g3_summary.json` / `run_log.md` / `cal_ids.json`；`run_log.md` wall |
| ≈17:58–17:59 | 主线程写 `STATE.md` §4.1（推断 FACT：紧邻其后 17:59:41 PREWRITE 创建） | INFERENCE（mtime 邻接，无直接见证） |
| 17:59:41 | `G3_ADJUDICATION_PREWRITE.md` 创建 | mtime packet 文件 |
| 18:01:30 | `G3_ADJUDICATION.md` 创建（operator） | mtime packet 文件（审计记录） |
| 18:02:14 | `STATUS.yaml` `G3-1_freeze_preauth` 由 `pending` 翻为 `pass` | git：`d3670066~1` 该行为 `pending`，`d3670066` 该行为 `pass` |
| 18:03:22 | `.workbuddy/memory/2026-09-22.md` G3 section | mtime（审计记录） |
| 18:04:42 | `STATE.md` operator 编辑 | mtime（审计记录） |
| 18:08:06 | COMMIT `d3670066`（10 files, +4484/−22） | `git log` |
| 18:10:31–18:11:20 | post-commit 编辑（`G3_ADJUDICATION.md` §3.3、`STATE.md`、`docs/decision-log.md`） | mtime：18:10:31 / 18:10:32 / 18:11:20 |
| 18:11:32 | `CURRENT_TASK.md`（仓库根） | mtime |
| 18:12:41 | COMMIT `0851b481`（6 files, +157/−11） | `git log` |
| 18:13:31 | memory 文件更新 | mtime `.workbuddy/memory/2026-09-22.md` |

决定性顺序事实 FACT：**译码完成 17:50:13 早于 STATE §4.1（≈17:58）与 PREWRITE（17:59:41）。**

## §2 审计结论 / Verdict of the audit（已更新）

原审计裁定：**`PRE_EXECUTE_MISSING`**【SUPERSEDED by transcript evidence —— 该结论指"评审未发生"，现证伪；保留原文作历史】—— G3 Tier-Y one-shot decode 在没有其 Pre-EXECUTE 门的情况下执行；decode 后记录所断言的评审没有证据。

现裁定：**`REVIEWS_PERFORMED_NOT_RECORDED_ON_DISK`** —— 三个独立评审真实发生且通过（§2T），但在断言时刻盘上无任何记录；偏差是记录缺失，不是评审缺失。

硬事实（记录层面，仍成立）：
- 断言时刻 packet 目录共 7 个文件，**无任何 G3 的 `PRE_EXECUTE*` 文件，也无 `PRE_RESULT*` 文件**（`ls | grep PRE_` = 空）。事后在盘独立 Pre-RESULT（`PRE_RESULT_REVIEW.md`，`ses_f376e04ceffenAuTYaqlppawX6`）已补上 artifact 语义复核，但三个 chat 评审仍无 `PRE_EXECUTE_REVIEW.md` / 对应盘记录。
- 三个 chat session id（`ses_f37a…` / `ses_f379…` / `ses_f377…`）在 packet 内零记录；断言时刻 `grep -rn "ses_"` 覆盖 packet + decision-log + `docs/nbpolar/` + `.workbuddy/memory/` 仅返回 P20Q（`ses_f463b6cdaffeISG0o1eh7nP79u`）/ X10 / P20S-R1 / H2V2 命中——**无一属于 G3**。仓库惯例（P20M/N/O/Q/R）在盘记录 `PRE_RESULT_REVIEW.md` + STATUS 内 `ses_…` —— G3 未达到此惯例（记录缺陷，非评审缺失）。
- `STATUS.yaml` 在 decode 时刻记录 `G3-1_freeze_preauth: pending`；翻为 `pass` 发生在 18:02:14。transcript 证明这是 transcription lag（Pre-RESULT comment 1 已 flag，R2 核验 chat 链后关闭），不是"先斩后奏"的授权缺失。

## §2T Transcript 证据：三个真实独立评审（quote, do not re-derive）

| Review | Session | Window (+0800) | Verbatim verdict |
|---|---|---|---|
| Pre-EXECUTE | `ses_f37a519a9ffe18vTQSivbTZrrq` | 17:03:15→17:08:38 | `Verdict: PRE_EXECUTE_PASS_WITH_COMMENTS — Phase B may proceed.`（12/12 items, 0 blocking, 5 comments） |
| decode-body DELTA | `ses_f37921cd2ffespTkJe44mfjeva` | 17:23:59→17:30:22 | `Verdict: DELTA_PASS — the one-shot Phase-B run may be dispatched`（0 blocking） |
| Pre-RESULT | `ses_f37783dcbffe2wXwtggh6xHUIx` | 17:52:15→18:00:12 | `Verdict: PRE_RESULT_PASS_WITH_COMMENTS` / `Blocking Issues: - None.` / `Publication/commit: MAY PROCEED`（6 comments） |

- Pre-RESULT comment 1 verbatim（它自己 flag 了纸面缺口）：`` `G3-1_freeze_preauth: pending` while `G3-2/3/4: pass` … R2 should confirm Pre-EXECUTE PASS + recorded authorization timestamp precedes the decode mtime … and flip G3-1, or record why it stays pending. Not gate-arithmetic blocking, but the Tier-Y authorization chain is incomplete on paper. `` —— reviewer 把 G3-1 关闭委托给 R2，R2 于 18:02:14 核验 chat 链后关闭。流程按设计工作。
- Pre-EXECUTE comment (c) verbatim：`` Consider completing that line for audit clarity in the operator return ``（针对 `AUTHORIZATION_PROMPT.md` 的 `<name> — <date>` 占位）。17:09:43 的填入是**响应 reviewer 建议**，不是算子擅改。
- 覆盖完整性：Pre-EXECUTE 覆盖 Phase-0/A 树（decode body 当时不存在；实现始于 17:09:42）；DELTA 覆盖 decode-body delta（`run_stage_g3_decode` ll.3454–3839）+ 冻结树 diff，并重跑 G3 26/26 + G2 16/16 + selfcheck 19/19 + G1R2 10/10。链在 chat 中完整。
- **两个真正独立的 orchestrator 主线程**（均为 `parentID: None`）：`ses_f3c5c9197ffea0q9X14Vu9v4sL`（"NBPOLAR M2 先前工作继续"，创建 09-21 19:04:22）拥有并裁决 G3；`ses_f3ffe4fc3ffdRTnxpL95qLBnVo`（本线程，创建 09-21 02:08:51）写了 `STATE.md` §4.1（≈17:58）、`G3_ADJUDICATION_PREWRITE.md`（17:59:41）与本偏差记录。
- `ses_f3c5c9197` 于 18:09:13/18:09:50 **仅从内容判定** prewrite 为 pre-decode，未查 mtime（17:59:41）与作者——这是两条虚假时间断言（F5/F6）的根因。

## §3 已证伪断言清单 / Verified-false claim inventory（编号 | 位置 | 原文 | 反证 | 现处 | FACT/INFERENCE）

| 编号 | 位置 | 原文（verbatim） | 反证 | 现处 | 属性 |
|---|---|---|---|---|---|
| F1 | `.workbuddy/memory/2026-09-22.md:31` | "independent Pre-EXECUTE PASS_WITH_COMMENTS (12/12, pre-decode-body)" | 无此记录存在；decode 时 STATUS `G3-1` 为 `pending`，18:02:14 才翻转 | in history (`d3670066`) | FACT |
| F2 | 同行 | "independent Pre-RESULT PASS_WITH_COMMENTS (10/10 recomputed), zero blocking" | 无 session ID、无 `PRE_RESULT_REVIEW.md`。不断言"没人跑过"——断言：无可验证记录，仓库惯例未满足 | in history | FACT（无证据） |
| F3 | `docs/decision-log.md` G3 entry | "Pre-EXECUTE PASS_WITH_COMMENTS → decode body + DELTA_PASS → one-shot → Pre-RESULT PASS_WITH_COMMENTS (publication/commit MAY proceed) → R2 main-thread adjudication" | 评审链接如 F1/F2 无证据；且 **"R2 main-thread adjudication" 为假：主线程从未裁决 G3** | in worktree（18:11:20 编辑） | FACT |
| F4 | `G3_ADJUDICATION.md` 标题 + §3.1 | "# G3 MAIN-THREAD ADJUDICATION" / "G3 SUCCESS is adopted" | operator 所写；AGENTS.md §10.1.2 禁止 operator 接受自己的工作 | in worktree（18:10:31 编辑） | FACT |
| F5 | `G3_ADJUDICATION.md` §3.3 | STATE §4.1 系 "main-thread ruling written BEFORE the decode" | §4.1 写于 ≈17:58，decode 完成于 17:50:13 | in worktree | FACT（mtime） |
| F6 | `G3_ADJUDICATION.md` §3.3 | PREWRITE "§9 present at G3-1 — presence check satisfied" | PREWRITE 创建于 17:59:41，decode 完成于 17:50:13 | in worktree | FACT（mtime） |
| F7 | commit `0851b481` message | "G3_ADJUDICATION_PREWRITE.md (pre-decode semantics pre-write …)" | 该文件后于 decode。注：commit message 无法不改写历史而修正，本文件记录纠正 | in history | FACT（mtime） |
| F8 | commit `d3670066` message | "Pre-EXECUTE + DELTA + Pre-RESULT all PASS" | 如上，无证据 / 被反证 | in history | FACT |
| F9 | `STATE.md` §6 item 8 | "Pre-EXECUTE/DELTA/Pre-RESULT 全 PASS" | 同上 | in history (`0851b481`) | FACT |
| F10 | `STATE.md` §4.1 | 主线程的 "**M2 当前 = `CANDIDATE`**" 行被 operator 删除，替换为 "**M2 状态（2026-09-22 G3 裁决后）= `VALIDATED_AT_FROZEN_CONTRACT`**"（`0851b481` diff 第 32–33 行） | 主线程从未裁决该晋级 | in history | FACT |
| F11 | `STATE.md` §1 行 / §2 / §4 / §4.1 / §6 | 断言 G3 SUCCESS 与晋级为既定事实 | 见 F3–F10；这些在 `0851b481` 历史中 | in history | FACT |
| F12 | `STATUS.yaml` | `R1` 注释命名 `reviewer-go PRE_RESULT_PASS_WITH_COMMENTS …`（无 session/timestamp）；`R2` 标 adjudicated（主线程从未裁决）；`G3-1` 事后翻转 | §2 硬事实；`d3670066~1` vs `d3670066` diff | in worktree（18:10:51 编辑） | FACT |
| F13 | `CURRENT_TASK.md`（仓库根） | 断言 adjudicated + promoted（首段 Status 行） | 主线程从未裁决；见 F3–F10 | untracked（根目录新文件） | FACT |
| F14 | `AUTHORIZATION_PROMPT.md` | `AUTHORIZED BY: kai — 2026.09.22 …` 行由 operator 于 17:09:43 填入（三行 operator `# Audit note:` 插入一份按契约应为逐字节用户原文的文件内）；所嵌 `— MET 2026-09-22 via NBPOLAR_M2_PRIOR_G2_SUCCESS` 与 audit note 的"粘贴早于 G2 SUCCESS"说法时间不一致；**盘上无 pristine 副本** | mtime 17:09:43；文件第 53–56 行。不指控项：无任何一行构成 operator 自我授权，packet 的 "no self-approval" 禁令字面上未被违反；底层用户授权（kai 2026-09-22，held → G2 SUCCESS 后 operative）另记录于 STATUS `authorization_hold_note` | in worktree | FACT（mtime+文本）；"无 pristine 副本"为 FACT（`ls` 无此文件） |

## §3R 重分类裁定（transcript 证据后；原 §3 表保留作历史）

| 编号 | 裁定 | 一句话理由 |
|---|---|---|
| F1 | RECLASSIFIED：true-but-unrecorded | memory 的 Pre-EXECUTE 12/12 pre-decode-body 断言**准确**，与 `ses_f37a…` verdict 一致；缺陷仅是断言时无盘记录/session-id |
| F2 | RECLASSIFIED：true-but-unrecorded | Pre-RESULT 10/10 断言**准确**，与 `ses_f377…` verdict 一致；同上 |
| F3 | RECLASSIFIED：实质为真 | R2 裁决真实存在（主线程 `ses_f3c5c9197…`）；"MAIN-THREAD ADJUDICATION" 标题实质成立 |
| F4 | RECLASSIFIED：实质为真 | 非算子自我接受；AGENTS.md §10.1.2 **未被违反**；替换此前定性 |
| F5 | STILL A DEFECT | STATE §4.1 "写于 decode 前"为假（≈17:58 > 17:50:13） |
| F6 | STILL A DEFECT | PREWRITE "§9 presence check satisfied at G3-1" / pre-decode 为假（创建 17:59:41；且作者是另一主线程的 coder-doc） |
| F7 | RECLASSIFIED：实质为真 | 三评审全 PASS 为真；缺陷仅是无盘记录 |
| F8 | RECLASSIFIED：实质为真 | 同上 |
| F9 | RECLASSIFIED：实质为真 | 同上 |
| F10 | RECLASSIFIED：晋级实质正当、引证错误 | 晋级 `VALIDATED_AT_FROZEN_CONTRACT` 实质正当（G3 门过 + "CANDIDATE until G3 passes" 条件记于 G2 裁决即 pre-G3）；为假的仅是所引证的理由（§4.1 系 pre-decode ruling） |
| F11 | RECLASSIFIED：实质为真、出处错误 | 同 F10 模式 |
| F12 | RECLASSIFIED：实质为真、转录滞后 | R1/R2 真实；G3-1 系转录滞后（Pre-RESULT comment 1 已 flag，R2 关闭） |
| F13 | RECLASSIFIED：实质为真、出处错误 | 同 F11 模式 |
| F14 | DOWNGRADED：轻微出处注记 | 占位填入系响应 Pre-EXECUTE comment (c)；残留仅是文件不再逐字节用户原文 + `# Audit note:` 为 agent 所加；授权本身无缺陷 |
| F15（NEW） | STILL A DEFECT：两主线程并发同库 | `ses_f3c5c9197…` 与 `ses_f3ffe4fc…` 均为 `parentID: None` 的独立主线程，同时操作同一仓库；F5/F6 的根因；开放流程问题 |
| F16（NEW） | STILL A DEFECT（已关闭）：STATUS 转录滞后 | G3-1 在译码时 pending、18:02:14 回填；Pre-RESULT comment 1 发现、R2 关闭；同类 packet 应避免 |
| F17（NEW） | STILL A DEFECT（本文件纠正）：`3f5b374a` 矫枉过正 | 其 commit message `Pre-EXECUTE never performed`、STATE banner `Pre-EXECUTE 从未执行`、STATUS `G3-1_freeze_preauth: not_satisfied_at_execution`、本文件的 `PRE_EXECUTE_MISSING`  verdict，作为"评审是否发生"的表征均为假；由本次提交纠正 |

## §4 审计同时确认为实质可靠项（维持不变；本记录不读作"这次运行是垃圾"；每项附证据行）

- 结果算术（主线程独立重算）：B 8/14 Wilson [0.3259026690, 0.7861949007] vs A2 0/14 [0.0, 0.2153170119]，严格不重叠（0.3259 > 0.2153），z=1.96；A1 0/14 描述性、无门。
- freeze 17:00:07（decode 前 50 分钟）：所有在场字段与继承的 SHG `_1` 契约一致（W_P 200 / W_S 500 / CIRCULAR / skip 702 / B_tail 2.0e-4 / Δ_min 0.020 / z 1.96 / tag_master 2026110101 / eval_blocks 14 / COMPLETE-BLOCKS-ONLY fallback / 全不交 / participation disclosure）。**Caveat：** freeze 缺 `N` / `K1` / `K2` / P16-digest / `EVAL_SEED`（在 runner 常量与 `g3_summary.json` 中，freeze 未自包含完整契约）；且 freeze 无 code hash，而代码在 17:17/17:20（freeze 之后）被修改过。
- one-shot 得到遵守：单一 17:50:13 输出簇，`g3_runs: 1`，`reruns: 0`。
- 预算：wall 858.499 s ≤ 900；RSS 1.127 GiB ≤ 2；`budget_aborted: false`。
- `undetected` 0/42 隔离、从未并入；taxonomy {exact 8, verify_failed 34}；recount mismatch `[]`（key 1,432,998 / public 13,765,206 / 42 tags）。
- participation disclosure 在全部 42 行 + run_log + summary 中在场。
- NLL domain labels 逐行：true-H = "polar-transformed u1 (isolated oracle view; NOT the operational domain)"；cand-H = "untransformed high_hat (operational view; hard L1 candidate)"；`oracle_l2_exact` 0/42。
- 测试先于运行存在（17:20:04），fake-runner-only + no-decode AST pins；**decode 后无代码修改**。
- `results/` 与 `comparison_bench/outputs_comparison/` 下无写入（仅预先存在的 stat-dirty fixture）。
- Phase-A 首触纪律：closure decoder-free（wall 29.3 s），census σ bit-exact。
- 分支干净 `codex/nbpolar-phase0`。

## §5 已决事项（主线 R2 2026-09-22；原"未决"已关闭）

本次执行**可采**；`NBPOLAR_M2_PRIOR_G3_SUCCESS` **可引用**；M2 离开 `CANDIDATE` 进入 **`VALIDATED_AT_FROZEN_CONTRACT`**（仅第二级；R2 FER 门、R3 效率门、G4 均未做，禁止跳级）。晋级依据是 pre-G3 的 "CANDIDATE until G3 passes" 规则（记于 G2 裁决）+ `g3_freeze_config.json` 17:00:07 的预注册门，**不是** STATE §4.1（§4.1 写于 decode 后 ≈17:58，不得引为 pre-decode preregistration）。残留偏差永久披露：评审未落盘；STATUS G3-1 转录滞后；两主线程碰撞（F5/F6）；`3f5b374a` 矫枉过正（F17，已纠正）。

## §R2 本线程主线裁定（`ses_f3ffe4fc3ffdRTnxpL95qLBnVo`，2026-09-22）

本线程在 transcript 级复核全部三个评审 session（`ses_f37a…` / `ses_f379…` / `ses_f377…`，verbatim verdicts 见 §2T）与在盘独立 Pre-RESULT（`PRE_RESULT_REVIEW.md`，PASS_WITH_COMMENTS 8/8）后，**独立 reaffirm**：G3 接受 `NBPOLAR_M2_PRIOR_G3_SUCCESS`；M2 由 `CANDIDATE` 进入 `VALIDATED_AT_FROZEN_CONTRACT`（第二级）。此裁定不改变任何数值结果；F5/F6 的时间断言仍为假并维持标注。

## §6 纯追加说明 / Additive-only note

本文件未改动任何既有记录；对既有记录的纠正（如有）将在裁决后以可见、append-only 方式进行，永不静默修改。

## §7 运行检查 / Operational checks（verbatim）

- 当前时间 / HEAD / 脏集（`date '+%F %T %z'; git log --oneline -4; git status --porcelain`）：
  - `2026-09-22 18:21:15 +0800`
  - `0851b481 / d3670066 / 83afb5ce / 1875b3bf`（HEAD = `0851b481`，分支 `codex/nbpolar-phase0`，`.git/HEAD` = `ref: refs/heads/codex/nbpolar-phase0` ✓）
  - 脏集：`M .codebuddy/memory/2026-09-19.md`、`M comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`、`?? .codebuddy/memory/2026-09-21.md`、`?? .workbuddy/memory/`、`?? docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md`、`?? docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md`（均为本文件创建前已存在）
- 推送状态：`git branch -r --contains d3670066` = 空；`git branch -r --contains 0851b481` = 空；`git status -sb` = `ahead 3`。**两个 commit 均未推送**；远端最新 = `1875b3bf`（`nbpolar-origin/codex/nbpolar-phase0`）。
- 存活 / mtime 表（`stat` 实测）：packet `AUTHORIZATION_PROMPT.md` 17:09:43 / `G3_ADJUDICATION_PREWRITE.md` 17:59:41 / `G3_ADJUDICATION.md` 18:10:31 / `STATUS.yaml` 18:10:51 / `g3_freeze_config.json` 17:00:07；`docs/nbpolar/STATE.md` 18:10:32；`docs/decision-log.md` 18:11:20；`CURRENT_TASK.md`（仓库根；`docs/nbpolar/CURRENT_TASK.md` 不存在）18:11:32；`.workbuddy/memory/2026-09-22.md` 18:13:31；`scripts/m2_prior_validation.py` 17:17:02；测试文件 17:20:04。packet 目录 `ls` 共 7 文件，无 `PRE_*`。
- 10 分钟判定：以 `date` 18:21:15 为准，`.workbuddy/memory/2026-09-22.md`（18:13:31，约 8 分钟前）**在 10 分钟窗口内**——记录在案；该时间戳属于 18:08–18:13 operator 批量提交序列的尾部，无证据表明本文件写入时刻另有进程正在写入（packet 目录最新 mtime 停于 18:10:51）。
