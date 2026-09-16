# Copy-paste authorization — Phase 6 fixed incremental disclosure

```text
我明确接受 Phase 5 的主线程验收范围，并授权执行仓库
D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的新任务包：
.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/TASK_PACKET.md

本授权仅开放 Phase 6 固定嵌套 disclosure 的实现、合成/注入数据自主探索、测试、
资源画像，以及在真正独立 Pre-EXECUTE PASS 后执行一次冻结的 paired 300-block
synthetic development gate。请先完整读取 AGENTS.md、WORKBUDDY_LIFECYCLE、P5
MAIN_THREAD_ACCEPTANCE、Phase 6 OpenSpec 与本包四件套；随后仅把 STATUS 中
documentation_authorized、implementation_authorized、synthetic_exploration_authorized、
decoder_execution_authorized、development_gate_authorized、rate_adaptation_authorized、
phase6_authorized 改为 true，其余权限保持 false。

冻结点保持 GF32/poly37/alpha2、N=256、erasure epsilon=0.05、物理 label=32*x_hat。
只实现 K=(29,33,37,41,45) 的 worst-first nested schedule；每层只发送新增的实际 GF32
坐标值且每个坐标只计一次。每个被调用层必须从头运行 SC，不得 warm-start 或跨层携带
belief/partial sum/hard decision。每层使用独立 64-bit Toeplitz tag；tag 匹配只接受当前
候选，tag 不匹配只允许丢弃当前候选并进入紧邻的下一冻结层，禁止在候选间选择、跳层、
排序或改变 decoder 参数。所有 tag、public seed 与 feedback control 调用均须计数。

先完成 nesting、任意零值、restart、tag tamper、no-candidate-selection、独立 transcript
recount、verification union bound、失败桶互斥和前驱回归。允许范围内自主修复，但不得调
K 集合、construction、channel point 或阈值。然后冻结全新未用 run/master seeds、精确
命令、唯一缺席输出根、预算与 stop rules，并取得独立 Pre-EXECUTE PASS。

唯一正式尝试必须让 paired static-K45 与 incremental 两臂使用完全相同的 300 个新合成
blocks；这是新 paired development run，不得读取、覆盖或伪装重跑 Phase 5 根。第一次
科学 sc_decode 调用即消耗 attempt 1/1，失败也禁止重跑、换 seed 或调参。incremental
候选硬门：undetected=0、exact>=285/300、one-sided 95% Wilson LB>=0.90、平均
key-dependent disclosure 至少比 paired static arm 低 5%，以及全部 coverage、资源、
invocation、union-bound、truth-isolation 和 recount 门通过。

禁止 Model-F artifact、parquet、TTBin、DEV/EVAL、真实数据、learned policy、frame-wise
调参、SCL/CRC、Phase 7、benchmark、key-rate/qualification/promotion、sibling/results/
outputs_comparison 写入、commit 或 push。必须由独立 reviewer 对实际 artifacts 做
Pre-RESULT 重算。最终只允许返回 FIXED_INCREMENTAL_DEVELOPMENT_CANDIDATE 或
BLOCKED(<single earliest gate>)，并报告 attempt/seed 消耗与未运行阶段。
```
