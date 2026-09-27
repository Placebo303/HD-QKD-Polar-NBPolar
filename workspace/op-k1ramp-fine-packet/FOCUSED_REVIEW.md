# op-k1ramp-fine-base focused numerical review + main-thread adjudication — 2026-09-27

## Reviewer recomputation (independent, no re-execution)

Recounted from `records`; all five outcome keys agree with `points[*].{operational_totals,oracle_totals}`
and the top-level totals.

| k1 | records | op exact | op verify_failed | op undetected | op decode_failed | op resource_abort | oracle exact |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 32 | 2 | 30 | 0 | 0 | 0 | 32 |
| 40 | 32 | 14 | 18 | 0 | 0 | 0 | 32 |
| 60 | 32 | 24 | 8 | 0 | 0 | 0 | 32 |

- Totals: operational `{exact 40, verify_failed 56}`; oracle `{exact 96}`;
  `oracle_candidate_divergence` `{defined 96, true 56}` is consistent with the 56 non-exact
  operational blocks.
- Structure: 96 records (32 per point), both seeds present at every point, `cells` 6/6.
- Arithmetic: `bits_a3_disclosed` = 2850/2950/3050 = `5*(k1+550)`; `f_actual_a3` reproduces
  disclosed / `H_times_N` (954.1939276637445) to the reported digits; the frozen `f_book`
  column is a rounded bookkeeping reference and is labelled as such.
- Isolation: `undetected`, `decode_failed`, `resource_abort` are zero everywhere and never
  merged into success or FER; `a3_key_dependent_bits_observed` = `[2914, 3014, 3114]` = disclosed + 64.
- Budget: wall `85.68 s` ≤ 600 s; peak RSS `216227840 B` ≤ 1 GiB; `within_budget = true`;
  `stop_rules_triggered = []`; `probe_runs = 1`, `reruns = 0`.
- Wording: efficiency/operating-point language appears only inside explicit negations.

## Combined descriptive dose–response (fine + coarse authoritative record)

Joining the coarse ramp (`op-k1ramp-k550-base`, authoritative; independently re-run once with
identical totals) with this fine interpolation, on the **same** `(x,y)` pairs, the same shared
`d2 = worst_k(H2,550)` and the same `k2 = 550`:

| k1 | 10 | 20 | 40 | 60 | 80 | 160 | 320 | 450 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| operational exact /32 | 0 | 2 | 14 | 24 | 30 | 32 | 32 | 32 |

**Main-thread conclusion sentence (Tier-X descriptive, non-claim):**
在 F4@q1024 / k2=550 / 共享 d2 下，operational exact 计数在 **k1∈(10,20] 区间首次脱离 0**，
随后随 k1 单调上升并在 k1=160 处达到 32/32（逐点计数 0/32、2/32、14/32、24/32、30/32、32/32、
32/32、32/32，分别对应 k1 = 10/20/40/60/80/160/320/450）；描述性 Tier-X、非 claim、非效率点。

## Boundaries of the reading

1. Synthetic F4@q1024 channel only. Not a real-data result, not a FER estimate for any
   acquisition, not an efficiency or operating-point result.
2. The whole `k1` axis is a **dose diagnostic**: the disclosure counts 2800–5000 bits are
   bookkeeping and are explicitly not efficiency points.
3. The oracle arm is 32/32 at every point including k1=10, so the observed operational
   failure at low dose is **not** explained by the layer-2 information set (which was the C1
   BASE set throughout) on these synthetic blocks.
4. No attribution beyond the dose axis: no L-H1/L-H2/L-H3 conclusion, no claim that any
   particular real-data K allocation is wrong, no comparison against any binary baseline.
5. No automatic continuation: whether a K-allocation question is pursued on real data is a
   separate main-thread decision requiring its own packet, freeze review, and authorization.
