# P9 implementation notes — NB-Polar Phase 4-P9 lower-rate boundary resolution

Rev 1 (2026-09-14), implementing session (`coder-fast`). Documentation
only; this file authorizes nothing and checks no OpenSpec box.

## 1. Deltas delivered

| artifact | delta |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py` | delta-only: `--gate-id` closed-choice, P9 protocol/prefix/labels/grid/root; P8 path byte-for-byte; no accepted module edited |
| `comparison_bench/tests/test_nbpolar_target_rate.py` | additions only: 12 new P9 focused tests (injected tables/orders/temp roots/fresh seeds); 12 P8 tests untouched and green |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p9/spec.md` | new P9 delta spec |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` | appended the P9 task section (all boxes unchecked; prior content untouched) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/STATUS.yaml` | STEP authorization flags/state (this wave) |
| `P9_FREEZE.md` | frozen point, command, schema, gates, budgets |
| `P9_IMPLEMENTATION_NOTES.md` | this file |

No other module, baseline file, old evidence root, sibling checkout or
output root was modified. No package `__init__` change was needed (the
frozen command and the tests import the module path directly, P7/P8
precedent). `HEAD` is unchanged
(`ab173f2a5e17336383a897b941080b731ba3dd9e`); no commit was made.

## 2. Implementation map (packet item -> code)

- P9-01/02 inputs: `run_target_rate(..., gate_id=...)` normalizes the
  gate first (`_normalize_gate_id`; `None` maps to P8 for injected-seam
  backward compatibility, unknown raises), then refuses an existing
  `--out-dir`, validates the frozen scalars and the gate-specific grids
  (`_gate_grids`), validates seed lists including P9 prior-stream
  disjointness (`_check_seed_lists(..., gate_id)`), then loads and
  validates the P7 orders file BEFORE the NPZ stat check and the single
  accepted `load_v25_channel_counts` call; read/attempt `1/1` with
  `open_count 1` are recorded at that content open. `main` refuses a
  missing `--gate-id` before any artifact access; the parser enforces the
  closed choice (`choices=[p8, p9]`, invalid raises `SystemExit`).
- Support rule and preconditions: the accepted P7 helpers, unchanged;
  failure raises `TargetPopulationContractError` before any SC call and
  before the output root is created.
- P9-03 SCREEN: `sample_shared_blocks` unchanged; `screen_grid` called
  with the explicit P9 grids yields the exact 56 points in K1-major
  order; `run_rate_arm(..., gate_id)` threads the gate into the P9-domain
  tag seed (`arm_seed_bits(..., gate_id)`); `screen_eligibility` unchanged
  (192 shape, 188 boundary); `select_point` unchanged (lexicographic
  minimum over eligible only).
- P9-04 CONFIRM: disjoint streams asserted plus P9 prior-overlap refusal;
  `run_confirm_pair(..., gate_id)` runs only the selected point's
  empirical arm plus the BEC control at the same K1/K2; confirm gates are
  `>= 618/640` + Wilson `>= 0.95` + decision-path zeros.
- P9-05: `5*(K1+K2)+64` / `2623` accounting with partial-invocation
  semantics (P7/P8 rule), including zero-K arms; phase/arm-literal
  `recount_events` unchanged (event ids carry no protocol); frame keys
  carry the gate prefix (`_gate_frame_prefix`); five scalar-only files
  plus persisted `gate_id`; planning-only `f`.
- P9-06/07: thirteen-flag CLI (`--gate-id` first, then the 12
  P8-equivalent fields with P9 values); frozen command in `P9_FREEZE.md`
  §7 is the packet command verbatim.

## 3. Key implementation decisions (review items)

1. **Gate-id optionality split (deliberate).** The parser declares
   `--gate-id` as optional (`default=None`) so the 12 accepted P8 parser
   tests still parse; `main` refuses `None` with return 2 before any
   artifact access, so every production invocation requires it. The
   Python seam `run_target_rate(gate_id=P8_GATE_ID)` defaults to P8 so
   all accepted P8 injected tests run unchanged. The reviewer must
   confirm this split satisfies "REQUIRED closed-choice" at the execution
   level while preserving the 240-test predecessor suite.
2. **Zero-K design (correct by construction).** Empty disclosure slices
   (`order[:0]`) flow through the unchanged SC path; L2 still invokes
   (every L1 candidate must invoke L2), the tag still invokes, so
   `(0,0)` discloses exactly 64 bits and `K1=0`/`K2=0` disclose zero for
   that layer. Verified by the focused zero-K test over `(0,0)`, `(0,4)`,
   `(3,0)` at `n=8` with event-level bit checks.
3. **Domain-separation values.** P9 protocol
   `nbpolar-p9-lower-rate-boundary-screen-confirm` vs P8
   `nbpolar-p8-target-rate-screen-confirm`; P9 mode
   `static-lower-rate-boundary-screen-confirm` vs P8
   `static-target-rate-screen-confirm`; P9 seed prefix
   `nbpolar-p9-lower-rate-boundary-seed` vs P8
   `nbpolar-p8-target-rate-seed`; P9 frame prefix
   `nbpolar-p9-lower-rate-boundary` vs P8 `nbpolar-p8-target-rate`;
   P9 labels `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` /
   `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` /
   `TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED` vs the P8 triple;
   `BLOCKED(<gate>)` format shared. Grid mismatch in either direction is
   refused, so P8 identifiers cannot silently enter the P9 path.
4. **Prior-stream disjointness (P9-only).** `_check_seed_lists` gains a
   `gate_id` parameter; only the P9 gate additionally refuses overlap
   with `P9_PRIOR_OFFICIAL_STREAMS` (`1650..52`, `1660..64`, `1680..82`,
   `1690..94`). The P8 path performs only the original
   distinct/disjoint checks, preserving behavior.
5. **NCONFIGS gating.** `_integrity_gates` takes `gate_id` and requires
   `len(screen_configs) == 56` for P9 vs `35` for P8; `run_target_rate`
   asserts the matching grid length. `shape_is_frozen` compares against
   the gate-specific frozen seeds/grids.
6. **Test seams unchanged.** `counts=`/`orders=`/`expected_entropies=`/
   `tag_fn=` remain keyword-only; the frozen CLI exposes none of them.
   Seed lists remain unpinned (frozenness gates the candidate label via
   `shape_is_frozen`), mirroring P8.
7. **Reuse, not redefinition.** Support, preconditions, sampler, buckets,
   Wilson, Toeplitz tag, transcript canonicalization, prior gather
   helpers and `sc_decode` are imported from accepted modules; only the
   gate selector, P9 constants, gate-threaded seed/frame derivation and
   gate-aware plan/report/labels are new.

## 4. Test evidence (pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`)

Focused file (12 P8 preserved + 12 new P9; grid completeness, zero-K,
Wilson boundary, selection ties/empty, isolation/prior-disjointness,
shared-block identity + selected-only + pairing, no-eligible path,
accounting/recount with zero-K, domain separation, CLI/refusals,
truth/buckets, no-forbidden-marker/empty-cwd-import):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_target_rate.py -q \
  -p no:cacheprovider --basetemp=/tmp/p9_focus_tmp2
# 24 passed, 1 warning in 15.12s
```

Full accepted NB-Polar suite (240 predecessor + 12 new = 252):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_*.py -q \
  -p no:cacheprovider --basetemp=/tmp/p9_full_tmp1
# 252 passed, 1 warning in 117.34s
```

Additional structural checks performed by the focused tests: injected
runs never call `load_v25_channel_counts`; the real output root and the
NPZ path are never referenced from tests (split-literal checks); frozen
P9 streams are read from constants only and never sampled (fresh seeds
`>= 2026091730` for every sampling call); every SCREEN config sees the
identical shared block objects across all 56; CONFIRM runs only the
selected K1/K2 on disjoint streams; P9 outputs carry no P8 protocol,
prefix or label.

## 5. Boundary statement (this session)

- The V25 NPZ was **not opened**; only `st_size` metadata was read
  (`25166822` bytes, matching `EXPECTED_NPZ_BYTES`).
- The P7 `construction_orders.json` was not read in this wave (no JSON
  open needed beyond the accepted P8 evidence cited for identity).
- The frozen gate was **not run**; no output root exists.
- Artifact reads consumed: **0/1**. Scientific attempts consumed: **0/1**
  (`STATUS.yaml`: `artifact_reads_used: 0`, `attempts_used: 0`).
- No Model-F/parquet/TTBin/held-out/raw/EVAL access, no `N>256`, no
  APP/SCL/FWHT path, no production benchmark, no commit or push.
- The real root
  `.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/`
  is absent and must remain absent until an authorized execution.

## 6. Open items for the Pre-EXECUTE reviewer

1. Confirm the refusal-ordering reading in `P9_FREEZE.md` §3.1
   (gate-id/out-dir/grid/seed/orders/stat before open; preconditions
   after open but before any SC call).
2. Confirm the frozen command text in `P9_FREEZE.md` §7 is byte-equivalent
   to the packet command (13 flags, gate-id first, with the verbatim P9
   values).
3. Confirm the target root is absent, the orders file carries the frozen
   digest, and the NPZ path/size are the registered ones.
4. Confirm the P9 streams are fresh and disjoint from all prior official
   streams, and the parser/`main` gate-id split (item §3.1) is
   acceptable.
5. Confirm the decision-path scope of the zero gates and the both-arms
   zero CONFIRM requirement carry over unchanged to the 56-point grid.
6. Confirm the 2 GiB/3600 s envelope for the one-shot execution (≈23k SC
   calls at N=256 GF32: 10752x2 SCREEN + 1280x2 CONFIRM).
7. Confirm zero-K accounting (`(0,0)` = 64-bit tag-only) and the
   no-interpolation rule for boundary selections.
