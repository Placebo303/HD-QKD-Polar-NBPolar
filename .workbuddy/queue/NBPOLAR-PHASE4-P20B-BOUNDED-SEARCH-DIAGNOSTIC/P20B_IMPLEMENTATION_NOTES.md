# P20B implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/bounded_search_diagnostic.py` | thin three-arm runner (new; ~2500 lines incl. docstrings/gates/CLI) |
| `comparison_bench/tests/test_nbpolar_bounded_search_diagnostic.py` | 34 focused injected tests (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20b/spec.md` | P20B OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20B section) | P20B task section appended to the umbrella change (edit) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/P20B_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/P20B_IMPLEMENTATION_NOTES.md` | this file (new) |

`git status` shows no modification to any file outside this manifest
(plus pre-existing unrelated worktree modifications that were already
present and were not touched). In particular: no change to
`operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`construction.py`, `prior.py`, `sc.py`, or any accepted evidence root.

## 2. Read-only reuse inventory (§12)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (S0), `_decode_layer` (S1 greedy prefix),
  `classify_operational_outcome` (S1) — `is operational_f13` objects.
- `run_oracle_control_block` + `OracleControlResult` (S2) — `is
  holdout_backoff_diagnostic` objects; P20B tag domain injected through
  the documented `tag_fn` closure (same trick P19 used for the P16 seed).
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
  smoothing, P16/P17/P18/P19 seed helpers, HOLD flags.

## 3. New logic and why it is local (not a shared change)

- `form_dev_blocks`: the accepted `form_holdout_blocks` is HOLD-range
  pinned by fail-closed equality (`_check_frame_range`) and the HOLD
  blocks are closed, so the VAL formation mirrors its validation
  line-for-line under P20B ranges. Proven by test: calling the accepted
  helper with DEV ranges raises.
- `run_search_block` (S1): calls the shared `_decode_layer` for the two
  frozen SC calls (identical inputs/disclosure as S0) but defers tagging
  so the record carries exactly one final tag; rescoring
  (`build_search_candidates` + `candidate_nll_bits`) is pure scoring on
  decoder posteriors. Equality with S0's greedy path is pinned by tests
  (full-disclosure anchor: identical hats; selection independent of tag
  closure).
- `verify_dev_manifest`: accepted manifest check plus the VAL 400/102400
  pool requirement from the same manifest.
- `candidate_nll_bits`: inf-tolerant twin of `holdout_nll_bits` (search
  needs a total order; greedy always scores finite). Both exist; the
  accepted one is reused for truth-indexed block scoring.
- Gates mirror the accepted P19 gate semantics field-for-field (derived
  SC/tag recomputation, per-record bits formula, file inventory + jsonl
  count, mode-aware one-open accounting, stat/registration/resource
  checks) with P20B names/counts (9 records, 15 SC, 9 tags, block-major
  slot order, VAL population).

## 4. Frozen quadruple

- bound: M=8 (`FROZEN_SEARCH_BOUND_M`), neighborhood `P20B-NBHD-1`
  (Hamming-1 U-domain, margin-ranked, rescore-only), one coherent NLL
  model, no tag-guided selection, no evidence reuse.
- population: VAL 1200..1599, blocks 1200..1327/1328..1455/1456..1583,
  remainder 1584..1599 unused, closed 1600..1983 disjoint by fail-closed
  gate; same file/digest identity as P18/P19 (no new digest).
- cap: 34119 operational / 32524 control key bits per block, 327743
  public bits per tag; 34119/327680 = 0.10412292 of raw; recount
  mismatch 0 or BLOCKED.
- command: §10 of `P20B_FREEZE.md` verbatim (16 required flags,
  block-major S0/S1/S2, 600 s / 2 GiB / 1-thread env).

## 5. Test commands and results (real counts)

Stage-A suite (pinned interpreter, fresh temp root, no cache):
`.../.venv/bin/python -m pytest
comparison_bench/tests/test_nbpolar_bounded_search_diagnostic.py -q
-p no:cacheprovider --basetemp=/tmp/p20b-<uuid>` → **34/34 green**.

Packet-scoped predecessors (same settings, fresh basetemp):
`test_nbpolar_operational_f13.py` +
`test_nbpolar_operational_f13_replication.py` +
`test_nbpolar_holdout_microcheck.py` +
`test_nbpolar_holdout_backoff_diagnostic.py` → **113/113 green**.

No shared predecessor code was changed, so the full NB-Polar suite was
not run. Failing/skipped: none. Bugs found during implementation (all
fixed, none touching shared code): `inf*0=nan` in the inf-tolerant NLL
sum; missing `block_index` in records; tuple-vs-dict gate plumbing;
`persist()` arity; gate schema drift vs the accepted record (fixed by
mirroring P19 gates field-for-field); test-seam SC double counting;
tag_fn true+hat evaluation pair (accepted pattern, tests corrected).

## 6. Protected-open audit (must be zero)

- Module guards `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are
  False at Stage-A close.
- No NPZ/parquet content open or stat in this stage. Only JSON
  provenance reads: P16 construction file (digest recomputed, §3 of the
  freeze) and the split manifest (+ the 512000-row inventory figure used
  for the VAL-layout rationale) — per P18/P19 Stage-A precedent, not
  TRAIN/HOLD content reads.
- Directory listings of the two registered input directories were made
  once during inventory (metadata only, no file opened); no further
  protected-path filesystem access after that point.
- Real-mode tests used throwaway stub files with patched loaders only;
  guard globals were restored afterwards.
- Stage-B root `bounded_search_diagnostic/` does not exist.

## 7. Scope concerns encountered (reported, not fixed beyond freeze)

- Same-file fresh HOLD blocks at N=32768 are arithmetically impossible
  (only 16 remainder frames outside closed 1600..1983); the freeze
  declares the VAL pool as the equivalent replacement (§4 of the
  freeze). Pre-EXECUTE owns approval; the runner fail-closes
  (`dev_population_exact`) if the layout differs.
- S1 L1 alternates are rescored with the greedy L2 (no re-decode by
  design freeze); documented in `SEARCH_RULE`, not a defect.
- For S2, candidate-H NLL equals true-H NLL by construction (truth
  conditioning); both fields are recorded identically, not claimed as
  independent evidence.

## 8. Not run in this stage

Independent Pre-EXECUTE review, Stage-B execution, Pre-RESULT review,
memory triage, main-thread acceptance. The operator does not accept its
own work and does not authorize Stage B.
