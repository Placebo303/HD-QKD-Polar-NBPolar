# P8 implementation notes — NB-Polar Phase 4-P8 target rate SCREEN → CONFIRM

Rev 1 (2026-09-14), implementing session (`coder-fast`). Documentation only;
this file authorizes nothing and checks no OpenSpec box.

## 1. Deltas delivered

| artifact | delta |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py` | new: core + CLI for the frozen P8 gate (no accepted module edited) |
| `comparison_bench/tests/test_nbpolar_target_rate.py` | new: 12 focused tests (injected tables/orders/temp roots/fresh seeds only) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p8/spec.md` | new P8 delta spec |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` | appended the P8 task section (all boxes unchecked; prior content untouched) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/STATUS.yaml` | STEP authorization flags/state (this wave) |
| `P8_FREEZE.md` | frozen point, command, schema, gates, budgets |
| `P8_IMPLEMENTATION_NOTES.md` | this file |

No other module, baseline file, old evidence root, sibling checkout or
output root was modified. No package `__init__` change was needed (the
frozen command and the tests import the module path directly, P7
precedent). `HEAD` is unchanged (`ab173f2a5e17336383a897b941080b731ba3dd9e`);
no commit was made.

## 2. Implementation map (packet item -> code)

- P8-01/02 inputs: `run_target_rate` refuses an existing `--out-dir`
  first, validates the frozen scalars/grids/seed lists, then loads and
  validates the P7 orders file (`validate_orders_doc` + frozen
  `EXPECTED_ORDERS_SHA`) BEFORE the NPZ stat check and the single accepted
  `load_v25_channel_counts(str(path))` call; read/attempt `1/1` with
  `open_count 1` are recorded at that content open (`input_mode="v25_npz"`).
- Support rule and preconditions: the accepted P7 helpers
  (`target_preconditions` incl. the ratified population entropy
  functionals); failure raises `TargetPopulationContractError`
  (`BLOCKED(target_population_contract)`) before any SC call and before
  the output root is created.
- P8-03 SCREEN: `sample_shared_blocks` samples each shared block once per
  stream; `screen_grid` yields the exact 35 points in K1-major order;
  `run_rate_arm` runs the empirical arm (fresh L1 then
  candidate-conditioned L2, rebuilt label, one P8-domain 64-bit tag);
  `screen_eligibility` records Wilson LB + 188-count + agreement;
  `select_point` is the lexicographic minimum over eligible points only.
- P8-04 CONFIRM: disjoint streams asserted (`_check_seed_lists` refuses
  any overlap); `run_confirm_pair` runs only the selected point's
  empirical arm plus the BEC control at the same K1/K2; confirm gates are
  `>= 618/640` + Wilson `>= 0.95` + decision-path zeros.
- P8-05: `5*(K1+K2)+64` / `2623` accounting with partial-invocation
  semantics (P7 rule), phase/arm-literal `recount_events`, five scalar-only
  files, planning-only `f = mean_key_dependent/(256*total)`.
- P8-06/07: twelve-flag CLI with no production default; frozen command in
  `P8_FREEZE.md` §7 is the packet command verbatim.

## 3. Key implementation decisions (review items)

1. **Wilson-equivalence verification (done).** `screen_eligibility`
   gates on the Wilson LB and records the `exact >= 188/192` count check
   plus `wilson_count_agree`. Verified numerically at freeze with the
   accepted `wilson_lower_bound`: `187/192 -> 0.9474773285638652`
   (ineligible), `188/192 -> 0.9544033287216636` (eligible), and the full
   `0..192` range satisfies `eligible ⟺ exact >= 188`; confirm shape
   `617/640 -> 0.9498753087068414`, `618/640 -> 0.9516826902311426`, full
   `0..640` range satisfies `LB >= 0.95 ⟺ exact >= 618`. The focused tests
   re-verify both full ranges against an independent literal Wilson
   implementation. Agreement is recorded, not separately gated.
2. **Shared-block mechanism.** `sample_shared_blocks` returns `SharedBlock`
   objects; the SCREEN loop passes the identical object to all 35 configs.
   The focused spy test asserts object identity (`id`) per block position
   across all 35 configs.
3. **Refusal ordering.** Absent-root → frozen validation → orders identity
   → NPZ stat → content open (consume) → preconditions (zero SC on
   failure). Preconditions necessarily follow the content open; see
   `P8_FREEZE.md` §3.1 for the explicit review item.
4. **Per-arm (not block-level) truth sentinel.** P7 applied the sentinel
   across both DEV arms of a block; P8 applies it inside `run_rate_arm`
   over that arm's own protected set and truth copies (SCREEN is
   single-arm, so a block-level sentinel would add nothing; CONFIRM arms
   each carry their own copies). Same coverage per arm, simpler structure.
5. **Zero-gate scope.** `undetected_zero`/`nonfinite_zero`/
   `resource_abort_zero` cover the decision path (eligible SCREEN configs
   + CONFIRM); rejected SCREEN configs are report-only, since their
   verify/decode failures are the screen working. `truth_leak_zero` is
   global. Any budget breach abort-fills, skips CONFIRM and blocks.
6. **Test seams.** `counts=`, `orders=` (loaded-form dict of four int64
   permutations), `expected_entropies=`, `tag_fn=` are keyword-only seams
   documented in the runner docstring; the frozen CLI exposes none of
   them. `validate_orders_doc(doc, expected_sha=...)` is the pure
   validation core so tests can exercise every refusal branch without
   forging the frozen digest. Injected runs record
   `input_mode="injected_counts"` with read/attempt `0/0` and are
   structurally unable to touch the NPZ (tests patch the loader with a
   raising stub). Seed lists are validated for distinctness/disjointness
   but not pinned to frozen values, mirroring P7 (the summary's
   `shape_is_frozen` flag gates the candidate label instead).
7. **Reuse, not redefinition.** Support, preconditions, sampler, buckets,
   Wilson, Toeplitz tag, transcript canonicalization, prior gather
   helpers and `sc_decode` are imported from accepted modules; only the
   P8 grid/selection/confirm orchestration, the P8 phase-domain seed
   derivation and the phase-aware recount are new.
8. **SCREEN seeds vs P7 test-local seeds.** Numerically coincident
   (`2026091680..1682`), never consumed as official streams (P7 consumed
   only TRAIN/DEV). CONFIRM seeds are fully fresh. Recorded in
   `P8_FREEZE.md` §9 for Pre-EXECUTE awareness.

## 4. Test evidence (pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`)

Focused suite (12 tests; grid completeness, Wilson boundary + full-range
equivalence, selection ties/empty, isolation/disjointness, shared-block
identity + selected-only + pairing, no-eligible path, truth isolation,
buckets, partial/full accounting + recount + tamper, orders refusals,
CLI/refusals/frozen constants, no-forbidden-marker/empty-cwd-import):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_target_rate.py -q \
  -p no:cacheprovider --basetemp=/tmp/p8_tests_tmp4
# 12 passed, 1 warning in 18.29s
```

Full accepted NB-Polar predecessor suite (228 predecessor + 12 new = 240):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_*.py -q \
  -p no:cacheprovider --basetemp=/tmp/p8_full_tmp1
# 240 passed, 1 warning in 146.11s
```

Additional structural checks performed by the focused tests: injected runs
never call `load_v25_channel_counts`; the real output root and the NPZ
path are never referenced from tests; `run_target_rate` imports cleanly
from an empty cwd without creating files; frozen SCREEN/CONFIRM seeds are
never used as test inputs; every SCREEN config sees the identical shared
block objects; CONFIRM runs only the selected K1/K2 on disjoint streams.

## 5. Boundary statement (this session)

- The V25 NPZ was **not opened**; only `st_size` metadata was read
  (`25166822` bytes, matching `EXPECTED_NPZ_BYTES`).
- The P7 `construction_orders.json` was read as JSON only (scalar identity
  fields: digest `8ec690…` recomputed == recorded, pooled order lengths
  256/256, BEC epsilons); the NPZ was never opened.
- The frozen gate was **not run**; no output root exists.
- Artifact reads consumed: **0/1**. Scientific attempts consumed: **0/1**
  (`STATUS.yaml`: `artifact_reads_used: 0`, `attempts_used: 0`).
- No Model-F/parquet/TTBin/held-out/raw/EVAL access, no `N>256`, no
  APP/SCL/FWHT path, no production benchmark, no commit or push.
- The real root
  `.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/`
  is absent and must remain absent until an authorized execution.

## 6. Open items for the Pre-EXECUTE reviewer

1. Confirm the refusal-ordering reading in `P8_FREEZE.md` §3.1
   (preconditions after the content open but before any SC call).
2. Confirm the frozen command text in `P8_FREEZE.md` §7 is byte-equivalent
   to the packet command (12 flags with the verbatim values).
3. Confirm the target root is absent, the orders file carries the frozen
   digest, and the NPZ path/size are the registered ones.
4. Confirm the SCREEN-seed / P7-test-local-seed numerical coincidence is
   acceptable (test-local use is not consumption) and the CONFIRM seeds
   are fresh.
5. Confirm the decision-path scope of the zero gates (§3.5) and the
   both-arms-zero CONFIRM requirement.
6. Confirm the 2 GiB/3600 s envelope for the one-shot execution (≈16k SC
   calls at N=256 GF32: 6720×2 SCREEN + 1280×2 CONFIRM).
