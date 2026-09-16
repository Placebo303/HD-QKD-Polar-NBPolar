# Independent Pre-EXECUTE review — NBPOLAR-PHASE6-FIXED-INCREMENTAL

Reviewer session: 2026-09-13 (WSL). Role: independent backup reviewer
(`reviewer-go`, deepseek-v4.1-flash); no code under review was written by this
session. Read-only except this file. The real paired-dev-gate command was NOT
run; no Model-F artifact, real data, or the immutable Phase 5 evidence root was
read. No commit or push was made.

**Verdict: PASS** (execution may proceed after main-thread authorization; all
12 required checks PASS; 4 non-blocking findings, no blocking issues.)

Scope of evidence: repository `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`,
HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged; `git reflog` shows
only the clone entry). Pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3,
pytest 9.1.1). Real output root
`.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`
verified ABSENT before and after this review.

---

## Blocking issues

None.

## Non-blocking findings

- **F-1 (environment, evidence accuracy).** Under the frozen wrapper
  `ulimit -v 2097152`, this WSL2 kernel corrupts
  `resource.getrusage(RUSAGE_SELF).ru_maxrss`: it returns a constant
  `1193268 KiB` (~1.14 GiB) from process start while the true high-water mark
  (`/proc/self/status VmHWM`) is ~105 MB. Reproduced 3× under ulimit and 0×
  without it (`rss_module_check.py`: without ulimit ru_maxrss 11.6→104 MB;
  with ulimit constant 1193268 from the first read). Consequence:
  `aggregate_comparison.json.rss_bytes_peak` (written by
  `incremental.py:901-904, :1331`) may persist ~1.22 GB instead of the true
  peak. **No hard gate and no candidate rule uses RSS** (verified: `rss` is not
  referenced in `_candidate_gates`, `incremental.py:1047-1185`), the plan's
  `rss_bytes_max` 2 GiB is not compared anywhere, and the true VmPeak under the
  frozen ulimit measured 611-628 MB, well inside the envelope. Advisory for
  Pre-RESULT: treat `rss_bytes_peak` as environment-dependent evidence, not a
  memory incident. Not repairable under the freeze (no flag/code change is
  permitted after freeze).
- **F-2 (test quality, vacuous assertion).**
  `comparison_bench/tests/test_nbpolar_incremental.py:766` calls
  `orig_p6_seed_tag(seen, original_p6_tag) == orig_p5_seed_tag(seen, original_p5_tag)`,
  but `orig_p5_seed_tag` (`:802-803`) ignores its second argument and recomputes
  with `original_p6_tag` on the P6 bits/seed, so both sides are the same P6
  evaluation. The intended P5-vs-P6 tag comparison is not exercised by that
  line. The surrounding checks (equal message bits, both 2623-bit seeds, seeds
  differ by derivation) do cover the frozen claim; no acceptance property
  depends on the vacuous line.
- **F-3 (doc precision).** `P6_FREEZE.md:272-274` lists the stdlib imports of
  the frozen modules as `argparse, hashlib, json, sys, time, dataclasses,
  numbers, pathlib` but omits `resource` (`incremental.py:100-103`, a stdlib
  import in a try/except used for RSS reporting). Documentation-only.
- **F-4 (evidence nit).** `_abort_pair` (`incremental.py:907-921`) writes
  `paired_match: True` for never-executed `resource_abort` pairs. This is
  vacuous (there is no metric to compare) and cannot produce a wrong
  conclusion because the asymmetry is visible per arm and
  `paired_coverage_complete` fails, but a future reader could misread it.
  Optional clarification in the report text at next touch.

---

## Numbered checklist (PASS/FAIL with exact commands and raw evidence)

### 1. STATUS edit exactness — PASS

Command: `cat .workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/STATUS.yaml`.

Exactly the seven authorized flags are `true`: `documentation_authorized`,
`implementation_authorized`, `synthetic_exploration_authorized`,
`decoder_execution_authorized`, `development_gate_authorized`,
`rate_adaptation_authorized`, `phase6_authorized`; all other authority flags
are `false`: `artifact_read_authorized`, `raw_data_authorized`,
`real_data_authorized`, `dev_eval_authorized`, `scl_authorized`,
`phase7_authorized`, `scientific_promotion`. `attempts_allowed: 1`,
`attempts_used: 0`. `state:
AUTHORIZED_FOR_AUTONOMOUS_PHASE6_FIXED_INCREMENTAL`, `next_gate:
IMPLEMENTATION_AND_SYNTHETIC_QUALIFICATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW`
— consistent with `AUTHORIZATION_PROMPT.md` and `P6_FREEZE.md` (the
authorization pins only the seven flags and keep-others-false; the whole queue
directory is untracked so no git diff baseline exists). 20 lines, no extra
flags.

### 2. Frozen schedule and nesting (P6-A01/A02) — PASS

Command: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
/tmp/opencode/p6rev/schedule_check.py` (recomputes from scratch via
`analytic_order(0.05, 256)`).

Raw: `order[:45] = [0,1,2,4,8,3,16,5,32,6,9,10,64,17,12,128,18,33,7,20,34,24,
11,65,36,66,40,13,129,68,19,14,48,130,72,21,132,80,22,35,136,96,25,144,26]`.

- `D_1 (K=29) = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,20,24,32,33,34,36,
  40,64,65,66,128,129]` — matches `P6_FREEZE.md:48-49`.
- `D_2 = D_1 + [14,19,48,68]`; `D_3 = D_2 + [21,72,130,132]`;
  `D_4 = D_3 + [22,35,80,136]`; `D_5 = D_4 + [25,26,96,144]` — match
  `P6_FREEZE.md:51-54`.
- Strict set inclusion at every step: `True` (|diff| = 4 each); full-order
  prefix equality `True`; `flat new[0..4]` sizes `[29,4,4,4,4]`, all 45
  distinct; `D_5 == static_disclosure_coordinates(256,45)` → `True`
  (accepted Phase 5 static K=45 set).
- `build_nested_schedule()` returns prefix/nesting/disjoint flags all `True`
  and its sets and new-coordinate lists equal the from-scratch recomputation
  (`code schedule equals recomputation: True`).
- Persisted plan from a non-frozen smoke run: `new_coordinates` lengths
  `[29,4,4,4,4]`, `new[1] = [14,19,48,68]`, proof flags `True True True`.
- Only new coordinates are transmitted/accounted once: disclosure events carry
  `5*len(new_positions[level])` (`incremental.py:801-823`), sum = `5*45`; the
  decoder receives the cumulative `known_positions=D_i` with actual
  `U[D_i]` values (`incremental.py:392-401`). Spy evidence
  (`test_a02` + reviewer script): per-level positions `== D_i`, values
  `== polar_transform(x)[D_i]`, all-zero vectors round-trip as values (200
  random x over `D_5` yielded 281 zero-valued coordinates, transmitted
  literally).

### 3. Restart semantics (P6-A03) — PASS

Ran the shipped instrumentation test (part of the 17-test focused suite, see
§10). Independently re-ran a bounded injected scenario
(`/tmp/opencode/p6rev/restart_tag_check.py`, non-frozen seed 2026091551,
in-memory), instrumenting `incremental.sc_decode` to record every call's
metric/positions/values with all five levels forced to tag-mismatch:

Raw: `verify_failed levels_invoked 5 tags 5 feedback 4 key_bits 545 seed_bits
13115`; `decode calls: 5`; every recorded metric `==` pre-run snapshot `True`;
the same `logp` ndarray object was passed each time `True`; positions
`== cumulative D_i` `True` (`[29,33,37,41,45]`); values `== actual U[D_i]`
`True`; caller metric unmutated after the run `True`.

Code review confirms no carried state: each iteration calls
`sc_decode(logp_arr, field, alpha=2, known_positions=positions,
known_values=disclosed)` (`incremental.py:390-401`); the returned candidate is
copied and discarded on mismatch (`:424-439`); `sc_decode` is pure (new arrays
per call, `sc.py:188+`); no module-level mutable decoder state exists.

### 4. Tag/control semantics (P6-A04/A05/A06) — PASS

- Accept/reject-only: the only tag use is `tag_true == tag_hat`
  (`incremental.py:435`, `:586`); no ranking/sorting/selection/parameter
  change.
- Exactly one level advance on mismatch: the loop increments exactly by one
  (`:440`); forced accept at level 0..4 gave `decodes == match_level+1`,
  positions always `D_0..D_j` in order, `tags == j+1`, `fb == j`
  (`restart_tag_check.py` part B), key bits `209,293,377,461,545` = `5*K_j +
  64*(j+1)`.
- Final-level mismatch = `verify_failed`: forced all-level mismatch → outcome
  `verify_failed`, 5 tags, 545 bits.
- Matching non-exact = `undetected` via the documented seam: injected
  colliding tag + wrong decode → `undetected`, `exact False`, 1 tag; with the
  real tag the same wrong decode → `verify_failed` (5 levels), never success.
  Production default confirmed: `inc.toeplitz_tag is shared.toeplitz_tag` →
  `True`, default `tag_fn=None` resolves to it in both
  `run_incremental_block` and `run_static_comparator_block`.
- Fail-closed decode: injected `NumericNonfiniteError` at each level 0..4 gave
  `decode_failed` at that level with `decodes = i+1`, zero tag calls at/after
  the failing level (`tag_calls = 2*i` for the forced-mismatch prefix), and
  key bits `145,229,313,397,481` = `5*K_i + 64*(i-1)` — all matching
  `incremental_record_consistent`. NaN decision marginals likewise stop after
  the first level.

### 5. Seeds — PASS

- `git grep -n 2026091340 HEAD` and `git grep -n 2026091341 HEAD`: both return
  no matches (rc=1), recorded before and re-verified now.
- Worktree grep over accepted sources/docs/dirs excluding the new Phase 6
  files: only `openspec/changes/formal-ir-nbpolar-phase6-fixed-incremental/
  design.md:60` carries the literals (a declared Phase 6 artifact). READ-ONLY
  grep of the sibling `../HD-QKD_Polar_Comparison` (excluding its `results/`
  and the Phase 5 evidence root) returned no matches. The Phase 5 consumed
  seeds 2026091317/2026091318 and the Phase 1-5 ranges are disjoint.
- Validator refuses exactly the declared 22 values
  (`BANNED_RUN_SEEDS`, `incremental.py:124-128`): `range(2026091200,2026091214)`
  ∪ `range(2026091314,2026091321)` ∪ `{2026091330}` = 22; sample refusals
  2026091317/18, 2026091330, 2026091314, 2026091320, 2026091213 all raise
  `ValueError: ... banned (consumed by Phase 1-5)`; 2026091340/41/42 pass
  validation.
- Derivation rule deterministic and independent: manual SHA-256 re-implementation
  (`"nbpolar-p6-toeplitz-seed:2026091341:<arm>:<block_index>:<level>:<counter>"`,
  MSB-first unpack, truncate to 2623) equals the implementation for 2 arms ×
  5 blocks × levels; 36 sampled seeds (arms × blocks 0-5 × levels) are
  pairwise distinct; repeat call identical; length `10*256+63 = 2623`.
- Raw seed bits never persisted: output-smoke scan found no `seed_hex`, no
  binary stream ≥300 chars of 0/1, no seed vectors; only the master seed
  integer and the derivation template appear in `frozen_plan.json`.

### 6. Paired runner — PASS

- One generator draw per block shared by both arms in the same order:
  `rng = np.random.default_rng(seed)` (`incremental.py:1217`), one
  `generate_erasure_block(rng, ...)` per loop iteration (`:1234`), then the
  static arm and the incremental arm on the same arrays (`:1239`, `:1241`);
  `paired_match` recorded per block (`:1252-1262`). Verified by test A10 and
  by code review.
- Static comparator vs accepted Phase 5 semantics: reviewer cross-check of
  12 + 30 injected blocks (`/tmp/opencode/p6rev/accounting_check.py`,
  `final_checks.py`) — 0 mismatches in outcome, exact, pre/post symbol/bit
  error counts and key/public bit counts; injected impossible disclosed value
  gives `decode_failed`/`ImpossibleDisclosedValueError`/225 bits in both.
  Message bits equal and seeds differ by derivation (checked: `True` / `True`;
  P6 seed equals `block_toeplitz_seed_bits`, P5 seed equals P5 derivation).
- In-run comparator, Phase 5 root never read: the module contains no read I/O
  at all (`Path(` usage only at `:1202`; two `write_text` calls at `:1483`,
  `:1553`), no sibling paths, and the forbidden-marker scan is clean.

### 7. Accounting and gates — PASS

Non-frozen smoke (`accounting_check.py`, 12 blocks, temp root):
per-arm literal event recount equals the incremental totals for
key-dependent bits, public-control bits, tag invocations and feedback
invocations (static 3468/31476/12/0; incremental 2316/23607/9/0;
mismatch_count 0 both arms). Per-block formula check: no violations for either
arm; feedback relation `tags-1` (tag-terminated) / `tags` (decode_failed) holds
for every record.

- `key_dependent_bits = 5*K_j + 64*j` (accepted/terminal level j 1-based);
  `5*K_i + 64*(i-1)` on `decode_failed` at level i; 0 on `resource_abort` —
  verified against per-block records and against injected fail levels
  (§3/§4).
- Independent literal recount is a separate literal walk
  (`recount_transcript`, `:860-878`) from the incremental counter
  (`_incremental_totals`, `:881-891`), compared by `mismatch_count` and by
  the `recount_zero_mismatch` / `invocation_universe_equals_recount_both_arms`
  gates.
- Feedback control: 1 public bit per advance with a separate invocation counter
  (`FEEDBACK_CONTROL_BITS=1`, `:132`, `:440-441`, `:457-458`); per-block
  relation verified; `feedback_control_counted` gate checks both.
- Union bound `min(1.0, total_tag_invocations * 2**-64)`
  (`shared.verification_union_bound`); smoke `total = 1.1384122811097797e-18`
  equals `min(1, n*2^-64)` and the recount count.
- 5% rule integer-exact: `incremental_key*100 <= 95*static_key`
  (`:1124-1127`), persisted as `lhs/rhs` (`:1386-1387`); smoke
  `lhs=231600 <= rhs=329460`.
- Wilson: `wilson_lower_bound` from Phase 5 with `z=1.6448536269514722`;
  Decimal-60 recomputation matched at (0,300), (285,300) → 0.9249844882028562,
  (300,300) → 0.9910621278248719, (4,12), (11,12) with max delta 1.1e-16.
- All 18 gates present with the frozen thresholds and precedence
  (`_candidate_gates`, `:1109-1173`): frozen_plan_identity (seed 2026091340,
  300, N=256, eps 0.05, K=(29,33,37,41,45)); paired_identical_blocks;
  outcome_buckets_disjoint_exhaustive_both_arms; paired_coverage_complete;
  incremental_undetected_zero; incremental_exact_ge_285 (>=285);
  incremental_wilson_lower_ge_0_90 (>=0.90);
  equal_attempted_denominators; incremental_avg_key_dependent_le_95pct_static;
  frozen_order_nesting_and_schedule_consistency;
  invocation_universe_equals_recount_both_arms; union_bound_consistent;
  recount_zero_mismatch; truth_leak_zero; nonfinite_zero;
  resource_stop_preregistered; feedback_control_counted;
  public_control_counted. Candidate label requires all 18 (`:1427-1429`).
  Outcome precedence `resource_abort > decode_failed > verify_failed > exact >
  undetected` is realized by control flow and persisted
  (`frozen_plan.outcome_precedence`).

### 8. Exact command, root, budget — PASS

Frozen command parses exactly (`cli_budget_check.py`, parser only; no run):
`PARSED: paired-dev-gate 2026091340 300
.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate`;
unknown flags (`--k 45`) and wrong mode (`dev-gate`) are refused with rc 2.
The `python -m` invocation works (documented cosmetic `runpy` RuntimeWarning
emitted; rc 0 on `--help`; root still absent afterwards).

Frozen command (P6_FREEZE.md:255-258):
```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental --mode paired-dev-gate --run-seed 2026091340 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate
```
Root absent now: `ls` → No such file or directory. Attempt-consumption point
stated: first scientific `sc_decode` (static comparator arm, block 0); no
rerun/seed change/tuning on failure (P6_FREEZE.md:261-264; plan and aggregate
fields `attempt_consumption_point` / `attempt_consumption`).

Budget re-measure (non-frozen seeds, temp roots, under `ulimit -v 2097152`):
50-block probe seed 2026091399 → total wall 1.586 s, per-paired-block max
0.06405 s, median 0.0314 s, projected 300-block mean 9.52 s; 60-block probe
seed 2026091571 → total wall 1.834 s, per-block max 0.0465 s, p90 0.0314 s,
projected 300-block mean 9.09 s. Margins: per-block soft cap 10 s (~156×
observed max), total 600 s (~330× observed total), timeout 1200 s, VmPeak
611-628 MB vs 2 GiB virtual limit. The frozen ulimit did not abort any probe.

### 9. Output schema — PASS

Smoke root (12 blocks): exactly five files `frozen_plan.json`,
`per_block_paired_outcomes.json`, `transcript_accounting.json`,
`aggregate_comparison.json`, `report.md`. All JSON nodes are
`null|bool|int|float|str` (recursive scalar check `True`); no `seed_hex`,
`u_hat`, `x_hat`, `known_values`, `labels_hat`, decoded keys, raw seed bits or
coordinate value lists; per-block records carry only scalar fields plus the arm
scalars. `frozen_plan.json` persists positions (D_sets/new_coordinates), not
values; transcript entries persist only counts, ids and `seed_bit_length`.
Refusal path: calling `run_paired_dev_gate` on an existing root raised
`FileExistsError` with decoder call counter `0`; a banned seed raised
`ValueError` with the target root still absent and decoder call counter `0`
(`refusal_check.py`).

### 10. Tests — PASS

Commands (pinned interpreter, `-p no:cacheprovider`, fresh `/tmp` basetemps):
- `... -m pytest -q -p no:cacheprovider --basetemp=/tmp/opencode/p6rev_focused_<pid> comparison_bench/tests/test_nbpolar_incremental.py` → **17 passed** in 7.99 s.
- `... -m pytest -q -p no:cacheprovider --basetemp=/tmp/opencode/p6rev_full2_<pid> comparison_bench/tests/test_nbpolar_*.py` → **153 passed** in 68.98 s (17 + 136, as expected).

Coverage inspection of the new file: A01 nesting/analytic prefixes; A02
incremental-only + zero round-trip + cumulative counting; A03 restart
instrumentation (metric identity, no hidden state, second-run equality); A04
one-level advance, no selection/skip/retry; A05 injected equal tag →
`undetected` never success (record + gate); A06 fail-closed decode/nonfinite
and final-mismatch `verify_failed`; A07 cumulative accounting + independent
literal recount + record/transcript tamper detection; A08 seed derivation,
distinctness, per-verification public-seed/control counting, union bound; A09
disjoint/exhaustive buckets, truth-leak sentinel, nonfinite gates; A10 paired
identity, one generator draw per block, mutating-arm detection; A11 signature
stability, comparator equivalence with `protocol.run_static_block`, decode
failure equivalence, embedded Phase 5 predecessor suite (16 tests, asserted
≥16); A12 tiny exhaustive n=8/K=(2,3,4) scheduler, frozen constants, no CLI
tuning knobs. Extra tests: refusals, five-file scalar schema, resource abort,
adapter round-trip/refusals, forbidden-marker/import-I/O/no-global-RNG scan.
The reserved seeds 2026091340/2026091341 appear only in constant assertions
(`:818-819`, `:887`) and are never used as RNG seeds; tests use 2026091342-44
only. No forbidden markers in the two production sources (independent grep: 0
for `outputs_comparison, model_f, v72p2d5, parquet, ttbin, dev_seed, eval_seed,
benchmark, sibling, artifact, results/`).

### 11. Risk report (not a tuning action) — REPORTED, not a blocker

Bounded probes (non-frozen seeds, in-memory/temp): operator profile seed
2026091399 40 blocks (`P6_IMPLEMENTATION_NOTES.md` §6: incremental 3
`decode_failed`); reviewer re-run same seed 50 blocks (4 `decode_failed`); reviewer
fresh seed 2026091571 60 blocks (6 `decode_failed`). Combined 13/150 = 8.67%
(95% Wilson CI [5.13%, 14.26%]; one-sided 95% upper 13.2%). All failures are
at invoked level 1 (K=29) with error type `ImpossibleDisclosedValueError` ("a
disclosed U value has exact-zero SC conditional support"), i.e. the early
K=29 disclosure is too small to be decodable on those blocks; static K=45 had
1/40 + 0/50 + 0/60 failures. Accepted incremental blocks were `exact` (no
`undetected`, no `verify_failed`).

Projected impact on the frozen gates: at p̂=8.7%, expected incremental
failures 26/300 → exact ≈274 < 285, so `incremental_exact_ge_285` (and the
Wilson LB ≥ 0.90 depending on the exact count) is at substantial risk; at the
optimistic CI edge (5.1%) failures ≈15, borderline; at the pessimistic edge
(14.3%) ≈43. The 5% disclosure gate is not at risk (accepted blocks disclose
209-293 bits vs static 289; smoke saving fraction 0.332; decode-failed blocks
disclose only 145). Independent level-1 failure risk also matches the
operator's own observation. Per packet rules this is not a blocker and no
threshold, K, epsilon, N or seed may be changed; the single frozen attempt
remains the preregistered discriminator and may legitimately return
`BLOCKED(incremental_exact_ge_285)`.

### 12. Scope and premises — PASS

`git status --porcelain` matches the declared set exactly: modified
`formal_ir/nbpolar/__init__.py` (additive explicit Phase 5+6 exports only —
verified by `git diff`: pure additions, Phase 5 names unchanged); new
`formal_ir/nbpolar/incremental.py`, `methods/nbpolar_incremental.py`,
`tests/test_nbpolar_incremental.py`, the Phase 6 queue directory (STATUS,
P6_FREEZE, P6_IMPLEMENTATION_NOTES, four original packet files) and the Phase 6
OpenSpec directory (design.md carries the Rev note; all ten `tasks.md` boxes
unchecked); plus the pre-existing dirty Phase 4/Phase 5 artifacts unchanged
(same list at review start and end). Phase 5 files predate Phase 6 by mtimes
(`protocol.py` 02:13, `nbpolar_static.py` 02:00, `test_nbpolar_protocol.py`
02:10 vs 03:03-03:18 for P6 files) and all 136 predecessor tests pass. HEAD
unchanged (`ab173f2a...`, reflog only clone; no commit/push). `git status` for
`src/ experiments/ tools/ results/ comparison_bench/outputs_comparison` is
empty (0 entries). Sibling checkout used only as the pinned interpreter
read-only; P6 sources contain no `../` or sibling path references. Real output
root absent.

---

## Complete frozen record (for execution and Pre-RESULT)

- **Point**: GF32 polynomial basis, primitive polynomial 37, alpha 2, natural
  order, N=256, q-ary erasure epsilon=0.05; physical labels `32*x_hat`;
  Toeplitz message domain `10*N = 2560` bits; tag 64 bits; seed per
  verification `10*N+63 = 2623` bits.
- **Schedule**: `D_i = sorted(analytic_order(0.05,256)[:K_i])` for
  `K=(29,33,37,41,45)`; D_1 `[0,1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18,20,24,
  32,33,34,36,40,64,65,66,128,129]`; new coordinates `+[14,19,48,68]`,
  `+[21,72,130,132]`, `+[22,35,80,136]`, `+[25,26,96,144]`; D_5 = accepted
  Phase 5 K=45 set. Strict nesting, prefix match and disjointness flags all
  `True`.
- **Seeds**: run `2026091340`; Toeplitz master `2026091341`; both absent from
  HEAD, from accepted Phase 1-5 streams and from tests. Refused run seeds
  (22): `2026091200..2026091213`, `2026091314..2026091320`, `2026091330`.
  Per-arm/per-block/per-level derivation:
  `SHA-256("nbpolar-p6-toeplitz-seed:2026091341:<arm>:<block_index>:<level>:<counter>")`
  concatenated for counter = 0,1,... MSB-first, truncated to 2623 bits; arm ∈
  {static, incremental}; block_index 0-based; level 0-based (static 0,
  incremental 0..4). Public control, never persisted raw.
- **Command** (exact): see §8. **Output root**:
  `.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`
  — absent now; refusal before any decoder call.
- **Budget**: total wall 600 s internal; per-paired-block soft cap 10 s;
  external `timeout 1200`; `ulimit -v 2097152` (2 GiB virtual); plan
  `rss_bytes_max = 2147483648`; measured VmPeak 611-628 MB; observed per-block
  max 0.064 s / 300-block projection ~9.1-9.5 s.
- **Schema**: exactly five scalar-only files (`frozen_plan.json`,
  `per_block_paired_outcomes.json`, `transcript_accounting.json`,
  `aggregate_comparison.json`, `report.md`); no symbols/labels/disclosed
  values/decoded keys/raw seed bits/coordinate value lists.
- **Precedence**: `resource_abort > decode_failed > verify_failed > exact >
  undetected`.
- **Gates (18)**: frozen_plan_identity; paired_identical_blocks;
  outcome_buckets_disjoint_exhaustive_both_arms; paired_coverage_complete;
  incremental_undetected_zero; incremental_exact_ge_285 (>=285);
  incremental_wilson_lower_ge_0_90 (>=0.90); equal_attempted_denominators;
  incremental_avg_key_dependent_le_95pct_static; 
  frozen_order_nesting_and_schedule_consistency;
  invocation_universe_equals_recount_both_arms; union_bound_consistent;
  recount_zero_mismatch; truth_leak_zero; nonfinite_zero;
  resource_stop_preregistered; feedback_control_counted; public_control_counted.
- **Formulas**: `key_dependent_bits = 5*K_j + 64*j` (terminal level j);
  `5*K_i + 64*(i-1)` on decode_failed at level i; 0 on resource_abort;
  union bound `min(1.0, total_tag_invocations * 2**-64)`;
  5% integer rule `incremental_total*100 <= 95*static_total`;
  one-sided 95% Wilson with `z = 1.6448536269514722`, denominator = attempted
  (resource_abort excluded).
- **Attempt consumption**: first scientific `sc_decode` call (static
  comparator arm, block 0) consumes attempt 1/1; failure is terminal (no
  rerun, no seed change, no tuning).

## Closure statements

- Real paired-dev-gate command was NOT run; no scientific `sc_decode` with
  seed 2026091340 was ever invoked.
- `attempts_used` is still `0`.
- The real output root is still ABSENT.
- Model-F artifact, real data and the immutable Phase 5 evidence root were not
  read; no frozen/sibling/results/outputs_comparison path was written.
- No commit or push; HEAD unchanged.
- Pre-EXECUTE disposition: **PASS** — execution of the frozen command is
  unblocked once the main thread supplies the authorization; Pre-RESULT
  recomputation remains mandatory.
