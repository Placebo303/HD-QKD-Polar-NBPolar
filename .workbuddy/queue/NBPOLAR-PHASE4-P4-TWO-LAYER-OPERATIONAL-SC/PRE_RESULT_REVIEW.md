# Independent Pre-RESULT review — NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC

Reviewer: fresh independent reviewer-go instance (read-only; did not write the
module, tests, freeze, operator notes, or run the gate; no file edited other
than this review). Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged). Date:
2026-09-13 13:39 +0800. Interpreter:
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).
Inputs read: the five gate artifacts, `frozen_plan.json`, packet docs,
`P4_FREEZE.md`, `PRE_EXECUTE_REVIEW.md`, `two_layer.py`,
`comparison_bench/tests/test_nbpolar_two_layer.py`, `report.md`.

**Independence statement.** The frozen 96-block command was **NOT rerun**; the
single attempt is consumed (attempt 1/1, `attempt_consumption_point = first gate
SC call`, persisted in `frozen_plan.json` and
`aggregate_summary.json.attempts_consumed_by_this_run = 1`). No gate SC call
was made by this review. The only in-memory module call was the decoder-free
`injected_wrong_l1_propagation_check()` (recorded `decoder_calls: 0`) to verify
its persisted record; this consumes nothing. All recomputation used the five
persisted artifacts plus the frozen source. No Model-F/artifact/parquet/TTBin/
real-data access; no old evidence root opened, parsed, or modified; no sibling
write; no commit/push. Only writes: this file and `/tmp/opencode/*` scratch.

## Verdict: PASS_WITH_COMMENTS

All 13 hard gates, all coverage/outcome/provenance/accounting numbers, the
report-only metrics, and the bounded wording recompute from the per-block
records exactly as persisted. No blocking issue found; the result may be
solidified. The comments below are reporting/housekeeping only.

---

## 1. Output-root audit (exactly 5 files, scalar-only)

```text
root: .workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/
files: aggregate_summary.json (3899 B)  sha256 9ae2cbef...42cc0
       frozen_plan.json (5349 B)        sha256 c3f5ab23...6d16f
       per_block_two_layer_outcomes.json (141468 B) sha256 6144b3de...8140c
       report.md (1938 B)               sha256 0db1c1cb...4341
       transcript_accounting.json (1226 B) sha256 84260f92...4b96c
no hidden/extra files; 5 total
mtimes: 13:29:38.812993 -> .829423 (17 ms span, dir .828418) = single generation
```

Deep scalar-only audit (recursive walk of every JSON leaf):

| file | leaves | containers | leaf types | anomalies | suspicious hex |
|---|---|---|---|---|---|
| aggregate_summary.json | 93 | 23 | bool,float,int,str | none | none (only whitelisted transcript sha) |
| frozen_plan.json | 238 | 15 | bool,float,int,str | none | none |
| per_block_two_layer_outcomes.json | 4129 | 290 | None,bool,float,int,str | none | none |
| transcript_accounting.json | 28 | 12 | int,str | none | none |

- No non-scalar leaf anywhere; no `high_hat`/`label_hat`/`u1_disclosed`/
  `u2_disclosed`/symbol/label/decoded-key/raw-seed-bit field exists in any
  persisted record (the only arrays live in the in-memory `TwoLayerBlockResult`
  and are never written; `_block_record`/`_arm_record` persist 20 scalar keys).
- Per-block schema uniform over all 96 records and both arms (same key set);
  `n_blocks = 96`, `len(blocks) = 96`.
- The only 64-hex value persisted is the public
  `transcript_sha256 c3ffc6d7...0135c5`, identical in
  `transcript_accounting.json` and `aggregate_summary.json.transcript`.

## 2. Coverage / pairing recomputed

```text
block_index == 0..95 strictly increasing: True
operational records 96 / oracle records 96; arm fields correct
operational: l1_executed=96 l1_decode_failed=0 | l2_invoked=96 l2_skipped=0 l2_decode_failed=0 | tag_invoked=96
oracle:      l1_executed=96 l1_decode_failed=0 | l2_invoked=96 l2_skipped=0 l2_decode_failed=0 | tag_invoked=96
invariants (l1_exec XOR l1_decode_failed; skip==l1fail; l2_invoked==not l1fail): True both arms
both arms' L2 invoked for every L1 candidate: True (96/96 pairs)
disjoint/exhaustive: l1 96+0; l2 96+0; outcomes sum 96 per arm
```

## 3. Outcome totals recomputed per arm

| arm | exact | undetected | verify_failed | decode_failed | resource_abort | sum |
|---|---|---|---|---|---|---|
| operational | 26 | 0 | 70 | 0 | 0 | 96 |
| oracle | 44 | 0 | 52 | 0 | 0 | 96 |

- `exact + verify_failed == 96` per arm; `undetected`/`decode_failed`/
  `resource_abort` are 0 and never folded into `exact`.
- `exact == (outcome=='exact' and label_match and tag_pass)`: True both arms;
  `verify_failed <=> not tag_pass`: True both arms.
- Persisted `outcome_totals`, `attempted` (96/96), `coverage` (1.0),
  `resource_stop_fired` (False) all match the recomputation.

## 4. Provenance and truth isolation

```text
op L1 = {PRIOR_ONLY: 96};  op L2 = {CANDIDATE_CONDITIONED: 96}
or L1 = {None: 96};        or L2 = {ORACLE_CONDITIONED: 96}
truth_leak_count {operational: 0, oracle: 0}; nonfinite_count {0,0}; decode_error_types {}
```

Code inspection of the truth path in `two_layer.py` (independent of the tests):
`high_arr`/`low_arr` are built at :623-624 but enter only (a) the disclosed
map `u1_disclosed/u2_disclosed` (:633-634), (b) the oracle arm
(`gather_p2_metrics(B, high_arr)` :738, oracle label :753), (c) scoring
(`op_label_match`/`tag_true` :678-679, oracle :754-755), and (d) the truth
sentinel :809-816. The operational metric, decoder args and tag never receive
them: op P1 = `build_p1_metrics(bob, p1_table)` (:640), op P2 =
`gather_p2_metrics(bob, op_high_hat, p2_table)` (:666), tag input
`labels_to_bits(op_label_hat)` with an arm/block seed (:679-681). The truth
sentinel (`_truth_isolation_sentinel`, :424-437; applied :808-819) mutated all
truth buffers after the decisions existed; both arms recorded
`truth_leak_violation=False` for all 96 blocks.

## 5. Accounting / recount recomputed from per-block records

```text
K1=45, K2=110: components 5*K1=225, 5*K2=550, tag=64, fully invoked 839
per-block formula mismatches (kdb == 225 + 550*invoked + 64*tag; pcb == 2623*tag): 0
key-dependent totals: op=80544 or=80544 total=161088 (= 96*839 per arm)
public control:       op=251808 or=251808 total=503616 (= 192*2623)
tag invocations:      op=96 or=96 total=192
event breakdown recomputed from per-block: l1=192 l2=192 tag=192 total=576  == persisted
incremental == recount (totals and by_arm): True; mismatch_count=0; mismatches=[]
2623 = 10*256 + 63 public seed bits per tag (frozen derivation)
```

Both file-level summaries and the independent per-block recomputation agree on
every number; `frozen_plan.json`/`aggregate_summary.json` accounting blocks
match the freeze §9 components.

## 6. 13 hard gates independently recomputed (not copied)

| gate | recomputed | persisted |
|---|---|---|
| paired_coverage_complete | True | True |
| both_arms_l2_invoked_for_l1_candidates | True | True |
| p1_provenance_prior_only | True | True |
| candidate_provenance_candidate_conditioned | True | True |
| oracle_provenance_oracle_conditioned | True | True |
| operational_truth_leak_zero | True | True |
| undetected_zero | True | True |
| nonfinite_zero | True | True |
| resource_abort_zero | True | True |
| outcome_buckets_disjoint_exhaustive | True | True |
| disclosures_exact | True | True |
| transcript_recount_mismatch_zero | True | True |
| pre_run_injected_wrong_l1_propagation_passed | True | True |

All 13 agree; each gate was re-derived from the per-block data with an
independent structural per-record proof (recomputed `per_record_ok: True`).
`candidate = TWO_LAYER_OPERATIONAL_SC_CANDIDATE` is only set when all gates
pass (code `_build_summary`), consistent with the persisted value.

**Pre-run check backing** (required item 6). Persisted schema has 9 keys:
`check, table, decoder_calls: 0, candidate_provenance:
CANDIDATE_CONDITIONED, oracle_provenance: ORACLE_CONDITIONED,
metric_max_abs_diff: 0.6, metric_divergent: true, label_divergent: true,
passed: true`. Independent verification: (a) reproducing the decoder-free
function in memory returns a dict byte-equal to the persisted record; (b)
independent numpy replication of the documented hand-injected table
(column b=0 mass A=0/1/32 = 0.2/0.3/0.5; all other columns uniform) gives
`p2[u1=0,b=0,:3] = [0.4, 0.6, 0.0]` vs `p2[u1=1,b=0,:3] = [1.0, 0.0, 0.0]`,
`max abs diff = 0.6`, and a real label divergence. The runner calls the check
before the block loop (`two_layer.py:1545-1547`) and refuses on failure, so
the check is real and decoder-free.

## 7. Report-only metrics and divergence definition

**Definition (code):** `_candidate_divergence(p2_hat, p2_true) =
not np.array_equal(p2_hat, p2_true)` (`two_layer.py:440-442`), applied per
block at :804-806 as `oracle_candidate_divergence` comparing the operational
candidate-conditioned `P2_hat` (32x1024 float64) with the oracle
true-L1-conditioned `P2_true`, i.e. **bitwise (bit-exact) array inequality at
float64 last-bit level**.

**Recomputed vs persisted:** exact operational 26 / oracle 44; divergence
`count = 34`, `defined = 96` — both equal the persisted values.

**What the 34 measures (from raw crosstabs):**

```text
divergence x op outcome:  False/verify_failed 36, False/exact 26, True/verify_failed 34
divergence x op label_match: False/False 36, False/True 26, True/False 34
divergence x oracle outcome: False/vf 36, False/exact 26, True/vf 16, True/exact 18
op-exact blocks divergent: 0;  op-exact subset of oracle-exact: True
```

Because the frozen layer-erasure model makes the table-derived `P2` rows
mathematically independent of the high symbol (Pre-EXECUTE measured
`max |P2[u1=0]-P2[u1=1]| = 7.77e-16`, pure float64 rounding), a wrong L1
candidate changes `P2_hat` only at rounding scale. The count of 34 therefore
counts the blocks where those rounding differences happened to change at least
one bit of the array — not a semantic metric-level L1→L2 dependence. It is
smaller than the 70 op label-mismatch blocks (36 of the 70 wrong-candidate
blocks produced bitwise-identical gathers), and it can coexist with an oracle
`exact` (18 blocks), confirming decision-level L2 recovery is independent of
the candidate at this model point. The flag has **no threshold and no
pass/fail use**: its only code consumers are the `report_only` summary block
(`:1394-1395`) and the `report.md` line; `hard_gates`/`candidate` never read
it. `exact` counts are likewise report-only. No performance/FER/efficiency
number is derived from either.

**Consequence required by Pre-EXECUTE NB-3 (recorded):** the frozen run's
`exact` and `oracle_candidate_divergence` numbers must be described in the
acceptance text as a label-level propagation / float-noise index signal of the
interface gate, **not** as metric-level L1→L2 dependence, and not as any
performance result.

## 8. Bounded wording check (`report.md` read fully)

- Report contains: protocol/mode, seeds, point, wall/RSS, the per-arm outcome
  table, accounting per arm, 13-gate table, `candidate` label, and the scope
  line. All numbers re-checked against the JSON artifacts (wall 10.154709 s,
  RSS 144609280 B, outcomes 26/70 and 44/52, 839/2623, 576 events, mismatch 0,
  34 of 96 divergence with "no threshold").
- The only occurrence of FER/leakage-efficiency/key-rate/qualification/
  promotion/f<=1.3 wording is the explicit disclaimer:
  `"synthetic two-layer interface and cross-layer-propagation development
  signal only; this is not real-data FER, leakage efficiency, key rate,
  qualification, promotion or f<=1.3 evidence"` (identical
  `claim_scope` in `aggregate_summary.json`). No positive performance claim,
  no FER, no secret-key-rate, no leakage-efficiency, no promotion wording.
- `resource_stop_fired: False`; wall 10.154709 s vs 3600 s budget; peak RSS
  144609280 B (137.9 MiB) vs 2 GiB — no NB-4 WSL2 inflation anomaly this run.

## 9. Implementation state — tests

```text
TMPDIR=/tmp/opencode/p4_result_review/tmp <pinned python> -m pytest comparison_bench/tests/test_nbpolar_two_layer.py -q -p no:cacheprovider
  -> 12 passed, 1 warning in 13.31 s
TMPDIR=/tmp/... <pinned python> -m pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider
  -> 192 passed, 1 warning in 98.15 s
```

- Focused P4 file: 12 tests (the "12 new"). The full NB-Polar glob actually
  matches **13** files (`test_nbpolar_construction/empirical_sc/incremental/
  incremental_r1/p2r1_diagnostic/prior/prior_artifact/protocol/r1/sc/
  transform/two_layer/two_layer_rate`), 192 tests total as expected
  (per-file `def test_` counts sum to 192). The "12-file suite" wording in the
  review request is a miscount; the expected test total (192) is met.
- The only warning is the pre-documented cosmetic `Unknown config option:
  cache_dir`/collection warning; no test failure, no real-data access.

## 10. Scope / provenance / no-overwrite

```text
git status --porcelain: 44 entries, identical before and after this review; nothing staged
HEAD: ab173f2a5e17336383a897b941080b731ba3dd9e (unchanged); no commit, no push
repo files newer than 13:20 (excl. __pycache__): PRE_EXECUTE_REVIEW.md (13:28, pre-gate)
  and the five gate artifacts (13:29:38); nothing else
old accepted evidence roots: static_protocol_dev_gate 02:31, paired_incremental_dev_gate 03:33,
  three_arm_paired_dev_gate 11:09, empirical_prior_sc_diagnostic 01:09 — all pre-gate, no writes
accepted modules (prior/sc/transform/construction/algebra/shared.py): mtimes 09-12, tracked clean
results/ and comparison_bench/outputs_comparison/: no file newer than 13:00 (none at all)
sibling checkout: no results/outputs_comparison writes; no sibling file in the gate window
  (13:29); unrelated concurrent D7-session activity exists (e.g. 13:26/13:32), not this packet
gate root sha256 re-checked after all review activity: unchanged (all 5 hashes identical)
```

- Single-generation mtimes in the root verified (17 ms span, same dir second).
- Attempt/seed state: `frozen_plan.json` `attempts_allowed 1 /
  attempts_consumed 1`, `run_seed 2026091360`, `toeplitz_master 2026091361`
  (both absent from the 27-entry refused set; refused set recomputed equal);
  the run seed is consumed at the first gate SC call (code order: decoder-free
  pre-check, then block 0 operational L1 at `:655`). Attempt 1/1 is consumed —
  no rerun is permitted or performed.

## Blocking Issues

- None.

## Non-Blocking Comments

1. **STATUS.yaml lag (housekeeping).** `STATUS.yaml` still shows
   `attempts_used: 0` and the pre-run `state` string; `P4_IMPLEMENTATION_NOTES`
   and the artifact records show the attempt consumed. Main thread should
   update STATUS to the gate-completed/consumed state at acceptance
   (docs-only; consistent with Pre-EXECUTE NB-5).
2. **Transcript events not persisted.** `recount_transcript` is computed
   in-memory and both its totals and the incremental totals are persisted, but
   the per-event list is not, so the literal recount cannot be replayed
   event-by-event from artifacts. This review independently reproduced every
   total and the event-type breakdown from the per-block records (192/192/192,
   totals equal), leaving no residual; a future schema could persist event
   counts per arm if literal replayability is desired (optional).
3. **Oracle-arm `l1_executed` semantics (Pre-EXECUTE NB-6).** For the oracle
   arm the persisted `l1_executed=True`/`l1_decode_failed=False` denote the
   shared block L1 stage / true-L1 availability, not an oracle-arm L1 SC call.
   Worth one clarifying sentence if the record is audited later.
4. **Test-file count wording.** Request says "12-file" suite; the glob matches
   13 files / 192 tests (all green). Reporting only.

## Checklist

- [x] Matches OpenSpec spec (P4 freeze §1-§13 semantics, point, taxonomy,
      provenance, accounting, gates, five-file schema)
- [x] Tests pass (focused 12/12; full NB-Polar glob 192/192; pinned
      interpreter; fresh TMPDIR; `-q -p no:cacheprovider`)
- [x] No scope creep (gate wrote exactly the 5 frozen files; no commit/push;
      no results/outputs_comparison/sibling/old-evidence writes)
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? Deferred to
      the main thread's post-gate documentation step (decision-log currently
      still pre-run per Pre-EXECUTE NB-5); not an evidence blocker.
