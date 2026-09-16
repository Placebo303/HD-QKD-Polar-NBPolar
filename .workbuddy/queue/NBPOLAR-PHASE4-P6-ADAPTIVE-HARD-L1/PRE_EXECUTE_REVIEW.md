# Pre-EXECUTE review — NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1

Independent reviewer-go session (2026-09-13, ~21:11–21:35 WSL). I did not write the
module, the tests, the freeze, the spec or the packet. Read-only except this file.
The real 640-pair gate command was **NOT executed** — no scientific SC call was made,
so the single attempt is **not consumed** (`attempts_used: 0`). No Model-F / artifact /
real-data access; X04/X05 and all predecessor evidence roots were read-only design
inputs; no commit or push. Repository `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`;
HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged); pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).

## Verdict: PASS

All eight required checks pass. The frozen point, schedule, disclosure sets,
seeds/masters, command, budgets, accounting, gates and labels in `P6_FREEZE.md` match
`adaptive_l1.py` and the OpenSpec P6 delta, and match the TASK_PACKET. The focused and
full predecessor suites pass (15 and 216), the tiny injected smoke writes exactly five
scalar-only files with all 12 integrity gates true and a large wall/RSS margin, and the
gate root is absent. No blocking issue found. Six non-blocking observations are listed
in §Findings; none changes a number, a gate or a conclusion.

## 1. STATUS edit exactness — PASS

`STATUS.yaml` (raw content) has exactly the 13 declared keys, no more:

- `documentation_authorized: true`, `implementation_authorized: true`,
  `decoder_execution_authorized: true`, `development_gate_authorized: true` — the four
  authorized flags;
- `artifact_read_authorized: false`, `real_data_authorized: false`,
  `scalable_decoder_authorized: false`, `scl_authorized: false`,
  `scientific_promotion: false` — all false, matching the authorization text
  (`AUTHORIZATION_PROMPT.md`) and the accepted P5 authorized precedent verbatim in
  flag block;
- `attempts_allowed: 1`, `attempts_used: 0`, `result: null`,
  `independent_pre_execute: pending`, `independent_pre_result: pending`;
- `state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P6_ADAPTIVE_HARD_L1`,
  `next_gate: IMPLEMENTATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW` — the pre-execution
  state consistent with `P6_FREEZE.md:7` ("awaiting independent Pre-EXECUTE PASS;
  authorizes nothing") and `TASK_PACKET.md` P6-E.

Evidence note: the packet directory is entirely untracked (`git ls-files` empty), so a
literal `false→true` diff against a committed STATUS template is not available; the
adjudication is content-vs-declared-authorization. The four-true/five-false pattern is
byte-identical to the accepted P5 authorized STATUS
(`.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/STATUS.yaml`).

## 2. OpenSpec delta — PASS

- `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p6/spec.md`
  (135 lines, new) exists and states, in six numbered requirements: the frozen
  GF32/poly-37/alpha-2/N=256 point, `epsilon1=0.05`, strong
  `epsilon2(u1)=0.02+0.36*u1/31`, nested `D1`/fixed `D2=140`; the static endpoint arm;
  the adaptive restart ladder with tag/feedback/nonterminal-terminal impossible
  semantics, no-state-reuse and truth scope; the `5*(K_j+140)+64*tag_invocations` /
  `2623*tag_invocations` accounting, literal recount and `min(1,tags*2^-64)` union
  bound; the 12 integrity + 4 scientific gates and the two registered labels; the
  frozen CLI, five-file output, refused seeds and bounded synthetic scope; and the
  independent Pre-EXECUTE/Pre-RESULT requirement.
- `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md:170-210` holds the P6 section
  P6-1..P6-8. `grep -n 'P6-' tasks.md | grep '\[x\]'` → no match: **no P6 task box is
  checked**, as required ("the implementing session never checks its own boxes").
- Cross-checked term by term against `TASK_PACKET.md` §P6-B/§P6-C/§P6-F and
  `P6_FREEZE.md` §3/§5/§6/§8/§9: point, schedule, restart/tag/feedback/impossible
  rules, accounting, gate names/order, labels and bounded scope are consistent; the
  refused-seed enumeration in `spec.md:107-112` equals the module set exactly (65 = 65).

## 3. Frozen identity — PASS

All values recomputed independently with the pinned interpreter from the accepted
modules (not read from the freeze):

| item | recomputed value | status |
|---|---|---|
| field | `make_gf32()` → `m=5`, `q=32`, `primitive_polynomial=37`; `ALPHA=2`; natural order | PASS |
| point | `FROZEN_N=256`, `FROZEN_EPSILON1=0.05`, `FROZEN_PROFILE="strong"`, `PROFILE_FORMULAS["strong"]="0.02 + 0.36*u1/31"` (mean exactly 0.20) | PASS |
| strong table | column deviation `3.774758283725532e-15 <= 1e-12`; `p2_maxdiff=0.34875000000000267` = closed form `0.36*31/32`; pre-decoder floor `0.30` enforced | PASS |
| H(A\|B) | chain `2.134043324031305` == reference; chain-vs-direct `4.44e-15`; denominator `256*H = 546.3150909520141` | PASS |
| D1 | sizes `[45,60,72,112]`; each equals `sorted(analytic_order(0.05,256)[:K])`; strict nesting true; `new_positions` partition `D1(112)`; `D1(45)` equals accepted `tl.frozen_disclosure_sets(n=256,k1=45,k2=140,epsilon1=0.05,epsilon2=0.20)[0]` | PASS |
| D2 | `sorted(analytic_order(0.20,256)[:140])`, shape `(140,)`, 140 unique; one `l2_disclosure` event per arm/block in the smoke | PASS |
| streams/masters | `(2026091550..2026091554)`, 128 blocks each → 640 pairs; masters `+10000` = `2026101550..2026101554`; per-arm/block/level SHA-256 domain derivation (`nbpolar-p4p6-toeplitz-seed:<master>:<arm>:<block>:<level>:<counter>`) reproduced bit-exactly by an independent implementation | PASS |
| freshness | `git grep -E "202609155[0-4]" HEAD` → exit 1 (no match); same for masters; worktree `rg` excluding this packet's files → exit 1 (no match) | PASS |
| refused set | module `BANNED_SEEDS` (65) is a strict superset of `penalty_gate.BANNED_SEEDS`, `incremental.R1_BANNED_RUN_SEEDS` and `two_layer.BANNED_RUN_SEEDS`; equals the spec/tasks enumeration; all five frozen seeds and masters accepted | PASS |
| attempt point | `ATTEMPT_CONSUMPTION_POINT="first scientific SC call (stream 2026091550, block 0, static L1)"`; instrumentation of `tl._decode_layer` confirms the **first decoder call** is the static L1 with `D1(112)`; static arm runs before adaptive in `run_paired_block` (`adaptive_l1.py:791`) | PASS |
| budgets | `TOTAL_WALL_S=3600.0`, `EXTERNAL_TIMEOUT_S=3600`, `ULIMIT_VIRTUAL_KIB=2097152`, `RSS_LIMIT_BYTES=2147483648`; command carries `ulimit -v 2097152` / `timeout 3600` | PASS |
| command | extracted bash blocks of `TASK_PACKET.md:92-95`, `P6_FREEZE.md:235-238` and module `FROZEN_COMMAND` are byte-identical (`packet==freeze: True`, `packet==module: True`); parsed by the module's own parser to exactly the frozen point (`k1_levels=[45,60,72,112]`, `k2=140`, `seeds=[2026091550..54]`, `blocks_per_seed=128`, `out_dir=.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate`) | PASS |
| gate root | `test ! -e .workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate` → ABSENT at review open and at close; `find . -type d -name paired_adaptive_gate` → none | PASS |

## 4. Code review (`adaptive_l1.py`, 2301 lines) — PASS

- **Static arm** (`run_static_arm:448`): one fresh L1 SC at `d1=D1(112)` on the P1
  `PRIOR_ONLY` metric, one fresh candidate-conditioned L2 SC at `K2=140` on a metric
  gathered from Bob + the hard candidate, label `low_hat + 32*high_hat`, exactly one
  64-bit Toeplitz tag under arm `static` level 1. Fully invoked cost `1324`.
- **Adaptive arm** (`run_adaptive_arm:577`): every stage calls a fresh
  `tl._decode_layer` on the **same original** `p1_logp` object with the cumulative
  nested prefix, then a freshly gathered `CANDIDATE_CONDITIONED` metric from Bob + the
  current stage's candidate, then one tag under level `stage+1`. No decoder object,
  metric, partial sum, candidate label or tag seed crosses stages; `sc._validate_metric`
  copies its input (`sc.py:107`), so the original metric is never mutated.
- **Stop/advance**: tag match stops (`:689`); pre-terminal mismatch emits exactly one
  feedback and advances one stage (`:693-696`); `K1=112` mismatch is `verify_failed`
  (`:697`).
- **Impossible semantics**: nonterminal `ImpossibleDisclosedValueError` → no
  candidate/tag for that stage, one feedback, advance (`:641-648`); terminal stage →
  `decode_failed` (`:649-652`); every other L1/L2 exception fails closed with no tag
  and no feedback (`:653-658`, `:682-687`). A decode rejection creates no tag.
- **Truth boundary**: `high/low` truth enters only sampling, `u1_true[d1]`/`u2_true[d2]`
  disclosed values, `labels_true(_bits)` for tag construction and scoring
  (`labels_true` is never passed to `build_p1_metrics`/`gather_p2_metrics`); the
  per-block mutation sentinel (`two_layer.py:424`) flips every truth buffer in place and
  requires every protected operational array to stay bitwise unchanged
  (`run_paired_block:825-842`).
- **Accounting** (`:705-711`, `:532-536`): `5*K_j + 5*140 (when L2 was invoked) +
  64*tag_invocations`; `public_seed_bits = 2623*tag_invocations`;
  `feedback_bits = feedback_invocations`; `public_control = seeds + feedback`. The only
  non-literal corner is the documented all-reject/no-L2 path counted as `5*K_j` and
  persisted as `no_l2_exhaustion_blocks` (`:2112-2113`); on every smoke record the
  literal formula held with zero arithmetic mismatches.
- **Independent literal recount** (`recount_transcript:1009`): parses the arm from the
  canonical `event_id`, sums key-dependent/public/feedback fields and counts tag/control
  events; required zero mismatch against incremental totals and against per-record sums.
  Verified on all smoke artifacts: `mismatch_count == 0`, recount == incremental.
  Union bound `verification_union_bound` (`shared.py:185`) = `min(1, tags*2^-64)`,
  reproduced exactly (e.g. 9 tags → `4.87890977618477e-19`).
- **Writer**: exactly `OUTPUT_FILES`; `per_block_paired_outcomes.json` records contain
  only the frozen scalar fields (`_arm_record:1097`, 25 keys) with **no arrays and no
  symbol/label/disclosed-value payloads**; no disclosed values or seed bits persisted.
- **Refusals before any decoder call** (`:1971-2002`): existing root, `n!=256`,
  `epsilon1!=0.05`, `profile!=strong`, `k1_levels!=(45,60,72,112)`, `k2!=140`,
  duplicate/banned seeds all raise before the table build/floor/nested proof and hence
  before any `sc_decode`; an instrumented bomb on `tl._decode_layer` was not reached for
  any refusal. `p2_maxdiff` floor and nested proof also precede decoder calls.
- **Gates/labels** (`_integrity_gates:1292`, `_scientific_gates:1448`): the 12 integrity
  and 4 scientific gate names/orders match TASK_PACKET §P6-F and P6_FREEZE §8/§9; labels
  `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` / `..._NOT_CONFIRMED` / `BLOCKED` with failing
  gate names in frozen order; the candidate label additionally requires the frozen
  640-pair shape (`:1450-1452`), so a tiny smoke can never emit it.
- **Forbidden audit**: zero matches for the whole FORBIDDEN_MARKERS list in the module;
  imports are exactly stdlib (`argparse`, `hashlib`, `json`, `sys`, `time`,
  `dataclasses`, `numbers`, `pathlib`, optional POSIX `resource`), numpy and the
  accepted NB-Polar modules; only RNG use is `np.random.default_rng(stream_seed)`
  (`:2061`); no `open(`; the only writes are the five files under the explicitly passed
  output root, created after all computation (`:2225-2238`).

## 5. Tests — PASS

Commands (pinned interpreter, fresh `/tmp` basetemps, `PYTHONDONTWRITEBYTECODE=1`):

- `pytest comparison_bench/tests/test_nbpolar_adaptive_l1.py -q -p no:cacheprovider
  --basetemp=<fresh>` → **15 passed** in 8.19 s (freeze recorded 15 / 8.20 s).
- `pytest 'comparison_bench/tests/test_nbpolar_*.py' -q -p no:cacheprovider
  --basetemp=<fresh>` → **216 passed** in 100.95 s (15 new + 201 predecessors; freeze
  recorded 216 / 104.28 s).

Test-file inspection (1003 lines, 15 `test_*`) confirms the P6-D coverage:
nested-set construction and accepted `D1(45)` identity (`:191`); level restart /
no-state-reuse with instrumented decoder and tag seam — original-metric object identity,
three distinct freshly gathered L2 objects, per-level distinct tag seeds equal to the
frozen derivation (`:215`); tag accept / one-level advance / terminal `verify_failed` /
tag-collision `undetected` (`:263`); nonterminal vs terminal impossible and
other-exception fail-closed with exact accounting (`:298`, `:429`); label assembly and
static endpoint (`:345`); truth-isolation sentinel and input invariance (`:383`);
per-class accounting at every termination class (`:429`); recount and tamper detection
including malformed-event fail-closed (`:514`); paired block identity and same-sample /
one-P1-metric proof (`:575`); tiny five-file scalar-only schema, gate booleans and
refusals (`:629`, `:750`); resource-abort and truth-leak gate paths (`:845`); frozen
constants/refused set/fresh test seeds and command byte-parts (`:883`); entropy and
`p2_maxdiff` conventions (`:946`); forbidden-marker + import-time-effect scan in a fresh
interpreter with temp cwd (`:957`).

Production-invocation rule: every runner call uses temp roots and fresh test seeds
`2026091560..2026091566` with master `2026101560` only (grep across all call sites); the
single `main()` call uses banned seed `2026091510` to prove the pre-decoder refusal path
and creates nothing. The frozen streams appear only as literal assertions of module
constants / the command string (lines 6, 884, 933); the frozen masters do not appear
anywhere in the worktree (`rg "202610155[0-4]"` → zero). `default_rng(<frozen>)` is
asserted absent from the test source.

## 6. Truth boundary and provenance — PASS

- L1 provenance is `PRIOR_ONLY` at every executed stage, built only from Bob
  (`prior.build_p1_metrics`); L2 provenance is `CANDIDATE_CONDITIONED`, gathered from
  Bob + the hard L1 candidate (`prior.gather_p2_metrics`); the gate asserts both strings
  and the truth-isolation sentinel result (`_integrity_gates:1406-1416`).
- No truth/oracle value enters an undisclosed operational metric, decision or tag seed:
  tag seeds derive only from the public master (stream+10000) and arm/block/level; the
  candidate label is decoder output; the only truth uses are the four permitted.
- The forbidden-marker/import audit passes independently: zero marker matches, only
  `default_rng`, no import-time I/O (fresh-interpreter test in a temp cwd leaves it
  empty), no `open(`.

## 7. Bounded re-measurement (tiny injected smoke) — PASS

No gate seed was used. Non-frozen seeds `2026091599` / `2026091598`, temp roots under
`/tmp/opencode/p6_review/`:

- exactly five files: `frozen_plan.json`, `per_block_paired_outcomes.json`,
  `transcript_accounting.json`, `aggregate_summary.json`, `report.md`;
- all 12 integrity gates present and true; 4 scientific gates present; label
  `ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED` (2/4-pair shape; `shape_is_frozen_640`
  false); `integrity_all_pass=true`; attempt metadata 1/0/1/0;
- every arm record is scalar-only (25 keys, no arrays); independent per-record
  arithmetic found zero mismatches and recount == incremental with `mismatch_count=0`;
- 4-pair run: in-run `wall_s=0.59856` → `0.14964 s/pair`, projected **≈ 96 s** for 640
  pairs; whole-process wall 2.78 s for 4 pairs → worst-case linear projection
  **≈ 445 s**, ≥ 8× inside the 3600 s cap; peak RSS 150 MB, ≥ 13× inside the 2 GiB cap;
- the same CLI ran under `ulimit -v 2097152` (exit 0, five files), so the external
  virtual-memory envelope of the frozen command is exercised by the module.

## 8. Scope and premises — PASS

- `git status --porcelain` = 59 entries (16 modified, 43 untracked). The
  P6-attributable set is exactly the declared one, by content and mtime (packet window
  ≈ 20:42–21:11): packet docs (20:42–21:10), `adaptive_l1.py` (20:59, new),
  `test_nbpolar_adaptive_l1.py` (21:06, new), `__init__.py` export (21:07, adds only the
  `adaptive_l1` import block and its `__all__` names), `specs/nbpolar-phase4-p6/spec.md`
  (20:52, new), `tasks.md` P6 section (20:52), STATUS (20:52); plus the ordinary
  milestone `CURRENT_TASK.md` / `docs/nbpolar/DOCUMENT_INDEX.md` touched in the
  packet-creation second (20:42:29).
- All other dirty entries are predecessor state with mtimes ≤ 20:17 (P3 empirical files
  ≤ 01:33, P4/P5/P6-R1 artifacts, docs ≤ 18:20). No `methods/nbpolar_adaptive_l1.py`
  (checked absent: the unchanged single-layer adapter does not admit this statistic).
- Accepted dependencies untouched: `two_layer.py` (12:59), `penalty_gate.py` (17:14),
  `incremental.py` (10:50), `protocol.py`/`two_layer_rate.py` (02:13/12:12),
  `algebra/prior/sc/construction/shared` (2026-09-12) — all before the P6 session and
  not modified.
- X04/X05 read-only design inputs untouched (X05 `results.json` 8532497 B, mtime 20:17,
  before the session; X05 confirms the S22 `[45,60,72,112]` frontier and the frozen
  `5*(K_j+140)+64*j` / `2623*j` accounting). No predecessor evidence root shows a
  session-window mtime; `results/` and `outputs_comparison/` clean.
- HEAD `ab173f2a...` unchanged since 2026-09-12; no commit/staging; no new untracked
  entries appeared during this review (59 before and after; repo `.pyc` caches predate
  the review and no tracked file changed).

## Complete frozen record

| field | frozen value |
|---|---|
| point/model | GF32 (primitive polynomial 37, alpha 2, natural order), N=256; `epsilon1=0.05`; strong `epsilon2(u1)=0.02+0.36*u1/31`; injected `P(B\|A)=Ph*Pl`; column dev `3.774758283725532e-15`, `p2_maxdiff=0.34875000000000267`, floor 0.30 |
| D sets | `D1=[45,60,72,112]` worst-first nested prefixes of `analytic_order(0.05,256)`; `D2=analytic_order(0.20,256)[:140]`, disclosed once per arm/block |
| streams | 2026091550, 2026091551, 2026091552, 2026091553, 2026091554; 128 blocks each; 640 paired blocks |
| masters | stream+10000 = 2026101550..2026101554; SHA-256 domain-separated per arm/block/level; public control, never persisted |
| command | the three-line TASK_PACKET/P6_FREEZE/module-identical WSL command (byte-identical, parses to the frozen point) |
| attempt point | first scientific SC call: stream 2026091550, block 0, static L1; `attempts_allowed 1`, `attempts_used 0` |
| budget | 2 GiB (`ulimit -v 2097152`), 3600 s (`timeout 3600` + internal cap) |
| output root | `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/` — ABSENT at review open and close |
| schema | exactly five files: `frozen_plan.json`, `per_block_paired_outcomes.json` (640 scalar records), `transcript_accounting.json`, `aggregate_summary.json`, `report.md` |
| integrity gates (12) | pairing_coverage_complete; stream_block_identity_exact; result_buckets_disjoint_exhaustive; d1_exactly_nested_and_d2_disclosed_once; provenance_and_truth_isolation_complete; undetected_zero; nonfinite_zero; resource_abort_zero; transcript_recount_mismatch_zero; tag_feedback_public_control_accounting_and_union_bound_exact; wall_rss_within_frozen_limits; attempt_seed_accounting_exact |
| scientific gates (4) | static_exact_at_least_620_of_640; adaptive_exact_equals_static_exact; paired_adaptive_only_zero_and_static_only_zero; leakage_100_adaptive_le_85_static |
| labels | `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` (all gates) / `ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED` (integrity only) / `BLOCKED` (any integrity failure, failing names in frozen order) |
| accounting | key-dependent `5*(K_j+140)+64*tag_invocations`; public seed `2623*tag_invocations`; feedback 1 bit/invocation; public control = seeds+feedback; union bound `min(1,tags*2^-64)`; fully invoked 989/1064/1124/1324; static 1324 |
| scope | synthetic N=256 single-point mechanism evidence only; no real data/FER/efficiency/key rate/qualification/promotion/commit/push |

## Findings

**Blocking issues: none.**

Non-blocking suggestions (no repair required before execution; record only):

- **N-1** `adaptive_l1.py:1433-1436`: `wall_rss_within_frozen_limits` passes when
  `rss_bytes is None` (Windows native has no `resource`). The frozen command is WSL with
  `resource` available (`RSS_LIMIT_BYTES` enforced in all verified runs), so this cannot
  weaken the authorized execution.
- **N-2** `adaptive_l1.py:1402-1404`: the `d1_exactly_nested_...` gate also asserts
  every static `termination_k1 == 112`, so in an internal-timeout run the
  `BLOCKED(<earliest gate>)` attribution can name this gate before `resource_abort_zero`.
  Both are integrity failures and the run is blocked either way; expected abort count is
  zero.
- **N-3** `P6_FREEZE.md:229-231` says on expiry "the remaining blocks are
  `resource_abort`"; the implementation aborts the remaining blocks of the current
  stream and then stops (later streams have no rows, so `pairing_coverage_complete`
  fails first). Outcome is still BLOCKED with all five files written. Documentation
  nuance only.
- **N-4** `adaptive_l1.py:1431`: the union-bound gate term compares the value to a
  recomputation from the same recount (tautological); the substantive checks are the
  event accounting sums and `2623`/`1` per-event control widths, which are exact.
- **N-5** `run_adaptive_arm:624,746`: after a later nonterminal rejection the in-memory
  `candidate`/`high_hat` may still reference the last successful stage. It is never read
  for L2/tag after a rejection and is excluded from persisted records
  (`_arm_record:1097`), so no disclosure or persistence impact.
- **N-6** The truth-isolation protected set excludes the disclosed-value copies
  (`u1_disclosed`/`u2_disclosed`); they are `copy=True` truth copies and disclosed by
  design, so no aliasing risk.

## Closure statements

- The real 640-pair gate command was **not run**; no scientific SC call was executed
  with any frozen seed; the gate root remains **ABSENT**.
- `STATUS.yaml` still reads `attempts_used: 0` and `independent_pre_execute: pending`
  (the main thread owns the PASS update).
- No file outside `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/
  PRE_EXECUTE_REVIEW.md` was written by this review; no commit or push; predecessor
  roots and X04/X05 untouched.
- This PASS permits the operator to run the single frozen command exactly as frozen.
  Per AGENTS.md §4.1 it does not grant acceptance, and any Pre-RESULT issue still blocks
  solidification.

## Review commands (condensed)

```
git status --porcelain; git rev-parse HEAD; git grep -E "202609155[0-4]" HEAD
rg --no-ignore -g '!.git' -e "202609155[0-4]" -e "202610155[0-4]" .
python /tmp/opencode/p6_review/verify.py        # command identity, banned superset, D1/D2, table, entropy, seeds
python /tmp/opencode/p6_review/verify2.py       # accepted D1(45), attempt-point instrumentation, refusal bomb
python /tmp/opencode/p6_review/verify3.py       # parser parse of the exact command; per-record accounting; union bound
python /tmp/opencode/p6_review/verify4.py       # refused-set equality (65 == 65)
pytest comparison_bench/tests/test_nbpolar_adaptive_l1.py -q -p no:cacheprovider --basetemp=<fresh>   # 15 passed
pytest 'comparison_bench/tests/test_nbpolar_*.py' -q -p no:cacheprovider --basetemp=<fresh>           # 216 passed
python -m ...adaptive_l1 --n 256 --epsilon1 0.05 --profile strong --k1-levels 45 60 72 112 \
  --k2 140 --seeds 2026091599 --blocks-per-seed 4 --out-dir /tmp/opencode/p6_review/smoke4          # five files, all gates true
( ulimit -v 2097152; python -m ...adaptive_l1 ... --seeds 2026091598 --blocks-per-seed 2 \
  --out-dir /tmp/opencode/p6_review/smoke_ulimit )                                                   # exit 0 under the frozen envelope
```
