# P3 Stage B freeze v2 — accepted-artifact model-sampled SC interface diagnostic

Rev 2a (2026-09-13): Pre-EXECUTE review NEEDS_CHANGES/F-1 resolved by ratifying
the implemented classifier semantics and correcting §4's precedence text; NB-1
(channel docstring), NB-2 (B4 `disclosed_value_source`), NB-4 (hard-gate
mapping) clarified. No frozen value changed.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; this doc authorizes nothing.**
Supersedes the stale draft `openspec/changes/formal-ir-nbpolar-mvp/P3_STAGEB_FREEZE.md`
(see its banner). No Stage B artifact run has been executed: the one
artifact-content attempt is **0 consumed** at freeze; it is consumed at the
first artifact-content open performed by the frozen command below.

## 1. Scope

P3 Stage B only: one controlled, model-sampled development diagnostic of the
boundary from the accepted Model-F count distribution through the accepted P1
dense `SymbolMetric` into the accepted q-ary SC decoder, plus a tiny
independent exhaustive-oracle check. No Phase 5, no FER/leakage/key-rate/
reconciliation claim, no construction/K/disclosure/rate tuning, no raw/TTBin/
held-out data, no commit/push.

## 2. Frozen artifact identity and attempt

| item | value |
|---|---|
| root (read-only, sibling) | `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/` |
| npz | `model_f_input.npz` — 208467 bytes |
| summary | `model_f_input_summary.json` — 752 bytes |
| loader | accepted `prior_artifact.load_prior_artifact` (single load; tables kept in memory) |
| derivation | accepted `prior.smooth_joint_to_conditional(counts_ab, LAMBDA_STAR)` then `prior.derive_p1`; `p_b = artifact.p_b` |
| prob→log conversion | accepted `prior.probs_to_symbol_metric` (q=32), A14 ownership |
| artifact-content attempts allowed | 1 |
| attempts consumed at freeze | 0 (no content open in this session) |
| attempt consumption point | first artifact-content open by the frozen command |
| attempt on failure | consumed regardless of result; no rerun |
| no-write rule | nothing under the sibling root, `results/`, or `comparison_bench/outputs_comparison/` |

## 3. Frozen seeds

- Stage B diagnostic seed: **2026091316** only (`empirical_channel.P3_DIAG_SEED`),
  passed through `empirical_channel.make_rng`, which refuses the banned
  predecessor range 2026091200..1213.
- Unit 2026091314 / TRAIN 2026091315 are unchanged and **not used** in Stage B
  sampling. No EVAL seed exists in P3. One RNG stream, fixed case order
  B1→B2→B3→B4 (B5 consumes no samples).

## 4. Frozen case / mask / block-count / threshold matrix

| case | N | masks | blocks | disclosure | oracle / gates |
|---|---|---|---|---|---|
| B1 | 2 | none | 64 | none | every SC conditional `res.decision_metrics[i]` at decoded prefix `res.u_hat[:i]` vs `empirical_oracle` exhaustive conditional; max prob err ≤1e-12, finite-entry max log err ≤1e-9, support mismatch 0, numeric failure 0, truth-leak sentinel 0 |
| B1 | 4 | none | 64 | none | same gates (vectorized exhaustive backend; q^N = 1048576) |
| B2 | 16 | M1–M5 | 16 each (80) | true U at mask positions | none; report exact / impossible / other / nonfinite per (N,mask) |
| B2 | 64 | M1–M5 | 16 each (80) | true U at mask positions | none; same report |
| B3 | 256 | M1–M5 | 8 each (40) | true U at mask positions | no exhaustive oracle; report n_exact / n_impossible / n_other / n_nan / n_initial_error / wall time per mask + totals; hard gate is only zero crash/nonfinite/truth-leak |
| B4 | 64, 256, 1024 | M5 only | timing only | M5 first N/2 positions | metric-only (4×N Bob batch) + decode-only on one prebuilt (N,32) log metric; 1 warm-up + ≥5 measured calls, median; record metric (N,32) / decision (N,32) shapes and peak RSS |
| B5 | — | — | attribution | — | classify every non-exact executed B1–B3 block (B4 is timing-only, 0 scored blocks) at its earliest observable layer |

Masks (disclosed positions; `U = polar_transform(A_high)`). B2/B3 disclose the
true U symbols at those positions. B4 is timing-only: it discloses true U when
available and records `disclosed_value_source` (`true_U`, or a `metric_argmax`
fallback when the true-value disclosure is unsupported); the fallback affects
no B1-B3 count or gate:

| mask | positions |
|---|---|
| M1 all-but-one | 0..N-2 (undisclosed N-1; N=256 discloses 255) |
| M2 prefix | 0..N/2-1 |
| M3 suffix | N/2..N-1 |
| M4 alternating | 0,2,...,N-2 |
| M5 construction-order | first N/2 positions of accepted `construction.analytic_order(0.05, N)`, imported unchanged |

Outcome semantics (accepted Phase 3): `exact` = `u_hat == u_true` **and**
`x_hat == x_true`; `impossible` = `ImpossibleDisclosedValueError`;
`nonfinite` = NaN/invalid metric (NumericNonfiniteError or NaN/+Inf in
decisions); `other` = any other non-exact outcome. Impossible/other/nonfinite
are never merged into exact. `n_initial_error` = blocks where
`argmax(logp, axis=1) != x_true` in ≥1 coordinate.

B5 attribution precedence (evaluated per non-exact executed block, earliest
observable layer first; matches `classify_stageb_failure` exactly):
`artifact_adapter_support` (sampled true symbol has zero probability in its
metric row) > `normalization` (metric-row normalization failure) >
`disclosure_contradiction` (`ImpossibleDisclosedValueError`) > `SC_numeric`
(nonfinite decision metrics / `NumericNonfiniteError`) > `unattributed`
(unclassified decoder exception; operationalizes the frozen crash=0 gate) >
`expected_under_disclosure` (finite non-exact block with at least one
undisclosed coordinate whose pointwise MAP disagrees with the truth) >
`SC_decision` (remaining finite non-exact blocks). B1 decodes without
disclosure, so its finite non-exact blocks are `SC_decision` (or
`unattributed` for unclassified exceptions).
Resource soft-stop blocks are recorded as `resource_abort` and are **not**
merged into exact counts or attribution-as-failure. Disjoint accounting per
case: `exact + impossible + other + nonfinite + resource_abort == planned`.

Hard-gate mapping (adds no scientific threshold beyond the frozen list):
`b1_all_gates` = frozen B1 five gates + zero decode/oracle exceptions
(crash=0); `b2_b3_zero_nonfinite` = frozen nonfinite=0;
`b2_b3_zero_unattributed` = frozen crash=0 for decoder exceptions;
`b2_b3_coverage_complete` and `b4_complete` = frozen evidence completeness
(all planned blocks executed; >=5 measured calls per B4 leg);
`zero_truth_leak` = frozen sentinel=0. B3 applies no exact-count threshold.

B1 threshold values: probability error (absolute max) **1e-12**; log error on
finite entries (absolute max) **1e-9**; support mismatches **0**; numeric
failures **0**; truth-leak violations **0**.

Truth isolation: the operational metric builder takes Bob + table only; Alice
truth may enter only the generator, the disclosed-U map and scoring. The
truth-leak sentinel adversarially mutates sampled truth copies after metric
creation and requires the metric and the decisions (with already-frozen
disclosed values) to stay bitwise unchanged; violations are counted and must
be 0.

## 5. Frozen budget

- Total wall budget: **3600 s** (`timeout 3600`).
- Per-case soft stop: **120 s**; expired cases record `resource_abort` for
  their remaining planned blocks (never counted exact) and continue.
- Memory envelope: RSS **< 2 GiB** (`ulimit -v 2097152` = 2147483648 bytes);
  `ulimit` enforces, the run records measured peak RSS. The frozen plan JSON
  records `rss_bytes_max = 2147483648`.

## 6. Frozen output root — single absent root, exactly 5 files

Root (relative to repo):
`.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/`

Confirmed **ABSENT** at freeze. Refused if it exists (checked before the
artifact open). Created only after the artifact load succeeds; exactly these
five files are written at the end, no other writes anywhere:

1. `frozen_plan.json`
2. `oracle_records.json`
3. `stress_and_profile.json`
4. `diagnostic_summary.json`
5. `report.md`

No count tables, symbol vectors, private rows or per-block raw posterior
arrays are written.

## 7. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_diagnostic --mode stageb --npz /mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz --summary /mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json --seed 2026091316 --out .workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic
```

No flags may be added; no re-run after any outcome.

## 8. Pre-EXECUTE evidence (implementation side, artifact never read)

- Vectorized exhaustive oracle backend implemented and tested against the
  accepted literal oracle (GF4 all prefixes; GF32 N=2; GF32 N=4 at prefixes
  of length 2 and 3 with an explicit test-only cap opt-in; batch transform
  vs `polar_transform_reference` at N=2/4/8). Default literal behavior and
  the 4096 cap are unchanged for existing callers.
- Measured cost of the frozen 64-block × 4-coordinate N=4 oracle sweep:
  **11.7 s** in the injected-table full-matrix dry run; final standalone
  median **0.1724 s/block → 11.0 s** (chain per block 0.17–0.19 s), well
  under the 120 s per-case soft stop.
- Injected-table full-matrix dry run (caller-supplied tables, temp root):
  wall ≈ 18.1 s, exactly 5 files, hard_gates_pass = true, truth-leak
  violations = 0, coverage complete. This consumed **no** artifact attempt.
- Focused + predecessor test suites green; ordinary tests never touch the
  sibling root.

## 9. Freeze status

FROZEN, awaiting independent Pre-EXECUTE PASS; this doc authorizes nothing.
All scientific execution, result publication and acceptance remain owned by
the main thread plus an independent reviewer.
