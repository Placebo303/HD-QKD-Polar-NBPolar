# R1 freeze — NB-Polar Phase 6-R1 decode-reject-advance three-arm development gate

Rev 1 (2026-09-13). Frozen by the operator session under the exact user
authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond the packet and
the Phase 6 main-thread disposition (option (a)) were invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No three-arm run has been executed. The single attempt is **0 consumed** at
freeze; it is consumed at the first scientific `sc_decode` call of the frozen
command below (static comparator arm, block 0). `STATUS.yaml` keeps
`attempts_used: 0`. The real output root is **ABSENT**.

## 1. Scope

One fresh 300-block synthetic development gate that runs three arms on the
identical per-block arrays: the static K=45 comparator, the accepted Phase 6
strict-stop incremental schedule, and the Phase 6-R1 decode-reject-advance
schedule. The R1 arm advances after a non-final impossible-disclosure rejection
(one public feedback request, no candidate, no tag); the strict-stop arm stays
byte-pinned to Phase 6. Not real-data FER, leakage efficiency, key rate,
qualification or promotion; no adaptive K, no tuning, no SC change, no cached
state, no SCL/CRC, no Phase 7, no commit or push.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py` |
| adapter | `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py` (`NBPolarIncrementalR1Method`; strict class output unchanged) |
| tests | `comparison_bench/tests/test_nbpolar_incremental_r1.py` (17 tests, R1-A01..A12 + refusals/adapter/schema) |
| re-exports | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` (explicit R1 aliases only) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3) |
| accepted predecessors reused unchanged | `algebra.make_gf32`, `transform.polar_transform`, `sc.sc_decode` / `ImpossibleDisclosedValueError` / `NumericNonfiniteError`, `synthetic.generate_erasure_block`, `construction.analytic_order`, `protocol.static_disclosure_coordinates/labels_from_symbols/labels_to_bits/wilson_lower_bound/OUTCOMES`, `shared.toeplitz_tag/canonical_event/transcript_summary/verification_union_bound` |
| untouched | Phase 5 `protocol.py`, `methods/nbpolar_static.py`, `test_nbpolar_protocol.py`, Phase 6 behavior/constants, frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, the immutable Phase 5/6 evidence roots (`static_protocol_dev_gate/`, `paired_incremental_dev_gate/`) |

## 3. The only semantic delta

`K=(29,33,37,41,45)` worst-first `analytic_order(0.05,256)` prefixes,
GF32/poly37/alpha2, `N=256`, erasure `epsilon=0.05`, label `32*x_hat`,
2560-bit Toeplitz message domain, per-arm/per-block/per-level seed derivation,
feedback/union-bound conventions, Wilson `z=1.6448536269514722` and all
thresholds are unchanged from Phase 6.

At a **non-final** level (K=29/33/37/41, levels 0..3) an
`ImpossibleDisclosedValueError` becomes `decode_rejected_continue`:

1. the intermediate rejection is recorded (`rejected_levels`, so
   `decode_rejected_continue_count` advances by one);
2. no candidate is created and no tag is invoked at that level;
3. exactly one public feedback request is counted
   (`feedback_control_invocations` / `feedback_control_bits` += 1);
4. the next fixed increment is disclosed (cumulative set `D_{i+1}`) and SC
   restarts from scratch on the **ORIGINAL** metric with no state, belief,
   partial sum or hard decision carried across levels.

At the **final** level K=45 the same error stays terminal `decode_failed`
(recorded in `decode_failed_level`; a final-level error is never recorded as a
rejection). No other exception may continue: `NumericNonfiniteError`, any
other `ValueError`/`TypeError`/other exception and nonfinite decision marginals
stay fail-closed terminal `decode_failed` at any level. An intermediate
rejection is never success and never a final outcome bucket. The strict-stop
path (`run_incremental_block`, default `advance_on_reject=False`) is unchanged
and its consistency proof rejects any record that carries a rejection.

## 4. Three arms and paired design

Arms, in frozen run order per block:

1. `static`: the static K=45 comparator (accepted Phase 5 semantics
   re-implemented thinly inside `incremental.py` with the R1 seed derivation);
2. `strict_stop`: `run_incremental_block` (Phase 6 semantics);
3. `r1`: `run_incremental_r1_block` (Section 3 delta).

One run seed drives ONE `numpy.random.Generator`; for each of the 300 blocks
the generator is called exactly once with
`generate_erasure_block(rng, 32, 256, 0.05)` and all three arms consume the
identical `(x, logp)` objects in the frozen order. `paired_match` is false if
any arm mutates either input array. Both incremental arms share the
`incremental` seed namespace so a block that never rejects is bit-identical
between strict-stop and R1; the paired comparison therefore isolates the
rejection delta. The static arm has its own namespace.

## 5. Frozen point and nested schedule

Identical to Phase 6 (see `P6_FREEZE.md` §3); `D_5` equals the accepted Phase 5
static K=45 set, and the nesting/prefix/disjoint proof flags are recomputed at
run time and gated:

```text
D_1 (K=29) ascending:
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 20, 24, 32, 33,
 34, 36, 40, 64, 65, 66, 128, 129]
D_2 (K=33): D_1 + [14, 19, 48, 68]
D_3 (K=37): D_2 + [21, 72, 130, 132]
D_4 (K=41): D_3 + [22, 35, 80, 136]
D_5 (K=45): D_4 + [25, 26, 96, 144]
```

Level `i` publishes only `D_i minus D_{i-1}` actual GF32 `U` values (zeros are
values); every coordinate is counted once; each invoked level runs a fresh
`sc_decode` on the same original metric.

## 6. Frozen seeds, derivation and absence proof

- Run seed **2026091350**; R1 Toeplitz master **2026091351**. Both were proven
  absent before implementation: `git grep -n 2026091350 HEAD` and
  `git grep -n 2026091351 HEAD` returned no matches (exit 1), and the
  pre-implementation worktree grep `grep -rn <seed> --exclude-dir=.git .`
  returned no matches (exit 1) over every accepted/consumed Phase 1-6 stream
  and document. They are never used by tests; R1 tests use 2026091360..1363.
- R1 validator (`validate_r1_run_seed`) refuses at least
  `2026091200..2026091213`, `2026091314..2026091321`, `2026091330`,
  `2026091340`, `2026091341` (25 values; exact set is `R1_BANNED_RUN_SEEDS`
  and persisted in `frozen_plan.json.refused_run_seeds`). The Phase 6
  `BANNED_RUN_SEEDS` and `validate_run_seed` stay byte-pinned and unchanged
  (2026091340 remains CLI-usable for the Phase 6 mode only).
- Per-arm/per-block/per-level seed rule (public control, never persisted raw):
  concatenate `SHA-256("nbpolar-p6-toeplitz-seed:2026091351:<arm>:<block_index>:
  <level>:<counter>")` for `counter = 0, 1, ...` (ASCII decimal), unpack each
  digest MSB-first, truncate to `10*N + 63 = 2623` bits.
  - `arm` is `static` or `incremental` (both incremental arms share the
    `incremental` namespace);
  - `block_index` is 0-based (0..299);
  - `level` is 0-based: static level 0, incremental levels 0..4 for
    `K = 29, 33, 37, 41, 45`.
- Each tag invocation consumes 2623 public seed bits.

## 7. Accounting, feedback and union bound

`j` = number of tag invocations on the block; levels are cumulative and each
coordinate is counted once.

- terminated block (`exact`/`undetected`/`verify_failed`):
  `key_dependent_bits = 5*K_terminal + 64*j`;
- `decode_failed` at level `i`: `5*K_i + 64*j` (j tags before the failing
  level; the failing level itself invokes no tag);
- `resource_abort`: 0.
- feedback: exactly one public `control` event
  (`key_dependent_bits=0`, `public_control_bits=1`) per level advance, whether
  the advance came from a tag mismatch or a non-final decode rejection; total
  advances `= levels_invoked - 1`. Per-block invariant (gated):
  `levels_invoked = tag_invocations + decode_rejected_continue_count`
  (+1 for a `decode_failed` terminal level, which produces neither).
- public control per tag = 2623 seed bits; the feedback split is reported.
- verification union bound `min(1.0, total_tag_invocations * 2**-64)` with
  per-arm and total invocation counts; consistency with the independent
  literal transcript recount is a hard gate (no invented numeric threshold).

The R1 transcript places a `verification_tag` event only on non-rejected
invoked levels and marks rejection advances with reason
`decode_rejected_advance_next_level` (tag mismatches keep
`tag_mismatch_advance_next_level`).

## 8. Outcome precedence

```text
resource_abort > decode_failed > verify_failed > exact > undetected
```

Buckets are disjoint and exhaustive per arm over the 300 planned blocks.
`decode_rejected_continue` is an intermediate transition, never a bucket.
`undetected` (tag match, not exact) is never success.

## 9. Rescue identities against the strict arm (reported, not gated)

For every paired block, with `strict` and `r1` outcomes:

- `rescued = (strict != exact and r1 == exact)`;
- `persisted = (strict outcome == r1 outcome)`;
- `regressed = (strict == exact and r1 != exact)`;
- `other = remainder` (listed with block indices; expected empty).

The four buckets partition the paired blocks; the counts and block-index lists
are persisted in `aggregate_comparison.json.rescue_comparison_against_strict`.
They do not change any threshold.

## 10. Budget and resource ceilings (three-arm N=256 profile evidence)

Profile command (injected non-frozen seed, temp root, NOT the frozen run):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python /tmp/opencode/p6r1_profile.py`
(`run_three_arm_paired_dev_gate(run_seed=2026091399, blocks=60, out_root=/tmp/opencode/p6r1_profile_out)`).

| workload | blocks | median | mean | p90 | max |
|---|---|---|---|---|---|
| paired three-arm block wall | 60 | 50.24 ms | 51.77 ms | 53.05 ms | 121.64 ms |
| static arm | 60 | 15.70 ms | 15.61 ms | 16.89 ms | 19.66 ms |
| strict-stop arm | 60 | 15.59 ms | 15.50 ms | 16.52 ms | 50.25 ms |
| R1 arm | 60 | 15.79 ms | 17.45 ms | 21.50 ms | 47.55 ms |
| metric generation | 60 | 0.14 ms | 0.17 ms | 0.18 ms | 1.29 ms |

Level distributions (60 injected blocks): strict-stop `levels_invoked` 1 on
58, 2 on 1, 3 on 1; R1 1 on 52, 2 on 5, 3 on 1, 4 on 1, 5 on 1. R1 had 11
rejections on 6 blocks (rejected level histogram 0:6, 1:2, 2:2, 3:1);
terminating levels -1:0, 0:52, 1:5, 2:1, 3:1, 4:1. Profile outcomes: static
exact 59 / decode_failed 1; strict exact 54 / decode_failed 6; R1 exact 59 /
decode_failed 1. Profile rescue identities: rescued 5, persisted 55,
regressed 0, other 0. Total profile wall 3.134 s; peak RSS 107933696 bytes
(~103 MiB).

Frozen ceilings:

- internal total wall budget: **900 s** (`THREE_ARM_TOTAL_WALL_S`; ≈ 57× the
  projected mean 300-block wall of ~15.7 s). On expiry, remaining planned
  blocks are `resource_abort` and the five files are still written.
- per-paired-block soft cap: **15.0 s**
  (`THREE_ARM_PER_PAIRED_BLOCK_SOFT_CAP_S`; ≈ 123× the observed maximum of
  121.64 ms). On expiry after a completed block, remaining planned blocks are
  `resource_abort`.
- external command timeout: **T = 1800 s** (`timeout 1800`), 2× the internal
  total budget so the internal stop fires first and the evidence is written.
- memory envelope: `ulimit -v 2097152` (2 GiB virtual); the plan records
  `rss_bytes_max = 2147483648`, and the measured peak `rss_bytes_peak` is
  persisted in `aggregate_comparison.json` (profile ~103 MiB).

## 11. Frozen output root and schema

Root (relative to repo):
`.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`

Confirmed **ABSENT** at freeze. The CLI refuses an existing root before any
decoder call. Exactly five compact scalar-only files are written; no symbol
vectors, labels, disclosed values, decoded keys, raw seed bits, transcript raw
events or per-block coordinate lists are persisted:

1. `frozen_plan.json` — protocol, mode, created_utc, repository, run_seed,
   planned_blocks, q, n, epsilon, field{}, channel, order, arms[],
   seed_derivation{}, schedule{K, D_sets, new_coordinates, proof flags},
   static_comparator{}, disclosure_rule, restart_rule, rejection_rule{},
   label_domain{}, toeplitz{}, accounting{}, union_bound,
   outcome_precedence[], budget{}, refused_run_seeds[], attempt_consumption_point.
2. `per_block_three_arm_outcomes.json` — `n_blocks` and one record per block:
   `block_index, paired_match, metric_wall_s, static_wall_s, strict_wall_s,
   r1_wall_s, three_arm_wall_s, static{...}, strict_stop{...}, r1{...}`; each
   arm record is scalar-only and carries `outcome, exact, accepted_level,
   decode_failed_level, levels_invoked, tag_invocations,
   feedback_control_invocations, key_dependent_bits, public_seed_bits,
   feedback_control_bits, public_control_bits, nonfinite, truth_leak_violation,
   error_type, pre_symbol_errors, pre_bit_errors, symbol_errors, bit_errors,
   wall_s, rejected_levels[], decode_rejected_continue_count,
   terminating_level, terminating_k`.
3. `transcript_accounting.json` — per-arm incremental totals, independent
   recount, mismatch counts, transcript sha256; union-bound block;
   public-control split for all three arms.
4. `aggregate_comparison.json` — per-arm outcome totals, attempted/coverage,
   key-dependent totals and averages, tag/feedback/level totals, per-arm
   Wilson blocks, `r1_rejection_accounting{}` (rejection count, blocks,
   per-level and terminating-level histograms), disclosure comparison
   (integer rule `r1_total*100 <= 95*static_total`),
   `rescue_comparison_against_strict{}`, union bound, public control,
   transcript recount, truth-leak/nonfinite counts, decode error types,
   `hard_gates{}` (all booleans), `candidate`, bounded `claim_scope`,
   wall/RSS, resource stop flag.
5. `report.md` — bounded human-readable summary.

## 12. Wilson calculation and hard gates

One-sided 95% Wilson lower bound for exact recovery, successes = `exact`,
denominator = attempted (executed blocks; `resource_abort` excluded),
`z = 1.6448536269514722` (accepted Phase 5 `wilson_lower_bound`).

All 18 gates must hold; each is persisted as a boolean in `hard_gates`:

1. `frozen_plan_identity` — run seed 2026091350, 300 blocks, N=256, epsilon
   0.05, schedule (29,33,37,41,45);
2. `three_arm_identical_blocks` — every block `paired_match` true and 300
   records;
3. `outcome_buckets_disjoint_exhaustive_all_arms` — all three arms sum to 300;
4. `coverage_complete_all_arms` — all three arms attempted 300 (no
   `resource_abort`);
5. `r1_undetected_zero`;
6. `r1_exact_ge_285` — R1 exact >= 285;
7. `r1_wilson_lower_ge_0_90` — R1 Wilson LB >= 0.90;
8. `r1_avg_key_dependent_le_95pct_static` — integer-exact
   `r1_total * 100 <= 95 * static_total` with equal attempted denominators;
9. `frozen_order_nesting_and_schedule_consistency` — nesting proof flags plus
   every per-block record consistent with the frozen schedule/accounting
   (R1 records checked under the R1 rules: advance counts equal rejected
   levels, terminating levels match the frozen rules, no final-level
   rejection, no other-exception continuation);
10. `invocation_universe_equals_recount_all_arms` — tag invocations and
    feedback invocations of all three arms equal the literal recount;
11. `union_bound_consistent` — per-arm and total bounds equal the recounts;
12. `recount_zero_mismatch` — all three arms;
13. `truth_leak_zero` — all three arms;
14. `nonfinite_zero` — all three arms;
15. `resource_stop_preregistered`;
16. `feedback_counted` — strict-stop and R1 feedback universe/bits/split
    consistency;
17. `public_control_counted` — all three arms;
18. `strict_arm_pinned_consistency` — every strict-stop record passes the
    strict Phase 6 proof with zero rejections.

Only if all gates pass is `DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE`
emitted; otherwise `candidate` is null. The label is a synthetic development
signal only.

## 13. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental --mode three-arm-paired-dev-gate --run-seed 2026091350 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate
```

No flags may be added or changed. The output root must still be absent at
execution time. The single attempt is consumed at the first scientific
`sc_decode` call (static comparator arm, block 0). On any failure the attempt
stays consumed: no rerun, no seed change, no tuning, no partial credit.

The `python -m` invocation emits one cosmetic `runpy` `RuntimeWarning` because
the package `__init__` re-exports the module (the same pattern as Phase 5/6);
it is not an error and does not affect the run.

## 14. Forbidden-path proof

- `incremental.py` and `nbpolar_incremental.py` import only stdlib
  (`argparse, hashlib, json, sys, time, dataclasses, numbers, pathlib`), numpy,
  the accepted nbpolar Phase 1-6 modules and `formal_ir/shared.py`. No Model-F
  stored file, parquet, TTBin, DEV/EVAL, benchmark, sibling-checkout, SCL/CRC
  or rate-adaptation code path exists in either module; no import-time I/O; no
  global RNG; the only write target is the explicitly passed output root
  (created after the run, refused if present).
- `test_no_forbidden_markers_or_import_time_side_effects` scans both sources
  for `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`,
  `dev_seed`, `eval_seed`, `benchmark`, `sibling`, `artifact`, `results/`
  (zero matches), imports both modules in a fresh interpreter with a temp cwd
  (no file created), and the R1 test additionally proves the R1 test file
  never references the real queue root or the frozen seeds.
- Tests use temporary directories and injected/non-frozen seeds only; no real
  data, stored file, `comparison_bench/outputs_comparison/`, `results/` or
  sibling path is touched. The sibling checkout is used read-only as the
  pinned interpreter only.
- No file in the immutable Phase 5/6 evidence roots (`static_protocol_dev_gate/`,
  `paired_incremental_dev_gate/`) was opened, parsed, read or written; only a
  directory metadata listing (file names and mtimes) was recorded once during
  the closeout to confirm they were untouched. The real R1 output root
  `.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`
  is absent and must remain absent until the authorized execution.

## 15. Pre-EXECUTE checklist for the independent reviewer

1. Confirm this freeze doc matches the implemented constants
   (`R1_RUN_SEED`, `R1_TOEPLITZ_MASTER_SEED`, `R1_BANNED_RUN_SEEDS`,
   `R1_FROZEN_BLOCKS`, `FROZEN_K`, thresholds, budgets, seed derivation
   string, level index and arm-namespace conventions).
2. Recompute the five `D_i` sets and the nesting/new-coordinate lists.
3. Re-run the focused R1 suite, the Phase 6 suite and the Phase 5 suite
   (expected 17 + 17 + 16, full NB-Polar 170).
4. Confirm the 300-block command and output root above; confirm the root is
   absent and `STATUS.yaml` grants only the authorized flags with
   `attempts_used: 0`.
5. Confirm `git grep 2026091350 HEAD` and `git grep 2026091351 HEAD` are
   empty and that R1 tests never use the frozen seeds.
6. FAIL blocks execution; issues return to the operator for scoped repair and
   re-review.
