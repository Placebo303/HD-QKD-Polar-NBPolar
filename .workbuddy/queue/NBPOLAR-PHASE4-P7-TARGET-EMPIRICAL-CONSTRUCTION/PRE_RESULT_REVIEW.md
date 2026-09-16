# Pre-RESULT review — NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION

- Reviewer: independent `reviewer-go` (backup instance). Did not write the
  reviewed code, freeze the plan, or run the gate.
- Date: 2026-09-14 (WSL). Repository: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- HEAD during review: `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged;
  no commit, no push).
- Read-only: the only file written by this review is this document. The V25 NPZ
  was **not reopened** (metadata `stat` only; no second content read); the
  frozen gate command was **not rerun**. Persisted accounting remains
  reads **1/1**, attempts **1/1**, retries 0, no reopen.
- Interpreter used for every recomputation and test run:
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).

## Verdict: PASS

Every required recomputation reproduces the persisted values bit-for-bit or
within the ratified tolerances; all 11 integrity gates and 3 scientific gates
recompute true; the label `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` follows from
the frozen rule; the wording is bounded. No blocking issues. Non-blocking
observations are in §10.

---

## 1. Root and scalar-only audit

`ls -la` / `iterdir()` of
`.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`:

```
aggregate_summary.json            11,389 B   2026-09-14 03:33:09.130 +0800
construction_orders.json          43,137 B   2026-09-14 03:33:09.112 +0800
frozen_plan.json                   6,301 B   2026-09-14 03:33:09.108 +0800
per_block_paired_outcomes.json   925,631 B   2026-09-14 03:33:09.128 +0800
report.md                          2,554 B   2026-09-14 03:33:09.133 +0800
```

Exactly the five frozen files; no subdirectories, no extras; all five mtimes
within 25 ms (single generation).

Deep scalar-only audit (recursive walk of the four JSON documents):

- zero non-scalar leaves outside the records/orders structures; no
  numpy/bytes objects; no non-string keys;
- exactly **10** array-like objects are 256-entry permutations of `0..255`:
  `layers.{l1,l2}` × {3 per-stream, pooled, bec};
- every other list is a 5/11-element int or frozen-name list, or the 640-entry
  `blocks` record list (each entry a dict of scalars);
- no seed-bit/binary strings (`^[01]{16,}$` none), no base64-like blobs; the
  only long strings are the frozen rule/claim/command texts;
- per-block records contain no symbols, labels, decoded keys, disclosed values
  or metric vectors.

## 2. Input preconditions (ratified Pre-EXECUTE §3.3 semantics)

The raw-MLE table cannot be independently recomputed without reopening the NPZ
(this review is forbidden to do so; read 1/1 was consumed by the gate run).
Verification is therefore the recorded raw-MLE values against the frozen
literals plus full internal arithmetic consistency:

| quantity | recorded | frozen literal | diff | tol | ok |
|---|---|---|---|---|---|
| `h1` (raw MLE) | 0.024280546818678802 | 0.02428054681872374 | −4.4939746368655165e-14 | 1e-12 | yes |
| `h2` (raw MLE) | 0.7767572780789994 | 0.7767572780789994 | 0.0 | 1e-12 | yes |
| `total` (raw MLE) | 0.8010378248976782 | 0.8010378248977232 | −4.5075054799781356e-14 | 1e-12 | yes |
| `h1 + h2` vs `total` | — | — | 0.0 (exact) | — | yes |

Floor guard (floored-table functional, reported but never gated against the
literals):

- `floor_total − total = 5.1600945738528026e-11` = recorded
  `floor_entropy_change` exactly; `<= 1e-9` → **true**;
- component shifts: `floor_h1 − h1 = 4.5902306261558223e-11`,
  `floor_h2 − h2 = 5.6985527407960035e-12`, sum `5.160085900235423e-11`
  (float-rounding consistent with the recorded total);
- Pre-EXECUTE synthetic-mimic estimate was `4.263e-11 + 8.540e-12 = 5.117e-11`
  vs the run's `5.16009e-11`: difference `+4.31e-13` (h1 component `+3.27e-12`,
  h2 component `−2.84e-12`). **This is an estimate-vs-run difference**, not a
  semantics change: the mimic estimate was explicitly a synthetic sparse
  population with a different lifted-cell pattern, the floor contribution is
  data-dependent at the e-13/e-12 level, and both values are ~1.5–2 orders
  below the `1e-9` guard.

Column checks: `column_dev = 1.1357581541915351e-13 <= 1e-12` → true;
`p_b_sum = 1.0` (deviation 0.0); `no_zero_bob_column` recorded true
(raw-table quantity, not independently recomputable without content open).

## 3. Consumption / accounting

Persisted (identical in `frozen_plan.json` and `aggregate_summary.json`):

```
artifact_content_reads_allowed   = 1     consumed_before = 0   consumed_by_run = 1
attempts_allowed                 = 1     consumed_before = 0   consumed_by_run = 1
open_count = 1   retries = 0   reopen_attempted = false   retry_after_open = false
stat_size_checked = true   observed_npz_bytes = expected_npz_bytes = 25166822
input_mode = v25_npz   consumption point = "first NPZ content open (load_v25_channel_counts)"
```

Independent metadata check (stat only, no open):

```
stat -c 'size=%s mtime=%y' \
 /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/\
nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz
→ size=25166822  mtime=2026-08-19 01:34:09.691122000 +0800
```

Size matches the frozen expectation; mtime is ~26 days before the gate run
(2026-09-14 03:30–03:33 +0800) and was unchanged after all review test reruns,
consistent with read-only use. The runtime code has exactly one loader call
site (`target_construction.py:1597`) and no reopen path; the accounting is
self-reported by construction (see §10.3).

## 4. Construction orders and statistics

Recomputation from `construction_orders.json` (`layers`) with the pinned
interpreter; Spearman computed independently two ways — closed form
`1 − 6·Σd²/(n³−n)` and Pearson of the inverse permutations — replicating the
accepted definition `spearman_rank_corr(position_rank(a), position_rank(b))`:

- all **10/10** orders are permutations of `0..255` (numpy sort equality) —
  recorded `permutation: true` for both layers confirmed;
- pairwise TRAIN Spearman (recomputed == recorded, exact float equality);
  minimum L1 **0.9973291943236439**, L2 **0.9950453479056992**:

| pair | L1 | L2 |
|---|---|---|
| 1650\|1651 | 0.9986896314946212 | 0.9950453479056992 |
| 1650\|1652 | 0.9973291943236439 | 0.9991917486839094 |
| 1650\|pooled | 0.999124513618677 | 0.9961668860151064 |
| 1651\|1652 | 0.9979378862439917 | 0.9953629262989242 |
| 1651\|pooled | 0.9991338120851453 | 0.9994220645456626 |
| 1652\|pooled | 0.998675326161593 | 0.9960874914168002 |

- report-only pooled-vs-BEC Spearman recomputed == recorded (L1
  0.8991073472190433; L2 0.9430797951476311; all 4 per layer match);
- report-only top-K overlaps recomputed == recorded (L1 k=45: 41/45
  `0.9111111111111111` for three streams, 40/45 `0.8888888888888888` for
  stream 1652; L2 k=140: `0.9285714285714286`/`0.9357142857142857` as
  recorded);
- provenance consistency: pooled `e_sum`/`h_sum`/`n_used`/`n_impossible` equal
  the sum of the three per-stream records exactly for both layers
  (l1 1064.196534960643 / 4606.5562986784225, l2 30877.54708431538 /
  152677.45508716966; 768 used, 0 impossible per layer, 256/stream);
- `orders_sha256` recomputed as
  `sha256(json.dumps(layers, sort_keys=True, separators=(",", ":")))` =
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`, equal in
  all three places (recomputed, `construction_orders.json`,
  `aggregate_summary.json`);
- `frozen_before_dev: true` and `orders_unchanged_after_dev: true` recorded;
  code order independently inspected: freeze block `:1696–1718` precedes the
  first DEV call (`:1720+`), and the digest is recomputed after DEV (`:1790`).
  Temporal "before" evidence is code-order + the recorded flags; it is not
  independently reproducible from artifacts without a rerun (non-blocking §10.2).

## 5. DEV outcomes, coverage and disclosure

From `per_block_paired_outcomes.json` (640 records), independently recomputed:

- buckets: `empirical = {exact: 640, undetected: 0, verify_failed: 0,
  decode_failed: 0, resource_abort: 0}`; `bec` identical. Empirical exact
  **640/640**, BEC exact **640/640**;
- paired cells: `both_exact 640 / empirical_only 0 / bec_only 0 / neither 0`;
  each record's `cell` recomputed from the two `exact` flags matches;
- structural invariants (all 1280 arms): outcome == frozen precedence
  (`decode_failed` → `verify_failed` → `exact`/`undetected`), `exact ==
  tag_pass ∧ label_match`, `l2_invoked == l1_executed`,
  `tag_invoked == l2_invoked ∧ ¬l2_decode_failed`,
  `key_dependent_bits == 225 + 700·l2_invoked + 64·tag_invoked`,
  `public_control_bits == 2623·tag_invoked`, provenance labels correct:
  **0 findings**;
- per-stream: 5 streams × 128 records, block indices 0..127 complete per
  stream, all arms `exact` 128/128 (matches `per_stream` in the summary);
  TRAIN seed set and DEV seed set disjoint; TRAIN per-stream `n_used = 256`,
  `n_impossible = 0` in both layers (⇒ 3×256 attempted per the freeze code
  path);
- truth-leak flags: 1280/1280 `false`; `nonfinite` 0; `resource_abort` 0;
  `resource_stop_fired` false;
- disclosure: all 1280 fully invoked arms carry exactly 989 bits
  (225 + 700 + 64); per-arm totals 632,960 key / 1,678,720 public / 640 tags;
  totals **1,265,920 / 3,357,440 / 1280**; independent literal recount from the
  records equals the incremental totals equals the persisted recount; event
  types `l1=1280, l2=1280, tag=1280`; `mismatch_count = 0`, `mismatches = []`.

## 6. Wilson bound, gates, label, resources

One-sided 95% Wilson lower bound from `640/640`, `z = 1.6448536269514722`
(same formula as `protocol.wilson_lower_bound`):

```
center = 1 + z²/(2·640); margin = z·sqrt(z²/(4·640²)); denom = 1 + z²/640
LB = (center − margin)/denom = 0.9957903841321254   (recorded: identical)
```

Gate table (recomputed from the artifact records — not copied booleans):

| # | integrity gate | recomputed | persisted |
|---|---|---|---|
| 1 | target_population_contract | true | true |
| 2 | coverage_complete_and_disjoint | true | true |
| 3 | orders_frozen_permutations_provenance | true | true |
| 4 | pairing_and_buckets | true | true |
| 5 | truth_leak_zero | true | true |
| 6 | undetected_zero | true | true |
| 7 | nonfinite_zero | true | true |
| 8 | resource_abort_zero | true | true |
| 9 | disclosure_and_recount_exact | true | true |
| 10 | attempt_read_accounting_exact | true | true |
| 11 | resource_limits_met | true | true |

Scientific gates recomputed: min Spearman `0.9950453479056992 >= 0.95` → true;
`640 >= 620` with `planned_pairs == 640` → true; Wilson
`0.9957903841321254 >= 0.95` → true. Resources: wall `132.523651 s <= 3600`,
peak RSS `383,832,064 B <= 2,147,483,648` → true; `shape_is_frozen_640` true.
Deriving the label from the recomputed gates gives
`TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`, equal to the persisted
`outcome_label`. Report cross-check: every numeric value in `report.md` equals
the corresponding `aggregate_summary.json` value (wall, RSS, entropies, floor
change, column dev, epsilons, stability minima, cells, Wilson, disclosure
totals, planning `f`, label).

## 7. Truth-boundary audit (`target_construction.py`)

Read of the operational path (`sample_target_block`, `run_dev_arm`,
`run_dev_block`, sentinel) plus a grep of every truth-variable use confirms:

- L1 metric is built from Bob only (`build_p1_metrics(bob, P1)`, `:838`);
  L2 metric is gathered from Bob and the **decoded hard candidate**
  (`gather_p2_metrics(bob, high_hat, P2)`, `:867`), provenance
  `PRIOR_ONLY` / `CANDIDATE_CONDITIONED`;
- truth enters only: sampling, the disclosed `U` values
  (`u1_arr[l1_positions]`, `u2_arr[l2_positions]`), tag construction
  (`tag_true = tag_fn(labels_true_bits, …)`) and scoring
  (`label_match`), exactly the frozen boundary;
- per-layer SC restart with fresh metric objects and no state/belief
  transfer; the block sentinel mutates all truth copies after the
  metrics/decisions exist and requires the protected set to stay bitwise;
- module has no import-time I/O; the only writes are the five output files
  (`_write_json`, `report.md` at `:2145–2159`); no `open(`, no global RNG
  (explicit `np.random.default_rng` per stream).

## 8. Bounded-wording check (`report.md`, read in full)

- Scope line present: "frozen V25 TRAIN target-population empirical
  construction development signal at N=256 only; not held-out or real frame
  FER, efficiency, key rate, scaling, qualification or promotion";
- `planning-only f` explicitly marked "not real-channel efficiency";
- BEC comparisons shown as report-only; no winner/threshold/"beats BEC" claim
  anywhere (lexical scan: no `winner`/`threshold`/`beat`);
- `undetected` is stated as never success (`report.md` scope line and
  `claim_scope` in both JSON artifacts); no undetected events exist.
- Note for interpretation (non-blocking §10.6): both arms saturate at 640/640,
  so the run is a feasibility/development signal and carries no
  empirical-vs-BEC discrimination at this point; the wording correctly makes no
  comparative claim.

## 9. Tests and scope

Commands (pinned interpreter, fresh basetemps, `-q -p no:cacheprovider`):

```
python -m pytest comparison_bench/tests/test_nbpolar_target_construction.py \
  -q -p no:cacheprovider --basetemp=/tmp/opencode/p7_prereview/focused
→ 11 passed, 1 warning in 7.75s

python -m pytest comparison_bench/tests/test_nbpolar_*.py (16 files) \
  -q -p no:cacheprovider --basetemp=/tmp/opencode/p7_prereview/full
→ 228 passed, 1 warning in 107.46s
```

Additional audit-hook reruns (hook blocks any non-temp open whose path matches
`channel_counts`/`outputs_comparison`/`model_f_input`/`pairs.parquet`/`ttbin`):
focused 11 passed with **0** artifact opens; full 16-file suite 228 passed with
**0** non-temp artifact opens (175 opens were `/tmp/tmp*/model_f_input.npz`
fixtures created by the prior-artifact tests). A first, over-broad hook attempt
blocked those temp fixtures and produced 10 spurious failures — recorded here
for transparency; with the corrected hook the suite is clean. Test seeds are
`2026091680..86`, disjoint from the frozen streams.

Scope/state checks:

- `git log -1`: HEAD still `ab173f2a5e17336383a897b941080b731ba3dd9e`; no commit.
- `git status --porcelain`: the 16 tracked-modified files are the same
  pre-existing set seen at Pre-EXECUTE; 51 untracked entries, all inside the
  declared P7 surface (module, test file, P7 OpenSpec delta/tasks row, packet
  queue incl. the five-file output root) plus pre-existing untracked items.
- No file in the repository was modified after this review started (03:35)
  outside `target_construction_gate/`; `find comparison_bench/outputs_comparison
  results -newermt '2026-09-14 02:23:00'` → empty; old probe roots X06/X07
  still 00:52/01:47; accepted modules (`sc.py`, `prior.py`, `construction.py`,
  `protocol.py`, `two_layer.py`, `transform.py`, `algebra.py`,
  `empirical_channel.py`, `penalty_gate.py`, `adaptive_l1.py`,
  `incremental.py`, `v35_algorithm_development.py`, `__init__.py`) all carry
  mtimes before the P7 session; the only newer source file is the P7
  implementation `target_construction.py` (03:02:59).

## 10. Non-blocking observations

1. **STATUS.yaml stale.** It still reads `artifact_reads_used: 0`,
   `attempts_used: 0`, `independent_pre_result: pending` and the pre-run state.
   The authoritative accounting is in the artifacts (1/1/1). Main-thread
   record update after acceptance.
2. **Frozen-before-DEV is self-reported.** The direct temporal proof is
   internal to the run (digest at freeze vs after DEV). Artifact evidence is
   code order + exact digest equality + the recorded flag; acceptable, worth
   deriving the flag if the pattern is reused (same as Pre-EXECUTE §5.1).
3. **Attempt/read accounting is self-reported** (single verified call site,
   no external open counter). Corroborated by the stat-size check and the
   unchanged NPZ metadata; no rerun was possible or performed.
4. **Raw-MLE precondition quantities** (zero columns, column normalization,
   raw H1/H2/total) are not independently recomputable without a second NPZ
   content open; verified against the ratified semantics by recorded-value
   arithmetic and internal consistency.
5. **Pre-EXECUTE floor estimate vs run**: `5.117e-11` vs `5.16009e-11`
   (`+4.31e-13`) — estimate-vs-run, data-dependent, both far inside the
   `1e-9` guard.
6. **Comparative saturation**: empirical and BEC both 640/640; this gate shows
   feasibility at the conservative fixed disclosure point but cannot
   discriminate the two order families. For the main thread's scientific
   interpretation; no wording change needed (and none permitted post-run).
7. **RSS reading** `383,832,064 B` is ~5.6× under the 2 GiB cap; the
   Pre-EXECUTE note on WSL `ru_maxrss` reliability still applies, with the
   external `ulimit -v 2 GiB` as the hard bound.

## 11. Closure statements

- The registered V25 `channel_counts.npz` was **not reopened** by this review
  (only `stat` metadata: size 25,166,822; mtime 2026-08-19 01:34:09 +0800);
  no second content read.
- The frozen gate command was **not rerun**; test reruns used injected/mimic
  data only (verified by audit hook).
- Gate-run accounting stands at reads **1/1**, attempts **1/1**, `open_count 1`,
  `retries 0`, no reopen; label `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`.
- No artifact/real-data/old-root writes; only this file was written; HEAD
  unchanged; no commit or push.

## Checklist

- [x] Matches OpenSpec spec (P7 delta == packet; frozen constants and gate
      order confirmed in artifacts)
- [x] Tests pass (11 focused + 228 full on the pinned interpreter; hook runs
      show no artifact opens)
- [x] No scope creep (declared P7 file set only; accepted modules and old
      roots untouched)
- [x] Pre-RESULT recomputation complete (inputs, orders/statistics, outcomes,
      Wilson, accounting, all gates, wording)
- [ ] docs/decision-log.md / AGENT_PROJECT_MEMORY.md updates → main-thread
      milestone action after acceptance (not a Pre-RESULT prerequisite)

Verdict: **PASS** — the five artifacts are internally consistent, reproduce
under independent recomputation, and support the bounded
`TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` development-signal claim only.
