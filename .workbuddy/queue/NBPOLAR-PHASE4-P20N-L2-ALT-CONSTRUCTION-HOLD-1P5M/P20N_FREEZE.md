# P20N Stage-A freeze (frozen 2026-09-19; Stage B NOT authorized)

Packet: `NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M`
(`TASK_PACKET.md`). State after Stage A: every `<FROZEN_AT_STAGE_A>` pin
below is filled. Stage-B execution needs, in order: Stage-A return, an
independent Pre-EXECUTE PASS (adjudicating the §3 derivation, the D2
feasibility outcome, the §5 K-literal, the §4 gate family, the §2
runner-delta design and the §7 instrumentation boundary), the filled
Stage-B authorization text, and target-output absence. The Stage-B output
root
`.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`
is ABSENT (verified at Stage-A close).

## 1. Alt-L2-table artifact (§3, P20N-R1)

- Path: `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz`
  (25430240 B; created once by the Stage-A derivation; fail-if-present).
- **File-bytes sha256 (the `--alt-digest` pin)**:
  `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`
  (independently confirmed with `sha256sum`).
- Keys (exactly 9): `counts_ab, f_alt, p1, p2_alt, alpha, floor_value,
  h1_inc, h2_alt, h_total_alt` (`alpha` stored `1.0`; `floor_value`
  stored `1e-15`; all arrays float64).
- Construction rule (frozen): `n_b[b] = counts_ab.sum(axis=0)`;
  `f_pre[a,b] = (counts_ab[a,b] + 1) / (n_b[b] + 1024)` (α=1 unit
  pseudocount, frozen; 1024 = Alice-alphabet size); `f_alt =
  max(f_pre, 1e-15)` then column renormalize (floor step RETAINED
  formally); zero columns fall back to `p_global` exactly;
  `p2_alt = derive_p2(f_alt)` under `A = 32*U1 + U2` FULL_BOB_ONLY;
  `p1` = the CARRIED incumbent P20M `p1` (L1 fixed, never re-derived);
  `h1_inc` = the carried incumbent H1 literal; `h2_alt`/`h_total_alt`
  recomputed descriptively via accepted `target_construction.entropy_bits`
  on `(p1_inc, p2_alt)` — DESCRIPTIVE ONLY, never a budget input.
- Derivation input: ONLY the `counts_ab` array of the digest-reverified
  P20M worktree npz
  `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz`
  (canonical digest `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`;
  worktree-file read, never a protected counts open; single content open,
  no-reopen guard consumed once). File-bytes sha256 of that npz (reference
  only): `6b8ae9b81782312d53081a6742cc31ac53ef30e4e92b0b07c9eba7f9787a3481`.
- Literals frozen at Stage A:

| literal | value |
|---|---|
| counts total | `424960` (== manifest TRAIN pairs) |
| floor hits (cells < 1e-15) | `0` / 1048576, rate `0.0` |
| zero columns | `0` |
| `f_alt` min / max | `0.000665335994677302` / `0.24762550881953543` |
| column renormalization dev | `6.894484982922222e-14` |
| `p1` equality max-abs-diff (stored vs incumbent) | `0.0` |
| descriptive α1-derived-marginal vs incumbent `p1` | `0.7353595255735041` (evidence that L1 is CARRIED, not re-derived) |
| `h1_inc` | `0.02519949692375297` (carried P20M H1) |
| `h2_alt` | `1.4447543021770293` |
| `h_total_alt` | `1.4699537991007823` (descriptive only) |

## 2. D1 feasibility literals + D2 gate outcome (§3, P20N-R9)

- Estimator (frozen literal):
  `ce_insample_bits_per_symbol = (1/total) * sum_{a,b} counts_ab[a,b] *
  (-log2 p2[u1(a), b, u2(a)])`, `u1(a)=(a>>5)&31`, `u2(a)=a&31`, on the
  SAME TRAIN counts the tables were built from (zero protected reads).
- D1 literals:

| literal | value |
|---|---|
| `ce_alt_insample_bits_per_symbol` | `0.9027311772313849` |
| `ce_incumbent_insample_bits_per_symbol` | `0.8003665547439149` (matches the carried H2 literal `0.8003665547495433` within 5.63e-12) |
| `alt_feasibility_ceiling_bits` | `33509 = 5*6689+64` |
| operational ceiling (reference) | `35164 = 5*7020+64` |
| `alt_ideal_length_bits = ce_alt * 32768` | `29580.69521551802` |

- **D2 `alt_construction_budget_feasibility` = FEASIBLE**:
  `29580.69521551802 <= 33509` (margin `3928.304784481981` bits). Evaluated
  at Stage A BEFORE any Stage-B root creation and before any HOLD contact;
  HOLD read stays 0/1; the packet proceeds to independent Pre-EXECUTE.

## 3. Carried disclosure point and orders (§5, P20N-R2/R3/R4)

- `(K1,K2) = (331,6689)`, `K_total = 7020`: CARRIED P20M literals
  (replayed, never recomputed; the alt-H literals never enter any budget).
- Budget-literal display (carried P20M line):
  `1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020`.
- Preregistered per-arm caps (rule `5*(K1+K2)+64` key-dependent bits/block,
  `10*32768+63 = 327743` public bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_incumbent_L2_operational | 331 | 6689 | 35164 = 5*7020+64 | 327743 |
| B_alt_L2_operational | 331 | 6689 | 35164 (Δ vs A exactly 0) | 327743 |
| C_incumbent_L2_oracle | 0 | 6689 | 33509 = 5*6689+64 | 327743 |
| D_alt_L2_oracle | 0 | 6689 | 33509 (Δ vs C exactly 0) | 327743 |

- Planned totals: key-dependent `549384` = 8*35164 + 8*33509 bits;
  public `5243888` = 16*327743 bits.
- Order file (shared read-only on ALL four arms):
  `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json`
  (438141 B), file-bytes sha256
  `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`
  (independently confirmed); disclosed L1 set = first-331, L2 set =
  first-6689 of the same frozen order file on every arm; zero Stage-B
  sampling.

## 4. Population, gates, tag domain, envelope (§§4/6/8, P20N-R2/R6)

- DEV: FIRST 512 HOLD frames of `type2_1.5M_20260121_183806` in
  (frame_id, pair_idx) order: `2213..2724`; blocks
  `2213..2340 / 2341..2468 / 2469..2596 / 2597..2724` (4 × 128 frames at
  N=32768; 131072 pairs); unused remainder `2725..2766` (42 frames /
  10752 pairs, counted never decoded); build frames TRAIN `0..1659`
  (S2-ii disjointness declared with frame sets). Consumed-TRAIN
  `0..1659`, consumed VAL DEV `1660..2043` and VAL remainder `2044..2212`
  are excluded by the frozen gate family (a)→(g) (cross-file
  source-tag+digest first, then intra-file HOLD-containment, then
  consumed-TRAIN / consumed-VAL-DEV / VAL-remainder exclusions incl. the
  S2-ii declaration, then alt-identity + order-freeze + K-literal).
- Tag domain (new P20N): master `2026092300`, prefix
  `nbpolar-p20n-l2-alt-hold-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
  MSB-first, truncated to `10*N+63 = 327743` bits).
- Hazard instrumentation: X09-R1 Req1+Req2 eight scalars
  (`l2_order_digest`, `l2_prefix_len` = 6689 gated, `l2_fail_in_prefix`,
  `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits`,
  `l2_prefix_hazard_mean_bits`, `l2_fail_nbhd_floor_frac`,
  `l2_prefix_floor_frac`), frozen radius R=8 window, post-decode
  recording-only boundary.
- Envelope: external timeout 900 s + virtual/RSS caps 2 GiB + single
  thread; 24 SC / 16 tags / 16 records; Stage-B TRAIN genie calls pinned
  at 0.

## 5. Exact commands

Stage-A derivation (executed EXACTLY once, 2026-09-19, exit 0, in-process
wall 0.572503 s; no rerun needed):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --derive --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alpha 1 --floor 1e-15 --out .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz
```

Stage-B execution command (FROZEN, byte-identical to the module
`FROZEN_COMMAND`, verified equal to the `<FROZEN_AT_STAGE_A>`-filled
AUTHORIZATION_PROMPT STEP-2 block; NOT AUTHORIZED until independent
Pre-EXECUTE PASS + pasted Stage-B authorization + target-output absence):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 900 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest 6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78 --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 2213 2724 --block-frames 128 --remainder-frames 2725 2766 --tag-master 2026092300 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m
```

Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(sibling-checkout venv; numpy/pytest/pandas verified present there).

Main-thread correction (2026-09-19, doc-only, after the independent
Pre-EXECUTE review): the two `cd` lines in §5 were corrected from
`/mnt/Code/...` to `/mnt/d/Code/...` (the module `FROZEN_COMMAND` and the
AUTHORIZATION_PROMPT STEP-2 block were already correct). All argv content is
unchanged; no re-derivation or re-execution.

## 6. Module + construction pins

- Runner: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py`
  (thin importer of accepted `raw_prior_val_1p5m`, ONLY the §2 d1–d7
  deltas; Stage-A pins filled in-module; 2866 lines, sha256
  `d101831bc54f65096bfbb505afebdbe37b965540d52b572cd29b7d5a50bf9082`).
- Focused tests: `comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py`
  (16 tests; 740 lines, sha256
  `ecb4b323e224b5b3c686201f223f567dce90acbaa10cbca33278c71d159676dd`).
- P16 construction digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  (accepted, carried over read-only).
- Split manifest: `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960
  + VAL 553/141568 + HOLD 554/141824.
- Accepted modules untouched (sha256 evidence in
  `P20N_IMPLEMENTATION_NOTES.md`).

## 7. Read audit at Stage-A close

| counter | value |
|---|---|
| V25 counts-calibration opens | 0 (budget 0/0) |
| HOLD parquet content opens/stats | 0 (budget 0/1) |
| VAL-remainder reads | 0 |
| reserved 2M open/stat/listing/read | 0 (pristine by non-access) |
| worktree P20M-npz reads | 1 (the single authorized Stage-A derivation) |
| real-data decoder execution | 0 |
| Stage-B output root | ABSENT |
| attempts used | 0/1 |

## 8. Stage-A test status

- `comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py`:
  **16 passed** (30.34 s; `-p no:cacheprovider`; fresh
  `workspace/p20n/<uuid>/` temp roots), both before and after the
  Stage-A pin fill.
- Predecessor suite `test_nbpolar_raw_prior_val_1p5m.py`: 16 passed,
  3 failed — all three are PRE-EXISTING Stage-A-era assertions broken by
  P20M's own accepted Stage-B execution (its evidence root exists since
  2026-09-19 10:53) and a P20M memory-doc edit (11:01), both before this
  session; no accepted file was touched by this Stage-A work. See
  `P20N_IMPLEMENTATION_NOTES.md` §5.
