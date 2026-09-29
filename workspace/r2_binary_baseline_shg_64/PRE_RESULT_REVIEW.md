# PRE_RESULT_REVIEW — r2-binary-baseline-shg-64 (独立 reviewer-go, 2026-09-29)

## 判定：SC 主臂 = PASS_WITH_COMMENTS；CA-SCL 副臂 = FAIL（实现缺陷，须 INVALID + 修复重测）
整包不可按现状发布 Table B2 / ca_scl_descriptive / “CA-SCL msg_exact=0” 叙述。SC 臂（Table A、B1、pooled/分层/分 session 计数）可发布，须带下述 caveat。

## A. 常规核查（独立重算，全部吻合）
- 64 个 part + 64 个 scl_part 重算：exact/fail = 4/60（m=0.02）、9/55（0.08）、25/39（0.18）；Wilson 失败率 [0.850,0.975]、[0.754,0.924]、[0.487,0.719]，与 results.json 一致。undetected=0、decode_failed=0、tag_pass&!exact=0（512 项）。
- 分层（A1_CAL/HELDOUT/EVAL）：m=0.18 为 7/16、8/20、10/28；分 session G2/G3：11/32、14/32；m=0.02：3/32、1/32；与 results.json 一致。
- Table A / B1 用 NB part 重算：三个 margin 全部逐格吻合（如 0.18：A=21/32/4/7；B1=23/39/2/0）。
- block_accounting 64=64 contributing，一致；写入范围：目录内新增文件 + 我自己的 review_scratch，无 results/ 或 sibling 写入。
- 注：R2 分层里 A1_CAL_characterization 的 16 块曾参与模型选择（R2 规则要求单独 stratum），已单列，OK。

## B. 异常诊断
### 异常 2（CA-SCL msg_exact≡0）= 实现 BUG（run.py:377-404 `scl_descriptive_codeword`）
- 证据：它调用 `decoder.decode_batch(...)`（run.py:397 附近），该 C++ 路径把冻结位当作 0（main.cpp:179 `frozen_values==nullptr → forced_bit=0`）；但真实数据 u_a=enc(a) 的冻结位是非零真实值。`decode_batch_frozen`（genie 冻结值，wrapper 已存在）没有被使用；`crc_true`（run.py 内）算出后从未使用。
- 合成复现（WSL，N=4096, p=0.0157, k=2828，PW 序取 [::-1]，12 码字，脚本 review_scratch/pr_scl_diag.py）：run.py 同款调用 0/12 成功；信道编码式（冻结=0 且 CRC 嵌入）12/12；`decode_batch_frozen`（genie 冻结值，不覆盖 CRC 位，比较全部 k 位）12/12；SC 6/6。结论：5120 码字全 0 是“调用错误”，不是基线能力。
- 附带：CRC 覆盖位方案本身在源编码语义下不成立；正确用法是 genie 冻结 + 不覆盖，CRC 检查会失败并回落到最优路径度量（等价于无 CRC 的 L=4 SCL），此时 f_scl≈f_sc（无 16bit/码字 CRC 税，或需另行说明 CRC 实际未起作用）。
### 异常 1（f_book_sc 4.1–4.8）= 基线原生“独立比特面 + 每码字 FER<0.05”模型所致，非 SC 实现 bug
- (1) 逐层 BER 合理：G2 = [4.9e-4, 7.3e-4, 1.5e-3, 3.2e-3, 7.3e-3, 1.57e-2, 2.94e-2, 5.93e-2, 0.1245, 0.2438]（construction_frozen_G2.json grid_points[*].layers[*].ber），MSB→LSB 单调升，LSB≈p(−1)+p(+1)=0.244，与 G1R2 δ 分布吻合；层序 layer_idx0=MSB（shift=9），与 `_extract_real_layer_bers`（experiments/run_real_polar_max_pie.py:566-581）逐字一致；y 侧取 Bob 同一比特面（run.py decode_block_all_layers：`layer_bit(sym_b, layer_idx)`）。高位层 k=3789/3779（几乎全信息位），并未浪费冻结位：高位层冻结 ≈300/4096，符合 BER→0 时容量近 1。
- (2) 基线原生无跨层条件化（grep：src/、experiments/ 无 MSD/conditional 译码，仅 sibling Release 的 low_dim_opt 有）。独立模型的熵：G2 Σh(BER_i)=2.1006，G3 2.0740；而 H(X|Y)=0.8168（G2 h_total_bits）/δ 分布熵 0.818。比值 2.57 (G2)/2.52 (G3)——即使容量达到、有限长度损失为 0、margin=0，独立层模型的 f 下限已是 ≈2.5–2.6。实测 f_book_sc=4.23–4.33（m=0.02–0.08）：分解为 2.57（模型下限）+ ≈1.7（N=4096 SC 有限长度差距：Σ(cap−k/N)=1.44 bit/符号 ÷0.817=1.76）。故 f≈4 由模型与 N=4096/PW 序 SC 所致。
- (3) 映射/MSB 顺序/ y 侧比特：见上，一致。构造序 `_polar_weight_order(N)[::-1]`（run.py:1359）与基线 run_real_polar_max_pie.py:553 一致（我的合成测试需 [::-1] 才通，反向证明 run.py 用对了）。
- (4) 100 帧 MC 校准：k 选取有赢家诅咒（最大 k 满足 ≤4/100 次错），导致实际码字 FER 偏高；且候选 k 只有 {1,.95,.9,.85,.8,.7,.6,.5}×k_base 的粗档。这解释异常 3：如 G2 layer9，m=0.02 时 k_base=733 的高档未过 MC → 落到 439（0.6×），m=0.08 时 k_base≈487 的 1.0× 过了→486，故 f 非单调（4.33 vs 4.23）。属基线原生校准噪声，非 bug；但 f(m) 曲线因此不可当作平滑单调曲线解读。
- 失败率 0.61–0.94 与设计吻合：基线准则是“每码字 FER<0.05”，块含 80 码字，块成功≈exp(−8·ΣFER_l)。用 construction 的 fer_calibrated 预测 G2 m=0.08：ΣFER=0.18 → 成功 ≈0.24（实测 5/32=0.16）；m=0.18：ΣFER=0.09 → 0.49（实测 11/32=0.34，G3 14/32）。量级吻合（略低，属赢家诅咒 + 真实数据非 iid）。这说明该基线的“FER<0.05/码字”规则本身就不能给出块级 FER≈0.03，而不是 SC 出错。
- 网格局限：`all_layers_usable`（run.py:~310）要求每层 k>16，margin≥0.2 时 layer9 的 k_base≤0 使整点被丢弃，于是网格只覆盖 f≈4.1–4.8、块失败率仍 0.4–0.9 的区间，看不到“块 FER 接近 NB 的 0.03 时二元基线需要多大 f”。这是冻结合同的取舍，需在发布语句中明确。
- (6) 与 Release 文档一致：POLAR_VS_LDPC_CROSS_REPO_COMPARISON_20260927.md §5.3：lab 二元 Polar 在其最优点（d=1024,bw300, BER 9e-5…2.2e-2, H(A|B)=0.3027）f_EC≈3.0（leak/H(A|B)），LDPC 在真实 Type2PPLN 数据 f_EC=2.92；口径 = leak/H(A|B)，独立比特面。本包 BER 更高（LSB 0.244）、且无 DE、N 固定 4096，f≈4.2 同量级，不矛盾。
## C. 发布条件与最小修复
1. SC 臂：可发布，措辞限定为“冻结原生二元 SC 基线（PW 序、独立比特面、每码字 FER<0.05 的校准准则、100 帧 MC）在该池上的表现”；必须并列写出：Σh(BER_i)/H=2.57 独立层下限、f(m) 非单调是 MC 噪声、网格未触及块 FER≈0.03 区、未做条件化 MSD（Release low_dim_opt 有，不属本基线）。f 与 NB 的 f_book_with_crc 口径需注明二元含 tag 但不含 per-layer CRC。
2. CA-SCL 副臂：标 INVALID，撤回 Table B2 与 ca_scl_descriptive 全部数字。修复：`scl_descriptive_codeword` 改用 `decoder.decode_batch_frozen(n,k,1,mask, frozen_values=(u_a*(1-mask)), llr)`，不覆盖 CRC 位，逐码字比较全部 k 个信息位，`disclosed_bits = n−k`（不加 16）；重跑 pass2（约 54 min，仅 pass2，不改 SC 部分与 construction）。旧 scl_part_* 移至 invalid_ 前缀保留。
3. 预期（合成估计，review_scratch/pr_fix_est.py，G2 m=0.02，每层 400 码字，iid BSC）：层 3/5/6/7/8/9 的 SC 失败率 0.045/0.010/0.0025/0.0075/0.020/0.010，修复后 L=4 SCL（无有效 CRC）0.0425/0.005/0.0025/0.0075/0.0075/0.000，即 ΣFER 约降为 SC 的 0.7 倍——只是小幅改善。因此修复后块成功率仅比 SC 略高（m=0.18 由 ≈0.39 到约 0.45–0.55），f_scl≈f_sc（4.2–4.8，无 CRC 税），不会接近 NB 的 f≈1.27。“二元基线 f≈3–4×NB 且块 FER 高得多”这一定性结论不变；被撤销的只有 CA-SCL 数字。
