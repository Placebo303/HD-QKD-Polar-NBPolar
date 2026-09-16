# Phase 4-P16 operator return — N=32768 operational f=1.3 gate (candidate, NOT acceptance)

Packet: `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13` (Tier-Y).
Result label: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` (candidate;
main-thread acceptance pending; this return is not an acceptance).

## 1. Mission

Measure actual two-layer hard-candidate SC recovery at the accepted V25 1M
TRAIN target model, N=32768, planning f≤1.3: empirical construction frozen
before DEV, 64 fresh operational DEV blocks, one 64-bit Toeplitz tag per
block. Context: P15's genie UCB was conservative and is not an operational
outcome. No BEC arm, no retry/adaptive arm, no P12 rerun.

## 2. Implementation / tests

Thin runner `formal_ir/nbpolar/operational_f13.py` + focused
`tests/test_nbpolar_operational_f13.py`: reused accepted P7 load/support/
preconditions, P13 genie/construction/allocation, P4 causal wiring, P5
hard-candidate/tag pattern, P11 chunked SC (`chunk_rows=512` contract-checked),
P12 f-budget helper. No accepted-module/evidence/old-root change.
Focused 23/23 green; full NB-Polar 358/358 green (pinned interpreter,
`-p no:cacheprovider`, fresh basetemps; injected tables/seeds only).

## 3. Pre-run checks

Independent Pre-EXECUTE review: PASS (five flagged items ratified, incl.
`2026092001`/v22-DE-seed coincidence ruled stream-fresh; nonfinite bucket,
TRAIN checkpoint shape, DEV-abort/TRAIN-raise split, Wilson-check placement).
Output root absent, NPZ stat-only 25166822 B, reads/attempts 0/0, frozen
command byte-identical to packet §P16-06.

## 4. Exact command

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13 --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 32768 --train-seeds 2026092000 2026092001 2026092002 2026092003 --train-blocks-per-stream 4 --dev-seeds 2026092010 2026092011 2026092012 2026092013 2026092014 2026092015 2026092016 2026092017 --dev-blocks-per-stream 8 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate
```

Single gate executed once: exit 0, stderr empty, wall 1183.61887 s (≤2100 s
budget). NPZ 25166822 B read-only (size/mtime 2026-08-19 unchanged).

## 5. Preconditions (7/7 true)

H1 0.024280546818678802 vs literal 0.02428054681872374 (Δ≈4.49e-14); H2
0.7767572780789994 exact; total 0.8010378248976782 vs literal
0.8010378248977232 (Δ≈4.51e-14); floored total 0.8010378249492791; floor
change 5.1600945738528026e-11 (≤1e-9); column deviation
1.1357581541915351e-13; p_b sum 1.0.

## 6. Consumption (1/1 spent, no rerun)

Artifact reads 1/1, attempts 1/1, opens 1, reopen False, retries 0; TRAIN
genie 32/32 (16 blocks × 2 layers) + DEV operational SC 128/128 (64 × 2);
provenance violations 0. No reopen, no rerun, no tuning.

## 7. Construction / allocation + TRAIN

N=32768, K_total 6811 (raw 6811.785936024251; split K1 319 + K2 6492),
leakage 34119 bits, f 1.2998502888173578 ≤ 1.3. TRAIN 16 blocks
(used_l1/used_l2 16, impossible 0, residual 5.87097048643237e-07); orders
frozen before first DEV; digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
(recomputed match).

## 8. DEV outcome table (64 blocks)

Counts: exact 62 / undetected 0 / verify_failed 2 / decode_failed 0 /
nonfinite 0 / resource_abort 0. Per-stream: seven streams 8/8 exact;
2026092015-block5 verify_failed (tag False, label False); 2026092017-block3
verify_failed (tag False, label False). Sums: l1_executed 64, l2_invoked 64,
tag_invoked 64 (pass 62 / False 2), label_match 62 / False 2,
truth_leak_violation 0, error None on all 64 rows.

## 9. Recovery gates (BOTH true, zero-count margin — blunt)

Exact fraction 62/64 = 0.96875 ≥ 62/64 TRUE. Wilson one-sided 95% LB (z
1.6448536269514722) = 0.9098711859061207 ≥ 0.90 TRUE (margin +0.00987).
Boundaries: 62/64 → 0.9098711859 (pass); 61/64 → 0.8883797144 (fail).
ZERO-count margin: exactly at threshold (62−62=0); ONE fewer exact flips the
frozen-rule classification to NOT_CONFIRMED. This is an exact threshold meet,
not headroom.

## 10. Disclosure / public / recount

Per-block key 34119 (= 5×6811+64), public 327743 (= 10×32768+63) per invoked
tag. Totals: key 2183616 (= 64×34119), public 20975552 (= 64×327743), tags
64. Independent literal recount: l1 64 / l2 64 / tag 64, mismatch 0.

## 11. Resources

Wall 1183.61887 s (per-block walls 11.794088–13.15363, sum 790.799327;
overhead ≈392.82 TRAIN/freeze/finalize); RSS peak 545861632 B (≈520.6 MiB);
per-block RSS HWM 543035392–545861632; VmPeak 761360–763408 kB; VmSize
597516–599564 kB; all < 2 GiB; aborts 0; no resource stop; no MemoryError.

## 12. Gate table (13/13 true, failing list empty)

target_population_contract / construction_frozen_before_dev /
train_dev_coverage_complete / streams_disjoint_frozen /
orders_valid_k_replay_f_within_budget / buckets_disjoint_exhaustive /
truth_isolation / undetected_zero / nonfinite_zero / no_unregistered_calls /
disclosure_recount_exact / attempt_read_accounting_exact /
resource_limits_met_and_no_abort — all TRUE (independently recomputed).

## 13. Classification derivation

Integrity all-TRUE ∧ recovery all-TRUE ⇒
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` uniquely per frozen
`select_label` rule. NOT_CONFIRMED would need recovery-FALSE; BLOCKED would
need earliest-integrity-FALSE; neither applies. Independent Pre-RESULT:
PASS_WITH_COMMENTS (independent 62/64 recount + own Wilson recomputation
confirm CANDIDATE; zero-count margin stated; k_total_raw repr dust and 18 ms
wall-sum dust immaterial).

## 14. Bounded scope

Model-sampled operational outcome at N=32768/f≤1.3 ONLY. NOT real-data FER,
held-out FER, efficiency/key-rate, scaling superiority, qualification, or
promotion. No BEC arm; planning f is not real-channel efficiency; undetected
is never success. Threshold-sit neutrality: reported as exact meet with zero
count buffer.

## 15. Unrun stages / provenance

Unrun stages: none (main-thread acceptance remains; this return does not
accept). Evidence: this file + `operational_f13_gate/` (five files:
frozen_plan / construction_and_allocation / per_block_outcomes /
aggregate_summary / report); packet `P16_FREEZE.md`,
`P16_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS),
`PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS). No box checked; no code/artifact/
old-root touched; NPZ untouched; no commit/push.
