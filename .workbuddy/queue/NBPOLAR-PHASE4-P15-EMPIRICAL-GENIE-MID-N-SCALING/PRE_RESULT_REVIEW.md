# Pre-RESULT review — NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING

Independent reviewer (wrote no code, froze no plan, ran no gate).
Read-only except this file. NPZ content never reopened (metadata `stat`
only). Gate command never rerun (reads 1/1 + attempts 1/1 already spent).

## Verdict: PASS

All eight recomputation blocks reproduce the persisted records within the
Pre-EXECUTE-bound tolerance (absolute ≥1e-9 for mean/std/UCB/TRAIN-residual;
exact elsewhere). Classification derives as NOT_CONFIRMED. Bounded wording
holds. Tests re-run green (15 focused + 335 full). Scope clean. Two
non-blocking observations at the end (reviewer-side shortcut lesson +
stale STATUS.yaml hygiene).

---

## 0. Commands used (all read-only; pinned interpreter)

- `ls -1A empirical_genie_mid_n_gate/` → exactly the five frozen files.
- `stat -c 'size=%s mtime=%y' <counts npz>` → metadata only.
- Python recomputations via
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` reading only the
  five gate artifacts (json/jsonl/md) — raw numbers below.
- `rg` token scans over artifacts + runner (no BEC/df=31 functional use).
- `TMPDIR=/tmp/p15-preres-tmp ... pytest
  comparison_bench/tests/test_nbpolar_empirical_genie_mid_n.py -q
  -p no:cacheprovider --basetemp=/tmp/p15-preres-base/focused` → 15 passed.
- `... pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider
  --basetemp=/tmp/p15-preres-base/full` → 335 passed.
- `git status --porcelain`, `git rev-parse HEAD` → `ab173f2a…` unchanged.

---

## 1. Root inventory + scalar-only audit — PASS

`ls -1A` of `empirical_genie_mid_n_gate/` returns exactly:

- `aggregate_summary.json`
- `construction_and_allocations.json`
- `frozen_plan.json`
- `per_block_genie_residuals.jsonl`
- `report.md`

No extras, no sidecars, no hidden files. Matches `frozen_plan.json`
`output_files` (lines 91–97) verbatim.

`per_block_genie_residuals.jsonl`: 32 rows; per-N counts
`{32768: 16, 65536: 16}`. Every row carries exactly the frozen keys
`{block_index, error, n, r_empirical, resources, stream_seed}` with
`resources = {rss_bytes_hwm, vm_peak_kb, vm_size_kb, wall_s}`; all 32
`error` values are null. No `counts`/symbols/truth/decoder-output/
metric-plane/RNG-state keys in any JSON artifact or jsonl record (naive
substring walk flags only `counts_path` — the NPZ path string — and
`p_b_sum`/`p_b_normalized` scalar check names, both allowed scalars, not
arrays). Construction file holds only public orders + pooled mean-risk
vectors + scalars per the packet (`l1_order/l2_order` length N,
`pooled_e1/h1/e2/h2_mean` length N, `k_total/k1/k2/train_residual/
leakage_bits/f/freeze_sha256/seeds/diagnostic stability`), as specified.

Row min/max match summary stats exactly:

- N=32768: row min `4.452207734151337e-06` == summary min; row max
  `0.1247046397723417` == summary max.
- N=65536: row min `2.4939197373896604e-09` == summary min; row max
  `0.43377941496412364` == summary max.

---

## 2. Preconditions + consumption — PASS (recomputed, not copied)

Persisted `entropy` block vs literals, absolute deviations:

- H1 `0.024280546818678802` vs expected `0.02428054681872374`:
  d = `4.4939746368655165e-14` ≤ 1e-12 ✓
- H2 `0.7767572780789994` vs expected `0.7767572780789994`: d = `0.0` ✓
- total `0.8010378248976782` vs expected `0.8010378248977232`:
  d = `4.5075054799781356e-14` ≤ 1e-12 ✓
- floor guard: `floor_entropy_change = 5.1600945738528026e-11` ≤ 1e-9 ✓
  (`floor_total 0.8010378249492791`); `column_dev =
  1.1357581541915351e-13` ≤ 1e-12 ✓; `p_b_sum = 1.0` exact ✓.
- All 7 precondition checks true (ratified semantics).

Consumption (`attempt_read_accounting`): reads consumed 1/1, attempts
consumed 1/1, `open_count 1`, `reopen_attempted false`, `retries 0`,
`retry_after_open false`; `observed_npz_bytes = expected_npz_bytes =
25166822`; `stat_size_checked true`; genie calls 128/128; `dev_block_count
32`; `provenance_violations 0`.

NPZ metadata (stat only, never opened): `size=25166822`,
`mtime=2026-08-19 01:34:09.691122000 +0800` — size matches
expected/observed; mtime unchanged from the frozen August-19 artifact.

---

## 3. Allocations + orders + seeds — PASS

K_total recomputed from both float64 spellings of H:

- N=32768: raw `6811.785936024635` (EXPECTED_TOTAL) /
  `6811.785936024634` (literal sum) → floor **6811** both; leakage
  `5*6811+64 = 34119`.
- N=65536: raw `13636.37187204927` / `13636.371872049267` → floor
  **13636** both; leakage `5*13636+64 = 68244`.

`K1+K2=K_total`: 314+6497=6811 ✓; 607+13029=13636 ✓.
`f` (runner formula `leakage/(n*h_measured)`, code line 1056) reproduces
bit-exact: `1.2998502888173578` / `1.2999645814656315`; both ≤ 1.3 ✓.
(Reviewer note: comparing against the EXPECTED literal instead of the
measured total differs by 7.3e-14 — float-association noise, not a
discrepancy; the code path uses measured h and matches exactly.)

Lexicographic `(residual,K1,K2)` argmin rescanned over the full feasible
range with the exact code-path residual (`g1[k1:].sum()+g2[k2:].sum()`)
for BOTH N:

- N=32768: argmin K1=314, K2=6497, residual
  `1.1128237904570182e-06` — bit-identical to persisted.
- N=65536: argmin K1=607, K2=13029, residual
  `1.1015630768662632e-10` — bit-identical to persisted.
- Window neighbours confirm local minimality (N=65536: K1=606 →
  `1.1032287583478961e-10`, K1=608 → `1.1031472957334643e-10`, both above
  the persisted `1.1015630768662632e-10`).

Orders: all four (`l1/l2` × both N) have length N and are exact
permutations (`sorted == range(n)`); full worst-first `(e,h,index)`
descending sort verified with zero violations; head `(e,h) =
(0.96875, 5.0)` vs tail `(0.0, 0.0)` as expected.

Freeze SHA recomputed (SHA-256 over the frozen key set incl. pooled
means, excl. stability) matches both cells:
`901644d3…5588b` (32768), `f2550ddf…68fca` (65536).
`frozen_before_first_dev: true`; per-N agg↔construction cross-checks
(K/K1/K2/f/leakage/residual/seeds/SHA) all identical.

N-to-seed grouping exact: TRAIN
`[1960,1961,1962,1963,1980,1981,1982,1983]`, DEV
`[1970,1971,1972,1973,1990,1991,1992,1993]`; per-N slices as frozen;
TRAIN∩DEV = ∅ within each N and across N; TRAIN sets disjoint across N;
DEV sets disjoint across N; jsonl seeds match (4 blocks each).

---

## 4. DEV statistics + classification — PASS

Recomputed from the 32 jsonl `r_empirical` values
(`math.fsum`/N + `statistics.stdev`, UCB factor `1.753050356`, /sqrt(16)=4):

- N=32768: mean `0.019146193040229846` (d=0.0), std
  `0.03822701382375279` (d=0.0), UCB `0.035899663088366535` (d=0.0);
  UCB≤0.01 → False.
- N=65536: mean `0.028768524223564552` (d=0.0), std
  `0.10806211430369776` (d=0.0), UCB `0.07612810621111707` (d=0.0);
  UCB≤0.01 → False.

Bit-exact agreement (differences `0.0`, far inside the ≥1e-9 binding).
`candidate_ns []` + `smallest_candidate_n null` recomputed (no UCB ≤
0.01) match persisted; integrity all-true with empty candidate set derives
`TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` == persisted
`outcome_label` (code lines 1203–1226 implement exactly this rule).

df=31 factor `1.695518782` / `df31|DF31|df=31` / `ucb_95_t31` are textually
absent from ALL five artifacts; the runner uses only `T_FACTOR_DF15_95 =
1.753050356` with `count==16` gating (lines 182, 466–468). (P13's
`empirical_genie_scaling.py` df=31 helper is that gate's own frozen
apparatus, untouched and unimported for statistics.)

---

## 5. Order-stability diagnostics — PASS (diagnostic-only, transcribed)

Both cells carry `order_stability_spearman_vs_pooled.diagnostic_only =
true`. Excluded from the freeze SHA (code lines 1069–1078) and never read
by any gate or the classifier (gates §§1287–1481; classification
1203–1205 reads only `ucb_95_t15`). Values transcribed without
interpretation:

- N=32768 L1: `[0.9970431450178441, 0.9968924022701393,
  0.9956017020452883, 0.9974631680735477]`; L2:
  `[0.9990702995474275, 0.9982176182070814, 0.9987523931676809,
  0.9985244829095918]`.
- N=65536 L1: `[0.997466841066661, 0.9976045353679233,
  0.9974054377210492, 0.9978767088027952]`; L2:
  `[0.9986463347003226, 0.9986834310390468, 0.9987121879317712,
  0.9985987388694616]`.
  (Packet context cited ~0.9956–0.9979 / ~0.9982–0.9991 — consistent.)

---

## 6. Integrity gates — PASS (all 12 recomputed from records)

| gate | recomputed | persisted | match |
|---|---|---|---|
| target_population_contract | True | True | ✓ |
| two_n_cells_complete | True | True | ✓ |
| streams_disjoint_frozen | True | True | ✓ |
| orders_valid_frozen_before_dev | True | True | ✓ |
| budget_allocation_reproduced | True | True | ✓ |
| risks_finite | True | True | ✓ |
| zero_genie_exceptions | True | True | ✓ |
| truth_isolation | True | True | ✓ |
| no_unregistered_calls | True | True | ✓ |
| checkpoint_accounting_consistent | True | True | ✓ |
| attempt_read_accounting_exact | True | True | ✓ |
| resource_limits_met_and_no_abort | True | True | ✓ |

Recomputation basis (independent of persisted booleans): precondition
literals/tolerances; 2 cells × (16 TRAIN + 16 DEV, 0 block errors, 32
jsonl rows, null errors); exact seed grouping + disjointness; order
permutation + SHA re-derivation; K_total floors + K1+K2 + leakage formula
+ f (measured-h, bit-exact) + leakage inequality + exact-path argmin;
finite TRAIN/DEV risks; 0 impossible + 0 provenance violations; 128/128
calls with 32 DEV rows; 5 files present + jsonl line count == dev records
+ accounting exactness; wall/RSS envelopes + no resource stop.
`failing_integrity_gates: []` confirmed empty; `integrity_all_pass true`
consistent. (Reviewer's first `budget_allocation_reproduced` draft used
the EXPECTED literal for f and read False by 7.3e-14; the runner's
measured-h formula — code line 1056 — reproduces bit-exact. Gate holds.)

Partial-fallback path NOT taken: outcome is the exit-0
`..._NOT_CONFIRMED` label (not `BLOCKED(...)`); all 64 blocks complete
(32 TRAIN + 32 DEV), `train_used_l1/l2 = 16/16` per N, `train_impossible
0`, `block_errors 0`, 128/128 genie calls. No MemoryError/resource stub
shape present.

---

## 7. Resources + accounting — PASS

- Wall: total `1620.511243 s` vs cell sum `569.717255 + 1050.793743 =
  1620.510998` (delta `2.45e-4` s finalize overhead) ✓; within 2100 s
  (headroom 479.5 s, margin 1.30×).
- RSS HWM peak `1033293824 B` == max cell HWM ✓; 0.481× of the 2 GiB
  limit (`2147483648`).
- VmPeak/VmSize (authoritative, `/proc`): 811928/693720 kB (32768),
  1241560/1025752 kB (65536); max 1241560 KiB ≤ 2097152 KiB ✓.
- `ru_maxrss` phantom check: it materialized — `rss_bytes_hwm` IS
  `ru_maxrss×1024` (code `_peak_rss_bytes`, lines 400–403, via
  `_cell_resource_record`), recorded per block and per cell; VmPeak/VmSize
  come from `/proc/self/status`. Both families present; the resource gate
  itself checks wall + `ru_maxrss` + stop-None (lines 1460–1467).
- 128/128 genie calls; checkpoint consistency (5 files on disk, jsonl 32
  lines == 32 dev records, accounting exact) ✓.

---

## 8. Bounded wording — PASS (report.md read fully, 50 lines)

- Genie-proxy-only framing throughout: title-adjacent header, per-N table
  headed “(proxy, not FER)”, and the closing Scope paragraph stating
  target-population development signal only — not held-out/real-frame
  FER, efficiency, key rate, scaling, qualification or promotion; UCB is
  a genie construction proxy, not an FER threshold or proof of any
  minimum N; `undetected` meaningless, no success bucket.
- No BEC arm: token `bec`/`BEC` absent from all three text artifacts.
  `toeplitz` occurs once, inside the frozen-plan `truth_boundary`
  negation (“no operational decoder … no tag, no Toeplitz master”) — an
  absence statement, not an arm. `FER`/`real-channel`/`minimum
  N`/`qualification`/`promotion` occur only in negations/scope limits.
- No qualification/promotion language; no `improv*` token anywhere.
- No cross-N improvement claim: N=65536 mean (`0.028768524223564552`)
  EXCEEDS N=32768 mean (`0.019146193040229846`), and no artifact claims
  scaling improvement — the table reports both rows neutrally and the
  label is NOT_CONFIRMED.
- Report transcribes aggregate numbers verbatim (stats/resources/entropy/
  gates/label/scope all present; `| True |` × 12; f/leakage live in
  aggregate+construction, not report columns, by schema).

---

## 9. Tests + scope — PASS

- Focused (pinned interpreter, fresh basetemp): **15 passed** in 218.82 s
  (operator froze 15/15; Pre-EXECUTE saw 15 in 208.29 s — same count).
- Full NB-Polar suite: **335 passed** in 786.77 s (320 prior + 15 P15;
  matches frozen 335).
- `git rev-parse HEAD` → `ab173f2a5e17336383a897b941080b731ba3dd9e`
  (unchanged from freeze record); no commit made by this review.
- `git status --porcelain` (100 entries, dirty tree reviewed by scope per
  AGENTS.md §10.1-11): P15 footprint is exactly the declared set —
  untracked runner `empirical_genie_mid_n.py`, untracked focused test,
  untracked `specs/nbpolar-phase4-p15/` delta, P15 section of shared
  `tasks.md`, and the P15 queue dir (incl. the new output root). Zero
  P15 tokens (`mid_n|196..199`) in any accepted module or other test
  file; zero P15-attributed hunks in the tracked diffs of `__init__.py /
  sc.py / empirical_channel.py / empirical_oracle.py /
  empirical_diagnostic.py`; P12/P13/P14 files untouched by this wave;
  X-roots untouched; no `results/` or `outputs_comparison/` writes.
- Gate NOT rerun; NPZ NOT reopened; no Model-F/HOLD/raw/real/EVAL/tag
  access; no P12/P13/P14/old-root writes; no commit/push.

---

## Findings

Blocking issues: none.

Non-blocking observations (no action required before acceptance):

1. Reviewer-method lesson (for the record): a first argmin rescan using
   suffix-subtraction (`total − cumsum[k]`) returned K1=608 at N=65536
   (residual diff 2.7e-11 vs a 1.6e-13 neighbour margin) — pure
   summation-order noise. Rescanning with the exact code-path residual
   (`g[k:].sum()`) reproduces the persisted (607, 13029) bit-exact for
   both N. This confirms the Pre-EXECUTE ≥1e-9 binding was load-bearing
   and that Pre-RESULT recomputation must use the exact summation path,
   not an algebraically identical shortcut.
2. `STATUS.yaml` still reads `artifact_reads_used: 0, attempts_used: 0,
   result: null, next_gate: INDEPENDENT_PRE_EXECUTE` although the gate
   ran and artifact accounting records 1/1 spent with a persisted label.
   Doc hygiene only — the artifacts are the authoritative consumption
   record. Suggest the main thread sync STATUS at solidification
   (no reviewer edit per constraints).

## Checklist

- [x] Matches OpenSpec spec (cells/construction/statistic/gates/labels per
      TASK_PACKET P15-02..P15-04; proxy-only wording; no BEC arm)
- [x] Tests pass (15 focused + 335 full, pinned interpreter, fresh basetemps)
- [x] No scope creep (declared P15 set + output root only)
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? — No:
      no new failure mode or durable decision surfaced. The
      summation-order rescan lesson (obs. 1) is recorded here; batch any
      ledger update at the milestone per AGENTS.md §10.4.

## Closure statements

- The V25 `channel_counts.npz` was NEVER opened by this review (metadata
  `stat` size 25166822 bytes + mtime 2026-08-19 only, matching frozen
  expectation and observed bytes).
- The frozen gate command was NEVER rerun by this review (all execution
  was test-suite re-runs on injected data with fresh `/tmp` basetemps).
- No Model-F/HOLD/raw/real/EVAL/tag/FWHT/APP/SCL path was accessed; no
  P12/P13/P14/old-root writes; no commit/push.
- Consumption: reads 1/1 + attempts 1/1 spent at the single content open
  (per artifact accounting); opens 1, no reopen, retries 0.
- Next gate: main-thread acceptance / solidification (no rerun permitted).
