# op-k1k2-split-560 focused numerical review + main-thread adjudication — 2026-09-27

## Reviewer recomputation (independent, no re-execution)

Recounted from `records` (256 records, 512 outcome entries); all five outcome keys agree with
`points[*].{operational_totals,oracle_totals}` and the top-level totals.

| k1 | k2 | op exact | op verify_failed | op undetected | op decode_failed | op resource_abort | oracle exact |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 550 | 0 | 32 | 0 | 0 | 0 | 32 |
| 40 | 520 | 14 | 18 | 0 | 0 | 0 | 32 |
| 80 | 480 | **28** | 4 | 0 | 0 | 0 | 30 |
| 160 | 400 | 1 | 31 | 0 | 0 | 0 | 1 |
| 240 | 320 | 0 | 32 | 0 | 0 | 0 | 0 |
| 320 | 240 | 0 | 32 | 0 | 0 | 0 | 0 |
| 400 | 160 | 0 | 32 | 0 | 0 | 0 | 0 |
| 480 | 80 | 0 | 32 | 0 | 0 | 0 | 0 |

- Totals: operational `{exact 43, verify_failed 213}`; oracle `{exact 95, verify_failed 161}`.
- Constant-disclosure check: every point has `k1+k2 = 560`, `bits_a3_disclosed = 2800`, and the
  **same** `f_actual = 2.93441397898595`. `a3_key_dependent_bits_observed = [2864]` is a single
  value (2800 + 64), which is the strongest in-artifact evidence that the budget really is constant.
- Structure: 32 blocks per split (2 seeds × 16), `cells` 16/16, 256 records.
- Isolation: `undetected`, `decode_failed`, `resource_abort` are zero at every point and never
  merged into success or FER.
- Budget: wall `159.39 s` ≤ 600 s; peak RSS `215060480 B` ≤ 1 GiB; `within_budget = true`;
  `stop_rules_triggered = []`; `probe_runs = 1`, `reruns = 0`.
- Wording: efficiency/operating-point language appears only inside explicit negations.

## Main-thread conclusion sentence (Tier-X descriptive, non-claim)

在 F4@q1024、**总披露恒定 2800 bits（f_book 恒定 2.9344）** 的前提下，operational exact 计数随
`k1/k2` 配比呈**单峰非单调**形态：k1=10/k2=550 → 0/32，k1=40/k2=520 → 14/32，
**k1=80/k2=480 → 28/32（本次观测最高）**，k1=160/k2=400 → 1/32，k1≥240 → 0/32；
两端均退化，最高值只出现在 k1≈80（k2≈480）的窄带。描述性 Tier-X、非 claim、非效率点。

## Boundaries of the reading (mandatory)

1. This is an **allocation effect at fixed budget**, not a dose-magnitude effect and not an
   efficiency improvement: every point spends the same bits, so the difference is attributable to
   the k1/k2 split rather than to a larger budget.
2. Synthetic F4@q1024 with `N=1024` only. **Not** a real-data result, not a FER estimate for any
   acquisition, not a recommendation for the frozen real-data counts K1=319/K2=6492. The synthetic
   optimum ratio is measured on a different `N`, channel, and construction; transferring it to real
   data would be an unlicensed extrapolation.
3. The oracle arm is 32/32 at k1=10/40, 30/32 at k1=80, and collapses to 0 from k1=240 onward; at
   k1≥240 **both** arms are zero, so per the standing rule that failure must not be attributed to a
   single labelled cause, no L-H attribution is made for the high-k1 collapse.
4. No operating point, no efficiency claim, no comparison against any binary baseline, no R2 sizing
   input, no promotion, and no automatic successor route.
5. Whether a K-allocation question is pursued on real data is a separate main-thread decision that
   requires its own packet, freeze review, and verbatim authorization; nothing here authorizes it.
