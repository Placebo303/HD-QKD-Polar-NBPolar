# Pre-RESULT review — NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1

Fresh independent reviewer-go session (2026-09-13, WSL). I did not write the
module, tests, freeze, packet or spec, and did not run the frozen gate. Read-only
except this file. Repository `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged; 0 commits since,
nothing staged). Pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(3.12.3, numpy 2.5.3). No real/artifact data, no predecessor-root content, no
commit/push. The five artifacts under
`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
were read only.

## Verdict: PASS_WITH_COMMENTS

The five persisted artifacts are an exact, internally consistent and honestly
labelled record of the one authorized run. Every persisted number was
independently reproduced; all 12 integrity booleans and all 4 scientific
booleans agree with my own recomputation. The single failing gate
`d1_exactly_nested_and_d2_disclosed_once` reproduces exactly and is diagnosed
below as a **gate-check implementation defect (class b)**, not a contract
violation and not an artifact/bookkeeping defect: the executed D2 disclosure
behaviour satisfies "once per arm/block" on all 640 blocks. Under the frozen
contract the gate's correct value would be **true**, but the executed run
remains **BLOCKED** as persisted; no rerun, repair or rescoring is permitted
here and the main thread owns the disposition.

---

## 1. Artifact set and generation

- Exactly five files, and only these, in the output root:
  `frozen_plan.json` (15,248 B), `per_block_paired_outcomes.json` (1,125,035 B),
  `transcript_accounting.json` (2,090 B), `aggregate_summary.json` (9,090 B),
  `report.md` (2,023 B).
- Single generation: all five written 2026-09-13 21:25:30.511–21:25:30.558
  (+0800), a 47 ms window; no `.tmp`/partial/backup files, no second copy, and
  `find .workbuddy -type d -name paired_adaptive_gate` finds exactly one root.
- `frozen_plan.created_utc = 2026-09-13T13:25:30Z` (= local 21:25:30) matches
  the write instant; `wall_s = 105.941485` implies the run started ≈ 21:23:44,
  after the Pre-EXECUTE review closed (21:22:40.22). No file outside the packet
  directory has an mtime after 21:22:40; no predecessor evidence root, probe
  root, `results/`, `outputs_comparison/` or accepted module has an mtime after
  20:30 (all checked by metadata only).
- Per-block records are scalar-only: exactly the 25 frozen arm keys, leaf types
  {int 12800, bool 12800, str 4480, NoneType 2560, float 1280} and no arrays,
  labels, symbols or seed payloads (grep for `high_hat|low_hat|label_hat|
  labels_true|u1_disclosed|u2_disclosed|seed_hex|"seed_bits"` → 0 matches).
- Frozen command byte-identical across `TASK_PACKET.md` bash block,
  `P6_FREEZE.md` §11 and `frozen_plan.frozen_command` (verified by extraction).

## 2. Number-by-number recomputation (all from the five artifacts)

Coverage / identity:

- 640 records, 640 unique `(stream_seed, block_index)` pairs; identity set
  equals the exact product `{2026091550..54} x {0..127}`; every stream has
  exactly 128 blocks; no duplicates.

Outcome buckets (both arms, mutually exclusive and exhaustive):

| arm | exact | undetected | verify_failed | decode_failed | resource_abort | sum |
|---|---|---|---|---|---|---|
| static | 632 | 0 | 8 | 0 | 0 | 640 |
| adaptive | 632 | 0 | 8 | 0 | 0 | 640 |

- All 640 static and all 640 adaptive records pass my independent re-implementation
  of the frozen per-record structural proof (stage/k1 map, tag/feedback/no-tag
  rules, provenance, exact-per-bucket arithmetic, `5*(K_j+140)+64*tags` /
  `2623*tags` / `1*feedback` / public-control sum).
- The 8 `neither` blocks are the same 8 blocks in both arms, all
  `verify_failed` (tag exhausted at stage 4; adaptive tags 4 / feedback 3 each):
  (2026091550,13), (2026091551,13), (2026091552,40), (2026091552,47),
  (2026091552,60), (2026091552,120), (2026091553,108), (2026091554,51).
  Per-stream `neither`: 1/1/4/1/1.

Paired cells, stage/k1 histogram:

- cells `{both_exact: 632, adaptive_only: 0, static_only: 0, neither: 8}`;
  `adaptive_only`/`static_only` zero also per stream; static and adaptive exact
  agree on every block.
- adaptive termination stage `{1:403, 2:185, 3:39, 4:13}`; termination_k1
  `{45:403, 60:185, 72:39, 112:13}`; stage 4 = 5 accepted + 8 verify_failed;
  static termination_k1 = 112 on all 640.

Totals (record sums == transcript incremental == summary, all recomputed):

| quantity | static | adaptive | total |
|---|---|---|---|
| key-dependent bits | 847,360 | 675,783 | 1,523,143 |
| public seed bits | 1,678,720 | 2,470,866 | 4,149,586 |
| feedback bits | 0 | 302 | 302 |
| public control bits | 1,678,720 | 2,471,168 | 4,149,888 |
| tag invocations | 640 | 942 | 1,582 |
| feedback invocations | 0 | 302 | 302 |

- static mean 1324.0 (640 x 1324 exact); adaptive mean 1055.9109375; absolute
  saving 268.0890625 bits; percentage saving 20.248418617824772%.
- `2623 * tag_invocations` public seed bits and `1 * feedback_invocations`
  feedback bits hold on every record; union bound
  `min(1, 1582*2^-64) = 8.57603918436034e-17` exact.
- Transcript event types recomputed from records:
  `{l1_disclosure: 1582 (=640 static + 942 adaptive), l2_disclosure: 1280
  (=640+640), verification_tag: 1582, control: 302}`; event_count 4746;
  `mismatch_count=0`, empty mismatch list; recount by-arm == incremental
  by-arm; fully-invoked values 989/1064/1124/1324 (+static 1324).
- Per-stream breakdown (exact 127/127/124/127/127, tags 128+192/128+190/
  128+190/128+192/128+178, feedback 64/62/62/64/50, KD 169472+135463/
  169472+135420/169472+135500/169472+135698/169472+133702) reproduced field by
  field, and the five rows sum to the global totals.
- Leakage integer comparison from the per-block records:
  `100*675783 = 67,578,300 <= 85*847360 = 72,025,600` → true (20.2484%
  reduction; the 15% requirement needs ≤72,025,600, slack 4,447,300).
- Budgets: wall 105.941485 s ≤ 3600 s; peak RSS 394,567,680 B ≤ 2,147,483,648 B;
  `resource_stop_fired=false`, `retries=0`, `no_l2_exhaustion_blocks=0`.

Attempt/stream accounting: allowed 1, consumed_before 0, consumed_by_this_run 1,
retries 0; five distinct fresh streams 2026091550..54; masters
2026101550..54 = stream+10000 persisted in the plan; seeds ∩ refused set =
∅; refused set 65 unique.

## 3. All 12 integrity gates and 4 scientific gates — independent recomputation

My own logic, seeded only from the persisted artifacts (integer/accounting
recounts, per-record structural proofs, plan-side D1/D2 recomputation including
`D1(K)=sorted(analytic_order(0.05,256)[:K])` and
`D2=sorted(analytic_order(0.20,256)[:140])` via the accepted
`construction.analytic_order`, and `new_positions` partition/disjointness):

| # | gate | persisted | my recomputation | agree |
|---|---|---|---|---|
| 1 | pairing_coverage_complete | true | true | yes |
| 2 | stream_block_identity_exact | true | true | yes |
| 3 | result_buckets_disjoint_exhaustive | true | true | yes |
| 4 | d1_exactly_nested_and_d2_disclosed_once | **false** | **false** (faithful reproduction) | yes |
| 5 | provenance_and_truth_isolation_complete | true | true | yes |
| 6 | undetected_zero | true | true | yes |
| 7 | nonfinite_zero | true | true | yes |
| 8 | resource_abort_zero | true | true | yes |
| 9 | transcript_recount_mismatch_zero | true | true | yes |
| 10 | tag_feedback_public_control_accounting_and_union_bound_exact | true | true | yes |
| 11 | wall_rss_within_frozen_limits | true | true | yes |
| 12 | attempt_seed_accounting_exact | true | true | yes |

| scientific gate | persisted | my recomputation |
|---|---|---|
| static_exact_at_least_620_of_640 | true | true (632) |
| adaptive_exact_equals_static_exact | true | true (632 == 632) |
| paired_adaptive_only_zero_and_static_only_zero | true | true (0/0) |
| leakage_100_adaptive_le_85_static | true | true (67,578,300 ≤ 72,025,600) |

`integrity_all_pass=false`, `failing_integrity_gates=[d1_...]`,
`scientific_all_pass=true`, `outcome_label=BLOCKED` — all reproduced.

## 4. Failing-gate diagnosis (central task)

### 4.1 What the gate computes (file:line)

`comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py`:

- gate entry `_integrity_gates` `:1391-1405`; the D2 term is
  `and l2_once` at `:1401`;
- `l2_once` `:1350-1354` = `l2_key_ok and all(count == 1 for count in l2_counts.values())
  and set(l2_counts) == expected_l2`;
- the count key is built at `:1341-1343`:
  `parts = str(event["event_id"]).split("-"); key = (int(event["block_id"]), parts[2])`;
- `expected_l2` `:1346-1349` = `{(block_index, arm) : arm.l2_invoked}` — also
  keyed by the per-stream block index.

Event identity construction (in-memory transcript only; never persisted):

- `_event` sets `frame_key = f"nbpolar-p4p6-synthetic:{block_index}"` (`:866`)
  and `block_id = int(block_index)` (`:872`);
- static L2 event id `block-{block_index}-static-l2-disclosure` (`:909`);
  adaptive L2 event id `block-{block_index}-adaptive-l2` (`:956`);
- `paired_block_events(result, ...)` (`:881-1006`) receives only the
  `PairedBlockResult`, whose `block_index` is the **per-stream** index; the
  caller at `:2110` does not pass `stream_seed`. The runner loops
  `for block_index in range(blocks)` inside `for stream_seed in seed_list`
  (`:2059-2062`, `:2087`), so all five streams reuse indices 0..127.

### 4.2 Raw counts reproduced for the 640-pair run

Reconstructing the in-run `l2_counts` exactly as the code does (one L2 event per
arm/block with `l2_invoked`, from the persisted records + the event-id format):

- 1280 L2 events (640 static + 640 adaptive), consistent with
  `transcript_accounting.event_types.l2_disclosure = 1280`;
- `l2_counts` has **256 keys** `{(0..127) x {static, adaptive}}`; the count
  distribution is **{5: 256}** — every key aggregates the same block index of
  all five streams;
- `set(l2_counts) == expected_l2` is **true** (set comparison hides the
  multiplicity);
- `all(count == 1 ...)` is **false** because every count is 5;
- the other gate-4 conjuncts are true: nested flags/sizes/pairwise chain true
  (plan `nested_assertions` all true; D1 recomputed equal to analytic-order
  prefixes; `new_positions` partition D1(112) exactly), and all 640 static
  `termination_k1 == 112`.

So the gate's only false term is the cross-stream `count == 1` requirement.

### 4.3 Classification: (b) gate-check implementation defect

- **Not (a).** The frozen contract (`P6_FREEZE.md` §5/§8 item 4, `TASK_PACKET.md`
  P6-C/P6-F: "D2 disclosed once per arm/block") is honoured in executed
  behaviour. Per `(stream_seed, block_index, arm)` the L2 disclosure event count
  is exactly 1 for all 640 blocks x 2 arms (1280/1280 = 640 static + 640
  adaptive); there is no block with 0 or ≥2 L2 disclosures among the 640 pairs;
  all `l2_invoked` records are accounted for; no D1 nesting invariant is
  violated. A genuine violation would have to show a raw per-block
  multiplicity ≠ 1 — none exists.
- **Not (c).** The persisted per-block bookkeeping is correct: every record
  carries `stream_seed`, `l2_invoked` and correct arithmetic, and the transcript
  totals are exact. The ambiguity lives only in the in-memory event identity
  (`frame_key`/`block_id`/event id omit `stream_seed`), which the gate then uses
  as a global count key.
- **Defect.** `_integrity_gates` aggregates events by `(block_id, arm)` where
  `block_id` is unique only within a stream; with the frozen 5-stream shape the
  "exactly once per arm/block" check degenerates into "exactly once per key",
  which the contract does not require and which 5 streams cannot satisfy. The
  correct key must include the stream identity (or the event identity must
  encode the full paired block).

### 4.4 Empirical corroboration (bounded, non-frozen, no attempt consumed)

- Production-function probe (no decoder): two synthetic streams sharing
  `block_index=0` produce event ids `block-0-static-l2-disclosure` /
  `block-0-adaptive-l2` twice; the gate extraction yields keys
  `(0,'static')`,`(0,'adaptive')` twice → collision true.
- Live tiny probes with fresh non-frozen seeds only (output under
  `/tmp/opencode/p6_prereview/`, never the frozen root):
  - 1 stream x 4 blocks (seed 2026091596): gate 4 = **true**,
    `integrity_all_pass=true` (single-stream shapes cannot expose the defect);
  - 2 streams x 4 blocks (seeds 2026091596/2026091597): gate 4 = **false**,
    `integrity_all_pass=false`, failing list exactly
    `['d1_exactly_nested_and_d2_disclosed_once']` — the same isolated failure as
    the 640-pair run.
- Focused test file re-run: `test_nbpolar_adaptive_l1.py` → 15 passed (5.80 s,
  fresh temp basetemp). Coverage gap confirmed by inspection: every runner call
  in the suite uses exactly one stream (`:516-524` 1 seed/2 blocks; `:617`
  1 seed/3 blocks; `:632-641` 1 seed/2 blocks with
  `assert summary["integrity_all_pass"] is True` at `:734`), so the suite can
  never catch a cross-stream event-key collision.

### 4.5 Correct value under the frozen contract and disposition

Under the frozen contract (D2 exactly once per arm/block, D1 exactly nested),
with per-`(stream, block, arm)` event counts of 1 and all other conjuncts true,
the correct value of `d1_exactly_nested_and_d2_disclosed_once` is **true**. Had
the check been written with the full block identity, the run would have been
`integrity_all_pass=true`, `scientific_all_pass=true` and the label
`ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`.

**This is a diagnosis only.** The packet's stop rule
(`TASK_PACKET.md` "Stop and boundary rules": no repair and rerun on any
integrity gate failure) is binding: the frozen command must not be rerun, the
failure root must be preserved, and the persisted label stays `BLOCKED`. The
main thread owns the disposition (accept `BLOCKED`, or authorize a corrected
check + fresh attempt as a new frozen packet); no rerun/repair/re-score is
permitted in this review.

## 5. Corrected-vs-persisted gate table

| # | gate | persisted (run) | recomputed by reviewer | contract-correct value | note |
|---|---|---|---|---|---|
| 1 | pairing_coverage_complete | true | true | true | — |
| 2 | stream_block_identity_exact | true | true | true | — |
| 3 | result_buckets_disjoint_exhaustive | true | true | true | — |
| 4 | d1_exactly_nested_and_d2_disclosed_once | **false** | **false** | **true** | check defect (b): cross-stream key collision; all D1/D2 behaviour correct per block |
| 5 | provenance_and_truth_isolation_complete | true | true | true | — |
| 6 | undetected_zero | true | true | true | — |
| 7 | nonfinite_zero | true | true | true | — |
| 8 | resource_abort_zero | true | true | true | — |
| 9 | transcript_recount_mismatch_zero | true | true | true | — |
| 10 | tag_feedback_public_control_accounting_and_union_bound_exact | true | true | true | — |
| 11 | wall_rss_within_frozen_limits | true | true | true | — |
| 12 | attempt_seed_accounting_exact | true | true | true | — |
| S1 | static_exact_at_least_620_of_640 | true | true | true | 632 |
| S2 | adaptive_exact_equals_static_exact | true | true | true | 632 = 632 |
| S3 | paired_adaptive_only_zero_and_static_only_zero | true | true | true | 0 / 0 |
| S4 | leakage_100_adaptive_le_85_static | true | true | true | 67,578,300 ≤ 72,025,600 |

## 6. Truth boundary and provenance

- Provenance labels from the records: L1 `PRIOR_ONLY` on every executed block
  (all 1280 arm records), L2 `CANDIDATE_CONDITIONED` wherever `l2_invoked` (all
  1280), and `truth_leak_violation=false` on all 1280 records.
- Code path: `build_p1_metrics(bob, ...)` takes no Alice input; L2 metrics come
  from `gather_p2_metrics(bob, candidate)`; the in-run mutation sentinel
  (`two_layer._truth_isolation_sentinel`, invoked at `run_paired_block:831-842`)
  flips truth copies and requires every operational array (P1 metric, candidates,
  P2 metric/probs, `low_hat`, `label_hat`) bitwise unchanged. Truth
  (`u1_true/u2_true/labels_true`) is used only for disclosed-value copies, tag
  construction and scoring — never passed into `build_p1_metrics`/
  `gather_p2_metrics`, and tag seeds derive only from the public master
  (`stream+10000`) with the arm/block/level domain.
- Restart/no-state: `run_adaptive_arm:632-687` calls `tl._decode_layer` afresh
  per stage with the same original `p1_logp` object and a freshly gathered L2
  metric per stage; `_decode_layer` (`two_layer.py:564-575`) calls `sc_decode`
  with no persistent decoder object, and `sc.py` copies its metric input. No
  decoder, metric, partial sum, candidate or tag seed crosses stages. The
  scalar-only schema cannot persist object identity, but the instrumented test
  (`test_p6_level_restart_and_no_state_reuse:215-260`) asserts original-metric
  object identity, three distinct freshly gathered L2 objects, per-level tag-seed
  distinctness and the frozen seed derivation; the pre-execute review reran it.
  Executed records are consistent with that path
  (`levels_invoked == termination_stage`, per-stage tags/feedbacks exact).

## 7. Bounded wording (`report.md` read fully, 53 lines)

- States "synthetic N=256 development evidence only", "not real-channel FER,
  reconciliation efficiency, key rate, qualification or promotion"; "undetected
  frames are never merged with exact frames"; planning-only f is not
  real-channel efficiency.
- Persists the failing gate honestly (`d1_exactly_nested_and_d2_disclosed_once
  | False`), the label `BLOCKED`, the four scientific gates true, and all
  headline accounting; no claim of promotion, efficiency or success.
- `undetected` is kept separate everywhere (buckets show `undetected: 0`;
  cells use exact only; never folded into exact).
- Non-blocking documentation note: `report.md` itself does not print the
  outcome table, per-stream breakdown or planning-only `f`; these are fully
  reported in `aggregate_summary.json` (`outcomes`, `per_stream`,
  `planning_only_f`), which the packet's reporting requirement read together
  with the artifact set satisfies.

## 8. Scope and state

- `git status --porcelain` = 59 entries, identical to the Pre-EXECUTE snapshot;
  the P6-attributable set matches the declared set: packet docs (20:42–21:22),
  `adaptive_l1.py` (20:59, new), `test_nbpolar_adaptive_l1.py` (21:06, new),
  `formal_ir/nbpolar/__init__.py` (21:07; diff adds the `adaptive_l1` imports and
  `__all__` names — predecessor phases' uncommitted exports remain in the same
  working-tree diff and were attributed by the Pre-EXECUTE review),
  `specs/nbpolar-phase4-p6/spec.md` (20:52), `tasks.md` P6 section (20:52), plus
  the two milestone docs at 20:42:29. No P6 task box is checked
  (`grep 'P6-' tasks.md | grep '\[x\]'` → 0).
- No `methods/nbpolar_adaptive_l1.py`; no file outside the packet changed after
  21:22:40; predecessor evidence/probe roots, `results/` and
  `outputs_comparison/` have zero files modified after 20:30 (metadata check
  only); accepted modules untouched (latest accepted mtime 17:14, before the P6
  session).
- HEAD `ab173f2a...` unchanged; no commit, no staging, no push; no new output
  root besides the single declared one.
- Attempt/streams/masters: attempt 1/1 consumed by this run (persisted in the
  artifacts: `attempts_consumed_before=0`, `attempts_consumed_by_this_run=1`,
  `retries=0`); streams 2026091550..54 and public masters 2026101550..54
  consumed; `STATUS.yaml` is untouched by the runner (`attempts_used: 0`,
  `independent_pre_execute: pending`, `independent_pre_result: pending`) —
  expected, the ledger belongs to the main thread, which should update it on
  adjudication.
- No rerun: one generation of the five files; the runner refuses an existing
  root; the frozen root was absent before the authorized execution (Pre-EXECUTE
  review) and has not been written again.

## 9. Closure statements

- The frozen 640-pair command was **not rerun** by this review; no frozen seed
  or master was used in any reviewer action. The only executions performed were
  (i) the focused test file re-run with the suite's own fresh test seeds, and
  (ii) two tiny diagnostic probes with fresh, non-refused seeds 2026091596/97
  written only under `/tmp/opencode/p6_prereview/`; neither touches the frozen
  output root or consumes an attempt.
- Attempt 1/1 is consumed; the failure root (`paired_adaptive_gate/` plus the
  persisted `BLOCKED` label and failing gate) is preserved byte-for-byte.
- The failing gate is diagnosed as a gate-check implementation defect (b) at
  `adaptive_l1.py:1336-1354` (`:1342` key, `:1352` count check) compounded by
  the stream-less event identity at `:866/:872/:909/:956`; the correct
  contract value would be true, but no repair/rerun/re-score is permitted and
  the main thread owns the disposition.
- This review wrote only
  `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/PRE_RESULT_REVIEW.md`.
  No commit, no push, no artifact/real-data access, no predecessor-root
  modification.

## Review commands (condensed, all read-only unless noted)

```
git rev-parse HEAD; git status --porcelain; git log --oneline ab173f2a..HEAD
find . -newermt '2026-09-13 21:22:40' -type f   # nothing outside this packet
python /tmp/opencode/p6_prereview/recompute.py  # all coverage/cells/totals/12+4 gates; 0 FAIL
python /tmp/opencode/p6_prereview/collision_probe.py  # production event ids collide across streams
python -m ...adaptive_l1 ... --seeds 2026091596 --blocks-per-seed 4 --out-dir /tmp/.../probe_1s   # gate4 true
python -m ...adaptive_l1 ... --seeds 2026091596 2026091597 --blocks-per-seed 4 --out-dir /tmp/.../probe_2s  # gate4 false only
pytest comparison_bench/tests/test_nbpolar_adaptive_l1.py -q -p no:cacheprovider  # 15 passed
```
