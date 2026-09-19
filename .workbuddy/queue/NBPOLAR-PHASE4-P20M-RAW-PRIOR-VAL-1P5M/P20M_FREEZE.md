# P20M Stage-A freeze (frozen 2026-09-19; Stage B NOT authorized)

Packet: `NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M` (`TASK_PACKET.md`).
State after Stage A: every `<FROZEN_AT_STAGE_A>` pin below is filled.
Stage-B execution needs, in order: Stage-A return, independent Pre-EXECUTE
PASS (adjudicating §3 derivation + §5 budget literal + §4 gate family +
§2 runner-delta design), the filled Stage-B authorization text, and
target-output absence. The Stage-B root
`.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/`
is ABSENT (verified at Stage-A close).

## 1. Corrected-prior artifact (§3, P20M-R1)

- Path: `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz`
  (25438650 B; created once by the Stage-A derivation; fail-if-present).
- Canonical digest (sorted-key `key + shape + dtype + C-order bytes` sha256):
  `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`
- Keys (exactly): `counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value,
  h1, h2, h_total` (`lambda_star` stored `0.0` = "no smoothing" marker;
  `floor_value` stored `1e-15`).
- Session H literals (recomputed via accepted `target_construction.entropy_bits`,
  X08 descriptive reference reproduced, never copied):
  H1 `0.02519949692375297` / H2 `0.8003665547495433` / TOTAL `0.8255660516732963`.
- `p_b` cross-check: stored `p_b` == `counts_ab` column totals / total within
  1e-12; counts total `424960` == manifest TRAIN pairs.
- Floor report: `1046140` floor-hit cells / `1048576` (`0.9976768493652344`;
  exactly the zero-count cells); `0` zero columns.
- Derivation input: ONLY the `counts_ab` array of the digest-reverified P20H
  worktree npz
  `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz`
  (canonical digest `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`;
  worktree-file read, never a protected counts open). Rule: raw-count MLE +
  1e-15 floor + column renormalize, zero columns fall back to `p_global`
  exactly, `p1`/`p2` via accepted `prior.derive_p1`/`derive_p2` under
  `A = 32*U1 + U2` `FULL_BOB_ONLY`; no lambda anywhere (the derivation
  function takes no lambda parameter).

## 2. Session-derived disclosure point (§5, P20M-R2/R3)

- Budget literal S2-(i), recomputed from the same-run session H (never carried):
  `1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020`
  via accepted `target_n_scaling.budget_k_total`. K_total `7020`.
- Split via accepted `empirical_genie_scaling.select_empirical_split` semantics
  on 16 synthetic TRAIN blocks model-sampled from the corrected prior under
  the frozen derivation seeds `2026092291, 2026092292, 2026092293, 2026092294`
  (4 streams x 4 blocks; 32 L1+L2 genie calls; never a real frame, never DEV;
  pooled means; worst-first `(e,h,index)` orders; exhaustive integer K1
  enumeration with `K2 = K_total - K1`; lexicographic minimum of
  `(TRAIN residual e sum, K1, K2)`): K1 `331`, K2 `6689`, TRAIN residual
  `3.0162993815141537e-07`.
- Preregistered per-arm caps (rule `5*(K1+K2)+64` key-dependent bits/block,
  `10*32768+63 = 327743` public bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| G0_old_point_base (operational control) | 319 | 6492 | 34119 = 5*6811+64 | 327743 |
| G1_raw_prior_session_budget (operational candidate) | 331 | 6689 | 35164 = 5*7020+64 | 327743 |
| G2_true_l1_diagnostic (oracle) | 0 | 6689 | 33509 = 5*6689+64 | 327743 |

- Planned totals: key-dependent `308376` = 3*34119 + 3*35164 + 3*33509 bits;
  public `2949687` = 9*327743 bits. G1 disclosure ratio vs raw input bits:
  `35164/327680 = 0.1073`; vs session CE budget `35164/(32768*0.8255660516732963)
  = 1.2999` (descriptive, NOT qualification efficiency).
- SC/tag/genie budget: Stage-A derivation 32 TRAIN genie calls (accounted here)
  + Stage-B pure DEV 15 SC (3 blocks x (2+2+1)) + 9 tags + 9 records with ZERO
  Stage-B sampling (Stage-B TRAIN genie calls pinned at 0).

## 3. Order file (§§5/9, P20M-R2/R4)

- Path: `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json`
  (438141 B; fail-if-present).
- File-bytes sha256: `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`
- Content: protocol `nbpolar-p20m-raw-prior-val-1p5m`, kind
  `raw-prior-orders-file`, n `32768`, k_total `7020`, k1 `331`, k2 `6689`,
  full L1+L2 worst-first permutations + derivation provenance (corrected-prior
  digest + program pin + derivation seeds + 16 blocks + budget literal +
  floor hits/rate + counts total + TRAIN residual).
- Stage-B read-only `--order-file` + `--order-digest` gated use, zero sampling.

## 4. Population, gates, tag domain, envelope (§§4/6/8, P20M-R2/R6)

- DEV: FIRST 384 VAL frames of `type2_1p5M_20260121_183806` in (frame_id,
  pair_idx) order: `1660..2043`; blocks `1660..1787 / 1788..1915 / 1916..2043`
  (3 x 128 frames at N=32768); unused remainder `2044..2212` (169 frames /
  43264 pairs, counted never decoded); build frames TRAIN `0..1659` (S2-ii
  disjointness declared with frame sets); gate family (a)->(g) frozen in the
  runner (cross-file source-tag+digest first, intra-file VAL-containment +
  VAL-exterior/HOLD second, P20H/P20I/P20J/P20K-TRAIN + remainder exclusions,
  corrected-prior-identity + order-freeze + budget-literal last).
- Tag domain (new P20M): master `2026092280`, prefix
  `nbpolar-p20m-raw-prior-val-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits).
- Envelope: external timeout 600 s + virtual/RSS caps 2 GiB + single thread.
  Stage-A derivation cost (reference only): 219.6 s in-process / 3:41 elapsed /
  571 MB RSS peak.
- Split-counted reads at Stage-A close: counts-calibration 0/0 + DEV 0/1 +
  HOLD 0/1; worktree-npz reads 1 (no-reopen guard consumed once); attempts 0/1.
  2M pristine by non-access (never opened/statted/listed); V25 counts NPZ
  never opened; no 1M-pool access in any form.

## 5. Exact commands

Stage-A derivation (executed EXACTLY once, 2026-09-19, exit 0):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m --derive
```

Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(sibling-checkout venv; this checkout has no local `.venv`; numpy/pytest/pandas
verified present there). No rerun (a rerun to fix an execution error is allowed
and would be recorded here; none was needed).

Stage-B execution command (FROZEN, byte-identical to the module
`FROZEN_COMMAND`; NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted
Stage-B authorization + target-output absence):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 1660 2043 --block-frames 128 --remainder-frames 2044 2212 --tag-master 2026092280 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m
```

with corrected-prior digest
`372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`,
order-file digest
`a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`,
derived `--k1/--k2` `331/6689`, session H literals
`0.02519949692375297 / 0.8003665547495433 / 0.8255660516732963`, and
budget-literal display
`1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020`.

## 6. Module + construction pins

- Runner: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/raw_prior_val_1p5m.py`
  (thin importer of accepted `l1_order_1p5m`, ONLY the §2 d1-d7 deltas;
  Stage-A pins filled in-module; `FROZEN_COMMAND` filled verbatim above).
- P16 construction digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  (accepted, carried over read-only).
- Split manifest: `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 +
  VAL 553/141568 + HOLD 554/141824.
