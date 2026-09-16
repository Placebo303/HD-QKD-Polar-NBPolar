# P4 freeze — NB-Polar Phase 4-P4 two-layer operational SC

Rev 1 (2026-09-13). Frozen by the operator session under the exact user
authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond the packet, the
Phase4-P0 contract and the user frozen-semantics text were invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No gate run has been executed. The single attempt is **0 consumed** at freeze;
it is consumed at the first gate SC call (block 0, operational L1 `sc_decode`).
`STATUS.yaml` keeps `attempts_used: 0`. The real output root is **ABSENT**.

## 1. Scope

Close the omitted Phase-4 dependency with the smallest two-stage SC closed
loop: Bob-only P1 → L1 SC → source-domain hard L1 candidate → Bob+candidate
P2_hat → fresh L2 SC → `low_hat + 32*high_hat` → exactly one final 64-bit
Toeplitz tag, paired on the same blocks and disclosures with a strictly
isolated true-L1 oracle diagnostic arm. Synthetic injected tables only; this
is an interface gate, not real-data FER, leakage efficiency, key rate,
qualification or promotion evidence; no `f<=1.3` claim, no SCL/Phase 7, no
adaptive K, no tuning, no cached state, no rerun. No commit or push.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py` |
| tests | `comparison_bench/tests/test_nbpolar_two_layer.py` (12 tests, P4-A01..A09 + failure taxonomy + A11 + forbidden-marker/import checks) |
| benchmark adapter | **none added** (documented decision in `P4_IMPLEMENTATION_NOTES.md`; the accepted `IRMethod`/`FrameBatch` contract is the single-layer `low half constant zero` convention and does not require or admit this two-layer gate without a schema change) |
| re-exports | `__init__.py` unchanged; the frozen command imports the module path directly |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3) |
| accepted predecessors reused unchanged | `prior.derive_p1/derive_p2/build_p1_metrics/gather_p2_metrics/probs_to_symbol_metric/SymbolMetric/Provenance`, `transform.polar_transform`, `sc.sc_decode` / `ImpossibleDisclosedValueError` / `NumericNonfiniteError`, `construction.analytic_order`, `shared.toeplitz_tag/canonical_event/transcript_summary` |
| untouched | Phase 5 `protocol.py`, Phase 6/R1 `incremental.py`, `methods/nbpolar_*.py`, all predecessor test files, frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, every existing evidence root |

## 3. Frozen point and injected model

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural-order
  transform; `q=32`, `N=256`; `epsilon1=0.05` (L1/high layer),
  `epsilon2=0.20` (L2/low layer).
- Generative model: `A = 32*high + low` with `high`, `low` iid uniform GF32;
  independent layer-erasure observation `B_high = high` w.p. `1-epsilon1`
  else uniform over full GF32, `B_low = low` w.p. `1-epsilon2` else uniform,
  `B = 32*B_high + B_low`.
- Table: the `[Alice,Bob]` `(1024,1024)` table is built explicitly as
  `f[a,b] = Ph(b_high|a_high) * Pl(b_low|a_low)` with
  `L(y|x) = epsilon/32 + (1-epsilon)*[y==x]`.  Because `A` and `B` are both
  uniform, `f` is exactly `P(A|B) = P(B|A)`, i.e. the accepted column
  normalized conditional; max column-sum deviation is `9.5e-15 <= 1e-12`.
  `derive_p1`/`derive_p2` produce `P1 [U1,B] (32,1024)` and
  `P2 [U1,B,U2] (32,1024,32)`.
- Generative/table equivalence: table-derived `P1`/`P2` equal the model
  conditionals by construction (`P1[u1,b] = Ph(b_high|u1)`,
  `P2[u1,b,u2] = Pl(b_low|u2)`); per-block sampling uses the explicit
  run-seed RNG in the frozen order `high`, `low`, then the `B_high` and
  `B_low` observations (erasure mask, then replacement draws for erased
  positions only).  No counts, smoothing, floor or stored table is used.
- Alice transforms `U1 = polar_transform(high)`, `U2 = polar_transform(low)`;
  the disclosed values are the actual GF32 entries of `U1[D1]` and `U2[D2]`
  (zeros are values, never sentinels).

**Model property recorded for review:** because the layer observations are
independent, the table-derived `P2` rows are mathematically independent of the
high symbol (`max |p2[u1=0,b,:] - p2[u1=1,b,:]| = 7.8e-16`, pure float64
rounding).  The operational vs oracle L2 *metrics* therefore differ only at
float-noise level when the L1 candidate is wrong, while the reconstructed
**label** propagates the L1 error through its five high bits.  The pre-run
injected propagation check and the focused tests use a hand-injected
layer-dependent table (column `b=0` mass `A=0/1/32 = 0.2/0.3/0.5`; all other
columns uniform) to prove the wrong-L1 hook detects real divergence; the gate's
per-block `oracle_candidate_divergence` stays report-only with no threshold.

## 4. Frozen disclosure sets

`D1 = sorted(analytic_order(0.05, 256)[:45])` (45 coordinates ascending):

```text
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21,
 22, 24, 25, 26, 32, 33, 34, 35, 36, 40, 48, 64, 65, 66, 68, 72, 80, 96,
 128, 129, 130, 132, 136, 144]
```

`D2 = sorted(analytic_order(0.20, 256)[:110])` (110 coordinates ascending):

```text
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
 39, 40, 41, 42, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58,
 60, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 80, 81,
 82, 83, 84, 88, 96, 97, 98, 100, 104, 112, 128, 129, 130, 131, 132, 133,
 134, 135, 136, 137, 138, 140, 144, 145, 146, 148, 152, 160, 161, 162, 164,
 168, 192, 193, 194]
```

Both are published actual GF32 values, `SC known_positions = sorted(D)`, and
every coordinate is disclosed exactly once per layer.

## 5. Arms and causal semantics

One shared L1 stage per executed block: `build_p1_metrics(B, p1_table)` →
`probs_to_symbol_metric` (`PRIOR_ONLY`) → ONE `sc_decode` with
`known_positions=D1`, `known_values=U1[D1]`; `high_hat = sc1.x_hat`
(source-domain hard candidate, a fresh copy).

Operational arm (causal, strict): `gather_p2_metrics(B, high_hat, p2_table)`
→ `probs_to_symbol_metric` (`CANDIDATE_CONDITIONED`) → ONE **fresh**
`sc_decode` with `known_positions=D2`, `known_values=U2[D2]`;
`low_hat = sc2.x_hat`; `label_hat = low_hat + 32*high_hat`; exactly ONE final
64-bit Toeplitz tag.

Oracle arm (strictly isolated diagnostic, same block and disclosures):
`gather_p2_metrics(B, high_true, p2_table)` → `probs_to_symbol_metric`
(`ORACLE_CONDITIONED`) → ONE fresh `sc_decode` with the SAME `D2/U2[D2]`;
`low_hat_oracle = sc2o.x_hat`; `label_oracle = low_hat_oracle + 32*high_true`;
exactly ONE final tag.  The oracle arm runs whenever true L1 is available (all
executed blocks), including blocks whose operational L1 failed.

No state/APP/belief/partial-sum transfer: the L2 metric is gathered from
scratch, every SC call is a new `sc_decode`, no warm start and no reuse of
`sc1` objects.  Truth enters only the oracle arm, the disclosed-U map and
scoring; it never enters the operational metric, decoder args or tag.

## 6. Provenance rules

| tensor | provenance |
|---|---|
| operational P1 metric | `PRIOR_ONLY` |
| operational P2_hat metric | `CANDIDATE_CONDITIONED` |
| oracle P2_true metric | `ORACLE_CONDITIONED` |
| APP / soft belief / cross-layer prior | never constructed |

## 7. Frozen seeds and derivation

- Run seed **2026091360**; public Toeplitz master **2026091361**.
- Both are absent from HEAD: `git grep -n 2026091360 HEAD` and
  `git grep -n 2026091361 HEAD` return no matches (exit 1).
- **R1-test seed-overlap note (for independent reviewer adjudication):**
  `2026091360`/`2026091361` were used only as P6-R1 **test-local** seeds
  (`comparison_bench/tests/test_nbpolar_incremental_r1.py:54-60`,
  `TEST_SEED_A/B = 2026091360/2026091361`; `R1_FREEZE.md` §6 records
  "R1 tests use 2026091360..1363").  They are **not** consumed official
  result streams.  The operator neither changed the frozen seeds nor re-ran any
  R1 test with them; the overlap is reported for the reviewer to adjudicate.
- Refused consumed official seeds (27 values, exact set persisted in
  `frozen_plan.json.refused_run_seeds`):
  `2026091200..2026091213`, `2026091314..2026091321`, `2026091330`,
  `2026091340`, `2026091341`, `2026091350`, `2026091351`; refused for both
  `--seed` and `--toeplitz-master`.  The frozen `2026091360/2026091361` are
  accepted.
- Per-arm/per-block seed rule (public control, never persisted raw):
  concatenate `SHA-256("nbpolar-p4-toeplitz-seed:<master>:<arm>:<block_index>:
  <counter>")` for `counter = 0, 1, ...` (ASCII decimal), unpack each digest
  MSB-first, truncate to `10*N + 63 = 2623` bits at the frozen point.  Arms are
  `operational` and `oracle`; `block_index` is 0-based (0..95).
- The single final tag per arm is over the MSB-first 10-bit expansion of the
  full label vector (`10*N = 2560` bits) using the accepted
  `shared.toeplitz_tag`.  Each tag invocation consumes **2623 public seed
  bits**, reported separately from key-dependent disclosure.

## 8. Outcome taxonomy (per arm, disjoint and exhaustive over the 96 blocks)

```text
resource_abort > decode_failed > verify_failed > exact > undetected
```

- `exact`: tag pass AND `label == true label` (both layers recovered);
- `undetected`: tag pass AND not exact; never success;
- `verify_failed`: tag mismatch;
- `decode_failed`: L1 or L2 SC exception / nonfinite decision marginals; NO tag
  for that arm;
- `resource_abort`: block not executed because the preregistered budget stop
  fired; zero disclosure and zero tag.

Per-layer sub-buckets persisted per arm: `l1_executed` / `l1_decode_failed`
(disjoint, exhaustive over executed blocks), `l2_invoked` /
`l2_skipped_by_l1_failure` / `l2_decode_failed`, and `tag_invoked` (at most
one per arm per block).  Every block whose L1 stage returns a candidate must
invoke BOTH arms' L2; the oracle L2 always runs when the block executed.

## 9. Accounting and transcript

Per executed arm per block: L1 disclosure `5*k1 = 225`, L2 disclosure
`5*k2 = 550` when L2 is invoked, tag `64` when the one final tag is invoked; a
fully invoked arm totals `5*(k1+k2) + 64 = 839`.  Public control is 2623 bits
per tag invocation, counted separately.

Canonical transcript events per executed arm, in order: `l1_disclosure`
(`key_dependent_bits=225`), `l2_disclosure` (`=550`), `verification_tag`
(`=64`, `public_control_bits=2623`, payload `{"seed_bit_length": 2623}`),
all under `nbpolar_two_layer`, frame key `nbpolar-p4-synthetic:<block>`.  An
independent literal recount (a separate implementation in `recount_transcript`
that parses the arm from the event id) must equal the incremental totals for
`key_dependent_bits`, `public_control_bits` and `tag_invocations`, per arm and
in total, with zero mismatch.

## 10. Truth isolation and wrong-L1 hook

- Truth-isolation sentinel: after the P1/P2 metrics and decisions exist, the
  truth copies (`high`, `low`, `U1`, `U2`, labels) are adversarially mutated in
  place; the protected operational metric arrays and decisions (and the oracle
  metric/decisions and the disclosed copies) must stay bitwise unchanged.
  Violations are counted and must be 0 for the operational arm.
- Wrong-L1 propagation hook: the module carries a documented
  `l1_candidate_override` assessment/test seam; when the candidate is forced
  wrong, `oracle_candidate_divergence = not array_equal(P2_hat, P2_true)` is
  recorded per block.  Report-only, no threshold.  The pre-run injected check
  (hand-injected layer-dependent table; decoder-free) must pass before any
  gate SC call; it proves a real metric divergence (`max abs diff 0.6`) and a
  real label divergence, so the attempt is consumed by the first gate SC call
  (block 0 operational L1), not by the self-check.
- `tag_override` is a documented injection seam used only by tests to force a
  wrong-tag `verify_failed` or a tag collision `undetected`; the frozen gate
  never passes either seam.

## 11. Hard gates (all persisted as booleans; all must pass)

1. `paired_coverage_complete` — 96/96 blocks executed for both arms;
2. `both_arms_l2_invoked_for_l1_candidates` — every L1-candidate block invokes
   both the operational and the oracle L2;
3. `p1_provenance_prior_only`;
4. `candidate_provenance_candidate_conditioned`;
5. `oracle_provenance_oracle_conditioned`;
6. `operational_truth_leak_zero`;
7. `undetected_zero` (both arms);
8. `nonfinite_zero` (both arms);
9. `resource_abort_zero` (both arms);
10. `outcome_buckets_disjoint_exhaustive` — per arm totals sum to 96, the
    per-layer sub-buckets partition the executed blocks, exactly one tag per
    fully invoked arm, and every per-block record passes the structural proof;
11. `disclosures_exact` — per fully invoked arm exactly `5*(K1+K2)` before the
    one final tag, then `839`; per-block formula `5*k1 + 5*k2 + 64`; no extra
    tags;
12. `transcript_recount_mismatch_zero` — independent literal recount equals the
    incremental totals per arm and in total;
13. `pre_run_injected_wrong_l1_propagation_passed`.

Report-only, no threshold: per-arm `exact` counts and the
`oracle_candidate_divergence` count (interface gate; no FER/f/performance
claim).

## 12. Budget, resource ceilings and measured profile

- Internal total wall budget: **3600 s**; on expiry the remaining planned
  blocks are `resource_abort` and the five files are still written.
- External command timeout: `timeout 3600`; memory envelope
  `ulimit -v 2097152` (2 GiB virtual); plan records
  `rss_bytes_max = 2147483648`.
- Profile (NOT the frozen run; temp root `/tmp/opencode/p4_profile`, non-frozen
  seeds 2026091372/2026091373, 8 injected N=256 blocks, command
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python /tmp/opencode/p4_profile.py`):
  total wall **0.93 s**, block wall median **106.5 ms** / mean **106.7 ms** /
  max **114.3 ms**, projected 96-block wall **~10 s** (~360× under budget);
  peak RSS **~139-153 MiB** (~13× under the 2 GiB envelope); all 13 hard gates
  true; transcript mismatch 0.  Nine repeat 6/8-block runs agree on the RSS
  envelope (see `P4_IMPLEMENTATION_NOTES.md` for one anomalous WSL2
  `ru_maxrss` reading).
- The `python -m` invocation emits one cosmetic `runpy` `RuntimeWarning`
  because the package `__init__` imports the module (same pattern as Phase
  5/6); it is not an error and does not affect the run.

## 13. Output root and five-file schema

Root (relative to repo):
`.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`

Confirmed **ABSENT** at freeze.  The CLI refuses an existing root before any
decoder call (before table construction), and creates the root only after the
run.  Exactly five compact scalar-only files are written; symbols, labels,
disclosed values, decoded keys and raw seed bits are never persisted:

1. `frozen_plan.json` — protocol, mode, created_utc, repository, run_seed,
   toeplitz_master, planned_blocks, q/n/k1/k2/epsilon1/epsilon2, field,
   generative/table model and equivalence, disclosure rule + coordinate lists,
   arms, provenance rules, restart rule, outcome precedence, accounting,
   Toeplitz derivation, budget, refused_run_seeds, seed-overlap note, attempt
   consumption point.
2. `per_block_two_layer_outcomes.json` — `n_blocks` plus one scalar record per
   block: `block_index`, `block_wall_s`, `oracle_candidate_divergence`, and
   per-arm `outcome, exact, label_match, tag_pass, l1_provenance,
   l2_provenance, l1_executed, l1_decode_failed, l2_invoked,
   l2_skipped_by_l1_failure, l2_decode_failed, tag_invoked,
   key_dependent_bits, public_control_bits, nonfinite, truth_leak_violation,
   l1_error_type, l2_error_type, wall_s`.
3. `transcript_accounting.json` — event count/types, per-arm incremental
   totals, independent recount (per arm and total), mismatch count/list,
   public control per tag, transcript sha256.
4. `aggregate_summary.json` — per-arm outcome totals, attempted/coverage,
   report-only metrics, accounting totals, pre-run check, truth-leak/nonfinite
   counts, decode error types, `hard_gates{}`, `candidate`, bounded
   `claim_scope`, wall/RSS, resource stop flag.
5. `report.md` — bounded human-readable summary.

## 14. Attempt consumption, no-rerun / no-tune

The single attempt (`attempts_allowed: 1`) is consumed at the **first gate SC
call** (block 0, operational L1).  On any failure the attempt stays consumed:
no rerun, no seed change, no table/K/threshold/set change, no partial credit.
The pre-run injected propagation check is decoder-free and consumes nothing.
The only permitted return labels are `TWO_LAYER_OPERATIONAL_SC_CANDIDATE`
(only if all 13 hard gates pass) or `BLOCKED(<single earliest gate>)`.

## 15. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer --n 256 --epsilon1 0.05 --epsilon2 0.20 --k1 45 --k2 110 --blocks 96 --seed 2026091360 --toeplitz-master 2026091361 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate
```

No flag may be added or changed.  The output root must still be absent at
execution time.

## 16. Forbidden-path proof

- `two_layer.py` imports only stdlib (`argparse`, `dataclasses`, `hashlib`,
  `json`, `sys`, `time`, `numbers`, `pathlib`, optional POSIX `resource`),
  numpy, the accepted nbpolar Phase 1-4 modules and `formal_ir/shared.py`.
  No Model-F stored file, columnar/TT-binary reader, real-frame, DEV/EVAL,
  benchmark, sibling-checkout, FWHT/scalable, SCL/CRC or APP-prior code path
  exists; no import-time I/O; no global RNG (`np.random.default_rng` only);
  `n <= 256` is enforced by the runner; the only write target is the
  explicitly passed output root (refused if present, created after the run).
- `test_no_forbidden_markers_or_import_time_side_effects` scans the module
  source for `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`,
  `dev_seed`, `eval_seed`, `benchmark`, `sibling`, `artifact`, `results/`,
  `fwht`, `scl/crc`, `app_fed`, `app_prior`, `get_l1_app`, `pandas`, `pyarrow`,
  `scipy` (zero matches), rejects non-`default_rng` `np.random.<call>`, imports
  the module in a fresh interpreter with a temp cwd (no file created), and
  proves the test file never references the real queue root or calls
  `default_rng` with the frozen seeds.
- Tests use temporary directories, injected/tiny inputs and fresh seeds
  `2026091364..2026091372` only; no real data, stored file,
  `comparison_bench/outputs_comparison/`, `results/` or sibling path is
  touched.  The sibling checkout is used read-only as the pinned interpreter.
- No file in any accepted evidence root (`static_protocol_dev_gate/`,
  `paired_incremental_dev_gate/`, `three_arm_paired_dev_gate/`,
  `empirical_prior_sc_diagnostic/`) was opened, parsed, read or written.
  Nothing was committed or pushed.

## 17. Pre-EXECUTE checklist for the independent reviewer

1. Confirm this freeze doc matches the implemented constants and semantics in
   `two_layer.py` (seeds, banned set, point, `K1/K2`, `D1/D2`, derivation
   string, arm labels, accounting, taxonomy, seams, budgets, `n <= 256`).
2. Recompute `D1`/`D2` from `analytic_order` and confirm the lists above.
3. Re-run the focused suite and the full NB-Polar predecessor suite
   (expected 12 + 180 = 192 passed) and the tiny CLI smoke.
4. Confirm the frozen command, the absent output root, `attempts_used: 0`, and
   the authorized STATUS flags.
5. Adjudicate the P6-R1 test-local seed overlap (`2026091360/2026091361`) and
   the recorded frozen-model `P2` layer-independence property (§3).
6. Confirm `git grep 2026091360 HEAD` and `git grep 2026091361 HEAD` are empty
   and that no frozen seed was used by any test or smoke.
7. FAIL blocks execution; issues return to the operator for scoped repair and
   re-review.
