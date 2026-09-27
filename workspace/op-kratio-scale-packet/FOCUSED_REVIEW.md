# op-kratio-scale focused numerical review + main-thread adjudication — 2026-09-27

## Reviewer recomputation (independent, no re-execution)

Recounted from `records` (160 records); all five outcome keys agree with `points[*].{operational_totals,oracle_totals}`
and the top-level totals.

| total k | k1 | k2 | disclosed | f_actual | op exact | op verify_failed | op undetected | op decode_failed | op resource_abort | oracle exact |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 560 | 80 | 480 | 2800 | 2.934414 | **28** | 4 | 0 | 0 | 0 | 30 |
| 448 | 64 | 384 | 2240 | 2.347531 | 0 | 32 | 0 | 0 | 0 | 0 |
| 336 | 48 | 288 | 1680 | 1.760648 | 0 | 32 | 0 | 0 | 0 | 0 |
| 280 | 40 | 240 | 1400 | 1.467207 | 0 | 32 | 0 | 0 | 0 | 0 |
| 224 | 32 | 192 | 1120 | 1.173766 | 0 | 32 | 0 | 0 | 0 | 0 |

- Ratio check: `k2 = 6*k1` holds at all five points; `disclosed = 5*(k1+k2)` matches
  `K1_POINTS`; `f_actual` decreases monotonically with total k.
- Structure: 32 blocks per total (2 seeds × 16), `cells` 10/10, 160 records.
- Isolation: `undetected`, `decode_failed`, `resource_abort` are zero everywhere and never merged
  into success or FER; `a3_key_dependent_bits_observed` = the five disclosed values + 64.
- Budget: wall `115.022 s` ≤ 600 s; peak RSS `215396352 B` ≤ 1 GiB; `within_budget = true`;
  `stop_rules_triggered = []`; `probe_runs = 1`, `reruns = 0`.
- Wording: efficiency/operating-point language appears only inside explicit negations.

## Main-thread conclusion sentence (Tier-X descriptive, non-claim)

在 F4@q1024、固定配比 `k1:k2 = 1:6` 的条件下缩放总预算，operational exact 计数随总披露下降而
**单调塌陷**：2800 bits 处 28/32（FER 0.125），2240/1680/1400/1120 bits 四处均为 0/32（FER 1.0，
两 seed 一致）。即：在该配比下，观测到仍能维持非零 operational 成功的最低总披露为
**2800 bits（f_actual = 2.934414）**，它同时是本次网格的最高披露点。描述性 Tier-X、非 claim、
非效率点。

## Boundaries of the reading (mandatory)

1. This is a **same-ratio scaling observation**. The ratio `1:6` is a declared derived choice taken
   from the peak band of `op-k1k2-split-560`; it is **not** an independently preregistered ratio and
   is **not** claimed to be optimal at lower totals.
2. The result therefore does **not** establish that low `f` is unreachable in general: at a smaller
   total the optimal ratio may differ, and that combination has not been measured.
3. Synthetic F4@q1024 with `N=1024` only. Not a real-data result, not a FER estimate for any
   acquisition, not a statement about the frozen real-data budget, and not an efficiency claim.
   In particular it must not be read as a comment on the real-data target `f≈1.27`.
4. At totals ≤448 **both** arms are zero, so per the standing rule no single-cause (L-H) attribution
   is made for that collapse.
5. No operating point, no efficiency claim, no comparison against any binary baseline, no R2 sizing
   input, no promotion, and no automatic successor route.
