# Pre-EXECUTE 审查记录 — r2d-locate-f-k-g2（2026-09-29）

独立 reviewer（Sonnet，只读）：**PASS_WITH_COMMENTS**，P1–P12 全 PASS（G3 不读、块清单、6 配置 K 核算、种子、SCL 语义同 R2B、线程覆盖在子进程生效、预算 12600 s、选择规则、启动守卫、交叉表只读、授权文本一致、smoke PASS 且不污染目录）。
意见（已处理）：1) 授权文本选择规则对齐 prereg/代码（32 块全完成、无 undetected、vf+df≤1）；2) smoke 收尾恢复值改 12600。
意见（记录）：3) Rust 另三个 kernel 用 available_parallelism，不在本路径；4) 300 s 为软检查，420 s 硬终止。
wall 估算 0.8–1.6 h（上限 3.5 h）。
