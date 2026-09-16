# Pre-RESULT review — NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM

**Verdict: PASS_WITH_COMMENTS**

Independent reviewer (did not write the code, freeze the plan, or run the gate).
Read-only review with two bounded exceptions: re-ran the focused + full test
suites (no production/artifact invocation — injected seams only) and wrote
**only** this file. The V25 NPZ content was **never opened** (stat metadata
only). The gate was **never rerun**. No artifact/real-data/old-root writes;
no commit/push.

Pinned interpreter for every command below:
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`.
Wilson `z = 1.6448536269514722` throughout.

## 1. Root: exactly five frozen files, no extras — PASS

Command:

```bash
ls -A .workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/
```

Raw output:

```
frozen_plan.json
report.md
screen_records.json
selection_and_confirmation_records.json
transcript_accounting.json
```

Exactly the five frozen names, no extras, no backup/duplicate/partial files.

Deep scalar-only audit (all four JSONs walked recursively): every per-block
arm record contains scalar values only (int/float/str/bool/None) — zero
non-scalar arm values over all 8000 arms. Block dict key sets are exact:
SCREEN `{stream_seed, block_index, empirical}`; CONFIRM
`{bec, block_index, cell, empirical, k1, k2, stream_seed}`. List lengths
seen anywhere: only structural `{0, 2, 3, 5, 7, 11, 35, 192, 640}` (arms,
seeds, K1 grid, integrity gates, configs, blocks). The only
case-insensitive hits for the forbidden vocabulary are false positives in
`frozen_plan.json` metadata: `labels` = outcome-label *names*
(`candidate`/`not_confirmed`/…) plus Toeplitz `arm_labels`/`phase_labels`
(strings, not per-block labels), and `source` = the string `"1M"` (source
identifier, not a source vector). No Bob/U/decoded/disclosed vectors, metric
arrays, per-block labels/tags, or seed-bit material are persisted.

## 2. Preconditions/orders/consumption/NPZ stat — PASS with note (C1)

- Recorded P7 sha: `frozen_plan.orders_sha256` =
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`.
  Independently recomputed canonical digest of the P7 `layers` payload
  (JSON read only, NPZ never touched):
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`
  — recorded == recomputed == frozen (`EXPECTED_ORDERS_SHA`,
  `TASK_PACKET.md:31`, `P8_FREEZE.md:53`). Both pooled orders are valid
  256-permutations (`sorted(order)==list(range(256))` True for L1 and L2).
- Entropy literals in `frozen_plan.entropy_expectations`:
  `h1=0.02428054681872374`, `h2=0.7767572780789994`,
  `total=0.8010378248977232`, `entropy_tol=1e-12`, `column_tol=1e-12`,
  `floor_entropy_change_tol=1e-09` — exact match to packet/freeze literals.
- NPZ stat (metadata only, no open):
  `size=25166822 == expected_npz_bytes=25166822`;
  `mtime=2026-08-19 01:34:09 +0800`, predating the gate run (artifacts dated
  2026-09-14) — the gate did not modify the NPZ.
- Consumption plan in `frozen_plan.artifact_read_accounting`:
  allowed 1 / before 0 / by-run 1 for both reads and attempts,
  `reopen_attempted=False`, `retries=0`, `retry_after_open=False` — as frozen.
- (C1) The *observed* raw-MLE H1/H2/total, floor-change value and runtime
  `open_count`/`stat_size_checked` live only in the run's in-memory summary
  (stdout JSON, not among the five files — the frozen schema in
  `P8_FREEZE.md` §8 never required them there). Number-by-number tolerance
  proof for the observations is therefore indirect: (a) the code raises
  `BLOCKED(target_population_contract)` with **no output root and zero SC
  calls** on any precondition failure, yet the root exists with 8000 fully
  invoked arms; (b) the report `target_population_contract=True`; (c) the
  exact planning-f triple (504.0, 205.0656831738056, 2.457749108478718)
  satisfies `504.0/205.0656831738056 == 2.457749108478718` exactly and
  implies observed `floor_total = 0.8010378248976782`, within `4.51e-14` of
  the literal — two orders of magnitude inside the `1e-9` floor guard and
  consistent with `target_population_contract` passing. Same for
  attempt/read accounting: plan values exact + single-call code path
  (`load_v25_channel_counts` once, `run_target_rate.py:1323`) + NPZ size
  match + no duplicate roots. Schema-compliant; flagged for main-thread
  awareness, not a blocker.

## 3. SCREEN: all 35 configs recomputed — PASS

Grid membership exact: persisted 35 `(K1,K2)` == full
`[8,10,12,16,24,32,45]×[80,94,110,125,140]` cross product. Every config:
192/192 blocks, `n_executed=192`, bucket sums exclusive
(`exact+verify_failed==192`, `undetected==decode_failed==resource_abort==0`
everywhere), all per-block `nonfinite=False` and
`truth_leak_violation=False`. Every persisted Wilson LB matches independent
recomputation to `<1e-12`; every `count_rule_188_of_192` and
`wilson_count_agree` flag verified; every eligibility re-derives True.
Boundaries: `187/192 -> 0.9474773285638652 (<0.95)`,
`188/192 -> 0.9544033287216636 (>=0.95)`.

Full 35-point table (recomputed == persisted on every column):

| k1 | k2 | exact/192 | wilson_lb (recomputed) | count_188 | eligible |
|---|---|---|---|---|---|
| 8 | 80 | 189 | 0.9615500026161811 | True | True |
| 8 | 94 | 190 | 0.9690137061775033 | True | True |
| 8 | 110 | 190 | 0.9690137061775033 | True | True |
| 8 | 125 | 190 | 0.9690137061775033 | True | True |
| 8 | 140 | 190 | 0.9690137061775033 | True | True |
| 10 | 80 | 191 | 0.9769953117481123 | True | True |
| 10 | 94 | 192 | 0.9861044354151461 | True | True |
| 10 | 110 | 192 | 0.9861044354151461 | True | True |
| 10 | 125 | 192 | 0.9861044354151461 | True | True |
| 10 | 140 | 192 | 0.9861044354151461 | True | True |
| 12 | 80 | 191 | 0.9769953117481123 | True | True |
| 12 | 94 | 192 | 0.9861044354151461 | True | True |
| 12 | 110 | 192 | 0.9861044354151461 | True | True |
| 12 | 125 | 192 | 0.9861044354151461 | True | True |
| 12 | 140 | 192 | 0.9861044354151461 | True | True |
| 16 | 80 | 191 | 0.9769953117481123 | True | True |
| 16 | 94 | 192 | 0.9861044354151461 | True | True |
| 16 | 110 | 192 | 0.9861044354151461 | True | True |
| 16 | 125 | 192 | 0.9861044354151461 | True | True |
| 16 | 140 | 192 | 0.9861044354151461 | True | True |
| 24 | 80 | 191 | 0.9769953117481123 | True | True |
| 24 | 94 | 192 | 0.9861044354151461 | True | True |
| 24 | 110 | 192 | 0.9861044354151461 | True | True |
| 24 | 125 | 192 | 0.9861044354151461 | True | True |
| 24 | 140 | 192 | 0.9861044354151461 | True | True |
| 32 | 80 | 191 | 0.9769953117481123 | True | True |
| 32 | 94 | 192 | 0.9861044354151461 | True | True |
| 32 | 110 | 192 | 0.9861044354151461 | True | True |
| 32 | 125 | 192 | 0.9861044354151461 | True | True |
| 32 | 140 | 192 | 0.9861044354151461 | True | True |
| 45 | 80 | 191 | 0.9769953117481123 | True | True |
| 45 | 94 | 192 | 0.9861044354151461 | True | True |
| 45 | 110 | 192 | 0.9861044354151461 | True | True |
| 45 | 125 | 192 | 0.9861044354151461 | True | True |
| 45 | 140 | 192 | 0.9861044354151461 | True | True |

Split: 1×(189,3vf) + 4×(190,2vf) + 6×(191,1vf) + 24×(192,0vf) = 35;
eligible 35/35 — exactly the persisted split.

Per-config stream coverage re-verified: each config's 192
`(stream_seed, block_index)` pairs == exactly
`{2026091680,2026091681,2026091682}×range(64)`.

## 4. Selection — PASS

Eligible set recomputed from records: all 35 points.
Lexicographic min of `(K1+K2, K1, K2)` recomputed = `(8, 80)` (sum 88;
the unique minimum-sum grid point, itself eligible, so the selection is
forced — no tiebreak path reachable). Persisted `selected = {k1: 8, k2: 80}`
matches. `eligible_points` list (35 entries) matches the recomputed set.
`confirm_executed=True` — the no-eligible path was correctly NOT taken.
No runtime/DEV outcome enters the records or the code path
(`select_point`: `min(eligible, key=(k1+k2,k1,k2))`).

## 5. CONFIRM — PASS

- Independence: CONFIRM block seeds == exactly
  `{2026091690..2026091694}`, disjoint from SCREEN `{2026091680..1682}`;
  Toeplitz masters `stream+10000` disjoint across phases
  (`2026101680..82` vs `2026101690..94`); phase/arm/block domain separation
  is code-level (`SEED_PREFIX`, `arm_seed_bits`). No SCREEN seed appears in
  any CONFIRM record.
- Only the selected point run in both arms with same-K pairing: all 640
  CONFIRM records carry `k1==8, k2==80` on block, empirical arm and BEC arm.
- Buckets recomputed from the 640 per-block records: empirical
  `exact=638, verify_failed=2, decode_failed=0, undetected=0,
  resource_abort=0`; BEC `exact=621, verify_failed=19, zeros elsewhere` —
  exact match to persisted marginals. Per-stream (records/emp/bec):
  1690: 128/127/124; 1691: 128/128/122; 1692: 128/128/123;
  1693: 128/128/127; 1694: 128/127/125 — sums 638/621 match pooled.
- Paired cells recomputed per block from arm exact flags:
  `both_exact=621, empirical_only=17, bec_only=0, neither=2` (621+17=638,
  621+0=621, total 640) — match persisted cells.
- Wilson LB from 638/640 recomputed = `0.9906013676984646`, exact match
  (bit-for-bit) to persisted. Count rule `638>=618` True. Boundaries:
  `617/640 -> 0.9498753087068414 (<0.95)`,
  `618/640 -> 0.9516826902311426 (>=0.95)`. Both scientific gates pass.
- CONFIRM zeros: nonfinite 0, truth-leak 0, undetected 0, resource_abort 0
  over all 1280 arms (recomputed from records).

## 6. Accounting — PASS

- Per-point formula: `5*(8+80)+64 = 504` for the selected point; every one
  of the 8000 per-block arm records carries exactly its config's
  `5*(K1+K2)+64` key bits and `2623` public bits with `tag_invoked=True`
  (all 8000 arms fully invoked — verified by exact sum match, not sampled).
- SCREEN key sum from blocks = `4824960` == closed-form
  `192*Σ_configs(5*(K1+K2)+64)` == transcript SCREEN phase value.
  SCREEN public `6720*2623 = 17626560` ✓; SCREEN tags 6720 ✓.
- CONFIRM from blocks: key `645120` (=1280×504), public `3357440`
  (=1280×2623), tags 1280 — all == transcript CONFIRM phase values.
- Totals: key `5470080`, public `20984000`, tags `8000`, events `24000`
  (=8000×3: L1/L2/tag) — incremental == literal recount in total, per phase
  and per arm with `mismatch_count=0`, `mismatches=[]`. By-arm split:
  empirical key `5147520` (=4824960+322560), BEC key `322560` (=640×504);
  empirical public `19305280`, BEC public `1678720`; tags 7360/640 — all
  recomputed from block records exactly.
- Planning f: `504.0/205.0656831738056 = 2.457749108478718` exact;
  report flags it planning-only (see §8). Partial-failure rule respected
  vacuously: zero decode failures before tag anywhere (all arms invoked
  L2+tag), and the code's partial semantics (`5*K1` on L1-fail, L2/tag only
  when invoked) is covered by focused tests.

## 7. Truth boundary (code audit) — PASS

`run_rate_arm` (target_rate.py:732-881): operational metrics use only
`bob_arr` (`build_p1_metrics(bob)`, `gather_p2_metrics(bob, high_hat)`
with the *hard L1 candidate* — the true high layer never enters the L2
metric); truth copies feed only the frozen-disclosure values
(`u1/u2_disclosed`, counted in `key_dependent_bits`), tag construction and
`label_match` scoring. The per-arm sentinel mutates the truth copies after
metrics/decisions exist and proves the protected set bitwise unchanged.
All 8000 persisted arms have `truth_leak_violation=False`. Provenance
`PRIOR_ONLY`/`CANDIDATE_CONDITIONED` on every arm. No scope creep in the
module beyond the frozen orchestration.

## 8. Bounded wording (report.md read fully, 109 lines / 6007 chars) — PASS

- Scope sentence present verbatim: frozen V25 TRAIN target-population
  static rate development signal at N=256 only; explicitly not held-out or
  real frame FER, efficiency, key rate, scaling, qualification or promotion;
  planning-only f is not real-channel efficiency; undetected never success.
- Every sensitive-term hit (`efficiency`, `key rate`, `FER`, `held-out`,
  `real frame`, `scaling`, `qualification`, `promotion`) is inside that
  disclaimer or the planning-only flag — no positive claim of any of them.
- BEC numbers (621/640, cells, gap 17) are reported without any
  winner/threshold/beats claim; the label rests solely on the frozen
  empirical gates. No `winner`/`beat`/`throughput` language anywhere.
- Label `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` is the frozen candidate
  label for integrity-pass + scientific-pass at the frozen shape.
- Report tables verified byte-exact against the JSON records: all 35 SCREEN
  rows (k1/k2/exact/Wilson-repr/count-flag/eligible) and all 5 CONFIRM
  per-stream rows regenerate character-for-character; integrity 11/11 True
  and scientific 2/2 True as rendered.
- Resource rendering: `wall 522.26697 s` (≤3600), `RSS 274264064 B`
  (≤2147483648), `resource stop fired: False`.

## 9. Tests/scope — PASS with notes (C2, C3)

- Focused: `12 passed` (15.44 s);
  full `test_nbpolar_*.py`: `240 passed` (141.54 s) — both with the pinned
  interpreter, `-q -p no:cacheprovider`, fresh `/tmp/p8_preresult_*`
  basetemps. Expectation 12 + 240 met.
- P8 file set: `?? target_rate.py`, `?? test_nbpolar_target_rate.py`,
  `?? specs/nbpolar-phase4-p8/`, `?? P8 queue dir` (incl. the five-file
  output root), `M tasks.md` with a single hunk (`@@ -51,3 +51,300 @@`,
  297 insertions, append-only P8 section). Frozen-command in frozen_plan is
  the 12-flag packet/freeze command verbatim.
- Accepted modules: `sc.py`, `prior.py`, `construction.py`,
  `v35_algorithm_development.py` clean; `results/` and
  `comparison_bench/outputs_comparison/` clean. `protocol.py`,
  `target_construction.py`, `two_layer.py` are untracked *predecessor-phase*
  files (P4/P7 deliverables) reused unchanged by P8 — P8's only new module
  is `target_rate.py`, which does not import the modified
  `empirical_channel.py` (that 4-line comment-only diff is P3 scope).
- HEAD unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e`. No commit.
  Gate not rerun (single five-file root, no duplicates/partials).
- (C2) The worktree carries unrelated dirt from other phases/probes
  (P3–P6/X-queues, AGENTS.md, decision-log, etc.). Per AGENTS.md §10.1(11)
  review-by-scope: unrelated changes preserved, none attributed to P8;
  P8 scope itself is clean.
- (C3) `STATUS.yaml` still shows the pre-execution state
  (`IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`, reads/attempts 0/0,
  both reviews pending). Post-gate STATUS bookkeeping is main-thread owned;
  it does not affect the artifact evidence either way.

## Gate table (recomputed vs persisted)

| gate | recomputed | report.md |
|---|---|---|
| orders_identity_and_permutations | True (sha recomputed == recorded == frozen; both pooled orders 256-perms) | True |
| target_population_contract | True (indirect: root exists + 8000 SC arms executed + f-implied floor_total within 4.51e-14 of literal; see C1) | True |
| coverage_complete_and_disjoint | True (35× exact 3×64 grid + 640 confirm + disjoint seeds) | True |
| pairing_and_buckets | True (all bucket sums + 8000/8000 per-record outcome consistency, 0 inconsistent) | True |
| truth_leak_zero | True (0 violations / 8000 arms + code audit) | True |
| undetected_zero | True (0 on decision path: all-eligible SCREEN + CONFIRM) | True |
| nonfinite_zero | True (0 flags on decision path) | True |
| resource_abort_zero | True (0 aborts + no resource stop + wall/RSS inside budget) | True |
| disclosure_and_recount_exact | True (formula-exact sums + 2623/tag + incremental==recount, mismatch 0) | True |
| attempt_read_accounting_exact | True (plan values exact + single-call path + NPZ size match; observations per C1) | True |
| resource_limits_met | True (522.26697≤3600 s; 274264064≤2147483648 B) | True |
| confirm_empirical_exact_≥618/640 | True (638) | True |
| confirm_empirical_wilson_≥0.95 | True (0.9906013676984646) | True |

Label `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` follows from the frozen rule.

## Closure statements

- The V25 NPZ content was **not reopened** by this review (read 1/1 remains
  consumed by the gate; only `stat` size/mtime metadata read here).
- The gate was **not rerun**; reads/attempts accounting is the gate's own
  (plan 1/1 consumed at its first content open; no second open exists).
- Tests were re-run in isolation only (12 + 240 passed); they use injected
  seams and never touch the NPZ or production paths.
- This review wrote **only** this `PRE_RESULT_REVIEW.md` file; no other
  artifact, source, or queue file was created, modified, committed or pushed.
