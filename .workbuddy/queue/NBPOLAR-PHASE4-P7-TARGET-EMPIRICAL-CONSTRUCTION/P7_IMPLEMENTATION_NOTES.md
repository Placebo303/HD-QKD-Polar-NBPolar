# P7 implementation notes — NB-Polar Phase 4-P7 target-population empirical construction

Rev 1 (2026-09-14), implementing session (`coder-fast`). Documentation only;
this file authorizes nothing and checks no OpenSpec box.

## 1. Deltas delivered

| artifact | delta |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_construction.py` | new: core + CLI for the frozen P7 gate (no accepted module edited) |
| `comparison_bench/tests/test_nbpolar_target_construction.py` | new: 11 focused tests (injected tables/temp roots/fresh seeds only) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p7/spec.md` | new P7 delta spec |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` | appended the P7 task section (all boxes unchecked; prior uncommitted P3-P6 content untouched) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/STATUS.yaml` | STEP 0 authorization flags/state |
| `P7_FREEZE.md` | frozen point, command, schema, gates, budgets |
| `P7_IMPLEMENTATION_NOTES.md` | this file |

No other module, baseline file, old evidence root, sibling checkout or output
root was modified. `git status` shows pre-existing uncommitted working-tree
changes from earlier sessions (`nbpolar/__init__.py`, `empirical_channel.py`,
`empirical_diagnostic.py`, `empirical_oracle.py`, `test_nbpolar_empirical_sc.py`,
docs) that were **not** touched by this session (mtimes 2026-09-13).

## 2. Implementation map (packet item -> code)

- P7-01/02 input: `run_target_construction` refuses an existing `--out-dir`
  first, then stat-checks `25166822` bytes, then calls the accepted
  `load_v25_channel_counts(str(path))` once, selects source `1M`, and records
  read/attempt `1/1` consumed at that content open (`input_mode="v25_npz"`).
- Support rule and preconditions: `build_target_conditional`,
  `target_entropies`, `target_preconditions`; failure raises
  `TargetPopulationContractError` (`BLOCKED(target_population_contract)`)
  before any genie/SC call and before the output root is created.
- P7-03 construction: TRAIN genie accumulation with the accepted
  `genie_conditionals`, per-stream/pooled worst-first orders frozen (canonical
  digest) before DEV; BEC controls from `epsilon_l = H_l/5`; DEV runs the two
  paired candidate-conditioned arms with fresh per-layer SC restarts, rebuilt
  labels, one 64-bit arm/block/stream-domain-separated tag, accepted buckets,
  a block truth sentinel, transcript events/recount and the frozen
  accounting.
- P7-04 tests: see section 4.
- P7-05/06: five-file output and frozen gates/labels implemented; the command
  in `P7_FREEZE.md` §8 is the packet command verbatim.

## 3. Key implementation decisions (review items)

1. **Entropy functional (must be confirmed at Pre-EXECUTE).** Preconditions
   3-5 compare the packet literals against the raw-MLE in-sample population
   entropies (`H1 = E_B H(P1_raw)`, `H2 = E_{B,U1} H(P2_raw)`), i.e. the
   accepted V26 `adapter_H` / V49 in-sample-chain functional; precondition 6
   compares the floored-protocol-table total against the raw-MLE total. On a
   synthetic sparse mimic of the V25 count structure (~2-3 nonzero cells per
   Bob column, integer counts, no zero column), the floored-table functional
   shifts the total by `5.118e-11` (H1 `4.27e-11`, H2 `8.5e-12`) while the
   population functional differs from the packet literals by construction
   arithmetic only. The strict "entropy of the floored table" reading would
   fail precondition 3 by ~`4e-11` and would make the gate unsatisfiable;
   the packet's own `1e-9` floor guard and `1e-12` literal tolerance are only
   jointly satisfiable under the population reading. Both readings are
   documented in `P7_FREEZE.md` §3.1; the reviewer must confirm before
   execution.
2. **Test/assessment seams.** `counts=` (injected tables), `expected_entropies=`
   and `tag_fn=` are keyword-only seams documented in the runner docstring;
   the frozen CLI exposes none of them. Injected runs record
   `input_mode="injected_counts"` with read/attempt `0/0` and are structurally
   unable to touch the NPZ (tests patch the loader with a raising stub).
3. **Budget semantics.** The wall/RSS guard applies from the start of the run;
   a breach during TRAIN raises `TargetConstructionResourceError` (no orders
   can be frozen, nothing written), a breach during DEV fills every remaining
   planned block with `resource_abort` arms and still writes the five files
   (P5 precedent). `_budget_exceeded` is the documented monkeypatch seam used
   by the abort-path test.
4. **Truth isolation.** Each arm copies its truth inputs and uses the copies
   for every computation; the block sentinel mutates those internal copies
   after metrics/decisions exist (metric log-rows, disclosed values, candidate
   arrays, labels and bit expansions are protected). The caller's arrays are
   never mutated.
5. **Reuse, not redefinition.** `labels_to_bits`, `seed_bits_for`,
   `OUTCOMES`, the disclosure-bit constants, `toeplitz_tag`,
   `canonical_event`, `wilson_lower_bound`/`WILSON_Z`, the prior gather
   helpers and `sc_decode` are imported from accepted modules; no formula or
   taxonomy is duplicated by hand.

## 4. Test evidence (pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`)

Focused suite (11 tests; floor/renorm + entropy reconstruction, axes/packing,
zero-column refusal, tiny injected sampler frequencies, per-stream/pooled
construction and freeze, arm separation + candidate-conditioned L2 truth
isolation, buckets, disclosure/tag accounting + literal recount + tamper,
CLI/refusals/frozen constants, sentinel + resource-abort paths,
no-forbidden-marker/empty-cwd-import):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_target_construction.py -v \
  -p no:cacheprovider --basetemp=/tmp/p7_tests_tmp6
# 11 passed, 1 warning in 8.54s
```

Full accepted NB-Polar predecessor suite (217 predecessor + 11 new = 228):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_*.py -q \
  -p no:cacheprovider --basetemp=/tmp/p7_full_tmp2
# 228 passed, 1 warning in 108.89s
```

Additional structural checks performed by the focused tests: injected runs
never call `load_v25_channel_counts`; the real output root is never referenced
from tests; `run_target_construction` imports cleanly from an empty cwd without
creating files; every arm's L1/L2 SC call receives a freshly built metric
object; the empty/abort/documentation paths leave no partial roots. The
resource-abort path test also pins that aborted arms are exempt from the
executed-arm disclosure formula, so the disclosure/recount gate stays true
while the resource gate alone blocks the label.

## 5. Boundary statement (this session)

- The V25 NPZ was **not opened**; only `st_size` metadata was read
  (`25166822` bytes, matching `EXPECTED_NPZ_BYTES`).
- The frozen gate was **not run**; no output root exists.
- Artifact reads consumed: **0/1**. Scientific attempts consumed: **0/1**
  (`STATUS.yaml`: `artifact_reads_used: 0`, `attempts_used: 0`).
- No Model-F/parquet/TTBin/held-out/raw/EVAL access, no `N>256`, no
  APP/SCL/FWHT path, no production benchmark, no commit or push.
- The real root
  `.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`
  is absent and must remain absent until an authorized execution.

## 6. Open items for the Pre-EXECUTE reviewer

1. Confirm the entropy functional in `P7_FREEZE.md` §3.1 (population raw-MLE
   vs strict floored-table reading) and that `1e-12` literal checks are
   expected to pass on the real V25 counts.
2. Confirm the frozen command text in `P7_FREEZE.md` §8 is byte-equivalent to
   the packet command (`--counts`, `--source 1M`, `--n 256`, `--floor 1e-15`,
   the two seed lists/block counts, `--k1 45`, `--k2 140`, `--out-dir`).
3. Confirm the target root is absent and the input file is the registered
   sibling-checkout path with the expected size/identity before authorization.
4. Confirm the DEV budget semantics (TRAIN raise vs DEV abort-fill) and the
   2 GiB/3600 s envelope are as intended for the one-shot execution.
