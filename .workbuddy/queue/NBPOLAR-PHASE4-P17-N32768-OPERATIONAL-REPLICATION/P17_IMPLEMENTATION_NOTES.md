# P17 implementation notes (Wave-A)

## Decisions

- Thin replication runner only
  (`comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13_replication.py`,
  ~1690 lines incl. docstrings, no new science): the P16 operational block
  path (`run_operational_block`, outcome precedence, record/event/recount
  helpers) is reused by import, never reimplemented. The only new logic is
  P17 wiring: predecessor-file identity verification, the 128-block fresh
  DEV matrix, the P17 tag-domain closure, 121/128 + Wilson-0.90 gates with
  the total pinned to 128, and the thirteen-flag CLI. Reusing P16's `run`
  entry point was impossible: it hardcodes the TRAIN phase, the P16 tag
  domain and the 64-block matrix.
- No construction path of any kind: L1/L2 orders and (K1, K2) arrive only
  through the verified P16 file, are never recomputed, and the module
  contains zero TRAIN/genie/BEC/adaptive/order-selection code paths
  (asserted by the forbidden-token test).
- P17 tag domain via the accepted `tag_fn` seam: each block precomputes
  `replication_seed_bits(master, n, gidx)` under the P17 prefix and the
  scored tag uses exactly that seed. Known wart (review item R1): the
  accepted P16 block helper still derives its own internal P16-domain
  array before invoking `tag_fn`; that array is in-memory only, never
  persisted and never scored. The focused test proves the scored seeds
  are P17-domain and differ from the P16-domain bits for the same inputs.
- Exact-seed pin is a gate, not a refusal (P16 precedent): refusals cover
  stream count, distinctness, P16 overlap, digest flag and contracts, so
  fresh-seed injected tests can execute the full pipeline; a non-frozen
  grouping runs but fails `dev_coverage_complete` /
  `streams_disjoint_frozen`. The frozen gate still enforces the exact
  eight streams through those gates plus the frozen CLI.
- Recovery total pinned to 128: `recovery_gates(exact, total=128)` fails
  the count gate for any other total, so the P16 62/64 context is
  structurally excluded from the decision (tested explicitly).
- `verify_predecessor_construction` checks file self-consistency (protocol
  marker, N/K/orders/digest recompute, K/f replay from the literals);
  `run_operational_replication` additionally pins the `--construction-
  digest` flag to the frozen digest before any root exists. Split keeps
  the verifier unit-testable with fabricated files.
- P17-local transcript event builders reuse `shared.canonical_event`:
  reusing P16's `block_events` would stamp P16 frame keys and method
  names into P17 evidence. Recount semantics are identical (literal,
  N/arm-tagged, tamper-detecting).
- No `__init__.py` export change: P7+ gate modules are not re-exported
  (accepted convention); tests import the module path directly, as do
  the frozen CLI and prior waves.
- The generic block-exception path builds a correct zero-disclosure
  error record from `(seed, block_index, k1, k2)` directly. P16 is
  untouched.

## Reuse map (all read-only, none modified)

- P16 `operational_f13.py`: `run_operational_block`,
  `classify_operational_outcome`, `_block_record`, `_abort_block`,
  `_record_dict_consistent`, `_transcript_mismatches`,
  `_order_is_permutation`, `_check_chunk_contract`, `_cell_resource_record`,
  `_peak_rss_bytes`, `_budget_exceeded`, `_write_json`, `_append_jsonl`,
  `OperationalBlockResult`, `TargetPopulationContractError` (via P16's
  re-export of the P7 error), constants (`EXPECTED_H1/H2/TOTAL`,
  tolerances, `PROTOCOL_NAME`, `EXPECTED_NPZ_BYTES` shape).
- P7 `target_construction.py`: `target_preconditions`,
  `PRECONDITION_ORDER`, entropy report fields (`p_b/f/p1/p2/h1/h2`),
  ratified literal semantics.
- P11 `sc.py`: untouched; `_minus_block(chunk_rows=512)` default
  contract-checked through the P16 helper, `sc_decode` reached only
  inside the accepted block helper with the production default.
- P4 `two_layer.py`: constants (`DISCLOSED_BITS_PER_COORDINATE`,
  `LABEL_SCALE`, `TAG_BITS`, `labels_to_bits`, `seed_bits_for`).
- `shared.py`: `toeplitz_tag` (P17-domain closure), `canonical_event`
  (P17 transcript builders).
- Loader `formal_ir/v35_algorithm_development.py:349`
  (`load_v25_channel_counts`): single content open, stat-first.

## Files changed (this wave only)

1. `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p17/spec.md` (new)
2. `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P17 section appended, boxes unchecked)
3. `comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13_replication.py` (new)
4. `comparison_bench/tests/test_nbpolar_operational_f13_replication.py` (new)
5. `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/P17_FREEZE.md` (new)
6. `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/P17_IMPLEMENTATION_NOTES.md` (this file)
7. `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/STATUS.yaml` (status fields only)

No other source, evidence root, output, seed, or config touched. No
commit/push.

## Review items (for independent Pre-EXECUTE / Pre-RESULT)

- R1: P17 tag-domain closure vs the helper-internal P16-domain array
  (in-memory only, never persisted/scored). Confirm the scored-seed
  proof in `test_p16_operational_parity_and_p17_tag_domain` is sufficient.
- R2: exact-seed pin as gate rather than refusal (P16 precedent).
  Confirm the frozen CLI + shape gates enforce the frozen matrix.
- R3: P16-non-pooling by pinned total (128) plus report-only context.
  Confirm no gate input admits P16 observations.
- R4: canonical digest recipe equality with P16 (key set, separators,
  sort order). Confirm byte-equality reasoning.
- R5: abort-fill and MemoryError paths preserve checkpoints and never
  rerun. Confirm BLOCKED finalization coverage.

## Test summary

- Focused file `test_nbpolar_operational_f13_replication.py`: 25 tests,
  all green (fresh /tmp basetemp, pinned interpreter, `-p
  no:cacheprovider`).
- Full NB-Polar suite `test_nbpolar_*.py`: 383 tests, all green
  (same settings). Baseline before this wave: 358.
