# Independent Pre-RESULT review — NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC

Reviewer: fresh independent reviewer-go instance (did not write the runner, the
freeze, the tests, or run the gate; read-only). Date: 2026-09-16.
Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`.
Artifacts reviewed (worktree, worktree-resident):
`.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`
(five files) plus the contract set (`TASK_PACKET.md`, `P19_FREEZE.md`,
`PRE_EXECUTE_REVIEW.md`, `STATUS.yaml`, `P19_IMPLEMENTATION_NOTES.md`) and
`comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_backoff_diagnostic.py`.

## VERDICT

**PASS_WITH_COMMENTS**

- **Blocking issues: none.** The finalized worktree artifacts are one
  internally consistent single-run record: 15/15 records, 27/27 SC, 15/15 tags,
  recount key 526200 / public 4916145 with zero mismatch, all 15 outcomes
  `verify_failed`, all 20 integrity gates recomputed true, label
  `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`, resources inside
  budget.
- The verdict is PASS_WITH_COMMENTS (not PASS) solely because of the **item A
  provenance anomaly**: a concurrent external commit landed the P11–P19 queue
  with a mid-run snapshot of the five artifacts on HEAD. It is **not a
  scientific failure** and does not invalidate the run, but acceptance must
  read the worktree files, never the HEAD blobs (mandatory handling
  instructions in item A.4 below).
- All numbers below were recomputed from the worktree artifacts, not copied
  from the context summary. One context-summary value was found to disagree
  with the artifacts (finding N-A); the artifacts are authoritative.

---

## ITEM A — concurrent external commit: adjudication

### A.1 The five worktree files are one finalized single-run record — PASS

Parsed independently (`json.loads`, line-by-line JSONL):

- exactly five files, no extras/sidecars; jsonl exactly 15 lines; all 12
  operational lines share one 45-key set and the 3 control lines add only the
  by-design `provenance` key (46 keys; `_control_record` line 858, confirmed in
  code).
- 15/15 records = 5 arms x 3 blocks in arm-major order
  (`base,l1_plus,l2_plus,both_plus,true_l1_control`), block indices `[0,1,2]`
  each.
- all 15 `outcome == "verify_failed"`, `exact false`, `tag_pass false`,
  `tag_invoked true`; every `error is None`; no `undetected`, no `nonfinite`,
  no `resource_abort`, no `truth_leak_violation`.
- `created_utc` ordering monotone in the same clock domain:
  `frozen_plan 2026-09-16T13:10:52Z` <= `identity 13:10:52Z` <=
  `aggregate 13:13:55Z`; file mtimes 21:10:52.58 / 21:13:55.83-88 +0800, all
  <= the external commit time 21:14:28 +0800.
- recount rebuilt from the records with the frozen event builder
  (`backoff_block_events` -> `backoff_recount_events`) equals the persisted
  recount: `{key 526200, public 4916145, tags 15, events l1 12 / l2 15 /
  tag 15}`, `_transcript_mismatches` empty.
- sums: per-record key bits 102357+104277+110037+111957 (operational) + 97572
  (control) = 526200; public 15 x 327743 = 4916145; per-record walls sum
  184.093475 s <= total `wall_s` 186.421779 s.
- no torn/duplicated/mixed-run content: unique (arm, block) keys, identical
  `protocol`, ranges `[1600..1727],[1728..1855],[1856..1983]` per arm,
  `frame_count 128`.

### A.2 The committed snapshot cannot be mistaken for the result — CONFIRMED

`git status --porcelain` (worktree): the four files are ` M` (unstaged), 
`frozen_plan.json` clean. Blob identity (via `git rev-parse HEAD:<path>` /
`git hash-object` / `git ls-files -s`; index == HEAD for all five):

| file | committed blob (HEAD = index) | worktree blob |
|---|---|---|
| aggregate_summary.json | fffc9a240bde250b0b6d7e8a91f20272a3e87159 | 69b74baa22b6ffb732cfc167d9eac43190f4a3b5 |
| input_and_predecessor_identity.json | d6de6695ddc42d4884fb23abbbbc91ccdd53aed4 | 6e16dc5d97c2f77350ec2d26514ad25e51d90dea |
| per_block_arm_outcomes.jsonl | d3168cfc01d4f0f92b861746749c9ec67a6808bb | 3313a2a21cc7b97b3dbe8584c6367cdd3bca137f |
| report.md | 422a30feef316c35322ca52202cea7a0ef83096a | 81ecfe2961e56dbc08e602d25ef774bce116ca3d |
| frozen_plan.json | 6d21510e9924e79e2cdc0a24357623e315189907 | identical (byte-identical) |

The committed blobs are a strict sub-state of the finalized run (verified by
`git show HEAD:<path>` parsing):

- committed aggregate: `outcome_label: RUNNING(record 11/15)`,
  `records_completed 11/15`, `sc_calls 22`, `tag_invocations 11`,
  `integrity_all_pass false`, `failing_integrity_gates
  ["sc_calls_exact","tags_exact"]`, `partition {operational 11, oracle_control
  0, total 11}`, `created_utc 13:13:21Z`, `oracle_control` arm empty;
- committed jsonl: 11 lines; committed report:
  `records: 11/15; SC calls: 22/27; tags: 11/15`;
- committed identity JSON differs only in
  `attempt_read_accounting.attempt_read_accounting_finalized` (absent vs
  `true`).

Neither blob can be read as a COMPLETE result (label is `RUNNING`, gates
false). **The finalized worktree files are the authoritative evidence; the
committed snapshot is a superseded mid-run checkpoint and must not be used
for acceptance.**

### A.3 The commit did not touch either protected input, and did not alter the run — PASS

- commit `faac0411` file list: 451 entries, **zero** under
  `nonbinary_diagnostics`, **zero** `.npz`/`.parquet`; the HOLD parquet path is
  untracked and not part of the commit; the NPZ lives in the sibling checkout.
- protected inputs now (stat only, no content open): NPZ 25,166,822 B /
  mtime_ns 1787074449691122000; parquet 1,354,289 B / mtime_ns
  1789155517259296100 — **current == recorded before/after == P19_FREEZE §11**
  (unchanged by the run and by the commit).
- ordering: committed snapshot `created_utc 13:13:21Z` < finalized
  `created_utc 13:13:55Z` < commit ts `2026-09-16 21:14:28 +0800`
  (=13:14:28Z); i.e. the external `git add` captured an 11/15 checkpoint
  while the run was live, and the commit landed ~33 s **after** the run's final
  write (this is an add-before-commit race, not a mid-write clobber).
- no history rewrite: `git reflog` has exactly two entries (initial clone,
  the external commit); no new commit since; `git diff --cached` empty (no
  staged content after the commit — so no post-finalization `git add`).
- no shared predecessor code changed around the run: runner/test mtimes
  20:02–20:03, `holdout_microcheck.py` 00:35, `operational_f13.py` 09-15 16:27,
  `operational_f13_replication.py` 09-15 19:38, `target_construction.py`
  09-14, `sc.py` 09-14 19:35 — all before the run start (~21:10:37). The
  external commit's `M` entries in `comparison_bench/src/.../nbpolar/`
  (`__init__.py`, `empirical_*.py`, `sc.py`, a test file) have worktree mtimes
  09-13/09-14, i.e. they are pre-existing accepted-work modifications that the
  consolidation commit merely versioned; none changed during the run window.

### A.4 Ruling + mandatory acceptance handling

**Ruling: the anomaly does NOT block the Pre-RESULT verdict and is not a
scientific failure.** Basis: the commit is additive to `HEAD` only, `git
add`/`git commit` never write worktree files, the finalized worktree files are
self-consistent as one 15/15 run, and the commit landed after the final write
(≥32 s margin, same-domain timestamps). There is no evidence of any process
writing to the five artifacts other than the run itself.

Residual uncertainty (stated exactly): the external process's full command
history is not observable — only its committed effect (`add`+`commit`), the
reflog, and the worktree state are. I verified every observable consequence
(worktree content, mtimes, index state, protected-input stats) and found no
interference signal; I cannot prove the absence of unrelated concurrent
processes, but no such process left any trace in the reviewed scope.

**Acceptance instructions (binding):**

1. Accept from the **worktree** files only. Read them from the filesystem; do
   **not** use `git show HEAD:<path>` for any of the five files. The
   authoritative worktree hashes are:
   `aggregate 69b74baa…`, `identity 6e16dc5d…`, `jsonl 3313a2a2…`,
   `report 81ecfe29…`, `frozen_plan 6d21510e…`; md5:
   `80ce92cf800bd3e4e8fddcdd559fbfc2`, `70e98e8d79a760d90bbb6c9a2ef74e77`,
   `e56474f157f18a8ed0837eb657f9f7d9`, `1747e2698a63e94742f3bafb289786bf`,
   `185c8e12b94eb900ce9122370f1b5ea7`.
2. Do **not** run `git restore`/`git checkout --`/`git stash`/`git reset
   --hard` on those four modified paths — it would overwrite the finalized
   artifacts with the superseded 11/15 snapshot and destroy the evidence.
3. If a commit is eventually authorized, `git add` the four finalized files
   after acceptance and cite the worktree hashes; do not push/describe
   `faac0411`'s blobs as the P19 result.
4. At memory triage, record the race as a provenance incident (see findings).

### A.5 No packet-operator git write — evidence

- The only HEAD movement after the clone is the external commit
  `faac0411` (author/committer `Placebo303 <karel.yangkai303@gmail.com>`,
  message "docs: consolidate NB-Polar research state and Astra pack",
  2026-09-16 21:14:28 +0800). No agent-authored commit, no push refs, no tags,
  no other reflog entries.
- The commit contains a mid-run snapshot (RUNNING 11/15) that a post-run
  operator commit could not have produced deliberately; it is consistent with
  an unsynchronized external add-before-commit.
- Worktree shows the four P19 files unstaged (` M`, not `M `) and index blobs
  == HEAD blobs: no `git add` happened after finalization.
- Conclusion: no evidence of any git write by this packet's operators. (The
  external commit is by the human/main-thread identity and is the only write.)

---

## NUMBER-BY-NUMBER RECOMPUTATION

All values below were produced by independent parse/recompute scripts under
`/tmp/p19_audit/` run with the pinned interpreter; the runner module was
imported only for its frozen constants/helpers (import performs no I/O).

### 1. Root/inventory/scalar-only — PASS

- `ls` root: exactly `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl`, `aggregate_summary.json`, `report.md`; no
  sidecars; queue dir holds only the 7 contract docs + the five files.
- Deep scalar walk: no arrays/vectors; every list is scalar and small
  (block ranges, `l1_head8`/`l2_head8` = 8 public order-head ints,
  `predecessor_dev_seeds` = the 8 public P16 seed identifiers 2026092010-17,
  `exact_counts_ordered`, arm lists). No seed-bit material, no counts,
  samples, labels, metric planes, per-arm orders; `seed_bits` appears nowhere;
  `stream_seed` is popped for operational records (`_operational_record`
  line 814).

### 2. Identity/manifest/preconditions — PASS

- P16 digest recomputed with **my own** canonical-JSON sha256 from the P16
  JSON (not the verifier): `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  == stored `freeze_sha256` == recorded `digest_recomputed` == frozen flag.
  n=32768, k1/k2/k_total 319/6492/6811, f=1.2998502888172847, leakage 34119;
  both orders are full valid permutations (re-derived).
- split manifest (read live): schema `nbldpc_v25_split_manifest_v1`, source tag
  `type2_1M_20260121_184040`, HOLD 400 frames / 102400 pairs, TRAIN 1200/307200,
  VAL 400/102400; live dict == recorded dict.
- P18 block pin: `verify_p18_block_identity()` verified True, all 15 sub-checks
  True, recorded pin identical; remainder `1984..1999` = 16 frames / 4096 pairs
  declared unused.
- preconditions vs literals (tol 1e-12 / floor guard 1e-9): h1
  0.024280546818678802 vs literal 0.02428054681872374 (dev 4.49e-14); h2 exact
  (dev 0); total 0.8010378248976782 vs 0.8010378248977232 (dev 4.51e-14);
  `floor_entropy_change` 5.160e-11 <= 1e-9; floor_total - total = +5.16e-11
  (floor raises entropy); `p_b_sum` 1.0; `column_dev` 1.14e-13 <= 1e-12; all
  7 recorded checks True. Scope limit: h1/h2 themselves are not recomputable
  without reopening the protected NPZ (forbidden); verified at
  tolerance/consistency level from the persisted record.

### 3. Blocks/records/K replay/domain — PASS

- 15 records; per-arm 3; ranges per arm exactly
  `[1600,1727],[1728,1855],[1856,1983]`, `frame_count 128`;
  population arithmetic 3x128+16=400 frames, 3x32768+4096=102400 pairs.
- per-record K/leakage replay exact: k1 {base 319, l1_plus 447, l2_plus 319,
  both_plus 447, control 0}; k2 {6492,6492,7004,7004,6492}; full-block key
  bits {34119, 34759, 36679, 37319, 32524}; per-record `key_dependent_bits =
  5*K1 + 5*K2*(l2_invoked) + 64*(tag_invoked)` exact; prefixes
  `l1_prefix_len/l2_prefix_len` == spec; `arm_index` exact; increments +128 /
  +512 exact; `chunk_rows` 512 in plan and aggregate, CLI/`_check_chunk_contract`
  path pinned (line 1860), records do not carry chunk_rows (scope note only).
- tag master 2026092060; 15 recomputed seeds all length 327743 bits and all
  distinct; P19 prefix `nbpolar-p19-holdout-backoff-diagnostic-seed` differs
  from the P16/P17/P18 module prefixes
  (`…p16-operational-f13-seed`, `…p17-operational-replication-seed`,
  `…p18-holdout-microcheck-seed`), and the same-args SHA-256 digest differs
  from all three predecessor domains.

### 4. Buckets/accounting — PASS

- outcomes: 15 x `verify_failed`; bucket keys unique; outcome values subset of
  the frozen 6 buckets; `record_dict_consistent` true for all 15.
- L1 correctness per block: base `[True,False,False]`, l1_plus `[True,True,True]`,
  l2_plus `[True,False,False]`, both_plus `[True,True,True]`, control `null`
  (l1 not executed) — fully consistent with K1 (319 vs 447).
- tag results: 15 invoked, 15 false.
- key-dependent bits: operational 3*(34119+34759+36679+37319) = 428628;
  control 3*32524 = 97572; total 526200 == recorded. Public 15*327743 =
  4916145 == recorded. Per-record `public_control_bits` 327743 when tagged.
- recount (rebuilt from records): `key 526200, public 4916145, tags 15,
  l1_disclosure 12, l2_disclosure 15, verification_tag 15`; mismatches `[]`;
  zero undetected / nonfinite / truth-leak; `provenance_violations 0`.
- per block: `raw_ser` 0.240936279296875 / 0.23980712890625 /
  0.240264892578125; `l1_nll` 773.8421894692976 / 868.6436203445395 /
  806.8510674338244; `l2_nll` 26815.50805586987 / 27015.516878425602 /
  26881.237733518323; `total_nll` 27589.350245339167 / 27884.160498770143 /
  27688.088800952148 — identical across all five arms in each block (fixed-prior
  truth-scored descriptive metrics), matching the context's quoted values.

### 5. Paired diagnostics + aggregation isolation — PASS

- recomputed `recovery_diagnostics(records)` == persisted:
  `exact_counts_ordered [0,0,0,0]`, `first_operational_recovery_arm null`,
  `ordered_exact_counts_non_monotone false`, paired tables
  `l1_plus/l2_plus/both_plus = {"verify_failed->verify_failed": 3}`,
  recovered 0 / lost 0 / same 3; no-threshold note present.
- operational aggregates EXCLUDE the control: operational record_count 12,
  key 428628, public 3932916, NLL 332646.39818024583, `oracle_control_excluded
  true`; control aggregate separate (3 records, key 97572, NLL
  83161.59954506146, deployable false, excluded true); partition
  `{operational 12, oracle_control 3, unassigned 0, total 15}`.
- CE ratios recomputed (Σkey/ΣNLL per arm over only that arm's records):
  base 102357/83161.59954506146 = **1.230820481567787**;
  l1_plus 104277/83161.59954506146 = **1.2539080605766497**;
  l2_plus 110037/83161.59954506146 = **1.3231707976032374**;
  both_plus 111957/83161.59954506146 = **1.3462583766121001**;
  control 97572/83161.59954506146 = **1.1732819057566373** (per-record control
  ratios 1.178860673077811 / 1.166396958640175 / 1.1746567353858512). Every
  persisted ratio equals the recomputed one; each ratio note says "explicitly
  NOT qualification reconciliation efficiency".
  **Context discrepancy (finding N-A):** the context summary's third
  operational ratio `1.339389` does not exist in any artifact (grep: no
  occurrence); the artifact value for `l2_plus` is **1.3231707976032374**.
  Neither the label, any gate, nor any claim depends on the summary value.

### 6. Label derivation — PASS

- all 20 gates recomputed true from the persisted records/identity/accounting
  (table below); persisted gates all true; `failing_integrity_gates []`;
  `backoff_label(recomputed gates)` =
  `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` == persisted.
- decision block: `recovery_threshold null`, `zero_recovery_is_complete true`,
  `three_recovery_is_complete true`; no Wilson/FER/exact-count/superiority
  code path exists (functional grep finds only the no-threshold prose; no
  `protocol.wilson` import); BLOCKED not taken.

### 7. Consumption/inputs — PASS

- `reads 1/1 + 1/1`, `attempts 1/1`, `counts_content_opens 1`,
  `hold_content_opens 1`, `retries 0`, `reopen_attempted false`,
  `retry_after_open false`, accounting `finalized true` (both JSONs);
  `opened_content_paths == registered_content_paths` (2 exact absolute paths);
  NPZ size check 25,166,822 passed pre-open.
- current stat (metadata only) == recorded before == recorded after for both
  inputs (values in A.3); `input_stat_unchanged` recomputed true.

### 8. Resources — PASS

- `wall_s 186.421779` <= 600; `rss_bytes_peak 615960576` <= 2147483648;
  per-record `rss_bytes_hwm` max 615960576, `vm_peak_kb` max 1,858,464
  (~1.77 GiB), `vm_size_kb` max 1,660,572 (~1.58 GiB), all < 2 GiB ulimit;
  resource stop not fired, `rejected_after_resource_stop false`, 0 aborts.
- Note (finding N-D): in-run monotonic wall vs realtime mtimes differ by
  ~3.1 s (derived start 21:10:49.5 vs `frozen_plan.json` mtime 21:10:52.6),
  consistent with a small WSL2 realtime adjustment; immaterial — all ordering
  claims use same-domain `created_utc` values with >=32 s margins.

### 9. Bounded wording — PASS

`report.md` read in full (72 lines). Checked sentences for FER / winner /
monotonicity / superiority / route / qualification / deployable / pass-fail:
every occurrence is a negation or an explicit neutrality statement ("no
threshold, no winner"; "reported neutrally: no monotonicity, superiority,
winner or threshold claim"; "never an operational protocol or deployable
rate"; "not real-frame FER, reconciliation efficiency, leakage, key rate,
scaling superiority, qualification or promotion evidence"; "explicitly NOT
qualification reconciliation efficiency"; "recovery threshold: None (none;
every 0/3..3/3 recovery pattern is a descriptive COMPLETE)"). No pass/fail
verdict words; the per-arm `exact (of 3) | 0` column is descriptive; oracle
control is isolated (`deployable False`, "excluded from every operational
aggregate"); the CE-ratio is labelled not-qualification-efficiency; the
remainder is recorded unused.

### 10. Tests re-run (independent) — PASS

Pinned interpreter, fresh `/tmp` basetemps, `-q -p no:cacheprovider`:

- `test_nbpolar_holdout_backoff_diagnostic.py` → **30 passed** (41.98 s)
- `test_nbpolar_operational_f13.py` → **23 passed** (486.09 s)
- `test_nbpolar_operational_f13_replication.py` + `test_nbpolar_holdout_microcheck.py`
  → **51 passed** (384.03 s)

Observed 30 + 23 + 51 = 104, exactly the expected counts. No protected input
was opened by any suite (loaders monkeypatched; protected stats unchanged
after the runs; no new files under `results/` or
`comparison_bench/outputs_comparison/`).

---

## GATE TABLE (recomputed vs persisted)

| gate | recomputed | persisted |
|---|---|---|
| predecessor_construction_identity | True | True |
| hold_split_manifest_identity | True | True |
| p18_block_range_identity | True | True |
| target_population_contract | True | True |
| hold_population_exact | True | True |
| blocks_exact_with_declared_remainder | True | True |
| fifteen_records_exact | True | True |
| sc_calls_exact | True | True |
| tags_exact | True | True |
| orders_valid_k_prefixes_within_registered_arms | True | True |
| oracle_isolation | True | True |
| buckets_disjoint_exhaustive | True | True |
| undetected_zero | True | True |
| nonfinite_zero | True | True |
| truth_isolation | True | True |
| disclosure_recount_exact | True | True |
| one_open_per_protected_input | True | True |
| input_stat_unchanged | True | True |
| no_unregistered_access | True | True |
| resource_limits_met_and_no_abort | True | True |

20/20 true, recomputed label == persisted label. Verification scope limits
(stated for honesty): the raw-population sub-checks (256 rows/frame,
pair_idx 0..255, symbol range 0..1023) and the entropy raw computation cannot
be re-derived from scalar artifacts without reopening the protected inputs
(forbidden); they are covered by the persisted in-run gates plus the
independent arithmetic/tolerance and permutation re-derivations above.

## Non-blocking findings

- **N-A** Context summary's operational CE ratio for `l2_plus` (`1.339389`)
  disagrees with the artifacts (1.3231707976032374); no occurrence of
  1.339389 in any of the five files. Context transcription error; artifacts
  authoritative; no gate/label/claim impact.
- **N-B** `aggregate_summary.json`'s `integrity` mapping is alphabetically
  ordered (accepted shared writer uses `sort_keys=True`); the frozen gate
  order is preserved in `report.md`'s table and in the runner's
  `INTEGRITY_GATE_ORDER`. Only affects `BLOCKED(<earliest gate>)` naming, and
  no gate failed. Cosmetic.
- **N-C** `STATUS.yaml` is stale relative to the executed lifecycle
  (`state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`, reads/attempts used
  0, `result: null`, `pre_result_review: pending`). The authoritative
  consumption record is the artifact accounting (reads 1/1+1/1, attempt 1/1,
  finalized). Main thread should update durable status at acceptance.
- **N-D** ~3.1 s monotonic-vs-realtime skew (see item 8); no impact.
- **N-E** During this review window an external docs activity appeared
  (`docs/nbpolar/DOCUMENT_INDEX.md` +6 lines at 21:24:45 and the untracked
  `docs/nbpolar/astra6_projectwide/` pack). Docs-only, unstaged, does not
  touch the five artifacts or any protected input; recorded for completeness.

## Closures

- **NEITHER protected input was reopened** by this review: `channel_counts.npz`
  and `pairs.parquet` were accessed with `stat` only (sizes/mtimes exactly as
  recorded, unchanged); no content open, no attempt consumed.
- **The gate was NOT rerun** (attempt 1/1 already spent; no execution of the
  runner). No Model-F/raw/real/EVAL access; no P12-P18/old-root writes; no
  writes under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push and no attempt to reconcile the external commit.
- Reads 1/1 + 1/1, attempt 1/1; no reopen/retry (artifact accounting).
- The only file written by this review is this `PRE_RESULT_REVIEW.md`. The
  five artifact files are byte-identical before/after review (md5 recorded
  above); their mtimes remain 21:10:52 / 21:13:55.
- Verdict does not accept results or choose a route; acceptance remains a
  main-thread decision, which must apply the item A.4 handling instructions.
