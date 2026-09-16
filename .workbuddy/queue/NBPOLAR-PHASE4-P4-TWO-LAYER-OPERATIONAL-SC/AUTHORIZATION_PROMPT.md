# Copy-paste authorization — Phase 4-P4

```text
我授权执行仓库 D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的新任务包：
.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/TASK_PACKET.md

本授权只开放 Phase 4-P4 的 documentation、implementation、synthetic_exploration、
decoder_execution 和 development_gate。目标是补齐最小两层因果闭环：Bob-only P1 →
L1 SC → source-domain hard L1 candidate → Bob+candidate 条件的 P2_hat → fresh L2 SC →
low_hat+32*high_hat → 单次最终 64-bit tag。另设严格隔离的 P2_true(true L1) oracle 臂，
只用于 paired 诊断与评分；不得把 Alice truth、oracle 值或 APP/soft belief 输入 operational 臂。

先用 injected synthetic joint tables 完成 N=2/4 exhaustive probability/decode oracle、轴/packing、
truth mutation、forced L1 error propagation、fresh-state、failure taxonomy、full-label/tag 与逐层
disclosure recount 测试，并通过全部 NB-Polar predecessor tests。禁止读取 Model-F artifact、
parquet、TTBin 或真实数据。

唯一 paired interface gate 已冻结为独立层擦除 injected joint table、GF32/N256、
epsilon1=0.05、epsilon2=0.20、analytic worst-first K1=45/K2=110、96 blocks、run seed
2026091360、public Toeplitz master 2026091361、2 GiB/3600 s；唯一输出根为
.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/
且运行前必须缺席，成功后只能有 frozen_plan.json、per_block_two_layer_outcomes.json、
transcript_accounting.json、aggregate_summary.json、report.md。精确 WSL 命令以 TASK_PACKET
为准，不得更改。任何 claim-bearing SC 前必须取得独立 reviewer-go Pre-EXECUTE PASS。
首次 gate SC call 消耗 attempt 1/1；禁止重跑、换 seed、调表、调 K 或调阈值。

硬门必须覆盖 96/96 paired coverage、所有可进入 L2 的块两臂均调用、operational truth
isolation、oracle/candidate provenance、tiny-oracle 容差、桶互斥穷尽、undetected=0、
nonfinite=0、resource_abort=0、逐层 disclosure/tag/control 独立重算、transcript mismatch=0，
以及运行前 injected wrong-L1 propagation 测试。exact 与 oracle/candidate divergence 仅报告，
不得设置或声称 f<=1.3、真实 FER 或性能门。
执行后必须由独立 reviewer-go 对实际 artifacts 做 Pre-RESULT 复算，之后才能返回。

禁止 N>256、经验 construction、FWHT/scalable decoder、SCL/Phase 7、真实数据、qualification、
promotion、旧证据根修改、commit/push。最终只允许返回
TWO_LAYER_OPERATIONAL_SC_CANDIDATE 或 BLOCKED(<single earliest gate>)，并报告 attempt/seed
消耗、测试、五文件清单与未运行阶段；验收归主线程。
```
