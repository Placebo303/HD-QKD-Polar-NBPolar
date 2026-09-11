# Copy-paste authorization command — Phase 4-P0

Copy the text below as one user message into the execution session:

```text
我现在明确授权执行仓库 D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的任务包：
.workbuddy/queue/NBPOLAR-PHASE4-P0-PRIOR-CONTRACT-FREEZE/TASK_PACKET.md

请先完整阅读仓库根目录 AGENTS.md、AGENT_PROJECT_MEMORY.md，以及该任务包目录中的
TASK_PACKET.md、PROMPT.md、STATUS.yaml。然后把 STATUS.yaml 仅按本次授权更新为：

state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P0_FREEZE
documentation_authorized: true
implementation_authorized: false
cal_read_authorized: false
model_f_execution_authorized: false
real_data_authorized: false
decoder_execution_authorized: false
phase4_p1_authorized: false
scientific_promotion: false
next_gate: INDEPENDENT_PHASE4_P0_FREEZE_REVIEW

本次只授权 Phase 4-P0 的只读源码/文档审计、数学与接口冻结、OpenSpec 和文档编写，
以及准备一份仍未授权的 Phase 4-P1 TASK_PACKET + PROMPT。你可以在该范围内自主探索、
调用只读 subagent/reviewer、修订文档并完成独立 freeze review，不需要逐步向我确认。

不得修改或新增任何 .py；不得加载 CAL 私有数据或原始 TTBin；不得运行 Model-F、
NB-Polar decoder、真实数据、benchmark 或 EVAL；不得修改 Phase 1-3 代码和冻结产物；
不得启动 Phase 4-P1、reconciliation、SCL、rate adaptation；不得 commit/push。

必须按 TASK_PACKET.md 的完整验收矩阵工作。最终只能返回：
1. FREEZE_CANDIDATE：包含文件清单、精确 source citations、选定 API、备选比较、
   validation matrix、独立 reviewer verdict、memory triage 和未授权的 P1 包；或
2. BLOCKED(<single earliest defect>)：包含原始证据、已尝试的只读补救、未执行项和
   唯一需要主线程裁决的问题。

这条消息就是 Phase 4-P0 的显式授权，但不构成 Phase 4-P1 或任何数据/decoder执行授权。
```
