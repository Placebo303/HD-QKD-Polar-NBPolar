# P17 operator return — N=32768 operational replication (Tier-Y)

Packet: `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION`
Result: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` (candidate, NOT acceptance).
Main-thread acceptance remains separate; this return authorizes nothing.

## 1. Mission

Resolve P16's zero-count-margin result (62/64 exact, Wilson LB 0.9098711859)
with an independent 128-block replication at exactly the same target model,
N=32768, construction (K1=319/K2=6492), disclosure and protocol. No retraining,
no retuning; P16 observations are report-only and never pooled into the decision.

## 2. Implementation and tests

Thin replication runner only
(`comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13_replication.py`,
1691 lines): predecessor-file identity verification, the 128-block fresh DEV
matrix, the P17 tag-domain closure, 121/128 + Wilson-0.90 gates with the total
pinned to 128, and the thirteen-flag CLI. P16 operational helpers
(`run_operational_block`, `classify_operational_outcome`, record/event/recount
helpers) reused by import; no construction path, no second arm, no retry, no
P16-domain tag reuse. Known wart (Pre-EXECUTE R1, ratified): the accepted P16
block helper still derives its own internal P16-domain array in-memory before
invoking `tag_fn`; that array is never persisted or scored — the focused spy
test proves the scored seeds are exactly P17-domain.

Focused `comparison_bench/tests/test_nbpolar_operational_f13_replication.py`:
25/25 green. Full NB-Polar suite `test_nbpolar_*.py`: 383/383 green
(baseline 358 + 25). Pinned interpreter, fresh basetemps, `-p no:cacheprovider`.

## 3. Pre-run checks

Independent Pre-EXECUTE review: PASS (11/11 checks; R1–R5 ratified, non-blocking
only). Predecessor digest independently recomputed
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
triple-match (stored == recomputed == frozen flag); N/K1/K2/orders/K-replay/
leakage/f verified. Seeds 2026092030..2037 fresh (P16's twelve streams
blocklisted). Output root absent; NPZ stat-only 25166822 B, content never
opened; P16 root untouched; reads/attempts 0/0.

## 4. Frozen command (verbatim, executed once)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2400 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13_replication --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-seeds 2026092030 2026092031 2026092032 2026092033 2026092034 2026092035 2026092036 2026092037 --dev-blocks-per-stream 16 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate
```

Single gate executed once: exit 0, stderr empty, wall_s 2031.385216 (within the
2400 s budget; margin 368.6 s).

## 5. Predecessor identity re-verification (at execution)

Digest recomputed `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`,
match true. N=32768 / K1=319 / K2=6492 / K_total=6811; L1/L2 length 32768,
both valid permutations; leakage `5*6811+64 = 34119`;
f 1.2998502888172847 ≤ 1.3. P16 root untouched (five-file sizes/mtimes predate
the run; construction file JSON-read only).

## 6. Preconditions (7/7 true)

H1 0.024280546818678802 vs literal …2374 (diff 4.49e-14 ≤ 1e-12); H2 exact
(diff 0.0); total …6782 vs …7232 (diff 4.51e-14 ≤ 1e-12); floored total
0.8010378249492791; floor change 5.1600945738528026e-11 ≤ 1e-9; column dev
1.1357581541915351e-13 ≤ 1e-12; p_b sum 1.0. V25 1M TRAIN NPZ 25166822 B
read-only (size/mtime 2026-08-19 unchanged).

## 7. Consumption (1/1 + 1/1, no rerun)

Artifact reads 1/1, attempts 1/1, opens 1, reopen false, retries 0, consumed
together at the first NPZ content open. 256 operational SC calls, 0 TRAIN/genie
calls, 128 tags, `provenance_violations` 0, `truth_leak_violation` 0/128. No
reopen, no rerun, no seed/N/K/floor/order/threshold/tag change.

## 8. 128-block outcome

Counts (independent recount matches persisted): exact 123, undetected 0,
verify_failed 5, decode_failed 0, nonfinite 0, resource_abort 0.
The 5 verify_failed: (2026092030,12), (2026092031,11), (2026092033,5),
(2026092034,8), (2026092035,0). All 123 exact have label_match + tag_pass true;
all 5 verify_failed have tag_pass false; zero mismatches.

Per-stream (n=16, block_index 0–15 each), exact/verify_failed:
2030 15/1; 2031 15/1; 2032 16/0; 2033 15/1; 2034 15/1; 2035 15/1; 2036 16/0;
2037 16/0.

## 9. Recovery gates (both pass, count margin exactly 2)

Fraction 123/128 = 0.9609375. One-sided 95% Wilson LB 0.921934049951655
(z 1.6448536269514722) ≥ 0.90: TRUE. Exact ≥ 121/128: TRUE.
Count margin is exactly 2 over 121 — stated plainly. LB margin +0.0219.
Boundaries: 121/128 → 0.9021084760 TRUE; 120/128 → 0.8924595822 FALSE
(both load-bearing, verified in code before DEV and in tests).

## 10. Non-pooling verification

P16's 62/64 + LB 0.9098711859 appear only as `predecessor_report_only`
(`pooled_into_decision: false`) and report discussion with explicit
never-pooled/zero-weight language. Decision inputs are exactly the 128 P17
blocks (recovery total pinned to 128; any P16-shaped total structurally fails).
No P16 stream seed among the 128 records; no P16 observation enters any gate.

## 11. Disclosure / public / recount

Per fully invoked block: key-dependent 34119 bits (`=34119/block`),
public 327743 bits (`=327743/block`), k1 319 / k2 6492 in all 128 records.
Totals: key 4367232, public 41951104, tags 128. Recount l1/l2/tag 128 each;
mismatches []. Formulae: `5*6811+64 = 34119`; `10*32768+63 = 327743`;
f 1.2998502888172847 ≤ 1.3.

## 12. Resources

wall_s 2031.385216 ≤ 2400 (margin 368.6 s, 15.4%); rss_bytes_peak 569614336
≤ 2 GiB (headroom ~2.9×); `resource_stop_fired` false; zero resource_abort
records. Per-record VmPeak/VmSize present in all 128 records
(vm_peak 661312–786044 kB; vm_size 452408–622200 kB; RSS HWM up to the aggregate
peak); the aggregate summary carries wall + RSS by schema design.
Item-8 resolution note (Pre-RESULT): the flagged aggregate-level VmPeak/VmSize
"absence" is a schema misreading — the frozen gate computes solely from
wall/RSS/stop-flag, and the per-record requirement (freeze §5) is met. No
repair possible or needed; no rerun.

## 13. Complete gate table (recomputed vs persisted — all match)

14/14 integrity true, failing list empty: predecessor_construction_identity;
target_population_contract; construction_frozen_before_dev;
dev_coverage_complete (128/128, 8 streams × block 0–15);
streams_disjoint_frozen; orders_valid_k_replay_f_within_budget;
buckets_disjoint_exhaustive; truth_isolation; undetected_zero; nonfinite_zero;
no_unregistered_calls (256 SC / 128 tags); disclosure_recount_exact;
attempt_read_accounting_exact (1/1, opens 1, size 25166822);
resource_limits_met_and_no_abort. Recovery exact≥121/128 true (margin exactly 2);
Wilson LB≥0.90 true (margin +0.0219).

## 14. Classification derivation

Integrity 14/14 true AND recovery true →
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` uniquely
correct (NOT_CONFIRMED would require recovery false; BLOCKED would require an
integrity/resource failure; failing list is empty). Independent Pre-RESULT
review: PASS_WITH_COMMENTS (123/128 recount + Wilson recomputation confirm
CANDIDATE; item-8 resolved as above). This return is candidate evidence only,
not acceptance.

## 15. Bounded scope

Model-sampled replication at N=32768/f≤1.3 ONLY. P16 context is report-only
neutrality, never pooled. Not real-data FER, not held-out FER, not efficiency,
key-rate, scaling, qualification, or promotion evidence. No success language
beyond the frozen `..._REPLICATION_CANDIDATE` label.

## 16. Unrun stages

None — the single authorized gate ran once. Remaining: main-thread acceptance
(separate; owns the STATUS advancement). No rerun, repair, or root reuse is
permitted.

## 17. Provenance and hygiene

Evidence root `operational_replication_gate/`: exactly five files, no sidecars
(`frozen_plan.json` 8486 B, `predecessor_construction_identity.json` 953 B,
`per_block_outcomes.jsonl` 85589 B / 128 lines, `aggregate_summary.json`
6118 B, `report.md` 2955 B). Banned-key walk empty. No `results/` or
`comparison_bench/outputs_comparison/` writes. No TRAIN/genie/BEC/adaptive/
Model-F/HOLD/raw/real/EVAL access. P16 root untouched. No OpenSpec box checked.
No commit/push. HEAD unchanged.
