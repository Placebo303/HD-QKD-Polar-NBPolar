# AUTHORIZATION — NBPOLAR-EXPLORATION-STEP1-SCREENING (Tier-X, synthetic only; non-claim)

> 执行前 `STATUS.yaml.authorizations` 必须非空；未 recorded 前不做任何计算。

## Verbatim user instruction (2026-09-23)

> 我的意思是做完全套本项目的方向探索部分

## Main-thread binding (2026-09-23; the ONLY thing this authorization covers)

This authorizes **ONE Tier-X Step-1 small-q screening run** and nothing else:

- Synthetic only: the frozen F4 channel instance, frozen seeds, frozen operating points
  (F5/F6); arms exactly as frozen (F1/F2). **No real data, no `.ttbin`, no EVAL/RESERVE
  contact, no decoder on real data, no frozen-constant change.**
- Reuse is READ-ONLY: `comparison_bench/formal_ir/` may be imported, never modified.
- Output scope: `workspace/exploration/nbpolar-native-highdim/step1/` (at most `prereg.md`,
  `results.json`, `notes.md`) + this packet dir. Nothing else, anywhere.
- Correctness gates (oracle agreement, noiseless round-trip, low-rate smoke) are binding;
  any failure ⇒ STOP with zero outputs.
- Non-claim by construction: synthetic FER values are L2-ledger screening readouts —
  never cited as real-data FER; no efficiency/promotion/qualification/composable-key
  statement; the stop-loss is the qualitative bar of design §5; no numeric threshold is
  fixed or tuned.
- NOT authorized by this instruction: any real-data decode, any Step-2/Step-3 run (own
  packets), any Tier-Y gate, any Stage-3 re-entry, any frozen-contract change.

AUTHORIZED BY: user (verbatim above) via main thread, 2026-09-23. Recorded in `STATUS.yaml`.
