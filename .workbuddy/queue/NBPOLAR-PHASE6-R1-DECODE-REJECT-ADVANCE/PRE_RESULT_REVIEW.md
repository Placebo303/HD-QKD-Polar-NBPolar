# PRE_RESULT_REVIEW — NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE

- Reviewer: fresh independent reviewer-go (backup instance). Did not write the code,
  freeze the plan, or run the gate.
- Date: 2026-09-13 (WSL). Read-only review; this file is the only write.
- HEAD at review: `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged).
- Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).
- Artifacts reviewed: `.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`
  (5 files, mtimes 2026-09-13 11:09:35, single generation).
- Reviewer scripts (repo-external): `/tmp/opencode/p6r1_prereview/verify_{schema,secret_scan,recompute,mechanism,spy}.py`.

## Verdict: PASS

All required recomputations are exact. The persisted candidate label
`DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE` is warranted: all 18 frozen gates were
independently recomputed true against the actual artifacts, with no vacuous gate.
No blocking issues. Non-blocking comments at the end.

## Independence statement

- The frozen three-arm command was **NOT rerun**. The reviewer only read the five
  artifacts, ran read-only recomputation scripts, an injected non-frozen-seed mechanism
  audit (seed 2026091373), a 3-block pairing spy (seed 2026091374, `/tmp` root), and the
  test suites. No `sc_decode` call used run seed 2026091350 or master 2026091351.
- Attempt 1/1 is **consumed** by the operator run that produced the artifacts
  (plan `created_utc 2026-09-13T03:09:35Z` = 11:09:35 local; frozen root was absent at the
  Pre-EXECUTE PASS and exists now). This review neither consumes nor restores an attempt.
- Phase 5/6 evidence roots, Model-F, real data, `results/`, `comparison_bench/outputs_comparison/`
  and sibling checkouts were not opened/written (directory `stat` only on the two evidence
  roots). No commit/push.

---

## 1. Output root and deep scalar-only audit — PASS

`ls` of the root returns exactly the 5 frozen files and nothing else:

```
aggregate_comparison.json 11041 B | frozen_plan.json 8343 B | per_block_three_arm_outcomes.json 806286 B
report.md 2707 B | transcript_accounting.json 2649 B
mtimes 11:09:35.615–11:09:35.640 (25 ms span, one write generation)
```

Recursive audit: leaf types `{int: 16466, str: 1877, list: 923, float: 2426, bool: 3024, None: 876}`;
all 300 per-block records carry exactly the declared top-level and 25-field arm key sets
(three arms); list-valued keys are only the declared ones (`schedule.D_sets`, `new_coordinates`,
`refused_run_seeds`, rescue index lists, `rejected_levels`, plus the two 5-int schedule lists);
no 256/2560/2623-length list exists; no forbidden key token (`u_hat`, `x_hat`, secret, decoded,
raw seed bits, symbol/label vectors) exists; the only long hex strings are the 6 declared
transcript sha256 values. No symbol vectors, labels, disclosed values, decoded keys or raw
seed bits are persisted.

## 2. Three-arm pairing and per-block consistency — PASS

- Code path (reviewed): exactly one generator draw per block
  (`incremental.py:2290`), fed to `run_three_arm_block` which snapshots `(x, logp)` and runs
  `static` (1347) → `strict-stop` (1351) → `R1` (1355), re-checking both arrays after each arm
  (1350/1354/1358); `paired_match` recorded at 2307. No arm mutates the shared metric.
- Bounded spy (seed 2026091374, 3 blocks, `/tmp` root): 3 generation calls; per block
  `id(x)`/`id(logp)` identical across the three arms; order confirmed; metric bytes unchanged
  after every arm; non-frozen run emits `candidate=None` with `frozen_plan_identity=false`
  (label correctly suppressed).
- Persisted records: 300 records, `block_index` 0..299, `paired_match` true 300/300; arm names
  `static`/`incremental`/`incremental_r1`; per-record wall fields equal their top-level copies.
- Independent per-block checker (freeze formulas, not the module's checker): **0 failures over
  900 arm records**. It verifies for every record: outcome bucket; exact flag; rejection
  ordering/non-final levels; `public_seed_bits = 2623*tag_invocations`;
  `feedback_control_bits = 1*feedback`; `public_control_bits = sum`;
  `key_dependent_bits = 5*K_term + 64*tags` (`K=45` for the static arm; terminating K for
  exact/undetected/decode_failed; distinct decode_failed formula); terminating level/K;
  invariants `levels_invoked = tags + rejections (+1 for a terminal decode_failed level)` and
  `feedback = levels_invoked - 1`.
- Non-rejecting blocks: 280; strict vs R1 field-for-field identity over 22 fields → 0 mismatches
  (shared `incremental` seed namespace confirmed indirectly).

## 3. Outcome totals, disjoint/exhaustive, undetected — PASS

Recomputed from `per_block_three_arm_outcomes.json`; all three arms sum to 300 and match
`aggregate_comparison.json` exactly:

| bucket | static | strict-stop | r1 |
|---|---|---|---|
| exact | 298 | 280 | 298 |
| undetected | 0 | 0 | 0 |
| verify_failed | 0 | 0 | 0 |
| decode_failed | 2 | 20 | 2 |
| resource_abort | 0 | 0 | 0 |

No impossible/other/nonfinite/undetected folding into exact: the only r1 exact values are
`outcome=="exact"` with a tag match; r1 undetected 0; error types are
`ImpossibleDisclosedValueError` only (static 2, strict 20, r1 2); `error_type` is null on all
success records. R1 histograms recomputed and equal to the persisted blocks:
accepted `{0:263,1:16,2:15,3:3,4:1}`, decode_failed `{4:2}`, terminating
`{-1:0,0:263,1:16,2:15,3:3,4:3}`, rejected `{0:20,1:7,2:3,3:2}`; 32 rejections / 20 blocks.

## 4. R1 exact, Wilson, gates, candidate label — PASS

- R1 exact = 298 (≥ 285) and static exact = 298; strict = 280.
- Wilson one-sided 95%, `z=1.6448536269514722`, n=300, Decimal 60-digit independent formula:

```
(298,300) = 0.980056573880127439848863189709044622961252070017721231742324
persisted   = 0.9800565738801275            (float rounding of the same value)
(280,300) = 0.905561824450154251541519439577337352211592185477874410632226 == persisted 0.9055618244501542
(285,300) = 0.924984488202856156430724777627323929546877457988536086721775 (threshold illustration)
```

- `r1_exact_ge_285` → true (298 ≥ 285); `r1_wilson_lower_ge_0_90` → true
  (0.9800… ≥ 0.90). All 18 gates recomputed independently from artifacts and each equals the
  persisted boolean true. The candidate is a single `all(gates.values())` conjunction
  (`incremental.py:2515-2517`); with all gates true no earliest-failing-gate ordering applies,
  and no gate is vacuous (each compared against the independent recomputation, including the
  schedule/accounting proof over all 900 records, the literal recount universe, and the
  strict-arm pinning). The label is therefore warranted; any false gate would have nulled the
  candidate by the same code path.

## 5. Disclosure accounting — PASS

Per-record recomputation of `key_dependent_bits = 5*K_j + 64*j` (j = tag invocations;
cumulative K from the terminating level; decode_failed uses its failing level; rejections add
no tag bits) and public control = `2623*tag_invocations + 1*feedback` matched **all 900 records**.
Totals and averages (recomputed == persisted):

| arm | key total | avg/block | tags | feedback | seed bits | control bits |
|---|---|---|---|---|---|---|
| static | 86572 | 288.573333333 | 298 | 0 | 781654 | 781654 |
| strict-stop | 64276 | 214.253333333 | 314 | 34 | 823622 | 823656 |
| r1 | 66152 | 220.506666667 | 333 | 67 | 873459 | 873526 |

Integer 5% rule: `66152*100 = 6615200 <= 95*86572 = 8224340` → true; saving fraction
0.235873031 (persisted equal). Public control total 2,478,836 bits. Union bound recomputed
`min(1, tags*2^-64)`: static 1.6154612370034016e-17, strict 1.702197410802242e-17,
r1 1.805196617188365e-17, total 5.1228552649940085e-17 over 945 = 298+314+333 tag
invocations (recount total equal).

## 6. Continuation-taxonomy audit — VALID SCIENCE, no defect

Artifacts: all 32 rejections are at non-final levels 0..3 (histogram above); no final-level
rejection is recorded; the 2 R1 `decode_failed` blocks (b85, b152) carry
`rejected_levels=[0,1,2,3]`, `levels_invoked=5`, `tags=0`, `feedback=4`, `key=225` — i.e. the
impossibility persisted through K45 and the final error stayed terminal; only
`ImpossibleDisclosedValueError` occurs, so no non-whitelisted exception was silently
continued. `outcome=="decode_rejected_continue"` is never assigned anywhere in the source
(code and data scan).

Bounded injected mechanism audit (non-frozen seed 2026091373; scripted `sc_decode` raising
IDE/other exceptions at chosen levels; real Toeplitz tag with a mutated candidate at
tag-mismatch levels; 13 scenarios, all PASS):

```
reject@0→accept@1      exact L2 T1 F1 key229  tags={1}          reject@1→accept@2  exact L3 T2 F2 key313 tags={0,2}
reject@2→accept@3      exact L4 T3 F3 key397  tags={0,1,3}      reject@3→accept@4  exact L5 T4 F4 key481 tags={0,1,2,4}
reject@{0,2}→accept@3  exact L4 T2 F3 key333  tags={1,3}        persist 0..3 + K45 IDE  df@4 rej(0,1,2,3) L5 T0 F4 key225
mismatch 0..3 + K45 IDE  df@4 rej() L5 T4 F4 key481             exc ValueError/TypeError/RuntimeError@1  df@1 L2 T1 F1 key229
NumericNonfiniteError@1 / NaN marginals@1  df@1, nonfinite=True  strict-mode reject@0  df@0 L1 T0 F0 key145
```

Instrumented facts in every scenario: each `sc_decode` call received the **same original
`logp` object**, byte-identical to the pre-run copy, with the cumulative `D_i` positions and
their actual U values; **no tag seed ever matched a rejected level** (tag levels were exactly
the accepted/tagged levels); `F == levels_invoked - 1` (one feedback per advance); the
rejection never became an outcome bucket. Conclusion: the continuation mechanism matches the
frozen delta (R1_FREEZE §3) — one rejected level = one rejection record, no candidate, no tag,
one feedback, next increment disclosed, fresh SC on the original metric; K45 IDE terminal;
everything else fail-closed. No scientific defect.

## 7. Rescue identities — PASS (reported, not gated)

Recomputed from the per-block arms: **rescued 18, persisted 282, regressed 0, other 0**
(sum 300; index lists equal and sorted; `partition_exhaustive` true). Rescued indices:
`18, 35, 73, 81, 122, 123, 128, 129, 149, 170, 173, 186, 218, 219, 223, 230, 279, 283`.
No threshold uses these counts (the gate bundle never references `rescue`; `rescue_comparison`
is computed after the gates at `incremental.py:2356` and only persisted/reported, matching
R1_FREEZE §9 "They do not change any threshold"). `regressed=0` is consistent with the
strict-relaxation argument: the 280 non-rejecting blocks are field-identical between strict
and R1 (same seed namespace), so R1 can only convert strict failures into acceptances.

## 8. Transcript / recount — PASS

Rebuilt each arm's totals from the persisted per-block scalars:
key-dependent bits 86572/64276/66152, public control 781654/823656/873526, tag invocations
298/314/333, feedback 0/34/67 — all equal to both the `incremental` totals and the literal
`recount` blocks in `transcript_accounting.json` (recount fields are the 4-field subset; all
four match per arm). Rebuilt event counts from scalars + frozen event grammar: static 598,
strict 682, r1 767 — equal to both persisted event counts. Mismatch counts 0/0/0. The three
sha256 values are 64-hex, distinct, and identical across `transcript_accounting.json` and
`aggregate_comparison.json`.

## 9. Bounded wording — PASS

`report.md` read in full (62 lines). The only occurrence of FER/efficiency/key-rate/
qualification/promotion/leakage is the explicit negation in the claim-scope line:
"**Scope:** synthetic paired development signal only; this is not real-data FER, leakage
efficiency, key rate, qualification or promotion evidence." No other quantitative claim
beyond the reported synthetic counts; no reference to the Phase 5/6 frozen roots (the only
`2026091340` occurrence in any artifact is inside `frozen_plan.refused_run_seeds`, which is
required for refusal); the strict-stop arm appears only as the second in-run arm of this
gate, never as a comparison to a frozen root. The candidate label is stated with its bounded
scope. Minor wording suggestion in Findings #3.

## 10. Implementation state — PASS

Pinned interpreter, fresh `/tmp` basetemps, `-q -p no:cacheprovider`:

```
test_nbpolar_incremental_r1.py          -> 17 passed, 1 warning in 13.76 s
all 11 test_nbpolar_*.py files          -> 170 passed, 1 warning in 85.94 s
```

Composition from source: 12+16+17+11+13+9+10+32 (earlier) +16 (P5) +17 (P6) +17 (R1) = 170;
the R1 file contains exactly 17 `test_`. Frozen seeds appear in tests only as constant
assertions/validator calls/comment text; `default_rng(2026091350|2026091351)` is asserted
absent by the tests themselves and by review grep. The run's own gates plus this review's
independent checker cover the accounting/schema checks.

## 11. Scope / provenance — PASS

- `git status --porcelain` = 35 entries, identical to the Pre-EXECUTE snapshot; only the
  declared R1 paths and the new output root are involved. `git status` on
  `src/ experiments/ tools/ results/ comparison_bench/outputs_comparison/` is empty (no
  tracked modification), and no file in `results/`/`outputs_comparison/` or the sibling
  checkouts was written.
- Files modified after 11:08: only `PRE_EXECUTE_REVIEW.md` (the prior reviewer) and the five
  run outputs. Implementation files predate the run (10:41–10:50). Phase 5/P6 evidence roots
  retain mtimes 02:31:13 / 03:33:34 (before this session; metadata `stat` only).
- HEAD `ab173f2a` unchanged; no commit/push. Output root mtimes are a single generation
  (11:09:35, 25 ms span); plan `created_utc 2026-09-13T03:09:35Z` matches.
- Budgets: max per-block `metric+three-arm` wall 0.195855 s (soft cap 15.0, ×77 margin),
  total wall 16.595318 s (cap 900 s), peak RSS 114622464 B (2 GiB envelope),
  `resource_stop_fired=false`.
- Seed/attempt state: run seed 2026091350 persisted in plan/aggregate; master 2026091351
  persisted as the public identifier only (no raw bits); attempt 1/1 consumed by the run.

## Findings

Blocking issues: **none**.

Non-blocking comments (no rework of the scientific result required):

1. **Static-arm `terminating_k` metadata (all 300 static records).** The static records show
   `terminating_k = 29` (the shared incremental schedule's `K[terminating_level]`), not the
   static comparator's `K=45` — because `_r1_arm_record(static, nested)` is called with the
   incremental `nested` (`incremental.py:2313`). The static `key_dependent_bits` (225/289) and
   every gate use `K=45` correctly, so no number in the result chain is affected. Fix or
   annotate when the file is next touched (for the static arm, `terminating_k` should be 45 or
   the field should be documented as nested-schedule-indexed).
2. **STATUS.yaml is stale.** It still reads `attempts_used: 0` and
   `next_gate: ...THEN_INDEPENDENT_PRE_EXECUTE_REVIEW` although attempt 1/1 was consumed at
   11:09. Update it in the post-run return/solidification (lifecycle bookkeeping only).
3. **report.md wording.** It does not literally say the strict-stop arm is an in-run
   recomputation; the in-run semantics are unambiguous from `frozen_plan.arms`/`mode` and the
   absence of any P6-root reference. Optional: state "all three arms were computed in this
   run" in the final human-readable summary.
4. **Inherited (Pre-EXECUTE finding 4, still true).** `_abort_three_arm` records
   `paired_match: true` for unexecuted `resource_abort` records; moot here (0 aborts) and the
   coverage gate would catch an all-abort run. No action for this packet.
5. Memory triage should record this Pre-RESULT PASS and the emitted candidate label in
   `docs/decision-log.md` (the option (a) ruling is already recorded); no new failure mode
   was found, so `docs/troubleshooting.md` needs no entry.

## Checklist

- [x] Matches OpenSpec spec / frozen contract (`R1_FREEZE.md`, `TASK_PACKET.md`, authorization)
- [x] Tests pass (17 R1 + 170 full NB-Polar, pinned interpreter)
- [x] No scope creep (declared R1 paths only; frozen dirs and evidence roots untouched)
- [x] docs/decision-log.md or docs/troubleshooting.md needs update? — decision-log via memory
      triage only; no troubleshooting entry required

— fresh independent reviewer-go (backup instance), 2026-09-13
