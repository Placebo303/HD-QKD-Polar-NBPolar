# G2/G3 逐块层级(L1/L2)失败归因 —— 描述性分析

**性质声明**: 本报告为只读描述性分析（descriptive），不是 claim，不改变任何已冻结状态串（`NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS` / M2 状态梯 `VALIDATED_AT_FROZEN_CONTRACT`均保持不变），不重跑任何解码器，不读取任何 .ttbin/时间标签原始数据。数据源仅为已产出的 per_block_outcomes.jsonl / *_ADJUDICATION.md / STATUS.yaml。

## 0. 数据源

- `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/{G2_ADJUDICATION.md,STATUS.yaml,g2_freeze.md}`
- `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/{G3_ADJUDICATION.md,STATUS.yaml}`
- `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/per_block_outcomes.jsonl` (G2, 42 行 = 3 臂 x 14 块)
- `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/per_block_outcomes.jsonl` (G3, 42 行 = 3 臂 x 14 块)
- 字段语义参照 `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py`（TwoLayerBlockResult，outcome 优先级 decode_failed > verify_failed > exact > undetected）与 `scripts/m2_prior_validation.py::g2_first_error`（first_error_coordinate/first_error_layer 的实际定义）。
- 跨域描述性对照：`workspace/probes/op-n32k-matched/results.json`（Tier-X，synthetic，label T6956_k1_326_k2_6630，f_book≈1.2999，share_target=0.0469）。

## 1. 字段语义说明（重要，避免误读）

- `l1_exact`（块级布尔）：该块全部 L1（high）符号是否与真值一致。
- `hard_l2_exact`（块级布尔）：该块全部 L2（low，operational 条件于 hard L1 输出）符号是否与真值一致。
- `first_error_coordinate` / `first_error_layer`：符号级扫描，取块内第一个 high 或 low 与真值不同的符号位置；若该位置上 high 已经不同 → 记 L1，否则（high 对、low 不对）记 L2。注意：这不等价于块级“L1 是否全对”——某块可能 l1_exact=False（块内某处存在 L1 错），但 first_error_layer 仍标 L2，因为块内最早出现的错误符号恰好是一个 L1 正确但 L2 错的符号，L1 错误出现在序列更靠后的位置。本分析以 l1_exact/hard_l2_exact（块级）为主归因依据，first_error_coordinate/layer 仅作辅助定位参考，两者在下表中都列出。
- `key_dependent_bits`（kdb）：本次冻结合同下恒为 34119（= K1+K2 的按符号披露位 + 64-bit Toeplitz tag），对 exact 与 verify_failed 结果一视同仁地披露（TwoLayerBlockResult 的披露会计与逐符号对错无关）。因此 kdb 不能作为“错误符号数”的代理——它在所有失败块之间不发生变化，不提供失败严重程度的区分信息。
- 逐块“错误符号数”/hamming 距离字段不存在于 per_block_outcomes.jsonl 的已记录字段集中（完整字段集见下）。可用的相关字段仅有块级布尔 l1_exact/hard_l2_exact/oracle_l2_exact 与符号级单点 first_error_coordinate/first_error_layer（只取“第一个”，不是全部错误符号的列表或计数）。n_raw_zero_hits/n_floor_lifted/floor_logloss_bits 是 L2 似然下溢/floor 诊断量，不是错误符号计数。结论：逐块错误符号数缺失，未尝试重算（遵指令止于此）。
- 已确认字段集（两个 session 完全一致）：arm, block_index, eval_frames, exact, first_error_coordinate, first_error_layer, floor_logloss_bits, hard_l2_exact, key_dependent_bits, l1_decode_failed, l1_error_type, l1_exact, l1_executed, l2_decode_failed, l2_error_type, l2_invoked, l2_skipped_by_l1_failure, label_match, n, n_floor_lifted, n_raw_zero_hits, nll_l2_candH_bits, nll_l2_candH_domain, nll_l2_trueH_bits, nll_l2_trueH_domain, nonfinite, oracle_error, oracle_l2_exact, outcome, pair_exact, participation_disclosure, public_control_bits, rss_gib_peak_advisory, sc_calls, tag_fn_calls, tag_invoked, tag_pass, truth_leak_violation, undetected, wall_s。

## 2. decode_failed / undetected 核查（应为 0）

- **G2 (SHG _1)**（42 行 = 3 臂 x 14 块）：outcome 分布 = {'verify_failed': 31, 'exact': 11}；undetected=True 行数 = **0**；l1_decode_failed=True 行数 = **0**；l2_decode_failed=True 行数 = **0**；nonfinite=True 行数 = **0**。
- **G3 (SHG _2)**（42 行 = 3 臂 x 14 块）：outcome 分布 = {'verify_failed': 34, 'exact': 8}；undetected=True 行数 = **0**；l1_decode_failed=True 行数 = **0**；l2_decode_failed=True 行数 = **0**；nonfinite=True 行数 = **0**。

**确认**：G2、G3 两个 session、全部 3 臂 x 14 块，均没有 decode_failed、undetected、nonfinite记录；唯二 outcome 取值是 exact 与 verify_failed，与两份 ADJUDICATION.md 中“taxonomy over 42 rows = {exact, verify_failed}” 的口径一致。

## 3. 逐块表

### G2 (SHG _1)

**臂 B_M2_32f_candidate** — exact 11/14

| block | outcome | L1(l1_exact) | first_error_coord | first_error_layer | L2(hard_l2_exact) | kdb | 备注 |
|---|---|---|---|---|---|---|---|
| 0 | exact | 对 | - | - | 对 | 34119 | |
| 1 | verify_failed | 对 | 1253 | L2 | 错 | 34119 |  |
| 2 | exact | 对 | - | - | 对 | 34119 | |
| 3 | exact | 对 | - | - | 对 | 34119 | |
| 4 | exact | 对 | - | - | 对 | 34119 | |
| 5 | verify_failed | 对 | 978 | L2 | 错 | 34119 |  |
| 6 | exact | 对 | - | - | 对 | 34119 | |
| 7 | exact | 对 | - | - | 对 | 34119 | |
| 8 | exact | 对 | - | - | 对 | 34119 | |
| 9 | exact | 对 | - | - | 对 | 34119 | |
| 10 | exact | 对 | - | - | 对 | 34119 | |
| 11 | exact | 对 | - | - | 对 | 34119 | |
| 12 | verify_failed | 对 | 2000 | L2 | 错 | 34119 |  |
| 13 | exact | 对 | - | - | 对 | 34119 | |

**臂 A1_M0_1024f_incumbent** — exact 0/14

| block | outcome | L1(l1_exact) | first_error_coord | first_error_layer | L2(hard_l2_exact) | kdb | 备注 |
|---|---|---|---|---|---|---|---|
| 0 | verify_failed | 对 | 111 | L2 | 错 | 34119 |  |
| 1 | verify_failed | 对 | 148 | L2 | 错 | 34119 |  |
| 2 | verify_failed | 对 | 125 | L2 | 错 | 34119 |  |
| 3 | verify_failed | 对 | 54 | L2 | 错 | 34119 |  |
| 4 | verify_failed | 对 | 30 | L2 | 错 | 34119 |  |
| 5 | verify_failed | 对 | 54 | L2 | 错 | 34119 |  |
| 6 | verify_failed | 对 | 148 | L2 | 错 | 34119 |  |
| 7 | verify_failed | 对 | 312 | L2 | 错 | 34119 |  |
| 8 | verify_failed | 错 | 5 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 9 | verify_failed | 错 | 10 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 10 | verify_failed | 对 | 436 | L2 | 错 | 34119 |  |
| 11 | verify_failed | 对 | 49 | L2 | 错 | 34119 |  |
| 12 | verify_failed | 错 | 4 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 13 | verify_failed | 对 | 18 | L2 | 错 | 34119 |  |

**臂 A2_M0_32f_matched** — exact 0/14

| block | outcome | L1(l1_exact) | first_error_coord | first_error_layer | L2(hard_l2_exact) | kdb | 备注 |
|---|---|---|---|---|---|---|---|
| 0 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 1 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 2 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 3 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 4 | verify_failed | 错 | 1 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 5 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 6 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 7 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 8 | verify_failed | 错 | 3 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 9 | verify_failed | 错 | 1 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 10 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 11 | verify_failed | 错 | 1 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 12 | verify_failed | 错 | 6 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 13 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |

### G3 (SHG _2)

**臂 B_M2_32f_candidate** — exact 8/14

| block | outcome | L1(l1_exact) | first_error_coord | first_error_layer | L2(hard_l2_exact) | kdb | 备注 |
|---|---|---|---|---|---|---|---|
| 0 | verify_failed | 对 | 6611 | L2 | 错 | 34119 |  |
| 1 | verify_failed | 对 | 911 | L2 | 错 | 34119 |  |
| 2 | verify_failed | 对 | 119 | L2 | 错 | 34119 |  |
| 3 | exact | 对 | - | - | 对 | 34119 | |
| 4 | verify_failed | 对 | 175 | L2 | 错 | 34119 |  |
| 5 | exact | 对 | - | - | 对 | 34119 | |
| 6 | exact | 对 | - | - | 对 | 34119 | |
| 7 | exact | 对 | - | - | 对 | 34119 | |
| 8 | exact | 对 | - | - | 对 | 34119 | |
| 9 | exact | 对 | - | - | 对 | 34119 | |
| 10 | verify_failed | 对 | 1207 | L2 | 错 | 34119 |  |
| 11 | verify_failed | 错 | 379 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 12 | exact | 对 | - | - | 对 | 34119 | |
| 13 | exact | 对 | - | - | 对 | 34119 | |

**臂 A1_M0_1024f_incumbent** — exact 0/14

| block | outcome | L1(l1_exact) | first_error_coord | first_error_layer | L2(hard_l2_exact) | kdb | 备注 |
|---|---|---|---|---|---|---|---|
| 0 | verify_failed | 对 | 285 | L2 | 错 | 34119 |  |
| 1 | verify_failed | 对 | 67 | L2 | 错 | 34119 |  |
| 2 | verify_failed | 对 | 41 | L2 | 错 | 34119 |  |
| 3 | verify_failed | 错 | 73 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 4 | verify_failed | 对 | 99 | L2 | 错 | 34119 |  |
| 5 | verify_failed | 对 | 139 | L2 | 错 | 34119 |  |
| 6 | verify_failed | 对 | 233 | L2 | 错 | 34119 |  |
| 7 | verify_failed | 对 | 17 | L2 | 错 | 34119 |  |
| 8 | verify_failed | 对 | 27 | L2 | 错 | 34119 |  |
| 9 | verify_failed | 错 | 14 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 10 | verify_failed | 错 | 52 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 11 | verify_failed | 错 | 11 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 12 | verify_failed | 对 | 17 | L2 | 错 | 34119 |  |
| 13 | verify_failed | 错 | 85 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |

**臂 A2_M0_32f_matched** — exact 0/14

| block | outcome | L1(l1_exact) | first_error_coord | first_error_layer | L2(hard_l2_exact) | kdb | 备注 |
|---|---|---|---|---|---|---|---|
| 0 | verify_failed | 错 | 1 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 1 | verify_failed | 错 | 4 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 2 | verify_failed | 错 | 2 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 3 | verify_failed | 错 | 3 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 4 | verify_failed | 错 | 2 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 5 | verify_failed | 错 | 1 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 6 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 7 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 8 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 9 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 10 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 11 | verify_failed | 错 | 3 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 12 | verify_failed | 错 | 0 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |
| 13 | verify_failed | 错 | 2 | L2 | 错 | 34119 | 块内含L1错误，但首个错误符号早于L1错误位置(见字段说明) |

## 4. 汇总：B 臂失败的分层归因

| session | B臂失败块 | l1_exact=True(纯L2错误) | l1_exact=False(块内含L1错误) |
|---|---|---|---|
| G2 (SHG _1) | 3 | 3 | 0 |
| G3 (SHG _2) | 6 | 5 | 1 |
| **合计** | **9** | **8** (88.9%) | **1** (11.1%) |

**B 臂失败的分层结论**：9 个失败块中 8 个（88.9%）是“L1 全对、L2 出错”（纯 L2 层失败）；1 个（G3 block 11，11.1%）是“块内存在至少 1 处 L1 错误”（同时该块 L2 也不对）。所有失败块的 first_error_layer 逐一核查均为 L2（见 §3 表，无一行是 L1），但如 §1 所述，这是“首个错误符号”口径，不等价于“块级 L1 全对”；块级归因请以 l1_exact 列为准。

## 5. 参照：A1 / A2 臂（所有失败块）分层归因

| session | 臂 | 失败块数 | l1_exact=True(纯L2) | l1_exact=False(含L1错) |
|---|---|---|---|---|
| G2 (SHG _1) | A1_M0_1024f_incumbent | 14 | 11 | 3 |
| G2 (SHG _1) | A2_M0_32f_matched | 14 | 0 | 14 |
| G3 (SHG _2) | A1_M0_1024f_incumbent | 14 | 9 | 5 |
| G3 (SHG _2) | A2_M0_32f_matched | 14 | 0 | 14 |

**观察（描述性）**：A2（M0 + 匹配 32 帧 CAL，无 M2 候选先验）的失败块 100%% 含 L1 错误（G2: 14/14, G3: 14/14，块级 l1_exact 全部为 False）——稀疏 32 帧 CAL 下 M0 的 L1 统计明显不足。A1（M0 + 自有 1024 帧 CAL，样本量约为 A2 的 32 倍）的失败块则以纯 L2 失败为主（G2: 11/14=78.6%%，G3: 9/14=64.3%%），与 B 臂（M2 候选先验 + 匹配 32 帧 CAL）的纯 L2 失败占比（88.9%%）方向一致——即 M2 候选先验在稀疏 CAL 下把 B 臂的 L1 层表现拉到接近甚至优于 A1（大 CAL）的水平，B 臂剩余失败集中在 L2 层，这与 A1 的主要失败模式相同，而与 A2（L1 主导失败）不同。这是描述性观察，非统计检验、非跨臂比较声明（各臂各自的 Wilson 门只针对 exact 计数，本节的 L1/L2 拆分不改变、不重算任何已裁决的 Wilson 区间或 SUCCESS 判定）。

## 6. 跨域描述性对照：synthetic op-n32k-matched（仅方向，不比量级）

来源：`workspace/probes/op-n32k-matched/results.json`（Tier-X，non-claim，claims 字段自述：no significance/better-than-baseline/... no pass/fail verdict）。取 label T6956_k1_326_k2_6630（f_book≈1.2999 ≈ 1.30，share_target=0.0469=4.69%%）。

| label | op exact | oracle exact | op 失败块 | oracle 在同块 |
|---|---|---|---|---|
| T6956_k1_326_k2_6630 | 13/16 | 16/16 | 3 块，outcome=decode_failed | 同 3 块 outcome=exact |

**跨域方向性观察**：在这个 synthetic 匹配信道探针里，operational 的 3 个失败块在 oracle（条件于真实 L1，不受 L1 决策误差影响）视角下全部变回 exact——即该探针把这 3 个失败归因于 L1（per_label_note: "both arms failing together must not be attributed to L-H1 alone" —— 探针本身也提示不要把两臂同时失败简单归为 L1，此处仅取“operational 失败但 oracle 成功”的差集作为 L1 归因证据）。这与真实数据 G2/G3 的 B 臂（M2 候选先验、匹配 32 帧 CAL）方向相反：B 臂的失败以纯 L2 为主（88.9%%），L1 错误占比很低（11.1%%）。这是跨域方向性对照，不是量级比较——synthetic 探针使用 delta∈{-1,0,+1} 的G1R2-matched 信道模型 + 不同的 outcome taxonomy（decode_failed vs 真实数据的 verify_failed），K1/K2 分配点也不同（k1=326/k2=6630 vs 真实的 319/6492），二者不可直接换算或合并为同一结论；本节不产生、不修改任何 candidate/accepted 状态或 Tier-Y 结论。

## 7. 结论摘要（供主线程引用）

1. **有无 decode_failed / undetected**：G2、G3 全部 84 行（42x2）均无 decode_failed/undetected/nonfinite；outcome 仅 exact/verify_failed 两类，与 ADJUDICATION 记录口径一致。已确认。
2. **B 臂失败的分层**：9 个失败块（G2: 3, G3: 6）中 8 个（88.9%%）为纯 L2 层失败（L1 块级全对），1 个（G3 block 11）块内含 L1 错误。多数失败发生在 L2 层，不在 L1 层。
3. **kdb / 错误符号数**：key_dependent_bits 在所有失败块恒为 34119（冻结披露会计，与逐符号对错无关），不提供失败严重程度的区分信息；逐块错误符号数字段不存在于已产出记录中，仅有块级布尔（l1_exact/hard_l2_exact/oracle_l2_exact）与符号级单点（first_error_coordinate/layer，仅首个）——按指令止步于此，未尝试重算。
4. **verify_failed 的分类**：所有失败块（B/A1/A2，两个 session）的 outcome 均为单一分类 verify_failed（tag 校验失败但非 decode_failed/undetected），没有子分类字段区分“差 1 处”还是“差多处”。
5. **跨域对照方向**：synthetic op-n32k-matched（f≈1.30, share 4.69%%）的 3 个失败块 100%% 可归因于 L1（oracle 全部恢复 exact）；真实数据 B 臂的失败以 L2 为主（88.9%%）。方向不同，仅作描述性并列，非量级比较，非跨域推断。
