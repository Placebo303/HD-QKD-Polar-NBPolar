# op-peak-refine focused numerical review + main-thread adjudication — 2026-09-27

## Reviewer recomputation (independent, no re-execution)

| k1 | k2 | op exact | op verify_failed | op undetected | op decode_failed | op resource_abort | oracle exact |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 60 | 500 | 24 | 8 | 0 | 0 | 0 | 32 |
| 100 | 460 | 26 | 6 | 0 | 0 | 0 | 26 |
| 120 | 440 | 20 | 12 | 0 | 0 | 0 | 20 |

- Totals: operational `{exact 70, verify_failed 26}`; oracle `{exact 78, verify_failed 18}`.
- Structure: 32 blocks per point (2 seeds × 16), `cells` 6/6, 96 records; every point's
  `summaries.a3_op_fer.n = 2`, so aggregation is clean (`k1` is unique in this grid).
- Constant-disclosure check: all three points have `k1+k2 = 560`, `bits_a3_disclosed = 2800`, and a
  single observed key-dependent value `2864` = 2800 + 64.
- Isolation: `undetected`, `decode_failed`, `resource_abort` zero everywhere and never merged into
  success or FER.
- Budget: wall `84.256 s` ≤ 600 s; peak RSS `215613440 B` ≤ 1 GiB; `within_budget = true`;
  `stop_rules_triggered = []`; `probe_runs = 1`, `reruns = 0`.
- Wording: efficiency/operating-point language appears only inside explicit negations.

## Combined peak-band curve (fixed total 560, 2800 bits, identical f)

Joining this refinement with the measured points of `op-k1k2-split-560` (same seeds, same shared
design vectors, same total):

| k1 | 10 | 40 | **60** | **80** | **100** | **120** | 160 | ≥240 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| operational exact /32 | 0 | 14 | 24 | **28** | 26 | 20 | 1 | 0 |
| oracle exact /32 | 32 | 32 | 32 | 30 | 26 | 20 | 1 | 0 |

**Main-thread conclusion sentence (Tier-X descriptive, non-claim):**
在 F4@q1024、总披露恒为 2800 bits 的条件下，operational exact 随 k1 呈**平滑单峰**：
峰顶位于 **k1≈80–100（28/32 与 26/32）**，峰宽约覆盖 **k1∈[60,120]**（24/26/20），
两侧快速退化（k1=40→14、k1=160→1、k1≥240→0）。描述性 Tier-X、非 claim、非效率点。

## What this adds beyond the coarse probe

1. The peak is a **plateau**, not a spike: three measured points inside [60,120] all lie between
   20/32 and 28/32, so the coarse single-point reading (28/32 at k1=80) is now bracketed rather than
   standing alone.
2. The oracle arm degrades earlier than suspected (30 at k1=80, 26 at k1=100, 20 at k1=120), so the
   k1 increase trades layer-2 conditioning against layer-1 conditioning — consistent with a fixed
   total budget.
3. It does **not** change the boundary conclusion of the total-scale and low-total probes: the peak
   exists at 2800 bits, and lower totals collapse even when the ratio is freed.

## Boundaries (mandatory)

1. Bookkeeping-only allocation diagnostic; no efficiency claim, no operating point, no FER estimate,
   no R2 sizing input, no promotion.
2. Synthetic F4@q1024 with `N=1024` only — not a real-data result and not a basis for changing the
   frozen real-data counts K1=319/K2=6492.
3. 3 points × 2 seeds × 16 blocks: bounded, no threshold, no significance wording.
4. No single-cause (L-H) attribution for the high-k1 collapse, where both arms degrade together.
