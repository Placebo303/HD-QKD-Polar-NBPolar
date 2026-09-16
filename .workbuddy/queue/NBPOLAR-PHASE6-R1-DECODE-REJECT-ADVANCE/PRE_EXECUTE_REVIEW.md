# PRE_EXECUTE_REVIEW — NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE

- Reviewer: independent reviewer-go instance (did not write the reviewed code).
- Date: 2026-09-13 (WSL). Read-only review; this file is the only write.
- HEAD at review: `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged during review).
- Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).
- Contract reviewed: `TASK_PACKET.md`, `STATUS.yaml`, `R1_FREEZE.md`,
  `R1_IMPLEMENTATION_NOTES.md`, `OPERATOR_RETURN.md`, `AUTHORIZATION_PROMPT.md`,
  Phase 6 `MAIN_THREAD_DISPOSITION.md` (option (a)),
  `openspec/changes/formal-ir-nbpolar-phase6-r1-decode-reject-advance/`,
  and the implementation/tests named in the freeze.
- Immutable Phase 5/6 evidence roots: directory `stat` only (mtime read); no
  file content read or written. No Model-F/real-data access. No commit/push.

## Verdict: PASS

All ten required checks pass. No blocking issues. The frozen command is
authorized to run once, unchanged, subject to the main thread's final GO.

---

## Required checks (PASS/FAIL with raw evidence)

### 1. STATUS edit exactness — PASS

Command: `awk -F': ' '/_authorized|scientific_promotion|^state:|attempts_|next_gate:/ ...' STATUS.yaml`; full file read.

```
state: AUTHORIZED_FOR_AUTONOMOUS_PHASE6_R1_DECODE_REJECT_ADVANCE
documentation_authorized: true
implementation_authorized: true
synthetic_exploration_authorized: true
decoder_execution_authorized: true
development_gate_authorized: true
artifact_read_authorized: false
raw_data_authorized: false
real_data_authorized: false
dev_eval_authorized: false
rate_adaptation_authorized: true
scl_authorized: false
phase6_r1_authorized: true
phase7_authorized: false
scientific_promotion: false
attempts_allowed: 1
attempts_used: 0
next_gate: IMPLEMENTATION_AND_SYNTHETIC_QUALIFICATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW
```

Exactly the seven authorized flags are `true` (documentation, implementation,
synthetic_exploration, decoder_execution, development_gate, rate_adaptation,
phase6_r1); all other seven flags are `false`; predecessor
`FIXED_INCREMENTAL_NEGATIVE_ACCEPTED`; `attempts_allowed: 1` /
`attempts_used: 0`; state and next_gate as declared. Matches
`AUTHORIZATION_PROMPT.md` line-by-line.

### 2. R1 delta semantics (code review + independent injected tests) — PASS

Implementation read end-to-end. Key sites:
- `run_incremental_block` (Phase 6 public, default path) delegates to
  `_run_incremental_block_impl(..., advance_on_reject=False, arm="incremental")`
  (`incremental.py:413-442`); `run_incremental_r1_block` delegates with
  `advance_on_reject=True, arm=R1_RESULT_ARM` (`incremental.py:445-477`).
- Non-final continuation branch `incremental.py:543-555`: only
  `ImpossibleDisclosedValueError`, only when `advance_on_reject and
  level + 1 < levels`; records the level, increments
  `feedback_control_invocations` by exactly one, `continue`s before any
  candidate/tag work. Final level or strict mode falls through to terminal
  `decode_failed`.
- Catch-all `except Exception` (`incremental.py:556-565`) stays fail-closed
  terminal at every level; `NumericNonfiniteError` explicitly raised for
  NaN/+inf marginals (`incremental.py:539-542`).
- Fresh restart: each loop iteration calls the module-global `sc_decode` with
  the same original `logp_arr` and the cumulative `nested.sets[level]`
  (`incremental.py:527-538`); no state, belief, partial sum or hard decision is
  carried.
- `outcome` is never assigned `decode_rejected_continue` (grep: no match);
  `_outcome_counts` buckets only `OUTCOMES`; the rejection count is carried as
  `rejected_levels` / `decode_rejected_continue_count`
  (`incremental.py:365-368, 647-648`).

Reviewer-owned injected matrix (scripts under `/tmp/opencode/p6r1_review/`,
run with the frozen interpreter; no repo writes):

- Single rejection at each level with acceptance at the next level
  (transitions 0->1, 1->2, 2->3, 3->4):

```
reject@0: outcome=exact accepted=1 rejected=(0,) levels=2 tags=1 fb=1 key=229
reject@1: outcome=exact accepted=2 rejected=(1,) levels=3 tags=2 fb=2 key=313
reject@2: outcome=exact accepted=3 rejected=(2,) levels=4 tags=3 fb=3 key=397
reject@3: outcome=exact accepted=4 rejected=(3,) levels=5 tags=4 fb=4 key=481
no-tag-at-rejected=True metric-unmutated=True (each: all sc_decode calls received
  the unmodified original metric; rejected level's seed never passed to a tag)
```

- Persistent through K45:

```
persistent: outcome=decode_failed fail_level=4 rejected=(0,1,2,3) levels=5
tags=0 fb=4 key=225 decode-calls=5 tag-calls=0 err=ImpossibleDisclosedValueError
```

- Non-whitelisted exception matrix (4 classes x 5 levels) and NaN-marginal
  matrix (5 levels): every cell terminal `decode_failed` at the injected level
  with `rejected_levels=()`, `levels_invoked = level+1`,
  `key = 5*K_level + 64*level`, and the R1 checker consistent:

```
exception matrix (4 classes x 5 levels): PASS   [NumericNonfiniteError,
  ValueError, TypeError, RuntimeError]
nonfinite-marginal matrix (5 levels): PASS
```

- Reject-then-final-mismatch edge (rejection at 0, all later tags mismatch):

```
outcome=verify_failed rejected=(0,) levels=5 tags=4 fb=4 key=481 consistent=True
control reasons: decode_rejected_advance_next_level + tag_mismatch_advance_next_level
```

Conclusion: at K=29/33/37/41 a non-final `ImpossibleDisclosedValueError`
records `decode_rejected_continue` with no candidate and no tag, exactly one
public feedback, then discloses the next increment and restarts SC on the
original metric with the cumulative known set; at K=45 it is terminal
`decode_failed`; every non-whitelisted exception/nonfinite marginal is
fail-closed terminal at every level; intermediate rejection is never a bucket
or success.

### 3. Strict-stop pinning and validator interpretation — PASS

- `run_incremental_block` signature pinned by
  `test_nbpolar_incremental.py::test_a11` (`block_index, x, logp, field, n,
  sizes, nested, tag_fn`) and the default path is the shared impl with
  `advance_on_reject=False`; `incremental_record_consistent(..., default)`
  refuses any record carrying a rejection (`incremental.py:824-826`).
- Phase 6 default mode (`run_paired_dev_gate`, `_candidate_gates`,
  `DEV_GATE_*` budgets, `FROZEN_RUN_SEED=2026091340`,
  `TOEPLITZ_MASTER_SEED=2026091341`, `BANNED_RUN_SEEDS` 22 values,
  `validate_run_seed`) is present and unchanged in behavior; Phase 6 tests
  pass unchanged (17/17 inside the full run).
- Reviewer bounded cross-check of strict records on injected blocks against the
  frozen Phase 6 formulas: impossible-disclosure terminal at every level 0..4
  (`key = 5*K_i + 64*i`, `tags = i`, `fb = i`) and tag-mismatch acceptance at
  every level 0..4 (`key = 5*K_m + 64*(m+1)`, `tags = m+1`, `fb = m`); all
  records pass the strict Phase 6 proof.
- Scoped interpretation (separate `validate_r1_run_seed` /
  `R1_BANNED_RUN_SEEDS`, `incremental.py:157-160, 211-222`): **adjudicated
  PASS**. The packet asks to "extend the banned-run-seed validator to refuse at
  least 2026091200..1213, 1314..1321, 1330, 1340, 1341" while its own
  acceptance requires the existing Phase 6 tests to pass; those tests pin
  `BANNED_RUN_SEEDS` exactly and `validate_run_seed(2026091340)==2026091340`
  (`test_nbpolar_incremental.py:884-887`). The R1 path refuses a strict
  superset (25 values: the 22 P6 values + 2026091321 + 2026091340 + 2026091341)
  and is the only validator used by the three-arm gate; the literal Phase 6
  validator remains byte-pinned for the Phase 6 mode only. The functional
  requirement is met without breaking the predecessor pin.
- Raw evidence:

```
BANNED size 22; validate_run_seed(2026091340) = 2026091340; refuses 2026091330
R1 banned size 25; R1 == packet-required set; refuses 2026091321/1340/1341
R1 budgets: total 900.0 | per-block 15.0 | RSS_LIMIT 2147483648
P6 constants: 2026091340 / 2026091341 / 300 / 285 / 0.9 / 600.0 / 10.0
```

### 4. Seeds — PASS

- `git grep -n "2026091350" HEAD` and `"2026091351" HEAD`: no output, exit 1
  (both absent from HEAD; raw output captured).
- Worktree grep (excluding `.git` and the two immutable evidence roots) finds
  the two seeds only in the new R1 artifacts: `incremental.py` constants
  (L151-156), the R1 test file (constant assertions/guards only: L5, L55,
  L874-875, L888, L1144-1145), the R1 queue docs, and the R1 OpenSpec design
  note. No accepted/consumed Phase 1-6 stream contains them.
- Derivation recomputed independently with a hand-written SHA-256 counter
  stream for `(arm, block, level)` = (static,0,0), (incremental,0,0),
  (incremental,0,1), (incremental,1,0), (incremental,299,4), (static,299,0),
  (incremental,7,3): all bit-identical to
  `block_toeplitz_seed_bits(..., master=2026091351)`, length 2623, dtype
  uint8, values in {0,1}; all pairwise distinct; default master reproduces the
  Phase 6 master string for the Phase 6 namespace.
- Arm namespaces are as frozen: `static` per arm; both incremental arms use
  `incremental` (`incremental.py:164, 581`); reviewer check of a non-rejecting
  block shows strict and R1 pass the identical seed sequence and get identical
  outcomes/keys (`non-rejecting strict/R1 seeds identical: True`).
- Raw seed bits are never persisted: the five output JSON files are scalar-only
  and contain no bit-array/hex fields; only derived scalar counts and the
  public master seed identifier (documented public control) appear.
- R1 tests use fresh seeds 2026091360..1363 (operator) and this reviewer used
  2026091365..1372; the frozen seeds are never RNG inputs
  (`default_rng(2026091350|1351)` absent).

### 5. Three-arm paired runner — PASS

- One generator draw per block: single call site
  (`incremental.py:2289-2290`); reviewer spy over a 4-block run shows exactly
  one `generate_erasure_block` call per block, all three arms receiving the
  identical unmutated `logp` object in the frozen order; known-set order per
  block was `[45, 29, 29]` (static -> strict-stop -> R1) on non-rejecting
  blocks.
- Arms run in order static, strict-stop, R1 (`incremental.py:1346-1358`), each
  mutation-checked; `paired_match` recorded per block
  (`incremental.py:2307`); mutating-arm counterexample in the R1 suite flips
  the gate and nulls the candidate.
- Exactly five scalar-only files are written to the passed root
  (`incremental.py:2553-2561`): `frozen_plan.json`,
  `per_block_three_arm_outcomes.json`, `transcript_accounting.json`,
  `aggregate_comparison.json`, `report.md`; verified on the probe output with
  recursive scalar-only and forbidden-token checks.
- Root refusal: `out_path.exists()` is checked before seed validation and any
  decoder call (`incremental.py:2254-2257`); reviewer run with a counting
  `sc_decode` confirms `FileExistsError` and **0** decoder calls; banned seed
  2026091340/2026091321 similarly refuses with 0 decoder calls.
- Attempt-consumption point recorded in the plan
  (`incremental.py:2234-2236`: "first scientific sc_decode call of the
  three-arm run (static comparator arm, block 0)") and in the aggregate; code
  order confirms the static comparator runs first.
- No code path references the old evidence roots: grep for
  `static_protocol_dev_gate|paired_incremental_dev_gate` over
  `comparison_bench/src/` and the R1 test returns no matches (the only hits in
  the repo are pre-existing temp-directory *names* in the unchanged Phase 6
  test file); no `NBPOLAR-PHASE6-R1` literal or `outputs_comparison|model_f|
  parquet|ttbin|results/|sibling|artifact` token exists in either changed
  module.

### 6. Accounting, feedback, union bound, recount, rescue identities — PASS

- Formulas implemented: terminated `5*K_j + 64*j`; `decode_failed` at level i
  `5*K_i + 64*j`; `resource_abort` 0 (`incremental.py:595-608`); R1 per-block
  invariant `levels_invoked = tag_invocations + rejections (+1 failing level)`,
  `feedback = levels_invoked - 1`, checked by
  `incremental_record_consistent(..., advance_on_reject=True)`
  (`incremental.py:857-894`).
- 2623 public seed bits per tag (`10*256+63`), 1 public feedback bit per
  advance (tag mismatch or decode rejection; `incremental.py:550, 591,
  167-171, 606-608`).
- Union bound `min(1.0, total_tag_invocations * 2**-64)` via
  `verification_union_bound`; probe total `1.3444e-17 = min(1, 248*2^-64)`.
- Reviewer-owned independent literal recount (separate implementation, never
  calling `recount_transcript`) on the 80-block probe: all three arms match
  totals exactly for key-dependent bits, public control, tag invocations and
  feedback invocations (`match=True`); all 240 block records match the
  hand-computed formulas and invariants; per-block event walk on an injected
  rejection block shows per-level disclosure bits `[145, 20]` = `5*len(new)`,
  one tag, one control with reason `decode_rejected_advance_next_level`, event
  key/public sums equal to the record.
- Rescue identities (`incremental.py:976-1013`) partition verified
  independently on the 80-block probe: mine `rescued=10, persisted=70,
  regressed=0, other=0` equals the persisted `rescue_comparison_against_strict`
  (indices lists included; `partition_exhaustive: true`).

### 7. Gates, command, root, budget — PASS

- All 18 frozen gates are present with the freeze's names and order
  (`incremental.py:1987-2069`; probe gate list matches the R1_FREEZE §12 list
  exactly, count 18). Thresholds confirmed in code: `MIN_EXACT=285`
  (gate `r1_exact_ge_285`), `WILSON_LB_MIN=0.90`, integer rule
  `r1_total*100 <= 95*static_total` with equal attempted denominators and
  `static_key > 0`, `r1_undetected_zero`, coverage, buckets, recount, union
  bound, truth, nonfinite, resource, feedback/public-control,
  `strict_arm_pinned_consistency`. Candidate label
  `DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE` is emitted only when all 18
  gates are true (`incremental.py:2515-2517`); it is never emitted for a
  non-frozen seed (probe `candidate: None` with `frozen_plan_identity: false`).
- Wilson: formula independently re-implemented; bit-identical results at
  (285,300) 0.9249844882028562, (271,300) 0.8715597837542944, (298,300)
  0.9800565738801275, (300,300) 0.9910621278248719. The frozen `WILSON_Z`
  value 1.6448536269514722 differs from `statistics.NormalDist().inv_cdf(0.95)`
  by 1 ulp (1.6448536269514715); this is the pre-existing accepted Phase 5
  constant, unchanged, and has no threshold effect (see findings).
- 5% rule verified integer-exact in code and on the probe
  (`1777600 <= 2196400 -> True`, saving fraction 0.2311).
- Frozen command parses with the frozen interpreter without executing a
  decoder (`build_parser().parse_args`): mode `three-arm-paired-dev-gate`,
  run_seed 2026091350, blocks 300, the exact absent root; no extra flags exist.
  `timeout 1800` and `ulimit -v 2097152` are external and freeze-recorded.
- Real root `.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/
  three_arm_paired_dev_gate/`: ABSENT (`test -e` false; `ls` exit 2).
- Reviewer bounded re-measurement (non-frozen seeds, temp roots):

```
80 blocks  seed 2026091365: wall 4.24 s, max per-block 0.180 s, RSS 107,941,888 B
100 blocks seed 2026091370: wall 5.49 s, RSS 109,035,520 B
100 blocks seed 2026091371: wall 5.39 s, RSS 112,050,176 B
margins: per-block cap x83, total 900 s x~170, RSS 2 GiB x~19
```

### 8. Tests — PASS

Commands (reviewer-run; fresh staged basetemps under `/tmp/opencode`):

```
$ .venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_incremental_r1.py \
    -q -p no:cacheprovider --basetemp=/tmp/opencode/p6r1_review_basetemp/r1
-> 17 passed, 1 warning in 14.95s

$ .venv/bin/python -m pytest <all 11 test_nbpolar_*.py> \
    -q -p no:cacheprovider --basetemp=/tmp/opencode/p6r1_review_basetemp/full
-> 170 passed, 1 warning in 85.56s
```

Composition matches the declared 17 new / 170 total. The R1 file contains
exactly 17 `test_*` functions covering R1-A01..A12 plus refusals, five-file
scalar schema, resource abort, adapter round-trip and forbidden-marker/
import-side-effect scans; `R1-A01`..`R1-A12` substance inspected line-by-line
(rescue at every next level, no candidate/tag, feedback/increment, restart,
terminal taxonomy, recount/tamper, buckets, three-arm pairing, identities,
strict pinning, truth/nonfinite/undetected, constants+predecessors). The test
source contains no forbidden artifact path, no `.workbuddy` reference, and no
`default_rng(2026091350|1351)`.

### 9. RISK REPORT (advisory, not tuning) — bounded probes

Three non-frozen probes (seeds 2026091365/2026091370/2026091371; temp roots;
no gates claimed):

| probe | blocks | static exact | strict exact | R1 exact | avg key static | avg key R1 | saving | rescued | regressed | other | R1 rejections | R1 Wilson LB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026091365 | 80 | 80/80 | 70/80 | 80/80 | 289.0 | 222.2 | 23.1% | 10 | 0 | 0 | 15 on 10 blocks | 0.9673 |
| 2026091370 | 100 | 100/100 | 91/100 | 100/100 | 289.0 | 223.2 | 22.8% | 9 | 0 | 0 | 12 on 9 blocks | 0.9737 |
| 2026091371 | 100 | 99/100 | 89/100 | 99/100 | 288.4 | 220.2 | 23.7% | 10 | 0 | 0 | 17 on 11 blocks | 0.9564 |

Interpretation:
- Expected R1 exact rate: probes show 100%, 100%, 99% (the 99% equals the
  static ceiling on that draw). R1 is monotone against strict by
  construction: a block that never hits a non-final impossible-disclosure runs
  the identical strict sequence (same seeds), so `exact_R1 >= exact_strict` and
  `regressed = 0` is structural, not luck. The frozen gates need `exact >= 285`
  and `Wilson LB >= 0.90`: with the accepted Phase 6 strict point at 271/300,
  only 14 of the 29 strict failures must convert; probes converted 29/29 at a
  strict failure rate of 9-11%, matching the Phase 6 observed 9.7%.
- Average key-dependent bits: R1 ~220-223 vs static ~288-289 (~23% saving)
  against a required 5%: wide margin even after adding the rescue cost
  (>=84 extra bits per level-0 rescue) and even under the pessimistic bound
  that every strict failure is rescued late (roughly 2-3 percentage points).
- Residual risks: a block whose impossibility persists through K45 stays
  `decode_failed` (never contributes to exact), and the static ceiling
  (1-2 static decode failures per 100) caps R1 just below 300; both are far
  from the 285 threshold. Budget risk is negligible (x83 per-block, x170 total,
  x19 RSS observed). Coverage/accounting/truth/nonfinite/union-bound gates were
  green in every probe (only `frozen_plan_identity` and `r1_exact_ge_285` were
  false, both expected at non-frozen seeds/<300 blocks).
- The frozen gates look attainable with comfortable margins in this regime.

### 10. Scope/premises — PASS

- `git status --porcelain` count 35 before and after the review (no reviewer
  writes to the repo). Files with mtime after the session start (10:30) are
  exactly the declared R1 set: queue `STATUS.yaml`, `R1_FREEZE.md`,
  `R1_IMPLEMENTATION_NOTES.md`, `OPERATOR_RETURN.md`,
  `incremental.py`, `methods/nbpolar_incremental.py`, `__init__.py`,
  `test_nbpolar_incremental_r1.py`,
  `openspec/.../phase6-r1-decode-reject-advance/design.md`. All other dirty
  paths predate the session (mtimes 00:31-03:47 or main-thread packet setup at
  10:26-10:27, including `MAIN_THREAD_DISPOSITION.md`).
- Frozen `src/`, `experiments/`, `tools/`, `results/`,
  `comparison_bench/outputs_comparison/`: `git status --porcelain -- <paths>`
  returns 0 lines. Sibling checkouts: `.git/HEAD` mtime 2026-09-02,
  `.venv` mtime 2026-09-10 (used read-only as interpreter), cascade worktree
  mtime 2026-08-30; no session writes.
- Immutable Phase 5/P6 evidence roots: `stat` mtimes
  `static_protocol_dev_gate` 2026-09-13 02:31:13 and
  `paired_incremental_dev_gate` 2026-09-13 03:33:34, both before this session;
  no content read or written by the reviewer.
- HEAD unchanged (`ab173f2a5e...`); real three-arm root still absent;
  `attempts_used` still 0.
- OpenSpec delta `specs/decode-reject-advance/spec.md` matches the design Rev
  note; `tasks.md` has all boxes unchecked (implementation awaits this PASS),
  consistent with "no task box checked"; `proposal.md` matches the frozen
  delta. `docs/decision-log.md` already records the option (a) ruling
  (2026-09-13 section). No new failure mode was discovered, so no
  `docs/troubleshooting.md` entry is required.

---

## Complete frozen record (verified)

| item | frozen value | verification |
|---|---|---|
| run seed | 2026091350 | constant; absent from HEAD; only new R1 artifacts |
| Toeplitz master | 2026091351 | constant; public; derivation string frozen |
| derivation | SHA-256("nbpolar-p6-toeplitz-seed:<master>:<arm>:<block>:<level>:<counter>"), MSB-first, 2623 bits | manual recompute bit-identical for 7 samples |
| arm namespaces | static; incremental (both incremental arms) | code L164/L581; strict/R1 seeds identical on non-rejecting block |
| arms/order | static K45, strict-stop, R1 | runner order; spy evidence `[45,29,29]` |
| schedule | K=(29,33,37,41,45); D1..D5 as freeze §5 | recomputed; nesting/prefix/disjoint flags true; D5 == static K45 |
| command | `ulimit -v 2097152; timeout 1800 ... --mode three-arm-paired-dev-gate --run-seed 2026091350 --blocks 300 --out .workbuddy/.../three_arm_paired_dev_gate` | parse-only check OK; not executed |
| root | absent until authorized | `test -e` false |
| budget | 900 s internal, 15 s per-block soft cap, 1800 s external, 2 GiB ulimit-v | constants; probe margins x83/x170/x19 |
| schema | exactly 5 scalar-only files, names as freeze §11 | probe file list + scalar scan |
| precedence | resource_abort > decode_failed > verify_failed > exact > undetected; rejection never a bucket | code; bucket sums |
| accounting | 5*K_j+64*j; feedback 1 bit/advance; 2623 seed bits/tag; union bound min(1, tags*2^-64) | independent recount 3 arms; formulas hand-checked |
| Wilson | one-sided 95%, z=1.6448536269514722, denominator attempted | formula re-implemented bit-identical |
| 5% rule | `r1_total*100 <= 95*static_total`, equal attempted | integer check on probe |
| rescue identities | rescued/persisted/regressed/other with index lists | independent recompute equals persisted |
| gates | 18 names as freeze §12, candidate label only if all true | list/count/label verified |

## Findings

Blocking issues: none.

Non-blocking suggestions:
1. `WILSON_Z` = 1.6448536269514722 vs `statistics.NormalDist().inv_cdf(0.95)`
   = 1.6448536269514715 (1 ulp). Pre-existing accepted Phase 5 constant, not
   part of this delta; recorded for completeness only. No action needed.
2. `frozen_plan.json.budget.rss_bytes_max` names the external `ulimit -v`
   2 GiB virtual ceiling while `rss_bytes_peak` measures RSS
   (`incremental.py:1475, 1253-1256`). Cosmetic naming; the freeze explicitly
   documents the ulimit as virtual. No action needed.
3. The R1 suite has no dedicated `reject -> final mismatch` case (covered by
   code review and this reviewer's independent check; branch
   `incremental.py:887-893` is correct). Optional future addition, not
   required by the packet.
4. `paired_match` is recorded `true` for unexecuted `resource_abort` records
   (`incremental.py:1385-1398`), matching the accepted Phase 6 pattern; the
   coverage gate catches aborts. No action needed.
5. The banned-validator interpretation (separate `validate_r1_run_seed`) is
   adjudicated PASS above; suggest the main thread note the functional-extension
   reading in the acceptance record so the wording difference is not
   re-litigated.
6. `docs/troubleshooting.md` needs no update now; after the run, the memory
   triage should record the Pre-RESULT outcome in `docs/decision-log.md`
   (the option (a) ruling is already recorded).

## Closure statements

- The real three-arm command was **not run** by this reviewer; only parse-only
  and temp-root/non-frozen-seed probes were executed. No `sc_decode` call was
  made with the frozen seed.
- `attempts_used` remains **0**; `attempts_allowed: 1`; the single attempt is
  unconsumed.
- The real output root
  `.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`
  is still **absent**.
- The immutable Phase 5/P6 evidence roots were not opened, parsed, or written
  (directory metadata only); frozen `src/`, `experiments/`, `tools/`,
  `results/`, `outputs_comparison/` and sibling checkouts are untouched.
- HEAD unchanged; no commit/push; no artifact/real-data/SCL/Phase 7 path used.
- The review pass authorizes execution of the frozen command by the main
  thread under the recorded authorization; it does not itself grant
  acceptance or consume the attempt.

— independent reviewer-go (backup instance), 2026-09-13
