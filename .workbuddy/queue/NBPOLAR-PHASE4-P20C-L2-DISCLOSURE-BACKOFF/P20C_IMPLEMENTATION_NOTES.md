# P20C implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_disclosure_backoff.py` | thin three-arm runner (new; ~2400 lines incl. docstrings/gates/CLI) |
| `comparison_bench/tests/test_nbpolar_l2_disclosure_backoff.py` | 34 focused injected tests (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20c/spec.md` | P20C OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20C section) | P20C task section appended to the umbrella change (edit) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/P20C_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/P20C_IMPLEMENTATION_NOTES.md` | this file (new) |

`git status` shows no modification to any file outside this manifest
(plus pre-existing unrelated worktree modifications that were already
present and were not touched). In particular: no change to
`operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`bounded_search_diagnostic.py`, `construction.py`, `prior.py`, `sc.py`,
or any accepted evidence root.

## 2. Read-only reuse inventory (§12)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (B0 and B1 share the seam; B1 passes k2=7516
  on the same frozen L2 order object — the order-prefix extension needs
  no new logic since the accepted helper slices `l2_order[:k2]`) —
  `is operational_f13` object; `_decode_layer`,
  `classify_operational_outcome` likewise.
- `run_oracle_control_block` + `OracleControlResult` (B2) — `is
  holdout_backoff_diagnostic` objects; P20C tag domain injected through
  the documented `tag_fn` closure (same trick P19/P20B used).
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
- Banned from the new module (asserted absent): sampling/RNG, genie,
  K-budget selection, analytic orders, Wilson, SCL/list/FWHT/APP,
  smoothing, P16/P17/P18/P19/P20B seed helpers, HOLD flags, every search
  token (`run_search_block`, `build_search_candidates`,
  `FROZEN_SEARCH_BOUND_M`, `NEIGHBORHOOD_ID`, `SEARCH_RULE`,
  `rescores_used`, `search_found_better`, `selected_source`, rescoring,
  argmin selection).

## 3. New logic and why it is local (not a shared change)

- `form_dev_blocks`: the accepted `form_holdout_blocks` is HOLD-range
  pinned by fail-closed equality (`_check_frame_range`) and the HOLD
  blocks are closed, so the TRAIN formation mirrors its validation
  line-for-line under P20C ranges. Proven by test: calling the accepted
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
  1200/307200 pool requirement from the same manifest.
- `verify_dev_block_identity`: dual fail-closed overlap gate — closed
  HOLD 1600..1983 checked first, then consumed VAL 1200..1599 — plus the
  P20C literal pins. `form_dev_blocks` repeats both overlap checks on
  the computed ranges.
- `candidate_nll_bits`: retained as a pure diagnostic scorer (feeds the
  per-record candidate-H/true-H NLL fields); all search selection use is
  deleted.
- Gates mirror the accepted P19/P20B gate semantics field-for-field
  (derived SC/tag recomputation, per-record bits formula, file inventory
  + jsonl count, mode-aware one-open accounting, stat/registration/
  resource checks) with P20C names/counts (9 records, 15 SC, 9 tags,
  block-major slot order, TRAIN population, per-arm K pins + B1
  disclosure triple, dual overlap gate).

## 4. Frozen quadruple

- step: ΔK2 = +1024 (`FROZEN_L2_DELTA_K2`), order-prefix extension
  (B1 K2 7516, K_total 7835; key-bit delta +5120 vs base), frozen before
  execution, unchanged after; no tag-guided selection, no evidence
  reuse, no post-hoc step-picking, no second step.
- population: same-file TRAIN 0..1199, blocks 0..127/128..255/256..383,
  remainder 384..1199 (816 frames / 208896 pairs) never used, closed
  1600..1983 and consumed 1200..1599 disjoint by dual fail-closed gate;
  same file/digest identity as P18/P19/P20B (no new digest).
- cap: 34119 base / 39239 B1 / 32524 control key bits per block, 327743
  public bits per tag; 34119/327680 = 0.10412292 and
  39239/327680 = 0.11974792 of raw; planned totals 317646 key /
  2949687 public; recount mismatch 0 or BLOCKED.
- command: §10 of `P20C_FREEZE.md` verbatim (16 required flags,
  block-major B0/B1/B2, 600 s / 2 GiB / 1-thread env).

## 5. Test commands and results (real counts)

Stage-A suite (pinned interpreter, fresh temp root, no cache):
`.../.venv/bin/python -m pytest
comparison_bench/tests/test_nbpolar_l2_disclosure_backoff.py -q
-p no:cacheprovider --basetemp=$PWD/workspace/p20c/<uuid>` → **34/34
green** (~28 s).

Packet-scoped predecessors (same settings, fresh basetemp):
`test_nbpolar_bounded_search_diagnostic.py` (34) +
`test_nbpolar_operational_f13.py` (29) +
`test_nbpolar_operational_f13_replication.py` (25) +
`test_nbpolar_holdout_microcheck.py` (26) +
`test_nbpolar_holdout_backoff_diagnostic.py` (33) → **147/147 green**
(~837 s; the predecessor suites include real-N=32768 SC runs).

No shared predecessor code was changed, so the full NB-Polar suite was
not run. Failing/skipped: none. Bugs found during implementation (all
fixed, none touching shared code): scripted fake raising before
consuming its script (all six operational records failed identically —
fixed by consuming the script before the raise); oracle-fake
`low_hat=None` leaving oracle diagnostics empty (test now asserts
populated diagnostics on operational records, key presence on oracle —
same convention as P20B); branch merge dropping the P20A
`MemoryError` re-raise marker comments (restored); test asserting an
absent `B1b` token while the freeze rule documents the forbidding
mention (test now pins exactly one forbidding mention).

## 6. Protected-open audit (must be zero)

- Module guards `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are
  False at Stage-A close.
- No NPZ/parquet content open or stat in this stage. Only JSON
  provenance reads: P16 construction file (digest recomputed, §3 of the
  freeze) and the split manifest (TRAIN/VAL/HOLD pools, §3 of the
  freeze) — per P18/P19/P20B Stage-A precedent, not TRAIN/HOLD content
  reads.
- Real-mode tests used throwaway stub files with patched loaders only;
  guard globals were restored afterwards.
- Stage-B root `l2_disclosure_backoff/` does not exist.

## 7. Scope concerns encountered (reported, not fixed beyond freeze)

- Manifest JSON gives pool counts, not frame numbering; TRAIN 0..1199
  follows by elimination from the accepted VAL 1200..1599 and HOLD
  1600..1999 ranges within the 2000-frame file. The runner fail-closes
  on any layout drift (`dev_population_exact` + dual overlap gate), so
  a wrong inference blocks before any SC call. Pre-EXECUTE owns the
  isolation adjudication (§4 of the freeze).
- The packet's "~11.98%" B1 ratio bar vs the exact 39239/327680 =
  0.11974792 (~11.97%): exact value frozen and reported; the bar holds
  either way (far below raw).
- For B2, candidate-H NLL equals true-H NLL by construction (truth
  conditioning); both fields are recorded identically, not claimed as
  independent evidence (same convention as P19/P20B).

## 8. Not run in this stage

Independent Pre-EXECUTE review, Stage-B execution, Pre-RESULT review,
memory triage, main-thread acceptance. The operator does not accept its
own work and does not authorize Stage B.
