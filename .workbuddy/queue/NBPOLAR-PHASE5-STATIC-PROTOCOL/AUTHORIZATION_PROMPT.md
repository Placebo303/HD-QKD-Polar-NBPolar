# Copy-paste authorization — Phase 5 static protocol

```text
我明确接受 Phase 4-P3 的主线程验收范围，并授权执行仓库
D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的任务包：
.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/TASK_PACKET.md

本授权仅开放 Phase 5 静态、合成数据 reconciliation protocol 的实现、范围内自主
探索、测试、资源画像，以及在独立 Pre-EXECUTE PASS 后执行一次冻结的 300-block
synthetic development gate。请先读取 AGENTS.md、WORKBUDDY_LIFECYCLE、P3
MAIN_THREAD_ACCEPTANCE、Phase 5 OpenSpec 与本包四件套，再把 STATUS 中仅以下权限改为 true：
documentation_authorized、implementation_authorized、synthetic_exploration_authorized、
decoder_execution_authorized、development_gate_authorized、phase5_authorized。

实现一条最小静态协议：GF32/poly37/alpha2、N=256、erasure epsilon=0.05、K=45；
公开冻结坐标的实际 GF32 值（含零），SC 只运行一次，完整重编码回物理 1024-ary
labels，最后只调用一次 64-bit Toeplitz tag。tag 不能选择、重试或改变 decoder 路径。
key-dependent disclosure 与 public seed/control 必须分开，并由独立事件重算；exact、
verified、undetected、decode-failed、verify-failed、resource-abort 必须互斥记账。

先完成 tiny exhaustive、任意零值、错误 tag、truth-isolation、transcript recount、
IRRunResult 薄适配与全前驱回归；允许在合成/注入数据上自主修复范围内问题。随后冻结一个
新的、未使用的 run seed 与每块独立 Toeplitz seed 派生规则、精确命令、唯一缺席输出根、
预算和 stop rules，并取得真正独立 Pre-EXECUTE PASS。只允许一次 300-block run；首次
科学 decoder 调用即消耗 attempt，失败也不得重跑或调参。

开发门仅允许报告：one-sided 95% Wilson exact-recovery lower bound 是否 >=0.90、
undetected 是否为 0、平均 key-dependent disclosure 是否 <10*N，以及所有记账/资源门。
这不是实数据 FER、泄漏效率、密钥率、qualification 或 promotion。

禁止读取 Model-F artifact、parquet、TTBin、DEV/EVAL 或真实 frame；禁止自适应 disclosure、
retry、SCL/CRC、rate scan、benchmark comparison、Phase 6、sibling/results/
outputs_comparison 写入、commit 或 push。Pre-RESULT 必须由独立 reviewer 对实际 artifacts
重算后才能返回。最终只允许 STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE 或
BLOCKED(<single earliest gate>)，并报告 attempt/seed 消耗及未运行阶段。
```
