# INVALID_CA_SCL — CA-SCL 副臂作废声明（2026-09-29，主线程裁定）

依据：`PRE_RESULT_REVIEW.md`（独立 reviewer-go）——CA-SCL 副臂 = **FAIL（实现缺陷）**。
SC 主臂 = PASS_WITH_COMMENTS，不受本声明影响（见 `RESULT_SUMMARY.md`）。

## 1. 作废范围（仅以标注方式作废；原始文件全部保留、不删除、不改名）
- `scl_part_*.json` 全部 64 个（pass 2 原始产物）。
- `results.json` 中：`pass2_ca_scl`、`cross_comparison_vs_nb_polar[*].table_B2_nb_scl_vs_binary_ca_scl_msg_proxy`
  及 `table_B2_coverage`、各 margin 下所有 `ca_scl_descriptive` 字段（taxonomy_by_session / taxonomy_pooled）、
  顶层 `ca_scl_arm_note`。
- 任何引用“CA-SCL msg_exact = 0 / 0 of 5120 codewords”的叙述。这些数字不得作为二元基线能力的证据。
- 不受影响：`part_*.json`（SC 主臂）、`construction_frozen_*.json`、Table A、Table B1、SC 的 pooled/分层/分 session 统计。

## 2. 原因
`run.py:377-404` `scl_descriptive_codeword` 调用 `decoder.decode_batch(...)`。该 C++ 路径把冻结位当作 0
（`main.cpp:179`，`frozen_values==nullptr → forced_bit=0`），而真实数据 `u_a = enc(a)` 的冻结位是非零真实值；
`decode_batch_frozen`（genie 冻结值，wrapper 已存在）未被使用；`crc_true` 算出后从未使用。
因此 5120 码字全部 0 成功是“调用错误”，不是二元 CA-SCL 的能力。此外“覆盖 16 个 CRC 位”方案在源编码语义下不成立。

## 3. 合成复现证据（review_scratch/pr_scl_diag.py；WSL，N=4096，p=0.0157，k=2828，PW 序取 [::-1]，12 个码字）
- run.py 同款调用（`decode_batch`，冻结=0）：**0/12** 成功。
- 信道编码式（冻结=0 且 CRC 嵌入）：12/12。
- `decode_batch_frozen`（genie 冻结值，不覆盖 CRC 位，比较全部 k 位）：**12/12**。
- SC：6/6。
估计（review_scratch/pr_fix_est.py，G2 m=0.02，每层 400 码字，iid BSC）：修复后 L=4 SCL（无有效 CRC）ΣFER 约为 SC 的 0.7 倍，
预期 f_scl≈f_sc（4.2–4.8），不会接近 NB 的 f≈1.27；定性结论不变，被撤销的只有 CA-SCL 数字。

## 4. 修复方案（未执行）
1. `scl_descriptive_codeword` 改用 `decoder.decode_batch_frozen(n, k, 1, mask, frozen_values=(u_a*(1-mask)), llr)`，
   传入 genie 冻结值；
2. 不覆盖 CRC 位；逐码字比较全部 k 个信息位；`disclosed_bits = n − k`（不加 16）；
3. 仅重跑 pass 2（约 54 min），不改 SC 部分与 construction；
4. 旧 `scl_part_*.json` 与 `results.json` 中旧 CA-SCL 字段保留原位（作为已作废记录），新产物使用新增/加前缀命名，不覆盖。

**是否重跑须 PI 另行裁决**；本声明不授权任何执行。
