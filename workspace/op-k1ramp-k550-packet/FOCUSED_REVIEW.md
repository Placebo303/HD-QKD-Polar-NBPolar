# op-k1ramp-k550-base focused numerical review + main-thread adjudication — 2026-09-27

## Reviewer recomputation (independent, no re-execution)

Recounted from `records` and cross-checked against `points[*].{operational_totals,oracle_totals}`
and the top-level totals.

| k1 | records | op exact | op verify_failed | op undetected | op decode_failed | op resource_abort | oracle exact |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 32 | 0 | 32 | 0 | 0 | 0 | 32 |
| 80 | 32 | 30 | 2 | 0 | 0 | 0 | 32 |
| 160 | 32 | 32 | 0 | 0 | 0 | 0 | 32 |
| 320 | 32 | 32 | 0 | 0 | 0 | 0 | 32 |
| 450 | 32 | 32 | 0 | 0 | 0 | 0 | 32 |

- Totals agree: operational `{exact 126, undetected 0, verify_failed 34, decode_failed 0,
  resource_abort 0}`; oracle `{exact 160}`.
- Structure: 160 records total (32 per point), each point covers both seeds with 16 blocks,
  `cells = {expected: 10, completed: 10}`.
- Arithmetic: `bits_a3_disclosed = 5*(k1+550)` = 2800/3150/3550/4350/5000 matches all three
  locations; `f_actual_a3` reproduces disclosed / `H_times_N` (954.1939276637445) exactly.
  The frozen `f_book` column differs from `f_actual` by ≤1.3e-4 and only in the bookkeeping column.
- Isolation: `undetected = 0` everywhere and never merged into success or FER;
  `decode_failed = resource_abort = 0`; observed key-dependent bits `[2864, 3214, 3614, 4414, 5064]`
  equal disclosed + 64 for the five points.
- Budget: wall `118.757 s` ≤ 600 s; peak RSS `216719360 B` (≈0.202 GiB) ≤ 1 GiB;
  `within_budget = true`, `stop_rules_triggered = []`, `probe_runs = 1`, `reruns = 0`.
- Wording: no efficiency / operating-point / better-than-baseline / significance assertion;
  the k1 points are labelled bookkeeping-only dose diagnostics throughout.

Independent **cross-run reproduction**: a second separately-authored one-shot run of the
same frozen configuration (`workspace/probes/op-k1-ramp-k550/`, produced concurrently by the
overnight automation) returned identical totals `op {exact 126, verify_failed 34}` and
`oracle {exact 160}` with the identical `H`, `H_times_N`, `H1_mean`, `H2_mean`. See
`DUPLICATE_RUN_NOTE.md` for the provenance incident and how it is treated.

## Main-thread adjudication (descriptive only)

**Conclusion sentence (Tier-X descriptive, non-claim):**
在 F4@q1024 / k2=550 / 共享 d2 下，operational exact 计数在 **k1=80 处首次脱离 0**
（逐点计数 0/32 → 30/32 → 32/32 → 32/32 → 32/32，k1 = 10/80/160/320/450），
描述性 Tier-X、非 claim、非效率点。

Interpretation boundaries:

1. This is a **dose diagnostic on a synthetic channel**, not a FER estimate, not an
   efficiency result, not an operating point, and not a real-data result.
2. The k1=10 anchor reproduces the C1 observation (operational 0/32-class behaviour) while
   its oracle arm is 32/32 — i.e. at the frozen 10-position layer-1 dose the failure is
   **not** explained by the layer-2 information set, which was C1's BASE set throughout.
3. No cause attribution beyond the dose axis: labels or failure-model attribution (L-H1/L-H2/L-H3)
   are **not** asserted by this probe.
4. No automatic successor route, no candidate token, no promotion, no R2 sizing input follows.
   The decision whether the underlying K-allocation question is pursued on real data belongs
   entirely to the main thread and requires its own packet and authorization.
