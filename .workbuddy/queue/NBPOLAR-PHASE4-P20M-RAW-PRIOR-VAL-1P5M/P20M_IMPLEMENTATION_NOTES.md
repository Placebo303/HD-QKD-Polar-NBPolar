# P20M Stage-A implementation notes (2026-09-19; Stage B NOT authorized)

## 1. Files created/modified (Stage-A manifest)

Created:

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/raw_prior_val_1p5m.py`
  (new thin runner; Stage-A pins filled post-derivation; see §2).
- `comparison_bench/tests/test_nbpolar_raw_prior_val_1p5m.py`
  (new focused suite, 19 tests; injected/fake inputs only).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz`
  (Stage-A product, 25438650 B).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json`
  (Stage-A product, 438141 B).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/P20M_FREEZE.md`
  (Stage-A freeze, all pins filled).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/P20M_IMPLEMENTATION_NOTES.md`
  (this file).

Modified in place:

- `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/STATUS.yaml`
  (stage-true text; counts 0/0, DEV 0/1, HOLD 0/1, attempts 0/1; Stage-A
  completion; both product digests; next gate = independent Pre-EXECUTE review).

Untouched: every accepted module (`l1_order_1p5m`, `l1_disclosure_1p5m`,
`per_session_calibration`, `prior`, `target_n_scaling`,
`empirical_genie_scaling`, `target_construction`, P16 construction file, P20H
calibration product, X08 probe root), `src/`, `experiments/`, `tools/`,
`results/`, `comparison_bench/outputs_comparison/`. The Stage-B root
`raw_prior_val_1p5m/` stays ABSENT (verified at close). No commit/push.

## 2. Runner-delta evidence (§2 d1-d7; thin importer, written equivalent)

The module imports accepted `l1_order_1p5m` read-only and reuses its
population, gate family (a)-(f), order-file mechanism shape, SC/tag/transform
seams and leaf scorers without edits. The ONLY new code is the d1-d7 delta:

- (d1) `derive_raw_prior_arrays` / `build_raw_prior_arrays` (§3 raw rule, no
  lambda parameter exists) + `load_worktree_counts_arrays` (digest-pinned
  single worktree read with no-reopen guard) + `verify_corrected_prior`
  (exact 10-key set, canonical digest, lambda-0.0 pin, floor pin, H
  recomputation within 1e-12, `p_b` cross-check, column normalization).
- (d2) `budget_literal_display` / `verify_budget_literal` (S2-i literal
  recomputed from the same-run H via accepted `budget_k_total`).
- (d3) `verify_stage_b_order_file_p20m` (L1+L2 permutations, K pins,
  derivation replay incl. 16 blocks) + `run_derive_stage_a` /
  `sample_synthetic_train_blocks` (accepted P13/P16 TRAIN procedure: model
  sampling + `block_genie_risks` + `select_empirical_split`; Stage A only).
- (d4) `build_arm_table` / `check_frozen_arm_table` (G0 319/6492 lambda/P16
  control; G1 derived K1/K2 raw/derived-orders; G2 oracle at candidate K2;
  5K+64 arithmetic; 15 SC / 9 tags).
- (d5) `raw_prior_val_1p5m_seed_bits` (master 2026092280, new prefix).
- (d6) per-record `floor_hits_1e15` / `floor_hit_rate` (= hits / 2N lookups) +
  `floor_hit_rate_reported` gate (construction floor hits + fields present on
  every record, values required wherever a candidate was selected;
  decode_failed/resource_abort select none, so None is honest there).
- (d7) `verify_build_dev_disjointness` (S2-ii: build TRAIN 0..1659 vs DEV VAL
  1660..2043, disjoint by split identity).
- Per-record `k_total` is arm-level (`k1+k2` of that arm: G0 6811, G1 derived,
  G2 K2) so every record is arithmetically self-consistent; the run-level
  S2-i `budget_literal` is shared on all records. Per-record `l1_order_digest`:
  G0 = P16 old-L1 digest, G1 = order-file digest, G2 = None (oracle).
- Two modes with refusal before any read/write: `--derive` (no other flags;
  mixed refuses), Stage-B frozen command (all 18 flags required, no defaults;
  bare invocation refuses as ambiguous).
- Justification for the written equivalent (packet §10 allows it): arms, K,
  orders, priors, tags and record schema differ per d1-d7, so the run body is
  P20M-local; every leaf call (SC, tag, metrics, NLL, floor diagnostics,
  first-error, construction/manifest verification, DEV formation) is the
  accepted function read-only.

## 3. Test commands/results (Stage-A suites, zero protected opens)

Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(sibling-checkout venv; this checkout has no local `.venv`; recorded).

Command (run twice; temp roots are fresh additive `workspace/p20m/<uuid>/`,
cleaned per test; `-p no:cacheprovider`):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_raw_prior_val_1p5m.py -p no:cacheprovider -q
```

- Pre-fill run (pins None, before derivation): 19 passed. Three fixes were
  needed during iteration (order-file/pin single reads instead of an
  all-pins check; floor-gate None semantics for candidate-less records;
  per-record arm-level k_total; oracle fake `low_hat`/`oracle_l2_exact`):
  all are in the final module + tests above, no scope change.
- Post-fill run (pins filled + freeze written): 19 passed (re-run after the
  pin-fill edit; the pin-state test cross-checks module pins against
  `P20M_FREEZE.md` in the filled state).
- Coverage: raw-math vs independent literal + normalization + zero-column
  fallback; artifact keys/dtypes/pins; digest determinism; `p_b` cross-check +
  five tamper refusals; seed grep-rule placement; order-file digest/provenance
  refusals; CLI mixed/ambiguous/missing refusals; Stage-B root absence;
  full Stage-B runs with scripted SC fakes (all-exact COMPLETE 9/15/9,
  restoration descriptive g1_restored_count, undetected BLOCKED with earliest
  gate, zero-sampling pin via forbidden samplers); tiny real SC/oracle via the
  accepted path; one-open guard refusals; guard audit (all False at close).

## 4. Protected-open audit (Stage-A close)

- counts-calibration content opens: 0/0 (V25 counts NPZ never opened, statted,
  or listed; `load_v25_channel_counts` not imported).
- DEV content opens: 0/1 (no parquet opened/statted; DEV formation only on
  injected tables in tests).
- HOLD reads: 0/1 (untouched).
- Worktree-npz reads: 1, consumed once by the single authorized `--derive`
  run (digest reverified `e8dd078a...` before the read; no-reopen guard set;
  tests restore guards and never touch the real file).
- 1M pool: never opened/statted/listed/read in any form. Reserved 2M: pristine
  by non-access (never opened/statted/listed/read). 1.5M VAL/HOLD: never
  touched. `results/` and `comparison_bench/outputs_comparison/`: zero writes.

## 5. Grep-rule evidence (master / test seeds / derivation seeds)

Repo `git grep -l` at Stage-A close: the master `2026092280`, test seeds
`2026092281..2026092287` and derivation seeds `2026092291..2026092294` appear
in tracked files ONLY under the P20M runner, the P20M test file, the P20M
queue dir, the P20M spec-doc prefix, and the pre-existing umbrella
`openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` P20M section
(asserted by `test_grep_rule_seed_placement`; queue dir itself is untracked,
so its files are additionally asserted by direct read). Test seeds appear in
the test file only (never the runner); master + derivation seeds appear in
the runner (frozen constants) and packet docs.

## 6. Stage-A derivation record (executed EXACTLY once)

Command (exit 0, no rerun needed):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m --derive
```

Result (stdout JSON, recorded verbatim in the freeze): worktree digest
`e8dd078a...` reverified; counts total `424960`; zero columns `0`;
floor hits `1046140` / rate `0.9976768493652344`; H
`0.02519949692375297 / 0.8003665547495433 / 0.8255660516732963` (X08 reference
reproduced to ~1e-17, recomputed never copied); K_total `7020`, K1 `331`,
K2 `6689`; TRAIN residual `3.0162993815141537e-07`; 16 blocks / 32 genie
calls; prior digest `372dcc1c...`; order digest `a9f18a9f...`; G1/G2 leakage
`35164/33509`; wall 219.6 s in-process (3:41 elapsed, 571 MB RSS peak, both
inside the 600 s / 2 GiB envelope class).
