# P6 freeze — NB-Polar Phase 4-P6 adaptive hard-L1 disclosure gate

Rev 1 (2026-09-13). Frozen by the operator session under the exact user
authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond the packet, the
accepted P5 conventions and the X04/X05 planning evidence were invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No gate run has been executed. The single attempt is **0 consumed** at freeze;
it is consumed at the first scientific SC call (stream 2026091550, block 0,
static L1). `STATUS.yaml` keeps `attempts_used: 0`. The real output root is
**ABSENT**.

## 1. Scope

One powered Tier-Y paired gate at the X05 frontier schedule: does the adaptive
worst-first hard-L1 ladder `K1=[45,60,72,112]` at the fixed dependent-L2 point
`K2=140` preserve the static `K1=112` endpoint's exact recovery while reducing
mean key-dependent disclosure by at least 15%?  Synthetic injected tables only;
this is a single-point mechanism result, not real-channel FER, efficiency,
loss, key rate, qualification or promotion evidence; no N>256, no scalable or
list decoder, no cross-layer soft path, no learned policy, no tuning, no
cached state, no rerun.  X04/X05 are read-only design inputs and are not
executed or imported by the gate; no commit or push.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core + CLI | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py` |
| tests | `comparison_bench/tests/test_nbpolar_adaptive_l1.py` (15 focused tests) |
| package export | `formal_ir/nbpolar/__init__.py` adds only the `adaptive_l1` names |
| internal dependencies (unchanged) | `penalty_gate.build_dependent_joint_table`/`profile_epsilon2`/`sample_dependent_block`/`p2_cross_u1_maxdiff`/`require_p2_maxdiff`/`P2_MAXDIFF_FLOOR`/`PROFILE_FORMULAS`; `incremental.build_nested_schedule`; `two_layer` primitives (`_decode_layer`, `_truth_isolation_sentinel`, `_checked_layer`, `layer_metric_tables`, `disclosure_coordinates`, `seed_bits_for`, `labels_to_bits`, `polar_transform`, `OUTCOMES`); `prior` metrics/provenance; `algebra.make_gf32`; `shared.toeplitz_tag`/`canonical_event`/`verification_union_bound` |
| changed accepted modules | **none** (`sc.py`, construction, prior semantics, `two_layer.py`, `penalty_gate.py`, `incremental.py`, P5/X03/X03b/X04/X05 and every earlier evidence root untouched) |
| benchmark adapter | **none added** (the frozen command imports the module path directly; the unchanged `FrameBatch/IRRunConfig/IRRunResult` single-layer adapter contract does not admit this paired two-layer statistic without a schema change) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3) |
| untouched | frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, every existing evidence root |

## 3. Frozen point, model and disclosure sets

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural-order
  transform; `q=32`, `N=256`; `epsilon1=0.05`; strong dependent-L2 profile
  `epsilon2(u1) = 0.02 + 0.36*u1/31` over the high-layer source value `u1` in
  `0..31` (mean exactly `0.20`).
- Dependent injected table
  `P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)` from the accepted
  `penalty_gate.build_dependent_joint_table(profile="strong")`; column-sum
  deviation `3.774758283725532e-15 <= 1e-12` (asserted, never renormalized);
  `p2_maxdiff = 0.34875000000000267` (closed form `0.36*31/32`) and the
  pre-decoder floor `0.30` is checked before any decoder call.
- Adaptive nested worst-first L1 prefixes
  `D1(K1_j) = sorted(analytic_order(0.05, 256)[:K1_j])` for
  `K1 in [45, 60, 72, 112]`; the accepted `build_nested_schedule` proves
  `strict_nesting`, `order_prefix_matches` and `new_coordinates_disjoint`
  (increments partition `D1(112)`); `D1(45)` equals the accepted
  `two_layer.frozen_disclosure_sets` `D1`.
- Fixed L2 prefix `K2=140`:
  `D2 = sorted(analytic_order(0.20, 256)[:140])`, disclosed once per arm/block
  and decoded with the same disclosed values at every adaptive stage.
- Sampler draw order (accepted): per stream one
  `np.random.default_rng(stream_seed)`; per block `high` uniform GF32, `low`
  uniform GF32, `B_high` erasure mask with `epsilon1` + replacements, `B_low`
  erasure mask with the per-position `epsilon2(high)` + replacements;
  `B = 32*B_high + B_low`.  No global RNG.

## 4. Frozen streams, masters and refused seeds

- Stream seeds **2026091550, 2026091551, 2026091552, 2026091553, 2026091554**,
  128 common blocks each (640 paired blocks in one attempt); public Toeplitz
  master `stream_seed + 10000` = **2026101550..2026101554**.
- Freshness at freeze: `git grep` over HEAD and a full-worktree `rg` (excluding
  this packet) find no prior use of the five seeds or the five masters.  No
  accepted/consumed Phase 1-6 or X-probe stream overlaps them.
- Refused consumed seeds (persisted in `frozen_plan.json.refused_run_seeds`):
  `2026091200..2026091213`, `2026091314..2026091321`, `2026091330`,
  `2026091340`, `2026091341`, `2026091350`, `2026091351`, `2026091360`,
  `2026091361`, `2026091400..2026091404`, `2026091410..2026091414`,
  `2026091420..2026091424`, `2026091430..2026091434`, `2026091450..2026091452`,
  `2026091470..2026091472`, `2026091490..2026091494`, `2026091510..2026091514`.
  The set is a strict superset of `penalty_gate.BANNED_SEEDS` and
  `incremental.R1_BANNED_RUN_SEEDS`; the frozen streams are accepted.

## 5. Frozen arm semantics

**Static arm (per block).** One fresh L1 SC call at `K1=112` on the P1 prior
metric (`PRIOR_ONLY`, Bob only); one fresh candidate-conditioned L2 SC call at
`K2=140` (`CANDIDATE_CONDITIONED`, metric gathered from Bob and the hard L1
candidate); label `low_hat + 32*high_hat`; exactly one 64-bit Toeplitz tag under
arm `static`, level 1.  Outcomes: `exact` (tag pass AND label == truth),
`undetected` (tag pass and not exact; never merged with exact), `verify_failed`,
`decode_failed` (L1/L2 SC exception or nonfinite marginals; no tag),
`resource_abort`.  Fully invoked cost `5*(112+140)+64 = 1324`.

**Adaptive arm (per block).** For each one-based stage `j` with `K1_j` in
`[45,60,72,112]`:

1. restart the L1 SC from the **ORIGINAL** P1 metric with the cumulative
   `D1(K1_j)` prefix;
2. if the L1 candidate exists, restart the candidate-conditioned L2 SC from the
   **ORIGINAL** P2 table gathered by that stage's hard candidate with `D2`;
3. assemble `low_hat + 32*high_hat` and verify the full 10-bit label with one
   64-bit tag under arm `adaptive`, level `j`;
4. tag match -> accept and stop (`exact` iff label == truth, otherwise
   `undetected`); tag mismatch before `K1=112` -> one public one-bit feedback,
   disclose only the next `D1` increment, advance; mismatch at `K1=112` ->
   `verify_failed`;
5. a nonterminal `ImpossibleDisclosedValueError` -> no candidate, no tag, one
   feedback bit, advance; at the terminal stage -> `decode_failed`;
6. every other exception fails closed (`decode_failed`, no tag, no feedback).

No decoder object, metric, partial sum, candidate label or tag seed is reused
between stages (every stage calls a fresh SC on the original metric; every L2
metric is freshly gathered).  Alice truth enters only sampling, disclosed
values, tag construction and scoring; it never enters an undisclosed operational
metric, decision or tag seed (per-block mutation sentinel required).

## 6. Frozen accounting and union bound

Per arm per block at the one-based termination/exhaustion stage `j` with
`K1=K_j`:

```text
key_dependent_bits = 5*(K_j+140) + 64*tag_invocations
public_seed_bits   = 2623*tag_invocations
feedback_bits      = 1*feedback_invocations
public_control     = public_seed_bits + feedback_bits
```

Realized from executed disclosures: cumulative L1 prefix `5*K_j`, the
once-per-arm/block L2 disclosure `5*140` when L2 was invoked, one 64-bit tag per
invocation.  A decode rejection creates no tag.  The only corner where the
literal formula and the executed-disclosure realization differ is an arm that
never produced any candidate (all four L1 decodes rejected by impossible
disclosure or failed): no L2 disclosure was ever sent, so `5*K_j` is counted
without the `5*140`; the count of such blocks is persisted as
`no_l2_exhaustion_blocks` (expected zero).  Fully invoked values:
`K1=45 -> 989`, `60 -> 1064`, `72 -> 1124`, `112 -> 1324` (equals the static
endpoint).  Tag control is 2623 public seed bits per tag (N=256).  The gate
performs its own independent literal recount of the canonical transcript events
(parses the arm from the event id, sums fields) and requires zero mismatch
against the incremental per-arm and total totals.  Verification union bound
`min(1.0, total_tag_invocations * 2**-64)`.

## 7. Output root and five-file schema

Output root (relative to the repository):
`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
— confirmed **ABSENT** at freeze and until an authorized execution; the runner
refuses an existing root before any decoder call and creates the root only after
the run.  Exactly five compact scalar-only files:

1. `frozen_plan.json` — protocol/mode/created_utc/repository/out_root, seeds,
   masters, blocks/pairs, point (q/n/epsilon1/profile/formula/field), dependent
   table (formula/deviation/`p2_maxdiff`+definition+floor), `k1_levels`,
   `k2`, `static_k1`, disclosure rule + `D1_by_level`/`D1_new_positions_by_level`/
   `D2`, nested assertions, arms, restart/tag/feedback/impossible rules, truth
   scope, seed derivation, accounting, cells/cell rule, gate order, scientific
   gates, attempt point/accounting, budgets, refused seeds, frozen command,
   bounded claim scope.
2. `per_block_paired_outcomes.json` — 640 scalar records: `stream_seed`,
   `block_index`, `paired_cell`, and per arm `outcome, exact, label_match,
   tag_pass, l1_provenance, l2_provenance, l1_executed, l1_decode_failed,
   l2_invoked, l2_decode_failed, tag_invoked, levels_invoked, tag_invocations,
   feedback_invocations, termination_stage, termination_k1,
   key_dependent_bits, public_seed_bits, feedback_bits, public_control_bits,
   nonfinite, truth_leak_violation, l1_error_type, l2_error_type, wall_s`.
   No symbol, label, disclosed-value, decoded-key or raw-seed payloads.
3. `transcript_accounting.json` — event counts/types, per-arm incremental
   totals and independent literal recount (key-dependent/public-seed/feedback/
   public-control bits, tag/feedback invocations), mismatch count/list,
   2623 public bits per tag, fully invoked values by level, union bound.
4. `aggregate_summary.json` — outcome totals per arm, four cells, adaptive
   termination stage/K1 histograms, mean/total disclosure, absolute and
   percentage saving, tag/feedback counts, public-control totals, union bound,
   per-stream breakdown, planning-only `f`, all integrity + scientific gates as
   booleans, failing gate names, result label, wall_s, rss_bytes_peak,
   resource-stop flag, attempt accounting, bounded claim scope.
5. `report.md` — bounded human-readable summary.

## 8. Integrity gates (all persisted as booleans; all must pass)

1. `pairing_coverage_complete` — 640/640 paired blocks;
2. `stream_block_identity_exact` — the exact stream/block product;
3. `result_buckets_disjoint_exhaustive` — every arm outcome in the accepted
   taxonomy, per-arm counts partition the blocks, and the per-record
   structural/accounting proof holds;
4. `d1_exactly_nested_and_d2_disclosed_once` — strictly nested `D1` prefixes,
   `new_positions` partition, exactly one `D2` disclosure per arm/block;
5. `provenance_and_truth_isolation_complete` — L1 `PRIOR_ONLY`, L2
   `CANDIDATE_CONDITIONED`, zero truth-isolation sentinel violations;
6. `undetected_zero`;
7. `nonfinite_zero`;
8. `resource_abort_zero`;
9. `transcript_recount_mismatch_zero` — incremental equals independent literal
   recount per arm and in total;
10. `tag_feedback_public_control_accounting_and_union_bound_exact` — per-record
    arithmetic, event public bits (2623 per tag, 1 per feedback), record sums
    equal the incremental totals, union bound exact;
11. `wall_rss_within_frozen_limits` — wall <= 3600 s and RSS <= 2 GiB;
12. `attempt_seed_accounting_exact` — the frozen attempt record, distinct
    non-refused seeds, planned coverage.

## 9. Scientific gates and outcome labels

- `static_exact_at_least_620_of_640` — static exact `>= 620` at the frozen
  640-pair shape (non-frozen shapes can never emit a candidate label);
- `adaptive_exact_equals_static_exact`;
- `paired_adaptive_only_zero_and_static_only_zero`;
- `leakage_100_adaptive_le_85_static` — exact integer
  `100*adaptive_total_key_dependent <= 85*static_total_key_dependent`.

All integrity + scientific gates true -> `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`.
Integrity true and any scientific gate false ->
`ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED`.  Any integrity failure ->
`integrity_all_pass=false` with the failing gate names in frozen order (the
operator maps this to `BLOCKED(<earliest gate>)`).  The label never claims FER,
efficiency, key rate, qualification or promotion; `undetected` is never merged
with `exact`; planning-only `f` is not real-channel efficiency.

## 10. Attempt consumption, no-rerun / no-tune, budgets

The single attempt (`attempts_allowed: 1`, `attempts_used: 0` at freeze) is
consumed at the **first scientific SC call (stream 2026091550, block 0, static
L1)**.  On any failure the attempt stays consumed: no rerun, no seed change, no
table/K/threshold/set change, no partial credit.  The table build, the
`p2_maxdiff` guard, the nested proof, the transcript recount and the gate
computation make no decoder calls.  `STATUS.yaml` is not updated by the runner;
the attempt ledger stays with the main thread and the operator return.
Budgets: internal wall cap 3600 s (on expiry the remaining blocks are
`resource_abort` and the five files are still written); external
`timeout 3600` and `ulimit -v 2097152` (2 GiB).

## 11. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 --n 256 --epsilon1 0.05 --profile strong --k1-levels 45 60 72 112 --k2 140 --seeds 2026091550 2026091551 2026091552 2026091553 2026091554 --blocks-per-seed 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate
```

No flag may be added or changed.  The output root must still be absent at
execution time.

## 12. Absent-target and forbidden-path proof

- `test ! -e .workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/
  paired_adaptive_gate` returns absent at freeze.
- `adaptive_l1.py` imports only stdlib (`argparse`, `hashlib`, `json`, `sys`,
  `time`, `dataclasses`, `numbers`, `pathlib`, optional POSIX `resource`),
  numpy, and the accepted NB-Polar modules listed in section 2.  No stored data
  product, no columnar/TT-binary reader, no real frame, no DEV/EVAL stream, no
  method adapter, no sibling-checkout code path, no fast-transform, scalable or
  list decoder, no soft-APP path, no learned policy, no import-time I/O, no
  global RNG (`np.random.default_rng` only); the runner refuses `n != 256`,
  profile `!= strong`, `k1_levels != [45,60,72,112]`, `k2 != 140`,
  `epsilon1 != 0.05`, and every refused seed; the only write target is the
  explicitly passed output root (refused if present, created after the run).
- `test_p6_no_forbidden_markers_or_import_time_effects` scans the module source
  for `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`,
  `dev_seed`, `eval_seed`, `benchmark`, `sibling`, `artifact`, `results/`,
  `fwht`, `scl/crc`, `app_fed`, `app_prior`, `get_l1_app`, `pandas`, `pyarrow`,
  `scipy` (zero matches), rejects non-`default_rng` RNG calls, imports the
  module in a fresh interpreter with a temp cwd (no file created) and proves the
  test file never references the real queue root or uses the frozen seeds.
- Tests use temporary directories, injected/tiny inputs and fresh test seeds
  `2026091560..2026091566` only; no stored data,
  `comparison_bench/outputs_comparison/`, `results/` or sibling path is touched
  (the sibling checkout is the pinned interpreter only).
- No file in any accepted evidence root (`static_protocol_dev_gate/`,
  `paired_incremental_dev_gate/`, `three_arm_paired_dev_gate/`,
  `empirical_prior_sc_diagnostic/`, `two_layer_operational_sc_gate/`,
  `paired_penalty_gate/`, X02/X03/X03b/X04/X05 probe roots) was opened, parsed,
  read or written.  Nothing was committed or pushed.

## 13. Pre-execution evidence recorded at freeze (non-frozen inputs only)

- Focused suite: `comparison_bench/tests/test_nbpolar_adaptive_l1.py` — 15
  passed (8.20 s, `-q -p no:cacheprovider`); the plain-python runner reports
  `15/15 passed`.
- Full accepted predecessor suite plus the new file:
  `comparison_bench/tests/test_nbpolar_*.py` — **216 passed** (104.28 s,
  fresh `/tmp` basetemp; 201 predecessors + 15 new).
- CLI smoke (NOT the gate; temp root `/tmp/opencode/p6_cli_smoke`, seed
  2026091566, 2 blocks): exit 0; exactly five files; `integrity_all_pass=true`;
  `outcome_label=ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED` (2-pair shape);
  cells 2/0/0/0; static mean 1324.0, adaptive mean 989.0, saving 25.30%.
  Refusals: existing root exit 2, banned seed 2026091510 exit 2, profile
  `weak` exit 2; refused roots were never created.
- Frozen-table reconstruction: `p2_maxdiff = 0.34875000000000267`,
  column deviation `3.774758283725532e-15`, nested proof flags all true,
  planning denominator `256*H(A|B) = 546.3150909520141` with
  `H(A|B) = 2.134043324031305` matching the accepted X04/X05 values exactly.
- Frozen seeds and masters absent from HEAD and the worktree; the ground output
  root absent; `attempts_used: 0`; no gate run executed with the frozen seeds.

## 14. Pre-EXECUTE checklist for the independent reviewer

1. Confirm this freeze matches the implemented constants and semantics in
   `adaptive_l1.py` (point, profile, table/floor, D1/D2, seeds/masters, refused
   set, arm restart/tag/feedback/impossible rules, accounting, gates, labels,
   attempt point, budgets).
2. Recompute the nested `D1` sets, `D2`, `p2_maxdiff`, `H(A|B)` and the
   fully-invoked accounting values from the accepted modules.
3. Re-run the focused suite and the full NB-Polar predecessor suite (expected
   15 + 201 = 216 passed) plus a tiny CLI smoke with a non-frozen seed.
4. Confirm the frozen command verbatim, the absent output root,
   `attempts_used: 0`, the authorized STATUS flags, the fresh streams/masters
   and that the runner refuses the consumed seeds and each wrong point.
5. Adjudicate: the implemented accounting realizes the frozen formula from
   executed disclosures with the documented no-candidate corner; the static arm
   runs first so the attempt point is the static L1 call at stream 0, block 0.
6. Confirm no gate run occurred with the frozen seeds and that no file outside
   the allowed list changed.
7. FAIL blocks execution; issues return to the operator for scoped repair and
   re-review.
