# AUTHORIZATION — NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER (Tier-X, synthetic only; non-claim)

> 执行前 `STATUS.yaml.authorizations` 必须非空；未 recorded 前不做任何计算。

## Verbatim user instruction (2026-09-23)

> 我的意思是做完全套本项目的方向探索部分

## Main-thread binding (2026-09-23; the ONLY thing this authorization covers)

This authorizes **ONE Tier-X Step-2 transfer-prior probe** and nothing else:

- Synthetic only: the frozen Step-1 envelope (decoder, channel instance F4, operating
  points, seeds) reused; arms differ ONLY in the initial-message priors (F3 informed vs
  F4 uniform). **No real data, no `.ttbin`, no EVAL/RESERVE contact, no `prior_m2.py` or
  CAL change, no decoder change, no frozen-constant change.**
- The M2 ±1 values enter as a FIXED NUMERICAL REFERENCE copied verbatim from the frozen
  G1R2 CAL32 record (never recomputed, never re-fitted); the frozen floor rule (1e-15,
  no renormalization) is part of what is measured — recorded.
- Output scope: `workspace/exploration/nbpolar-native-highdim/step2/` (at most `prereg.md`,
  `results.json`, `notes.md`) + this packet dir. Nothing else, anywhere; the Step-0 /
  Step-1 / Step-3 roots are read-only reference.
- Correctness gates (G1a/G1b oracle with the respective priors, G2 round-trip, G3 smoke)
  are binding; any failure ⇒ STOP with zero outputs.
- Non-claim by construction: synthetic paired readouts are L2-ledger screening values —
  never cited as real-data FER; no efficiency/promotion/qualification/composable-key
  statement; zero/negative gain is kept as evidence, not discarded.
- NOT authorized: any real-data decode, any Step-1/Step-3 run (own packets), any Tier-Y
  gate, any Stage-3 re-entry.

AUTHORIZED BY: user (verbatim above) via main thread, 2026-09-23. Recorded in `STATUS.yaml`.
