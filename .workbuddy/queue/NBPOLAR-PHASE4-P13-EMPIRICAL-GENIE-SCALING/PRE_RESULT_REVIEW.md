# Pre-RESULT review — NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING (Tier-Y)

## Verdict: PASS_WITH_COMMENTS

All recomputations reproduce the persisted gate record within benign
floating-point summation order (≤1 ulp, one ~4e-12 BEC-residual case noted
below). Classification
`TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` is correctly derived:
integrity 12/12 true but no N meets the frozen UCB≤0.01 rule. No blocking
issue. Comments C1–C5 are non-blocking follow-ups for the main thread
(STATUS.yaml staleness, ulp notes, wall-overhead note).

Independent reviewer scope: read-only review of the frozen packet, freeze,
Pre-EXECUTE review, the five artifacts under `empirical_genie_scaling_gate/`,
and `empirical_genie_scaling.py` (code-order/constant spot checks only). The
V25 `channel_counts.npz` content was NOT opened (metadata `stat` only). The
gate command was NOT rerun (reads 1/1 + attempts 1/1 already spent). No
Model-F/HOLD/raw/real/EVAL/tag access; no old-root writes; no commit/push.
Only this file was written.

---

## 1. Root inventory + scalar-only audit — PASS

Command:

```
ls -1A .workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/
ls -la ... (sizes); stat -c '%s %y %n' <npz>
```

Raw evidence:

- Files: exactly five —
  `aggregate_summary.json` (8002 B),
  `construction_and_allocations.json` (3572734 B),
  `frozen_plan.json` (6541 B),
  `per_block_genie_residuals.jsonl` (13080 B),
  `report.md` (2839 B). No extras, no sidecars.
- `construction_and_allocations.json` top keys: `cells, frozen_before_first_dev,
  protocol`. `cells` holds exactly `16384, 4096, 8192`; each cell holds
  `bec_report_only, dev_seeds, f, freeze_sha256, k1, k2, k_total, l1_order,
  l2_order, leakage_bits, n, pooled_e1_mean, pooled_e2_mean, pooled_h1_mean,
  pooled_h2_mean, train_blocks, train_impossible, train_residual, train_seeds,
  train_used_l1, train_used_l2` (+ `residual` inside `bec_report_only`).
  `frozen_before_first_dev: true`.
- Banned-payload walk over construction keys (counts/symbols/truth
  vectors/decoder outputs/metric planes/RNG state stems): NONE. Only
  scalar/contract names appear (`counts_path`, `truth_boundary`,
  `truth_isolation`, `p_b_sum`, `p_b_normalized`, `no_zero_bob_column` are
  scalar contract/provenance fields, not payload vectors — verified no list
  payload behind them; the only long lists are the allowed public
  `l1_order/l2_order` (length N) and pooled means (length N)).
- `per_block_genie_residuals.jsonl`: 96 lines; every row keys exactly
  `{block_index, error, n, r_bec, r_empirical, stream_seed}`; row 0 e.g.
  `{"block_index":0,"error":null,"n":4096,"r_bec":12.299968234555678,
  "r_empirical":0.9127248514369684,"stream_seed":2026091870}`; N distribution
  32/32/32; `error` null on all 96 rows (Counter `{'None':96}`); per
  (n, seed) block_index sets all exactly 0..7 (12 groups × 8).

## 2. Preconditions / consumption / NPZ metadata — PASS

Commands: python JSON reads of `aggregate_summary.json:entropy`,
`attempt_read_accounting`, `frozen_plan.json:entropy_expectations`, plus K
floor recomputation under both H spellings.

Raw evidence (recomputed, not copied):

- `h1` rec `0.024280546818678802` vs expected `0.02428054681872374`,
  diff `4.4939746368655165e-14` ≤ 1e-12 → true.
- `h2` rec `0.7767572780789994` vs expected `0.7767572780789994`,
  diff `0.0` → true.
- `total` rec `0.8010378248976782` vs expected `0.8010378248977232`,
  diff `4.5075054799781356e-14` ≤ 1e-12 → true (ratified P7 semantics:
  raw-MLE vs literal; floor-perturbed total `0.8010378249492791` is separate).
- `floor_entropy_change 5.1600945738528026e-11` ≤ 1e-9 → true.
- `column_dev 1.1357581541915351e-13`, `p_b_sum 1.0`; all 7 checks true
  (`conditional_columns_normalized, floor_entropy_change_at_most_1e-9,
  h1/h2/total_matches_literal, no_zero_bob_column, p_b_normalized`).
- Zero-column precondition passes per `no_zero_bob_column: true` (no zero Bob
  column).
- Accounting: allowed 1 / consumed-before 0 / consumed-by-run 1 for both
  reads and attempts; `open_count 1`, `reopen_attempted false`, `retries 0`,
  `retry_after_open false`; `observed_npz_bytes 25166822`,
  `expected_npz_bytes 25166822`, `stat_size_checked true`; loader
  `...formal_ir.v35_algorithm_development.load_v25_channel_counts`,
  `input_mode v25_npz`. Reads 1/1 + attempts 1/1 spent at first open —
  consistent with the freeze consumption point.
- NPZ metadata stat only (never opened):
  `25166822 bytes`, mtime `2026-08-19 01:34:09.691122000 +0800` — unchanged
  from the frozen `EXPECTED_NPZ_BYTES` / freeze §8.

## 3. Allocations / selection / orders / freeze — PASS

Commands: K_total floor recompute from literals (both H spellings);
K1+K2/leakage/f cross-checks; full lexicographic argmin recompute from pooled
risks for ALL three N; permutation + full `(e,h,index)` worst-first verify;
SHA-256 recompute per runner §1128/§1413 construction.

Raw evidence:

- `H1+H2` float64 `0.8010378248977231`; EXPECTED_TOTAL literal
  `0.8010378248977232` (1 ulp). Floors identical:
  N=4096 raw `840.2732420030792`/`840.2732420030794` → 840;
  N=8192 raw `1693.3464840061583`/`1693.3464840061588` → 1693;
  N=16384 raw `3399.492968012317`/`3399.4929680123178` → 3399.
  Persisted `frozen_k_total_from_literals {4096:840, 8192:1693, 16384:3399}` —
  match.
- Per-N (aggregate == construction on every field):
  N=4096 K1+K2 `38+802=840` ✓, f `1.2995836059713857` ≤ 1.3 ✓,
  leakage `5*840+64=4264` ✓, clip `[0,8192]` ✓;
  N=8192 `78+1615=1693` ✓, f `1.299735996169084` ✓, leakage `8529` ✓,
  clip `[0,16384]` ✓;
  N=16384 `152+3247=3399` ✓, f `1.2998121912679332` ✓, leakage `17059` ✓,
  clip `[0,32768]` ✓.
  (C1, non-blocking: recomputing f as `(5K+64)/(N*(H1+H2))` with the float64
  sum gives `1.2995836059713126/1.2997359961690111/1.2998121912678602`,
  i.e. ~7e-14 below persisted — the persisted f uses the literal path; both
  ≤ 1.3, no decision impact.)
- Lexicographic `(residual,K1,K2)` argmin recomputed from frozen TRAIN pooled
  risks (suffix sums over empirical orders) reproduces all three selections
  exactly:
  N=4096 best `(38,802)` resid `0.10927696273202786`
  (neighbours K1=37 → `0.11092684947725502`, K1=39 → `0.11026552515491694`);
  N=8192 best `(78,1615)` resid `0.005622605905980432`
  (K1=77 → `0.005741508619746233`, K1=79 → `0.005712741077877878`);
  N=16384 best `(152,3247)` resid `9.123285118244062e-05`
  (K1=151 → `9.161354593606452e-05`, K1=153 → `9.135748013955336e-05`).
  Persisted TRAIN residuals identical to full precision.
- Orders: `l1_order`/`l2_order` lengths exactly N per cell; all six are exact
  permutations of `range(N)`; full worst-first `(−e,−h,index)` non-decreasing
  verified over all N−1 adjacencies per order (6/6 full-pass, not spot-only).
- Pooled risks finite: all four mean arrays per N finite (e.g. N=4096
  e-min `0.0`, e-max `0.9687499999897988`/`0.96875`; h-max `5.246857883388498`/
  `5.742766024728208`; N=8192/16384 likewise finite).
- Freeze SHA-256 recomputed with the runner's exact canonicalisation
  (`sort_keys, separators=(",",":")` over
  n/k_total/k1/k2/l1_order/l2_order/pooled means) matches persisted for all N:
  4096 `c40e8b1e…f71ccfe` ✓, 8192 `6f444ebf…14cc8b` ✓, 16384 `b5fb574c…d275922` ✓;
  aggregate per-N `freeze_sha256` equals construction ✓;
  `frozen_before_first_dev true` ✓ (construction froze orders/allocation/
  TRAIN residual before the DEV loop per code order TRAIN-pool → select+SHA →
  DEV, Pre-EXECUTE §4-verified; no DEV-based selection possible — DEV loop
  only appends residuals).
- BEC report-only splits: (37,803)/(80,1613)/(166,3233), sums equal K_total,
  eps1 `0.00485610936373576`, eps2 `0.15535145561579988`, lengths N ✓ —
  match the frozen pinned splits. (C2: construction BEC TRAIN residuals
  `3.363831923433267/2.26484026328486/1.2717801865422018` differ from the
  freeze-doc pinned literals `...3437399/...288221/...43192` by ~2–4e-12 —
  summation-order noise, no impact; BEC is report-only regardless.)

## 4. DEV statistics / UCBs / classification / BEC — PASS

Command: recompute per-N mean/sample-std (ddof=1)/min/max + one-sided 95%
Student-t UCB `mean + 1.695518782*std/sqrt(32)` from the 96 JSONL `R` values;
same for the BEC arm; `emp−bec` differences; UCB≤0.01 comparisons.

Raw evidence:

- N=4096 emp: mean `0.827698743150655` ✓ exact;
  std persisted `0.4156658929058898` == numpy ddof=1 exactly
  (naive-python-sum gives `...984`, 1-ulp order noise — C3, benign);
  min `0.11514359942895647` ✓; max `1.7636954144631765` ✓;
  UCB persisted `0.9522855359820204` == numpy-path recompute exactly;
  `UCB ≤ 0.01` → False (margin ~0.94).
- N=8192 emp: mean `0.39684042554673166` ✓; std `0.2972785735520714` ✓
  (== statistics.stdev and numpy; naive loop 1-ulp lower — benign);
  min `0.003468452776927977` ✓; max `1.264753487350557` ✓;
  UCB `0.4859431994053538` ✓ exact; comparison False (margin ~0.48).
- N=16384 emp: mean `0.1932197376646005` ✓; std `0.19774453910014764` ✓;
  min `0.004172203043802836` ✓; max `0.7382396685293214` ✓;
  UCB `0.2524893538319819` ✓ exact; comparison False (margin ~0.24).
- Classification derivation: integrity all-true (see §6) AND candidate set
  empty (`candidate_ns []`, `smallest_candidate_n null`) because ALL THREE
  UCB comparisons are False → label `NOT_CONFIRMED` is the unique correct
  outcome under packet P13-04 (CANDIDATE requires ≥1 N with UCB≤0.01;
  BLOCKED requires an integrity/resource failure — none). Persisted
  `outcome_label TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` ✓;
  `failing_integrity_gates []` ✓.
- BEC report-only recomputed exactly: means
  `18.631744135001654/33.207758990009765/57.155382700913776` ✓;
  UCBs `19.650591422865244/34.646718795027105/58.580859237207626` ✓;
  emp−bec means `-17.804045391850998/−32.81091856446303/−56.96216296324918` ✓.
  Report table matches aggregate to full precision on every column.

## 5. TRAIN/DEV separation — PASS

- Seeds: TRAIN 12
  `1860..1863/1880..1883/1900..1903` == frozen plan ✓;
  DEV 12 `1870..1873/1890..1893/1910..1913` == frozen plan ✓;
  TRAIN∩DEV empty ✓; per-N grouping exact in aggregate, construction and
  JSONL (DEV rows cover exactly the 4 DEV seeds × 8 blocks per N) ✓.
- Counts: TRAIN 8+8+8 (train_blocks 8, train_used_l1/l2 8/8, train_impossible 0
  per cell); DEV 32×3 = 96 blocks ✓.
- TRAIN residual vs DEV mean gap (descriptive only, no interpretation beyond
  the numbers): N=4096 `0.10927696273202786` vs `0.827698743150655`
  (gap `0.718421780418627`); N=8192 `0.005622605905980432` vs
  `0.39684042554673166` (gap `0.3912178196407512`); N=16384
  `9.123285118244062e-05` vs `0.1932197376646005` (gap `0.19312850481341803`).
  In-sample TRAIN optimism noted as numbers only, per instruction.
- No DEV-based selection could have occurred: `frozen_before_first_dev true`,
  freeze SHAs recomputed ✓ (§3), selection replay uses TRAIN-pooled risks only
  (argmin reproduced without touching DEV rows), DEV loop appends residuals.

## 6. Integrity gates (recomputed, not copied) — 12/12 PASS

| gate (frozen order) | recomputed evidence | persisted |
|---|---|---|
| target_population_contract | 7/7 checks true; \|dH1\| 4.49e-14, \|dH2\| 0, \|dTot\| 4.51e-14 ≤1e-12; floor 5.16e-11 ≤1e-9; col dev 1.14e-13 | true ✓ |
| three_n_cells_complete | 3 cells; TRAIN 8+8+8; DEV 32/32/32 = 96 rows; (n,seed,block) 96 unique triples, indices 0..7 per group | true ✓ |
| streams_disjoint_frozen | TRAIN∩DEV ∅; TRAIN/DEV == frozen plan; per-N grouping exact | true ✓ |
| orders_valid_frozen_before_dev | 6/6 permutations; 6/6 full worst-first; frozen flag true; 3/3 SHAs recomputed | true ✓ |
| budget_allocation_reproduced | K floors 840/1693/3399; K1+K2=K; f≤1.3 (1.29958/1.29974/1.29981); leakage 4264/8529/17059 = 5K+64; 3/3 argmins reproduced | true ✓ |
| risks_finite | all 12 pooled arrays finite | true ✓ |
| zero_genie_exceptions | block_errors 0/0/0; train_impossible 0/0/0; 96/96 JSONL errors null | true ✓ |
| truth_isolation | provenance_violations 0 | true ✓ |
| no_unregistered_calls | genie_calls 240 == planned 240 (= 2×(24 TRAIN + 96 DEV)) | true ✓ |
| checkpoint_accounting_consistent | 5 files present; per-block 96 rows reconcile to per-N n=32 summaries (§4 exact); construction↔aggregate fields identical (§3); dev_block_count 96 | true ✓ |
| attempt_read_accounting_exact | 1/1 + 1/1, before 0, open_count 1, no reopen/retry, sizes 25166822==25166822 | true ✓ |
| resource_limits_met_and_no_abort | walls/RSS/VmPeak/VmSize recorded per cell; rss peak 301961216 ≤ 2 GiB; total wall 496.58 s ≤ 1800 s; resource_stop false/reason null | true ✓ |

Failing list recomputed: empty ✓ (`failing_integrity_gates []`,
`integrity_all_pass true`). Partial-fallback path NOT taken: all 96 DEV
blocks + 3/3 N cells complete with the exit-0 completed label persisted in all
five files (no RUNNING partials, no BLOCKED stub path).

## 7. Resources / accounting — PASS

- Per-cell (aggregate, matches report): N=4096 wall `65.04243`, RSS
  `244137984`, VmPeak `470620`, VmSize `440156`; N=8192 wall `139.731162`,
  RSS `244137984`, VmPeak `470620`, VmSize `442716`; N=16384 wall
  `291.806806`, RSS `301961216`, VmPeak `525660`, VmSize `486108`.
- Total wall `496.580679`; cell sum `496.580398`; diff `0.000281` s —
  pre/post-cell overhead, expected (C4, informational only).
- RSS peak `301961216` == max cell HWM ✓; virtual/recorded values far below
  the 2 GiB budget; `resource_stop_fired false`, reason null → no resource
  stop ✓.
- Calls: `genie_calls 240 / planned_genie_calls 240`; `dev_block_count 96`;
  `provenance_violations 0`; checkpoint files consistent (§6).
- Timestamps: `frozen_plan 2026-09-14T17:08:48Z` → aggregate
  `2026-09-14T17:17:15Z` (Δ 507 s vs 496.58 s wall — plausible overhead) ✓.
- Persisted context (exit 0, stderr empty, total wall 496.580679 s) is
  consistent with the completed-label-in-all-files exit-0 path; not
  re-observed (no rerun), accepted as operator record.

## 8. Bounded wording — PASS (report.md read fully)

- Header scopes the table as "construction and DEV genie residuals
  (proxy, not FER)"; per-N wording carries the proxy label.
- Scope footer (verbatim): "frozen V25 TRAIN target-population
  empirical-genie construction/rate development signal only; not held-out or
  real frame FER, efficiency, key rate, scaling, qualification or promotion;
  BEC results and empirical-minus-BEC differences are report-only; undetected
  has no meaning in this tag-free gate and no success bucket exists."
  The FER/efficiency/key-rate/qualification/promotion/undetected grep hits are
  all inside explicit denials — correct.
- `residual_scope`/`claim_scope`/`truth_boundary` in frozen_plan carry the
  same proxy-only wording ("not operational FER, not a real-channel result
  and not proof of any minimum N"; "no tag, no Toeplitz master").
- ABSENT as required: ε_eff-type back-inference, HOLD framing, EVAL/Model-F
  references, minimum-N proof language, qualification/promotion claims. The
  single "toeplitz" hit is the "no Toeplitz master" denial. Single-draw
  variance is handled by the frozen UCB design, not by extra claims.
- No candidate/promotion language: label NOT_CONFIRMED, smallest null.

## 9. Tests / scope / git — PASS

Commands (pinned interpreter, fresh /tmp basetemps, `-q -p no:cacheprovider`):

```
.../.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p13-preresult-focused comparison_bench/tests/test_nbpolar_empirical_genie_scaling.py
→ 20 passed in 7.59 s
.../.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p13-preresult-allnbpolar comparison_bench/tests/test_nbpolar_*.py
→ 305 passed in 152.03 s
```

- Expectation 20 + 305 met exactly.
- `git log --oneline -1` → `ab173f2a` (HEAD unchanged, no commit).
- `git status --porcelain`: 17 tracked mods identical to the Pre-EXECUTE
  baseline (cumulative P3..P13, e.g. tasks.md +553 spans P3..P13 — baseline
  artifact, not P13 scope creep) + additive untracked P13 set
  (`empirical_genie_scaling.py`, `test_nbpolar_empirical_genie_scaling.py`,
  phase4-p13 spec dir, P13 queue root incl. the new gate output root). No
  new tracked modification from the gate run; accepted P7–P12/X-root modules
  untouched by this wave beyond the pre-existing baseline; no old-root writes
  (`results/`, `comparison_bench/outputs_comparison/` unmodified — gate
  output confined to the authorised queue root).
- No rerun of the gate; no writes outside this review file + /tmp basetemps.

---

## Blocking Issues

- None.

## Non-Blocking Suggestions

- (C1) f spelling: persisted f uses the literal path; float64-sum
  recomputation differs ~7e-14. Both ≤ 1.3. No action; noted for provenance.
- (C2) BEC TRAIN residuals in construction differ ~2–4e-12 from the
  freeze-doc pinned literals (summation order). Report-only; no action.
- (C3) N=4096/N=8192 sample-std naive-loop recompute differs 1 ulp from
  persisted; numpy ddof=1 path reproduces exactly (N=4096 UCB included).
  Benign float associativity; UCB margins (0.94/0.48/0.24) make the
  comparisons robust. No action.
- (C4) Total wall exceeds cell-sum by 0.000281 s (run overhead). Informational.
- (C5) `STATUS.yaml` still shows `IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`
  with reads/attempts 0/1 — the spent 1/1 accounting lives in the gate
  artifacts. Main thread should roll STATUS forward (reads_used 1,
  attempts_used 1, result NOT_CONFIRMED, reviews recorded) at acceptance;
  reviewer did not touch it (read-only).

## Checklist

- [x] Matches OpenSpec spec (packet P13-01..P13-07 vs phase4-p13 delta, verified at Pre-EXECUTE and re-confirmed via artifact semantics)
- [x] Tests pass (20 focused + 305 NB-Polar, pinned interpreter, fresh basetemps)
- [x] No scope creep (additive P13 set; accepted modules/old roots untouched; output confined to authorised root)
- [x] docs/decision-log.md or docs/troubleshooting.md needs update? — No new failure mode observed; nothing to add (C5 is a STATUS roll-forward, not a troubleshooting entry).

## Closure statements

- The V25 `channel_counts.npz` content was NOT reopened during this review
  (metadata `stat` size `25166822`, mtime `2026-08-19` only; the single
  artifact read belongs to the gate run).
- The gate was NOT rerun (reads 1/1 + attempts 1/1 already spent; 240/240
  genie calls, 96 DEV blocks and 3/3 cells complete with the exit-0 completed
  label — no remaining attempt to spend).
- No files were modified except this `PRE_RESULT_REVIEW.md`; no commit/push
  was made; HEAD remains `ab173f2a`.
- Findings above are the reviewer's independent recomputations; main-thread
  acceptance remains separate per AGENTS.md §4.1.

(End of file)
