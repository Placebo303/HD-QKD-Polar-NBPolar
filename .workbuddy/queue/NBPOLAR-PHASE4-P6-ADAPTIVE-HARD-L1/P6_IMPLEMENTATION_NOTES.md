# P6 implementation notes — NB-Polar Phase 4-P6 adaptive hard-L1 disclosure gate

Rev 1 (2026-09-13). Operator session notes for the freeze; evidence only, no
acceptance. Companion documents: `P6_FREEZE.md`, `TASK_PACKET.md`,
`AUTHORIZATION_PROMPT.md`, `docs/nbpolar/probes/X04_L1_DISCLOSURE_PARETO.md`,
`docs/nbpolar/probes/X05_L1_LADDER_REPLAY.md`, and the read-only X05 evidence
`workspace/probes/nbpolar_x05_l1_ladder_replay/results.json`.

## 1. What was built

One module
`comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py` with:
the frozen-point CLI/runner, the static `K1=112` endpoint arm, the adaptive
nested `[45,60,72,112]` restart ladder with per-stage tag/feedback semantics and
the nonterminal/terminal impossible-disclosure split, the per-arm/block/level
Toeplitz seed domain, canonical transcript events with an independent literal
recount, the executed-disclosure accounting, the verification union bound, the
12 integrity gates, the 4 scientific gates, the two registered outcome labels
and the five-file writer.  One focused test file
`comparison_bench/tests/test_nbpolar_adaptive_l1.py` with 15 tests.  The
`formal_ir/nbpolar/__init__.py` surface adds only the new `adaptive_l1` names.
No accepted module was modified.

## 2. Alternatives and decisions

1. **Reuse the accepted dependent table and sampler.**  The injected
   `[Alice,Bob]` table, the strong-profile kernel, the explicit-RNG draw order
   and the pre-decoder `p2_maxdiff` guard come from the accepted
   `penalty_gate` module unchanged; the measured `p2_maxdiff` is
   `0.34875000000000267` and the column deviation
   `3.774758283725532e-15`, bit-identical to the P5/X02 arithmetic.  The
   `H(A|B)` planning denominator recomputed here is exactly the accepted
   X04/X05 value `2.134043324031305`.
2. **Reuse the accepted nested-schedule builder.**  `D1` sets, increments and
   the strict-nesting/non-overlap proofs come from
   `incremental.build_nested_schedule`; `D2` from
   `two_layer.disclosure_coordinates`.  No new construction code.
3. **Own per-arm/block/level Toeplitz domain.**  The packet requires master
   `stream+10000` domain-separated per arm/block/level.  The accepted
   `two_layer` seed derivation is per arm/block only and the `incremental` one
   is single-layer; a local helper mirrors the accepted SHA-256 construction
   with the domain string `nbpolar-p4p6-toeplitz-seed:<master>:<arm>:<block>:
   <level>:<counter>` (level = one-based invocation index within the arm;
   static uses level 1).  The tag function itself is the accepted
   `shared.toeplitz_tag`.
4. **Static arm first.**  `run_paired_block` runs the static arm before the
   adaptive ladder so the attempt-consumption point is exactly the static L1
   SC call at stream 0, block 0, as frozen; both arms receive the identical
   sampled arrays, the identical P1 metric object and the identical disclosed
   values.
5. **Executed-disclosure accounting.**  Each arm counts only disclosures it
   actually sent: cumulative `5*K_j` L1, the once-per-arm/block `5*140` L2
   disclosure when L2 was invoked at least once, and `64` per tag.  This equals
   the frozen formula `5*(K_j+140) + 64*tag_invocations` on every accept/
   verify-failed/undetected path and on any decode failure after a candidate
   existed.  A block that never produced a candidate (all four L1 decodes
   rejected/failed) never sent `D2`, so it counts `5*K_j`; the persisted
   `no_l2_exhaustion_blocks` records that corner (expected zero).  The
   independent transcript recount is therefore literal and exact on every path.
6. **Impossible semantics split.**  A nonterminal
   `ImpossibleDisclosedValueError` records a rejection (no candidate, no tag),
   emits one public feedback bit and advances to the next cumulative prefix;
   the terminal stage and every other exception are fail-closed
   `decode_failed`.  This mirrors the accepted Phase 6-R1 decode-reject-advance
   semantics, extended to the two-layer candidate-conditioned L2.
7. **Level tags, level-restart proof.**  Every stage calls a fresh SC on the
   original P1 metric object and a freshly gathered L2 metric; tests instrument
   `two_layer._decode_layer` and the tag seam and assert L1 object identity,
   distinct freshly gathered L2 objects, strictly increasing disclosed
   prefixes, per-level distinct tag seeds and the exact frozen seed
   derivation.
8. **No benchmark adapter.**  As in P4/P5, the unchanged
   `FrameBatch/IRRunConfig/IRRunResult` single-layer contract does not admit
   this paired two-layer synthetic statistic without a schema change; the
   frozen command imports the module path directly.  No
   `methods/nbpolar_adaptive_l1.py` was added.
9. **No new thresholds or gates beyond the packet.**  The 12 integrity and 4
   scientific gate names/order are persisted in the plan and summary; the
   candidate label additionally requires the frozen 640-pair shape, so a tiny
   smoke can never emit it.
10. **Tests are sealed.**  All focused tests use temporary roots, injected
    tiny blocks, the accepted strong table and fresh seeds `2026091560..1566`;
    no runner call uses a frozen stream/master, no stored data or predecessor
    root is read, and the plain-python runner works without pytest.

## 3. Evidence

### 3.1 Tests (pinned interpreter, `-q -p no:cacheprovider`)

```text
comparison_bench/tests/test_nbpolar_adaptive_l1.py                    15 passed   (8.20 s)
comparison_bench/tests/test_nbpolar_*.py (all NB-Polar)              216 passed  (104.28 s)
plain runner: python comparison_bench/tests/test_nbpolar_adaptive_l1.py  15/15 passed
```

The 15 focused tests cover: nested-set construction and the accepted `D1(45)`
identity; level restart/no-state-reuse with instrumented decoder and tag calls
(original-metric identity, fresh L2 objects, per-level distinct seeds); tag
accept/advance (forced mismatch advances exactly one level; terminal mismatch is
`verify_failed`; colliding tag on a wrong label is `undetected`); nonterminal vs
terminal impossible-disclosure semantics and other-exception fail-closed;
label assembly and the static endpoint; truth-isolation sentinel and input
invariance; accounting at every termination class (accepted stage 1/2/3,
`verify_failed`, `undetected`, terminal rejection, rejection-then-accept,
nonfinite failure); transcript recount and tamper; paired block identity and
same-sample/one-P1-metric proof; the tiny five-file scalar-only schema and
gates; runner and CLI refusals without decoder calls (existing root, banned
seeds, wrong point, `p2_maxdiff` floor, missing flags); resource-abort and
truth-leak gate paths; frozen constants/refused set/fresh test seeds;
`H(A|B)`/`p2_maxdiff` conventions; forbidden-marker and import-time-effect
scans.

### 3.2 CLI smoke (non-frozen seed, temp root, NOT the gate)

```text
python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 \
  --n 256 --epsilon1 0.05 --profile strong --k1-levels 45 60 72 112 --k2 140 \
  --seeds 2026091566 --blocks-per-seed 2 --out-dir /tmp/opencode/p6_cli_smoke
exit 0; five files; integrity_all_pass=true; cells 2/0/0/0;
static mean 1324.0; adaptive mean 989.0 (both blocks accepted at K1=45);
saving 25.30%; outcome ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED
(2-pair shape, not the frozen 640 shape)

repeat call: exit 2 ("refusing to overwrite existing output root")
seed 2026091510: exit 2 ("banned"); profile weak: exit 2; refused roots absent
```

### 3.3 Seed and scope evidence

- `git grep` over HEAD and a full-worktree `rg` (excluding this packet) find no
  prior use of 2026091550..2026091554 or 2026101550..2026101554; the frozen
  streams are unused.
- Real output root `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
  confirmed absent; `attempts_used: 0`; no gate run executed with the frozen
  seeds.
- No changes under `results/` or `comparison_bench/outputs_comparison/`; no
  sibling checkout write; existing evidence roots untouched; no commit or push.

## 4. Non-blocking notes for the carrier / reviewer

1. The `python -m` invocation may emit the accepted cosmetic `runpy`
   `RuntimeWarning` seen in the P4/P5/P6 modules; it is not an error.
2. The `no_l2_exhaustion_blocks` accounting corner is expected to be zero in
   the real run; if nonzero it is persisted and reviewer-visible rather than
   silently merged into the frozen formula.
3. The static `K1=112` and the adaptive terminal stage share the same P1
   metric, candidate and L2 metric construction, so structural agreement of
   `exact` is expected; the gate still measures it and `adaptive_only`/
   `static_only` must be zero.
4. Planning-only `f` uses the X04/X05 denominator `256*H(A|B)`; it is not
   real-channel efficiency, leakage or qualification evidence.
5. Small 2-block smoke runs estimate the per-block cost at roughly 0.1-0.2 s
   for the paired arms plus one-off table derivation; the 640-block gate should
   stay far inside the 3600 s / 2 GiB envelope, but the wall/RSS gate is
   persisted regardless.
