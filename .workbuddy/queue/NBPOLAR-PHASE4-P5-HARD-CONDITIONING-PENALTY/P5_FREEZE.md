# P5 freeze — NB-Polar Phase 4-P5 hard-L1 conditioning penalty

Rev 1 (2026-09-13). Frozen by the operator session under the exact user
authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond the packet, the
X02 provenance addendum and the user frozen-semantics text were invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No gate run has been executed. The single attempt is **0 consumed** at freeze;
it is consumed at the first gate L1 SC call (stream 0, block 0).
`STATUS.yaml` keeps `attempts_used: 0`. The real output root is **ABSENT**.

## 1. Scope

One powered Tier-Y paired gate at the X02-recommended dependent-L2 point: does a
correct-L1 oracle and a hard-candidate operational arm, on the same blocks and
disclosures, show a material operational penalty (oracle-only events) while
operational-only events stay structurally zero?  Synthetic injected tables only;
this is a single-point mechanism discriminator, not real-data FER, efficiency,
loss, key rate, qualification or promotion evidence; no N>256, no scalable or
list decoder, no cross-layer soft path, no adaptive K, no tuning, no cached
state, no rerun.  X02 is reconstructed from the frozen formulas and the accepted
P4 runner; the X02 execution body is neither executed nor imported.  No commit
or push.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/penalty_gate.py` (statistic/runner wrapper only) |
| tests | `comparison_bench/tests/test_nbpolar_penalty_gate.py` (9 focused tests) |
| internal dependency | accepted `formal_ir/nbpolar/two_layer.py` reused unchanged through `run_two_layer_block`, `layer_metric_tables`, `frozen_disclosure_sets`, `block_events`, `seed_bits_for`, `OUTCOMES`, `_abort_arm` |
| accepted predecessors reused unchanged | `prior.derive_p1/derive_p2/Provenance`, `algebra.make_gf32`, `construction.analytic_order` (through `two_layer.disclosure_coordinates`), `formal_ir/shared.toeplitz_tag` (inside the accepted runner) |
| changed accepted modules | **none** (`two_layer.py`, `prior.py`, `sc.py`, `transform.py`, `construction.py`, `protocol.py` untouched) |
| benchmark adapter | **none added** (the frozen command imports the module path directly; no re-export) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3) |
| untouched | all predecessor test files, frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, every existing evidence root |

## 3. Frozen point and injected model

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural-order
  transform; `q=32`, `N=256`; `epsilon1=0.05`; strong dependent-L2 profile
  `epsilon2(u1) = 0.02 + 0.36*u1/31` over the high-layer source value `u1` in
  `0..31` (mean exactly `0.20`); `K1=45`, `K2=140`.
- Dependent injected table: `P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)`,
  where `Ph` is the `epsilon1=0.05` q=32 marked-erasure kernel
  (`L(y|x) = eps/32 + (1-eps)[y==x]`) and `Pl` is the same kernel with
  per-high-value erasure probability `epsilon2(high)`.  The `[Alice,Bob]`
  `(1024,1024)` table is column-normalized to 1; max column-sum deviation is
  `3.774758283725532e-15 <= 1e-12` (asserted, never renormalized).
- `derive_p1`/`derive_p2` produce `P1 [U1,B] (32,1024)` and
  `P2 [U1,B,U2] (32,1024,32)`.  Unlike P4's independent-layer model, the `P2`
  rows now depend on `u1` through `epsilon2(u1)`.
- Pre-decoder table guard: `p2_maxdiff = max_{u1,u1',b,u2} |P2[u1,b,u2] -
  P2[u1',b,u2]|` is computed on the derived table **before any decoder call**
  and the runner refuses to decode if it is `< 0.30`.  Strong-profile expected
  value `0.34875`; measured `0.34875000000000267`, exactly equal to the value
  persisted by X02 (`workspace/probes/nbpolar_x02_dependent_l2_point_search/
  results.json`, config strong/45/140).  Closed form: `0.36 * 31/32`.
- Block sampling (documented deterministic draw order, one
  `np.random.default_rng(seed)` per stream): `high` uniform GF32, `low` uniform
  GF32, `B_high` erasure mask with `epsilon1` + replacement draws for erased
  positions, `B_low` erasure mask with the per-position `epsilon2(high)` +
  replacements; `B = 32*B_high + B_low`.  No counts, smoothing, floor or stored
  table is used; no global RNG.
- Alice transforms `U1 = polar_transform(high)`, `U2 = polar_transform(low)`;
  disclosed values are the actual GF32 entries of `U1[D1]` and `U2[D2]` (zeros
  are values, never sentinels).

## 4. Frozen disclosure sets

`D1 = sorted(analytic_order(0.05, 256)[:45])` (45 coordinates ascending):

```text
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21,
 22, 24, 25, 26, 32, 33, 34, 35, 36, 40, 48, 64, 65, 66, 68, 72, 80, 96,
 128, 129, 130, 132, 136, 144]
```

`D2 = sorted(analytic_order(0.20, 256)[:140])` (140 coordinates ascending):

```text
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
 57, 58, 60, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
 80, 81, 82, 83, 84, 85, 86, 88, 89, 90, 92, 96, 97, 98, 99, 100, 101, 102,
 104, 105, 106, 108, 112, 113, 114, 128, 129, 130, 131, 132, 133, 134, 135,
 136, 137, 138, 139, 140, 141, 142, 144, 145, 146, 147, 148, 149, 150, 152,
 153, 154, 160, 161, 162, 163, 164, 165, 168, 176, 192, 193, 194, 196, 200,
 208, 224]
```

Both are published actual GF32 values, `SC known_positions = sorted(D)`, and
every coordinate is disclosed exactly once per layer.  `D2` uses the profile
mean `0.20` (not the per-`u1` vector).

## 5. Frozen streams, masters and arms

- Stream seeds **2026091470, 2026091471, 2026091472**, 128 paired blocks each
  (384 pairs in one attempt); public tag master `stream_seed + 10000` =
  **2026101470, 2026101471, 2026101472**.  All six values are absent from HEAD
  (`git grep` returns no matches); the seeds are accepted and are not in the
  refused set.
- Refused consumed seeds (29 values, persisted in `frozen_plan.json.
  refused_run_seeds`): `2026091200..2026091213`, `2026091314..2026091321`,
  `2026091330`, `2026091340`, `2026091341`, `2026091350`, `2026091351`, plus
  the P4 gate streams `2026091360`, `2026091361`.  The frozen P5 seeds
  `2026091470..1472` are accepted.
- Per block the wrapper calls accepted
  `two_layer.run_two_layer_block(block_index, high, low, bob, ...,
  toeplitz_master=seed+10000)` exactly once; the operational and isolated-oracle
  arms share the block, the disclosures and the stream master.  L1: one SC call
  with `D1/U1[D1]`, source-domain hard candidate `sc1.x_hat`.  Operational L2:
  `P2_hat` gathered on Bob + candidate, `CANDIDATE_CONDITIONED`, one fresh SC
  call with `D2/U2[D2]`.  Oracle L2: `P2_true` gathered on Bob + true high layer,
  `ORACLE_CONDITIONED`, one fresh SC call with the same `D2/U2[D2]`.  Each arm
  invokes exactly one final 64-bit Toeplitz tag under its own arm label.

## 6. Four-cell paired table and the structural impossibility

Each of the 384 pairs is classified exactly once:

| cell | rule |
|---|---|
| `both_exact` | operational exact AND oracle exact |
| `oracle_only` | NOT operational exact AND oracle exact |
| `operational_only` | operational exact AND NOT oracle exact |
| `neither` | NOT operational exact AND NOT oracle exact |

The four cells are disjoint and exhaustive over 384.  `operational_only` is
structurally impossible when the L1 candidate is correct: a correct candidate
makes the operational `P2_hat` bitwise identical to the oracle `P2_true`, so
both fresh L2 SC calls receive identical arguments and produce identical labels
and tags; when the candidate is wrong, the operational label cannot match the
true label, so the operational arm cannot be exact.  The gate requires
`operational_only == 0` and the discriminator includes it.

## 7. Integrity gates (persisted as booleans; all must pass)

1. `pairing_coverage_complete` — every planned pair present (384/384 at the
   frozen run); both arms on each pair;
2. `p2_maxdiff_at_least_0p30` — pre-decoder table guard value;
3. `provenance_candidate_oracle_complete` — 384/384 operational arms
   `CANDIDATE_CONDITIONED` and 384/384 oracle arms `ORACLE_CONDITIONED`;
4. `operational_truth_leak_zero` — truth-isolation sentinel violations 0;
5. `undetected_zero` — both arms (tag pass and not exact is never success);
6. `nonfinite_zero` — both arms;
7. `resource_abort_zero` — both arms;
8. `cells_disjoint_exhaustive` — the four cell counts partition the pairs;
9. `disclosures_exact_and_transcript_recount_zero` — per fully invoked arm
   exactly `5*(K1+K2)+64 = 989` key-dependent bits, `2623` public control bits
   per tag invocation, and an independent literal transcript recount (parses the
   arm from the event id) equals the incremental per-arm and total totals with
   zero mismatch; `tag_invocations == 2623`-seeded tag count;
10. `attempt_accounting_at_frozen_point` — exactly one allowed attempt, zero
    consumed before this run, one consumed by this single pass, zero retries,
    and coverage equal to the planned pairs.

## 8. Scientific discriminator (persisted values + booleans)

- `oracle_exact >= 365` (out of 384);
- `operational_only == 0`;
- `X = oracle_only` count; the one-sided 95% exact lower bound `L` solves

  ```text
  sum_{j=X}^{384} C(384,j) L^j (1-L)^(384-j) = 0.05
  ```

  by monotone bisection on `L in [0,1]` (the tail `P[Bin(384,L) >= X]` is
  increasing in `L`); stdlib `math` only, log-space terms; frozen edge handling
  `X=0 -> L=0.0` and `X=384 -> L=0.05**(1/384)`;
- discriminator passes iff `oracle_exact >= 365` AND `operational_only == 0`
  AND `L > 0.30`.

No binomial interval is applied to the difference of the two marginal rates.

`HARD_L1_CONDITIONING_PENALTY_CANDIDATE` iff all integrity gates pass AND the
discriminator passes at the 384-pair shape; `HARD_L1_CONDITIONING_PENALTY_
NOT_CONFIRMED` iff integrity passes but the discriminator fails; if any
integrity gate fails the summary persists `integrity_all_pass=false` and the
failing gate names in frozen order (the operator return maps this to
`BLOCKED(<earliest gate>)`).  The runner never claims FER, efficiency,
qualification or promotion.

## 9. Accounting and transcript

Per executed arm per pair: L1 disclosure `5*45 = 225`, L2 disclosure
`5*140 = 700` when L2 is invoked, tag `64` when the final tag is invoked; a
fully invoked arm totals `5*(45+140) + 64 = 989`.  Public control is 2623 bits
per tag invocation (N=256), counted separately.  Canonical events come from the
accepted `two_layer.block_events` (L1 disclosure, L2 disclosure, verification
tag, per arm, in order); the P5 wrapper performs its own independent literal
recount and requires zero mismatch against its incremental totals.

## 10. Attempt consumption, no-rerun / no-tune

The single attempt (`attempts_allowed: 1`, `attempts_used: 0` at freeze) is
consumed at the **first gate L1 SC call (stream 0, block 0)**.  On any failure
the attempt stays consumed: no rerun, no seed change, no table/K/threshold/set
change, no partial credit.  The p2 table build, the `p2_maxdiff` guard, the
transcript recount and the discriminator computation make no decoder calls.
`STATUS.yaml` is not updated by the runner; the attempt ledger stays with the
main thread and the operator return.

## 11. Budgets and output root

- Internal wall budget `total_wall_s = 3600.0`; on expiry the remaining planned
  blocks are `resource_abort` and the five files are still written.
- External command: `timeout 3600` and `ulimit -v 2097152` (2 GiB virtual);
  plan records `rss_bytes_max = 2147483648`.
- Output root (relative to the repository):
  `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
  — confirmed **ABSENT** at freeze and must remain absent until an authorized
  execution.  The CLI refuses an existing root before any decoder call and
  creates the root only after the run.
- Exactly five compact scalar-only files are written:

1. `frozen_plan.json` — protocol/mode/created_utc/repository, out_root, seeds,
   masters, `blocks_per_seed`, `planned_pairs`, q/n/k1/k2/epsilon1, profile and
   formula, field, dependent-table formula/kernel/normalization deviation/
   `p2_maxdiff` + definition + floor, disclosure rule + `D1`/`D2` lists, arms,
   pairing, sampling order, provenance rules, cells + cell rule, integrity gate
   order, discriminator definition, attempt consumption point and accounting,
   budgets, refused seeds, frozen command, bounded claim scope.
2. `per_block_paired_outcomes.json` — one scalar record per pair:
   `stream_seed`, `block_index`, `cell`, and per-arm `outcome, exact,
   label_match, tag_pass, l1_provenance, l2_provenance, l1_executed,
   l1_decode_failed, l2_invoked, l2_skipped_by_l1_failure, l2_decode_failed,
   tag_invoked, key_dependent_bits, public_control_bits, nonfinite,
   truth_leak_violation, l1_error_type, l2_error_type, wall_s`.  No raw symbols,
   labels, disclosed values or seed bits.
3. `transcript_accounting.json` — event count/types, incremental totals (total
   and per arm), independent literal recount, mismatch count/list, public
   control per tag, fully invoked arm bits, per-pair disclosure bits.
4. `aggregate_summary.json` — four cells, marginals and per-arm outcome totals,
   `X`, `lower_bound` + definition, all integrity gates, `integrity_all_pass`,
   failing gate names, provenance counts, discriminator booleans, outcome label,
   accounting totals, transcript summary, attempt accounting, wall_s,
   rss_bytes_peak, resource stop flag, bounded claim scope.
5. `report.md` — bounded human-readable summary.

## 12. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate --n 256 --epsilon1 0.05 --profile strong --k1 45 --k2 140 --seeds 2026091470 2026091471 2026091472 --blocks-per-seed 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate
```

No flag may be added or changed.  The output root must still be absent at
execution time.

## 13. Forbidden-path proof

- `penalty_gate.py` imports only stdlib (`argparse`, `json`, `math`, `sys`,
  `time`, `dataclasses`, `numbers`, `pathlib`, optional POSIX `resource`),
  numpy, and the accepted `two_layer`/`algebra`/`prior` modules.  No stored data
  product, no columnar/TT-binary reader, no real frame, no DEV/EVAL stream, no
  method adapter, no sibling-checkout code path, no fast-transform or scalable
  decoder, no list decoder and no cross-layer soft-prior path exists; the runner
  refuses `n != 256`, profile `!= strong`, `(k1,k2) != (45,140)` and
  `epsilon1 != 0.05`; no import-time I/O; no global RNG (`np.random.default_rng`
  only); the only write target is the explicitly passed output root (refused if
  present, created after the run).
- `test_p5_no_forbidden_markers_or_import_time_effects` scans the module source
  for `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`,
  `dev_seed`, `eval_seed`, `benchmark`, `sibling`, `artifact`, `results/`,
  `fwht`, `scl/crc`, `app_fed`, `app_prior`, `get_l1_app`, `pandas`, `pyarrow`,
  `scipy` (zero matches), rejects non-`default_rng` `np.random.<call>`, imports
  the module in a fresh interpreter with a temp cwd (no file created) and proves
  the test file never references the real queue root or uses the frozen seeds.
- Tests use temporary directories, injected/tiny inputs and fresh seeds
  `2026091480..2026091485` only; no stored data, no
  `comparison_bench/outputs_comparison/`, no `results/` and no sibling path is
  touched.  The sibling checkout is used read-only as the pinned interpreter.
- No file in any accepted evidence root (`static_protocol_dev_gate/`,
  `paired_incremental_dev_gate/`, `three_arm_paired_dev_gate/`,
  `empirical_prior_sc_diagnostic/`, `two_layer_operational_sc_gate/`) was
  opened, parsed, read or written.  Nothing was committed or pushed.

## 14. Pre-execution evidence recorded at freeze (non-frozen inputs only)

- Focused suite: `comparison_bench/tests/test_nbpolar_penalty_gate.py` — 9
  passed (5.32 s, `-q -p no:cacheprovider`).
- Full accepted predecessor suite plus the new file: 201 passed (104.98 s).
  The 192 P4-equivalent predecessors are all green.
- CLI smoke (NOT the gate; temp root `/tmp/opencode/p5_cli_smoke`, seed
  2026091486, 2 blocks): exit 0, exactly five files, `integrity_all_pass=true`,
  `outcome_label=HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED` (2-pair shape, not
  the 384 shape; `X=1`, `L=0.00013356736655250473`).  Refusals: existing root
  exit 2, banned seed 2026091360 exit 2, profile `weak` exit 2; the refused
  roots were never created.
- Bisection residual at the root is `<= 3.5e-16` against an independent direct
  product-sum tail for X in {1, 2, 200, 365, 370, 380}; small-n cross-checks at
  (10,3), (10,7), (20,13), (50,40) agree within 1e-9.

## 15. Pre-EXECUTE checklist for the independent reviewer

1. Confirm this freeze doc matches the implemented constants and semantics in
   `penalty_gate.py` (point, profile, D1/D2, seeds, masters, refused set, table
   formula, `p2_maxdiff` definition/floor, sampling order, five-file schema,
   gates, discriminator, bisection edge cases, attempt point, budgets).
2. Recompute D1/D2 from `analytic_order` and the `p2_maxdiff` value from the
   frozen table; compare with the X02 persisted value.
3. Re-run the focused suite and the full NB-Polar predecessor suite (expected
   9 + 192 = 201 passed) and the tiny CLI smoke with non-frozen seeds.
4. Confirm the frozen command, the absent output root, `attempts_used: 0`, the
   AUTHORIZED STATUS flags, and that the runner refuses the consumed seeds.
5. Adjudicate: P4's `BANNED_RUN_SEEDS` did not include 2026091360/2026091361,
   and P5 refuses them in addition (P4 evidence already exists at those
   streams); the X02 point is reconstructed from formulas, not from the X02
   body.
6. Confirm the gate runner is never invoked with the frozen seeds before the
   authorized execution and that no file outside the allowed list changed.
7. FAIL blocks execution; issues return to the operator for scoped repair and
   re-review.
