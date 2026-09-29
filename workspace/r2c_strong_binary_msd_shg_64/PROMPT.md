# PROMPT — execution operator, r2c-strong-binary-msd-shg-64

你是执行 operator（只执行，不裁决）。前置：主线程已贴出 PI 逐字授权（`AUTHORIZATION_PROMPT.md`）、Pre-EXECUTE 审查 PASS、STATUS.yaml `authorizations` 已填。缺任一项 ⇒ 不要运行，回报阻塞。

1. 读 AGENTS.md（§3、§5.7、§10.1、§10.3）与 `TASK_PACKET.md`。仓库 `D:\Code\HD-QKD_Polar_Comparison-nbpolar`（WSL `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`），分支 `codex/nbpolar-phase0`。
2. 运行前检查：`results.json`、`part_*.json`、`construction_frozen_*.json` 均不存在；`git -C /mnt/d/Code/qkd-reconciliation-lab status --porcelain` 记录到 `EXECUTION_TRANSCRIPT.md`；确认没有其它重负载进程占用（`uptime`）。
3. 运行 `AUTHORIZATION_PROMPT.md` 末尾的命令（一次，重定向 stdout/stderr 到本目录 `run.log`；记录命令/PID/起止时间）。不得改任何参数、种子、阈值、f 网格或 L。
4. 若退出码 3（不变性门失败，D2）：不要重跑；把 `construction_frozen_*.json` 中的 `invariance` 段回报主线程（STOP 交 PI）。若退出码 4：lab 目录被改动，立即回报。
5. 只允许一次"实现缺陷重启"，且须先回报缺陷、得到主线程确认，并记为独立 attempt；绝不因结果不理想重跑。
6. 完成后回报：命令与起止、退出码、`results.json` 中 `block_accounting`、`stop_undetected`、`resources`、`lab_readonly_check.lab_unchanged`、各 f 点 pooled exact/verify_failed/undetected/D；不做判定、不写 RESULT_SUMMARY / OPERATOR_RETURN（须先经独立 Pre-RESULT 审查）。
7. 返回条件只有两种：全部完成，或具体阻塞（失败命令 + 完整报错 + 已尝试补救 + 需主线程决定的单一事项）。
