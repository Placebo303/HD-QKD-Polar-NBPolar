# P16 implementation notes (Wave-A)

## Decisions

- Thin runner only (`operational_f13.py`, ~2240 lines incl. docstrings, no
  new science): TRAIN reuses the accepted P13 genie/construction path
  verbatim in structure; DEV reuses the accepted P8 operational arm shape
  (single arm, causal L1-candidate L2, Toeplitz tag, canonical events,
  literal recount). The only new logic is P16 wiring: empirical
  orders/allocation feeding one operational arm, the six-bucket outcome
  precedence, Wilson recovery gates, and the P16/N/block tag domain.
- `nonfinite` bucket: the packet lists six mutually exclusive buckets
  with a `nonfinite_zero` gate and "nonfinite precedence". No accepted
  module has `nonfinite` as an outcome (P7/P8/P12 use a flag with
  `decode_failed`). Implemented as its own bucket outranking generic
  `decode_failed` (numeric SC failure → `nonfinite`, other SC exception
  → `decode_failed`), with the flag retained for the gate. Record
  consistency enforces the mapping both ways.
- Checkpointing after every TRAIN block as well as DEV: TRAIN
  checkpoints rewrite the same five files with progress counters (no
  records yet); construction content lands at the freeze checkpoint.
  Matches the packet's "after every block" letter with P13's file set.
- Budget breach split: TRAIN breach raises fail-closed (no honest
  construction possible); DEV breach abort-fills remaining blocks and
  completes as BLOCKED (full 64-record evidence). MemoryError anywhere
  post-open finalizes BLOCKED stubs if possible and raises the resource
  error. Nothing reruns.
- `check_wilson_boundary` runs post-open, pre-DEV: pure recomputation
  against the frozen literals, zero artifact interaction, fail-closed on
  accepted-helper drift.
- No `formal_ir/nbpolar/__init__.py` change: P7+ gate modules are not
  re-exported there (accepted convention); tests import the module path
  directly, as do the frozen CLI and prior waves.

## Reuse map (all read-only, none modified)

- P7 `target_construction.py`: `target_preconditions`,
  `PRECONDITION_ORDER`, `TargetPopulationContractError`, entropy report
  fields (`p_b/f/p1/p2/h1/h2`), ratified literal semantics.
- P8 `target_rate.py`: causal L1-candidate-L2 wiring, internal truth
  copies + mutation sentinel, tag invocation shape, disclosure formula
  (`5*K+64`), public-bits formula (`seed_bits_for`), canonical events +
  literal recount, buckets incl. undetected-never-success.
- P11 `sc.py`: untouched; `_minus_block(chunk_rows=512)` default
  contract-checked, `sc_decode` called with production default.
- P12 `target_n_scaling.py`: `budget_k_total` (shared identity),
  f-inequality assert shape, abort-fill + resource-error patterns.
- P13 `empirical_genie_scaling.py`: `block_genie_risks`,
  `select_empirical_split` (shared identity), TRAIN accumulation/pool/
  freeze/SHA shape, stub-before-open + checkpoint discipline,
  reopen guard + accounting shape, MemoryError/contract handlers.
- P4 `two_layer.py`: constants (`DISCLOSED_BITS_PER_COORDINATE`,
  `LABEL_SCALE`, `TAG_BITS`, `labels_to_bits`, `seed_bits_for`),
  outcome-precedence and record-consistency structure.
- Loader `formal_ir/v35_algorithm_development.py:349`
  (`load_v25_channel_counts`): single content open, stat-first.

## Files changed (this wave only)

1. `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p16/spec.md` (new)
2. `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P16 section appended, boxes unchecked)
3. `comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13.py` (new)
4. `comparison_bench/tests/test_nbpolar_operational_f13.py` (new, 23 tests)
5. `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/P16_FREEZE.md` (new)
6. `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/P16_IMPLEMENTATION_NOTES.md` (new)
7. `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/STATUS.yaml` (state update only)

## Tests

- Focused: 23/23 green.
- Full `test_nbpolar_*.py`: 358/358 green (335 predecessors + 23 new),
  pinned interpreter, `-p no:cacheprovider`, fresh `/tmp` basetemps,
  ~19 min wall (large-N predecessor cases dominate).
- Seams: injected `counts`/`expected_entropies`/`tag_fn`; module-level
  `sample_full_block` / `block_genie_risks` / `run_operational_block` /
  `_budget_exceeded` patch points (same pattern as P13/P15 tests).

## Review items (for independent Pre-EXECUTE/Pre-RESULT)

See `P16_FREEZE.md` §9 (five items). No self-acceptance; state left at
`IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`.
