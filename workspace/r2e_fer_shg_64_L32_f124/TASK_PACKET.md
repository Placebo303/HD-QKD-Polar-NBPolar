# TASK PACKET — r2e-fer-shg-64-L32-f124

Delta-successor（AGENTS.md §10.1/§10.4）。合同全文：`docs/nbpolar/R2E_L32_F124_DELTA_20260929.md`；
前驱包：`workspace/r2b_fer_shg_64_L32_f120/`（只读，已执行/已裁决）。K 来源：`workspace/r2d_locate_f_k_g2/`（只读，描述性定位）。
本包**不授权任何事**；授权文本见 `AUTHORIZATION_PROMPT.md`，STATUS.yaml `authorizations` 为空。

## 0. 允许/禁止

- 允许写（新增，不得预先存在）：`workspace/r2e_fer_shg_64_L32_f124/results.json`、
  `part_<G2|G3>_<global_block_index:02d>.json`（64 个）、执行后的 `EXECUTION_TRANSCRIPT.md` 与日志。
- 禁止：修改任何冻结模块；写 `results/`、`comparison_bench/outputs_comparison/`、前驱目录、`workspace/r2d_locate_f_k_g2/`、
  `workspace/m2_prior_validation/`；读池外帧；git 写操作；无授权运行 run.py。

## 1. 与前驱的差异（run.py diff 见 `DIFF_vs_predecessor.diff`）

| ID | R2B | 本包 |
|---|---|---|
| E1 | K_total=6442, k1=302, k2=6140 (f=1.20) | K_total=6657, k1=253, k2=6404 (R2D f1.24_s0380)；硬编码并断言；SC 路径仍 319/6492 |
| E2 | eval_seed 2026092902 / tag 2026102902 | 2026092904 / 2026102904 |
| E3 | 分层：official / task | 另增 `stratum_selection`（G3=clean, G2=selection_touched）、`taxonomy_by_stratum_selection`、`clean_layer_G3_descriptive`（n=32 仅描述）、`known_hard_block_gbi23`（每块记录 `known_hard_block`，仍在分母） |
| E4 | 判定/预算/解码器 | 不变（D 规则、300 s/块、4 GiB、7200 s、串行、native L=32 top_m=4） |
| 元数据 | probe_id / docstring / classification | 更新为 r2e |

## 2. 验收项

- A1 run.py 与 R2B 的 diff 只含 §1 所列改动。
- A2 导入期断言 (K_total,k1,k2)==(6657,253,6404)；f_book 见合同 §E1 表（G2 1.245976/1.246574，G3 1.238902/1.239496）。
- A3 SCL 调用 native L=32 top_m=4；SC 用 319/6492。
- A4 种子 2026092904/2026102904；global_block_index 0..63 唯一。
- A5 启动守卫：results.json 或任一 part 已存在 → exit 2（烟测已验证）。
- A6 预算常量与总 wall 边界（烟测已验证）；not_started 路径写出 selection 标签（烟测已验证）。
- A7 仅 status=="ok" 入 D；undetected 隔离并触发 stop_undetected；not_started/resource_abort 不进 D。
- A8 selection 标签：G3 全 clean，G2 全 selection_touched；gbi 23 ∈ G2 EVAL，带 known_hard_block 标注但计入所有分母。
- A9 执行前 Pre-EXECUTE PASS；执行后 Pre-RESULT PASS（D≥56、undetected 隔离、四套分层表并列、clean 层 Wilson 附"n=32 仅描述"、f_book 分解、gbi 23 单列）。

## 3. 返回条件

全部完成，或具体阻塞（失败命令 + 完整报错 + 已尝试补救 + 需主线程决定的单一事项）。
