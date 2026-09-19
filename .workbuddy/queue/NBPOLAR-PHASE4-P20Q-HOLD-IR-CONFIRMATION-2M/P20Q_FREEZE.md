# P20Q Stage-A freeze (frozen 2026-09-19; Stage B NOT authorized)

Packet: `NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M`
(`TASK_PACKET.md`). State after Stage A: every `<FROZEN_AT_STAGE_A>` pin
below is filled. Stage-B execution needs, in order: Stage-A return, an
independent Pre-EXECUTE PASS (adjudicating the §3 reuse/alt replay, the D2
replay outcome, the §5 budget/K-literal replay, the §4 gate family, the §2
runner-delta design and the §7 nine-scalar + IR-1..IR-5 boundary incl. IR-3
thresholds and IR-5 cap), the filled Stage-B authorization text, and
target-output absence. The Stage-B output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/`
is ABSENT (verified at Stage-A close).

Operator: `coder-fast` Stage-A instance. No commit/push. Operator never
self-accepts.

## 1. Reuse verification (R1 — worktree files ONLY; zero protected opens)

- Prior `raw_prior_2m.npz` (25438650 B): canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`
  replay-EXACT (`per_session_calibration.canonical_prior_digest` recipe);
  keys exactly `counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value,
  h1, h2, h_total` (`lambda_star` 0.0; `floor_value` 1e-15); H literals
  `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`
  recomputed via the accepted verifier within 1e-12; `p_b` cross-check
  passed (column totals / total, sum 1.0); floor hits `1045941` /
  `1048576` (rate `0.9974870681762695`); zero columns `0`.
- Orders `raw_prior_orders_2m.json` (438535 B): file-bytes sha256
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`
  replay-EXACT; full L1+L2 permutations, K1 334 / K2 6746 / K_total 7080,
  derivation program + seeds + 16-block/genie provenance pinned.
- Alt `alt_l2_tables_2m.npz` (25430240 B): file-bytes sha256
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
  replay-EXACT; keys exactly `counts_ab, f_alt, p1, p2_alt, alpha,
  floor_value, h1_inc, h2_alt, h_total_alt` (`alpha` 1.0; `floor_value`
  1e-15); `p1`-equality max-abs-diff `0.0` (within 1e-12); descriptive
  alt-H `1.3245794596410305 / 1.3502415084837889` (never a budget input).
- The `--verify-reuse` path of the new runner replays all three on the
  real frozen files: `{"reuse_prior_digest": "b16f52...",
  "reuse_alt_digest": "98e254...", "reuse_order_digest": "b22554...",
  "k_total": 7080, "d2_feasible": true,
  "d2_margin_bits": 4791.0965273576585, "hold_contact": 0, "verified": true}`.

## 2. Budget/split/orders replay (R2 — S2-i satisfied by reuse)

- **Budget literal (S2-i, same-run 2M session H)**:
  `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536] = 7080`.
  Replayed as a literal, never recomputed, never a carried absolute from
  1.5M; the alt-H literals never enter any budget.
- **K literals**: `K_total = 7080`, `K1 = 334`, `K2 = 6746`
  (`K1+K2 = K_total`; replayed, never recarried).
- Split manifest (JSON metadata only, schema
  `nbldpc_v25_split_manifest_v1`): 2M TRAIN 2187/559872 + VAL 729/186624
  + HOLD 729/186624. HOLD base 2916 by TRAIN 2187 + VAL 729
  manifest-count arithmetic (same arithmetic P20O used for TRAIN/VAL).

## 3. D1/D2 replay (R9 — BEFORE any HOLD contact; HOLD stays 0/1)

- D1 literals (recomputed from the worktree counts, zero HOLD reads):
  `ce_alt` 0.8850983725781965, `ce_incumbent` 0.8069006731253678,
  ceilings 33794/35464, `alt_ideal_length_bits` 29002.90347264234.
- **D2 `alt_construction_budget_feasibility_replayed` = FEASIBLE**:
  `29002.90347264234 <= 33794` (margin `4791.09652735766` bits;
  recomputed `4791.0965273576585`). Evaluated at Stage A before any
  Stage-B root creation and before any HOLD contact; the packet proceeds
  to independent Pre-EXECUTE.

## 4. Population, gates, tag domain, envelope (R2/R6)

- DEV: FIRST 640 HOLD frames of `type2_2M_20260121_183657` in
  (frame_id, pair_idx) order: `2916..3555`; blocks
  `2916..3043 / 3044..3171 / 3172..3299 / 3300..3427 / 3428..3555`
  (5 × 128 frames at N=32768; 163840 pairs); unused remainder
  `3556..3644` (89 frames / 22784 pairs, counted never decoded); build
  frames 2M TRAIN `0..2186` (S2-ii disjointness declared with frame sets).
- Consumed/closed exclusions enforced by the frozen gate family (a)→(g):
  cross-file 2M source identity first (the 1M full-pool path and the 1.5M
  session path refuse by name; the size pin `2458335` B + sha256
  `d5a36eec8a03ce7e801bba4fd4b2e62cf8aef13c1efe1166766db79364ffc307` are
  the v13r3fresh build-manifest provenance constants), then intra-file HOLD
  containment (`2916..3644`, no TRAIN/VAL overlap), consumed-2M-TRAIN /
  consumed-2M-VAL (DEV 2187..2826 + remainder 2827..2915) and
  identity-level consumed-1M / consumed-1.5M exclusions incl. the S2-ii
  declaration, then reuse-prior + reuse-alt + order-freeze + K-literal +
  budget-literal + hold-confirmation-identity pins — all before any SC call.
- Tag domain (new P20Q): master `2026092330`, prefix
  `nbpolar-p20q-hold-ir-2m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
  MSB-first, truncated to `10*N+63 = 327743` bits). Master/test seeds
  (`2026092331..2026092337`) verified by repo grep to appear only in the
  P20Q runner, tests, packet and P20Q OpenSpec documents.
- Envelope: external `timeout 1200` s, virtual `ulimit -v 2097152` KiB,
  `RSS_LIMIT_BYTES = 2 GiB`, single-thread exports; P20A resource-stop
  passthrough; abort is BLOCKED, never success.

## 5. Per-arm caps and planned totals (R3)

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_incumbent_L2_operational | 334 | 6746 | 35464 = 5*7080+64 | 327743 |
| B_alt_L2_operational | 334 | 6746 | 35464 (Δ vs A exactly 0) | 327743 |
| C_incumbent_L2_oracle | 0 | 6746 | 33794 = 5*6746+64 | 327743 |
| D_alt_L2_oracle | 0 | 6746 | 33794 (Δ vs C exactly 0) | 327743 |

Planned totals: key-dependent `692580` bits; public `6554860` bits.
Twenty records (5 blocks × 4 arms), 30 SC calls, 20 tags at Stage B; genie
0+0 (zero sampling at every stage).

## 6. Runner delta d1–d8 + instrumentation (R4/R5)

- New thin runner
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_ir_2m.py`
  importing accepted `l2_alt_maintain_2m` read-only (no accepted file
  touched) with ONLY the §2 d1–d8 delta; four hardcoded arms (§6);
  `reuse_prior_identity` + `reuse_alt_identity` + `reuse_order_freeze` +
  K-literal replay + cross-file source-tag+digest + intra-file
  HOLD-containment + consumed-1M/1.5M/2M exclusions (S2-ii) +
  hold-confirmation-identity + order-freeze + K-literal fail-closed gates.
- §7 recorders: the nine carried scalars via the carried-over P20O
  `_l2_hazard_diagnostics` callsite pattern PLUS the mandatory IR-1..IR-5
  recorder `_ir_hazard_diagnostics` (IR-1 64-bin {prefix,outside} with the
  frozen 65-edge log-spaced formula; IR-2 rank percentile in [0,1], null
  unless L2 failure; IR-3 EXACTLY two thresholds at 1.0×/2.0× record
  prefix-mean; IR-4 top-16 with 1-based ranks; IR-5 capped 4096×2 float32
  with truncation flag; all PRESENT, bounded, recording-only, post-decode,
  truth-isolation boundary pinned and sentinel-tested).
- IR-3 multipliers `1.0×/2.0×` (X10 median fail/prefix ratio 2.246
  justification, frozen before the run, never fed back); IR caps
  64-bin / 1-float / 2-threshold / top-16 / 4096×2+flag (~35 KB/record,
  ~700 KB/20 records).

## 7. Frozen Stage-A verify command (verbatim)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_ir_2m --verify-reuse --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --k1 334 --k2 6746
```

Executed at Stage A with output `verified: true`, `hold_contact: 0`
(see §1).

## 8. Frozen Stage-B command (byte-identical to the module FROZEN_COMMAND)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_ir_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --source 2M --floor 1e-15 --n 32768 --k1 334 --k2 6746 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2916 3555 --block-frames 128 --remainder-frames 3556 3644 --tag-master 2026092330 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m
```

`FROZEN_COMMAND` in the module equals this block byte-for-byte (verified
by programmatic string comparison at Stage A). NOT AUTHORIZED until
independent Pre-EXECUTE PASS + pasted Stage-B authorization.

## 9. Stage-A close state and read audit

- Stage-B output root ABSENT (frozen check in the test suite).
- Protected reads at Stage-A close: **counts 0/0 + HOLD-DEV 0/1 +
  VAL-DEV 0 + VAL-remainder 0 + 1M/1.5M 0 in every form** (worktree-file
  digest recomputation + split-manifest JSON-metadata reads only; no
  parquet/NPZ protected open/stat/listing; no decoder execution; zero
  sampling/genie at every stage).
- Focused tests: 14/14 green
  (`comparison_bench/tests/test_nbpolar_l2_alt_hold_ir_2m.py`,
  `pytest -p no:cacheprovider`); fresh additive `workspace/p20q/<uuid>/`
  roots; no production invocation.
- Stage B remains unauthorized; the operator marks nothing accepted.

(End of file)
