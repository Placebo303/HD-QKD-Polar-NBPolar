# P6-R1 operator return — NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX

Δ successor operator session (2026-09-14, WSL), repository
`/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`. Pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3,
pytest 9.1.1). The original P6 evidence root and its persisted `BLOCKED` field
were never modified. No commit, no push, no new attempt, no new seed.

**R1-04 independent revalidation review is complete**: an independent
reviewer-go produced `INDEPENDENT_REVALIDATION_REVIEW.md` with verdict
**PASS_WITH_COMMENTS** (three non-blocking notes, no blocking issue). The
successor label is therefore returned as a **candidate**; main-thread
acceptance remains separate.

---

## R1-I01 — STATUS.yaml (PASS)

Only the three authorized flags, the state and the next gate changed; every
decoder/gate/artifact/real-data/promotion flag stayed false, attempts stayed
`0/0`, `original_root_immutable: true` stayed true.

```
-state: FROZEN_AWAITING_EXPLICIT_AUTHORIZATION
+state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P6R1_GATE_IDENTITY_FIX
-documentation_authorized: false
+documentation_authorized: true
-implementation_authorized: false
+implementation_authorized: true
-existing_evidence_read_authorized: false
+existing_evidence_read_authorized: true
-next_gate: EXPLICIT_USER_AUTHORIZATION
+next_gate: IMPLEMENTATION_AND_READONLY_REVALIDATION_THEN_INDEPENDENT_REVALIDATION_REVIEW
```

Unchanged/kept: `decoder_execution_authorized: false`,
`development_gate_authorized: false`, `artifact_read_authorized: false`,
`real_data_authorized: false`, `scientific_promotion: false`,
`attempts_allowed: 0`, `attempts_used: 0`, `result: null`,
`independent_revalidation_review: pending`.

## R1-I02 — OpenSpec rev note (PASS)

Appended a dated `### P6-R1 rev note (2026-09-13)` section to
`openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` recording the sole
identity correction and that no scientific constant/threshold/decoder path
changes, the immutable original root/label and the read-only successor
revalidation. No other planning artifact was touched.

## R1-I03 — Code delta limited to event identity/checker (PASS)

Changed files and hashes (sha256):

| file | sha256 |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py` | `910296ae3c4a56bdfa602dc05b0ac63f281f8ec61ba0531cd749d98a7f4fcc83` |
| `comparison_bench/tests/test_nbpolar_adaptive_l1.py` | `249af18f79063cff37b0ec16dfef214fb20faa6dcb5f34811ec2e7b6031e99ce` |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1_revalidate.py` (new) | `b84d00b55bc1d11c0a6dee195c3063b7096b9928789512c4c0e589a11f26f23a` |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` | `fd1ee6d9fb5a4c9d692b07ebe80464815f2a91d283bd88eb75d7d6527cd86b09` |
| `.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/STATUS.yaml` | `8b9b5cff4366e3334539a1f3a7d21c8367831ab31640fb648a3db564cc500913` (implementation-session snapshot; superseded by the finalized candidate status) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json` | `4b684a046c87bc8aead2e6f7aead3c7abf6b096b7e15f71e35e03a0f25ee12c1` |

`adaptive_l1.py` delta: +32/-6 lines (13 hunks; diff in the appendix). It is exactly:

1. `_event` gains the public scalar `stream_seed` and the stream-qualified
   `frame_key` (`...synthetic:<stream_seed>:<block_index>`);
2. all seven `_event(...)` call sites and the `paired_block_events`
   signature pass the stream identity (with `_as_int` validation);
3. the diagnosed gate site (`_integrity_gates`) keys the D2 count on
   `(int(event["stream_seed"]), int(event["block_id"]), parts[2])` and
   `expected_l2` on `(int(r.stream_seed), int(r.block_index), arm.arm)`;
4. the runner caller passes `stream_seed=int(stream_seed)`;
5. docstring/comment lines only otherwise.

No scientific constant, threshold, disclosure formula, decoder path, outcome
taxonomy, seed/master, accounting rule or schema line changed. The frozen
constants read identically at their original lines (spot check):
`TAG_BITS=64` :88, `DISCLOSED_BITS_PER_COORDINATE=5` :89,
`FEEDBACK_CONTROL_BITS=1` :90, `FROZEN_N=256` :92, `FROZEN_EPSILON1=0.05` :93,
`FROZEN_K1_LEVELS=(45,60,72,112)` :96, `FROZEN_K2=140` :97, `STATIC_K1=112`
:98, `FROZEN_SEEDS=(2026091550..54)` :99, `STATIC_EXACT_MIN=620` :103,
`RSS_LIMIT_BYTES=2*1024**3` :105, `TOTAL_WALL_S=3600.0` :106, `BANNED_SEEDS`
:117–127. No edit to `sc.py`, prior/construction/two-layer semantics, `methods/`
adapters, P5, `__init__.py`, or any probe/evidence root.

Baseline provenance: the P6 module was never committed (untracked), so the
pre-R1 baseline used for the diff was reconstructed in `/tmp` by
inverse-applying the six logged edit operations; a forward round-trip of that
baseline reproduces the current file byte-for-byte (`round-trip == current:
True`). The reconstructed baseline matches every pre-R1 line anchor recorded in
`PRE_RESULT_REVIEW.md` §4.1 (`key` at `:1342`, `paired_block_events` at `:881`,
stream-less `_event`).

## R1-I04 — Regression test, focused and full suites green (PASS)

New test: `test_p6_r1_multistream_compound_d2_identity_gate` (in
`test_nbpolar_adaptive_l1.py`). Two streams (`2026091560/61`) share block
indices `0..1`; injected TEST-ONLY scalar arms feed the production
`paired_block_events` and `_integrity_gates`. Pure record/checker logic — no
SC/RNG/tag call. It asserts:

- the corrected compound-identity gate is `True` and **all 12** integrity gates
  pass on the fixture;
- 8 L2 events = 2 streams × 2 blocks × 2 arms; every event carries
  `stream_seed` and the stream-qualified `frame_key`;
- the pre-R1 `(block_id, arm)` key multiplicities are `[2,2,2,2]` — i.e. the
  old `count == 1` check would fail on exactly this fixture;
- dropping or duplicating one compound D2 disclosure makes the gate `False`
  while every other frozen gate stays unchanged (recount/mismatches held
  fixed).

Evidence that the *pre-R1 code* fails this fixture — a reconstructed pre-R1
copy run read-only from `/tmp` (no repo writes):

```
$ cd /tmp/opencode/p6r1_oldgroup && PYTHONPATH=/tmp/opencode/p6r1_oldgroup \
    /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python probe_old_grouping.py
l2_events 8
old_key_multiplicities [2, 2, 2, 2]
old_gate4 False
other_gates_true True
probe exit: 0
```

The same fixture under the R1 module (the new test) yields gate 4 `True` and all
gates `True`. Running the new test against the pre-R1 module also fails on the
new (now mandatory) `stream_seed` event parameter:
`TypeError: paired_block_events() got an unexpected keyword argument 'stream_seed'`
(1 failed, 15 deselected), confirming the identity field is required.

Exact test commands (pinned interpreter, fresh `/tmp` basetemps):

```
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m py_compile \
    comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py
COMPILE_OK
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m py_compile \
    comparison_bench/tests/test_nbpolar_adaptive_l1.py
TEST_COMPILE_OK
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
    comparison_bench/tests/test_nbpolar_adaptive_l1.py -q -p no:cacheprovider \
    --basetemp=/tmp/opencode/p6r1_focused_1
16 passed, 1 warning in 6.77s
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
    comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider \
    --basetemp=/tmp/opencode/p6r1_predecessors_1
217 passed, 1 warning in 114.86s
```

(201 accepted predecessors + 16 focused adaptive-L1 tests; the pre-run
expectation from `P6_FREEZE.md` was 216 = 201 + 15, plus the one new test.)
Fresh-interpreter import check in an empty cwd: `IMPORT_OK`; the directory
stayed empty. The exact `-q` command must be shell-expanded (`test_nbpolar_*.py`
unquoted); the quoted form collects nothing.

The mandated suite re-run executes its own accepted tiny injected test fixtures
with the suite's fixed fresh test seeds under `/tmp` only. It does not use a
frozen seed, does not run the frozen command, and does not write into either
evidence root (verified below).

## R1-I05 — Read-only revalidation of the immutable P6 root (PASS)

Helper: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1_revalidate.py`
(new, pure stdlib json/math/hashlib, executable as a plain script). It reads
only the five stored files, records the input inventory (sizes + sha256) first,
re-verifies it before writing, and refuses to run if any decoder/RNG/tag module
is loaded. It reconstructs the 1280 `(stream_seed, block_index, arm)` D2
arm-block obligations from the per-block records, anchors the one-disclosure
count on the recorded/recounted transcript L2 total (1280), recomputes the 12
integrity gates (corrected compound D2 grouping) and the 4 scientific gates
with the frozen thresholds verbatim, and stops on any recomputed-vs-persisted
gate difference other than the diagnosed `d1_...` false→true correction.

```
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python \
    comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1_revalidate.py
{"corrected_gate": true, "integrity_all_pass": true,
 "output": ".../NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json",
 "result_label": "ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE"}
```

`revalidation.json` is the single machine-readable result, written outside the
old root. Headline content:

- `original_persisted`: label `BLOCKED`, `integrity_all_pass=false`,
  `failing_integrity_gates=["d1_exactly_nested_and_d2_disclosed_once"]`,
  `scientific_all_pass=true` (unchanged; report.md also still `BLOCKED`);
- `corrected_gate`: `d1_exactly_nested_and_d2_disclosed_once = true`;
- `gate_differences_vs_persisted`: exactly
  `[{gate: d1_exactly_nested_and_d2_disclosed_once, persisted: false, recomputed: true}]`
  — no second discrepancy; the helper would have STOPPED otherwise;
- all 12 integrity gates `true` and all 4 scientific gates `true`:
  `static_exact_at_least_620_of_640` (632/640),
  `adaptive_exact_equals_static_exact` (632=632),
  `paired_adaptive_only_zero_and_static_only_zero` (0/0),
  `leakage_100_adaptive_le_85_static` (67,578,300 ≤ 72,025,600);
- `paired`: 640 records, 640 unique `(stream_seed, block_index)` identities,
  exact product, 2 arms/record;
- `outcomes`: static/adaptive `{exact: 632, verify_failed: 8, others: 0}`;
  `cells {both_exact: 632, neither: 8, adaptive_only: 0, static_only: 0}`;
- `disclosure`: static 847,360 / adaptive 675,783 key-dependent bits, tags
  640/942/1582, feedback 302, public control 1,678,720/2,471,168;
- `l2_disclosure`: obligations 1280, recorded 1280, recounted 1280,
  distinct compound identities 1280;
- `counters {decoder_calls: 0, rng_calls: 0, tag_calls: 0}`,
  `attempts_consumed: 0`, `old_root_unchanged: true`;
- `cross_checks` all true, including `persisted_blocked_state_exact`,
  `plan_thresholds_verbatim`, summary-outcome/cell/union-bound agreement.

Old-root input inventory, before and after (identical; sha256 and size):

```
f27fa45d5485b31de286f800e7a248e27f2db5bfbd20091f3dadb92d8705be07  frozen_plan.json            15248
7b794dddac31d9cf8aa51a13da4ec054b7ba23f1dc74dd131c599638e5e61423  per_block_paired_outcomes.json 1125035
c308489879739aa3a6fea4ceeedcc3fe20583f1b06aa428b46bfdb884d8b4138  transcript_accounting.json   2090
2c2c09bf90c0376720e6cdd6e1db8a26ef4ef62574c981972f400906d59c5dc6  aggregate_summary.json       9090
d595e95f4c9b12ca700fc67f417833bbd7400151b6f1c4061f53eafb76187ce3  report.md                    2023
```

The five files are also unchanged after the full predecessor suite run; mtimes
remain `2026-09-13 21:25:30.511–.558` and the directory still contains exactly
these five files (no `.tmp`, no copy, no new output root). The persisted
`BLOCKED` field was not rewritten or reinterpreted.

## R1-I06 — Zero decoder/RNG/tag calls, zero attempt consumption (PASS)

- The code fix path adds only scalar identity/checker logic and calls no
  decoder, RNG, sampler or tag function.
- The new regression test builds injected scalar records only; it calls no
  SC/RNG/sampling/tag function (`simulate`/`default_rng`/`toeplitz_tag` absent).
- The revalidation helper never imports/loads `numpy`, `random`, `sc`, `prior`,
  `two_layer`, `penalty_gate`, `incremental`, `adaptive_l1` (it refuses if any
  are loaded) and reports `decoder_calls=0`, `rng_calls=0`, `tag_calls=0`,
  `attempts_consumed=0`.
- R1 `STATUS.yaml` stays `attempts_allowed: 0`, `attempts_used: 0`. The mandated
  R1-02 test re-run uses the accepted suite's own tiny test fixtures/test seeds
  in `/tmp` only and consumes no attempt.

## R1-I07 — No old-root writes / scope violations (PASS)

Files touched by this session (from `find . -newermt '2026-09-13 23:43'`):
`STATUS.yaml`, `revalidation.json`, `OPERATOR_RETURN_R1.md` (this file) in the
R1 packet; `tasks.md` rev note; `adaptive_l1.py`; `adaptive_l1_revalidate.py`;
`test_nbpolar_adaptive_l1.py`. `CURRENT_TASK.md` / `DOCUMENT_INDEX.md` carry the
pre-existing 23:43:48 main-thread packet-preparation mtimes, not session edits.
No file under `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/` or any
other evidence/probe/results root changed. No commit or push.

## Stop rules

None triggered: the old-root inventory is unchanged, the stored identity is
unambiguous (640 unique compound records × 2 arms), the only gate discrepancy is
the single diagnosed identity correction, tests pass, and no path can reach the
decoder/RNG/tag generator. The successor label remains a candidate until the
independent R1-04 review and main-thread acceptance.

## Appendix — `adaptive_l1.py` R1 diff (reconstructed pre-R1 → current)

```diff
--- /tmp/opencode/p6r1_diff/adaptive_l1_pre_r1.py	2026-09-14 00:00:04 +0800
+++ comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py	2026-09-13 23:53:13 +0800
@@ -34,7 +34,10 @@
 ``2623*tag_invocations``; one public feedback bit per invocation; public
 control = seed + feedback.  A decode rejection creates no tag.  An independent
 literal transcript recount must equal the incremental totals with zero
-mismatch; the verification union bound is ``min(1, tags * 2**-64)``.
+mismatch; the verification union bound is ``min(1, tags * 2**-64)``.  Every
+transcript event carries the public scalar ``stream_seed``; because block
+indices repeat across streams, the D2-once gate keys on the compound
+``(stream_seed, block_index, arm)`` identity.
 
 Outcome labels: ``ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`` iff every integrity
 and scientific gate passes at the frozen 640-pair shape;
@@ -852,6 +855,7 @@
 
 def _event(
     *,
+    stream_seed: int,
     block_index: int,
     event_id: str,
     event_type: str,
@@ -863,12 +867,13 @@
 ) -> dict:
     event = {
         "event_id": event_id,
-        "frame_key": f"nbpolar-p4p6-synthetic:{int(block_index)}",
+        "frame_key": f"nbpolar-p4p6-synthetic:{int(stream_seed)}:{int(block_index)}",
         "method": "nbpolar_adaptive_l1",
         "event_type": event_type,
         "direction": direction,
         "parent_event_id": parent_event_id,
         "pass_id": 0,
+        "stream_seed": int(stream_seed),
         "block_id": int(block_index),
         "key_dependent_bits": int(key_dependent_bits),
         "public_control_bits": int(public_control_bits),
@@ -878,14 +883,20 @@
     return event
 
 
-def paired_block_events(result: PairedBlockResult, *, nested, d2, n: int) -> list:
+def paired_block_events(result: PairedBlockResult, *, stream_seed: int, nested, d2, n: int) -> list:
     """Canonical public transcript events for both arms, in protocol order.
 
     Static: L1 disclosure, L2 disclosure (when invoked), one tag.  Adaptive:
     one cumulative-increment L1 disclosure per invoked stage, one L2 disclosure
     per arm/block (when invoked), one tag per invoked stage and one one-bit
     control event per feedback (tag mismatch or nonterminal rejection).
+
+    Block indices repeat across streams, so every event carries the public
+    scalar ``stream_seed`` alongside ``block_id`` and the arm encoded in the
+    event id: the unambiguous event identity is
+    ``(stream_seed, block_index, arm)``.
     """
+    stream_seed = _as_int(stream_seed, "stream_seed", minimum=0)
     seed_length = tl.seed_bits_for(n)
     events: list[dict] = []
     block_index = int(result.block_index)
@@ -895,6 +906,7 @@
         l1_id = f"block-{block_index}-static-l1-disclosure"
         events.append(
             _event(
+                stream_seed=stream_seed,
                 block_index=block_index,
                 event_id=l1_id,
                 event_type="l1_disclosure",
@@ -909,6 +921,7 @@
             l2_id = f"block-{block_index}-static-l2-disclosure"
             events.append(
                 _event(
+                    stream_seed=stream_seed,
                     block_index=block_index,
                     event_id=l2_id,
                     event_type="l2_disclosure",
@@ -922,6 +935,7 @@
             if static.tag_invoked:
                 events.append(
                     _event(
+                        stream_seed=stream_seed,
                         block_index=block_index,
                         event_id=f"block-{block_index}-static-verification",
                         event_type="verification_tag",
@@ -940,6 +954,7 @@
             l1_id = f"block-{block_index}-adaptive-l1-{stage}"
             events.append(
                 _event(
+                    stream_seed=stream_seed,
                     block_index=block_index,
                     event_id=l1_id,
                     event_type="l1_disclosure",
@@ -956,6 +971,7 @@
                 l2_id = f"block-{block_index}-adaptive-l2"
                 events.append(
                     _event(
+                        stream_seed=stream_seed,
                         block_index=block_index,
                         event_id=l2_id,
                         event_type="l2_disclosure",
@@ -971,6 +987,7 @@
                 verification_id = f"block-{block_index}-adaptive-verification-{stage}"
                 events.append(
                     _event(
+                        stream_seed=stream_seed,
                         block_index=block_index,
                         event_id=verification_id,
                         event_type="verification_tag",
@@ -986,6 +1003,7 @@
                 control_id = f"block-{block_index}-adaptive-control-{stage}"
                 events.append(
                     _event(
+                        stream_seed=stream_seed,
                         block_index=block_index,
                         event_id=control_id,
                         event_type="control",
@@ -1339,12 +1357,16 @@
         if event["event_type"] != "l2_disclosure":
             continue
         parts = str(event["event_id"]).split("-")
-        key = (int(event["block_id"]), parts[2])
+        # Block indices repeat across streams, so the once-per-arm/block check
+        # must key on the compound (stream_seed, block_id, arm) identity.
+        key = (int(event["stream_seed"]), int(event["block_id"]), parts[2])
         l2_counts[key] = l2_counts.get(key, 0) + 1
         if int(event["key_dependent_bits"]) != DISCLOSED_BITS_PER_COORDINATE * int(k2):
             l2_key_ok = False
     expected_l2 = {
-        (int(r.block_index), arm.arm) for r in results for arm in (r.static, r.adaptive)
+        (int(r.stream_seed), int(r.block_index), arm.arm)
+        for r in results
+        for arm in (r.static, r.adaptive)
         if arm.l2_invoked
     }
     l2_once = (
@@ -2107,7 +2129,11 @@
                 )
             )
             records.append(_block_record(paired, stream_seed=int(stream_seed)))
-            events.extend(paired_block_events(paired, nested=nested, d2=d2, n=n))
+            events.extend(
+                paired_block_events(
+                    paired, stream_seed=int(stream_seed), nested=nested, d2=d2, n=n
+                )
+            )
             accumulate(paired.static, paired.adaptive)
             if paired.adaptive.outcome == "decode_failed" and not paired.adaptive.l2_invoked:
                 no_l2_exhaustion_blocks += 1
```

## R1-04 — Independent revalidation review: PASS_WITH_COMMENTS

`INDEPENDENT_REVALIDATION_REVIEW.md` (fresh independent reviewer-go session,
HEAD `ab173f2a...`, unchanged) returned **PASS_WITH_COMMENTS** with no blocking
issue. The reviewer:

- audited the 13-hunk delta and proved it is limited to the event-identity
  change and the corrected D2-once grouping (scientific constants/semantics
  unchanged);
- independently reconstructed all 640 compound `(stream_seed, block_index)`
  identities, all 1280 `(stream, block, arm)` D2 obligations (each count 1), the
  L2 total 1280, all 12 integrity gates and all 4 scientific gates, matching
  `revalidation.json` field-for-field (42/42 comparison fields) with exactly the
  single diagnosed `d1_...` false→true correction;
- reproduced the pre-R1 fixture failure and re-ran the focused (16 passed) and
  full NB-Polar (217 passed) suites;
- confirmed the old root is byte-for-byte unchanged (five files; sizes, sha256
  and mtimes identical) and that the helper/test paths made zero
  decoder/RNG/tag calls (audit-hook and patched-entry-point probes).

Non-blocking reviewer comments: (1) this return's earlier `+31/-6` line-count
was off by one (actual +32/−6; corrected above); (2) `revalidation.json.counters`
are declarative constants rather than instrumented counters (the substantive
zero-call evidence is the import guard, the pure-stdlib implementation, the
audit-hook re-run and the patched-entry-point test run); (3) the corrected
D2-once revalidation is anchor-based — it reconstructs the 1280 obligations from
the stored per-block records and anchors the count on the recorded/recounted
transcript L2 total, exactly as the packet's R1-03 defines. Main-thread
acceptance remains separate.

## Closure statements

- No decoder, RNG, sampler or tag-generator call was made by the fix path, the
  regression test or the revalidation helper.
- The old root is byte-for-byte unchanged (five files, sizes and sha256
  identical before/after; mtimes untouched) and its persisted `BLOCKED` field
  is untouched.
- No new attempt, no new scientific sample, no new seed, no rerun of the P6
  gate, no artifact/real data, no APP/SCL/FWHT work, no commit, no push.
- `INDEPENDENT_REVALIDATION_REVIEW.md` is present with verdict
  **PASS_WITH_COMMENTS** (no blocking issue); the successor label
  `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` is returned as a candidate, and
  main-thread acceptance remains separate.
