# P4 implementation notes — NB-Polar Phase 4-P4 two-layer operational SC

Rev 1 (2026-09-13). Operator session notes for the freeze; evidence only, no
acceptance. Companion documents: `P4_FREEZE.md`, `TASK_PACKET.md`,
`AUTHORIZATION_PROMPT.md`, `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`.

## 1. What was built

One module `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py`
with: the explicit injected `[Alice,Bob]` table, `derive_p1`/`derive_p2` metric
tables, `analytic_order` disclosure sets, the explicit-RNG block sampler, the
per-arm/per-block SHA-256 counter-stream Toeplitz seed, the paired two-layer
block runner (operational + isolated oracle arms, truth-isolation sentinel,
wrong-L1 and tag injection seams), the canonical transcript events, the
independent literal recount, the 13 hard gates, the five-file writer and the
frozen CLI.  One focused test file
`comparison_bench/tests/test_nbpolar_two_layer.py` with 12 tests covering
P4-A01..A09, the failure taxonomy, A11, refusals, the five-file
scalar-only schema and the forbidden-marker/import-time checks.

## 2. Alternatives and decisions

1. **One module, no adapter (explicit packet instruction).**  The accepted
   benchmark contract (`methods/base.IRMethod`, `types.FrameBatch`/
   `IRRunConfig`/`IRRunResult`) is the synthetic single-layer convention:
   `batch.dimension == 1024`, `frame_len_symbols == 256`, Alice labels
   `32*x` with **low half constant zero** (see `methods/nbpolar_static.py`
   docstring and its label validator).  The P4 model's Alice label
   `low + 32*high` has a non-constant low half and its paired oracle arm has no
   `IRRunResult` field without changing the frozen schema.  Under the
   repository schema-stability rule (AGENTS.md §5.3) the smallest valid action
   is **no adapter**: the frozen command imports the module path directly.  The
   existing benchmark contract does not require one.
2. **Local `labels_to_bits` instead of importing `protocol.labels_to_bits`.**
   Keeps the P4 module independent of the P5 protocol module (the packet lists
   exactly which accepted helpers to reuse).  Tests compare it bit-for-bit
   against a literal `format`-style expansion and against the tag arithmetic.
3. **Decoder-free pre-run propagation check.**  The hard gate is "pre-run
   injected wrong-L1 propagation test passed".  The check uses a hand-injected
   layer-dependent table and compares gathered metrics plus label arithmetic
   only, so it consumes **no** SC call and no attempt; the attempt
   consumption point stays unambiguously "the first gate SC call" (block 0,
   operational L1).  The end-to-end hook (forced wrong L1 through
   `run_two_layer_block`) is covered by `test_p4_a08_forced_wrong_l1_propagation`.
4. **Strict bitwise `oracle_candidate_divergence`.**  The frozen semantics say
   "the operational P2_hat must differ from P2_true"; the implementation records
   `not np.array_equal(P2_hat, P2_true)`.  Under the frozen independent-layer
   model the table rows are mathematically independent of the high symbol
   (`max |p2[u1=0,b,:]-p2[u1=1,b,:]| = 7.77e-16`, float64 rounding), so the
   flag is only a real signal of "the candidate index differed from truth".
   The hand-injected check (`max abs diff 0.6`) and the tests prove decisive
   divergence is detected when the model has layer dependence.  Report-only,
   no threshold.
5. **Seed namespace `nbpolar-p4-toeplitz-seed`.**  Distinct from the P5
   (`nbpolar-p5-toeplitz-seed`) and P6/R1 (`nbpolar-p6-toeplitz-seed`)
   streams, so the R1 test-local use of `2026091360/2026091361` with the P6
   prefix cannot collide with the P4 gate streams.
6. **`n <= 256` enforced in the runner.**  The frozen scope is N=256; the
   runner refuses `n > 256` with a `ValueError` (CLI exit 2); block-level
   functions still accept tiny N=2/4 for the exhaustive oracle tests.
7. **Budget stop checked before each block.**  A block is either fully executed
   (both arms) or `resource_abort`; there is no mid-block partial accounting.
   Internal and external budgets are both 3600 s, matching the frozen command;
   the projected 96-block wall is ~10 s, so the boundary is not reachable in
   practice.
8. **Pristine `labels_true` exposure.**  The truth-isolation sentinel mutates
   the internal truth copies after the decisions exist; the block result
   exposes a pristine copy (`labels_true_out`) so tests never observe a
   sentinel-mutated truth vector.  Nothing is persisted.

## 3. Evidence

### 3.1 Tests (pinned interpreter, `-q -p no:cacheprovider`)

```text
comparison_bench/tests/test_nbpolar_two_layer.py                     12 passed
comparison_bench/tests/test_nbpolar_sc.py + prior + transform +
  construction + prior_artifact + p2r1_diagnostic + r1 + empirical_sc  120 passed  (61.94 s)
test_nbpolar_protocol.py + incremental + incremental_r1 +
  two_layer_rate                                                        60 passed  (27.30 s)
all comparison_bench/tests/test_nbpolar_*.py                          192 passed  (95.81 s)
```

The 12 focused tests cover: P1 Bob-only + source-domain candidate (A01),
Bob+candidate P2 literal gather (A02), isolated true-L1 oracle (A03), fresh
`sc_decode` calls / no state transfer (A04), full label + single final tag +
wrong-tag/collision seams (A05), truth-mutation sentinel and determinism (A06),
tiny exhaustive N=2 (Phase-2 oracle) and N=4 (accepted P3 vector oracle)
probability/decode checks (A07), forced wrong-L1 propagation (A08), buckets +
recount + tamper + five-file scalar-only schema (A09), failure taxonomy
(L1/L2/impossible/nonfinite), constants/CLI/refusals/N>256 + predecessor
suites (A11), and forbidden markers/import-time I/O.

### 3.2 Tiny CLI smoke (non-frozen seeds, temp root, not the gate)

```text
python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer \
  --n 4 --epsilon1 0.05 --epsilon2 0.20 --k1 1 --k2 2 --blocks 2 \
  --seed 2026091374 --toeplitz-master 2026091375 --out-dir /tmp/opencode/p4_cli_smoke
exit 0; five files written; repeat call exit 2 ("refusing to overwrite existing output root")
```

### 3.3 N=256 profile (NOT the frozen run)

Command: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python /tmp/opencode/p4_profile.py`
(`run_two_layer_dev_gate(run_seed=2026091372, toeplitz_master=2026091373,
blocks=8, out_root="/tmp/opencode/p4_profile")`).  Result: wall 0.93 s; block
median 106.5 ms / mean 106.7 ms / max 114.3 ms; projected 96-block wall ~10 s;
all 13 hard gates true; transcript mismatch 0; accounting exactly
`8 x 2 x 839 = 13424` key-dependent bits and `16 x 2623 = 41968` public
control bits; per-arm divergence count 4 of 8 defined blocks; operational exact
0 vs oracle exact 4 (report-only; the L1 candidate's five high bits propagate
into the label and the final tag catches the mismatch).  Peak RSS
~139-153 MiB across nine repeat 6/8-block runs (VmHWM agrees).  Measurement
note: one intermittent WSL2 `ru_maxrss` reading of ~1.2 GiB was observed for
an otherwise identical 8-block smoke; `/proc/self/status` VmHWM and all repeat
runs agree on ~139 MiB, so the reading is attributed to the WSL2 measurement
environment and should be re-checked by the reviewer.

### 3.4 Frozen model table evidence

- column-sum deviation `9.55e-15 <= 1e-12`;
- `max |p2[u1=0,b,:] - p2[u1=1,b,:]| = 7.77e-16` (mathematical independence of
  the layer-erasure model; see freeze §3);
- `P1[u1,b] = Ph(b_high|u1)`, `P2[u1,b,u2] = Pl(b_low|u2)` verified against
  literal loops in the tests.

### 3.5 Seed and scope evidence

- `git grep -n 2026091360 HEAD` and `git grep -n 2026091361 HEAD` → no matches
  (exit 1).  Both appear only as P6-R1 **test-local** seeds in the untracked
  R1 test file (`TEST_SEED_A/B`); that overlap is flagged for adjudication.
- Real output root `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`
  confirmed absent at freeze; `attempts_used: 0`.
- No changes under `results/` or `comparison_bench/outputs_comparison/`; no
  sibling checkout write; no commit or push.

## 4. Non-blocking notes for the carrier / reviewer

1. The frozen independent-layer model makes the L2 metrics layer-independent
   (item 4 above); the interface gate therefore measures the causal wiring,
   the provenance/accounting discipline and the label-level propagation, not a
   performance delta.  This is a property of the frozen model, not a deviation.
2. Internal and external wall budgets are both 3600 s (the frozen command's
   `timeout 3600`), unlike P5/P6 which had a smaller internal budget.  The
   ~360x margin makes the boundary unreachable at the frozen point; the
   reviewer may prefer to keep this as-is to stay byte-faithful to the packet
   command.
3. `ArmBlockResult`/`TwoLayerBlockResult` keep in-memory arrays for tests;
   every persisted record is scalar-only and checked by the schema test.
4. The cosmetic `runpy` warning on `python -m` is the accepted Phase 5/6
   pattern and is not an error.
