# Copy-paste authorization — Phase 6-R1

```text
我明确接受 Phase 6 strict-stop 的负结果及主线程 option (a) 处置，并授权执行仓库
D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的新任务包：
.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/TASK_PACKET.md

本授权只开放 Phase 6-R1 decode-reject-advance 的实现、合成/注入探索、测试、资源画像，
以及独立 Pre-EXECUTE PASS 后唯一一次 three-arm paired 300-block synthetic development
gate。仅将 STATUS 的 documentation_authorized、implementation_authorized、
synthetic_exploration_authorized、decoder_execution_authorized、development_gate_authorized、
rate_adaptation_authorized、phase6_r1_authorized 改为 true；其余保持 false。

冻结 K=(29,33,37,41,45)、worst-first order、GF32/N256/epsilon0.05、label=32*x_hat、
全部阈值不变。唯一语义修订：K<45 时 `ImpossibleDisclosedValueError` 记为
decode_rejected_continue，不产生候选、不调用 tag，计一次 public feedback，公开下一固定
增量并从原始 metric 完全重启 SC；K45 同类错误仍为 decode_failed。禁止吞掉其他异常、
跨层携带状态、改变 SC、跳层、调 K 或把中间拒收计为成功。

先完成 injected rescue、persistent final failure、异常 taxonomy、no-tag-on-reject、restart、
disclosure/feedback recount、tamper 与全部前驱回归。随后冻结全新未用 run/master seeds、
精确命令、唯一缺席输出根、预算和 stop rules，并取得真正独立 Pre-EXECUTE PASS。

唯一正式尝试让 static K45、原 strict-stop incremental、R1 advance 三臂使用相同的 300 个
新合成 blocks。不得读取或覆盖 Phase 5/P6 旧根。首次科学 sc_decode 即消耗 attempt 1/1；
禁止重跑、换 seed 或调参。R1 硬门保持 exact>=285/300、Wilson LB>=0.90、undetected=0、
平均 key-dependent disclosure 比 paired static 至少低 5%，并要求 coverage、桶互斥、
truth isolation、nonfinite、feedback/tag/union-bound/transcript recount 全部通过。另须报告
相对 strict-stop 的 rescued/persisted/regressed 配对计数，但不得据此改变阈值。

禁止 artifact、parquet、TTBin、DEV/EVAL、真实数据、learned policy、SCL、Phase 7、
benchmark、qualification/promotion、sibling/results/outputs_comparison 写入、commit/push。
必须独立 Pre-RESULT 重算。最终只允许返回
DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE 或 BLOCKED(<single earliest gate>)，并报告
attempt/seed 消耗及未运行阶段。
```
