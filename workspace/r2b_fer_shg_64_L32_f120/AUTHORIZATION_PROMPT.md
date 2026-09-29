# AUTHORIZATION — r2b-fer-shg-64-L32-f120

**Status: TEMPLATE. NOT YET GRANTED.** 由 PI 阅读后整段原样贴回聊天。链接不构成授权（AGENTS.md §10.1）。
前置：独立 Pre-EXECUTE 审查 PASS。

---- 可直接复制的授权文本 ----

授权执行 r2b-fer-shg-64-L32-f120（R2B，r2-fer-shg-64 的 delta-successor）：在 SHG _1/_2 全会话共 64 块（DATA_LEDGER.md §7 冻结清单：每会话帧 0–1023 共 8 块、1056–2335 共 10 块、2398–4189 共 14 块；CAL32 帧 1024–1055 不入池）上，用 M2 先验 + 原生 SCL（scl_joint_native.scl_joint_decode_native，Rust 全递归，L=32，top_m=4，CRC-16；等价标准 B，证据 commit 8fcc9119 T-N1/T-N2）、P16（digest 055c9064…faea1b）、W_P=200/W_S=500/CIRCULAR/skip=702 做一次性 FER 测量。K：两会话共用 K_total=6442（f=1.20），k1=302、k2=6140；SC 保真路径仍用冻结的 K1=319/K2=6492。这是与前驱不同的实现，本次结果是"原生 SCL 实现"在 L=32、f=1.20 下的测量，不是对 scl_joint 的复现；前驱 SCL(L=16) 结果只作描述性参考，不作保真门。eval_seed=2026092902、tag_master=2026102902。预算：串行，每块 wall ≤ 300 s、RSS ≤ 4 GiB、总 wall ≤ 2 h（超限后未开始的块记 not_started，不进分母）、原生线程数取默认值，超预算即 STOP 不调参。判定规则：有效分母 D = exact + verify_failed + decode_failed，D < 56 判为 INSUFFICIENT，否则给出 Wilson 95% 点估计和置信区间；汇总数字必须与分层表同时报告（P-1）；只要 undetected ≥ 1，就单列、STOP、暂缓判定，并计入这次 one-shot（P-2）；28 个已解码 EVAL 块中任一 SC 保真检查与 per_block_outcomes.jsonl 不一致，就标为保真受损、不做判定。解释器 /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python。输出只写 workspace/r2b_fer_shg_64_L32_f120/。one-shot，reruns=0（只允许修复实现缺陷后重启一次，绝不因为结果不理想而重跑）。本授权不替代 Pre-EXECUTE 和 Pre-RESULT 独立审查，也不替代主线程对结果的最终裁定。

---- 授权文本结束 ----

执行命令（授权后，WSL，仓库根目录）：

```
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2b_fer_shg_64_L32_f120/run.py
```
