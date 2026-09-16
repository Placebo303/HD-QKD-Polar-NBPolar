# Copy-paste authorization — Phase 6-R2

```text
我授权执行仓库 D:\Code\HD-QKD_Polar_Comparison-nbpolar 中的任务包：
.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/TASK_PACKET.md

本授权只开放 documentation_authorized、implementation_authorized 和
decoder_free_analysis_authorized。任务必须冻结并使用有 provenance 的 full-precision
L1/L2 entropy，完成 q=32 BEC surrogate 的 N=2^8..2^18 两层 rate-feasibility
敏感性分析，显式计算 5*(K1+K2)+64、n*(H1+H2) 与 f，并以 f<=1.3 为目标门。

必须先由独立 literal oracle 验证递推与最小 K 选择，并复现 N=256、epsilon=0.05、
whole-block FER union-bound target=1e-2 时 K=43。必须比较至少 equal 与
entropy-proportional 的两层 FER budget 分配，并覆盖所有已接受 empirical sources。
必须审计 oracle-L2(true L1) 与 operational L2(candidate L1) 是否实际进入过 SC，
将缺口写成后继前置条件。

BEC 表只能称为 surrogate planning estimate；不得称为真实邻位偏移信道性能、严格
乐观下界或 decoder 证据。禁止 SC/decoder 执行、artifact/parquet/TTBin、合成 block
采样、attempt/seed 消耗、修改旧证据根、FWHT/scalable decoder、SCL/Phase 7、真实数据、
qualification/promotion、commit/push。任一输入 provenance、K43 calibration、独立实现
一致性、finite 或完整性门失败即 STOP，不得看结果后改公式或 FER 分配。

完成 focused tests、独立 reviewer-go 结果复算和 memory triage 后，只返回
TWO_LAYER_RATE_FEASIBILITY_CANDIDATE 或 BLOCKED(<single earliest gate>)，验收归主线程。
```
