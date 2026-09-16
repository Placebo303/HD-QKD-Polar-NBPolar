# P13 implementation notes (Wave-A: delta + implementation + tests + freeze)

## 1. Decisions

- Thin runner, no new science: `empirical_genie_scaling.py` reuses the
  accepted P7 loader/support/precondition pattern (`target_preconditions`,
  `sample_full_block` wrapper, `Provenance.PRIOR_ONLY` L1 /
  `ORACLE_CONDITIONED` L2 metric wiring), the accepted
  `genie_conditionals` choke point (called, never changed), the accepted
  P11 chunked SC (default `chunk_rows=512` verified by contract check,
  `sc_decode` never called directly), and the P12 f-budget/BEC helpers
  (`budget_k_total`, `allocate_layer_ks` imported, that file untouched).
  P13-specific logic is limited to TRAIN pooling, `(e,h,index)` orders,
  exhaustive `(K1,K2)` selection, scalar DEV residuals, the t-UCB
  aggregate, the 0.01 decision rule, stub-then-checkpoint outputs and
  VmPeak/VmSize records.
- Single genie choke point: every genie/SC call flows through
  `genie_layer_risks` → module-global `genie_conditionals`, counted in
  the runner-owned `calls` budget (incremented even on raises); the
  `no_unregistered_calls` gate requires the exact planned total
  (240 in the frozen run). BEC report-only residuals are pure
  re-indexing of the same DEV rows (`dev_block_residuals`, zero SC by
  construction, covered by a call-count test).
- Stub-then-checkpoint: all five files are created before the content
  open; post-open failures best-effort finalize BLOCKED into the
  existing stubs (documented divergence from P12's no-root refusal,
  required by the packet). Precondition failure therefore keeps zero
  genie calls with consumption spent (tested).
- `student_t_ucb_95` returns `ucb=None` for non-32 sample counts
  (test-seam behaviour only; the frozen run always holds 32 DEV blocks).
  The t factor `1.695518782` is a frozen literal, independently
  recomputed in the test from `math.fsum`.
- Resource stop and MemoryError share one path: preserve checkpoints,
  best-effort BLOCKED finalize, raise
  `EmpiricalGenieScalingResourceError`, never rerun. DEV L1-genie
  failure records a block error (gate fails); TRAIN
  `ImpossibleDisclosedValueError` mirrors the P7 skip counter and fails
  the `zero_genie_exceptions` gate.
- No `formal_ir/nbpolar/__init__.py` change: P7/P12 are also not
  re-exported there; the CLI uses the full dotted path.

## 2. Reuse map (all read-only, unchanged)

- `formal_ir/v35_algorithm_development.py:349`
  `load_v25_channel_counts` — single NPZ content open.
- `nbpolar/target_construction.py` — `target_preconditions`,
  `build_target_conditional`/`target_entropies` semantics,
  `sample_target_block`, `TargetPopulationContractError`,
  `PRECONDITION_ORDER`, P7 TRAIN genie/provenance pattern.
- `nbpolar/construction.py` — `genie_conditionals`,
  `disclosure_order_from_stats`, `analytic_order` (via P12 helper).
- `nbpolar/sc.py` — chunked `_minus_block` default-512 contract only.
- `nbpolar/target_n_scaling.py` — `budget_k_total`,
  `allocate_layer_ks` (BEC report-only arm + replay gate).
- `nbpolar/prior.py`, `nbpolar/empirical_channel.py`,
  `nbpolar/algebra.py`, `nbpolar/transform.py` — metric builders,
  sampler, GF32, polar transform.

## 3. Test summary

- New `comparison_bench/tests/test_nbpolar_empirical_genie_scaling.py`:
  20 tests, all passing (fresh seeds 2026091620..1629; injected
  1024×1024 counts; temp roots; N=64 tiny runs since N=8 cannot clear
  the frozen leakage assert under injected entropies — documented in
  the test helper).
- Full NB-Polar suite green; TRUE total reported at return (the packet
  text cites 262 but the accepted total is 285 after P12's +23; the
  rerun below establishes the new true total including the 20 P13
  tests).

## 4. Review items for the main thread / independent reviewer

- R1 (seed-numeral overlap, non-blocking, no action taken): P13 frozen
  TRAIN seeds 2026091900..1903 for N=16384 coincide numerically with
  test-local seeds in `test_nbpolar_target_n_scaling.py`
  (TEST_SEED_A..D = 2026091900..1903). Those P12 tests use injected
  tables and temp roots only and never open the NPZ, so there is no
  scientific contamination; the P13 seeds remain disjoint from every
  official prior stream. P12's own `PRE_EXECUTE_REVIEW.md` ratified
  "executed seeds >= 2026091900 and disjoint" as test-local space, so
  the overlap is pre-existing and documented on both sides. Flagged for
  awareness only.
- R2 (count convention and full-suite triage): the packet text cites a
  262-test predecessor suite; the true accepted NB-Polar total is 285
  after P12's +23, and the rerun below establishes 305 with the 20 new
  P13 tests. Full `comparison_bench/tests` run (pinned interpreter,
  `-p no:cacheprovider`, 22 pre-existing Windows-path collection errors
  ignored): 2117 passed, 468 failed, 21 skipped in 4617.94 s. All 468
  failures sit in legacy LDPC/nonbinary/v-series files (missing
  sibling-checkout artifacts, `D:/`-path fixtures under WSL); ZERO
  failures in any `test_nbpolar_*` file and none of the failing files
  reference the new module. The failures are pre-existing/environmental
  and out of this wave's scope — reported, not fixed.
- R3 (pre-existing dirty worktree): `git status` at freeze time shows
  modifications predating this wave (P3 queue files, AGENTS.md, memory,
  `nbpolar/__init__.py`, `empirical_channel.py`,
  `empirical_diagnostic.py`, `empirical_oracle.py`, `sc.py`). This wave
  touched none of them; the allowed manifest is listed in the return.
- R4 (`_render_report` tolerance): the report renderer accepts partial
  (RUNNING) cell dicts so per-block checkpointing never crashes on
  missing aggregate keys; final summaries always carry the full keys
  (covered by the tiny end-to-end test asserting all five files parse).
