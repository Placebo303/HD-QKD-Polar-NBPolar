# Copy-paste authorization command — Phase 4-P3

```text
我明确接受 P2-R1 仅限 CAL prior-table validation 的结果，并授权执行仓库
D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的新任务包：
.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/TASK_PACKET.md

请先完整阅读 AGENTS.md、docs/nbpolar/WORKBUDDY_LIFECYCLE.md、
docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md、P1与P2-R1的MAIN_THREAD_ACCEPTANCE.md，
以及本P3目录的TASK_PACKET.md、PROMPT.md、STATUS.yaml。随后仅将STATUS更新为：

state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P3_EMPIRICAL_PRIOR_SC
documentation_authorized: true
implementation_authorized: true
accepted_artifact_read_authorized: true
artifact_content_attempts_allowed: 1
synthetic_model_f_sampling_authorized: true
decoder_execution_authorized: true
autonomous_synthetic_exploration_authorized: true
resource_profiling_authorized: true
raw_data_authorized: false
real_data_authorized: false
dev_eval_authorized: false
reconciliation_authorized: false
phase4_p3_authorized: true
phase5_authorized: false
scientific_promotion: false
next_gate: STAGE_A_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW

本次授权允许新增 empirical_channel.py、独立 tiny oracle、对应测试、P3诊断入口和
包内文档。请把它作为heavy自主研究包执行，不要在第一个working example后返回：先在
不读artifact的Stage A/A2中比较vectorized与literal likelihood、probability与log表示，
覆盖exact-zero/one-hot/极端dynamic range、GF4/GF32 metamorphic检查、失败分类，并对
N={2,4,8,16,64,256,1024}在资源允许时做metric/SC分离profiling。允许自主修复范围内的
实现、测试和文档问题，记录探索过的方案、否决理由和证据；只有冻结合同冲突、accepted
predecessor缺陷、attempt耗尽或资源门才BLOCKED。

完成全部synthetic工作与回归后，冻结新seed/mask/命令/目标并取得真实独立
Pre-EXECUTE PASS；之后只允许一次读取同一accepted Model-F artifact。读入后在内存中
完成GF32 N=2/4至少64块oracle、N=16/64多种预注册disclosure shape、N=256的20到64块
bounded sanity、N=64/256/1024资源画像及逐失败attribution matrix；总预算3600秒、单case
120秒soft stop、RSS<2GiB。只写任务包规定的5个compact文件，最后做独立Pre-RESULT review。

禁止读取parquet/TTBin或held-out真实frame，禁止DEV/EVAL、L2 candidate链、调construction/
K/disclosure/rate、SCL/CRC、protocol/reconciliation/benchmark，禁止写sibling/results/
outputs_comparison，禁止commit/push，禁止Phase5与性能宣称。Alice真值只能用于生成、
冻结disclosure与评分，不能进入metric builder或SC likelihood。

可以在上述范围内自主实现、修复、测试并调用独立reviewer。最终只能返回
EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE或BLOCKED(<single earliest gate>)，并报告
artifact attempt与所有seed是否消耗。这条消息不授权真实数据FER、reconciliation或P5。
```
