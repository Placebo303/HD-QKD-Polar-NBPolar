# P18 implementation notes (Wave-A)

## Decisions

- Thin HOLD microcheck runner only
  (`comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_microcheck.py`,
  ~1880 lines incl. docstrings, no new science): the accepted P16/P17
  operational block path (`run_operational_block`, outcome precedence,
  record/abort/recount helpers) and the accepted P17 predecessor verifier
  (`verify_predecessor_construction`, exact canonical-digest recipe) are
  reused by import and never reimplemented or modified. The only new logic
  is P18 wiring: protected-input loading/one-open accounting, deterministic
  HOLD block formation, the P18 tag-domain closure, descriptive NLL/SER
  scoring, the integrity gates and the sixteen-flag CLI.
- Protected inputs: the NPZ (accepted `load_v25_channel_counts`, stat-only
  25,166,822-byte check) and the 1M pairs parquet (accepted
  `load_pairs_table` + `normalize_pair_columns`). Module-level guards
  `_NPZ_CONTENT_OPENED` / `_HOLD_PARQUET_CONTENT_OPENED` refuse a second
  content open. Both before/after stats (size, mtime_ns) and the attempt
  consumption point are recorded; the attempt is consumed at the first
  protected content open.
- `form_holdout_blocks` is pure: it validates the HOLD population
  (400 frames, 102400 rows, 256 rows/frame, `pair_idx 0..255`, symbols
  0..1023), sorts by `(frame_id, pair_idx)`, slices the three registered
  blocks and records the unused remainder. It contains no RNG, no shuffle
  and no fitting call; a structural token test plus exact call-count test
  enforce this.
- NLL rule (invented descriptive definition, flagged R1): per block
  `l1 = sum_i -log2 p1[high_i, bob_i]` and
  `l2 = sum_i -log2 p2[high_i, bob_i, low_i]` where `high = A//32`,
  `low = A%32` are the true 10-bit label's layers and `p1`/`p2` are the
  accepted `derive_p1`/`derive_p2` of the floored TRAIN conditional. This
  matches the V49 `nll_u1`/`nll_u2`/`nll_total` semantics (per-layer
  conditional NLL in bits). Scoring-only: the truth enters NLL and SER as
  scores, never as Bob metrics/candidate priors/decisions.
- `raw_ser` (invented definition, flagged R2): mean of
  `alice_symbol != bob_symbol` over the block, i.e. the raw channel symbol
  error rate, not a decoder metric.
- CE-normalized disclosure ratio (flagged R3): per block the packet's
  literal `34119 / observed_block_NLL_bits` is reported even when a block
  is partially invoked, because the numerator is the registered full-block
  disclosure; actual disclosure stays visible in the transcript recount.
  Aggregate = `34119 * (#blocks with NLL) / sum(block NLL)`.
- Outcome/SC/tag gates: `sc_calls_exact` and `tags_exact` are recomputed
  from the persisted records (`1 + l2_invoked` per executed block, up to 6;
  `tag_invoked` count, up to 3). This keeps a legitimate `decode_failed`
  block (one L1 call, no tag) from becoming an integrity failure, matching
  the packet's "COMPLETE regardless of 0..3 exact" rule; only
  undetected/nonfinite/resource/truth/accounting failures block.
- No thresholds: the label function takes only the integrity gates; there
  is no count input, no Wilson helper import and no recovery threshold key
  beyond the explicit `"recovery_threshold": None` statement. A structural
  test asserts the absence of Wilson/recovery code tokens.
- `verify_split_manifest` checks the accepted schema
  `nbldpc_v25_split_manifest_v1` and the 1M source's 400 HOLD frames /
  102400 HOLD pairs. The manifest path is a frozen module constant
  (`FROZEN_MANIFEST_PATH`), not a CLI flag (flagged R4).
- P18 tag domain: `holdout_seed_bits` reuses the accepted SHA-256
  construction with the P18 prefix, master 2026092050 and block index
  0..2, and closes over the seed through the accepted `tag_fn` seam. As in
  P17 (R1 there), the reused helper still derives its own internal
  P16-domain array before invoking `tag_fn`; that array is in-memory only,
  never persisted and never scored. The focused test proves the scored
  seeds are P18-domain and differ from the P16 and P17 domain bits.
- Output files: `frozen_plan.json`, `input_and_construction_identity.json`,
  `per_block_outcomes.jsonl`, `aggregate_summary.json`, `report.md`,
  created as stubs before the opens and checkpointed after every block.
- No `__init__.py` export change: P7+ gate modules are not re-exported
  (accepted convention); tests import the module path directly, as do the
  frozen CLI and prior waves.

## Invented CLI flags (all flagged for Pre-EXECUTE review)

The packet has no P18-05 command block; the command was constructed from
the P17 pattern with P18 values. `--hold-pairs`, `--hold-frames`,
`--block-frames`, `--remainder-frames` and `--tag-master` are new. The
other eleven flags mirror P17 exactly (`--counts`, `--source`, `--floor`,
`--n`, `--k1`, `--k2`, `--construction`, `--construction-digest`,
`--chunk-rows`, `--tag-bits`, `--out-dir`) with P18 values. All sixteen are
required; each non-frozen value is refused before any content open.

## Loader and manifest discovery notes

- Pairs loader: `comparison_bench/src/comparison_bench/io/pairs_loader.py`
  (`load_pairs_table` handles `.parquet` via `pd.read_parquet` with a
  pickle fallback; `normalize_pair_columns` enforces the required
  `frame_id`/`pair_idx`/`alice_symbol`/`bob_symbol` columns and integer
  coercion). It is the loader used by `nonbinary_v25_gate.SOURCES` and the
  V64 fresh registry, i.e. the accepted repo-root-relative
  `v13r3fresh_pairs_20260816/<source_tag>/pairs.parquet` convention. The
  registered 1M file resolves to
  `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet`
  (1,354,289 bytes; `build_manifest.json` in the same tree records the same
  size).
- Split manifest: `nbldpc_v25_20260818/run_04/split_manifest.json`
  (schema `nbldpc_v25_split_manifest_v1`, generated by
  `nonbinary_v25_gate.split_frame_manifest`/`split_by_frame`: sorted unique
  frames, 60/20/20 → for the 1M source the last 400 frames 1600..1999 are
  HOLD). It declares 400 HOLD frames / 102400 HOLD pairs for
  `type2_1M_20260121_184040`, matching the packet. run_04 is also the run
  that owns the frozen TRAIN NPZ.
- The registered relative parquet path in the packet
  (`v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet`) is a
  suffix of the accepted repo-relative registry path; the full repo-relative
  path is used in the frozen command and the resolved absolute path is
  documented in `P18_FREEZE.md` §3.

## Reuse map (all read-only, none modified)

- P16 `operational_f13.py`: `run_operational_block`,
  `classify_operational_outcome` (via the helper), `_block_record`,
  `_abort_block`, `_record_dict_consistent`, `_transcript_mismatches`,
  `_order_is_permutation`, `_check_chunk_contract`, `_check_n`,
  `_check_tag_bits`, `_cell_resource_record`, `_peak_rss_bytes`,
  `_budget_exceeded`, `_write_json`, `_append_jsonl`,
  `OperationalBlockResult`, `TargetPopulationContractError`, constants
  (`EXPECTED_H1/H2/TOTAL`, tolerances, `OUTCOMES`, `PRECONDITION_ORDER`).
- P17 `operational_f13_replication.py`: `verify_predecessor_construction`
  (identity + digest + K/f replay) only.
- P7 `target_construction.py`: `target_preconditions`, `target_entropies`
  tables (`p1`/`p2`), ratified literal semantics.
- P11 `sc.py`: untouched; the `_minus_block(chunk_rows=512)` default
  contract is checked through the accepted P16 helper and `sc_decode` is
  reached only inside the accepted block helper with the production
  default.
- P4 `two_layer.py`: constants (`DISCLOSED_BITS_PER_COORDINATE`,
  `LABEL_SCALE`, `TAG_BITS`, `labels_to_bits`, `seed_bits_for`).
- `formal_ir/shared.py`: `toeplitz_tag` (P18-domain closure),
  `canonical_event` (P18 transcript builders).
- Loader `formal_ir/v35_algorithm_development.py:349`
  (`load_v25_channel_counts`) and `SOURCE_IDS` for the manifest key.
- `io/pairs_loader.py` for the protected HOLD parquet.

## Files changed (this wave only)

1. `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p18/spec.md` (new)
2. `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P18 section appended, boxes unchecked)
3. `comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_microcheck.py` (new)
4. `comparison_bench/tests/test_nbpolar_holdout_microcheck.py` (new)
5. `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/P18_FREEZE.md` (new)
6. `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/P18_IMPLEMENTATION_NOTES.md` (this file)
7. `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/STATUS.yaml` (status fields only)

No other source, evidence root, output, seed, or config touched. Neither
protected input content was opened. No commit/push.

## Review items (for independent Pre-EXECUTE / Pre-RESULT)

- R1: NLL definition (`l1`/`l2`/total under the fixed floored TRAIN
  `p1`/`p2`, layers `A//32`/`A%32`, V49 `nll_u1`/`nll_u2` semantics).
  Confirm this is the intended reading of "per-layer NLL under the fixed
  TRAIN prior" and that scoring-only use is inside the truth boundary.
- R2: `raw_ser = mean(alice != bob)` (raw channel SER) versus any
  decoded-label SER reading of "raw SER".
- R3: CE ratio numerator fixed at the registered `34119` for partially
  invoked blocks (actual disclosure stays in the recount); aggregate
  formula `34119 * (#NLL blocks) / sum(NLL)`.
- R4: manifest path as a frozen module constant (no CLI flag) and the
  repo-relative `--hold-pairs` value with the resolved absolute path
  documented in the freeze doc.
- R5: `sc_calls_exact` / `tags_exact` as recomputed maxima (≤6 / ≤3) so
  legitimate `decode_failed` blocks are descriptive, not integrity
  failures. Confirm this matches the packet's "six SC calls; three tags"
  intent together with the "COMPLETE regardless of 0..3 exact" rule.
- R6: the reused P16 helper's internal P16-domain seed array (in-memory
  only, never scored/persisted) under the P18 `tag_fn` seam; confirm the
  scored-seed proof in `test_fixed_orders_k_tag_domain_and_truth_boundary`
  and `test_tiny_real_block_truth_isolation_and_p18_tag_domain`.
- R7: HOLD parquet expected size (1,354,289) recorded as provenance only,
  never a refusal; the integrity gate is the before/after size+mtime
  equality plus the exact population checks.
- R8: the five invented CLI flags (see above) and the verbatim command in
  `P18_FREEZE.md` §5.
- R9 (found on interrupted-run resumption): the explicit `except` chain
  finalizes BLOCKED only for `HoldoutMicrocheckContractError`,
  `TargetPopulationContractError` and `MemoryError`. A plain `ValueError`
  raised post-open (e.g. the defensive counts-shape check) propagates to
  the CLI, which prints a refusal and returns 2 with the five checkpoint
  files preserved but `aggregate_summary.json` left at
  `pending_content_open`. These defensive branches are unreachable for the
  verified frozen inputs (shape/keys are fixed), so this was left
  unchanged rather than re-writing tested code; the reviewer may require a
  generic finalize if it is judged claim-relevant.

## Test summary

- Focused file `test_nbpolar_holdout_microcheck.py`: 26 tests, all green
  (fresh `/tmp` basetemp, pinned interpreter, `-p no:cacheprovider`).
- Full NB-Polar suite (`test_nbpolar_*.py`, 25 files): 409 tests, all
  green (same settings). Baseline before this wave: 383 (383 + 26 = 409).
- Interrupted-run resumption re-ran both suites green with the same
  settings; earlier 25/408 counts were stale and are corrected here.
