# CODE_REVIEW.md — scl_joint.py / test_nbpolar_scl_joint.py 独立评审

评审者：reviewer-go（只出 findings，不改代码）。范围：`comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl_joint.py`、
`comparison_bench/tests/test_nbpolar_scl_joint.py`；`scl.py`/`sc.py`/`two_layer.py`/`prior.py` 只读，未改动（已核对无 diff）。

## 判定：**FAIL**（阻断 T3 2+小时门；根因是测试而非联合算法本身）

## 关键发现

1. **[FAIL-1] T-a 回归测试当前实际失败，与其 docstring「N=64 已验证可靠」不符。**
   `pytest comparison_bench/tests/test_nbpolar_scl_joint.py` 实测 = **1 failed, 4 passed**。
   `test_l1_m1_identity_matched_channel` 在 `TEST_SEED_A=2026092751, N=64, k1=5, k2=20` 的 **block=2**
   处 `low_hat` 不一致 (`assert got.low_hat.tolist() == ref.operational.low_hat.tolist()` 失败)。
   用 review_scratch 脚本复现并定位根因：`U[2]` 处 `sc_decode` 与 `scl_decode(L=1)` 在同一 `p2` 行上
   两个候选符号的原始分数只差 `4.44e-16`（真正的 float64 并列），随后 SC 递归的级联效应把这一个叶子
   的翻转放大成 7 个位置、最大 75 个自然对数单位的下游发散——**根因诊断本身是对的**（`scl.py`
   `decode_leaf` 用 `path.metric+score` 排序、`sc.py` 用纯 `argmax(row)`，是 `scl.py` 既有、docstring
   已如实描述、不在本次改动范围内的性质），但"N=64 可靠"的经验声明是假的：本机复现同一采样序列
   N=64 共 20 block 中 5 个不一致（25%），N=256（k1=5/k2=20 及 45/110）几乎全部不一致（19-20/20）。
   **这是一个当前会在 CI/pytest 中真实 FAIL 的测试，不是描述性 flaky 项**——AGENTS §10.1/tasks.md T2
   明确要求"聚焦测试必须在执行前通过"，T3 计时探针已经在此状态下跑了（`timing.json`），属于流程缺口。
   **最小修复建议**（转交 coder，不越权改代码）：不要求修改 `scl.py`；改为 (a) 让 T-a 用脚本实际穷举/
   验证过、真正 0 mismatch 的 seed+block+n 组合替换当前断言用例，或 (b) 在测试里显式检测该已知
   float64 近并列（例如对 L2 metric 逐叶最大与次大分数差设一个数值阈值，若某 block 触发已知并列则
   跳过并计入一个"skip_due_to_known_scl_tiebreak"计数而非静默通过/失败），并重新贴上真实验证过的
   docstring 结论。修复后必须重跑并确认 0 failed。

2. **[PASS] 联合度量自洽性与真值隔离。** `m1`（L1 `scl_decode` 的 `path_metrics`）与 `m2`（对每个
   L1 硬候选 `gather_p2_metrics(bob_row, high_cand[None,:], p2_table)` 后重新 `scl_decode` 的
   `path_metrics`）都是 `scl.py` 同一套自然对数、`LOGSUMEXP_ZERO` 归一化路径度量，量纲一致，`m1+m2`
   是自洽的联合对数似然，与 `two_layer.py` 的 `CANDIDATE_CONDITIONED` 构造方式完全一致
   （对照 `run_two_layer_block` L666 一行）。L2 度量正确用**候选** `high_cand` 重建，从未用真值或
   SC 结果代替；`scl_joint_decode` 全程不接受 Alice 真值参数，真值只可能通过调用方传入的 `crc_true`
   （标量）间接介入，且只用于逐候选 CRC 比较，绝不进入候选排序（排序只看 `joint_metric`）。经
   `test_small_n_enumerator_oracle_matches_full_width_joint_scl`（独立、非递归的暴力枚举 oracle）
   验证一致，1e-9 容差通过，该测试本次 pytest 运行通过。

3. **[PASS] 披露语义。** `d1_positions/d1_values`、`d2_positions/d2_values` 与 `sc_decode`/`scl_decode`
   的 `known_positions/known_values` 契约完全一致：真值只在测试/探针脚本里一次性构造披露值
   （`u1_true[d1]`），再作为公开披露传入解码器，与 `two_layer.py`（`pos1/u1_disclosed` 等）同构，
   不构成真值泄漏进排序或 CRC 计算路径。

4. **[PASS] CRC。** `crc16_ccitt_false_bits("123456789")==0x29B1` 测试通过（已知校验值正确）。CRC 对象
   是 Alice **完整符号串**（`s=low+32*high` 每位置，复用 `two_layer.labels_to_bits` 的 10-bit
   MSB-first 打包），解码侧对**每个候选**重算比较；`crc_bits` 恒为 16，无论 pass/fail 只计一次
   （`test_crc_bits_counted_once_pass_and_fail` 通过，含强制翻转 CRC 的 fail 分支）。

5. **[PASS] top-M / top-L 剪枝与回退。** `top_l_prune` 用 `np.argsort(-metrics, kind="stable")` 截断，
   不改变并列顺序；`top_m_used=min(top_m, l1_res.survivor_count)` 正确处理 L1 存活数不足 M 的情况；
   合并排序键 `(-joint_metric, l1_rank, l2_rank)` 是确定性的，且 `l1_rank`/`l2_rank` 本身已是各自
   `scl_decode` 调用内部 canonical 排序结果，故复合顺序有效——由 oracle 测试里对
   `ranked_candidates` 全表单调性的断言覆盖（本次通过）。`crc_failed` 时回退到 `ranked[0]`
   （联合度量最高者），标记为 report-only，从不静默提升为 pass；`test_crc_bits_counted_once_...`
   显式检查了这一点。

6. **[COMMENT] `SCLJointResult` 本身不产出 `exact`/`undetected` 分桶**（不同于 `two_layer.ArmBlockResult`
   的 `outcome` 字段）。这是设计上合理的（模块不接受真值，无法自行分类），但意味着 **T3 驱动脚本
   必须自己**用 `label_hat` 与真值比对 + `crc_pass` 交叉算出 `undetected`（CRC 通过但错），模块
   docstring 未明确写这一责任转移。建议在 T3 packet/脚本里显式核对这一步存在，否则"undetected 单独
   统计"这一 R2 披露语义要求可能被漏掉。

7. **[PASS] 计时探针披露口径。** `timing_run.py`/`timing.json` 明确记录 `disclosure_note`：用固定前缀
   `0..k-1` 而非 `worst_k`，并声明"解码耗时取决于 N/list-width，与披露哪些位置无关"——这个理由
   在 `sc.py`/`scl.py` 的实现里成立（复杂度是 `O(N q^2 log N)` 逐位置遍历，disclosed 位置只是跳过
   分支而非改变整体复杂度量级），不会让计时明显偏离 T3 真实负载。非阻断。

## 复现方式（供转交）
`workspace/probes/scl-joint-timing/review_scratch/{repro_ta_n256.py, repro_ta_n256_verbose.py,
isolate_l2_divergence.py}`；用 `D:\software\Miniforge3\python`（本机唯一可用的带 numpy/pytest 解释器，
`.venv` 在本 checkout 不存在，非本评审引入的问题，供主线程知悉环境现状）。
