# Pre-EXECUTE 审查记录 — r2b-fer-shg-64-L32-f120（2026-09-29）

独立 reviewer（Sonnet 子代理，只读）总裁决：**PASS_WITH_COMMENTS**，无阻塞项。主线程裁定：接受，进入 PI 逐字授权。

| 项 | 结果 | 要点 |
|---|---|---|
| E1 合同一致性 | PASS | K_total=6442, k1=302, k2=6140；f_book G2 1.205813/1.206410，G3 1.198966/1.199560（不含/含 CRC）；run.py:67-72 导入期断言 |
| E2 K 不交叉 | PASS | SCL 用 302/6140（run.py:439-462），SC 保真用 319/6492（:395-396）；主线程裁定此口径 |
| E3 分母/判定 | PASS | D 只计 status=="ok"；not_started 单列；undetected 扫全部块；F1 未回归；Wilson 正确 |
| E4 预算/停止 | PASS | 300 s/块、7200 s 总 wall（monotonic, 严格 >）；估算 ~70–100 min 可完成；RSS 仅 advisory |
| E5 种子/tag | PASS | 2026092902 / 2026102902 生效 |
| E6 防覆写 | PASS | 目标输出不存在；启动守卫 exit 2，先于读原始数据 |
| E7 块清单 | PASS | 与 DATA_LEDGER §7 一致（64 块，CAL32 排除） |
| E8 环境 | PASS | hd-qkd venv：Swabian TimeTagger 可导入，rust backend 可加载 |
| E9 聚焦测试 | PASS | test_nbpolar_scl_joint_native.py 15 passed/7 skipped；_smoke_synthetic.py SMOKE PASS |
| E10 授权文本 | PASS | 与合同/代码一致；authorizations: [] |

非阻塞意见：(1) 36 个非 EVAL 块描述性 SC 基线 K=6811(f≈1.27) 与 SCL f=1.20 不可直接比较，汇总须注明；(2) 总 wall 含 session 建立；(3) fork 前未调用解码；(4) 首块耗时若远超 ~41 s 估算应立即停查；运行时带 PYTHONDONTWRITEBYTECODE=1，避免与其他重 CPU 任务并跑。
