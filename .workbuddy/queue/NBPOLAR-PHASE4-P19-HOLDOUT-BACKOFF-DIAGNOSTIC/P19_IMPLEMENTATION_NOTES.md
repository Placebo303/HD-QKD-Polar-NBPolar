# P19 implementation notes (Wave-A)

## Decisions

- Thin layer/backoff diagnostic runner only
  (`comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_backoff_diagnostic.py`,
  ~2450 lines incl. docstrings, no new science): the accepted P18
  loading/block formation/identity checks and the accepted P16/P17 operational
  helpers are reused by import and never reimplemented or modified. The only
  new logic is P19 wiring: the five-arm loop, the oracle-labelled L2 control
  path, the P19/arm/block tag-domain closure, the descriptive aggregates and
  paired recovery tables, the integrity gates and the sixteen-flag CLI.
- Protected inputs: the NPZ (accepted `load_v25_channel_counts`, stat-only
  25,166,822-byte check) and the 1M pairs parquet (accepted
  `load_pairs_table` + `normalize_pair_columns`). Module-level guards
  `_NPZ_CONTENT_OPENED` / `_HOLD_PARQUET_CONTENT_OPENED` refuse a second
  content open. Both before/after stats (size, mtime_ns) and the attempt
  consumption point are recorded; the attempt is consumed at the first
  protected content open.
- Block formation is the accepted P18 `form_holdout_blocks` (pure: validates
  the HOLD population, sorts by `(frame_id, pair_idx)`, slices the three
  registered blocks and records the 4096-pair unused remainder). No RNG, no
  shuffle, no fitting; a structural token test plus exact call-count test
  enforce this.
- Five frozen arms as a module constant tuple (`FROZEN_ARMS`), never
  CLI-tunable: `base(319,6492)`, `l1_plus(447,6492)`, `l2_plus(319,7004)`,
  `both_plus(447,7004)`, `true_l1_control(oracle, K1=0, K2=6492)` with
  leakages 34119/34759/36679/37319/32524 = `5*(K1+K2)+64`. `--k1/--k2` pin the
  base arm only and refuse anything but 319/6492; a fail-closed
  `check_frozen_arm_table()` re-derives the increments, leakage arithmetic,
  order, oracle label and the 27 SC / 15 tag design totals before any root
  exists.
- Operational arms reuse the accepted `run_operational_block` (one L1 plus
  one candidate-conditioned L2 SC per block, accepted outcome precedence,
  record/abort/recount helpers, truth sentinel). The P19 tag closure ignores
  the helper's internal P16-domain seed array and scores with
  `backoff_seed_bits(master=2026092060, n, arm, block_index)` (SHA-256,
  P19 prefix, arm token; arm/block separated). The internal P16-domain array
  is in-memory only, never scored and never persisted (same seam as P18 R6).
- Oracle control path (`run_oracle_control_block`): true high-layer
  conditioning for the L2 metric (`Provenance.ORACLE_CONDITIONED`), one L2 SC
  call, `label_hat = 32*true_high + low_hat`, at most one tag, no L1 SC and no
  L1 disclosure. The metric gathers on the **true high-layer symbol** (the
  `[U1,B,U2]` table's U1 index space, the same space the accepted operational
  path indexes with its hard L1 candidate); the transform-domain `u1_true`
  argument is retained only as a truth-isolation guard input (flagged R4).
  Records carry `arm_provenance = ORACLE_TRUE_L1_CONTROL`,
  `oracle_truth_use = True`, `provenance = ORACLE_TRUE_L1_CONTROL`; they are
  excluded from every operational aggregate and never presented as an
  operational protocol or deployable rate.
- Counted-budget gates: `sc_calls_exact`/`tags_exact` are recomputed from the
  persisted records and require exactly the frozen 27/15 totals; the fully
  accounted partial transcript is accepted only while a registered resource
  stop is set, so a wall/RSS stop surfaces as
  `BLOCKED(resource_limits_met_and_no_abort)` rather than as a count gate
  (flagged R1). Without a stop, a `decode_failed`/`nonfinite` block shortens
  the transcript and the label becomes `BLOCKED(sc_calls_exact)` or
  `BLOCKED(tags_exact)`; the Pre-EXECUTE reviewer may prefer P18's
  recomputed-maxima reading instead.
- Descriptive outputs: per (arm, block) outcome bucket, L1 correctness, tag
  result, disclosure/public bits, raw channel SER, per-layer/total NLL bits
  under the fixed floored TRAIN prior and `arm_leakage/NLL` CE-normalized
  ratio; aggregates per arm plus paired recovery tables versus `base`,
  `first_operational_recovery_arm` (first operational arm in frozen order
  with an exact block, `null` if none; the oracle control is never a
  candidate) and a neutral `ordered_exact_counts_non_monotone` flag (flagged
  R5/R6).
- Oracle isolation: a strict two-partition filter (kind + provenance) so a
  record with any other label lands in `unassigned` and fails the gate; no
  operational record may carry oracle conditioning or `oracle_truth_use`.
- No thresholds: `backoff_label` takes only the integrity gates; there is no
  count input, no Wilson helper import, no recovery-gate function and no
  `EXACT_MIN`/`exact_fraction`/`fer_rate` code path. The plan states
  `recovery_threshold: None`, `zero_recovery_is_complete: True`,
  `three_recovery_is_complete: True`; 0/3..3/3 (operational and control) is
  COMPLETE in the focused tests.
- P18 pin: `verify_p18_block_identity()` compares P19 literals against the
  accepted P18 module constants (N, base K1/K2, digest, block ranges,
  remainder, frame range, block frames) at code level; the P18 evidence root
  is never re-read (flagged R7).
- Output files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl`, `aggregate_summary.json`, `report.md`,
  created as stubs before the opens and checkpointed after every (arm, block)
  record (15 checkpoints).
- No `__init__.py` export change: P7+ gate modules are not re-exported
  (accepted convention); tests import the module path directly, as do the
  frozen CLI and prior waves.

## Constructed CLI fields (flagged for Pre-EXECUTE review)

The packet lists the expected flags but has no literal command block; the
command in `P19_FREEZE.md` §6 was constructed from the accepted P18 pattern
with P19 values. All sixteen flags are required with no production default;
no new flag was invented. Literal-from-packet values: `--source 1M`,
`--floor 1e-15`, `--n 32768`, `--construction` (P16 root), `--construction-digest`
(frozen digest), `--hold-pairs` (1M parquet), `--hold-frames 1600 1999`,
`--block-frames 128`, `--remainder-frames 1984 1999`, `--tag-master 2026092060`,
`--chunk-rows 512`, `--tag-bits 64`, `--out-dir` (P19 root). The two fields
needing explicit review are `--k1 319 --k2 6492` (the packet's base-arm
credentials; they pin the `base` arm and are not the arms' CLI inputs) and the
absence of any arm-selection flag (the five arms are frozen constants per the
"do not add or change arms" rule).

## Reuse map (all read-only, none modified)

- P18 `holdout_microcheck.py`: `form_holdout_blocks`, `verify_split_manifest`,
  `holdout_nll_bits`, `raw_symbol_error_rate`, `HoldoutMicrocheckContractError`
  (caught for post-open BLOCKED finalization) and the constants used by the
  P18 block pin.
- P17 `operational_f13_replication.py`: `verify_predecessor_construction`
  (identity + canonical digest + K/f replay) only.
- P16 `operational_f13.py`: `run_operational_block`, `_decode_layer` (control
  L2 call), `_block_record`, `_record_dict_consistent`, `_abort_block`
  semantics, `_transcript_mismatches`, `_order_is_permutation`,
  `_check_chunk_contract`, `_check_n`, `_check_tag_bits`,
  `_cell_resource_record`, `_peak_rss_bytes`, `_budget_exceeded`, `_write_json`,
  `_append_jsonl`, `classify_operational_outcome`, `_truth_isolation_sentinel`,
  `_nonfinite_flag`, `OperationalBlockResult`, `TargetPopulationContractError`,
  constants (`EXPECTED_H1/H2/TOTAL`, tolerances, `OUTCOMES`,
  `PRECONDITION_ORDER`).
- P7 `target_construction.py`: `target_preconditions`, `target_entropies`
  tables (`p1`/`p2`), ratified literal semantics.
- P11 `sc.py`: untouched; the `_minus_block(chunk_rows=512)` default contract
  is checked through the accepted P16 helper and `sc_decode` is reached only
  inside the accepted block helpers with the production default.
- P4 `two_layer.py`: constants (`DISCLOSED_BITS_PER_COORDINATE`,
  `LABEL_SCALE`, `TAG_BITS`, `labels_to_bits`, `seed_bits_for`).
- `formal_ir/shared.py`: `toeplitz_tag`, `canonical_event`.
- Loaders: `v35_algorithm_development.load_v25_channel_counts`,
  `io/pairs_loader.py`.
- prior.py: `gather_p2_metrics`, `probs_to_symbol_metric`, `Provenance`
  (oracle control metric only).

## Files changed (this wave only)

1. `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p19/spec.md` (new)
2. `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P19 section appended, boxes unchecked)
3. `comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_backoff_diagnostic.py` (new)
4. `comparison_bench/tests/test_nbpolar_holdout_backoff_diagnostic.py` (new)
5. `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/P19_FREEZE.md` (new)
6. `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/P19_IMPLEMENTATION_NOTES.md` (this file)
7. `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/STATUS.yaml` (status fields only)

No other source, evidence root, output, seed, or config touched. Neither
protected input content was opened. No commit/push.

## Review items (for independent Pre-EXECUTE / Pre-RESULT)

- R1: strict counted-budget gates (exactly 27 SC / 15 tags; registered
  resource stop accepts the fully accounted partial transcript). This is
  stricter than P18's accepted "recomputed maxima" wording and follows this
  packet's "27 SC calls and 15 tags / Assert these counts" line. Confirm, or
  require the P18-style recomputed-maxima reading so a legitimate
  `decode_failed` block keeps COMPLETE. Decision must be taken before the
  attempt.
- R2: `l1_plus`/`l2_plus`/`both_plus` deliberately exceed the accepted
  `f<=1.3` planning budget (leakages 34759/36679/37319 vs the 34122.9-bit
  budget); only `base` is in-budget. This is the packet's backoff diagnostic
  and must be reported as descriptive disclosure levels, never as qualified
  operational points or deployable rates.
- R3: NLL definition (`l1`/`l2`/total under the fixed floored TRAIN
  `p1`/`p2`, layers `A//32`/`A%32`, accepted P18/V49 semantics) and
  scoring-only use.
- R4: the oracle control conditions on the true **high-layer symbol** (the
  `[U1,B,U2]` index space), not the transform-domain `u1_true` vector;
  `u1_true` is retained only for the truth-isolation sentinel. Confirm this
  reading of "true U1 conditioning".
- R5: control records disclose `5*K2+64 = 32524` key-dependent bits per
  tagged record, run one L2 SC and at most one tag, and carry
  `ORACLE_TRUE_L1_CONTROL` plus `oracle_truth_use`; the control is excluded
  from all operational aggregates and from the first-recovery-arm scan, but
  its three outcomes are still reported in an isolated section.
- R6: paired tables pair each ordered operational arm's blocks with the same
  `block_index` of `base` (outcome-pair counts, recovered-vs-base,
  lost-vs-base); `first_operational_recovery_arm` includes `base` as the
  first operational member and is `null` when no operational arm has an exact
  block; `ordered_exact_counts_non_monotone` is reported neutrally.
- R7: the P18 pin is a code-level comparison against the accepted P18 module
  constants, not a re-read of the P18 evidence root; the P16 construction file
  is read as JSON (2,581,862 bytes) for the identity/digest check.
- R8: the constructed verbatim command and the `--k1/--k2` base-pin role (see
  above); the packet has no literal P19 command block.
- R9: `sc_calls_exact`/`tags_exact` under a resource stop (see R1) and the
  abort-fill ordering (arm-major, remaining slots) with per-record
  checkpoints.
- R10: per-record CE ratio numerator is the registered full-block arm
  leakage, so a partially invoked record keeps a nominal ratio while the
  actual disclosure stays in the transcript recount (P18 R3 convention);
  aggregate = `arm_leakage * observed_blocks / sum(NLL)`.
- R11: the `input_and_predecessor_identity.json` name and record contents
  (predecessor/manifest/P18-pin identity, input stat metadata, open/attempt
  accounting; order heads only, full orders stay in the immutable P16 file).

## Test summary

- Focused file `test_nbpolar_holdout_backoff_diagnostic.py`: 30 tests, all
  green (fresh `/tmp` basetemp, pinned interpreter `-p no:cacheprovider`,
  39.6 s). Coverage: identity refusals before reads (construction/manifest/
  P18-pin tampers, zero reads, zero root), P18 slicing/remainder and
  malformed-population BLOCKED, both one-open guards, no-RNG/fitting tokens
  plus exact call counts, five-arm semantics and 27 SC / 15 tag totals, the
  +128/+512 K and 640/2560/3200-bit arithmetic, P19 tag-domain proof against
  P16/P17/P18, oracle isolation (control excluded, partition tamper,
  operational oracle-conditioning refusal), counts/buckets/recount tamper,
  paired tables/first arm/non-monotone, all 0/3..3/3 operational and control
  patterns COMPLETE with no Wilson/FER path, four-arm failure precedence,
  budget abort-fill, MemoryError classification, scalar-only five-file
  inventory with banned-key walk, real-mode accounting/stat gates on
  throwaway files with patched loaders, CLI refusals, and two tiny real
  blocks (accepted operational helper with the P19 closure; oracle control
  with real SC and the P19-domain tag).
- Packet-scoped predecessor suites (same settings): `test_nbpolar_operational_f13.py`
  23/23 green (491.8 s); `test_nbpolar_operational_f13_replication.py` +
  `test_nbpolar_holdout_microcheck.py` 51/51 green (386.0 s). No shared
  predecessor code was changed and no focused failure required broader
  coverage, so the full NB-Polar suite was not run (packet rule); this is the
  packet-scoped set and the reason.
