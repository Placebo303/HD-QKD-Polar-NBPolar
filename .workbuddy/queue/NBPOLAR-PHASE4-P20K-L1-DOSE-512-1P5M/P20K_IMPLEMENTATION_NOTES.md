# P20K implementation notes (Stage A operator record)

## 1. Files added (no shared file modified)

| file | purpose |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_512_1p5m.py` | thin three-arm L1-dose-512 runner (new; 2892 lines, derived as a P20J clone with the §2 +512 L1 order-prefix swap + new-segment population + P20J-DEV exclusion gate (sextuple) + new tag domain) |
| `comparison_bench/tests/test_nbpolar_l1_dose_512_1p5m.py` | 36 focused injected runner tests (new; P20J-clone adapted) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20k/spec.md` | P20K OpenSpec delta (new) |
| `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P20K section) | P20K task section appended to the umbrella change (edit; purely additive — zero deletions; tracked-holder bar same as P20J) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/P20K_FREEZE.md` | freeze (new) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/P20K_IMPLEMENTATION_NOTES.md` | this file (new) |

`git diff --numstat` on the one tracked file touched by this stage
(`tasks.md`) shows 983 insertions / 0 deletions in the worktree, of
which this stage added only the trailing +145-line P20K section (the
file already carried pre-existing uncommitted P20E–P20J sections
before this stage; same situation as P20J). In particular: no change
to `operational_f13.py`, `operational_f13_replication.py`,
`holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
`l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
`plus1024_extension.py`, `plus1024_independent_session.py`,
`per_session_calibration.py`,
`plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
`l1_dose_escalation_1p5m.py`, `construction.py`, `prior.py`,
`sc.py`, or any accepted evidence root. (The worktree carries
pre-existing untracked files and unrelated tracked dirt from earlier
cycles; none of it was touched in this stage. The predecessor suites
were run read-only against those files.)

## 2. Read-only reuse inventory (§12)

Direct shared references (identity-pinned by
`test_accepted_helpers_shared_not_reimplemented`):

- `run_operational_block` (E0 and E1 share the seam; E1 passes k1=831
  on the same frozen L1 order object — the order-prefix extension
  needs no new logic since the accepted helper slices
  `l1_order[:k1]`) — `is operational_f13` object; `_decode_layer`,
  `classify_operational_outcome` likewise.
- `run_oracle_control_block` + `OracleControlResult` (E2) — `is
  holdout_backoff_diagnostic` objects; P20K tag domain injected
  through the documented `tag_fn` closure (same trick
  P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J used).
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
  formula pins only) from `per_session_calibration`; the P20J module
  `l1_dose_escalation_1p5m` is imported read-only by ONE test
  (`test_zero_tuning_carry_over_from_p20j`) to pin N/floor/base
  K/caps/prior-reuse/budgets/gates/provenance equality; the runner
  itself shares no code path with it (same arms via the same accepted
  seams, not via the P20J module).
- Banned from the new module (asserted absent by source tests):
  sampling/RNG, genie, K-budget selection, analytic orders, Wilson,
  SCL/list/FWHT/APP, smoothing inside Stage B, any NPZ/counts loader
  inside Stage B (`load_v25_channel_counts`, `counts_path`,
  `channel_counts`, `_NPZ_CONTENT_OPENED`, `v25_npz`), P16/P17/P18/
  P19/P20B/P20C/P20E/P20F/P20G/P20H seed helpers, HOLD flags, every
  search token, plus the P20H module/token names and arm names
  (`B0/B1/B2`, `plus1024_per_session_confirmation`), the P20I
  module/token/arm names (`l1_disclosure_1p5m`, `L1Disclosure1p5m`,
  `C0_sc_base`, `C1_L1plus`, `C2_true_l1_diagnostic`, `c1_restored`,
  `FROZEN_K1_C1`, `FROZEN_C1_`, `C1b`) AND the P20J module/token/arm
  names (`l1_dose_escalation_1p5m`, `L1DoseEscalation1p5m`,
  `D0_sc_base`, `D1_L1plus`, `D2_true_l1_diagnostic`, `d1_restored`,
  `FROZEN_K1_D1`, `FROZEN_D1_`, `D1b`) themselves. Exactly one
  forbidding mention of a second L1 tier (`E1b`); no implementation.

## 3. New logic and why it is local (not a shared change)

- `l1_prefix_positions` / `l2_prefix_positions`: pure frozen-order
  views (`order[:k1]` / `order[:k2]`); E1 runs k1=831 on the SAME
  frozen P16 L1 order object as E0 (pinned by object-identity in the
  differential test) — isomorphic with the accepted K2 prefix rule, no
  reselection, on ANY data.
- `verify_stage_b_prior`: digest equality against the §3 frozen pin +
  lambda/floor pins + exact key set + recomputed H1/H2/TOTAL within
  1e-12 of the recalibrated literals (or the injected
  `expected_literals` seam). Raises before any SC call on any
  mismatch; the two gates (`calibration_identity`,
  `target_population_contract`) pass iff no raise — the same
  structure as P20J, only the E1 disclosure triple differs.
- `verify_dev_source_identity` (sextuple gate, FIRST): exact-path
  equality against the 1.5M pairs path; the 1M full-pool path and the
  reserved 2M path refuse with distinct messages; any other path
  refuses. The 2M path is a refusal string only (never opened,
  statted, or read — asserted by the zero-contact test).
- `verify_dev_block_identity` (sextuple gate, SECOND–FIFTH): VAL/HOLD
  overlap (VAL first), then P20H-DEV, P20I-DEV, **P20J-DEV** exclusion
  in that frozen order, each raising before any root exists; the
  literal pins (DEV 1152..1535, blocks, remainder 1536..1659/124/
  31744, VAL/HOLD, P20H/P20I/P20J ranges) mismatch with their names.
  `form_dev_blocks` repeats the same five disjointness checks at run
  level on the injected/normalized table.
- `check_frozen_arm_table`: pins the three E-arms, the single +512
  step (ΔK1, K1 831, keyΔ 2560), the leakage arithmetic
  (5·K+64 per arm), the 15-SC/9-tag design totals and the far-below-raw
  bar. `check_frozen_calibration_pins`: pins lambda/floor/digest/
  literal consistency at code level (no I/O).
- Record builders (`_operational_record` / `_control_record` /
  `_abort_record`), per-record schema checks, `recovery_diagnostics`
  (`e1_restored_count` analogue + per-block E0/E1 rows),
  `build_aggregates` (oracle never in operational totals),
  `l1_dose_512_block_events` / `l1_dose_512_recount_events`
  (canonical transcript + independent recount, mismatch 0),
  `_integrity_gates` (21 gates in frozen order), the five-file writer
  with per-(arm, block) checkpointing, the P20A resource path
  (`MemoryError` re-raised at all three SC sites; abort preserves
  evidence and BLOCKS): all carried over from the P20J structure with
  E-arm/K1-831/+512/remainder-124 substitutions only.
- CLI: 16 required flags, no production default; K1/K2/floor/dev-frames/
  remainder/tag-master frozen by equality checks; arms hardcoded in
  `FROZEN_ARMS` (never CLI-tunable); `--source` vocabulary frozen to
  `1p5M` only.

## 4. Deliberate derivation method (mechanical clone + judged deltas)

The runner and its test file were derived as mechanical clones of the
accepted P20J pair (ordered token script in `/tmp`, outside the repo:
arm renames D→E, `L1_DOSE_ESCALATION`→`L1_DOSE_512`,
quintuple→sextuple, tag master 2026092240→2026092250, DEV/remainder
geometry, disclosure arithmetic literals), followed by judged manual
deltas: the +512 dose values (ΔK1 512, K1 831, keyΔ 2560), the P20J-DEV
exclusion gate (new constant + checks in `verify_dev_block_identity`
and `form_dev_blocks` + pins), the module/test docstrings, the
DISCLOSURE/ARM/CLAIM/support prose, the `FROZEN_OUT_ROOT` packet path,
the seed-domain predecessor list, and the test-side P20J carry-over
pins (including the corrected P20I seed-prefix entry and the new P20J
prefix assertion). Every mechanical substitution was audited by grep
(no D-arm/`d1_`/`quintuple`/stale-dose remnants in the runner; no
stale P20I-refs in the test) and the suites below re-verify the
semantics literally (order-prefix object identity, gate refusal
order, cap arithmetic, recount).

## 5. Test evidence (exact commands, fresh roots, zero protected opens)

Interpreter (this checkout carries no `.venv`; same
frozen-command-family path as P20J):
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(`numpy/pytest/pandas` verified). All runs with `-p no:cacheprovider`
and fresh additive basetemps under `workspace/p20k/stageA-run1/`:

- new suites: `pytest
  comparison_bench/tests/test_nbpolar_l1_dose_512_1p5m.py -q -p
  no:cacheprovider --basetemp=$PWD/workspace/p20k/stageA-run1/new-suites`
  → **36/36 green** (~26 s, first run, no runner change needed);
- pred-A: dose-escalation (36) + disclosure (36) + per-session-confirm
  (36) + calibration (17) + independent-session (36) + extension (36)
  + confirmation (36) → **233/233 green** (~144 s);
- pred-B: l2-backoff (34) + bounded-search (34) → **68/68 green**
  (~40 s);
- pred-C: operational-f13 (29) + replication (25) + microcheck (26) +
  backoff-diagnostic (33) → **113/113 green** (~826 s).
- Grand total **450/450 green**; failing/skipped: none.
  Per-file collection re-verified:
  36/36/36/17/36/36/36/34/34/29/25/26/33 + new 36.

Protected-open audit at Stage-A close: counts-calibration 0/0 (the §2
digest recomputation is a worktree-file `np.load` of the P20H
calibrated prior, never the V25 counts NPZ and never a refit), DEV
0/1, HOLD 0/1; no 1M-pool or reserved-2M open/stat/listing/read in any
form (2M pristine by non-access; no parent-directory listing of the
pairs root was performed); no real-data decoder execution; no
Stage-B output root; no commit/push. The real-mode tests use a
throwaway temporary prior stub plus synthetic in-memory priors with
patched loaders only.

## 6. Scope notes and deferred items

- The `FROZEN_OUT_ROOT` packet-path literal was caught during the
  Stage-A audit (mechanical clone had produced the P20J-packet-style
  directory name) and corrected to the packet-§9 path
  `.../NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m` before
  the freeze; no test asserted the old value.
- The P20J test's seed-prefix list carried a mislabeled P20I entry
  (`p20j-l1-disclosure`); the P20K test corrects it to the real P20I
  prefix and additionally asserts the real P20J prefix differs from
  the new P20K domain.
- No second L1 tier, no second L2 step, no alternative construction,
  no efficiency tuning, no SCL/new kernel/model/schema, no FER or
  qualification language anywhere in code, tests, or docs
  (descriptive-only label; `undetected` isolated).
- Stage B (single authorized execution), independent Pre-EXECUTE
  review (§3 reuse + §4 sextuple gate adjudication), Pre-RESULT
  review, and main-thread acceptance are all deferred and explicitly
  NOT authorized by this stage.
