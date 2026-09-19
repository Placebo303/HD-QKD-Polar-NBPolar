# Operator return — Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic

- Task: `NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC` (Tier Y, single attempt)
- Operator: documentation session, operator only (no acceptance)
- Date: 2026-09-16 (WSL); branch `codex/nbpolar-phase0`
- Result label: `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`
- State: `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE_PENDING_MAIN_THREAD_ACCEPTANCE`;
  this return is not an acceptance

## 1. Mission

On the exact three accepted P18 HOLD blocks (frames 1600..1727, 1728..1855,
1856..1983 of the 1M `pairs.parquet`), determine **descriptively** whether
additional L1 disclosure (+128 coordinates), additional L2 disclosure (+512
coordinates), both, or true-L1 conditioning changes hard recovery. This is a
five-arm real-input layer/backoff diagnostic at N=32768. It is not a FER gate
and has no recovery, winner, monotonicity or qualification threshold: every
recovery pattern (0/3..3/3) is a descriptive COMPLETE when integrity holds, and
only integrity or resource failures produce `BLOCKED(<earliest gate>)`.

## 2. Implementation and tests

- Runner: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_backoff_diagnostic.py`
  (thin P19 wiring; accepted P16 operational helpers, the accepted P17
  predecessor verifier, the accepted P18 loading/block formation, the accepted
  P7 floor/support/preconditions and the accepted P11 chunked SC reused
  unchanged).
- Focused tests: `comparison_bench/tests/test_nbpolar_holdout_backoff_diagnostic.py`.
- OpenSpec P19 delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p19/spec.md`;
  tasks appended to the P19 section, no box checked.
- Test runs (pinned interpreter, fresh `/tmp` basetemps): 30 passed (P19
  focused) + 23 passed (`test_nbpolar_operational_f13.py`) + 51 passed
  (`test_nbpolar_operational_f13_replication.py` + `test_nbpolar_holdout_microcheck.py`)
  = **104 passed**; independently re-run by the Pre-RESULT reviewer with the same
  counts. No protected input was opened by any suite (real-path loaders
  monkeypatched/stubbed).
- No change to decoder, prior, construction, disclosure, tag, packing or
  outcome semantics. No commit, no push by this packet's operators.

## 3. Pre-run checks (before the single execution)

- Independent `reviewer-go` Pre-EXECUTE review: **PASS WITH COMMENTS**
  (`PRE_EXECUTE_REVIEW.md`); four non-blocking findings N1–N4, none able to
  change the run, a gate or a scientific conclusion. N1: the `FROZEN_COMMAND`
  literal persisted in `frozen_plan.json` reads `cd /mnt/Code/…` (missing
  `d`), while `P19_FREEZE.md` §6 and every other command line are correct
  `/mnt/d/Code/…`; the string is never executed and `/mnt/Code` does not
  exist, so a copied command would fail loudly with no side effects. The
  freeze command is authoritative.
- Output root `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`
  absent before execution; reads 0/1 and attempt 0/1 at that time.
- Identity/manifest/P18-pin preconditions verified before any protected open;
  neither protected input content-opened by either review (stat/JSON only).

## 4. Frozen command and run outcome

Verbatim frozen command (`P19_FREEZE.md` §6, authoritative; four lines):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_backoff_diagnostic --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --hold-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 --tag-master 2026092060 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic
```

- Exit code 0; stderr empty.
- In-run `wall_s` 186.421779 s (≤ 600 s); outer wrapper ≈ 206.7 s (600 s
  external timeout not fired).
- One execution only; no rerun, repair, retune, seed/parameter/arm change or
  cleanup.

## 5. Identity, manifest and preconditions

- Predecessor P16 digest match true: recomputed = stored = flag =
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`;
  N=32768, K1=319, K2=6492, K_total=6811, leakage=34119,
  f=1.2998502888172847 ≤ 1.3; both orders full valid permutations of length
  32768.
- Split manifest `nbldpc_v25_split_manifest_v1`: 1M `type2_1M_20260121_184040`
  HOLD = 400 frames / 102400 pairs (required 400/102400); TRAIN 1200/307200,
  VAL 400/102400.
- P18 block-range pin (`verify_p18_block_identity`): verified true, all 15
  sub-checks true; blocks `1600..1727`/`1728..1855`/`1856..1983`, remainder
  `1984..1999` = 16 frames / 4096 pairs declared unused.
- Preconditions 7/7 true: H1 0.024280546818678802 (literal 0.02428054681872374,
  deviation 4.49e-14), H2 0.7767572780789994 (deviation 0.0), total
  0.8010378248976782 (literal 0.8010378248977232, deviation 4.51e-14), floor
  entropy change 5.1600945738528026e-11 ≤ 1e-9, column deviation
  1.1357581541915351e-13 ≤ 1e-12, `p_b_sum` 1.0, no zero Bob column.

## 6. Consumption

- Attempts allowed 1 / consumed 1; consumption point = first protected content
  open (`load_v25_channel_counts`).
- NPZ content opens 1/1; HOLD parquet content opens 1/1; `retries` 0,
  `reopen_attempted` false, `retry_after_open` false; both persisted accounting
  copies (`input_and_predecessor_identity.json` and the copy in
  `aggregate_summary.json`) finalized.
- `opened_content_paths` == `registered_content_paths` (two exact absolute
  paths); pre-open NPZ size check 25,166,822 bytes passed.
- Input stats before == after and unchanged: NPZ 25,166,822 B / mtime_ns
  1787074449691122000; parquet 1,354,289 B / mtime_ns 1789155517259296100. No
  reopen.

## 7. Five frozen arms (K, leakage, per-block SC/tag; no threshold)

| arm | kind | K1 | K2 | leakage bits | SC/block | provenance | exact (of 3) |
|---|---|---|---|---|---|---|---|
| base | operational | 319 | 6492 | 34119 | 2 | OPERATIONAL | 0 |
| l1_plus | operational | 447 | 6492 | 34759 | 2 | OPERATIONAL | 0 |
| l2_plus | operational | 319 | 7004 | 36679 | 2 | OPERATIONAL | 0 |
| both_plus | operational | 447 | 7004 | 37319 | 2 | OPERATIONAL | 0 |
| true_l1_control | oracle_control | 0 | 6492 | 32524 | 1 | ORACLE_TRUE_L1_CONTROL | 0 |

Fixed increments +128 L1 / +512 L2; `chunk_rows=512`; tag master 2026092060;
27 SC calls and 15 tags in total. `base` replays the accepted P16 operational
point (f ≤ 1.3); the three `*_plus` arms disclose above the accepted planning
budget and are descriptive diagnostic disclosure levels, not qualified
operational points.

## 8. Per-record summary (15/15 records; all `verify_failed`)

Shared per-block values (identical across all five arms in that block —
fixed-prior truth-scored descriptive metrics):

| block | frames | raw SER | L1 NLL bits | L2 NLL bits | total NLL bits |
|---|---|---|---|---|---|
| 0 | 1600..1727 | 0.240936279296875 | 773.8421894692976 | 26815.50805586987 | 27589.350245339167 |
| 1 | 1728..1855 | 0.23980712890625 | 868.6436203445395 | 27015.516878425602 | 27884.160498770143 |
| 2 | 1856..1983 | 0.240264892578125 | 806.8510674338244 | 26881.237733518323 | 27688.088800952148 |

Per (arm, block) outcome record:

| arm | block | outcome | L1 correct | tag | key-dep bits | public bits | CE ratio | wall s |
|---|---|---|---|---|---|---|---|---|
| base | 0 | verify_failed | true | false | 34119 | 327743 | 1.236673 | 13.361351 |
| base | 1 | verify_failed | false | false | 34119 | 327743 | 1.223598 | 13.632511 |
| base | 2 | verify_failed | false | false | 34119 | 327743 | 1.232263 | 13.00025 |
| l1_plus | 0 | verify_failed | true | false | 34759 | 327743 | 1.259870 | 12.989782 |
| l1_plus | 1 | verify_failed | true | false | 34759 | 327743 | 1.246550 | 13.945373 |
| l1_plus | 2 | verify_failed | true | false | 34759 | 327743 | 1.255377 | 13.598242 |
| l2_plus | 0 | verify_failed | true | false | 36679 | 327743 | 1.329462 | 14.069716 |
| l2_plus | 1 | verify_failed | false | false | 36679 | 327743 | 1.315406 | 13.81042 |
| l2_plus | 2 | verify_failed | false | false | 36679 | 327743 | 1.324721 | 13.67355 |
| both_plus | 0 | verify_failed | true | false | 37319 | 327743 | 1.352660 | 13.636906 |
| both_plus | 1 | verify_failed | true | false | 37319 | 327743 | 1.338358 | 13.164644 |
| both_plus | 2 | verify_failed | true | false | 37319 | 327743 | 1.347836 | 13.194333 |
| true_l1_control | 0 | verify_failed | null (not executed) | false | 32524 | 327743 | 1.178861 | 7.344307 |
| true_l1_control | 1 | verify_failed | null (not executed) | false | 32524 | 327743 | 1.166397 | 7.299835 |
| true_l1_control | 2 | verify_failed | null (not executed) | false | 32524 | 327743 | 1.174657 | 7.372255 |

Each operational record: `frame_count` 128 (× 256 pairs = 32768 symbols), one
L1 + one candidate-conditioned L2 SC, one 64-bit tag, `l1_provenance`
PRIOR_ONLY, `l2_provenance` CANDIDATE_CONDITIONED, `truth_leak_violation`
false, `error` null. Each control record: one oracle-conditioned L2 SC (L1 not
executed), `l2_provenance` ORACLE_CONDITIONED, `oracle_control` true,
`oracle_truth_use` true, `provenance` ORACLE_TRUE_L1_CONTROL.

Per-arm aggregates (all 3 blocks; CE ratio = Σ key-dependent bits / Σ total NLL
bits, a sample CE-normalized descriptive disclosure ratio, explicitly **not**
qualification efficiency):

| arm | key-dep bits | total NLL bits | aggregate CE ratio | exact_count | outcome_counts |
|---|---|---|---|---|---|
| base | 102357 | 83161.59954506146 | 1.230820481567787 | 0 | verify_failed 3 |
| l1_plus | 104277 | 83161.59954506146 | 1.2539080605766497 | 0 | verify_failed 3 |
| l2_plus | 110037 | 83161.59954506146 | **1.3231707976032374** | 0 | verify_failed 3 |
| both_plus | 111957 | 83161.59954506146 | 1.3462583766121001 | 0 | verify_failed 3 |
| true_l1_control (excluded; deployable false) | 97572 | 83161.59954506146 | 1.1732819057566373 | 0 | verify_failed 3 |

Transcription note N-A: an earlier operator transcription of the `l2_plus`
aggregate CE ratio said `1.339389`; the ARTIFACT value is
Σkey/ΣNLL = 110037 / 83161.59954506146 = **1.3231707976032374**, and the
per-block ratios 1.329462 / 1.315406 / 1.324721 stand. The artifacts are
authoritative; no gate, label or claim depends on the transcribed value.

## 9. Paired/first-recovery diagnostics and oracle isolation

- ordered operational exact counts: [0, 0, 0, 0]; `first_operational_recovery_arm`
  null; `ordered_exact_counts_non_monotone` false (reported neutrally: no
  monotonicity, superiority, winner or threshold claim is made; exact counts are
  descriptive).
- paired vs base: `l1_plus`, `l2_plus`, `both_plus` each
  `{verify_failed->verify_failed: 3}`, recovered 0 / lost 0 / same 3.
- Oracle control: provenance `ORACLE_TRUE_L1_CONTROL`, 3 records, excluded from
  every operational aggregate, `deployable` false, notice "never an operational
  protocol or deployable rate". Partition: operational 12, oracle_control 3,
  unassigned 0, total 15. Oracle isolation gate true.

## 10. Disclosure and verification accounting

- Operational key-dependent bits 428628; control key-dependent bits (isolated)
  97572; total 526200. Public control bits 4916145 (fixed 327743 per tag × 15).
- Transcript recount: `{key_dependent_bits 526200, public_control_bits
  4916145, tag_invocations 15, event_types {l1_disclosure 12, l2_disclosure 15,
  verification_tag 15}}`; recount mismatches `[]`.
- SC calls 27/27; tags 15/15; records 15/15; outcome counts exact 0 / undetected
  0 / verify_failed 15 / decode_failed 0 / nonfinite 0 / resource_abort 0;
  `provenance_violations` 0.
- Per-record walls sum 184.093475 s ≤ total `wall_s` 186.421779 s.
- Note N-B: `aggregate_summary.json`'s `integrity` mapping is alphabetized by
  the shared writer; the frozen gate order is preserved in `report.md` and in
  the runner's `INTEGRITY_GATE_ORDER`.

## 11. Resources

| item | value | budget |
|---|---|---|
| in-run wall_s | 186.421779 | ≤ 600 s |
| external timeout | not fired (wrapper ≈ 206.7 s) | 600 s |
| peak RSS | 615960576 B | ≤ 2147483648 B (2 GiB) |
| `ulimit -v` virtual | 2097152 KiB | 2097152 KiB |
| per-record VmPeak max (kB) | 1858464 | ≤ 2097152 |
| per-record VmSize max (kB) | 1660572 | — |
| per-record RSS HWM max (B) | 615960576 | — |
| resource stop | false (reason null) | — |
| `rejected_after_resource_stop` | false | — |
| threads/env | `OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2` | as frozen |

## 12. Integrity gates (20/20 true)

| gate | result |
|---|---|
| predecessor_construction_identity | true |
| hold_split_manifest_identity | true |
| p18_block_range_identity | true |
| target_population_contract | true |
| hold_population_exact | true |
| blocks_exact_with_declared_remainder | true |
| fifteen_records_exact | true |
| sc_calls_exact | true |
| tags_exact | true |
| orders_valid_k_prefixes_within_registered_arms | true |
| oracle_isolation | true |
| buckets_disjoint_exhaustive | true |
| undetected_zero | true |
| nonfinite_zero | true |
| truth_isolation | true |
| disclosure_recount_exact | true |
| one_open_per_protected_input | true |
| input_stat_unchanged | true |
| no_unregistered_access | true |
| resource_limits_met_and_no_abort | true |

`failing_integrity_gates` []; `integrity_all_pass` true.
Unused remainder: frames 1984..1999, 16 frames / 4096 symbols, `used: false`.

## 13. Label derivation

All 20 integrity gates true → `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`.
The label path consumes only the integrity gates dict;
`decision.recovery_threshold` is `null`; `zero_recovery_is_complete` and
`three_recovery_is_complete` are both true. There is no exact-count, FER,
winner, monotonicity, superiority or qualification threshold and no recovery
gate of any kind. The 15 `verify_failed` records (undetected 0) are descriptive
real-input observations, **not** a gate and not a pass/fail threshold;
`BLOCKED(<earliest gate>)` was not taken. `undetected` is never success.

## 14. Reviews

- Independent Pre-EXECUTE review: **PASS WITH COMMENTS**
  (`PRE_EXECUTE_REVIEW.md`); blocking issues none; N1–N4 non-blocking.
- Independent Pre-RESULT review: **PASS_WITH_COMMENTS**
  (`PRE_RESULT_REVIEW.md`); zero blocking issues; verdict downgraded from PASS
  solely because of the external-commit provenance anomaly (section 15), with
  all numbers independently recomputed from the worktree artifacts. Non-blocking
  findings N-A (transcription, corrected here), N-B, N-C (STATUS staleness,
  fixed here), N-D (≈3.1 s monotonic-vs-realtime skew), N-E (external docs-only
  activity: `docs/nbpolar/DOCUMENT_INDEX.md` +6 lines and untracked
  `docs/nbpolar/astra6_projectwide/`, unrelated to P19).

## 15. EXTERNAL COMMIT PROVENANCE ANOMALY (not a scientific failure; no rerun)

During/around the execution a **concurrent external commit landed that was not
made by this packet's operators**. Facts (from Pre-RESULT review item A,
independently verified there):

- HEAD advanced `ab173f2a` → `faac0411684819f5a9055cd71fc1b4bae6955287`
  (author/committer `Placebo303 <karel.yangkai303@gmail.com>`,
  2026-09-16 21:14:28 +0800, subject
  "docs: consolidate NB-Polar research state and Astra pack").
- That commit captured the five P19 artifacts at a **mid-run snapshot**:
  `RUNNING(record 11/15)`, 11 records, `sc_calls 22`, `tag_invocations 11`,
  `integrity_all_pass false`, `failing_integrity_gates
  ["sc_calls_exact","tags_exact"]`, `created_utc 13:13:21Z`. It landed ≈33 s
  **after** the run's final write (`created_utc 13:13:55Z`): an
  add-before-commit race, not a mid-write clobber.
- The WORKTREE holds the FINALIZED 15/15 files; four are ` M` versus the commit
  (`aggregate_summary.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl`, `report.md`), and `frozen_plan.json` is
  byte-identical to the committed blob.
- The commit is additive (451 entries; zero `.npz`/`.parquet` entries) and did
  not touch either protected input (stats unchanged). No history rewrite; no
  agent-authored commit; no push. No process other than the run left any trace
  on the five artifacts.

**Binding acceptance instructions (verbatim from Pre-RESULT review item A.4):**

> 1. Accept from the **worktree** files only. Read them from the filesystem; do
>    **not** use `git show HEAD:<path>` for any of the five files. The
>    authoritative worktree hashes are:
>    `aggregate 69b74baa…`, `identity 6e16dc5d…`, `jsonl 3313a2a2…`,
>    `report 81ecfe29…`, `frozen_plan 6d21510e…`; md5:
>    `80ce92cf800bd3e4e8fddcdd559fbfc2`, `70e98e8d79a760d90bbb6c9a2ef74e77`,
>    `e56474f157f18a8ed0837eb657f9f7d9`, `1747e2698a63e94742f3bafb289786bf`,
>    `185c8e12b94eb900ce9122370f1b5ea7`.
> 2. Do **not** run `git restore`/`git checkout --`/`git stash`/`git reset
>    --hard` on those four modified paths — it would overwrite the finalized
>    artifacts with the superseded 11/15 snapshot and destroy the evidence.
> 3. If a commit is eventually authorized, `git add` the four finalized files
>    after acceptance and cite the worktree hashes; do not push/describe
>    `faac0411`'s blobs as the P19 result.
> 4. At memory triage, record the race as a provenance incident (see findings).

This is reported as a **provenance anomaly, not a scientific failure**; the run
is not rerun.

## 16. Bounded scope

Descriptive real-input layer/backoff diagnostic of the frozen V25 1M HOLD split
at N=32768 only (three accepted P18 chronological blocks, frames 1600..1983), at
the fixed P16 construction and fixed floor-1e-15 TRAIN prior, in five frozen
arms. It is not real-frame FER, reconciliation efficiency, leakage, key rate,
scaling superiority, qualification or promotion evidence; the CE-normalized
disclosure ratio is a sample descriptive ratio and explicitly NOT qualification
efficiency; the true-L1 arm is an oracle-labelled diagnostic control, never an
operational protocol or deployable rate, and never enters any operational
aggregate; the unused remainder (frames 1984..1999) was never used; no pooling
with TRAIN/VAL/P16/P17.

## 17. Unrun stages and no-commit statement

- Unrun stages: none remaining in the packet except main-thread acceptance
  (owner: main thread). No box in `tasks.md` is checked by the operator.
- No code, artifact, old-root or protected-input change beyond the declared P19
  wave; neither protected input was reopened.
- This packet's operators made no git write. The single HEAD advance
  (`faac0411`) is an external commit and is described in section 15; no
  reconciliation (restore/checkout/add/stash) was attempted.

**This return is not an acceptance, not a qualification and not a FER result.
Main-thread acceptance remains separate and must apply the section 15 worktree
rule.**
