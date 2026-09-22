# AUTHORIZATION — NBPOLAR-EXPLORATION-STEP0-SURVEY (Tier-X, non-claim)

> 本文件是执行门的 verbatim 授权记录。执行前 `STATUS.yaml.authorizations` 必须非空。
> 未 recorded 前：stage = PACKET_DRAFT，next_gate = DRAFT_CHECK，不做任何计算。

## Verbatim user instruction (2026-09-23, overnight delegation to the main thread)

> 顺着本本 exploration 往下推进，我要睡觉了，希望早上能直接看到你的完整准确诊断的 exploration

## Main-thread binding (2026-09-23; the ONLY thing this authorization covers)

This authorizes **ONE Tier-X Step-0 channel-survey probe** and nothing else:

- Inputs: the frozen, already-derived artifacts M1–M6 named in `TASK_PACKET.md` (read-only).
- Prohibited: any decode / SC call / tag generation; any raw-data or `.ttbin` read; any EVAL or
  RESERVE contact; any frozen-constant / contract / packet change; any write outside the
  probe root `workspace/exploration/nbpolar-native-highdim/step0/` + this packet dir.
- Non-claim by construction: no FER / efficiency / promotion / qualification / composable-key
  statement; L3 descriptive-survey ledger only; never cited as L1 real-data FER.
- Discipline: one-shot (runs=1, reruns=0; one corrective rebuild only after a zero-output
  crash, recorded); budget wall ≤ 300 s / RSS ≤ 2 GiB / single-threaded; stop rules binding;
  independent focused numerical review follows the run; main-thread adjudication before any
  durable record.
- NOT authorized by this instruction: any Step-1/Step-2/Step-3 run, any Stage-3 re-entry,
  any Tier-Y decision gate, any decoder/GF(32)/prior-CAL/freeze/new-data work — each needs
  its own packet + freeze review + verbatim authorization.

AUTHORIZED BY: user (verbatim above) via main thread, 2026-09-23. Recorded in `STATUS.yaml`.
