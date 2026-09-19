# P20O Stage-A freeze (frozen 2026-09-19; Stage B NOT authorized)

Packet: `NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION`
(`TASK_PACKET.md`). State after Stage A: every `<FROZEN_AT_STAGE_A>` pin
below is filled. Stage-B execution needs, in order: Stage-A return, an
independent Pre-EXECUTE PASS (adjudicating the §3 prior/alt derivation, the
D2 feasibility outcome, the §5 budget/K-literal, the §4 gate family, the §2
runner-delta design and the §7 instrumentation boundary incl. the U-domain
scalar), the filled Stage-B authorization text, and target-output absence.
The Stage-B output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/`
is ABSENT (verified at Stage-A close).

Operator: backup `coder-fast` instance (primary was platform-aborted before
any write). No commit/push. Operator never self-accepts.

## 1. Counts input identity (the SINGLE protected open; R1)

- Canonical file (the only file opened):
  `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
  — the accepted canonical data root already pinned by
  `holdout_microcheck.FROZEN_COUNTS_PATH` and used by every accepted
  nbpolar derivation (e.g. P20H identity doc). The packet's repo-relative
  spelling of the same canonical path
  (`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`)
  resolves inside this worktree to a missing gitignored `*.npz`; the
  canonical sibling root is the established read-only resolution and was
  used for the single open. The runner's `--counts` check accepts ONLY a
  path resolving to the canonical file.
- npz size (stat at open): `25166822` B (matches the P20H identity pin).
- Array opened: `type2_2M_20260121_183657_N_ab_train_N_ab_train` (the
  `--source 2M` TRAIN array) — the npz member listing comes from the zip
  directory; NO other member content was read (never the 1M/1.5M arrays).
- Array identity: shape `(1024, 1024)`, dtype `float64`, total
  `559872` (== manifest 2M TRAIN pairs), C-order bytes sha256
  `e391a3466eee4354f76d65be7093f78b8322103178b6d8577331dbcd092351e4`
  (no whole-file hash was computed, so no other array's bytes were touched).
- `p_b` cross-check: column totals / total = `1.0`; counts total integer
  `559872`.
- **counts-calibration opens 1/1 (consumed by the single Stage-A
  derivation open); every other source array 0.**
- Floor/zero-column literals: `f_raw` pre-floor cells below `1e-15` =
  `1045941` / `1048576` (rate `0.9974870681762695`); zero columns `0`;
  column-renormalization dev `1.13464793116691e-13`.

## 2. 2M raw-prior artifact (§3, P20O-R1)

- Path: `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz`
  (25438650 B; created once; fail-if-present).
- **Canonical digest (the `--prior-digest` pin)**:
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`
  (`per_session_calibration.canonical_prior_digest` recipe: sorted-key
  `key + shape + dtype + C-order bytes` sha256; independently recomputed
  read-only from the artifact).
- Keys (exactly 10): `counts_ab, f_raw, p1, p2, p_b, lambda_star,
  floor_value, h1, h2, h_total` (`lambda_star` stored `0.0`; `floor_value`
  stored `1e-15`; no lambda anywhere).
- Rule (frozen): `n_b[b] = counts_ab.sum(axis=0)`;
  `f_raw[a,b] = counts_ab[a,b]/n_b[b]`; `f_raw = max(f_raw, 1e-15)` then
  column renormalize; zero columns fall back to `p_global` exactly;
  `p1`/`p2` via accepted `prior.derive_p1`/`derive_p2` under
  `A = 32*U1 + U2`, `FULL_BOB_ONLY`.
- Session H literals (computed via accepted
  `target_construction.entropy_bits`, never hand-filled):
  `h1 = 0.02566204884275839`, `h2 = 0.8069006731309893`,
  `h_total = 0.8325627219737477`.

## 3. Budget/split/orders (§§3/5, P20O-R2)

- **Budget literal (S2-i, same-run 2M session H)**:
  `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536] = 7080`.
  Recomputation from `FROZEN_H_TOTAL` replays exactly; never a carried
  absolute from 1.5M; the alt-H literals never enter any budget.
- **K literals**: `K_total = 7080`, `K1 = 334`, `K2 = 6746`
  (`K1+K2 = K_total`; replayed, never recarried).
- Split rule: accepted `select_empirical_split` semantics on 16 synthetic
  TRAIN blocks model-sampled from the 2M raw prior under frozen derivation
  seeds `2026092321..2026092324` (4 streams × 4 blocks; L1+L2 genie calls
  `32/32`; `train_blocks_used 16`; `train_impossible 0`;
  `provenance_violations 0`; TRAIN residual
  `3.603823440223586e-07`). Never a real frame; never DEV.
- Order file: `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json`
  (438535 B), file-bytes sha256
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`
  (the `--order-digest` pin; independently confirmed with `sha256sum`).
  Document: protocol `nbpolar-p20o-2m-maintain-confirmation`, kind
  `raw-prior-orders-file`, `n 32768`, `k1 334`, `k2 6746`, `k_total 7080`,
  full L1+L2 permutations of `0..N-1`, derivation program pin (exact),
  derivation seeds and 16-block/genie provenance. Zero Stage-B sampling.

## 4. Alt-L2-table artifact (§3, P20O-R1/R4)

- Path: `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz`
  (25430240 B; created once by the same Stage-A run; fail-if-present).
- **File-bytes sha256 (the `--alt-digest` pin)**:
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
  (independently confirmed with `sha256sum`).
- Keys (exactly 9): `counts_ab, f_alt, p1, p2_alt, alpha, floor_value,
  h1_inc, h2_alt, h_total_alt` (`alpha` stored `1.0`; `floor_value`
  stored `1e-15`).
- Rule (frozen α=1): `f_alt[a,b] = (counts_ab[a,b] + 1)/(n_b[b] + 1024)`
  (1024 = Alice-alphabet size) → `1e-15` floor + column renormalize
  (retained formally) → `p2_alt = derive_p2(f_alt)` under
  `A = 32*U1 + U2`, `FULL_BOB_ONLY`; `p1` = the Stage-A 2M incumbent `p1`
  (L1 fixed; the SAME counts).
- Literals frozen at Stage A:

| literal | value |
|---|---|
| counts total | `559872` (== manifest 2M TRAIN pairs) |
| floor hits (cells < 1e-15) | `0` / 1048576, rate `0.0` |
| zero columns | `0` |
| `f_alt` min / max | `0.0006071645415907555` / `0.2895392278953916` |
| column renormalization dev | `7.127631818093505e-14` |
| `p1` equality max-abs-diff (stored vs incumbent) | `0.0` |
| `h1_inc` | `0.02566204884275839` (== session H1) |
| `h2_alt` | `1.3245794596410305` |
| `h_total_alt` | `1.3502415084837889` (descriptive only) |

## 5. D1 feasibility literals + D2 gate outcome (§3, P20O-R9)

- Estimator (frozen literal):
  `ce_insample_bits_per_symbol = (1/total) * sum_{a,b} counts_ab[a,b] *
  (-log2 p2[u1(a), b, u2(a)])`, `u1(a)=(a>>5)&31`, `u2(a)=a&31`, on the
  SAME 2M TRAIN counts the tables were built from (zero protected reads).
- D1 literals:

| literal | value |
|---|---|
| `ce_alt_insample_bits_per_symbol` | `0.8850983725781965` |
| `ce_incumbent_insample_bits_per_symbol` | `0.8069006731253678` |
| `alt_feasibility_ceiling_bits` | `33794 = 5*6746+64` |
| operational ceiling (reference) | `35464 = 5*7080+64` |
| `alt_ideal_length_bits = ce_alt * 32768` | `29002.90347264234` |

- **D2 `alt_construction_budget_feasibility` = FEASIBLE**:
  `29002.90347264234 <= 33794` (margin `4791.09652735766` bits). Evaluated
  at Stage A BEFORE any Stage-B root creation and before any VAL contact;
  VAL-DEV read stays 0/1; the packet proceeds to independent Pre-EXECUTE.

## 6. Per-arm caps and planned totals (§5, P20O-R3)

- Preregistered per-arm caps (rule `5*(K1+K2)+64` key-dependent bits/block,
  `10*32768+63 = 327743` public bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_incumbent_L2_operational | 334 | 6746 | 35464 = 5*7080+64 | 327743 |
| B_alt_L2_operational | 334 | 6746 | 35464 (Δ vs A exactly 0) | 327743 |
| C_incumbent_L2_oracle | 0 | 6746 | 33794 = 5*6746+64 | 327743 |
| D_alt_L2_oracle | 0 | 6746 | 33794 (Δ vs C exactly 0) | 327743 |

- Planned totals: key-dependent `692580` = 5*(2*35464 + 2*33794) bits;
  public `6554860` = 20*327743 bits. Twenty records (5 blocks × 4 arms),
  30 SC calls, 20 tags at Stage B; zero Stage-B sampling.

## 7. Population, gates, tag domain, envelope (§§4/6/8, P20O-R2/R6)

- DEV: FIRST 640 VAL frames of `type2_2M_20260121_183657` in
  (frame_id, pair_idx) order: `2187..2826`; blocks
  `2187..2314 / 2315..2442 / 2443..2570 / 2571..2698 / 2699..2826`
  (5 × 128 frames at N=32768; 163840 pairs); unused remainder
  `2827..2915` (89 frames / 22784 pairs, counted never decoded); build
  frames 2M TRAIN `0..2186` (S2-ii disjointness declared with frame sets).
- Consumed/closed exclusions enforced by the frozen gate family (a)→(g):
  cross-file 2M source identity first (the 1M full-pool path and the 1.5M
  session path refuse by name; the size pin `2458335` B + sha256
  `d5a36eec8a03ce7e801bba4fd4b2e62cf8aef13c1efe1166766db79364ffc307` are
  the v13r3fresh build-manifest provenance constants), then intra-file VAL
  containment (`2187..2915`, no TRAIN/HOLD overlap), consumed-2M-TRAIN /
  2M-HOLD and identity-level consumed-1M / consumed-1.5M exclusions incl.
  the S2-ii declaration, then session-prior + alt-identity + order-freeze +
  K-literal + budget-literal + maintain-confirmation-identity pins — all
  before any SC call.
- Tag domain (new P20O): master `2026092310`, prefix
  `nbpolar-p20o-maintain-2m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
  MSB-first, truncated to `10*N+63 = 327743` bits). Master/test/derivation
  seeds verified by repo grep to appear only in the P20O runner, tests,
  packet and P20O OpenSpec documents.
- Envelope: external `timeout 1200` s, virtual `ulimit -v 2097152` KiB,
  `RSS_LIMIT_BYTES = 2 GiB`, single-thread exports; P20A resource-stop
  passthrough; abort is BLOCKED, never success.
- §7 instrumentation: the eight X09-R1 scalars PLUS the ninth U-domain
  scalar `l2_fail_in_prefix_u_domain` **frozen PRESENT** (main-thread
  instruction; closes the P20N domain-mixed `l2_fail_in_prefix`
  ambiguity). Frozen semantics: null unless `first_error_layer == L2`;
  otherwise whether the U-domain first-mismatch index
  (`polar_transform(low_hat)` vs the U-domain truth `view['u2']`; the
  disclosed L2 prefix set `first-K2 of the frozen 2M L2 order` lives in the
  same U-domain index space) lies in the disclosed L2 prefix set. Computed
  post-decode in `_l2_hazard_diagnostics(..., field=..., low_hat=...)`,
  recording-only, covered by
  `test_instrumentation_fields_nullability_and_formulas` (both membership
  outcomes + exact formula) and the truth-isolation sentinel; every record
  must carry it with the frozen nullability or the
  `hazard_instrumentation_complete` gate BLOCKS.

## 8. Frozen Stage-B command (byte-identical to the filled STEP-2 block)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --source 2M --floor 1e-15 --n 32768 --k1 334 --k2 6746 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2187 2826 --block-frames 128 --remainder-frames 2827 2915 --tag-master 2026092310 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m
```

`FROZEN_COMMAND` in the module equals this block byte-for-byte (verified by
substituting the five `<FROZEN_AT_STAGE_A>` placeholders of the frozen
STEP-2 template and comparing strings).

## 9. Stage-A close state and read audit

- Stage-B output root ABSENT (frozen check in the test suite).
- Protected reads at Stage-A close: **counts 1/1 (2M array ONLY) +
  VAL-DEV 0/1 + VAL-remainder 0 + 2M HOLD 0 + 1M/1.5M 0 in every form**
  (the derivation opens only the counts file and never touches any pairs
  parquet; no decoder execution; 32 Stage-A-only synthetic genie calls,
  zero real frames).
- Audit deviation (disclosed): during early reconnaissance, one `ls -la`
  directory listing of the 2M pairs directory printed the parquet's size
  and mtime metadata (no content read, no hash, no frame/symbol access,
  no content open). No pin, derivation, selection or gate input uses that
  observation: the size pin `2458335` comes from the v13r3fresh
  build-manifest JSON, which was read (metadata) as the packet allows; the
  observed size happens to equal it. Recorded in
  `P20O_IMPLEMENTATION_NOTES.md` and the operator return.
- Focused tests: 20/20 green pre-freeze (pins `None`, injected seams) and
  20/20 green post-freeze (frozen pins; `39.17 s`); fresh additive
  `workspace/p20o/<uuid>/` roots; no production invocation.
- Stage B remains unauthorized; the operator marks nothing accepted.
