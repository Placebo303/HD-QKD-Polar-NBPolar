# TASK PACKET — r2b-fer-shg-64-L32-f120

Delta-successor（AGENTS.md §10.1/§10.4）。合同全文：`docs/nbpolar/R2B_L32_F120_DELTA_20260929.md`；
前驱包：`workspace/r2_fer_shg_64/`（只读）。本包**不授权任何事**；授权文本见 `AUTHORIZATION_PROMPT.md`，STATUS.yaml `authorizations` 为空。

## 0. 允许/禁止

- 允许写（新增，不得预先存在）：`workspace/r2b_fer_shg_64_L32_f120/results.json`、
  `part_<G2|G3>_<global_block_index:02d>.json`（64 个）、执行后的 `EXECUTION_TRANSCRIPT.md` 与日志。
- 禁止：修改任何冻结模块（sc/scl/scl_joint/scl_joint_native/two_layer/transform/algebra/prior/prior_m2/operational_f13*/
  m2_prior_validation）；写 `results/`、`comparison_bench/outputs_comparison/`、前驱目录、`workspace/m2_prior_validation/`；
  读池外帧；git 写操作；无授权运行 run.py。

## 1. 与前驱的差异（run.py diff，全文见 `DIFF_vs_predecessor.diff`）

| ID | 前驱 | 本包 |
|---|---|---|
| D1 | K1=319/K2=6492 (K=6811, f≈1.27) | K_total=6442, k1=302, k2=6140 (f=1.20)；`kdb` 用新 K；SC 路径保留 319/6492 (`k1_sc/k2_sc`) |
| D2 | `scl_joint.scl_joint_decode`, L=16 | `scl_joint_native.scl_joint_decode_native`, L=32, top_m=4；记录 native backend、k1_scl/k2_scl |
| D3 | eval_seed 2026092801 / tag 2026102801 | 2026092902 / 2026102902 |
| D4 | 保真检查 | 不变（SC 路径不变） |
| D5 | 1200 s/块, 2 GiB, 3 h, 8 路 | 300 s/块, 4 GiB, 2 h, 串行；`_total_wall_exceeded` (monotonic, 严格 >) → `not_started_total_wall_budget` |
| D6 | n=56 | 不变 |
| 其他 | | probe_id/docstring/results 元数据；taxonomy 增 `not_started` 计数与 `not_started_block_ids`；`frozen_params` 增 k_total/f_target/decoder/budget |

## 2. 验收项

- A1 run.py 与前驱的 diff 只含 §1 所列改动（审 `DIFF_vs_predecessor.diff`）。
- A2 导入期断言 (K_total,k1,k2)==(6442,302,6140)；f_book 见合同 §D1 表（G2 1.205813/1.206410，G3 1.198966/1.199560）。
- A3 SCL 调用为 `scl_joint_decode_native(L=32, top_m=4)`；SC 调用使用 `k1_sc/k2_sc`=319/6492。
- A4 种子 2026092902/2026102902；global_block_index 0..63 唯一。
- A5 启动守卫：results.json 或任一 part 已存在 → exit 2 拒绝（烟测已验证）。
- A6 预算常量 300/4/7200/串行；总 wall 边界 7200.0 不超、7200.001 超（烟测已验证）。
- A7 only `status=="ok"` 块进入分类；undetected 隔离且在任意块 scl 记录上触发 `stop_undetected`；not_started 与 resource_abort 不进 D。
- A8 环境：解释器含 Swabian TimeTagger、numpy、Rust 原生库并导出 `nbpolar_scl_decode_f64`（已验证）。
- A9 执行前 Pre-EXECUTE PASS；执行后 Pre-RESULT PASS（含 D≥56、undetected 隔离、分层表、f_book 分解）。

## 3. 返回条件

全部完成，或具体阻塞（失败命令 + 完整报错 + 已尝试补救 + 需主线程决定的单一事项）。
