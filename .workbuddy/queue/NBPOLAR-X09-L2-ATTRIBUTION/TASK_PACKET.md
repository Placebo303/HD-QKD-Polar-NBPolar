# TASK_PACKET.md — NBPOLAR-X09-L2-ATTRIBUTION (frozen Tier-X probe)

Probe: `NBPOLAR-X09-L2-ATTRIBUTION` | Tier: X (non-claim, decoder-free) | Date: 2026-09-19
Worktree: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` | Branch: `codex/nbpolar-phase0`
Cost class: zero-cost diagnostic. Consumes NO counts/DEV/HOLD reads and NO attempt.

## 1. Question

P20M (`NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M`, accepted descriptive) is the first
genuinely out-of-sample 1.5M test:

- G0 (λ control 319/6492): 0/3, L1 first errors 24/5/17
- G1 (raw prior 331/6689): 0/3, first errors L2/26 (l1_exact TRUE), L1/848, L2/31 (l1_exact TRUE)
- G2 (true-L1 oracle, K2 6689): 0/3, first errors L2/26, L2/3646, L2/31 (`oracle_l2_exact` false)

Oracle arms on TRAIN segments were 3/3 exact. Attribution question: which mechanism
explains the out-of-sample L2 failure at K2=6689 —

- (H1) K2 disclosure-budget insufficiency out-of-sample,
- (H2) L2 order/metric non-generalization, or
- (H3) floor/heavy-tail (TRAIN zero-count cell) exposure —

using ONLY already-persisted worktree artifacts.

## 2. Frozen inputs (worktree-file reads only; stat size/mtime for each)

P20M (9 records + priors + plan):
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/per_block_arm_outcomes.jsonl`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/aggregate_summary.json`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/frozen_plan.json`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/input_and_predecessor_identity.json`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/report.md`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz`
  (keys: counts_ab / f_raw / p1 / p2 / p_b)
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json`
  (L1/L2 permutations + provenance)

In-sample comparison records:
- `.workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m/per_block_arm_outcomes.jsonl`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/l1_dose_escalation_1p5m/per_block_arm_outcomes.jsonl`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m/per_block_arm_outcomes.jsonl`
- `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation/per_block_arm_outcomes.jsonl`

Runner code (read-only, field semantics only):
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/raw_prior_val_1p5m.py`
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_order_1p5m.py`
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_disclosure_1p5m.py`
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_escalation_1p5m.py`
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_512_1p5m.py`

Frozen constants: K2=6689, N=32768, H2=0.8003665547495433,
G2 cap 33509 (=5*K2+64), G1 cap 35164 (=5*331+5*6689+64),
in-sample conditional entropy N*H2 bits. Observed L2 failure coords: 26, 3646, 31.

FORBIDDEN: any parquet/pairs content; any DEV/VAL/HOLD/1M/V25-counts/2M open,
stat, or listing in any form; decoder/RNG/tag calls; any write outside the two
allowed roots (` workspace/probes/nbpolar_x09_l2_attribution/` execution writes;
this packet dir for packet docs); commit/push.

## 3. Computation (frozen; no decoder)

1. `field_semantics`: for every per-record field used, cite writing code line
   (file:line) + exact meaning; in particular `first_error_layer`,
   `first_error_coord` (index space precisely: natural symbol index vs L1/L2
   decode-order position, verified against code), endpoint booleans (`l1_exact`,
   `hard_l2_exact`, `pair_exact`, `oracle_l2_exact`), floor fields
   (`floor_hits_1e15`, `floor_hit_rate`, `floor_hit_log_loss_bits`, `raw_zero_count_hits`).
2. `available_fields`: inventory across P20M 9 records + in-sample predecessor
   records; state whether any per-record L2 NLL / cross-entropy / per-layer
   log-loss-bit fields exist (exact key names); else UNAVAILABLE.
3. `budget_attribution` (H1): exact in-sample L2 budget arithmetic
   (capacity `5*K2+64`, N*H2 bits, ratio); IF per-record out-of-sample L2 NLL/CE
   bits persisted, compare per arm/block vs capacity with margin; ELSE
   H1 NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS.
4. `floor_attribution` (H3): per-record floor-hit counts/rates/log-loss bits
   P20M vs in-sample predecessors; totals + per-arm tables; descriptive
   floor-exposure comparison; floor-attributable bits of any persisted L2 log-loss.
5. `order_geometry` (H2): from orders json + f_raw/counts_ab: L2 permutation first
   K2=6689 positions; TRAIN zero-count cells (counts_ab==0 → f_raw==floor mass)
   under p_b-weighted TRAIN law; overlap/coverage (fraction of top-K2 positions
   that are floor-hazard cells); rank/neighbor statistics of failure coords
   (26, 3646, 31) vs disclosed prefix + floor-hazard structure — only what
   persisted data supports.
6. `hypothesis_table`: H1/H2/H3 each SUPPORTED / NOT SUPPORTED /
   NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS with single strongest evidence line.
7. `next_packet_requirements`: minimal instrumentation a successor packet must
   persist to close NOT-DECIDABLE items (e.g. per-record L2 NLL bits,
   failure-neighborhood floor stats). Requirements only, no packet design.

## 4. Output

Probe root `workspace/probes/nbpolar_x09_l2_attribution/`:
`prereg.md` (pre-read; fenced ```python body block + exact command + artifact list),
`body.py` (byte-identical to block; runtime equality assert), `results.json`
(indent=1; ONLY file body.py writes) with at least: probe_id, tier "X", status
"X09_PROBE_COMPLETE_DESCRIPTIVE_ONLY", question, prereg_sha256, body_sha256,
body_sha_match, artifact_inventory (path/size/mtime_ns per file read;
`protected_opens_attempted: false`), field_semantics, available_fields,
budget_attribution, floor_attribution, order_geometry, hypothesis_table,
next_packet_requirements, command, interpreter, wall_s, rss_bytes, decoder_calls 0,
rng_calls 0, tag_calls 0, writes, notes. No verdict about the next scientific factor.

## 5. Execute (exactly once; execution-error rerun allowed and recorded)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_x09_l2_attribution/body.py
```

## 6. Stop rules

Missing/absent expected file, unreadable JSON/JSONL, key-set surprise in npz,
nonfinite result → STOP, write results.json with specific STOP status, return.
No repair by editing inputs.

## 7. Return (deltas only)

Files created; exact command + exit/wall; hypothesis table; budget/floor/order key
numbers; UNAVAILABLE items; next-packet requirement list; blocker-or-none. No claims
beyond descriptive support labels; no commit/push.
