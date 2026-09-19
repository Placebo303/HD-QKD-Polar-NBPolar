# P20G implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/plus1024_independent_session.py` | thin three-arm independent-session runner (new; ~2620 lines incl. docstrings/gates/CLI, derived as a P20F clone) |
| `comparison_bench/tests/test_nbpolar_plus1024_independent_session.py` | 36 focused injected tests (new; ~1530 lines) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20g/spec.md` | P20G OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20G section) | P20G task section appended to the umbrella change (edit; no seed literals in the tracked file, same bar as P20C/P20E/P20F) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/P20G_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/P20G_IMPLEMENTATION_NOTES.md` | this file (new) |

`git status` shows exactly one tracked modification outside the new
files: the `tasks.md` P20G section above. In particular: no change to
`operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
`plus1024_extension.py`, `bounded_search_diagnostic.py`,
`construction.py`, `prior.py`, `sc.py`, or any accepted evidence root.
(The worktree carries pre-existing untracked files and unrelated tracked
dirt from earlier cycles; none of it was touched in this stage.)

## 2. Read-only reuse inventory (§12)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (B0 and B1 share the seam; B1 passes k2=7516
  on the same frozen L2 order object — the order-prefix extension needs
  no new logic since the accepted helper slices `l2_order[:k2]`) —
  `is operational_f13` object; `_decode_layer`,
  `classify_operational_outcome` likewise.
- `run_oracle_control_block` + `OracleControlResult` (B2) — `is
  holdout_backoff_diagnostic` objects; P20G tag domain injected through
  the documented `tag_fn` closure (same trick P19/P20B/P20C/P20E/P20F used).
- `verify_predecessor_construction` (`is` replication module),
  `verify_split_manifest` + `holdout_nll_bits` / `raw_symbol_error_rate`
  (`is` microcheck module), `form_holdout_blocks` (imported for the pin
  proof; never called on DEV ranges).
- `SOURCE_IDS` (accepted session-tag vocabulary: `1p5M` maps to
  `type2_1p5M_20260121_183806`), `target_preconditions`,
  `load_v25_channel_counts` (returns per-source arrays keyed `1M` /
  `1p5M` / `2M`; the runner reads the `1p5M` array), `load_pairs_table`
  (+ `normalize_pair_columns`), `polar_transform`, `make_gf32`,
  `toeplitz_tag`, `build_p1_metrics`, `gather_p2_metrics`,
  `probs_to_symbol_metric`, `seed_bits_for`, `labels_to_bits`,
  `DISCLOSED_BITS_PER_COORDINATE`, `LABEL_SCALE`, `TAG_BITS` — by module
  contract, never reimplemented.
- Zero-tuning reference: the P20F module `plus1024_extension` is
  imported read-only by ONE test (`test_zero_tuning_carry_over_from_p20f`)
  to pin K/floor/caps/budgets/arm/provenance/rule/gate equality; the
  runner itself shares no code path with it (same arms via the same
  accepted seams, not via the P20F module).
- Banned from the new module (asserted absent): sampling/RNG, genie,
  K-budget selection, analytic orders, Wilson, SCL/list/FWHT/APP,
  smoothing, P16/P17/P18/P19/P20B/P20C/P20E/P20F seed helpers, HOLD flags,
  every search token (`run_search_block`, `build_search_candidates`,
  `FROZEN_SEARCH_BOUND_M`, `NEIGHBORHOOD_ID`, `SEARCH_RULE`,
  `rescores_used`, `search_found_better`, `selected_source`, rescoring,
  argmin selection), plus the P20F module/token names themselves
  (`plus1024_extension`, `Plus1024Extension`).

## 3. New logic and why it is local (not a shared change)

- `form_dev_blocks`: the accepted `form_holdout_blocks` is HOLD-range
  pinned by fail-closed equality (`_check_frame_range`) and the HOLD
  blocks are closed, so the TRAIN formation mirrors its validation
  line-for-line under P20G ranges. Proven by test: calling the accepted
  helper with DEV ranges raises.
- `verify_dev_manifest`: the accepted `verify_split_manifest` is
  source-pinned to 1M by fail-closed equality (it refuses any other
  source), so the 1.5M manifest check mirrors its validation
  line-for-line under P20G source/pins (schema + 1.5M tag + TRAIN
  1660/424960 + VAL 553/141568 + HOLD 554/141824). Proven by test:
  calling the accepted helper with source `1p5M` raises.
- B0/B1 unified operational branch: both arms call the shared
  `run_operational_block` with their registered (k1, k2); the +1024 step
  is the arm-table constant `FROZEN_K2_B1`, never a CLI flag. Order
  identity across arms is pinned by tests (same L2 order object reaches
  the seam for B0 and B1).
- `l2_prefix_positions`: pure view helper documenting the prefix rule
  (`order[:k2]`); B1's first 6492 positions equal the base prefix by
  construction (pinned by test).
- `verify_dev_source_identity`: the double gate's FIRST half (pure
  string/constant check, no I/O). The DEV content-open path must equal
  the frozen 1.5M pairs path (derived from the accepted 1M path by
  session-tag substitution, so no new path literal breaks the
  no-production-path source ban); the 1M full-pool path and the reserved
  2M path refuse with their own messages; any other path refuses. The
  size/sha pins are build-manifest provenance constants recorded in the
  plan/identity docs; the size is additionally enforced from stat before
  the content open at run level. Gate order (a)→(b) is pinned by tests
  (a 1M/2M/foreign path refuses before any root, ahead of every range
  check).
- `verify_dev_block_identity`: the double gate's SECOND half —
  intra-file VAL (1660..2212, checked first) then HOLD (2213..2766)
  disjointness, plus the P20G literal pins. Ordering is pinned by tests
  (a remainder touching both pools reports VAL first).
  `form_dev_blocks` repeats the intra-file overlap checks on the
  computed ranges.
- Declared-remainder measurement (same structural pattern as
  P20E/P20F): the remainder (384..1659, 1276 frames / 326656 pairs)
  lies OUTSIDE the frozen DEV selection (0..383) by design, so (i) the
  closure check pins `remainder starts where the three DEV blocks end`
  (383 → 384), and (ii) remainder presence/span is measured from the
  UNFILTERED pool before DEV slicing — counted, never decoded.
  Remainder per-frame/per-row shape is deliberately not re-validated
  (unused region; presence + span + row-count is the proportionate
  check). Covered by
  `test_declared_remainder_measured_and_fail_closed` (drop/shrink the
  remainder → `BLOCKED(blocks_exact_with_declared_remainder)`).
- `candidate_nll_bits`: retained as a pure diagnostic scorer (feeds the
  per-record candidate-H/true-H NLL fields); all search selection use is
  deleted.
- Gates mirror the accepted P19/P20B/P20C/P20E/P20F gate semantics
  field-for-field (derived SC/tag recomputation, per-record bits
  formula, file inventory + jsonl count, mode-aware one-open accounting,
  stat/registration/resource checks) with P20G names/counts (9 records,
  15 SC, 9 tags, block-major slot order, new-session population,
  per-arm K pins + B1 disclosure triple, double gate). The 20
  `INTEGRITY_GATE_ORDER` names are byte-identical to P20E/P20F (pinned
  by the carry-over test); the cross-file source pin folds into the
  frozen `dev_block_range_identity` gate alongside the intra-file pin.
- `DISCLOSURE_RULE` is byte-identical to P20F (pinned by the carry-over
  test): the step description is unchanged; the normative exclusion of
  the 1M pools / 2M file / 1.5M VAL/HOLD lives in the double gate and
  `DEV_BLOCK_RULE`, not in the step prose.

## 4. Frozen quadruple

- carry-over: ΔK2 = +1024 (`FROZEN_L2_DELTA_K2`), order-prefix extension
  (B1 K2 7516, K_total 7835; key-bit delta +5120 vs base), prior / floor
  / construction-order / kernel / representation / SC byte-identical to
  P20C/P20E/P20F (pinned literally against the P20F module); Model-F
  cross-session use recorded as a to-be-verified assumption for
  Pre-EXECUTE with no refit fallback; no tag-guided selection, no
  evidence reuse, no post-hoc step-picking, no second step; only the
  new-session population and new tag domain differ.
- population: 1.5M TRAIN prefix 0..383, blocks
  0..127/128..255/256..383, remainder 384..1659 (1276 frames /
  326656 pairs) never used (counted, never decoded), intra-file VAL
  1660..2212 + HOLD 2213..2766 disjoint by the second-half gate
  (VAL first); 1M full pool + reserved 2M file excluded by the
  first-half source-tag+digest gate (path + 1869178 B size pin, sha
  `ca351e52…a06b` provenance pin); file/digest identity from JSON
  build-manifest provenance, never a content open.
- cap: 34119 base / 39239 B1 / 32524 control key bits per block, 327743
  public bits per tag; 34119/327680 = 0.10412292 and
  39239/327680 = 0.11974792 of raw; planned totals 317646 key /
  2949687 public; recount mismatch 0 or BLOCKED.
- command: §10 of `P20G_FREEZE.md` verbatim (16 required flags,
  `--source 1p5M`, block-major B0/B1/B2, 600 s / 2 GiB / 1-thread env).

## 5. Test commands and results (real counts)

Stage-A suite (pinned interpreter, fresh temp root, no cache):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
comparison_bench/tests/test_nbpolar_plus1024_independent_session.py -q
-p no:cacheprovider --basetemp=$PWD/workspace/p20g/9f3a2c1e-7b4d-4a1e-9c2e-5f8a1d4b6e01`
→ **36/36 green** (~26 s).

Packet-scoped predecessors (same settings, fresh basetemp
`workspace/p20g/7a1e5c82-4b4f-4d9a-8e6c-2b7f0a9d5c44`):
`test_nbpolar_plus1024_extension.py` (36) +
`test_nbpolar_plus1024_confirmation.py` (36) +
`test_nbpolar_l2_disclosure_backoff.py` (34) +
`test_nbpolar_bounded_search_diagnostic.py` (34) +
`test_nbpolar_operational_f13.py` (29) +
`test_nbpolar_operational_f13_replication.py` (25) +
`test_nbpolar_holdout_microcheck.py` (26) +
`test_nbpolar_holdout_backoff_diagnostic.py` (33) → **253/253 green**
(~911 s; the predecessor suites include real-N=32768 SC runs;
per-file collection re-verified: 36/36/34/34/29/25/26/33).

No shared predecessor code was changed, so the full NB-Polar suite was
not run. Failing/skipped: none. Bugs found during implementation (all
fixed, none touching shared code): the first real-mode-test pass failed
2/36 because the cross-file source pin literal-checked the patchable
size constant against its frozen value — the runtime pin now checks
only the never-patched source vocabulary (literals live in the
frozen-constants test; enforcement at run level via the stat-size
check); the 1.5M/2M path derivation initially used full path literals
that tripped the no-production-path source ban — paths are now derived
from the accepted 1M path by session-tag substitution.

## 6. Protected-open audit (must be zero)

- Module guards `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are
  False at Stage-A close.
- No NPZ/parquet content open or stat in this stage. Only JSON
  provenance reads: P16 construction file (digest recomputed, §3 of the
  freeze), the split manifest (1.5M TRAIN/VAL/HOLD pools, §3 of the
  freeze) and the build manifest (1.5M file size/sha pins, §3 of the
  freeze) — per P18/P19/P20B/P20C/P20E/P20F Stage-A precedent, not
  TRAIN/HOLD content reads.
- The 2M file was never opened, statted, listed, or read in any form;
  the 2M refusal path is a string literal only (asserted refusal-tested
  with guards still False).
- Real-mode tests used throwaway stub files with patched loaders only;
  guard globals were restored afterwards.
- Stage-B root `independent_session/` does not exist.
- This checkout carries no `.venv`; Stage-A pytest used the neighboring
  frozen-command-family interpreter
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, same path the
  frozen Stage-B command names) — no install, no network, no repo write
  outside the fresh temp root.

## 7. Scope concerns encountered (reported, not fixed beyond freeze)

- Manifest JSON gives pool counts, not frame numbering; TRAIN base 0
  follows from the frozen split code (time-ordered first-60%) +
  same-pipeline parity with the accepted 1M 0-based layout, and the
  P20G DEV prefix 0..383 is the packet-expected pattern at that base.
  The runner fail-closes on any layout drift
  (`dev_population_exact` + double gate), so a wrong base blocks before
  any SC call. Pre-EXECUTE owns the cross-session isolation
  adjudication (§4 of the freeze).
- The 1.5M sha is a recorded provenance pin (build manifest → frozen
  plan/identity docs), enforced operationally by path-string + stat-size
  checks pre-open; it is not recomputed from content (that would be a
  second read outside the accepted loader seam).
- The packet's "~11.97%" B1 ratio bar vs the exact 39239/327680 =
  0.11974792: exact value frozen and reported; the bar holds (far below
  raw).
- For B2, candidate-H NLL equals true-H NLL by construction (truth
  conditioning); both fields are recorded identically, not claimed as
  independent evidence (same convention as P19/P20B/P20C/P20E/P20F).
- Remainder rows are counted, never decoded; per-frame shape inside the
  remainder is not re-validated (§3 rationale).
- The `DISCLOSURE_RULE` string is byte-identical to P20F by design (R1
  pin); the P20G-specific exclusions live in the double gate and
  `DEV_BLOCK_RULE` (§3 rationale).

## 8. Not run in this stage

Independent Pre-EXECUTE review, Stage-B execution, Pre-RESULT review,
memory triage, main-thread acceptance. The operator does not accept its
own work and does not authorize Stage B.
