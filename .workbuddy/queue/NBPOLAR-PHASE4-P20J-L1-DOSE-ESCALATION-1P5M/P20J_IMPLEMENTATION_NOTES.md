# P20J implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_escalation_1p5m.py` | thin three-arm L1-dose-escalation runner (new; ~2860 lines, derived as a P20I clone with the §2 +256 L1 order-prefix swap + new-segment population + P20I-DEV exclusion gate + new tag domain) |
| `comparison_bench/tests/test_nbpolar_l1_dose_escalation_1p5m.py` | 36 focused injected runner tests (new; P20I-clone adapted) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20j/spec.md` | P20J OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20J section) | P20J task section appended to the umbrella change (edit; purely additive — zero deletions; tracked-holder bar same as P20I) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/P20J_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/P20J_IMPLEMENTATION_NOTES.md` | this file (new) |

`git diff` on the one tracked file touched by this stage (`tasks.md`)
shows insertions only, zero deletions (the file already carried
pre-existing unrelated insertions before this stage; this stage added
only the trailing P20J section). In particular: no change to
`operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
`plus1024_extension.py`, `plus1024_independent_session.py`,
`per_session_calibration.py`,
`plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
`construction.py`, `prior.py`, `sc.py`, or any accepted evidence
root. (The worktree carries pre-existing untracked files and unrelated
tracked dirt from earlier cycles — e.g. `operational_f13.py`,
`holdout_backoff_diagnostic.py` and four NB-Polar test files show as
modified before this stage started; none of it was touched in this
stage. The predecessor suites were run read-only against those files.)

## 2. Read-only reuse inventory (§12)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (D0 and D1 share the seam; D1 passes k1=575
  on the same frozen L1 order object — the order-prefix extension
  needs no new logic since the accepted helper slices
  `l1_order[:k1]`) — `is operational_f13` object; `_decode_layer`,
  `classify_operational_outcome` likewise.
- `run_oracle_control_block` + `OracleControlResult` (D2) — `is
  holdout_backoff_diagnostic` objects; P20J tag domain injected
  through the documented `tag_fn` closure (same trick
  P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I used).
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
- Prior-reuse pins read-only: `FROZEN_LAMBDA` + `PRIOR_NPZ_KEYS` +
  `canonical_prior_digest` + `load_calibrated_prior` (digest function +
  formula pins only) from `per_session_calibration`; the P20I module
  `l1_disclosure_1p5m` is imported read-only by ONE test
  (`test_zero_tuning_carry_over_from_p20i`) to pin N/floor/base
  K/caps/prior-reuse/budgets/gates/provenance equality; the runner
  itself shares no code path with it (same arms via the same accepted
  seams, not via the P20I module).
- Banned from the new module (asserted absent by source tests):
  sampling/RNG, genie, K-budget selection, analytic orders, Wilson,
  SCL/list/FWHT/APP, smoothing inside Stage B, the banned per-cell twin
  (`build_f_model(`), any NPZ/counts loader inside Stage B
  (`load_v25_channel_counts`, `counts_path`, `channel_counts`,
  `_NPZ_CONTENT_OPENED`, `v25_npz`), P16/P17/P18/P19/P20B/P20C/P20E/
  P20F/P20G/P20H seed helpers, HOLD flags, every search token, plus the
  P20H module/token names and arm names (`B0/B1/B2`,
  `plus1024_per_session_confirmation`) AND the P20I module/token/arm
  names (`l1_disclosure_1p5m`, `L1Disclosure1p5m`, `C0_sc_base`,
  `C1_L1plus`, `C2_true_l1_diagnostic`, `c1_restored`,
  `FROZEN_K1_C1`, `FROZEN_C1_`, `C1b`) themselves. Exactly one
  forbidding mention of a second L1 tier (`D1b`); no implementation.

## 3. New logic and why it is local (not a shared change)

- `l1_prefix_positions` / `l2_prefix_positions`: pure frozen-order
  views (`order[:k1]` / `order[:k2]`); D1 runs k1=575 on the SAME
  frozen P16 L1 order object as D0 (pinned by object-identity in the
  differential test) — isomorphic with the accepted K2 prefix rule, no
  reselection, on ANY data.
- `verify_stage_b_prior`: digest equality against the §2 frozen pin +
  lambda/floor pins + exact key set + recomputed H1/H2/TOTAL within
  1e-12 of the recalibrated literals (or the injected
  `expected_literals` seam). Raises before any SC call on any
  mismatch; the two gates (`calibration_identity`,
  `target_population_contract`) pass iff no raise — the same
  fail-before-SC pattern as P20H/P20I's precondition block. No refit
  path exists in the runner (no counts loader, no smoothing import).
- `check_frozen_arm_table`: pure code-level pins (lambda/floor/
  digest/literals; arm order, K values, the single +256 step, leakage
  arithmetic 34119/35399/32524, oracle label, 15 SC / 9 tag design
  totals). Any drift raises before any root exists.
- Runner prior accounting: `counts_content_opens` is ALWAYS 0 in Stage
  B (no NPZ loader exists in the module); `prior_content_loads` 1/0 +
  `dev_content_opens` 1/0 keyed by input mode; the single attempt is
  consumed at the first DEV content open (prior load is a
  worktree-file read, not a protected open).
- `verify_dev_source_identity` / `verify_dev_block_identity` /
  `verify_dev_manifest` / `form_dev_blocks`: carried over from P20I
  unchanged except branding, the next-segment ranges (768..1151 /
  1152..1659), and the FIFTH gate (P20I-DEV 384..767 exclusion after
  the P20H-DEV exclusion and before the calibration-identity gate);
  same refusal order with the P20J packet token. `form_dev_blocks`
  additionally refuses per-block P20I-DEV overlap, mirroring its
  VAL/HOLD/P20H checks.
- `INTEGRITY_GATE_ORDER` is the P20I 21-gate order byte-identical
  (pinned by the carry-over test), with `dev_block_range_identity`
  now covering the quintuple gate.
- `DISCLOSURE_RULE` carries the single +256 L1 step (K1 319→575,
  +1280 key bits); `SUPPORT_RULE` is byte-identical to P20I (same
  digest-pinned prior program); the P20J-specific deltas live in the
  arm table, the population pins (incl. the P20I-DEV exclusion), and
  the new tag domain.
- `recovery_diagnostics` reports the descriptive `d1_restored_count`
  analogue (D0 fail → D1 exact) with per-block endpoint rows; no
  threshold, no winner, label stays COMPLETE when integrity holds.

## 4. Frozen quadruple

- prior reuse: P20H Stage-A product read-only, digest
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  (recomputed in this session, match) + lambda 137.3823795883264 +
  floor 1e-15 + recalibrated literals H1 2.006647056368773 / H2
  1.9017235959286112 / TOTAL 3.908370652297384; zero calibration
  opens; V25 counts NPZ never opened; §3 reuse evidenced for
  Pre-EXECUTE.
- population: 1.5M TRAIN next segment 768..1151, blocks
  768..895/896..1023/1024..1151, remainder 1152..1659 (508 frames /
  130048 pairs) never used (counted, never decoded), intra-file VAL
  1660..2212 + HOLD 2213..2766 disjoint by the second gate (VAL
  first), consumed P20H DEV 0..383 disjoint by the third gate,
  consumed P20I DEV 384..767 disjoint by the fourth gate; 1M full
  pool + reserved 2M file excluded by the first-half
  source-tag+digest gate (path + 1869178 B size pin, sha
  `ca351e52…a06b` provenance pin); file/digest identity from JSON
  build-manifest provenance, never a content open.
- cap: 34119 base / 35399 D1 / 32524 control key bits per block,
  327743 public bits per tag; 34119/327680 = 0.10412292 and
  35399/327680 = 0.10802917 of raw; D1 delta +1280 = 5·256; planned
  totals 306126 key (operational 208554 + oracle 97572) / 2949687
  public; recount mismatch 0 or BLOCKED.
- command: §10 of `P20J_FREEZE.md` verbatim (16 required flags,
  `--prior` frozen-digest path, `--source 1p5M`, `--dev-frames 768
  1151`, `--remainder-frames 1152 1659`, new P20J tag master
  2026092240, 600 s / 2 GiB / 1-thread env); the 16-flag argv
  verified present in the module `FROZEN_COMMAND` by import (no
  `--counts` flag).

## 5. Test commands and results (real counts)

New suite (pinned interpreter, fresh temp root, no cache):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
comparison_bench/tests/test_nbpolar_l1_dose_escalation_1p5m.py
-q -p no:cacheprovider
--basetemp=$PWD/workspace/p20j/7f3a9c2e-1b4d-4e8f-a5c6-d7e8f9a0b1c2/rerun3`
→ **36/36 green** (~26 s; the first attempt stopped at 34/36 on two
test-side assertion typos — a `d1_` key name and the ban-list arm
prefix — the runner itself was untouched; both fixed, full file
rerun 36/36 on a fresh basetemp).

Packet-scoped predecessors (same settings, fresh basetemps
`workspace/p20j/7f3a9c2e-1b4d-4e8f-a5c6-d7e8f9a0b1c2/pred-A|pred-B|pred-C`):
`test_nbpolar_l1_disclosure_1p5m.py` (36) +
`test_nbpolar_plus1024_per_session_confirmation.py` (36) +
`test_nbpolar_per_session_calibration.py` (17) +
`test_nbpolar_plus1024_independent_session.py` (36) +
`test_nbpolar_plus1024_extension.py` (36) +
`test_nbpolar_plus1024_confirmation.py` (36) → chunk A **197/197**
green (~121 s);
`test_nbpolar_l2_disclosure_backoff.py` (34) +
`test_nbpolar_bounded_search_diagnostic.py` (34) → chunk B **68/68**
green (~41 s);
`test_nbpolar_operational_f13.py` (29) +
`test_nbpolar_operational_f13_replication.py` (25) +
`test_nbpolar_holdout_microcheck.py` (26) +
`test_nbpolar_holdout_backoff_diagnostic.py` (33) → chunk C **113/113**
green (~839 s; the predecessor suites include slow real-N SC runs,
which is why the run was split into three chunks with fresh
basetemps).

Grand total: **414/414 green** (36 new + 378 predecessors).
Per-file collection re-verified: 36/36/36/17/36/36/36/34/34/29/25/
26/33 plus the new 36.

No shared predecessor code was changed, so the full NB-Polar suite
was not run. Failing/skipped at close: none. Bugs found during
implementation: the two test-side typos above (no runner change
involved); plus three derivation-script misses caught by the script's
own fail-closed Miss rule before any file was written (all fixed in
`/tmp`, never in the repo). One harness note, same as P20I: every
run pre-creates its `--basetemp` parent (pytest creates the leaf
with `parents=False`).

## 6. Protected-open audit

- Counts-calibration: ZERO opens (0/0; no NPZ open in this packet).
  The §2 digest check recomputed the canonical digest of the P20H
  worktree prior file only — a worktree-file read, never a counts
  open. The runner contains no NPZ loader (asserted absent by source
  test).
- DEV/VAL/HOLD: ZERO content opens or stats in Stage A (DEV 0/1,
  HOLD 0/1 at close). Only JSON provenance reads: P16 construction
  file (digest recomputed, freeze §3), the split manifest
  (population part, freeze §3), the build-manifest size/sha
  provenance pins.
- 1M pool: never opened.
- 2M file: never opened, statted, listed, or read in any form; the 2M
  refusal path in the runner is a string literal only (asserted
  refusal-tested with guards still False). No parent-directory
  listing of the pairs root was performed in this stage.
- Real-mode tests used throwaway stub files / synthetic in-memory
  priors with patched loaders only; guard globals were restored
  afterwards (`_PRIOR_CONTENT_LOADED` /
  `_DEV_PARQUET_CONTENT_OPENED` False at close; asserted by
  `test_zero_protected_opens_audit`).
- Stage-B root `l1_dose_escalation_1p5m/` does not exist (verified
  absent).
- This checkout carries no `.venv`; Stage-A pytest and the digest
  checks used the neighboring frozen-command-family interpreter
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, same path
  the frozen Stage-B command names) — no install, no network, no repo
  write outside the fresh temp roots and the frozen packet/spec
  paths.

## 7. Scope concerns encountered (reported, not fixed beyond freeze)

- The P20J runner/tests were derived as mechanical P20I clones with
  the packet-frozen swaps; the derivation script enforced a
  fail-closed Miss rule (every replacement must hit ≥1 site) and the
  result was diff-reviewed hunk by hunk plus pin-checked by import
  (35/35 carry-over pins byte-identical; D1/total/tag/population
  pins exact). No requirement was changed and no shared file was
  modified. The transcript event vocabulary (`l1_disclosure` event
  type, `l1_disclosure_rule` record key) is deliberately carried over
  byte-identical — it is shared taxonomy, not the P20I module.
- The project-local `.venv` does not exist in this checkout (same as
  P20H/P20I Stage A); the frozen packet's own Stage-B command names
  the neighboring interpreter, which was used for all Stage-A runs.
  Pre-EXECUTE may adjudicate interpreter provenance.
- Manifest JSON gives pool counts, not frame numbering; TRAIN base 0
  follows from the frozen split code (time-ordered first-60%) +
  same-pipeline parity with the accepted 1M 0-based layout (carried
  over from P20H §3), and the P20J DEV segment 768..1151 is the
  packet-expected pattern at that base. The runner fail-closes on any
  layout drift (`dev_population_exact` + quintuple gate), so a wrong
  base blocks before any SC call. Pre-EXECUTE owns the cross-session
  isolation adjudication (§4 of the freeze).
- The 1.5M sha is a recorded provenance pin (build manifest → frozen
  plan/identity docs), enforced operationally by path-string +
  stat-size checks pre-open; it is not recomputed from content (that
  would be a read outside the accepted loader seam).
- For D2, candidate-H NLL equals true-H NLL by construction (truth
  conditioning); both fields are recorded identically, not claimed as
  independent evidence (same convention as P19/P20B/P20C/P20E/P20F/
  P20G/P20H/P20I).
- Remainder rows are counted, never decoded; per-frame shape inside
  the remainder is not re-validated (§3 rationale, same as
  P20E/P20F/P20G/P20H/P20I).
- The `check_frozen_arm_table` f≤1.3 budget check still references
  the 1M `opf.EXPECTED_H1/H2` planning denominator (carried over
  unchanged; it guards cap growth, not the prior — changing it would
  be scope creep).
- The pre-existing worktree dirt (tracked modifications under
  `comparison_bench/src/.../operational_f13.py`,
  `holdout_backoff_diagnostic.py`, four NB-Polar test files, docs,
  and the unrelated `tasks.md` insertions above the P20J section)
  predates this stage and was left untouched; Pre-EXECUTE owns the
  scoped-cleanliness adjudication for the Stage-B gate.

## 8. Not run in this stage

Independent Pre-EXECUTE review (including the §3 reuse pins and the
§4 quintuple gate), Stage-B execution, Pre-RESULT review, memory
triage, main-thread acceptance. The operator does not accept its own
work and does not authorize Stage B.
