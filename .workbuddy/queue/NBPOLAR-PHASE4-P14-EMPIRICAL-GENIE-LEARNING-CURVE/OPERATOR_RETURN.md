# OPERATOR_RETURN — NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE (Tier-Y, single gate, negative)

Packet: `.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/`
Result label: `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` (not a candidate, not blocked).
Main-thread acceptance is pending; this return is not an acceptance and makes no recommendation
(the more-TRAIN / regularization / larger-N choice is packet-reserved to the main thread).

## 1. Mission

At P13's N=16384 point, determine whether failure to reach the f=1.3 residual target
(P13 DEV UCB 0.2524893538319819, far above 0.01) was materially caused by constructing
from only eight TRAIN blocks. Build nested 8/16/32/64/128-block constructions from one
128-block TRAIN sequence and evaluate all five on the same independent 32-block DEV set.
Model-sampled genie construction diagnostic only — not operational FER, not real-data
qualification.

## 2. Implementation and tests

- Thin runner `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_learning_curve.py`:
  single stream-major TRAIN pass with running sums (prefix-B means at `used == B`, no block
  revisited), five-way DEV scoring from one decode per DEV block via shared P13
  `residual_for_orders`, paired differences through P13's `student_t_ucb_95` alias, no BEC arm,
  no tag/Toeplitz anywhere. Accepted P7/P11/P13 modules called, never changed.
- Focused suite `comparison_bench/tests/test_nbpolar_empirical_genie_learning_curve.py`:
  15/15 pass (K pin, matrix constants, P13-helper identity, nested/call-budget/stream-order,
  order-K replay, five-way + paired-UCB + report-only recompute, refusals, checkpoint-resume
  refusal, accounting, precondition zero-genie BLOCKED stubs, MemoryError classification,
  forbidden-token scan). Full NB-Polar suite 320/320 green, no regressions.

## 3. Pre-run checks

- Independent Pre-EXECUTE review: PASS (three non-blocking observations, no pre-execution repair).
- Gate root absent at start; V25 NPZ stat-only 25166822 bytes, content never opened pre-run;
  frozen seeds 1930..1943 fresh and disjoint from all P7–P13/probe/test seeds.
- K_total = 3399 verified from literals (`floor((1.3*16384*0.8010378248977232-64)/5)`,
  raw 3399.4929680123178); wall envelope adequate (~1170 s projected vs 1800 s cap).

## 4. Exact command (executed once)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_learning_curve --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 16384 --train-seeds 2026091930 2026091931 2026091932 2026091933 2026091934 2026091935 2026091936 2026091937 --train-blocks-per-stream 16 --prefix-blocks 8 16 32 64 128 --dev-seeds 2026091940 2026091941 2026091942 2026091943 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate
```

Exit 0, stderr empty, wall 1110.16709 s. No rerun, no retry, no tuning.

## 5. Preconditions (7/7 true)

|dH1| 4.4939746368655165e-14, |dH2| 0.0, |dTot| 4.5075054799781356e-14 (all ≤1e-12);
floor guard 5.1600945738528026e-11 (≤1e-9); column dev 1.1357581541915351e-13.

## 6. Consumption

Reads 1/1, attempts 1/1, open_count 1, before 0/0, retries 0, no reopen, no retry-after-open;
V25 1M TRAIN NPZ 25166822 B read-only (size/mtime 2026-08-19 unchanged).
Genie calls 320/320 (2 × (128 TRAIN + 32 DEV), each block decoded once per layer);
0 block errors, 0 provenance violations. No reopen, no rerun.

## 7. Nested construction and five allocations

K_total = 3399, leakage 5*3399+64 = 17059, f = 1.2998121912679332 (≤1.3).
Orders frozen before first DEV; nested exact (telescoping diffs ≥ −4e-323);
streams disjoint stream-major; TRAIN ∩ DEV ∅; no P13 merge (P13 B=8 reference only).

| B | K1 | K2 | TRAIN residual |
|---|---|---|---|
| 8 | 158 | 3241 | 5.3882981160102705e-05 |
| 16 | 161 | 3238 | 0.0002739494046524113 |
| 32 | 162 | 3237 | 0.0013067725980560572 |
| 64 | 162 | 3237 | 0.0036843863984939752 |
| 128 | 173 | 3226 | 0.013279461298516686 |

## 8. Per-prefix DEV residuals (n=32, t factor 1.695518782, df=31)

| B | mean | std | min | max | UCB | UCB≤0.01 |
|---|---|---|---|---|---|---|
| 8 | 0.1175773969604019 | 0.18328617696455765 | 0.00023161951066219544 | 0.6632266438755844 | 0.17251343416734777 | False |
| 16 | 0.13176399133297984 | 0.18728900823240302 | 0.00015639852900284357 | 0.6981597350727797 | 0.18789978997914214 | False |
| 32 | 0.1060391737357177 | 0.17563973337252425 | 0.0002421531531953125 | 0.6972184077530478 | 0.15868335611416776 | False |
| 64 | 0.08983984405791562 | 0.16445710274458678 | 0.0004354717782820705 | 0.8070449161693778 | 0.13913227660764454 | False |
| 128 | 0.1419810706809162 | 0.19735260988460465 | 0.00017760231322272446 | 0.806151592316756 | 0.2011332146072146 | False |

## 9. Paired differences (mean / std / UCB)

Vs R_8: R_16−R_8 (0.014186594372577927 / 0.17294151558954643 / 0.06602204477258328);
R_32−R_8 (−0.011538223224684209 / 0.1348726212270291 / 0.028886905721941962);
R_64−R_8 (−0.02773755290248629 / 0.11712473187364603 / 0.0073680329885239225);
R_128−R_8 (0.024403673720514288 / 0.16989973009547454 / 0.07532741520801287).
Adjacent steps: R_32−R_16 (−0.025724817597262136 / 0.1031757123802204 / 0.005199853690245681);
R_64−R_32 (−0.01619932967780208 / 0.08917824709781177 / 0.010529906436730147);
R_128−R_64 (0.05214122662300058 / 0.12867194063944914 / 0.09070783669434054).

## 10. Report-only diagnostics (transcribed without interpretation)

- Spearman_vs_128 L1/L2: 8: 0.9929179557129755/0.9976659246808045;
  16: 0.9942806123577369/0.9984572002774081; 32: 0.9958371560141577/0.9990437934812538;
  64: 0.9979087564465174/0.9994517134307482.
- topK overlap vs 128 (at frozen B=128 depths K1=173/K2=3226) L1/L2:
  8: 0.930635838150289/0.9866707997520149; 16: 0.9479768786127167/0.9885306881587105;
  32: 0.9479768786127167/0.9891506509609423; 64: 0.9595375722543352/0.9910105393676379.
- Allocation movement (K1,K2): 8: (158,3241); 16: (161,3238); 32: (162,3237);
  64: (162,3237); 128: (173,3226).
- vs-R8 counts (improved/regressed/tied): 8: 0/0/32; 16: 19/13/0; 32: 19/13/0;
  64: 20/12/0; 128: 17/15/0.

## 11. Resources

wall 1110.16709 s (run clock; resources.wall_s 1110.717597, Δ finalization);
rss hwm 283115520 B; VmPeak 508308 kB; VmSize 462600 kB (authoritative per Pre-EXECUTE
instruction; WSL2 ru_maxrss phantom disregarded — rss sat below VmPeak on this run).
No resource stop; wall ≈ 62% of the 1800 s budget. Accounting/checkpoint consistent.

## 12. Gates (13/13 true, failing list empty)

target_population_contract, one_n_cell_complete, nested_prefixes_exact,
streams_disjoint_frozen, orders_valid_frozen_before_dev, budget_allocation_reproduced,
risks_finite, zero_genie_exceptions, truth_isolation, no_unregistered_calls,
checkpoint_accounting_consistent, attempt_read_accounting_exact,
resource_limits_met_and_no_abort — all true (independently recomputed by Pre-RESULT review).

## 13. Classification derivation

Integrity 13/13 true (not blocked) AND B=128 DEV UCB 0.2011332146072146 > 0.01
(not a candidate) → `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`
is uniquely correct. Independent Pre-RESULT: PASS_WITH_COMMENTS (all non-blocking,
numbers verified). No rerun is permitted (read 1/1 + attempt 1/1 spent).

## 14. Mission-question descriptive answer (numbers only, no causal overclaim)

The learning curve is FLAT: B=128 (mean 0.1419810706809162, UCB 0.2011332146072146)
is not better than B=8 (mean 0.1175773969604019, UCB 0.17251343416734777);
paired R_128−R_8 mean +0.024403673720514288. More TRAIN blocks did not move the DEV
residual toward the 0.01 target within this gate.

## 15. Bounded scope

Genie union-bound construction proxy only. Not operational FER, not a real-channel result,
not proof of any minimum N or TRAIN size; no held-out/real FER, efficiency, key-rate,
scaling, qualification or promotion claim. No recommendation on more TRAIN,
regularization, or larger N — that choice belongs to the main thread.
No qualification or promotion of any kind.

## 16. Unrun stages and provenance

Unrun stages: none — the single authorized gate executed once. Remaining: main-thread
acceptance only. Evidence root `empirical_genie_learning_curve_gate/` (five files, read-only).
No OpenSpec box checked; no code/artifact/old-root touched; no commit/push; NPZ untouched.
