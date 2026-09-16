# P6 implementation notes — alternatives and evidence

Operator session 2026-09-13. Companion to `P6_FREEZE.md` (authoritative frozen
semantics). These notes record choices, rejected alternatives and raw evidence;
they authorize nothing.

## 1. Files changed

- new `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`
  (core + CLI)
- new `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py`
  (thin `IRMethod` adapter)
- new `comparison_bench/tests/test_nbpolar_incremental.py` (P6-A01..A12 + refusals)
- modified `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py`
  (explicit Phase 6 aliases only; Phase 5 exports unchanged)
- modified `openspec/changes/formal-ir-nbpolar-phase6-fixed-incremental/design.md`
  (Rev note only; no task box checked)
- queue `STATUS.yaml` flags/state/next_gate; new `P6_FREEZE.md`, this file
- no Phase 5 code was modified (no defect was proven); no frozen baseline,
  results, comparison outputs, sibling checkout, commit or push.

## 2. Frozen conventions and why

- **Seed derivation level index.** `arm` distinguishes the static comparator
  (`static`) from the incremental schedule; `level` is 0-based (static level 0;
  incremental levels 0..4). Chosen so the derivation string matches the frozen
  template literally and the mapping is unambiguous; documented in both the
  module and the freeze doc.
- **Feedback control.** One `control` transcript event per level advance
  (`key_dependent_bits=0`, `public_control_bits=1`), emitted after a mismatching
  tag when the next frozen level is actually invoked. Implemented as an
  increment on advance, not as a closed-form derivation, so the independent
  recount checks the same event list. Per-block relation: `feedback =
  tags - 1` for tag-terminated blocks (accept/final mismatch) and `feedback =
  tags` for `decode_failed` blocks (every previous tag advanced). Both are
  exercised in tests.
- **Static comparator.** Re-implemented thinly inside `incremental.py` with the
  Phase 6 seed derivation instead of importing `protocol.run_static_block`,
  because the frozen contract requires a P6-seeded in-run comparison and the
  Phase 5 root must not be touched. Equivalence is enforced by tests against
  `protocol.run_static_block` (outcomes, error counts, bit counts; equal message
  bits with different seeds), including the decode-failure path.
- **Restart proof.** The per-level `sc_decode` call receives the same original
  metric array with cumulative `D_i`; tests spy on every call and assert the
  metric contents equal the pre-run snapshot for every invoked level and that
  the caller's metric is unmutated after the block.
- **Pairing.** The paired runner snapshots `x`/`logp` before the static arm and
  after each arm; `paired_match` is false if either arm mutates the input, and
  the incremental arm always runs on the verified-unchanged arrays. A test
  injects a mutating static arm and confirms the gate fails.
- **Truth isolation.** Local `truth_isolation_sentinel` (same adversarial
  post-decision mutation pattern as Phase 5) checks every level's decision
  arrays plus all disclosed arrays; violations flip `truth_leak_zero`.
- **Union bound.** Reuses `shared.verification_union_bound` (`min(1.0, n*2**-64)`)
  over both arms; consistency gate compares the count universe with the
  transcript recount and the persisted bound with both.
- **Gates.** 18 booleans persisted; the candidate label requires all of them.
  `frozen_plan_identity` (seed 2026091340, 300 blocks, N=256, eps 0.05, frozen K)
  and `paired_identical_blocks` are separated so a failure identifies the cause.

## 3. Rejected alternatives

- Lazy/generator disclosure or warm-start SC reuse: forbidden by the frozen
  restart rule.
- Deriving accounting from accepted levels only (ignoring failed partial
  disclosure): would under-count fail-closed blocks; rejected.
- Persisting per-block seed digests as pairing evidence: forbidden; the scalar
  `paired_match` boolean plus snapshot checks are used instead.
- Adding a numeric union-bound threshold beyond count consistency: explicitly
  not authorized; the gate only checks internal consistency.
- Reusing the Phase 5 evidence root as the comparator: forbidden; not read.

## 4. Adapter notes

`methods/nbpolar_incremental.py` reuses `_validate_labels` and
`_observation_metric` from the accepted Phase 5 `methods/nbpolar_static.py`
(import only, no Phase 5 edit); `FrameBatch`/`IRRunConfig`/`IRRunResult`
signatures are untouched and asserted in tests. `n_frames_success = exact`
only; `undetected` never becomes success; `decode_failed`/`verify_failed` stay
disjoint; `beta_eff_empirical` remains derived.

## 5. Test evidence

- New focused suite: `comparison_bench/tests/test_nbpolar_incremental.py`,
  17 tests covering A01..A12 plus adapter round-trip/refusals, refusals,
  five-file scalar schema, resource abort, and the
  forbidden-marker/import-I/O/no-global-RNG scan.
- Command (operator run):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_incremental.py
  -q -p no:cacheprovider --basetemp=/tmp/opencode/pytest_p6`
  -> `17 passed` (≈ 9-14 s); standalone runner -> `17/17 passed` with the
  embedded predecessor suite `16` in `1.85 s`.
- Full NB-Polar suite (new file + 9 predecessor files, including the embedded
  Phase 5 suite run inside A11):
  -> `153 passed in 72.85 s`.
- Key semantics exercised: strict nesting/analytic prefixes; new-coordinate-only
  disclosure with zero values round-tripping; fresh restart on the identical
  metric for all five levels; one-level advance per mismatch with no selection,
  skip or parameter change; injected equal tag -> `undetected` never success;
  forced all-level mismatch -> `verify_failed` after exactly 5 tags; decode and
  nonfinite failures stop fail-closed with no further tags; cumulative formula,
  literal recount and tamper detection; seed/feedback/union-bound counting;
  disjoint/exhaustive buckets, truth-leak and nonfinite gates; paired identity;
  signature stability, comparator equivalence, predecessor regression; adapter
  round-trip outcome/leak mapping and refusals; tiny n=8/K=(2,3,4) exhaustive
  scheduler and mutation cases; refusal paths; smoke only with test seeds
  2026091342/1343/1344 and temp roots.

## 6. Profile evidence (injected seed 2026091399, temp root)

Command: `.venv/bin/python /tmp/opencode/p6_profile.py` ->
`run_paired_dev_gate(seed=2026091399, blocks=40, out=/tmp/opencode/p6_profile_out)`.

| workload | median | mean | p90 | max |
|---|---|---|---|---|
| paired block wall | 35.52 ms | 35.55 ms | 38.08 ms | 73.88 ms |
| static arm | 16.79 ms | — | — | 19.83 ms |
| incremental arm | 16.60 ms | 16.65 ms | — | 50.69 ms |
| metric generation | 0.144 ms | — | — | 1.53 ms |

Levels invoked: 1 (39 blocks), 3 (1 block). Outcomes: static exact 39 /
decode_failed 1; incremental exact 37 / decode_failed 3. Total wall 1.43 s;
peak RSS 105943040 bytes. Projected 300 blocks: 10.66 s mean / 11.42 s p90.
Frozen ceilings: total 600 s, per-paired-block soft cap 10 s, external timeout
1200 s, `ulimit -v 2097152` (2 GiB), measured peak ~101 MiB.

## 7. Observations for the main thread

- The `python -m` run emits a cosmetic `runpy` `RuntimeWarning` because the
  package `__init__` re-exports the module (same pattern as Phase 5); harmless,
  no effect on results.
- In the 40-block injected profile the incremental arm had 3 `decode_failed`
  (a level-0 impossible disclosed value at K=29); the real 300-block run's
  `incremental_exact_ge_285` and `undetected_zero` gates are the intended
  discriminators. No tuning was performed and none is permitted.
- CLI refusals verified with temp roots and non-frozen/banned seeds: existing
  root -> exit 2 `refusing to overwrite`; banned seed -> exit 2 with the target
  path still absent. Real output root remains absent; real run not executed.
