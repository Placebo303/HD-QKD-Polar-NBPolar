# Copy-paste authorization command — P2-R1

```text
我明确批准 P2 attempt 1/1 以 BLOCKED(P2_DIAG_INDEX_ERROR) 保留，并授权执行仓库
D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的新恢复任务包：
.workbuddy/queue/NBPOLAR-PHASE4-P2-R1-DIAGNOSTIC-INDEX-RECOVERY/TASK_PACKET.md

请先完整阅读 AGENTS.md、docs/nbpolar/WORKBUDDY_LIFECYCLE.md、原P2的
MAIN_THREAD_ADJUDICATION.md、P2_SYNTHETIC_IMPLEMENTATION.md、STATUS.yaml，以及本R1
目录的 TASK_PACKET.md、PROMPT.md、STATUS.yaml。随后仅将R1 STATUS.yaml更新为：

state: AUTHORIZED_FOR_AUTONOMOUS_P2_R1_INDEX_RECOVERY
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
phase4_p2_r1_authorized: true
phase4_p3_authorized: false
scientific_promotion: false
next_gate: FIX_AND_ASYMMETRIC_TESTS_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW

本次只授权修复诊断中 [U1,B,U2] 的Bob轴索引：将错误语义
f3[u1,:,nz_b] 修为 f3[u1,nz_b,:]，先用非对称shape和独立三重循环oracle证明。
必须通过新增测试、全部79个前代测试和真实独立Pre-EXECUTE review后，才允许对同一
sibling accepted artifact进行一次新的content-read attempt，并只能写原先缺席的
cal_prior_validation/cal_prior_summary.json和cal_prior_report.md。attempt在首次打开
NPZ/JSON内容时即消耗，无论成功失败；禁止rerun、替换root或修改旧BLOCKED记录。

禁止读取parquet/TTBin、重建CAL、修改lambda/floor、运行Model-F或SC decoder、
construction、DEV/EVAL、benchmark、reconciliation，禁止写sibling/results/
outputs_comparison，禁止commit/push，禁止启动P3或作性能宣称。

可在以上范围自主修复、测试和调用独立reviewer。最终只返回
P2_R1_CAL_PRIOR_VALIDATION_CANDIDATE或BLOCKED(<single earliest gate>)，并报告R1
content attempt count。这条消息不授权P3、decoder或其他数据执行。
```
