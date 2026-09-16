# Independent Pre-RESULT review — NBPOLAR-PHASE6-FIXED-INCREMENTAL

Reviewer session: 2026-09-13 (WSL), fresh independent reviewer (`reviewer-go`
backup, deepseek-v4.1-flash). Did not write the code, freeze the plan, or run
the gate. Read-only except this file. The frozen paired command was **NOT
rerun** (attempt 1/1 already consumed). No Model-F artifact, real data or the
Phase 5 evidence root was read or written. No commit or push.

**Verdict: PASS_WITH_COMMENTS** — the evidence root is self-consistent, the
recomputed numbers match the persisted artifacts, and the observed candidate
failure is a genuine, correctly reported gate failure (not an evidence or
implementation defect). Comments are closeout actions only; no blocking issue.

Output root reviewed:
`.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`
HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e`; pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3,
pytest 9.1.1).

Commands used (scripts in `/tmp/opencode/p6_review/`, in-memory/temp only):

```
PYTHONDONTWRITEBYTECODE=1 <pinned-python> /tmp/opencode/p6_review/recompute.py
PYTHONDONTWRITEBYTECODE=1 <pinned-python> /tmp/opencode/p6_review/plan_ident.py
PYTHONDONTWRITEBYTECODE=1 <pinned-python> /tmp/opencode/p6_review/mechanism.py
<pinned-python> -m pytest comparison_bench/tests/test_nbpolar_incremental.py -q -p no:cacheprovider --basetemp=/tmp/opencode/pytest_p6_review_focused
<pinned-python> -m pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider --basetemp=/tmp/opencode/pytest_p6_review_full
```

---

## 1. Output root: exactly 5 files, scalar-only

Files (mtime nanoseconds, single generation — all within 03:33:34.733–.755,
dir 03:33:34.753):

| file | bytes | mtime |
|---|---|---|
| frozen_plan.json | 6640 | 03:33:34.733631100 |
| per_block_paired_outcomes.json | 470477 | 03:33:34.744807500 |
| transcript_accounting.json | 1810 | 03:33:34.748987400 |
| aggregate_comparison.json | 4822 | 03:33:34.751991000 |
| report.md | 2314 | 03:33:34.754992500 |

Deep recursive type audit over all four JSON files: every node is
`null | bool | int | float | str`; zero non-scalar nodes. No forbidden private
tokens (`seed_hex`, `u_hat`, `x_hat`, `known_values`, `labels_hat`, `decoded`,
`raw_seed`); zero `NaN`/`Infinity` tokens.

Top-level key inventory:
- `frozen_plan.json` (24 keys): accounting, attempt_consumption_point, budget,
  channel, created_utc, disclosure_rule, epsilon, field, label_domain, mode, n,
  order, outcome_precedence, planned_blocks, protocol, q, refused_run_seeds,
  repository, restart_rule, run_seed, schedule, static_comparator, toeplitz,
  union_bound.
- `per_block_paired_outcomes.json`: `n_blocks`=300, `blocks`=300 records; each
  record has 8 keys (block_index, paired_match, metric_wall_s, static_wall_s,
  incremental_wall_s, paired_wall_s, static, incremental) and each arm record
  has the same 21 scalar keys (19 frozen schema keys + arm + block_index).
  All 300 record/arm key sets identical.
- `transcript_accounting.json`: static/incremental blocks with keys
  incremental, mismatch_count, recount, transcript_sha256; plus
  static_event_count, incremental_event_count, union_bound, public_control.
- `aggregate_comparison.json` (26 keys; all groups listed in freeze §9.4).
- `report.md`: bounded prose + tables, no vectors.

## 2. Paired identity

- `paired_match` true for all 300 records (300 nested records, block_index
  0..299 contiguous).
- Code path (`incremental.py:1227-1246`): one `np.random.default_rng(seed)`
  (line 1217) and exactly one `generate_erasure_block(rng, ...)` per block;
  the only `rng` uses in the module are those two lines. Static arm runs first
  on the shared `x`/`logp`, then the incremental arm on the same arrays; both
  snapshot-compare `x` and `logp` after their arm and set `paired_match =
  static_ok and incremental_ok`.
- Both arms copy their inputs (`_validate_common` / `astype(..., copy=True)` in
  `sc_decode`), and the tool tests (A03/A10) spy that every invoked level
  receives the original metric and that an injected mutating arm flips the
  gate. Re-ran those tests: pass.
- `paired_identical_blocks` gate recomputed true.

## 3. Outcome totals (recomputed from `per_block_paired_outcomes.json`)

| bucket | static | incremental |
|---|---|---|
| exact | 298 | 271 |
| undetected | 0 | 0 |
| verify_failed | 0 | 0 |
| decode_failed | 2 | 29 |
| resource_abort | 0 | 0 |
| sum | 300 | 300 |

- Disjoint/exhaustive over 300 per arm: yes (both sums exactly 300).
- Accepted-level histogram: static {0: 298}; incremental {0: 263, 1: 2, 2: 4, 3: 2}
  (271 accepted in total; no acceptance at level 4).
- Decode-failure level histogram: static {0: 2}; incremental {0: 29}.
- Error types: 100% `ImpossibleDisclosedValueError` (static 2, incremental 29),
  all at level 0.
- `undetected` = 0 both arms; no record has `exact=true` with a non-exact
  outcome or vice versa (0 folding contradictions). No decode_failed /
  verify_failed / undetected is folded into exact.

## 4. Incremental exact, Wilson, failing gates

- Incremental exact = **271/300 attempted** (coverage 1.0).
- Wilson one-sided 95% LB, independent Decimal (60-digit) recomputation with
  `z = 1.6448536269514722`, `n=300`:
  `0.871559783754294351530176653684640267297671367928419275005094`.
  The float-formula recomputation reproduces the persisted value exactly:
  `0.8715597837542944` (identical to `aggregate.incremental.wilson.lower_bound`;
  the 1-ulp difference vs the Decimal value is normal float arithmetic, not a
  defect). Static `298/300 -> 0.9800565738801275` also reproduced.
- Failing gates (of 18; 16 true / 2 false):
  - gate #6 `incremental_exact_ge_285`: observed **271** vs threshold **285**
    -> False (shortfall 14).
  - gate #7 `incremental_wilson_lower_ge_0_90`: observed **0.8715597837542944**
    vs threshold **0.90** -> False (shortfall 0.028440216245705648).
- Frozen gate ordering (P6_FREEZE §10, items 1..18): gates 1-5 are true, so the
  **earliest failing gate is #6 `incremental_exact_ge_285`**. The persisted
  JSON shows the two `false` flags only; `candidate` is `null` (recomputed:
  null). Required return label: `BLOCKED(incremental_exact_ge_285)`.

## 5. Disclosure accounting, public control, union bound, transcript recount

Per-block formula check over all 600 arm-blocks: **0 mismatches**.
- Static: exact/undetected/verify_failed = `5*45+64 = 289`; decode_failed =
  `5*45 = 225`; total `298*289 + 2*225 = 86572` (avg 288.573333333, exact
  288.5733333333333); tag invocations 298, seed bits `2623*298 = 781654`.
- Incremental: accepted level j -> `5*K_j + 64*(j+1)`; decode_failed level i
  -> `5*K_i + 64*i`. Totals `263*209 + 2*293 + 4*377 + 2*461 + 29*145 =
  54967+586+1508+922+4205 = 62188` (avg 207.293333333, exact
  207.2933333333333); tag invocations 287, seed bits `2623*287 = 752801`;
  feedback 16 invocations / 16 bits. `levels_invoked` total 316 = 316
  disclosures + 287 tags + 16 controls = 619 incremental events (matches
  persisted event count); static events 598 = 300 + 298.
- Fail-closed check: every decode_failed record has `levels_invoked =
  level+1`, `tag_invocations = feedback_invocations = level`, key bits per
  formula, seed/feedback 0 at level 0.
- 5% integer rule: `62188*100 = 6218800 <= 95*86572 = 8224340` -> holds
  (saving fraction 0.28166150718477106, persisted rounded 0.281661507).
- Public control total `781654 + 752801 + 16 = 1534471` (static seed 781654,
  incremental seed 752801, feedback 16).
- Union bound over 298+287 = 585 tag invocations:
  `585*2^-64 = 3.1712913545201005e-17`; per-arm `1.6154612370034016e-17`
  (static), `1.555830117516699e-17` (incremental). All match persisted.
- Transcript independently rebuilt from the persisted per-block scalars with an
  own canonical serializer (sort_keys, compact separators, utf-8, `\n`
  terminated) and hashed: static sha256
  `e7a3302e287773d2de1048d9bb33c7f155e2a9d7e64fd36ae14ef0af74d58fb3` and
  incremental sha256
  `dadf5e3e5ebcd546b5d1f7ddaa3c01d216b421089fd0ec5d4930363fc8182299` — both
  **exactly** match the persisted hashes. Recount totals match the persisted
  recount; mismatch counts 0/0; `transcript_accounting.json` cross-checks equal
  `aggregate_comparison.json`.

## 6. Failure-mechanism audit (critical) — valid science, not a defect

Code: `run_incremental_block` (`incremental.py:390-497`) forces the actual true
`U[D_i]` values (`u_truth = polar_transform(x_truth)`), calls the accepted
`sc_decode`, and on any exception (including `ImpossibleDisclosedValueError`)
sets `decode_failed` at that level, breaks **before** the tag and before any
advance (no tag, no feedback), and accounts `5*K_i + 64*tag_invocations`
(=145 at level 0). The static comparator mirrors this (`225` bits, no tag).

Bounded injected/in-memory reproduction (non-frozen seed 2026091420, no temp
output persisted):
- Direct `sc_decode` with `known_positions = D_1` and the true `U[D_1]` raises
  `ImpossibleDisclosedValueError: impossible disclosed value: U[65]=14 has
  exact-zero support` from accepted `sc.py:214`.
- A spy confirms the harness passed `known_positions == D1`, `known_values ==
  true U[D1]`, and the unmutated Bob metric; `run_incremental_block` then
  returns `decode_failed`, `decode_failed_level=0`, `levels_invoked=1`,
  `tag_invocations=0`, `feedback=0`, `key_dependent_bits=145`,
  `public_seed_bits=0`, `error_type=ImpossibleDisclosedValueError`,
  `nonfinite=false`; a tag spy records **0** tag calls (fail-closed).
- An independent traced replay of the same decoder arithmetic shows the first
  decision deviating from truth at `U[35]` (an argmax decision on an erased
  coordinate, 0 vs true 27), before the forced known coordinate `U[65]` where
  the true disclosed value has exact-zero support. The same block with a
  noiseless metric decodes `exact` at level 0.
- Mechanism: on the q-ary erasure channel the true disclosed value always has
  positive posterior mass under the true prefix, so exact-zero support implies
  an earlier wrong SC decision (SC prefix error propagation). This is a genuine
  decoder failure mode, classified fail-closed by the frozen rule; the harness
  passes only the protocol's true disclosed values and Bob's metric, so it
  cannot fabricate the exception.
- **Conclusion: 271/300 exact with 29 level-0 `decode_failed` is a valid
  scheduled-science result under the frozen contract, not an implementation
  defect.** The two failed candidate gates are therefore genuine and correctly
  reported.

## 7. Bounded wording

`report.md` read in full: no FER, leakage-efficiency, key-rate, qualification or
promotion claim; scope line "synthetic paired development signal only; this is
not real-data FER, leakage efficiency, key rate, qualification or promotion
evidence" present in both report and aggregate; `candidate: null` stated
honestly; both failing gates shown in the gate table; decode failures and the
counts are disclosed, not hidden. Wording PASS.

## 8. Scope, provenance, attempt/seed state

- `git status --porcelain`: P6-window changes are only the declared P6 paths
  (`formal_ir/nbpolar/incremental.py`, `methods/nbpolar_incremental.py`,
  `tests/test_nbpolar_incremental.py`, `formal_ir/nbpolar/__init__.py` exports,
  P6 OpenSpec, queue dir + output root) plus the allowed
  lifecycle/index/decision/project-memory docs; all older P3/P4/P5 dirt has
  mtimes <= 02:52:42 and pre-exists the P6 window. Phase 5 code
  (`protocol.py` 02:13, `methods/nbpolar_static.py` 02:00,
  `test_nbpolar_protocol.py` 02:10) and the P5 evidence root (02:31) are
  untouched by P6.
- `results/` and `comparison_bench/outputs_comparison/`: zero files newer than
  02:52. Sibling checkout `../HD-QKD_Polar_Comparison`: zero files newer than
  03:30 (directory Sep 10). No writes outside the declared root.
- HEAD unchanged `ab173f2a...` (reflog contains only the clone entry); no
  staged changes; no commit/push. Output root is single-generation (5 files,
  ~21 ms span) and contains exactly 5 files; the root was absent before the run.
- Seeds: run seed `2026091340` in `frozen_plan.json` + aggregate; Toeplitz
  master `2026091341` in `frozen_plan.json`; `git grep` in HEAD finds neither;
  22 refused seeds persisted as frozen. Freedoms absent (no K/seed/flag
  overrides in the persisted plan).
- Attempt state: the written root is the consumed 1/1 attempt; the code order
  (static comparator block 0 first) matches the frozen consumption point.
  **`STATUS.yaml` is still `attempts_used: 0` / pre-execute `next_gate`** — this
  is a closeout action (see N-1), not an evidence defect. The frozen command
  itself was not rerun by this review.
- The exact argv/exit code are not independently re-provable from the artifacts
  (no command log is persisted); the artifacts (seed, 300 blocks, root, wall
  9.619874 s, peak RSS 111816704 bytes) are consistent with the frozen command.

## 9. Implementation state

- Focused suite: `test_nbpolar_incremental.py` -> **17 passed** in 9.02 s.
- Full suite: `comparison_bench/tests/test_nbpolar_*.py` -> **153 passed** in
  72.04 s (17 + 136). Both with pinned interpreter 3.12.3 / numpy 2.5.3, fresh
  `/tmp` basetemp, `-q -p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1` (no
  repo artifacts created; no `.pytest_cache`).
- Tiny-math/plan identity: D_sets recomputed from `analytic_order(0.05,256)`
  prefixes (equal), new-coordinate set differences (equal), strict proper
  nesting, D5 == `static_disclosure_coordinates(256,45)`, budget/seed/schema
  scalars match the freeze.

---

## Blocking issues

None.

## Non-blocking suggestions / closeout actions

- **N-1 (required closeout).** Update `STATUS.yaml`: `attempts_used: 0 -> 1`
  and post-result `next_gate` for the `BLOCKED(incremental_exact_ge_285)`
  return; write `OPERATOR_RETURN.md` reporting the two failing gates and the
  single earliest gate. No rerun, no tuning, no seed change.
- **N-2 (advisory, carried from Pre-EXECUTE F-1).** `rss_bytes_peak`
  (111816704 B, ~106.6 MiB) is environment-dependent evidence under the WSL
  `ulimit -v`/`ru_maxrss` quirk; it is not gate-bearing and must not be
  described as a memory envelope claim.
- **N-3 (test quality, carried from Pre-EXECUTE F-2).** The equality at
  `tests/test_nbpolar_incremental.py:766` is vacuous because
  `orig_p5_seed_tag` (:802-803) reuses the P6 bits/seed. It does not affect the
  frozen run; optional future rework only (do not touch under this freeze).
- **N-4 (numeric note).** The persisted Wilson LB `0.8715597837542944` is the
  exact value of the frozen float formula (recomputed identical); the Decimal
  value differs by 1 ulp. Both are well below 0.90; no action.
- **N-5.** Publish only after N-1; `docs/decision-log.md` /
  `docs/troubleshooting.md` memory triage belongs to the closeout (no durable
  doc currently claims a P6 result).

## Checklist

- [x] Matches OpenSpec spec / frozen packet (schedule, outcome precedence,
      accounting, 18 gates, Wilson denominator = attempted, 5% integer rule)
- [x] Tests pass (17 focused + 153 full)
- [x] No scope creep (declared P6 paths + allowed docs; pre-existing P3/P4/P5
      dirt accounted for; results/outputs_comparison/siblings untouched)
- [x] docs/decision-log.md / docs/troubleshooting.md update? Not required by
      this review; closeout/memory triage owns it.

## Closure statements

- The frozen paired command was **NOT rerun**; no scientific `sc_decode` was
  invoked with seed 2026091340 by this review. Attempt 1/1 is already consumed
  by the written evidence root.
- Verdict **PASS_WITH_COMMENTS**: the artifacts are valid and the
  `BLOCKED(incremental_exact_ge_285)` result may be published after N-1. No
  blocking issue; no rework of frozen evidence.
