# Copy-paste authorization command — Phase 4-P2

```text
我明确授权执行仓库 D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的任务包：
.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/TASK_PACKET.md

请先完整阅读 AGENTS.md、AGENT_PROJECT_MEMORY.md、
docs/nbpolar/WORKBUDDY_LIFECYCLE.md、docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md、
Phase4-P1 的 MAIN_THREAD_ACCEPTANCE.md，以及本任务目录的 TASK_PACKET.md、
PROMPT.md、STATUS.yaml。随后仅将 STATUS.yaml 更新为：

state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P2_CAL_PRIOR_VALIDATION
documentation_authorized: true
implementation_authorized: true
cal_read_authorized: true
accepted_artifact_read_authorized: true
artifact_content_attempts_allowed: 1
model_f_execution_authorized: false
raw_data_authorized: false
real_data_authorized: false
decoder_execution_authorized: false
dev_eval_authorized: false
phase4_p2_authorized: true
phase4_p3_authorized: false
scientific_promotion: false
next_gate: P2_IMPLEMENT_SYNTHETIC_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW

本次授权允许实现只读 prior_artifact adapter 和合成测试；读取且仅读取 sibling
D:/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/
中的两个已接受文件；必须先完成 synthetic tests 和真实独立 Pre-EXECUTE PASS；之后
最多进行一次 artifact-content read，并只在本P2包目录新增 cal_prior_validation/
cal_prior_summary.json 与 cal_prior_report.md；最后完成独立 Pre-RESULT review。

禁止读取原始 parquet/TTBin，禁止重建CAL，禁止运行Model-F拟合、SC decoder、
construction、DEV/EVAL、benchmark、protocol或reconciliation；禁止选择lambda、floor、
K或rate；禁止写 sibling、results、outputs_comparison；禁止commit/push；禁止启动P3。

你可以在上述范围内自主实现、修复、测试和调用独立reviewer，无需逐步询问。最终只能
返回 P2_CAL_PRIOR_VALIDATION_CANDIDATE 或 BLOCKED(<single earliest gate>)，并报告
artifact content-read attempt count。这条消息不授权P3、decoder或任何性能宣称。
```
