# Copy-paste authorization command — Phase 4-P1

Copy the text below as one user message into the execution session:

```text
我明确授权执行仓库 D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的任务包：
.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/TASK_PACKET.md

请先完整阅读 AGENTS.md、AGENT_PROJECT_MEMORY.md、
docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md、
openspec/changes/formal-ir-nbpolar-phase4-p0/，以及任务目录中的
TASK_PACKET.md、PROMPT.md、STATUS.yaml。随后仅将 STATUS.yaml 更新为：

state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P1_IMPLEMENTATION
documentation_authorized: true
implementation_authorized: true
cal_read_authorized: false
model_f_execution_authorized: false
real_data_authorized: false
decoder_execution_authorized: false
phase4_p1_authorized: true
scientific_promotion: false
next_gate: P1_IMPLEMENTATION_AND_INDEPENDENT_REVIEW

本次授权仅允许新增 formal_ir/nbpolar/prior.py、对应 __init__.py 最小导出、
test_nbpolar_prior.py、P1包内结果/评审文档，以及准备一个保持全false的Phase4-P2包。
允许自主实现、运行 synthetic V-P0-01至07、修复问题、跑Phase1-3回归并调用独立
reviewer。禁止读取CAL/TTBin/真实数据，禁止运行Model-F、SC decoder、benchmark、
DEV/EVAL，禁止选择数据驱动floor，禁止修改Phase1-3代码或冻结产物，禁止commit/push。

最终只返回 P1_IMPLEMENTATION_CANDIDATE 或 BLOCKED(<single earliest gate>)。
这条授权不构成Phase4-P2、CAL、decoder、真实数据或scientific promotion授权。
```
