# P20F implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/plus1024_extension.py` | thin three-arm extension runner (new; 2489 lines incl. docstrings/gates/CLI, derived as a P20E clone) |
| `comparison_bench/tests/test_nbpolar_plus1024_extension.py` | 36 focused injected tests (new; 1495 lines) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20f/spec.md` | P20F OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20F section) | P20F task section appended to the umbrella change (edit; no seed literals in the tracked file, same bar as P20C/P20E) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/P20F_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/P20F_IMPLEMENTATION_NOTES.md` | this file (new) |

`git status` shows exactly one tracked modification outside the new
files: the `tasks.md` P20F section above. In particular: no change to
`operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
`bounded_search_diagnostic.py`, `construction.py`, `prior.py`, `sc.py`,
or any accepted evidence root. (The worktree carries pre-existing
untracked files and unrelated tracked dirt from earlier cycles; none of
it was touched in this stage.)

## 2. Read-only reuse inventory (§12)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (B0 and B1 share the seam; B1 passes k2=7516
  on the same frozen L2 order object — the order-prefix extension needs
  no new logic since the accepted helper slices `l2_order[:k2]`) —
  `is operational_f13` object; `_decode_layer`,
  `classify_operational_outcome` likewise.
- `run_oracle_control_block` + `OracleControlResult` (B2) — `is
  holdout_backoff_diagnostic` objects; P20F tag domain injected through
  the documented `tag_fn` closure (same trick P19/P20B/P20C/P20E used).
- `verify_predecessor_construction` (`is` replication module),
  `verify_split_manifest` / `holdout_nll_bits` / `raw_symbol_error_rate`
  (`is` microcheck module), `form_holdout_blocks` (imported for the pin
  proof; never called on DEV ranges).
- `target_preconditions`, `load_v25_channel_counts`, `load_pairs_table`
  (+ `normalize_pair_columns`), `polar_transform`, `make_gf32`,
  `toeplitz_tag`, `build_p1_metrics`, `gather_p2_metrics`,
  `probs_to_symbol_metric`, `seed_bits_for`, `labels_to_bits`,
  `DISCLOSED_BITS_PER_COORDINATE`, `LABEL_SCALE`, `TAG_BITS` — by module
  contract, never reimplemented.
- Zero-tuning reference: the P20E module `plus1024_confirmation` is
  imported read-only by ONE test (`test_zero_tuning_carry_over_from_p20e`)
  to pin K/floor/caps/budgets/arm/provenance/rule/gate equality; the
  runner itself shares no code path with it (same arms via the same
  accepted seams, not via the P20E module).
- Banned from the new module (asserted absent): sampling/RNG, genie,
  K-budget selection, analytic orders, Wilson, SCL/list/FWHT/APP,
  smoothing, P16/P17/P18/P19/P20B/P20C/P20E seed helpers, HOLD flags, every
  search token (`run_search_block`, `build_search_candidates`,
  `FROZEN_SEARCH_BOUND_M`, `NEIGHBORHOOD_ID`, `SEARCH_RULE`,
  `rescores_used`, `search_found_better`, `selected_source`, rescoring,
  argmin selection), plus the P20E module/token names themselves
  (`plus1024_confirmation`, `Plus1024Confirmation`).

## 3. New logic and why it is local (not a shared change)

- `form_dev_blocks`: the accepted `form_holdout_blocks` is HOLD-range
  pinned by fail-closed equality (`_check_frame_range`) and the HOLD
  blocks are closed, so the TRAIN formation mirrors its validation
  line-for-line under P20F ranges. Proven by test: calling the accepted
  helper with DEV ranges raises.
- B0/B1 unified operational branch: both arms call the shared
  `run_operational_block` with their registered (k1, k2); the +1024 step
  is the arm-table constant `FROZEN_K2_B1`, never a CLI flag. Order
  identity across arms is pinned by tests (same L2 order object reaches
  the seam for B0 and B1).
- `l2_prefix_positions`: pure view helper documenting the prefix rule
  (`order[:k2]`); B1's first 6492 positions equal the base prefix by
  construction (pinned by test).
- `verify_dev_manifest`: accepted manifest check plus the TRAIN
  1200/307200 pool requirement from the same manifest (unchanged
  `FROZEN_MANIFEST_TRAIN_*` constants — the manifest pool is unchanged,
  only the DEV subrange is new).
- `verify_dev_block_identity`: QUADRUPLE fail-closed overlap gate —
  consumed P20C DEV 0..383 checked first, then consumed P20E DEV
  384..767, then consumed VAL 1200..1599, then closed HOLD 1600..1983 —
  plus the P20F literal pins. Ordering is pinned by tests (a range
  touching two pools reports the earlier pool). `form_dev_blocks`
  repeats the quadruple overlap checks on the computed ranges.
- Declared-remainder measurement (same structural pattern as P20E):
  P20E's remainder (768..1199) lay OUTSIDE its DEV selection
  (384..767); P20F's remainder (1152..1199, 48 frames / 12288 pairs)
  likewise lies OUTSIDE the frozen DEV selection (768..1151) by design,
  so (i) the closure check pins `remainder starts where the three DEV
  blocks end` (1151 → 1152), and (ii) remainder presence/span is
  measured from the UNFILTERED pool before DEV slicing — counted, never
  decoded. Remainder per-frame/per-row shape is deliberately not
  re-validated (unused region; presence + span + row-count is the
  proportionate check). Covered by
  `test_declared_remainder_measured_and_fail_closed` (drop/shrink the
  remainder → `BLOCKED(blocks_exact_with_declared_remainder)`).
- `candidate_nll_bits`: retained as a pure diagnostic scorer (feeds the
  per-record candidate-H/true-H NLL fields); all search selection use is
  deleted.
- Gates mirror the accepted P19/P20B/P20C/P20E gate semantics
  field-for-field (derived SC/tag recomputation, per-record bits
  formula, file inventory + jsonl count, mode-aware one-open accounting,
  stat/registration/resource checks) with P20F names/counts (9 records,
  15 SC, 9 tags, block-major slot order, new TRAIN-subrange population,
  per-arm K pins + B1 disclosure triple, quadruple overlap gate).

## 4. Frozen quadruple

- carry-over: ΔK2 = +1024 (`FROZEN_L2_DELTA_K2`), order-prefix extension
  (B1 K2 7516, K_total 7835; key-bit delta +5120 vs base), prior / floor
  / construction-order / kernel / representation / SC byte-identical to
  P20C/P20E (pinned literally against the P20E module); no tag-guided
  selection, no evidence reuse, no post-hoc step-picking, no second
  step; only the new-block population and new tag domain differ.
- population: same-file TRAIN subrange 768..1151, blocks
  768..895/896..1023/1024..1151, remainder 1152..1199 (48 frames /
  12288 pairs) never used (counted, never decoded), consumed P20C DEV
  0..383 + consumed P20E DEV 384..767 + consumed VAL 1200..1599 + closed
  HOLD 1600..1983 disjoint by quadruple fail-closed gate (P20C first);
  same file/digest identity as P18/P19/P20B/P20C/P20E (no new digest).
- cap: 34119 base / 39239 B1 / 32524 control key bits per block, 327743
  public bits per tag; 34119/327680 = 0.10412292 and
  39239/327680 = 0.11974792 of raw; planned totals 317646 key /
  2949687 public; recount mismatch 0 or BLOCKED.
- command: §10 of `P20F_FREEZE.md` verbatim (16 required flags,
  block-major B0/B1/B2, 600 s / 2 GiB / 1-thread env), byte-identical to
  the module `FROZEN_COMMAND` (verified by import).

## 5. Test commands and results (real counts)

Stage-A suite (pinned interpreter, fresh temp root, no cache):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
comparison_bench/tests/test_nbpolar_plus1024_extension.py -q
-p no:cacheprovider --basetemp=$PWD/workspace/p20f/3f2c9a41-7e4d-4b1a-9c2e-5f8a1d4b6e01`
→ **36/36 green** (~25 s).

Packet-scoped predecessors (same settings, fresh basetemp
`workspace/p20f/7a1e5c82-3b4f-4d9a-8e6c-2b7f0a9d5c33`):
`test_nbpolar_plus1024_confirmation.py` (36) +
`test_nbpolar_l2_disclosure_backoff.py` (34) +
`test_nbpolar_bounded_search_diagnostic.py` (34) +
`test_nbpolar_operational_f13.py` (29) +
`test_nbpolar_operational_f13_replication.py` (25) +
`test_nbpolar_holdout_microcheck.py` (26) +
`test_nbpolar_holdout_backoff_diagnostic.py` (33) → **217/217 green**
(~911 s; the predecessor suites include real-N=32768 SC runs;
per-file collection re-verified: 36/34/34/29/25/26/33).

No shared predecessor code was changed, so the full NB-Polar suite was
not run. Failing/skipped: none. Bugs found during implementation (all
fixed, none touching shared code): the `__all__` tail still named the
P20E `Plus1024Confirmation*` / `run_plus1024_confirmation` /
`plus1024_confirmation_label` symbols after the class
rename — caught by the repo-wide banned-token grep before any suite
ran; test-seed / gate-order / remainder literals re-pointed to the P20F
2026092201..2207 / 2026092200 domain with the P20E master and P20E test
seeds added to the never-use set.

## 6. Protected-open audit (must be zero)

- Module guards `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are
  False at Stage-A close.
- No NPZ/parquet content open or stat in this stage. Only JSON
  provenance reads: P16 construction file (digest recomputed, §3 of the
  freeze) and the split manifest (TRAIN/VAL/HOLD pools, §3 of the
  freeze) — per P18/P19/P20B/P20C/P20E Stage-A precedent, not TRAIN/HOLD
  content reads.
- Real-mode tests used throwaway stub files with patched loaders only;
  guard globals were restored afterwards.
- Stage-B root `plus1024_extension/` does not exist.
- This checkout carries no `.venv`; Stage-A pytest used the neighboring
  frozen-command-family interpreter
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, same path the
  frozen Stage-B command names) — no install, no network, no repo write
  outside the fresh temp root.

## 7. Scope concerns encountered (reported, not fixed beyond freeze)

- Manifest JSON gives pool counts, not frame numbering; TRAIN 0..1199
  follows by elimination from the accepted VAL 1200..1599 and HOLD
  1600..1999 ranges within the 2000-frame file, and the P20F DEV subrange
  768..1151 is the packet-preregistered enablement of P20E's never-used
  remainder. The runner fail-closes on any layout drift
  (`dev_population_exact` + quadruple overlap gate), so a wrong inference
  blocks before any SC call. Pre-EXECUTE owns the isolation adjudication
  (§4 of the freeze).
- The packet's "~11.97%" B1 ratio bar vs the exact 39239/327680 =
  0.11974792: exact value frozen and reported; the bar holds (far below
  raw).
- For B2, candidate-H NLL equals true-H NLL by construction (truth
  conditioning); both fields are recorded identically, not claimed as
  independent evidence (same convention as P19/P20B/P20C/P20E).
- Remainder rows are counted, never decoded; per-frame shape inside the
  remainder is not re-validated (§3 rationale).
- The 48-frame remainder (1152..1199) is the last same-file TRAIN
  tranche; frames beyond 1199 in this file belong to the consumed VAL
  pool and the closed HOLD range and are refused by the quadruple gate.

## 8. Not run in this stage

Independent Pre-EXECUTE review, Stage-B execution, Pre-RESULT review,
memory triage, main-thread acceptance. The operator does not accept its
own work and does not authorize Stage B.
