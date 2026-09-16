# Authorization

```text
我授权执行 NBPOLAR-X01-PROBE-TIER-BOOTSTRAP：先按 OpenSpec
nbpolar-probe-tier-and-decision-gate-slimming 在 AGENTS.md 与 docs/nbpolar 中正式加入
Tier X 探索档、Tier Y 判定档、阈值前方差证据和 Δ-后继快路径；再执行 TASK_PACKET.md
冻结的 X01 四组五种子合成探针。

只开放 workflow_change_authorized、documentation_authorized、synthetic_probe_authorized
和 decoder_probe_authorized。探针固定 N=256；P5 seeds 2026091400..1404，R1 seeds
2026091410..1414，P4 independent seeds 2026091420..1424，dependent-L2 seeds
2026091430..1434；public master=run_seed+10000。dependent 模型固定
epsilon2(u1)=0.08+0.24*u1/31，并须在解码前证明 P2 跨 u1 最大差至少 0.10。

探针只写 workspace/probes/nbpolar_x01_20260913/prereg.md 与 results.json；允许记录执行
错误后的重跑，但不得在 prereg 后改参数、模型或 seed。结果只报告逐 seed 与 mean/std/range，
用于设计下一判定门；不得产生 candidate/accepted、pass/fail、attempt 消耗或反向升级旧证据。

禁止 artifact/真实数据、旧证据根写入、qualification/promotion、decision-log/index/memory
逐探针更新、commit/push。完成一次 focused numerical review 后返回探索摘要与下一 Tier-Y
建议，不做科学验收。
```
