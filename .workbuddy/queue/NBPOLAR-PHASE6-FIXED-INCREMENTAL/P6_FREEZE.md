# P6 freeze — NB-Polar Phase 6 fixed incremental disclosure paired development gate

Rev 1 (2026-09-13). Frozen by the operator session under the exact user
authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond the packet were
invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No paired run has been executed. The single attempt is **0 consumed** at freeze;
it is consumed at the first scientific `sc_decode` call of the frozen command
below (static comparator arm, block 0). `STATUS.yaml` keeps `attempts_used: 0`.
The real output root is **ABSENT**.

## 1. Scope

One fixed nested-disclosure schedule at the accepted Phase 5 point, paired with
an in-run static K=45 comparator on the same 300 newly generated synthetic
blocks, plus focused tests, a budget profile, and one preregistered development
gate after this freeze receives an independent Pre-EXECUTE PASS. Not real-data
FER, leakage efficiency, key rate, qualification, promotion, adaptive
disclosure, Phase 7, SCL/CRC, retry, rate scan or per-frame tuning. No commit
or push.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py` |
| adapter | `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py` |
| tests | `comparison_bench/tests/test_nbpolar_incremental.py` |
| re-exports | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` (explicit aliases only) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3) |
| accepted predecessors reused unchanged | `algebra.make_gf32`, `transform.polar_transform`, `sc.sc_decode`, `synthetic.generate_erasure_block`, `construction.analytic_order`, `protocol.static_disclosure_coordinates/labels_from_symbols/labels_to_bits/wilson_lower_bound/OUTCOMES`, `shared.toeplitz_tag/canonical_event/transcript_summary/verification_union_bound` |
| untouched | `protocol.py`, `methods/nbpolar_static.py`, `test_nbpolar_protocol.py`, frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, accepted nbpolar modules, the immutable Phase 5 evidence root |

## 3. Frozen point and nested schedule

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural index order.
- q-ary erasure channel, `N=256`, `epsilon=0.05`; physical labels `32*x`.
- Worst-first `analytic_order(0.05, 256)`; `D_i = sorted(order[:K_i])` for
  `K=(29, 33, 37, 41, 45)`; strict prefix nesting is verified at run time
  (`order_prefix_matches`, `strict_nesting`, `new_coordinates_disjoint`).
- Level `i` (1-based here) publishes only `D_i minus D_{i-1}` actual GF32 `U`
  values, zeros included as values. Every coordinate is counted once.

```text
D_1 (K=29) ascending:
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 20, 24, 32, 33,
 34, 36, 40, 64, 65, 66, 128, 129]
  new (29): the same list.
D_2 (K=33): D_1 + [14, 19, 48, 68]
D_3 (K=37): D_2 + [21, 72, 130, 132]
D_4 (K=41): D_3 + [22, 35, 80, 136]
D_5 (K=45): D_4 + [25, 26, 96, 144]
```

`D_5` equals the accepted Phase 5 static K=45 set (independently checked in
tests).

Per invoked level the decoder receives the cumulative known set `D_i` and the
actual `U[D_i]` values on the SAME original Bob metric; there is a fresh
`sc_decode` call with no state, belief, partial sum or hard decision carried
across levels. A level whose decode raises or returns nonfinite decision
marginals stops the block fail-closed (`decode_failed`) with no further levels
and no tag at that level.

## 4. Frozen seeds and seed derivation

- Run seed **2026091340**; Toeplitz master **2026091341**. Both were proven
  absent from `HEAD` (`git grep 2026091340 HEAD` and `git grep 2026091341 HEAD`
  return no matches, recorded 2026-09-13 before implementation) and absent from
  every accepted/consumed Phase 1-5 stream and document (the same grep over the
  pre-Phase-6 worktree returned no matches; only the new Phase 6 sources and this
  queue directory now carry them). They are never used by tests.
- `validate_run_seed` refuses at least: `2026091200..2026091213`,
  `2026091314`, `2026091315`, `2026091316`, `2026091317`, `2026091318`,
  `2026091319`, `2026091320`, `2026091330` (22 values; exact set is frozen in
  `BANNED_RUN_SEEDS` and persisted in `frozen_plan.json.refused_run_seeds`).
- Per-arm/per-block/per-level seed rule (public control, never persisted raw):
  concatenate `SHA-256("nbpolar-p6-toeplitz-seed:2026091341:<arm>:<block_index>:
  <level>:<counter>")` for `counter = 0, 1, ...` (ASCII decimal), unpack each
  digest MSB-first, truncate to `10*N + 63 = 2623` bits.
  - `arm` is `static` or `incremental`;
  - `block_index` is 0-based (0..299);
  - `level` is 0-based: the static comparator uses level 0; the incremental
    schedule uses levels 0..4 corresponding to cumulative
    `K = 29, 33, 37, 41, 45`.
- Each tag invocation consumes 2623 public seed bits. Each level advance emits
  one public feedback `control` transcript event (`key_dependent_bits=0`,
  `public_control_bits=1`). Feedback control is counted separately as
  `feedback_control_invocations` / `feedback_control_bits`, included in the
  public-control total, and the split is reported.

## 5. Static K=45 comparator (in-run, never the Phase 5 root)

Thin re-implementation of the accepted Phase 5 semantics inside
`incremental.py` with the Phase 6 seed derivation:

1. `D = sorted(analytic_order(0.05, 256)[:45])`, publish actual `U[D]`
   values including zeros.
2. Exactly ONE `sc_decode` on the original Bob metric with the known set.
3. On SC exception or nonfinite marginals: `decode_failed`, 225 key-dependent
   bits, no tag.
4. Otherwise ONE 64-bit Toeplitz verification: tag pass and exact -> `exact`;
   tag pass and not exact -> `undetected` (never success); tag mismatch ->
   `verify_failed`. Key-dependent total `225 + 64 = 289`; public seed 2623.

Equivalence with `protocol.run_static_block` on deterministic injected blocks
(outcomes, error counts, bit counts equal; message bits equal and seeds
different by derivation) is covered by tests. The comparator never reads or
reruns the immutable Phase 5 evidence root.

## 6. Outcome precedence and accounting (frozen)

Outcome precedence (first matching rule wins; buckets disjoint and exhaustive
over the 300 planned blocks per arm):

```text
resource_abort > decode_failed > verify_failed > exact > undetected
```

- `resource_abort`: paired block not executed because the preregistered budget
  stop fired; both arms 0 bits, 0 invocations.
- `decode_failed`: SC exception or nonfinite decision marginals at invoked level
  `i` (1-based); stop fail-closed; key-dependent `5*K_i + 64*(i-1)`; public seed
  `2623*(i-1)` plus feedback bits `(i-1)`.
- `verify_failed`: all five levels tag-mismatched; key-dependent
  `5*45 + 64*5 = 545`; public seed `2623*5` plus feedback `4`.
- `exact` / `undetected`: tag match at accepted level `j` (1-based);
  key-dependent `5*K_j + 64*j`; public seed `2623*j` plus feedback `j-1`.

Verification union bound: `min(1.0, total_tag_invocations * 2**-64)` with
per-arm and total invocation counts; consistency with the independent
transcript recount is a hard gate (no invented numeric threshold).

Transcript recount is an independent literal walk over the in-memory event list
(`static_disclosure` / `incremental_disclosure`, `verification_tag`, `control`);
it must equal the per-arm incremental totals for key-dependent bits, public
control bits, tag invocations and feedback control invocations. Per-block
schedule consistency is recomputed from the frozen schedule and the record
fields.

## 7. Paired design (frozen)

One run seed drives ONE `numpy.random.Generator`; for each of the 300 blocks the
generator is called exactly once with `generate_erasure_block(rng, 32, 256,
0.05)` and BOTH arms run on the identical arrays in the same order (static arm
first, then incremental). The unmutated metric is verified after each arm; the
per-block `paired_match` flag records it. The static comparator is an in-run
comparator, not a rerun of the Phase 5 root.

## 8. Budget and resource ceilings (paired N=256 profile evidence)

Profile command (injected non-frozen seed, temp root, NOT the frozen run):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python /tmp/opencode/p6_profile.py`
(`run_paired_dev_gate(run_seed=2026091399, blocks=40, out_root=/tmp/opencode/p6_profile_out)`).

| workload | blocks | median | mean | p90 | max |
|---|---|---|---|---|---|
| paired block wall | 40 | 35.52 ms | 35.55 ms | 38.08 ms | 73.88 ms |
| static arm decode | 40 | 16.79 ms | — | — | 19.83 ms |
| incremental arm decode | 40 | 16.60 ms | 16.65 ms | — | 50.69 ms |
| metric generation | 40 | 0.144 ms | — | — | 1.53 ms |

Levels invoked: level 1 on 39/40 blocks, level 3 on 1/40. Profile outcomes:
static exact 39 / decode_failed 1; incremental exact 37 / decode_failed 3.
Total profile wall 1.43 s; peak RSS 105943040 bytes (~101 MiB; `/proc/self`
VmHWM 106876928 bytes). Projected 300-block wall: 10.66 s by mean, 11.42 s by
p90.

Frozen ceilings:

- internal total wall budget: **600 s** (`DEV_GATE_TOTAL_WALL_S`; ≈ 56× the
  projected mean). On expiry, remaining planned blocks are `resource_abort` and
  the five files are still written.
- per-paired-block soft cap: **10.0 s** (`DEV_GATE_PER_PAIRED_BLOCK_SOFT_CAP_S`;
  ≈ 135× the observed maximum of 73.88 ms). On expiry after a completed pair,
  remaining planned blocks are `resource_abort`.
- external command timeout: **T = 1200 s** (`timeout 1200`), 2× the internal
  total budget so the internal stop fires first and the evidence is written.
- memory envelope: `ulimit -v 2097152` (2 GiB virtual); the plan records
  `rss_bytes_max = 2147483648`, and the measured peak `rss_bytes_peak` is
  persisted in `aggregate_comparison.json` (profile ~101 MiB).

## 9. Frozen output root and schema

Root (relative to repo):
`.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`

Confirmed **ABSENT** at freeze. The CLI refuses an existing root before any
decoder call. Exactly five compact scalar-only files are written; no symbol
vectors, labels, disclosed values, decoded keys, raw seed bits, transcript raw
events or per-block coordinate lists are persisted:

1. `frozen_plan.json` — protocol, mode, created_utc, repository, run_seed,
   planned_blocks, q, n, epsilon, field{}, channel, order, schedule{K, D_sets,
   new_coordinates, proof flags}, static_comparator{}, disclosure_rule,
   restart_rule, label_domain{}, toeplitz{}, accounting{}, union_bound,
   outcome_precedence[], budget{}, refused_run_seeds[], attempt_consumption_point.
2. `per_block_paired_outcomes.json` — `n_blocks` and one record per paired block:
   `block_index, paired_match, metric_wall_s, static_wall_s,
   incremental_wall_s, paired_wall_s, static{...}, incremental{...}`; each arm
   record is scalar-only (`outcome, exact, accepted_level, decode_failed_level,
   levels_invoked, tag_invocations, feedback_control_invocations,
   key_dependent_bits, public_seed_bits, feedback_control_bits,
   public_control_bits, nonfinite, truth_leak_violation, error_type,
   pre_symbol_errors, pre_bit_errors, symbol_errors, bit_errors, wall_s`).
3. `transcript_accounting.json` — per-arm incremental totals, independent
   recount, mismatch counts, transcript sha256; union-bound block; public-control
   split.
4. `aggregate_comparison.json` — per-arm outcome totals, attempted/coverage,
   key-dependent totals and averages, Wilson blocks, disclosure comparison
   (integer rule `incremental_total*100 <= 95*static_total`), union bound,
   public control, transcript recount, truth-leak/nonfinite counts, decode error
   types, `hard_gates{}` (all booleans), `candidate`, bounded `claim_scope`,
   wall/RSS, resource stop flag.
5. `report.md` — bounded human-readable summary.

## 10. Wilson calculation and hard gates

One-sided 95% Wilson lower bound for exact recovery, successes `s = exact`,
denominator `n = attempted` (executed blocks; `resource_abort` excluded), `z =
1.6448536269514722` (accepted Phase 5 `wilson_lower_bound`).

All gates must hold; each is persisted as a boolean in `hard_gates`:

1. `frozen_plan_identity` — run seed 2026091340, 300 blocks, N=256, epsilon
   0.05, schedule (29,33,37,41,45);
2. `paired_identical_blocks` — every block `paired_match` true and 300 records;
3. `outcome_buckets_disjoint_exhaustive_both_arms` — both arms sum to 300;
4. `paired_coverage_complete` — both arms attempted 300 (no `resource_abort`);
5. `incremental_undetected_zero`;
6. `incremental_exact_ge_285` — exact >= 285;
7. `incremental_wilson_lower_ge_0_90` — Wilson LB >= 0.90;
8. `equal_attempted_denominators`;
9. `incremental_avg_key_dependent_le_95pct_static` — integer-exact
   `incremental_total * 100 <= 95 * static_total`;
10. `frozen_order_nesting_and_schedule_consistency` — nesting proof flags plus
    every per-block record consistent with the frozen schedule/accounting;
11. `invocation_universe_equals_recount_both_arms`;
12. `union_bound_consistent` — per-arm and total bounds equal the recounts;
13. `recount_zero_mismatch`;
14. `truth_leak_zero`;
15. `nonfinite_zero`;
16. `resource_stop_preregistered`;
17. `feedback_control_counted`;
18. `public_control_counted`.

Only if all gates pass is
`FIXED_INCREMENTAL_DEVELOPMENT_CANDIDATE` emitted; otherwise `candidate` is
null. The label is a synthetic development signal only.

## 11. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental --mode paired-dev-gate --run-seed 2026091340 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate
```

No flags may be added or changed. The output root must still be absent at
execution time. The single attempt is consumed at the first scientific
`sc_decode` call (static comparator arm, block 0). On any failure the attempt
stays consumed: no rerun, no seed change, no tuning, no partial credit.

The `python -m` invocation emits one cosmetic `runpy` `RuntimeWarning` because
the package `__init__` re-exports the module (the same pattern as Phase 5); it
is not an error and does not affect the run.

## 12. Forbidden-path proof

- `incremental.py` and `nbpolar_incremental.py` import only stdlib
  (`argparse, hashlib, json, sys, time, dataclasses, numbers, pathlib`), numpy,
  the accepted nbpolar Phase 1-5 modules and `formal_ir/shared.py`. No Model-F
  stored artifact, parquet, TTBin, DEV/EVAL, benchmark, sibling-checkout,
  SCL/CRC or rate-adaptation code path exists in either module; no import-time
  I/O; no global RNG; the only write target is the explicitly passed output
  root (created after the run, refused if present).
- `test_no_forbidden_markers_or_import_time_side_effects` scans both sources for
  `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`, `dev_seed`,
  `eval_seed`, `benchmark`, `sibling`, `artifact`, `results/` (zero matches) and
  imports both modules in a fresh interpreter with a temp cwd, asserting no file
  is created.
- The adapter builds its metric from the passed observation only; Alice truth
  never enters the metric or the decoder arguments.
- Tests use temporary directories and injected/non-frozen seeds only; no real
  data, stored artifact, `comparison_bench/outputs_comparison/`, `results/` or
  sibling path is touched. The sibling checkout is used read-only as the pinned
  interpreter only.
- The real output root `.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/
  paired_incremental_dev_gate/` is absent and must remain absent until the
  authorized execution.

## 13. Pre-EXECUTE checklist for the independent reviewer

1. Confirm this freeze doc matches the implemented constants
   (`FROZEN_RUN_SEED`, `TOEPLITZ_MASTER_SEED`, `BANNED_RUN_SEEDS`, `FROZEN_K`,
   `FROZEN_BLOCKS`, `MIN_EXACT`, budgets, seed derivation string, level index
   convention).
2. Recompute the five `D_i` sets and the nesting/new-coordinate lists.
3. Re-run the focused suite and the NB-Polar predecessor suite.
4. Confirm the 300-block command and output root above; confirm the root is
   absent and `STATUS.yaml` grants only the authorized flags with
   `attempts_used: 0`.
5. Confirm `git grep 2026091340 HEAD` and `git grep 2026091341 HEAD` are empty.
6. FAIL blocks execution; issues return to the operator for scoped repair and
   re-review.
