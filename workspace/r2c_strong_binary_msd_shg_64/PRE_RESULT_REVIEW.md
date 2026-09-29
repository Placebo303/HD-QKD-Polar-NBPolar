# Pre-RESULT 审查记录 — r2c-strong-binary-msd-shg-64（2026-09-30）

独立 reviewer（Sonnet，只读，从 64 个 part 文件与 construction_frozen_* 逐块重算）：**PASS_WITH_COMMENTS**，无阻塞项。
R1 计数/Wilson/undetected（256 块点）PASS；R2 f 记账逐会话逐点复算、"二元不付 CRC"与合同 §5/§6/D4 一致 PASS；R3 undetected 隔离 PASS；R4 分层 PASS；R5 构造阶段数字与 k_i 独立重算、构造只用 CAL32 PASS；R6 首错层与 NB 配对四格表 PASS；R7 PASS_WITH_COMMENTS；R8 PASS_WITH_COMMENTS。
已采纳：F2 结论句并列分会话 2/32 vs 16/32；局限补 0/64 Wilson 上界 0.057>0.03、F2 同披露总量口径、设计集粒度、3% 点 f 区间 1.28–1.313；§8 注明执行窗口内 r2c-layer-diag 残留作业可能的 CPU 争用；状态行更新。
