# TASK_PACKET — NBPOLAR-X10-H2-SCALAR-ADJUDICATION (Tier-X, frozen)

Probe ID: `NBPOLAR-X10-H2-SCALAR-ADJUDICATION`
Tier: X (non-claim, decoder-free, read-only on already-persisted worktree artifacts).
Branch: `codex/nbpolar-phase0`. Worktree: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.

## 1. Question
The frozen `ALT-L2-LAPLACE-α1` construction restores blocks the incumbent loses
(P20N 1.5M HOLD: B 1/4 vs A 0/4; P20O 2M VAL 2187..2826: B 2/5 vs A 0/5, D 3/5),
yet the alt metric has HIGHER in-sample CE (0.8851 vs 0.8069) and higher prefix
hazard means (0.89–0.90 vs 0.80–0.86). Adjudicate sub-hypotheses H2a–H2e (L2
order/metric non-generalization) SOLELY from the persisted 9-scalar
instrumentation + coordinates, and emit precise instrumentation-enhancement
requirements for whatever remains undecidable. Descriptive support labels only;
no significance claims; no scientific claims beyond the persisted scalars.

## 2. Frozen inputs (worktree-file reads only)
Required (STOP if missing/unreadable):
- `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/per_block_arm_outcomes.jsonl` (16 records)
- `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/aggregate_summary.json`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/per_block_arm_outcomes.jsonl` (20 records)
- `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/aggregate_summary.json`
Optional baseline (record absent-and-continue if missing; no STOP):
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/per_block_arm_outcomes.jsonl` (9 records where fields overlap)
Geometry context, optional, recording-in-inventory-only (no STOP on absence; NPZ
files are NEVER opened — stat for inventory only):
- Candidate `raw_prior_orders_1p5m.json`, `raw_prior_orders_2m.json`,
  `raw_prior_1p5m.npz`, `raw_prior_2m.npz`, `alt_l2_tables_1p5m.npz`,
  `alt_l2_tables_2m.npz` (short names from freeze; exact worktree paths were not
  resolved at packet-freeze time — body treats any unresolved candidate as
  absent, no search, no glob).
- Runner code for field semantics, inventory-only (content not required):
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py`,
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_maintain_2m.py`.

FORBIDDEN: any protected-content open/stat/listing (V25 counts NPZ, pairs
parquet, 1M/1.5M/2M content, not even stat); decoder/RNG/tag calls; any write
outside the two allowed roots; commit/push.

## 3. Computations (frozen; no decoder)
1. Normalized compact table: 16 (P20N) + 20 (P20O) = 36 records, plus the 9-row
   P20M baseline where fields overlap. Per record: packet/session/block/arm,
   K1/K2, outcome, first_error_layer/coord, tag_pass/label_match, key bits, and
   the nine scalars where present (scalars only — drop list/dict series).
2. H2a average-quality: order arms within each block by
   `l2_prefix_hazard_mean_bits`; check exactness ordering, paired per block and
   across blocks; surface P20O b1/b2 and P20N b3 higher-mean-exact cases.
3. H2b first-error hazard: failing records, `l2_fail_hazard_bits` and
   `l2_fail_nbhd_mean_bits` vs block prefix mean (ratios/distribution), split
   incumbent (arm A) vs alt (arm B); arms C/D reported separately.
4. H2c coordinates: first-error natural-coordinate distribution (early/late) per
   arm/session; cross-tab with `l2_fail_in_prefix` (X) and
   `l2_fail_in_prefix_u_domain` (P20O); consolidate 12/14-in-X (P20N) and
   11/11-in-X-but-out-U (P20O) against recomputed counts.
5. H2d floor: `l2_fail_nbhd_floor_frac` vs `l2_prefix_floor_frac` separation
   check (expected flat).
6. H2e static-order geometry: verify per-position `(b,u1)` sequences / hazard
   series are absent (prefix means only); list exactly the missing quantities.
7. `instrumentation_requirements`: minimal, BOUNDED, recording-only additions
   (histograms, rank percentile, above-threshold counts, top-k positions, capped
   series) each with size cap + truth-isolation boundary.
8. `results.json` (indent=1) keys: probe_id, tier "X", status
   "X10_PROBE_COMPLETE_DESCRIPTIVE_ONLY", question, prereg_sha256, body_sha256,
   body_sha_match, artifact_inventory (paths/sizes/mtimes;
   `protected_opens_attempted: false`), record_table, hypothesis_table,
   h2a/h2b/h2c/h2d/h2e, instrumentation_requirements, command, interpreter,
   wall_s, rss_bytes, decoder_calls 0, rng_calls 0, tag_calls 0, writes, notes.

## 4. Output / stop rules
- Probe root `workspace/probes/nbpolar_x10_h2_scalar_adjudication/` MUST be
  absent before start (it was: verified 2026-09-19). Contents after: `prereg.md`
  (pre-read), `body.py` (byte-identical to prereg fenced block; runtime assert),
  `results.json` (only file body.py writes).
- Execute EXACTLY once:
  `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_x10_h2_scalar_adjudication/body.py`
  One rerun allowed ONLY on execution error, recorded in `results.json` notes.
- STOP (with specific status in `results.json`, no repair of inputs) on:
  missing/unreadable required file, malformed JSONL/summary, record-count
  mismatch on required files (16/20), or nonfinite numeric result.

## 5. Return (deltas only)
Files created; command + exit/wall; hypothesis table; key H2a/H2b/H2c numbers;
instrumentation-requirements list; blocker-or-none. No claims beyond descriptive
support labels; no commit/push.
