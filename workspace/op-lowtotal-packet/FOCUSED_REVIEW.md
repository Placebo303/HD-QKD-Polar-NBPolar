# op-lowtotal-ratio focused numerical review + main-thread adjudication — 2026-09-27

## Reviewer recomputation (independent, no re-execution)

Recounted from `records` (256 records) keyed by `f_label` (necessary because `k1=96` occurs at both
totals); all five outcome keys agree with `points[*].{operational_totals,oracle_totals}` and the
top-level totals.

| total | k1 | k2 | disclosed | op exact | op verify_failed | oracle exact |
|---:|---:|---:|---:|---:|---:|---:|
| 448 | 32 | 416 | 2240 | **1** | 31 | 5 |
| 448 | 64 | 384 | 2240 | 0 | 32 | 0 |
| 448 | 96 | 352 | 2240 | 0 | 32 | 0 |
| 448 | 128 | 320 | 2240 | 0 | 32 | 0 |
| 336 | 24 | 312 | 1680 | 0 | 32 | 0 |
| 336 | 48 | 288 | 1680 | 0 | 32 | 0 |
| 336 | 72 | 264 | 1680 | 0 | 32 | 0 |
| 336 | 96 | 240 | 1680 | 0 | 32 | 0 |

- The single operational exact is seed `2026092701`, block `0`, at `T448_k1_32_k2_416`
  (per-seed FER 0.9375 / 1.0000).
- Structure: 32 blocks per point, 2 seeds each, `cells` 16/16, 256 records; every point's
  `summaries.a3_op_fer.n = 2`, so the aggregation-key defect flagged at review is confirmed fixed.
- Arithmetic: `k1+k2` = 448 (four points) and 336 (four points); disclosed 2240 / 1680;
  `f_actual` 2.3475311831887598 and 1.76064838739157.
- Isolation: `undetected`, `decode_failed`, `resource_abort` zero everywhere and never merged into
  success or FER; `a3_key_dependent_bits_observed = [1744, 2304]`.
- Budget: wall `158.75 s` ≤ 600 s; peak RSS `215760896 B` ≤ 1 GiB; `within_budget = true`;
  `stop_rules_triggered = []`; `probe_runs = 1`, `reruns = 0`.
- Wording: efficiency/operating-point language appears only inside explicit negations.

## Main-thread conclusion sentence (Tier-X descriptive, non-claim)

在 F4@q1024 的有界低总量配比网格（总 448 与 336，各四个 k1 配比，共 8 点、256 块）内，
operational 恢复**基本缺席**：仅 `T448_k1_32_k2_416` 观测到 **1/32** exact（oracle 5/32），
其余七点为 0/32；总 336（1680 bits，f≈1.76）四点全为零。描述性 Tier-X、非 claim、非效率点。

## Two observations worth carrying forward (both descriptive, both bounded)

1. **最优配比随总量移动**：总 560 的峰值在 `k1:k2 ≈ 1:6`，而总 448 下唯一出现非零的点是
   `k1:k2 ≈ 1:13`。因此不能把某一总量下测得的"最优配比"外推到其它总量——这也正是
   `op-kratio-scale`（固定 1:6 缩放）在 448/336 处全零的一个自洽解释。
2. **本夜合成证据指示可用区间在 2800 bits（f≈2.93）附近**：低于该预算后（2240 bits 起）
   恢复率坍塌到 ≤1/32。这不构成"低 f 不可达"的一般结论（网格有界、两 seed、每点 32 块、
   未测其它构造/译码/信道），但它确实表明：**仅靠 K 分配层面的重分配，不足以把合成工作点
   推向 f≈1.27 量级**；要接近该目标更需要的是算法/构造/译码层面的改变，而非预算挪动。

## Boundaries (mandatory)

1. Bounded 8-point grid, 2 seeds, 32 blocks per point — no threshold, no significance wording,
   no Wilson interval, no scoreboard row, no R2 sizing input.
2. Synthetic F4@q1024 with `N=1024` only. Not a real-data result and not a statement about the
   frozen real-data budget or the `f≈1.27` target; any transfer would be an unlicensed extrapolation.
3. At total 336 all counts are zero on **both** arms, so per the standing rule no single-cause
   (L-H) attribution is made.
4. No operating point, no efficiency claim, no comparison against any binary baseline, no
   promotion, and no automatic successor route.
