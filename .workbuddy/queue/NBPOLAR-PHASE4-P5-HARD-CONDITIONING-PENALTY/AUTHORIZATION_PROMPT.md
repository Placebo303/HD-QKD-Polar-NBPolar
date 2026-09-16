# Authorization

```text
我授权执行 .workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/TASK_PACKET.md。

只开放 documentation、implementation、decoder_execution 和 development_gate。
冻结点为 GF32/N256、epsilon1=0.05、strong dependent-L2
epsilon2(u1)=0.02+0.36*u1/31、K1=45、K2=140；使用全新 streams
2026091470..2026091472，每 stream 128 paired blocks，public master=seed+10000，
合计 384 pairs，单一 attempt 1/1。输出根、五文件、2 GiB/3600 s 及 TASK_PACKET 中
精确 WSL 命令不得更改，并须由 Pre-EXECUTE 逐项核对；首次 gate L1 SC call 即消耗 attempt。

必须记录 both-exact/oracle-only/operational-only/neither-exact 四格。不得对两个边际率之差
直接使用 Clopper-Pearson。仅在 oracle exact>=365/384、operational-only=0，且 oracle-only
事件比例的一侧 95% exact lower bound（按 TASK_PACKET 的二项尾概率方程独立求根）>0.30
时返回 HARD_L1_CONDITIONING_PENALTY_CANDIDATE；完整性门通过但判别条件未通过则返回
HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED；完整性失败才返回 BLOCKED。

必须独立 Pre-EXECUTE 与 Pre-RESULT。禁止重跑、换 seed、调模型/K/阈值，禁止 artifact、
真实数据、经验 construction、N>256、FWHT/SCL、APP/soft 实现、效率/真实 FER/qualification/
promotion、旧根修改、commit/push。验收与路线处置归主线程。
```
