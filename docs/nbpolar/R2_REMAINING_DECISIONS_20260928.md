# R2 剩余待决项 — 20260928（planner 建议稿，含推荐值）

- **性质**：为 `openspec/changes/nbpolar-r2-fer-measurement-contract` T4 剩余 8 行
  PENDING（D-ACQ-01/04/07/08、D-FER-04/05/06/07）准备**可一句话批准**的推荐值。
  与既有纪律（`R2_T4_PI_DECISION_CARDS_20260927.md`、`R2_OPEN_INPUTS_DECISION_LIST_20260925.md`）
  不同：**本文件按 PI 明确要求给出推荐值**，但每条推荐都必须可追溯到
  `AGENTS.md` §5.8 R1–R5、`docs/nbpolar/DATA_LEDGER.md`、PI 已采纳的方向
  （M2 + SCL(L=16, top_m=4, CRC-16) + K1=319/K2=6492 + P16，在 SHG `_1`/`_2`
  全会话共 64 块上做一次预注册 FER 测量，HELDOUT 与已解码 EVAL 分层报告，
  适用域限定 2026-01-13 两次 SHG 采集）。
- **本文件本身不裁定、不冻结、不授权**：仍需 PI 逐行确认（或按建议批准）后，
  由 T4 把对应行由 `PENDING` 改为 `DECIDED` 并写回
  `openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md` §5 ledger；
  T5/T6/T7/T8/T9 仍分别受 `tasks.md` GATE-T5/GATE-T6/BOUNDARY-T7T8 与
  `AGENTS.md` §10.3 Pre-EXECUTE/Pre-RESULT 约束，本文件不改变、不绕过这些门。
- **已裁决背景（不重开，仅引用）**：D-FER-01（Wilson z=1.96）/D-FER-02（w=0.10）/
  D-FER-03（n=56，2026-09-28 重裁决，替代旧值 n=65）/D-ACQ-02（源=SHG `_1`/`_2`
  全会话）/D-ACQ-03（配额=每会话 32 块）/D-ACQ-05（适用域=仅限两次 2026-01-13
  SHG 采集）/D-ACQ-06（预算=40 s/block、2 GiB/block、5400 s 总量、单进程独占、
  超预算 STOP）均 `DECIDED`；出处 `openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md:87-115`、
  `docs/nbpolar/DATA_LEDGER.md` §7、`docs/decision-log.md` 2026-09-27/28 各条目。

---

## D-ACQ-01 — 执行分支与目标 n/w

**① 待决项原文**（`docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md:95`）
> 执行分支（A: 50–100 / A′: ~260 / B 远期）与目标 n、w。

**② 可选项**
- O-1a：按 Branch A（50–100 blocks 量级）落地，用现有 64 块池、n=56、w=0.10。
- O-1b：按 Branch A′（w=±0.05 → n≈259）落地——现有 64 块不足，需新采集。
- O-1c：维持 PENDING。

**③ 推荐值：O-1a — 64 块、n=56、w=0.10。**

**理由**：
- `D-FER-02`（w=0.10）与 `D-FER-03`（n=56）已经是 `DECIDED`
  （`openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md:110-116`），
  这两行已经**落在** `ACQUISITION_SPEC_DRAFT_20260922.md:19` 定义的 Branch A
  （50–100 blocks）区间内（56 ∈ [50,100]），不需要 Branch A′（~260）或 Branch B（~1000，
  R3 远期 aspiration，`FER_DEFINITION_DRAFT_20260922.md:64-69`）。
- `DATA_LEDGER.md` §7（`:126-154`）已算出：R2 合格源 = 64 块，**覆盖** n=56 的样本量
  目标，**无需新采集**——这正是 R5 流程规则的示例（`AGENTS.md` §5.8 R5）：本条不得
  脱离这一已算出的缺口（=0）另选 A′/B。
- 选 O-1a 不需要任何新数据、不新增采集窗口，是"最简单、科学上可辩护"路径
  （PI 采纳方向明示）。

**④ 是否阻塞冻结**：**阻塞**——D-ACQ-01 是 C10 分支承载行，T5 配额算术的方向性
输入之一；但由于 n/w 已 `DECIDED`，本行事实上只是把已定的 n/w 正式挂到
"Branch A" 标签上，风险低。

---

## D-ACQ-04 — Type0 纳入与否

**① 待决项原文**（`docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md:98` /
`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:192`）
> `Type0_nofilter_*` 是否纳入 R2 样本系独立决策：(i) 不纳入；(ii) 纳入但单列报告。

**② 可选项**
- O-4a：不纳入（草稿默认）。
- O-4b：纳入，单列报告（不与 SHG 混算 FER）。
- O-4c：维持 PENDING。

**③ 推荐值：O-4a — 不纳入。**

**理由**：`DATA_LEDGER.md` §5（`:88-104`）记录 7 个 `Type0_nofilter_*`/`Type2_*`
2026-01-20/21 会话，配置与参照（SHG `_1`/`_2`）在**电子学/resolution 模式**层面
不一致（resolution Standard vs HighResB、normalization True vs False、
resolution_rms 2.0 vs 1.5、ch1 delay 55/289 vs 4 ps 量级差异，见 `DATA_LEDGER.md:90-98`）——
`DATA_LEDGER.md:100-104` 明确这与此前 PI 已裁定的"Type0/SHG 只是**光源**差异、对
IR 过程无影响"是**不同层面**的问题，两者不得混同：光源差异已裁定不影响 IR，
但 resolution/normalization 差异是采集通道本身的差异，未经验证是否可比。
2026-09-28 盘点范围本就**未对这些会话计帧**（`DATA_LEDGER.md:100`），无解析后
ledger 可用；纳入需要额外的可比性论证（工作点声明、`D-ACQ-05` 式差异带），
而当前 64 块 SHG 池已覆盖 n=56，没有必要为凑数引入一个配置不一致、未计帧的源。
按 R5：先查账本、算缺口——缺口已是 0，不纳入 Type0 不产生任何样本量风险。

**④ 是否阻塞冻结**：**不阻塞** T5 配额算术（T5 只用 SHG 64 块池运行）；但 C11
仍需要这一行有一个明确状态（`DECIDED(不纳入)` 而非空白 PENDING）才能让 T3
的红线映射验收完全落地。

---

## D-ACQ-07 — 配对与构造契约沿用

**① 待决项原文**（`docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md:101`）
> 配对/构造契约沿用（W_P/W_S/MOD/skip/K1/K2/P16）：默认继承冻结契约；任何偏离需
> 单独立项。

**② 可选项**
- O-7a：全部沿用 G2/G3 冻结值（W_P=200/W_S=500/CIRCULAR/skip=702/K1=319/K2=6492/P16
  digest `055c9064…`），**且沿用 G2/G3 各自的 tag_master**（G2 `2026103001`，
  G3 `2026110101`）。
- O-7b：构造契约（W_P/W_S/MOD/skip/K1/K2/P16）沿用 G2/G3 冻结值，但 **tag_master
  为 R2 新铸造、单一、预注册的值**（两会话统一用同一个新 master，不复用 G2/G3
  各自的旧 master）。
- O-7c：维持 PENDING。

**③ 推荐值：O-7b —— 构造契约沿用，tag_master 新铸造。**

**理由（含对可复现性的影响说明）**：
- **构造契约部分（W_P/W_S/MOD/skip/K1/K2/P16）沿用没有争议**：这些是
  `AGENTS.md` §5.3 schema-stability 保护的冻结值，G2/G3 已验证一致
  （`docs/decision-log.md:177,201`："Frozen contract INHERITED/intact:
  K1=319/K2=6492, P16 digest `055c9064…`, W_P=200/W_S=500/CIRCULAR/skip=702"）；
  R2 沿用即 C14 的默认行为，无需单独立项。
- **tag_master 需要新铸造、不能沿用**，理由有三：
  1. **本仓已有直接先例**：G3 本身就没有沿用 G2 的 tag_master——G3 铸造了
     "G3-fresh" 的 `2026110101`，与 G2 继承值 `2026103001` 显式不同
     （`docs/decision-log.md:177`"tag_master 2026110101 G3-fresh, distinct
     from G2's inherited 2026103001"）。即：**同一构造契约下沿用配对/K1/K2/P16、
     但为每次新的独立解码执行铸造新 tag_master，本身就是这两次会话已经在
     用的模式**，R2 只是把这个模式延伸到"新的一次独立测量"而不是"新的一次会话"。
  2. **R2 是一次新的、独立预注册的测量执行**（M2 + **SCL**(L=16, top_m=4,
     CRC-16)，而 G2/G3 冻结的是 **SC**——`docs/decision-log.md:85-114` 的
     2026-09-28 SCL 27/28 合并本身被明文标注为"描述性诊断,不构成 R2 决策"）。
     `AGENTS.md` §10.3 Pre-EXECUTE 要求"冻结输入、命令"在执行前锁定；把 R2
     的验证 tag 绑定到一个属于 G2 或 G3 各自旧执行上下文的 master，会让"R2
     是独立预注册测量"这一定位变得含糊——沿用哪一个（G2 的还是 G3 的）本身
     就没有单一答案，而两会话各用各的旧 master 又会让"64 块统一池"在 tag
     层面变得会话异构，增加不必要的复杂度。
  3. **R1（"解码 ≠消耗"，`AGENTS.md` §5.8）覆盖的是披露记账**，不覆盖 tag
     生成本身——重新验证一个已解码块不产生新披露，但这不等于必须复用旧
     tag_master；铸造新 master 不违反 R1。
- **对可复现性的影响（必须在合同里写清楚）**：
  - G2/G3 各自的冻结 SC 结果（含各自的 42 个 tag、`per_block_outcomes.jsonl`）
    **完全不受影响**——它们仍在各自的冻结 tag_master 下产生，是各自 change 的
    frozen 证据，永久保持可复现（不改、不重算）。
  - 2026-09-28 的 SCL 描述性合并结果（27/28，`docs/decision-log.md:85-114`）
    同样不受影响——那次运行复用的是 G2/G3 各自的冻结 tag（未铸造新 master）。
  - R2 一旦执行，会对全部 64 块（含 28 个已解码 EVAL 块）在**新 tag_master**
    下重新计算 tag 并重新判定 taxonomy；R2 报告中的 `exact`/`verify_failed`
    **tag 字节值**会与 G2/G3 冻结产物、以及 2026-09-28 SCL 描述性产物**不同**
    ——这是**预期行为、不是不一致**，R2 报告必须显式声明"R2 使用独立铸造的
    tag_master，其 tag 值与 G2/G3 冻结产物及 2026-09-28 SCL 描述性合并的 tag
    值不可逐字节比对，taxonomy 分类结果（exact/verify_failed 计数）预期一致
    （Toeplitz 通用哈希在不同 master 下误判概率同量级，不因换 master 而系统性
    改变分类），但**不保证**逐块 bit-identical 复现旧 artifact 的 tag 字段"。
  - 具体数字（新 tag_master 的取值）建议遵循已有命名惯例——`eval_seed`→
    `tag_master = eval_seed + 10000`（`scripts/m2_prior_validation.py:419-420,2848-2849`
    与 `comparison_bench/tests/test_nbpolar_m2_g3_confirm.py:476-477` 已验证的
    惯例）；具体数字在 T6 packet 组装时机械生成即可，不需要 PI 对具体整数值再
    做一次实质裁决（PI 需要批准的是"新铸造、单一、统一两会话"这个**政策**）。

**④ 是否阻塞冻结**：**阻塞**——C14 明确"任何偏离需单独立项"，tag_master 新铸造
就是这样一处偏离，必须在 T4 显式裁定，否则 T6 无法写 `authorizations` 之外的
"command"字段（Pre-EXECUTE 需要锁定的具体输入之一）。

---

## D-ACQ-08 — 最低会话数（≥2）

**① 待决项原文**（`docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md:102`）
> 独立 session 复现的最低会话数（路线图 R1 门 ≥2）是否与 R2 同批采集满足。

**② 可选项**
- O-8a：两个 SHG session（`_1`/`_2`）满足 ≥2 session 门，同批即满足，无需新会话。
- O-8b：≥2 session 门需要**额外**新会话（不算 SHG `_1`/`_2` 本身）。
- O-8c：维持 PENDING。

**③ 推荐值：O-8a —— 两个 session 同批满足。**

**理由**：`DATA_LEDGER.md` §1/§2 记录的正是两个**物理独立**的采集
（`20260113_SHG_Type2PPLN_3s` 与 `20260113_SHG_Type2PPLN_3s_2`，各自独立的
`frame_census.json`/对齐复现，`DATA_LEDGER.md:36-71`），G2/G3 本身已经把它们当作
两个独立 session 处理（各自独立冻结 tag_master、独立对齐复现 σ 值：G2
112.45189572400645，G3 114.43029692866367/114.4 附近，见 `docs/decision-log.md:177,201`）。
路线图 R1 门"≥2 session"的字面要求（≥2 个物理独立采集）已经满足；`D-ACQ-05`
的裁定原文也把两次 SHG 采集并列处理、适用域"仅限于这两次 2026-01-13 SHG
采集自身条件"（`tasks.md:89`），隐含承认这两次是两个可比较的独立观测。按 R5
（先查缺口）：不存在"额外会话"缺口。

**④ 是否阻塞冻结**：**阻塞** C13 的合取项（`design.md:75`"`READY_FOR_QUALIFICATION`
的 sessions 合取项继续悬空"）；本条裁定后该合取项可以闭合。

---

## D-FER-04 — `H(q)` → 经验 `H(X\|Y)` 替换口径

**① 待决项原文**（`docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md:98`）
> `H(q)`→经验 `H(X\|Y)` 替换口径：必须预注册；具体估计子待定。

**② 可选项**
- O-4a：每 session 用**自己的** CAL32 M2 三元组拟合现算 `H_total`（不共享常量）。
- O-4b：两 session 共用一个 pooled/hand-filled 常量 `H_total`。
- O-4c：维持 PENDING。

**③ 推荐值：O-4a —— 每 session 自算，不共享常量。**

**理由**：
- 这**已经是本仓的既定做法**，不是新发明：G2/`docs/decision-log.md:5569`
  记录 G2（SHG `_1`）"H_M2 = 0.0252536+0.7915602 = **0.8168138**"，由该 session
  自己的 CAL32（frames 1024–1055）三元组拟合现算；G3 同样在
  `docs/decision-log.md:116`（2026-09-28 SCL 重解条目）明确写"G3 的
  `h_total_bits=0.8214782076249098` **由 G3 自身的 CAL 拟合现算，非沿用他处
  常量**"。2026-09-28 的 `f_book` 计算（`workspace/m2_scl_check_g2g3_success/run.py:263-276`）
  同样是每个 session 各自 `fit_g2_arm`→`model_entropy_bits`→`H_total_bits`，
  从未跨 session 共享一个常量。
- `AGENTS.md` §5.5"`beta_eff_empirical` 必须从泄漏与错误输入导出，绝不手填"——
  沿用同一纪律：`H(X\|Y)` 必须是每次测量自己的经验拟合，不是手填/共享常量。
- 估计子/来源：CAL32（32 帧，1024–1055）该 session 自己的 M2 候选先验三元组拟合
  （q0/q+1/q−1/q_rest），走 `scripts/m2_prior_validation.py` 中
  `fit_g2_arm`→`model_entropy_bits` 同一代码路径（已在 G2/G3/2026-09-28 SCL
  包三次独立验证一致）；偏差处理：raw-count MLE + 1e-15 floor（无额外偏差修正，
  与既有 H_total 计算一致，未使用 Miller–Madow 等偏差修正——沿用 M2 既有算法，
  不在 R2 引入新估计量）。
- 预注册数值（供 T5/T6 直接引用）：G2（SHG `_1`）`H_total = 0.8168138`
  （`docs/decision-log.md:5569`）；G3（SHG `_2`）`H_total = 0.8214782076249098`
  （`docs/decision-log.md:116`）。**CAL32 本身仍按 R3 保持排除/牺牲，不进入
  64 块池**——这里只是复用 CAL32 已经算出的 `H_total` 数值（R1"解码≠消耗"精神的
  类比：CAL32 已经被"消耗"过一次用于先验拟合，复用其已算出的 `H_total` 不构成
  新的接触）。

**④ 是否阻塞冻结**：**阻塞** C6/D-FER-04 行，属于 f_FER 计算（D-FER-05）的直接
输入；但因为两个数值已经存在于仓库并被两次独立验证过，裁定成本极低。

---

## D-FER-05 — `f_FER` 记账式冻结

**① 待决项原文**（`docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md:99`）
> `f_FER` 记账式冻结：指向 Martínez-Mateo→Müller eq(11)/(13)，项级合同待 R3。

**② 可选项**
- O-5a：采用本仓已实现、已通过 Pre-RESULT 的 `f_book` 公式（含 CRC、含 tag，
  按每 session 自己的 `H_total` 归一化），作为 R2 的 `f_FER` 记账式，并显式声明
  它与 Müller eq(11) 的差异点。
- O-5b：重新按 Müller eq(11) 逐项建一套新的失败块加权记账式。
- O-5c：维持 PENDING。

**③ 推荐值：O-5a —— 采用既有 `f_book_with_crc` 公式，显式声明与 Müller eq(11) 的差异。**

**理由**：
- 公式（`workspace/m2_scl_check_g2g3_success/run.py:286-289`，与
  `workspace/m2_scl_rescue_g2g3/run.py:275-276` 完全一致，已经过 Pre-EXECUTE/
  Pre-RESULT 双重独立复核 `PASS`）：

  ```text
  kdb_no_crc   = disclosed_bits_per_coordinate × (K1 + K2) + tag_bits
  kdb_with_crc = kdb_no_crc + CRC_BITS_EXTRA        # CRC-16 ⇒ +16
  f_FER = f_book_with_crc = kdb_with_crc / (H_total_bits × N)   # N = 32768
  ```

  每 session 各自用自己的 `H_total_bits`（D-FER-04）代入。
- **含 CRC、含 tag**：`kdb_with_crc` 已经把 K 坐标披露（`K1+K2` 个坐标 ×
  `disclosed_bits_per_coordinate`）、Toeplitz tag 位（`tag_bits`）、CRC-16
  （`+16`）三项全部计入分子——直接满足题面"写成含 CRC、含 tag…的记账式"要求。
- **含失败块**：在本协议（leak-then-decode，K 坐标在解码**之前**无条件披露）中，
  `kdb_with_crc` 对**每一个**有效 block（无论 `exact` 还是 `verify_failed`/
  `decode_failed`）都是**同一常数**——因为 K 坐标披露发生在解码结果揭晓之前，
  与结果无关。这是本协议与 Müller eq(11)"失败帧按整帧计入泄漏、成功帧只计
  已用部分"这一**交互式/增量披露**协议假设的**结构性差异**，必须在 R2 报告中
  显式声明（不是把 Müller 公式囫囵套用）：
  - 相同点：两者都遵守"失败块不得少计泄漏"的精神——本协议因为披露无条件
    发生，失败块的记账天然等于成功块，不存在"少计"的风险。
  - 差异点：Müller eq(11) 的加权是因为它的协议里失败/成功披露量不同；本协议
    不需要这个加权，因为披露量本就与结果无关。R2 报告中必须用一句话把这个
    差异写清楚，避免读者误以为 R2 直接照搬了 Müller 的加权规则。
- **stated f vs computed f**（C7 要求）：`f_book_with_crc`（上式）= computed f
  （从实际披露位数反推）；stated f = 当前冻结 K1=319/K2=6492 隐含的设计目标
  （现行频率约 f≈1.275，`docs/decision-log.md:120`"`f_book`：G2 不含 CRC
  1.2747448953789544 / 含 CRC 1.2753426830727925；G3 不含 CRC
  1.267506841182456 / 含 CRC 1.268101234613064"）。R2 报告应并排列出两者，
  不得只报一个。

**④ 是否阻塞冻结**：**阻塞** C7/D-FER-05；但由于公式与两组 session 的实测数字
已经在本仓存在且通过评审，裁定成本低，只是把已验证的公式**指定为 R2 的
frozen 记账式**（而不是发明新公式）。

---

## D-FER-06 — `undetected > 0` 升级规则

**① 待决项原文**（`docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md:100`）
> `undetected > 0` 升级规则：待定。

**② 可选项**
- O-6a：`undetected ≥ 1` ⇒ 单列该块（不并入 FER 分子分母）+ 摘要中大声 STOP
  声明 + 该次测量**暂缓**判定 `FER_MEASURED_AT_CONTRACT`，升级给 PI 复核后再定。
- O-6b：`undetected ≥ 1` ⇒ 单列 + 摘要声明，但**不阻断** `FER_MEASURED_AT_CONTRACT`
  判定（照常按有效分母出 FER）。
- O-6c：维持 PENDING。

**③ 推荐值：O-6a —— 单列 + 大声 STOP 声明 + 暂缓晋级、上报 PI。**

**理由**：
- `undetected`（tag 通过但实际解码错误——最危险的一类，Toeplitz 哈希漏检）在
  C4/C5 中已经是"永不并入 success 或 FER"的隔离类目（`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:89-94,103`），
  这部分**不需要**本条再裁定——本条只裁定"出现 ≥1 个之后如何升级处理"这一
  额外反应。
- `ACQUISITION_SPEC_DRAFT_20260922.md:86-87`（§10 stop 规则）已有先例："任何
  frozen-contract 外的拟合/选窗/选模 ⇒ STOP 大声；歧义 ⇒ STOP 并上报，不猜测"；
  `undetected` 是安全模型里最不该出现的事件（若在 G2/G3 42 块中出现过 0 次——
  `docs/decision-log.md:177,201` 两次均"undetected 0/42 isolated"），一旦在
  64 块（约 1.5 倍规模）里出现 ≥1，是明显偏离既有经验分布的信号，按同一
  "歧义/异常⇒STOP、不猜测"精神处理最一致：**先大声披露+暂缓晋级**，比"照常
  出数字"更保守，也更符合 `AGENTS.md` §3 Pre-RESULT 门"issue 触发立即返工，
  不得先发布再补丁"的精神——`undetected` 属于比"结果需要返工"更严重的"安全模型
  异常"，理应比普通 issue 更谨慎。
- 不选 O-6b：如果只声明不暂缓，等于让一个"哈希漏检"事件在不经过 PI 复核的
  情况下就被"消化"进正常报告流程，与"最危险类目"的定性不符。

**④ 是否阻塞冻结**：**阻塞** C4/C14/D-FER-06；本条只裁定**规则**（升级到什么
程度），不产生任何数字，成本低。

---

## D-FER-07 — per-acquisition-frame 派生读数允许条件

**① 待决项原文**（`docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md:101`）
> per-acquisition-frame 派生读数允许条件：默认不允许；例外需预注册。

**② 可选项**
- O-7a：R2 本次**不报**任何 per-frame 派生读数（维持草稿默认）。
- O-7b：R2 允许报告，但只作**描述性**（non-claim）附注，不进入任何门/结论。
- O-7c：维持 PENDING。

**③ 推荐值：O-7a —— 不报（或至多 O-7b 描述性附注，两者皆可，但默认不报）。**

**理由**：
- C2/C8（`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:64-70,128-132`）已经把
  reconciliation block（32768 symbols）定为**唯一**统计单位，per-frame 读数
  "默认不允许…派生读数为次要、non-claim，不得替代 C2 单位"。R2 的核心任务是
  按 `AGENTS.md` §1.1"最短科学有效路径"完成一次 block 级 FER 测量，不需要
  额外维护一套 frame 级派生指标；这类附加读数属于"审计/verifier 精细化"的
  范畴，`AGENTS.md` §1.1 明确"这类工作只应在能具体导致错误结论/不可复现/
  破坏性覆盖时才可阻塞算法工作"——per-frame 读数目前没有任何门依赖它，纯增量
  维护负担，默认关闭最省力也最不容易引入新的口径漂移。
- 若之后有具体科学问题需要 frame 级粒度（例如想看错误是否集中在某些帧内位置），
  应该是一次单独预注册的子研究，而不是搭在 R2 主测量里顺手做。

**④ 是否阻塞冻结**：**阻塞** C8/D-FER-07（需要一个明确状态而非空白），但裁定
本身是"关闭一个默认关闭的开关"，成本最低。

---

## T5 配额算术（64 块来源 + 余量 + COMPLETE-BLOCKS-ONLY 影响）

**来源**（`docs/nbpolar/DATA_LEDGER.md` §7，`:126-154`，帧区间按 post-skip 编号）：

| 层（stratum） | 帧区间 | 每 session 块数 | 两 session 合计 | 备注 |
|---|---|---|---|---|
| `A1_CAL_characterization` | 0–1023 | 8 | 16 | 曾用于 M0（非 M2）拟合定征，须标注分层 |
| `HELDOUT_model_selection` | 1056–2397（余 62 帧不用） | 10 | 20 | 参与过 M2 的 NLL 模型选择（G1R2 门），须标注分层 |
| `EVAL_already_decoded` | 2398–4189 | 14 | 28 | 已按冻结候选 SC 解码（+2026-09-28 SCL 描述性），须标注"已解码" |
| **合计** | — | **32** | **64** | CAL32（1024–1055，两 session 各 32 帧）始终排除，不计入任何层 |

- **算术**：16 + 20 + 28 = **64** 块（与 `DATA_LEDGER.md:50,70-71,75` 的
  "32+32=64"逐字一致）。
- **与 n=56 对照的余量**：64 − 56 = **8 块余量**（约 12.5%）。
  - 若按**分层各自独立**门槛读（即每一层都要单独 ≥56）：**无一层单独达标**
    （最大层 EVAL 仅 28 < 56）——这一点在下面"仍需 PI 决定"一节单独列出，
    因为它直接决定 n=56 与"HELDOUT/EVAL 不得合并"这两条已冻结规则要如何共存。
  - 若按（本文件建议的）**跨层汇总**读（64 块合并计入分母，同时仍必须输出
    分层描述表满足"不得合并为单一未分层数字"里"不得**只**给一个数字、隐藏
    分层"的实质要求）：64 ≥ 56 达标，余量 8 块。
- **对 COMPLETE-BLOCKS-ONLY 的影响**：64 块全部是完整 128 帧块（`DATA_LEDGER.md`
  §1/§2 表逐行标注"块仍为 128 帧"），RESERVE（29/99 帧）本就 <1 block 已被排除、
  未计入 64 块池，不存在"凑不满整块"的风险；只要执行时未出现
  `resource_abort`/`undetected` 把有效分母打到 56 以下，COMPLETE-BLOCKS-ONLY
  的 `INSUFFICIENT ⇒ INCONCLUSIVE` 触发条件（`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:194-196`）
  不会被触发；8 块的余量本身就是对"万一有 1–2 个块因 undetected/resource_abort
  被剔除"的天然缓冲，但缓冲有限（若被剔除数 >8，仍会跌破 n=56）。

## 预计判定规则（`FER_MEASURED_AT_CONTRACT`）

按已冻结的 D-FER-01（Wilson z=1.96）/D-FER-02（w=0.10）/D-FER-03（n=56），本文件
建议的判定链：

1. **执行**（Pre-EXECUTE 通过、显式用户授权后，T8）：对 64 块池按冻结候选
   （M2 + SCL(L=16, top_m=4, CRC-16) + K1=319/K2=6492 + P16 + D-ACQ-07 新
   tag_master）逐块解码+验证，落入 C5 五元 taxonomy（`exact`/`verify_failed`/
   `decode_failed`/`undetected`/`resource_abort`）,分层记录（`A1_CAL_characterization`/
   `HELDOUT_model_selection`/`EVAL_already_decoded`）。
2. **有效分母** `D = #exact + #verify_failed + #decode_failed`
   （剔除 `undetected` 与 `resource_abort`，C2/C5）。
3. **COMPLETE-BLOCKS-ONLY 检查**：若 `D < 56` ⇒ `INSUFFICIENT` ⇒ `INCONCLUSIVE`，
   **不得**垫块/复用/缩 N（C11）；本文件建议的 8 块余量在此处起作用。
4. **点估计** `p̂ = (#verify_failed + #decode_failed) / D`。
5. **Wilson 95% CI**（z=1.96）：
   `center = (p̂ + z²/2D) / (1 + z²/D)`；
   `half_width ≈ z·sqrt(p̂(1−p̂)/D + z²/4D²) / (1 + z²/D)`。
6. **`undetected` 检查**（D-FER-06）：若 `undetected ≥ 1`——单列该块 id、大声 STOP
   声明，**暂缓** `FER_MEASURED_AT_CONTRACT` 判定，升级 PI 复核；若
   `undetected = 0`（与 G2/G3 42/42 先例一致）——继续第 7 步。
7. **晋级判定**：`D ≥ 56` 且步骤 6 未触发 STOP ⇒ 可判定
   `FER_MEASURED_AT_CONTRACT`（该候选配置、该 64 块池），**适用域限定**为
   D-ACQ-05 裁定文字（"仅适用于 2026-01-13 两次 SHG 采集自身条件"）。
8. **必须包含在报告中的分层项**（不得省略任一项）：
   - 三层（`A1_CAL_characterization`/`HELDOUT_model_selection`/
     `EVAL_already_decoded`）各自的 taxonomy 计数表 + 各自 Wilson CI（描述性，
     供比对"是否有系统性差异"）；
   - 跨层汇总的 taxonomy 计数表 + 汇总 Wilson CI（主报告点估计，n=56 达标判定
     以此为准，见下节"仍需 PI 决定"关于 pooling 语义的说明）；
   - "已行使过的选择自由度"表（R2(b) 要求）：哪些块（`A1_CAL`/`HELDOUT`）
     曾参与 M0/M2 的哪一步模型选择（先验拟合 / NLL 打分），不得省略；
   - `undetected`、`resource_abort` 各自计数与逐块 id 披露（即使为 0 也要
     显式写"0"，不得留空）；
   - `f_FER`（D-FER-05 公式）与 `H_total`（D-FER-04，两 session 分列）；
     computed f vs stated f 并排；
   - Carried caveats (a)–(d)（C1，逐字承接）+ D-ACQ-05 适用域声明。
9. 全流程仍受 `AGENTS.md` §10.3 Pre-EXECUTE（执行前）与 Pre-RESULT（发布前）
   两道独立复核门约束，T6 `authorizations: []` 不因本文件而改变，T7/T8/T9
   仍需另行明确用户授权。

## 仍需 PI 本人决定、无法给推荐的点

1. **n=56 与"HELDOUT/已解码 EVAL 不得合并"如何共存**：`D-ACQ-05` 冻结文字
   （`tasks.md:89`）明确"HELDOUT（1838-2397）与已解码的 EVAL（2398-4189）
   必须分层报告，不得合并为单一未分层 FER 数字"。但三层任一单独都达不到
   n=56（最大 28 < 56），只有跨层汇总才能达到 64 ≥ 56。本文件按"汇总数字
   + 强制分层表并列展示"给出建议读法（见上节判定规则第 8 步），但"不得合并
   为单一未分层数字"这句话本身是否允许"给一个汇总数字，但同时给分层表"，
   还是要求"**完全不给**任何跨层汇总数字"，是文字本身的歧义，建议 PI 用
   一句话明确："n=56 达标判定 = 跨层汇总分母（可以出一个汇总 FER 数字，但
   必须同表给出三层分列），还是 = 任一单层各自判定（若选后者，当前 64 块
   不足以让任何单层达标，需另行决定是否降低 n 或扩大某一层）"。
2. **D-FER-06 的"STOP 暂缓晋级"是否需要额外的 Tier-Y 一次性纪律豁免**：
   若 `undetected ≥ 1` 触发 STOP、暂缓判定，这次测量本身是否仍计入"一次性
   执行、不得重跑"的 Tier-Y attempt 预算（即：STOP 之后如果 PI 复核认为可以
   继续晋级，是当次结果直接采纳，还是要重新走一次新的 one-shot？）——这是
   一条纯流程/纪律问题，本文件不代 PI 裁定。

---

## 最短裁定格式（PI 逐行填一句即可）

```
D-ACQ-01 = 按建议（O-1a：64 块 / n=56 / w=0.10）
D-ACQ-04 = 按建议（O-4a：Type0 不纳入）
D-ACQ-07 = 按建议（O-7b：构造契约沿用，tag_master 新铸造统一一个）
D-ACQ-08 = 按建议（O-8a：两 session 同批满足 ≥2 门）
D-FER-04 = 按建议（O-4a：每 session 自算 H_total，G2=0.8168138 / G3=0.8214782076249098）
D-FER-05 = 按建议（O-5a：沿用 f_book_with_crc 公式，含 CRC/tag，声明与 Müller eq(11) 的结构差异）
D-FER-06 = 按建议（O-6a：undetected≥1 单列 + STOP 声明 + 暂缓晋级上报 PI）
D-FER-07 = 按建议（O-7a：本次不报 per-frame 派生读数）
```

*本文件为 planner 建议稿；不裁定、不冻结、不授权。裁定权属 PI（T4），归位写入属
本 change 的 T2 文档更新流程；T5/T6/T7/T8/T9 门序与 `AGENTS.md` §10.3
Pre-EXECUTE/Pre-RESULT 复核不因本文件而改变。*
