# P20I Stage-B operator return (single authorized execution, descriptive only)

- Packet: `NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M` (Tier-Y). Operator: Stage-B single attempt.
- Branch: `codex/nbpolar-phase0`, HEAD `faac0411` (matches Pre-EXECUTE).
- Transcription check: the user-pasted command matches `P20I_FREEZE.md` §10 verbatim
  (16 flags, `--dev-frames 384 767` / `--remainder-frames 768 1659` /
  `--tag-master 2026092230`, K1 319 / K2 6492, dual digests). Module `FROZEN_COMMAND`
  import-check confirms byte-identical content. **No transcription correction needed.**
- Prior digest pre-check (worktree-file read, never a counts open): canonical digest
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` MATCH,
  lambda `137.3823795883264`, floor `1e-15`, H1 `2.006647056368773` / H2
  `1.9017235959286112` / TOTAL `3.908370652297384`, exact 10-key set. PASS.
- Output-root absence pre-check: `l1_disclosure_1p5m/` ABSENT (stat ENOENT). PASS.

## Actual execution command (verbatim, one shot)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_disclosure_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 384 767 --block-frames 128 --remainder-frames 768 1659 --tag-master 2026092230 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m
```

- Start: 2026-09-18T18:48:27Z. End: 2026-09-18T18:50:20Z. Exit code: 0.
- Stdout tail: 9 records, `integrity_all_pass: true`, label
  `TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE`,
  `operational_exact_count: 0`, `c1_restored_count: 0`.
- No rerun, no tuning, no second invocation. One-shot consumed at first DEV content open.

## Five evidence files

`.workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m/`:
`frozen_plan.json`, `input_and_predecessor_identity.json`,
`per_block_arm_outcomes.jsonl` (9 records), `aggregate_summary.json`, `report.md`.

## Gate statistics

- Integrity: 21/21 PASS, failing `[]`. Label
  `TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE` (descriptive, any
  exact count is COMPLETE when integrity holds).
- SC 15/15 (operational 2/record × 6 + oracle 1/record × 3), tags 9/9, recount
  mismatch 0 (`disclosure_recount_exact: true`).
- `undetected` 0 (isolated, never success), `nonfinite` 0, `decode_failed` 0,
  `resource_abort` 0, no abort, `resource_limits_met_and_no_abort: true`.
- Wall 110.58 s (ceiling 600 s), peak RSS 559026176 B (~533 MB, cap 2 GiB),
  single-thread env. Within the P20C-class envelope.
- `oracle_isolation: true`, `truth_isolation: true`, `buckets_disjoint_exhaustive:
  true`, `one_open_per_protected_input: true`, `input_stat_unchanged: true`
  (DEV size 1869178 B identical before/after), `no_unregistered_access: true`.
- Construction digest recomputed `055c9064…c3faea1b` match; prior digest
  `e8dd078a…e43b` match; DEV sha `ca351e52…a06b` / size 1869178 B pin verified.

## Per-arm exact / L1 correctness (descriptive)

| arm | exact | per-block outcomes |
|---|---|---|
| C0_sc_base (K1 319, operational) | 0/3 | blk0 verify_failed, blk1 verify_failed, blk2 verify_failed |
| C1_L1plus (K1 447, +128 order-prefix, operational) | 0/3 | blk0 verify_failed, blk1 verify_failed, blk2 verify_failed |
| C2_true_l1_diagnostic (K1 0, oracle, deployable=false) | 3/3 exact | blk0/1/2 exact, isolated from every operational aggregate |

- `c1_restored_count` analogue (C0 fail → C1 exact): **0/3** (blk0 false, blk1
  false, blk2 false). No restoration, no maintain (C0 exact nowhere).
- Endpoints per operational record: `l1_exact` false (6/6), `hard_l2_exact` false
  (6/6), `pair_exact` false (6/6); oracle records `oracle_l2_exact` true (3/3).
- Zero FER /晋级 claim: none. Zero recovery/efficiency/promotion language: none.

## First-error layer and endpoint table (descriptive)

All six operational first errors are L1-layer:

| block (frames) | C0 first error | C1 first error | C1 ΔK1 / keyΔ |
|---|---|---|---|
| blk0 384..511 (raw SER 0.2520) | 2/L1 | 2/L1 (unchanged) | 128 / +640 |
| blk1 512..639 (raw SER 0.2526) | 17/L1 | 1/L1 (moved earlier) | 128 / +640 |
| blk2 640..767 (raw SER 0.2535) | 13/L1 | 16/L1 (moved later) | 128 / +640 |

- C2 records: no first error (exact under true-L1 conditioning at base K2=6492).
- Per-record keys: C0 key 34119 / C1 key 34759 / C2 key 32524, public 327743/tag.
- C1 disclosure triple pinned per record: `l1_delta_k1_applied` 128 (C1) / 0
  (C0/C2), rule frozen-order-prefix-extension (C1) / base (C0), `key_bit_delta_vs_base`
  640 (C1) / 0.

## Accounting identities (recomputed from artifacts)

- Key: 3·34119 = 102357 (C0) + 3·34759 = 104277 (C1) + 3·32524 = 97572 (C2) =
  304206 total (operational 206634 + oracle 97572). Match.
- Public: 9·327743 = 2949687 (3 arms × 983229). Match.
- Caps vs raw (327680 bits/block): base 34119 → 0.10412292 (~10.41%), C1 34759 →
  0.10607605 (~10.61%), far below raw. CE ratios descriptive, not efficiency.
- SC derived recomputation 15, tags 9. Match.

## Consumption counts (split-counted)

- counts-calibration opens: 0/0 (V25 counts NPZ never opened; no NPZ loader in runner).
- Prior worktree-file loads: 1 (read-only reuse, not a protected open).
- DEV content opens: 0/1 → **1/1 SPENT** (first protected content open consumed the
  single attempt; `reopen_attempted: false`).
- HOLD reads: 0/1 untouched. Attempts: 0/1 → **1/1 SPENT**.
- No execution-error rerun (identical-freeze repeat not needed).

## 2M pristine confirmation

- 2M path appears only as `refused_2m_path` in the cross-file gate pins; never in
  `opened_content_paths` (exactly 2: frozen prior + 1p5M pairs parquet).
  `no_unregistered_access: true`. 2M never opened/statted/listed/read.

## Not run in this stage

- Pre-RESULT review, main-thread acceptance, memory triage, any §16 branch
  decision (C1-zero-restoration → P20D candidacy is planning input AFTER
  acceptance, never an in-packet verdict). No commit/push. No self-acceptance.
- No writes under `results/` or `comparison_bench/outputs_comparison/`.

## Blocker

- None. Return condition (a): Stage-B single attempt complete with commands,
  artifacts, and audits above; acceptance IDs R1–R8 stage-appropriately evidenced
  for Pre-RESULT review. The operator does not mark its own work accepted.
