# R1 implementation notes — alternatives and evidence

Operator session 2026-09-13. Companion to `R1_FREEZE.md` (authoritative frozen
semantics). These notes record choices, rejected alternatives and raw
evidence; they authorize nothing.

## 1. Files changed

- modified `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`
  (R1 mode, three-arm runner/CLI, mode-aware consistency checker and
  transcript emitter, R1 seeds/validator/budgets; Phase 6 default path
  unchanged)
- modified `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py`
  (added `NBPolarIncrementalR1Method`; strict class output unchanged)
- new `comparison_bench/tests/test_nbpolar_incremental_r1.py` (17 tests,
  R1-A01..A12 + refusals/adapter/schema/forbidden-marker scan)
- modified `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py`
  (explicit R1 aliases only)
- modified `openspec/changes/formal-ir-nbpolar-phase6-r1-decode-reject-advance/design.md`
  (Rev note only; no task box checked)
- queue `STATUS.yaml` flags/state/next_gate; new `R1_FREEZE.md`, this file
- no Phase 5 code was modified; no frozen baseline, results, comparison
  outputs, sibling checkout, commit or push.

## 2. Frozen conventions and why

- **R1 as an explicit mode without breaking the Phase 6 signature pin.**
  Phase 6's `test_a11` asserts the exact parameter list of
  `run_incremental_block`; adding `advance_on_reject` to that public function
  would fail the predecessor suite. The mode flag therefore lives on the
  private shared implementation
  `_run_incremental_block_impl(..., advance_on_reject, arm)`, and the R1 arm
  is the explicit public wrapper `run_incremental_r1_block`. This is the
  packet's `advance_on_reject` mode, implemented so that the default path and
  all existing P6 tests/behavior are unchanged.
- **Separate R1 validator.** Phase 6's `test_refusals...` asserts both the
  exact `BANNED_RUN_SEEDS` frozenset and
  `validate_run_seed(2026091340) == 2026091340` (the Phase 6 seed stays
  usable in the Phase 6 mode). The packet also requires the R1 validator to
  refuse `2026091321`, `2026091340` and `2026091341`. Resolution:
  `BANNED_RUN_SEEDS`/`validate_run_seed` stay byte-pinned, and the R1 run
  uses the new `validate_r1_run_seed` / `R1_BANNED_RUN_SEEDS` (Phase 1-6
  consumed set plus `2026091321`, `2026091340`, `2026091341`; 25 values).
- **Shared `incremental` seed namespace.** Both incremental arms derive tag
  seeds with `arm="incremental"`, so a block that never rejects is
  bit-identical between strict-stop and R1; every strict/R1 difference is
  attributable to the rejection delta, and the rescue identities are clean.
  The static arm keeps its own namespace. Chosen over separate arm names
  (which would add tag randomness noise to a paired mechanism comparison).
- **Rejection accounting and invariants.** `rejected_levels` records only
  non-final intermediate rejections (strictly increasing, all `< 4`); a
  final-level error is `decode_failed` in `decode_failed_level`. Per-block
  invariants enforced by the R1 proof:
  `levels_invoked = tag_invocations + decode_rejected_continue_count`
  (+1 for a `decode_failed` terminal level), `feedback_control_invocations =
  levels_invoked - 1`, and `key_dependent_bits = 5*K_terminating +
  64*tag_invocations`. `incremental_record_consistent(..., advance_on_reject=
  False)` refuses any record carrying a rejection, which is the strict pin.
- **Transcript truth.** The R1 event emitter places `verification_tag`
  events only on non-rejected invoked levels and marks rejection advances
  with `decode_rejected_advance_next_level`; the strict emitter is unchanged.
  The literal recount only sums scalars, but the event list itself is honest
  about where tags happened.
- **Restart proof.** Rejections `continue` the level loop before any tag or
  candidate work; the next iteration calls `sc_decode` with the original
  `logp_arr` and the cumulative `D_{i+1}`. Tests spy on every call and assert
  the metric equals the pre-run snapshot and that a re-run reproduces the
  same sequence.

## 3. Rejected alternatives

- Adding `advance_on_reject` to the public `run_incremental_block` signature:
  breaks the Phase 6 signature pin (`test_a11`), which the packet requires to
  stay green.
- Extending `BANNED_RUN_SEEDS` in place: breaks the Phase 6 exact-set and
  Phase 6-frozen-seed assertions.
- Catch `ValueError` broadly to detect impossible disclosure: would swallow
  other `ValueError`s; only `ImpossibleDisclosedValueError` is whitelisted
  and the tests pin `ValueError`/`TypeError`/`RuntimeError`/
  `NumericNonfiniteError` as terminal.
- Recounting rejections as tags/verifications in the transcript: would
  misstate the protocol; rejections carry no tag event.
- Deriving rescue identities from a threshold: the identities are a report;
  only the frozen gates decide the candidate.
- Persisting per-block seed digests or per-block rejected value details:
  forbidden; scalar counts and the public `paired_match`/seed-derivation
  documentation are used instead.

## 4. Adapter notes

`methods/nbpolar_incremental.py` keeps `NBPolarIncrementalMethod` output
unchanged (same method name, backend status, notes and metadata keys;
verified by test) and adds `NBPolarIncrementalR1Method` with the same
`IRMethod` contract, `method="nbpolar_incremental_r1"`, the R1 block runner,
and three extra metadata keys (`decode_rejected_continue_count`,
`rejected_level_histogram`, `terminating_level_histogram`). `FrameBatch` /
`IRRunConfig` / `IRRunResult` signatures are untouched and asserted in tests.
`n_frames_success = exact` only; rejections are never success.

## 5. Test evidence

- New focused suite: `comparison_bench/tests/test_nbpolar_incremental_r1.py`,
  17 tests covering R1-A01..A12 plus refusals, five-file scalar schema,
  resource abort and adapter round-trip.
- Commands (operator run):
  - `.venv/bin/python comparison_bench/tests/test_nbpolar_incremental_r1.py`
    -> `17/17 passed; predecessor P5 16 + P6 17 in ~8 s`.
  - `.venv/bin/python -m pytest <11 NB-Polar test files> -q -p no:cacheprovider
    --basetemp=/tmp/opencode/pytest_p6r1` -> `170 passed in 99.42 s`
    (120 earlier + Phase 5 16 + Phase 6 17 + R1 17).
- Key semantics exercised: injected rescue at every next level (0->1, 1->2,
  2->3, 3->4) with one feedback, no candidate and no tag at the rejected
  level (seed-level proof plus `labels_from_symbols` call counts), cumulative
  disclosure and eventual accept; persistent impossible failure through K45
  -> terminal `decode_failed` with zero tags; final-level failure after
  mismatches; exception taxonomy (only `ImpossibleDisclosedValueError`
  continues); restart on the identical unmutated metric; recount equality and
  tamper detection (events and records); three-arm identical-block pairing
  with a mutating-arm counterexample; rescue/persisted/regressed/other
  identities; strict-stop pinning against Phase 6 on deterministic blocks and
  the unchanged signature; truth-leak/nonfinite/undetected handling; tiny and
  edge cases; refusal paths (existing root, banned seeds, CLI); no forbidden
  markers; no import-time I/O; no global RNG.

## 6. Profile evidence (injected seed 2026091399, temp root)

Command: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python /tmp/opencode/p6r1_profile.py`
-> `run_three_arm_paired_dev_gate(seed=2026091399, blocks=60, out=/tmp/opencode/p6r1_profile_out)`.

| workload | median | mean | p90 | max |
|---|---|---|---|---|
| paired three-arm block | 50.24 ms | 51.77 ms | 53.05 ms | 121.64 ms |
| static arm | 15.70 ms | 15.61 ms | 16.89 ms | 19.66 ms |
| strict-stop arm | 15.59 ms | 15.50 ms | 16.52 ms | 50.25 ms |
| R1 arm | 15.79 ms | 17.45 ms | 21.50 ms | 47.55 ms |
| metric generation | 0.14 ms | 0.17 ms | 0.18 ms | 1.29 ms |

Level distributions: strict-stop 1 level on 58/60, 2 on 1, 3 on 1; R1 1 on
52, 2 on 5, 3 on 1, 4 on 1, 5 on 1. R1 rejections: 11 across 6 blocks
(rejected level histogram 0:6, 1:2, 2:2, 3:1); terminating levels 0:52, 1:5,
2:1, 3:1, 4:1. Profile outcomes: static exact 59/decode_failed 1; strict
exact 54/decode_failed 6; R1 exact 59/decode_failed 1. Rescue identities:
rescued 5, persisted 55, regressed 0, other 0. Total wall 3.134 s; peak RSS
107933696 bytes. Projected 300 blocks ~15.7 s mean / ~16.0 s p90. Frozen
ceilings: total 900 s, per-block soft cap 15 s, external timeout 1800 s,
`ulimit -v 2097152`, measured peak ~103 MiB.

## 7. Seed absence raw evidence (before implementation, 2026-09-13)

```text
$ git grep -n "2026091350" HEAD        -> no output, exit 1
$ git grep -n "2026091351" HEAD        -> no output, exit 1
$ grep -rn "2026091350" --exclude-dir=.git .   -> no output, exit 1
$ grep -rn "2026091351" --exclude-dir=.git .   -> no output, exit 1
```

After implementation the worktree matches only the new R1 sources and this
queue directory (expected); `HEAD` greps remain empty.

## 8. Observations for the main thread

- The 60-block injected profile showed 5 rescues, 0 regressions and 0
  "other": the R1 delta does recover strict-stop losses on rejected blocks in
  the profile regime. This is a non-frozen profile, not the authorized
  attempt.
- The strict arm's 6 `decode_failed` in the profile were level-0 impossible
  disclosures (consistent with the accepted Phase 6 negative mechanism);
  the R1 arm converted the non-final ones.
- The real output root is absent; the real three-arm 300-block run was not
  executed; `attempts_used` remains 0.
