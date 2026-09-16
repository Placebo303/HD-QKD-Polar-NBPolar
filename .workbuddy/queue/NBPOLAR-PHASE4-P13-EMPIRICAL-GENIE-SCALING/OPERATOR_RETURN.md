# OPERATOR_RETURN — NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING (Tier-Y)

Result: `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` (valid scientific
negative; not a candidate, not blocked). Main-thread acceptance remains
separate; this return authorizes and accepts nothing.

## 1. Mission

Pre-P12-retry empirical-genie check at N=2^12–2^14 (N=4096/8192/16384):
determine whether the V25 1M TRAIN target model reaches the planning budget
`f<=1.3` when construction and rate allocation are learned from empirical
genie risks rather than a same-entropy BEC surrogate. Model-sampled
construction/rate development gate only — not operational FER, not real-data
qualification.

## 2. Implementation / tests (Wave-A, frozen, unchanged by the gate run)

- Thin runner `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_scaling.py`
  reuses accepted P7 loading/support/precondition pattern, the accepted
  `genie_conditionals` choke point (called, never changed), accepted P11
  chunked SC (`chunk_rows=512` contract-checked pre-open, `sc_decode` never
  called directly), and P12 f-budget/BEC helpers (`budget_k_total`,
  `allocate_layer_ks` imported, those files untouched). No tag/Toeplitz
  master anywhere in this gate.
- Focused `comparison_bench/tests/test_nbpolar_empirical_genie_scaling.py`:
  20/20 pass. Full NB-Polar suite 305/305 green (both at Pre-EXECUTE and at
  Pre-RESULT, pinned interpreter, fresh basetemps). Full
  `comparison_bench/tests` triage (2117 passed / 468 failed, all failures in
  legacy LDPC/nonbinary/v-series files, zero in any `test_nbpolar_*`) is
  pre-existing/environmental, reported not fixed.
- Freeze: `P13_FREEZE.md` + `P13_IMPLEMENTATION_NOTES.md` (this doc
  authorizes nothing).

## 3. Pre-run checks

- Independent Pre-EXECUTE review: **PASS** (10/10 checks; R1 seed-numeral
  overlap 2026091900..1903 ratified FRESH as test-local-only numerals; R2
  262-vs-305 count ratified cosmetic; R3 dirty-worktree ratified wave-scoped
  additive; R4 partial-report tolerance ratified).
- Target root `empirical_genie_scaling_gate/` verified absent; NPZ stat-only
  25166822 B; reads/attempts 0/1; HEAD `ab173f2a` unchanged.

## 4. Exact command (verbatim, from `frozen_plan.json:frozen_command`)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_scaling --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 4096 8192 16384 --train-seeds 2026091860 2026091861 2026091862 2026091863 2026091880 2026091881 2026091882 2026091883 2026091900 2026091901 2026091902 2026091903 --dev-seeds 2026091870 2026091871 2026091872 2026091873 2026091890 2026091891 2026091892 2026091893 2026091910 2026091911 2026091912 2026091913 --train-blocks-per-stream 2 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate
```

## 5. Execution outcome

- Single gate executed once: **exit 0, stderr empty**, total wall
  496.580679 s (per `aggregate_summary.json`; accepted as operator record,
  not re-observed — no rerun).
- V25 1M TRAIN NPZ 25166822 B read-only (size/mtime unchanged:
  `2026-08-19 01:34:09.691122000 +0800`).
- Preconditions 7/7 true: H1 rec `0.024280546818678802` vs
  `0.02428054681872374` (diff 4.49e-14 ≤ 1e-12); H2 exact
  (`0.7767572780789994`, diff 0.0); total rec `0.8010378248976782` vs
  `0.8010378248977232` (diff 4.51e-14 ≤ 1e-12); floor guard
  `5.1600945738528026e-11` ≤ 1e-9; column dev `1.1357581541915351e-13`;
  `p_b_sum 1.0`; no zero Bob column.
- Consumption: reads 1/1, attempts 1/1 (`open_count` 1, `reopen_attempted`
  false, `retries` 0, `retry_after_open` false). No reopen/retry/rerun.

## 6. Allocations + TRAIN diagnostics (frozen before first DEV)

| N | K_total | K1 | K2 | TRAIN residual | f | leakage_bits |
|---:|---:|---:|---:|---|---|---:|
| 4096 | 840 | 38 | 802 | 0.10927696273202786 | 1.2995836059713857 | 4264 |
| 8192 | 1693 | 78 | 1615 | 0.005622605905980432 | 1.299735996169084 | 8529 |
| 16384 | 3399 | 152 | 3247 | 9.123285118244062e-05 | 1.2998121912679332 | 17059 |

TRAIN 8+8+8 blocks, DEV 32×3=96 (`dev_block_count` 96, `block_errors` 0).
Orders lengths N per cell, exact permutations, full worst-first
`(e,h,index)` 6/6; `frozen_before_first_dev` true; freeze SHAs recomputed
match (4096 `c40e8b1e…f71ccfe`, 8192 `6f444ebf…14cc8b`, 16384
`b5fb574c…d275922`).

## 7. Per-N DEV empirical residuals (decision arm; t-factor 1.695518782, df=31)

| N | mean | std (sample) | min | max | UCB 95% | UCB≤0.01 |
|---:|---|---|---|---|---|---|
| 4096 | 0.827698743150655 | 0.4156658929058898 | 0.11514359942895647 | 1.7636954144631765 | 0.9522855359820204 | False |
| 8192 | 0.39684042554673166 | 0.2972785735520714 | 0.003468452776927977 | 1.264753487350557 | 0.4859431994053538 | False |
| 16384 | 0.1932197376646005 | 0.19774453910014764 | 0.004172203043802836 | 0.7382396685293214 | 0.2524893538319819 | False |

`candidate_ns` [], `smallest_candidate_n` null.

## 8. BEC controls (report-only, transcribed without interpretation)

- Means: 18.631744135001654 / 33.207758990009765 / 57.155382700913776.
- UCBs: 19.650591422865244 / 34.646718795027105 / 58.580859237207626.
- emp−bec means: −17.804045391850998 / −32.81091856446303 /
  −56.96216296324918.
- Report-only splits (37,803) / (80,1613) / (166,3233); same DEV rows,
  zero extra SC calls.

## 9. Resources (per cell wall_s / RSS HWM / VmPeak / VmSize)

- N=4096: 65.04243 / 244137984 / 470620 / 440156.
- N=8192: 139.731162 / 244137984 / 470620 / 442716.
- N=16384: 291.806806 / 301961216 / 525660 / 486108.
- Total wall 496.580679 s ≤ 1800 s; RSS peak 301961216 ≤ 2 GiB; no
  resource stop (`resource_stop_fired` false).

## 10. Accounting / checkpoints

- `genie_calls` 240 / planned 240 (= 2×(24 TRAIN + 96 DEV));
  `provenance_violations` 0; checkpoint consistent (96 JSONL rows reconcile
  to per-N n=32 summaries; construction↔aggregate fields identical).
- Five files, no sidecars: `frozen_plan.json` (6541 B),
  `construction_and_allocations.json` (3572734 B),
  `per_block_genie_residuals.jsonl` (13080 B, 96 lines),
  `aggregate_summary.json` (8002 B), `report.md` (2839 B).

## 11. Gates — 12/12 true, failing list empty

`target_population_contract`, `three_n_cells_complete`,
`streams_disjoint_frozen`, `orders_valid_frozen_before_dev`,
`budget_allocation_reproduced`, `risks_finite`, `zero_genie_exceptions`,
`truth_isolation`, `no_unregistered_calls`,
`checkpoint_accounting_consistent`, `attempt_read_accounting_exact`,
`resource_limits_met_and_no_abort` — all true (independently recomputed).

## 12. Classification derivation

Integrity 12/12 true BUT no registered N meets the frozen UCB≤0.01 rule
(UCBs 0.952/0.486/0.252, margins ~0.94/0.48/0.24) → per packet P13-04 the
unique correct label is
`TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` (CANDIDATE requires ≥1
N with UCB≤0.01; BLOCKED requires an integrity/resource failure — none).

## 13. Independent Pre-RESULT review

**PASS_WITH_COMMENTS** (all non-blocking, numbers verified): C1 f-spelling
~7e-14 literal-path note; C2 BEC TRAIN residuals ~2–4e-12 summation-order
note; C3 1-ulp std note (numpy ddof=1 reproduces exactly); C4 0.000281 s
cell-sum overhead note; C5 STATUS roll-forward note (closed by this
return). Tests re-run 20 + 305 green; HEAD `ab173f2a`; no rerun, no
commit/push.

## 14. User-stated interpretive guards (main-thread bounds, recorded verbatim)

- (1) ε_eff≈0.115 is currently only a scenario hypothesis back-inferred
  from small-N behavior, not established;
- (2) higher HOLD entropy means the fixed TRAIN disclosure is only
  ≈f=1.23 relative to HOLD (less redundancy) — not numerically f≈1.37.

These are main-thread bounds, not extended here.

## 15. Bounded scope

Genie union-bound construction proxy only; not operational FER, not a
real-channel result, not proof of any minimum N. BEC results and
empirical-minus-BEC differences are report-only. No tag/Toeplitz master;
undetected has no meaning in this gate and no success bucket exists. No
held-out/real FER, efficiency, key-rate, scaling, qualification or
promotion claim either way. No qualification/promotion of any P12
successor.

## 16. Unrun stages / closeout

Unrun stages: none — the single authorized attempt is spent (reads 1/1,
attempts 1/1). Next gate: MAIN_THREAD_ACCEPTANCE (pending; this return is
not an acceptance). No OpenSpec box checked. No code/artifact/old-root
touched; NPZ untouched. No commit/push.
