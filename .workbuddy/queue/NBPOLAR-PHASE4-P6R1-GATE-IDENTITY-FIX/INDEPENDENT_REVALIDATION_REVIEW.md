# Independent revalidation review — NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX

Fresh independent reviewer-go session (2026-09-14, WSL), working tree
`/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, HEAD `ab173f2a...` (unchanged;
no commit, no push). Pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3,
pytest 9.1.1). I did not write the fix, the tests or the revalidation helper,
and did not run the frozen P6 gate or any production/frozen-seed decoder.

Read-only: the P6 evidence root and its persisted `BLOCKED` label were only
read; every before/after hash and mtime is identical (section 4). The only file
this review created is this `INDEPENDENT_REVALIDATION_REVIEW.md`.

## Verdict: PASS_WITH_COMMENTS

No blocking issue. The code delta is limited to the event-identity change and
the corrected D2-once grouping; the multi-stream regression test fails on the
pre-R1 grouping and passes only on the compound identity; my independent
reconstruction of all 640 records / 1280 obligations / 12 integrity / 4
scientific gates matches `revalidation.json` with exactly the one diagnosed
false→true correction; the old root is byte-for-byte unchanged; the helper and
the new test paths made zero decoder/RNG/tag calls. Three non-blocking notes
are recorded at the end (a narrative line-count off-by-one, declarative rather
than instrumented counters, and the inherent anchor-based D2 recount). The
successor label may be returned by the operator as a candidate; main-thread
acceptance remains separate.

---

## 1. Code delta audit — PASS

### 1.1 Delta and provenance

`adaptive_l1.py` is untracked in git, so the pre-R1 baseline cannot be taken
from git. The operator reconstructed it in `/tmp/opencode/p6r1_diff/` by
inverse-applying the logged edits. I regenerated the diff myself from that
baseline and the current file and obtained exactly the operator's saved diff
(identical hunks, headers aside):

- baseline `/tmp/opencode/p6r1_diff/adaptive_l1_pre_r1.py`, sha256
  `20ad2a8e...ddbae`, 2301 lines — identical hash to the `/tmp/opencode/p6r1_oldgroup/`
  copy used for the old-grouping probe;
- current `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py`,
  sha256 `910296ae3c4a56bdfa602dc05b0ac63f281f8ec61ba0531cd749d98a7f4fcc83`
  (matches the OPERATOR_RETURN_R1 table), 2327 lines;
- diff = **13 hunks, +32/−6 lines** (the OPERATOR_RETURN narrative says
  `+31/-6`; see non-blocking note 1).

Baseline plausibility: the reconstructed pre-R1 file matches **every**
pre-R1 line anchor recorded in the independent P6 `PRE_RESULT_REVIEW.md`:
`frame_key` at :866, `block_id` at :872, `paired_block_events` def at :881,
static L2 event id at :909, adaptive L2 event id at :956, gate key at :1342,
`expected_l2` at :1347, `all(count == 1 ...)` at :1352, gate entry at :1391,
runner caller at :2110, stream loop at :2059.

### 1.2 The 13 hunks are exactly the two authorized operations

| hunk | change | class |
|---|---|---|
| docstring :34 | 4 lines documenting the compound identity | (a) doc |
| `_event` signature :855 | `stream_seed: int` kwarg | (a) identity |
| `_event` body :867 | `frame_key` → `...:<stream_seed>:<block_index>`; event dict gains `"stream_seed"` | (a) identity |
| `paired_block_events` :883 | signature gains `stream_seed`; `_as_int` validation; docstring | (a) identity |
| 7 `_event(...)` call sites :906/:921/:935/:954/:971/:987/:1003 | pass `stream_seed=stream_seed` | (a) identity |
| gate :1357 | D2 count key `(block_id, arm)` → `(stream_seed, block_id, arm)`; `expected_l2` → `(r.stream_seed, r.block_index, arm.arm)`; 2 comment lines | (b) gate grouping |
| runner :2129 | `paired_block_events(..., stream_seed=int(stream_seed), ...)` | (a) wiring |

All seven `_event(` calls in the file (the only call sites) were updated; the
only `paired_block_events` caller updated. No hunk touches any other function.

### 1.3 Scientific constants/semantics unchanged

Frozen constants read identically at their original lines: `TAG_BITS=64` :88,
`DISCLOSED_BITS_PER_COORDINATE=5` :89, `FEEDBACK_CONTROL_BITS=1` :90,
`FROZEN_N=256` :92, `FROZEN_EPSILON1=0.05` :93, `FROZEN_K1_LEVELS=(45,60,72,112)`
:96, `FROZEN_K2=140` :97, `STATIC_K1=112` :98, `FROZEN_SEEDS` :99,
`STATIC_EXACT_MIN=620` :103, `RSS_LIMIT_BYTES=2*1024**3` :105, `TOTAL_WALL_S=3600.0`
:106, `ATTEMPT_ACCOUNTING` 1/0/1/0 :164-169, `INTEGRITY_GATE_ORDER` :136-149,
`BANNED_SEEDS` :117-130. No change to the decoder call path, outcome taxonomy,
disclosure formulas, recount, scientific gates, CLI or output schema; the new
`stream_seed` is an additive public event field that does not alter event ids
(so `recount_transcript`, which parses the arm from `event_id`, is unaffected).

### 1.4 Untouched modules/roots

- `sc.py`, `prior.py`, `construction.py`: tracked and `git status` clean
  (sha256 `5f1591cb…`, `c6fb48cb…`, `423783ad…`).
- `two_layer.py` (`c6584325…`, mtime 2026-09-13 12:59), `penalty_gate.py` P5
  (`30dbd334…`, 17:14), `methods/nbpolar_static.py` (`f20e4f01…`, 09-13 02:00),
  `methods/nbpolar_incremental.py` (`155bb829…`, 10:41): all mtimes before the
  R1 session (23:43) and no repo-wide find hit.
- Probes `docs/nbpolar/probes/*` and `.workbuddy/queue/NBPOLAR-X01-*`: mtimes
  15:40–20:07, before the session.
- `formal_ir/nbpolar/__init__.py`: mtime 21:07 (P6 session, pre-R1); R1 did not
  edit it. A revalidation-package export was allowed but not needed.
- Repo-wide `find . -newermt '2026-09-13 23:43' -type f` after all reviewer
  work returns only: the R1 packet files, `adaptive_l1.py`,
  `adaptive_l1_revalidate.py`, `test_nbpolar_adaptive_l1.py`, the OpenSpec rev
  note, the two packet-preparation mtimes (`CURRENT_TASK.md`,
  `DOCUMENT_INDEX.md` = 23:43:48), this review file, and regenerable
  `__pycache__` `.pyc` build cache (untracked; touched by py_compile and the
  test runs — not source, not evidence).

## 2. Regression test and suites — PASS

### 2.1 Test design (inspected)

`test_p6_r1_multistream_compound_d2_identity_gate` (test file lines 629–814):

- two streams `TEST_SEED_A=2026091560`, `TEST_SEED_B=2026091561` share block
  indices `0..1` (4 distinct `(stream, block)` pairs, 8 arm-blocks);
- builds TEST-ONLY scalar fake arms and feeds the **production**
  `paired_block_events` and `_integrity_gates` (pure record/checker logic);
- asserts the corrected gate and `all(gates.values())` on the fixture;
- asserts 8 L2 events, each carrying `stream_seed` and the stream-qualified
  `frame_key`; compound distinct identity == 8;
- reconstructs the **old** `(block_id, arm)` counts and asserts multiplicities
  `[2,2,2,2]`, i.e. the pre-R1 `count == 1` check must fail on exactly this
  fixture;
- drops and duplicates one compound D2 disclosure and asserts the gate becomes
  `False` while every other frozen gate stays `True` (recount/mismatches held
  fixed).

### 2.2 Pre-R1 failure reproduced independently

- Fixture-level arithmetic (my own): old keys
  `{(0,static):2,(0,adaptive):2,(1,static):2,(1,adaptive):2}` →
  `all(count == 1) = False`; compound keys all count 1 → `True`.
- Pre-R1 module probe re-run by me, read-only from `/tmp`:
  `l2_events 8`, `old_key_multiplicities [2,2,2,2]`, `old_gate4 False`,
  `other_gates_true True`, exit 0.
- New test run against the pre-R1 module (`/tmp/opencode/p6r1_oldgroup`):
  `1 failed, 15 deselected` with
  `TypeError: paired_block_events() got an unexpected keyword argument 'stream_seed'`,
  confirming the identity field is mandatory.

### 2.3 Suites (pinned interpreter, fresh `/tmp` basetemps, `-q -p no:cacheprovider`)

| command | result |
|---|---|
| `py_compile` module + helper + test | `COMPILE_OK` |
| focused `test_nbpolar_adaptive_l1.py` | **16 passed**, 1 warning, 8.06 s |
| full `test_nbpolar_*.py` | **217 passed**, 1 warning, 122.69 s |

(201 accepted predecessors + 16 focused, matching the P6 freeze expectation
216 + the one new test.)

## 3. Independent gate reconstruction vs `revalidation.json` — PASS

I read only the five original files and recomputed everything with my own
stdlib script (not the operator helper): coverage/identity product, per-record
static/adaptive structural proofs, nested-D1 proof from the persisted plan,
compound-identity D2 obligations, transcript recount/accounting, wall/RSS,
attempt accounting, and the four scientific gates with the frozen thresholds.

Raw reconstruction results:

- 640 records, 640 unique `(stream_seed, block_index)` = exact product
  `{2026091550..54} × {0..127}`, no duplicates, 2 arms each;
- 1280 `(stream, block, arm)` obligations, all `l2_invoked=true`, all count 1,
  1280 distinct; recorded = recounted = summary transcript L2 total = 1280;
  per stream/arm 128 each (10 × 128);
- under the old grouping: 256 keys each with multiplicity 5 — exactly the
  diagnosed collision;
- outcomes static/adaptive `{exact: 632, verify_failed: 8, others: 0}`; cells
  `{both_exact: 632, neither: 8, adaptive_only: 0, static_only: 0}`;
- key-dependent bits static 847,360 / adaptive 675,783; tags 640/942/1582;
  feedback 302; public control 1,678,720/2,471,168; union bound
  `8.57603918436034e-17`.

Gate-by-gate comparison (persisted = original frozen `aggregate_summary.json`;
corrected = `revalidation.json`; mine = independent recompute):

| # | gate | persisted | corrected | mine |
|---|---|---|---|---|
| 1 | pairing_coverage_complete | true | true | true |
| 2 | stream_block_identity_exact | true | true | true |
| 3 | result_buckets_disjoint_exhaustive | true | true | true |
| 4 | d1_exactly_nested_and_d2_disclosed_once | **false** | **true** | **true** |
| 5 | provenance_and_truth_isolation_complete | true | true | true |
| 6 | undetected_zero | true | true | true |
| 7 | nonfinite_zero | true | true | true |
| 8 | resource_abort_zero | true | true | true |
| 9 | transcript_recount_mismatch_zero | true | true | true |
| 10 | tag_feedback_public_control_accounting_and_union_bound_exact | true | true | true |
| 11 | wall_rss_within_frozen_limits | true | true | true |
| 12 | attempt_seed_accounting_exact | true | true | true |
| S1 | static_exact_at_least_620_of_640 | true | true | true (632/640) |
| S2 | adaptive_exact_equals_static_exact | true | true | true (632=632) |
| S3 | paired_adaptive_only_zero_and_static_only_zero | true | true | true (0/0) |
| S4 | leakage_100_adaptive_le_85_static | true | true | true (67,578,300 ≤ 72,025,600) |

Value comparison `revalidation.json` ↔ my recompute: **42/42 checked comparison fields
match** (after normalizing dictionary key names and zero-count cells), including all 12+4 gates, `gate_differences_vs_persisted` (exactly the
single d1 false→true entry), paired counts, L2 totals, outcomes, cells,
marginals, all six disclosure totals, counters, `attempts_consumed=0`,
`old_root_unchanged`, both inventories, and all 9 `cross_checks`. The only
difference vs the persisted run is the diagnosed identity correction; no second
discrepancy exists. A fresh helper re-run (written to `/tmp` only) is
**byte-identical** to the committed `revalidation.json`
(sha256 `4b684a046c87bc8aead2e6f7aead3c7abf6b096b7e15f71e35e03a0f25ee12c1`,
matching the OPERATOR_RETURN table).

## 4. Old-root immutability — PASS

`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
contains exactly the five original files. Hashes before my first read and after
all reviewer work are identical, and match the recorded inventory:

| file | size | sha256 (before = after) |
|---|---|---|
| frozen_plan.json | 15248 | `f27fa45d…5be07` |
| per_block_paired_outcomes.json | 1125035 | `7b794ddd…61423` |
| transcript_accounting.json | 2090 | `c3084898…b4138` |
| aggregate_summary.json | 9090 | `2c2c09bf…5dc6` |
| report.md | 2023 | `d595e95f…87ce3` |

mtimes remain `2026-09-13 21:25:30.511–.558` (the single P6 generation
instant); directory mtime unchanged; no `.tmp`/copy/extra file appeared. The
persisted `aggregate_summary.json` still says `outcome_label=BLOCKED`,
`integrity_all_pass=false`, `failing_integrity_gates=[d1_...]`,
`scientific_all_pass=true`; `report.md` still prints `BLOCKED`. The P6
`STATUS.yaml` remains `BLOCKED_INTEGRITY_GATE_DEFECT_PENDING_MAIN_THREAD_DISPOSITION`
with `attempts_used: 1`.

## 5. Zero decoder/RNG/tag calls, zero attempt consumption — PASS

- **Helper**: stdlib-only imports (`argparse/hashlib/json/sys/pathlib`);
  `FORBIDDEN_MODULES` guard refuses if numpy/random/sc/prior/two_layer/
  penalty_gate/incremental/adaptive_l1/shared are loaded. I re-ran it under an
  independent `sys.addaudithook` import logger: exit 0, 39 import events,
  **zero** forbidden-prefix imports. Call-site audit finds no
  `default_rng`/`toeplitz_tag`/`sc_decode`/sampler/runner reference.
- **New test**: I re-ran it with `toeplitz_tag`, `sc_decode`,
  `two_layer._decode_layer`, `adaptive_l1.run_paired_block`,
  `adaptive_l1.run_adaptive_gate`, `penalty_gate.sample_dependent_block` and
  `numpy.random.default_rng` all patched to raise — the test completed clean,
  zero forbidden calls fired. Static audit of the test body: no forbidden call
  names.
- **Attempts/seeds**: `revalidation.json` reports
  `counters={decoder_calls:0, rng_calls:0, tag_calls:0}`,
  `attempts_consumed=0`; R1 `STATUS.yaml` is `attempts_allowed/used: 0/0`. The
  only executions I performed were the mandated test suites (their own tiny
  injected fixtures and fixed test seeds 2026091560.. under `/tmp`) and
  read-only/`/tmp` helper runs; no frozen seed, master or production root was
  touched by any of them.

## 6. Persisted label / successor-label consistency — PASS

The original `BLOCKED(d1_exactly_nested_and_d2_disclosed_once)` label is not
rewritten or reinterpreted anywhere; `revalidation.json` preserves it under
`original_persisted` and records `old_root_unchanged: true`.
`result_label = ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` is emitted **iff all
corrected integrity and scientific gates are true**; all 16 are true in both
`revalidation.json` and my reconstruction, so the iff holds. The helper does
not write inside the old root (refuses if `out` is inside `root`), and its
result file is the single declared artifact outside it.

## Non-blocking comments

1. OPERATOR_RETURN_R1 §R1-I03 says the delta is `+31/-6`; both my plain and
   unified diffs count **+32/−6** (the appendix diff itself contains 32 added
   lines). Documentation off-by-one only; no semantic impact.
2. `revalidation.json.counters` are declarative constants, not runtime
   instrumented counters (the helper never increments them). The substantive
   zero-call evidence is the import guard, the pure-stdlib implementation, my
   audit-hook re-run and the patched-entry-point test run; consider tying the
   counters to actual call sites if they are ever meant as tamper evidence.
3. The corrected D2-once revalidation cannot replay in-memory events (never
   persisted); it reconstructs the 1280 obligations from the per-block records
   and anchors the one-disclosure count on the recorded/recounted transcript
   total (1280). This is exactly the packet's R1-03 definition and matches the
   P6 Pre-RESULT diagnosis; no over-claim is made.

## Closure statements

- No decoder, RNG, sampler or tag-generator call was made by the fix path, the
  new regression test or the revalidation helper; no frozen gate was rerun and
  no frozen seed/master was used by this review.
- The old root is byte-for-byte unchanged (five files; sizes, sha256 and mtimes
  identical before/after) and its persisted `BLOCKED` field is untouched.
- I independently reconstructed all 640 compound identities, all 1280 D2
  obligations, the L2 total (1280), all 12 integrity gates and all 4 scientific
  gates; `revalidation.json` matches with exactly the single diagnosed
  false→true correction and byte-identical reproduction.
- Only this file was written; no commit, no push.

## Reviewer commands (condensed, all read-only except `/tmp` outputs)

```
diff /tmp/opencode/p6r1_diff/adaptive_l1_pre_r1.py <module>              # 13 hunks, +32/-6
python3 /tmp/opencode/p6r1_reviewer/independent_recompute.py             # 12+4 gates, sole d1 diff
python3 /tmp/opencode/p6r1_reviewer/compare_to_packet.py                 # 0 mismatches vs revalidation.json
/mnt/.../.venv/bin/python /tmp/opencode/p6r1_reviewer/audited_run.py     # helper rerun, no forbidden imports
/mnt/.../.venv/bin/python /tmp/opencode/p6r1_reviewer/zerocall_test_probe.py  # patched entry points, 0 fired
pytest comparison_bench/tests/test_nbpolar_adaptive_l1.py -q -p no:cacheprovider --basetemp=/tmp/opencode/p6r1_reviewer_focused      # 16 passed
pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider --basetemp=/tmp/opencode/p6r1_reviewer_predecessors           # 217 passed
sha256sum <five old-root files>; ls -la --time-style=full-iso <old root>  # before == after, mtimes 21:25:30
```

**Verdict: PASS_WITH_COMMENTS** — no blocking issue; the three comments above
are documentation/transparency notes. Reviewer PASS permits the operator to
return the successor candidate label; main-thread acceptance remains separate.
