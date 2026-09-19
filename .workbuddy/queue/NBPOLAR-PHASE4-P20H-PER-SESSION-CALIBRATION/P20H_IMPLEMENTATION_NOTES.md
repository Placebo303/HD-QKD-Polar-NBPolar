# P20H implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/per_session_calibration.py` | thin Stage-A calibration entrypoint: frozen §3 program (new; ~600 lines incl. docstrings/gates/CLI) |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/plus1024_per_session_confirmation.py` | thin three-arm per-session confirmation runner (new; ~2770 lines, derived as a P20G clone with the §3 prior swap) |
| `comparison_bench/tests/test_nbpolar_per_session_calibration.py` | 17 focused injected calibration tests (new) |
| `comparison_bench/tests/test_nbpolar_plus1024_per_session_confirmation.py` | 36 focused injected runner tests (new; P20G-clone adapted) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20h/spec.md` | P20H OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20H section) | P20H task section appended to the umbrella change (edit; purely additive — zero deletions; no seed literals in tracked files beyond the frozen master/seeds bar) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/` | calibration product, five files from the single declared open (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/P20H_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/P20H_IMPLEMENTATION_NOTES.md` | this file (new) |

`git status` shows exactly one tracked modification by this stage: the
`tasks.md` P20H section above (additive only). In particular: no change
to `operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
`plus1024_extension.py`, `plus1024_independent_session.py`,
`construction.py`, `prior.py`, `sc.py`, or any accepted evidence root.
(The worktree carries pre-existing untracked files and unrelated tracked
dirt from earlier cycles; none of it was touched in this stage.)

## 2. Read-only reuse inventory (§12 + calibration)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (B0 and B1 share the seam; B1 passes k2=7516
  on the same frozen L2 order object — the order-prefix extension needs
  no new logic since the accepted helper slices `l2_order[:k2]`) —
  `is operational_f13` object; `_decode_layer`,
  `classify_operational_outcome` likewise.
- `run_oracle_control_block` + `OracleControlResult` (B2) — `is
  holdout_backoff_diagnostic` objects; P20H tag domain injected through
  the documented `tag_fn` closure (same trick P19/P20B/P20C/P20E/P20F/P20G used).
- `verify_predecessor_construction` (`is` replication module),
  `verify_split_manifest` + `holdout_nll_bits` / `raw_symbol_error_rate`
  (`is` microcheck module), `form_holdout_blocks` (imported for the pin
  proof; never called on DEV ranges).
- `SOURCE_IDS` (accepted session-tag vocabulary: `1p5M` maps to
  `type2_1p5M_20260121_183806`), `load_pairs_table`
  (+ `normalize_pair_columns`), `polar_transform`, `make_gf32`,
  `toeplitz_tag`, `build_p1_metrics`, `gather_p2_metrics`,
  `probs_to_symbol_metric`, `seed_bits_for`, `labels_to_bits`,
  `DISCLOSED_BITS_PER_COORDINATE`, `LABEL_SCALE`, `TAG_BITS` — by module
  contract, never reimplemented.
- Calibration program reuses read-only: `smooth_joint_to_conditional` /
  `derive_p1` / `derive_p2` (accepted P0/P2 formula + adapter),
  `prior_artifact.LAMBDA_STAR` (lambda provenance pin, never searched),
  `entropy_bits` (floor-table functionals), `hm._check_floor`,
  `hm.FROZEN_COUNTS_PATH / FROZEN_MANIFEST_PATH / FROZEN_MANIFEST_SCHEMA /
  NPZ_LOADER_IDENTITY` (path/schema pins).
- Zero-tuning reference: the P20F module `plus1024_extension` is
  imported read-only by ONE test (`test_zero_tuning_carry_over_from_p20f`)
  to pin K/floor/caps/budgets/arm/provenance/step/gate equality; the
  runner itself shares no code path with it (same arms via the same
  accepted seams, not via the P20F module).
- Banned from the new modules (asserted absent by source tests):
  sampling/RNG, genie, K-budget selection, analytic orders, Wilson,
  SCL/list/FWHT/APP, smoothing inside Stage B, the banned per-cell twin
  (`build_f_model(`), the V25 counts loader inside Stage B
  (`load_v25_channel_counts`, `counts_path`, `channel_counts`,
  `_NPZ_CONTENT_OPENED`, `v25_npz`), P16/P17/P18/P19/P20B/P20C/P20E/
  P20F/P20G seed helpers, HOLD flags, every search token, plus the P20G
  module/token names themselves.

## 3. New logic and why it is local (not a shared change)

- `per_session_calibration.calibrate_array`: pure §3 program —
  `smooth_joint_to_conditional(counts, 137.3823795883264)` →
  per-cell 1e-15 floor + column renormalization (isomorphic to
  `build_target_conditional`'s floor step, applied to the smoothed
  table) → `derive_p1`/`derive_p2` → floor-table H1/H2/TOTAL
  functionals (the quantities that drive SC) + unfloored-smoothed
  functionals for the floor-change diagnostic. Proven isomorphic by
  test against an independent literal full-pipeline oracle (≤1e-12 on
  tables, ≤1e-9 on entropies).
- `canonical_prior_digest`: sorted-key `key + shape + dtype + C-order
  bytes` sha256 — deterministic across NPZ zip timestamps; computed
  identically in Stage A (freeze) and Stage B (verify).
- `load_calibrated_prior`: exact key-set / shape / normalization
  (1e-12) / lambda-floor-pin / literal-self-consistency validation;
  returns arrays + recomputed digest. Digest equality against the
  Stage-A pin is checked by the Stage-B runner (`verify_stage_b_prior`
  + `check_frozen_calibration_pins`), never here.
- `run_per_session_calibration`: six required flags
  (`--counts/--source/--lambda/--floor/--manifest/--out-dir`, all
  pinned); plan written pre-open; single counts open via the accepted
  loader (only the `1p5M` key accessed — the `1M`/`2M` keys are never
  indexed); manifest cross-check (counts total == TRAIN pairs,
  fail-closed); five files written post-open; in-process reopen
  refused. The module has no pairs/parquet code path, so DEV contact is
  impossible by construction.
- Runner `verify_stage_b_prior`: digest equality + lambda/floor pins +
  exact key set + recomputed H1/H2/TOTAL within 1e-12 of the
  recalibrated literals (or the injected `expected_literals` seam).
  Raises before any SC call on any mismatch; the two gates
  (`calibration_identity`, `target_population_contract`) pass iff no
  raise — the same fail-before-SC pattern as P20G's precondition block.
- Runner prior accounting: `counts_content_opens` is ALWAYS 0 in Stage
  B (no NPZ loader exists in the module); `prior_content_loads` 1/0 +
  `dev_content_opens` 1/0 keyed by input mode; the single attempt is
  consumed at the first DEV content open (prior load is a worktree-file
  read, not a protected open).
- `form_dev_blocks` / `verify_dev_manifest` / `verify_dev_source_identity`
  / `verify_dev_block_identity`: carried over from P20G unchanged
  except branding (same ranges, same gate order, same refusal strings
  with the P20H packet token).
- `INTEGRITY_GATE_ORDER` is the P20E/P20F/P20G 20-gate order plus the
  new `calibration_identity` gate after `dev_block_range_identity`
  (21 gates; pinned by the carry-over test).
- `DISCLOSURE_RULE` is byte-identical to P20F/P20G (pinned); the
  `SUPPORT_RULE` differs by design (lambda-smoothing + digest-pinned
  prior file) and says so.

## 4. Frozen quadruple

- calibration delta: §3 program with lambda 137.3823795883264
  (D4R2/`prior_artifact.LAMBDA_STAR` provenance) on the 1.5M TRAIN
  counts (total 424960, sha `e5e99cc8…c3a2d59c`); recalibrated literals
  H1 2.006647056368773 / H2 1.9017235959286112 / TOTAL
  3.908370652297384; prior digest
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`;
  DEV-zero-contact evidenced; §3 (i)–(iv) recorded for Pre-EXECUTE.
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
- command: §10 of `P20H_FREEZE.md` verbatim (16 required flags,
  `--prior` frozen-digest path, `--source 1p5M`, block-major B0/B1/B2,
  600 s / 2 GiB / 1-thread env); byte-identical to the module
  `FROZEN_COMMAND` (verified by import).

## 5. Test commands and results (real counts)

New suites (pinned interpreter, fresh temp root, no cache):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
comparison_bench/tests/test_nbpolar_per_session_calibration.py
comparison_bench/tests/test_nbpolar_plus1024_per_session_confirmation.py
-q -p no:cacheprovider --basetemp=$PWD/workspace/p20h/new-suites`
→ **53/53 green** (17 + 36, ~30 s).

Packet-scoped predecessors (same settings, fresh basetemp
`workspace/p20h/pred-suites`):
`test_nbpolar_plus1024_independent_session.py` (36) +
`test_nbpolar_plus1024_extension.py` (36) +
`test_nbpolar_plus1024_confirmation.py` (36) +
`test_nbpolar_l2_disclosure_backoff.py` (34) +
`test_nbpolar_bounded_search_diagnostic.py` (34) +
`test_nbpolar_operational_f13.py` (29) +
`test_nbpolar_operational_f13_replication.py` (25) +
`test_nbpolar_holdout_microcheck.py` (26) +
`test_nbpolar_holdout_backoff_diagnostic.py` (33) → **289/289 green**
(~980 s; the predecessor suites include real-N=32768 SC runs;
per-file collection re-verified: 36/36/36/34/34/29/25/26/33).

No shared predecessor code was changed, so the full NB-Polar suite was
not run. Failing/skipped: none. Bugs found during implementation (all
fixed, none touching shared code): the accepted `derive_p1`/`derive_p2`
require exactly (1024,1024), so the tiny-shape isomorphism tests were
rewritten as full-shape synthetic tests against an independent literal
full-pipeline oracle; a stray duplicated `def` line from a bulk rename
was removed; the Stage-B one-open gate was re-keyed from counts-NPZ to
prior-file + DEV.

## 6. Protected-open audit

- Counts-calibration: exactly ONE content open — the §10 calibration
  command (`counts_content_opens 1`, wall 0.420163 s, counts total
  424960 == TRAIN pairs, digest-recorded). No second calibration, no
  reopen. STATUS `counts_calibration_reads_used` 0→1 by this stage.
- DEV/VAL/HOLD: ZERO content opens or stats in Stage A (DEV opens 0 at
  close). Only JSON provenance reads: P16 construction file (digest
  recomputed, freeze §3), the split manifest (verified inside the
  calibration run), the build-manifest pins carried over from P20G §3.
- 1M pool: never opened (only the `1p5M` key of the loaded counts dict
  was accessed; the `1M` key was never indexed).
- 2M file: never opened, statted, listed, or read in any form; the 2M
  refusal path in the runner is a string literal only (asserted
  refusal-tested with guards still False). One inadvertent
  parent-directory listing during early inventory (`ls` of the
  `v13r3fresh_pairs_20260816/` directory, revealing only the three
  session directory names) is recorded here for main-thread
  adjudication; no 2M content/stat/open followed, and no further
  listing was performed.
- Real-mode tests used throwaway stub files / synthetic in-memory
  priors with patched loaders only; guard globals were restored
  afterwards (`_PRIOR_CONTENT_LOADED` / `_DEV_PARQUET_CONTENT_OPENED`
  False at close; calibration `_COUNTS_CONTENT_OPENED` consumed once
  by the declared run — process-level, recorded in the product).
- Stage-B root `per_session_confirmation/` does not exist.
- This checkout carries no `.venv`; Stage-A pytest and the calibration
  run used the neighboring frozen-command-family interpreter
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, same path
  the frozen Stage-B command names) — no install, no network, no repo
  write outside the fresh temp roots and the frozen product paths.

## 7. Scope concerns encountered (reported, not fixed beyond freeze)

- The recalibrated 1.5M TRAIN literals (H1 2.0066 / H2 1.9017 / TOTAL
  3.9084 bits) are far above the 1M literals (0.0243 / 0.7768 / 0.8010)
  — a descriptive observation quantifying P20G's BLOCKED finding, not a
  claim; branch reading belongs to main-thread planning after
  acceptance.
- Manifest JSON gives pool counts, not frame numbering; TRAIN base 0
  follows from the frozen split code (time-ordered first-60%) +
  same-pipeline parity with the accepted 1M 0-based layout (carried over
  from P20G §3), and the P20H DEV prefix 0..383 is the packet-expected
  pattern at that base. The runner fail-closes on any layout drift
  (`dev_population_exact` + triple gate), so a wrong base blocks before
  any SC call. Pre-EXECUTE owns the cross-session isolation
  adjudication (§4 of the freeze).
- The 1.5M sha is a recorded provenance pin (build manifest → frozen
  plan/identity docs), enforced operationally by path-string + stat-size
  checks pre-open; it is not recomputed from content (that would be a
  second read outside the accepted loader seam).
- For B2, candidate-H NLL equals true-H NLL by construction (truth
  conditioning); both fields are recorded identically, not claimed as
  independent evidence (same convention as P19/P20B/P20C/P20E/P20F/P20G).
- Remainder rows are counted, never decoded; per-frame shape inside the
  remainder is not re-validated (§3 rationale, same as P20E/P20F/P20G).
- The `DISCLOSURE_RULE` string is byte-identical to P20F/P20G by design
  (carry-over pin); the P20H-specific calibration delta lives in the
  `SUPPORT_RULE` and the calibration-identity gate.
- The `check_frozen_arm_table` f≤1.3 budget check still references the
  1M `opf.EXPECTED_H1/H2` planning denominator (carried over unchanged;
  it guards cap growth, not the prior — changing it would be scope
  creep).

## 8. Not run in this stage

Independent Pre-EXECUTE review (including the §3 calibration-vs-tuning
gate), Stage-B execution, Pre-RESULT review, memory triage,
main-thread acceptance. The operator does not accept its own work and
does not authorize Stage B.
