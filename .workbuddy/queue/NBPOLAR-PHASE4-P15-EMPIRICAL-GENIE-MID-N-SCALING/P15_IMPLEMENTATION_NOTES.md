# P15 IMPLEMENTATION NOTES — empirical-genie mid-N scaling

Wave-A delta log: OpenSpec delta + thin runner + focused tests + freeze
docs. No gate execution, no commit. Decisions, the P13/P14 reuse map, and
items flagged for the independent Pre-EXECUTE reviewer.

## Decisions

1. **Mirror P13's structure, drop the second arm.** The runner
   (`comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_mid_n.py`)
   follows `empirical_genie_scaling.py` block-for-block (stub-first five
   files, stat-then-open input, P7 preconditions, per-N TRAIN-freeze-DEV
   loop, per-block checkpointing, MemoryError/contract/resource handlers,
   12-gate integrity order) minus everything P15 forbids: no second
   residual arm, hence no `allocate_layer_ks`/`analytic_order` import, no
   `bec_*` records, and a df=15 UCB helper (`ucb_95_t15`,
   factor 1.753050356) instead of P13's df=31 one.
2. **Per-N TRAIN-then-DEV loop (not P14's all-TRAIN-first).** The packet
   requires each N's order/allocation/TRAIN residual frozen BEFORE that
   N's first DEV call, so the loop is per N cell: 16 TRAIN, freeze, 16
   DEV. Consequence for tests: the deterministic genie fake keys its
   TRAIN/DEV formula off position within each 32-call N group
   (`(k % 32) < 16`), not a global TRAIN/DEV split — an early version of
   the fake used P14's global split and failed replay, which caught the
   mismatch before any production use.
3. **Run-level refusal of non-frozen N/bps (P14-style, stricter than P13).**
   `n_values != [32768, 65536]` and bps != 4/4 raise before the open;
   exact frozen seed VALUES stay as integrity gates (so injected-data test
   runs complete as `BLOCKED(two_n_cells_complete)`). Rationale: the
   packet forbids any other N outright.
4. **Per-block record resources.** The packet's "resources per record" is
   implemented literally: every DEV jsonl record carries
   `{wall_s, rss_bytes_hwm, vm_peak_kb, vm_size_kb}` alongside the
   P13-style per-cell resource records.
5. **Order-stability diagnostic.** Per-stream TRAIN accumulators are kept
   alongside the pooled ones; per-stream worst-first orders are scored by
   Spearman against the pooled order via the accepted
   `spearman_rank_corr` on position ranks. Diagnostics-only: excluded from
   the freeze SHA and from every gate.
6. **No package export change.** `formal_ir/nbpolar/__init__.py` does not
   export P13/P14 either; tests import the module by full path, so no
   export edit was needed (minimal diff).
7. **Float tolerance 1e-9 (not 1e-12) for injected mean/std recomputation.**
   Residuals reach ~1e4 at N=65536; runner-side numpy mean vs test-side
   `math.fsum` differ by ~1.8e-12 from summation order alone (relative
   ~2e-16). Order/allocation replay stays exact (1e-15/identical op order).

## P13/P14 reuse map (all READ, none changed)

- From accepted P13 `empirical_genie_scaling` (shared identity, asserted
  by test): `block_genie_risks` (sole genie choke point, calls counter),
  `residual_for_orders` (DEV residual kernel), `select_empirical_split`
  ((e,h,index) orders + lexicographic (residual,K1,K2) rule).
- From accepted P7 `target_construction`: `target_preconditions`,
  `PRECONDITION_ORDER`, `TargetPopulationContractError`, entropy literals
  H1/H2/total, support rule, floor/column tolerances.
- From accepted P12/P13 `target_n_scaling`: `budget_k_total` ONLY (no BEC
  allocation helper — forbidden here).
- From accepted P11 `sc.py`: chunk contract check only (`_minus_block`
  default 512, keyword-only, `sc_decode` chunk-free); called with
  chunk_rows=512 via the P13 genie path.
- From accepted loader `formal_ir/v35_algorithm_development.py:349`:
  `load_v25_channel_counts` (single NPZ-mode call site + reopen guard).
- Structural reference only: P14 `empirical_genie_learning_curve.py`
  (two-seam fake pattern, per-N-freeze layout, stub-first checkpointing).
- Accepted `construction.py`: `disclosure_order_from_stats`,
  `spearman_rank_corr`; `empirical_channel.sample_full_block`;
  `prior` PRIOR_ONLY/ORACLE_CONDITIONED metrics; `algebra.make_gf32`;
  `transform.polar_transform`; `sc.ImpossibleDisclosedValueError`.

## Test summary

`comparison_bench/tests/test_nbpolar_empirical_genie_mid_n.py`, 15 tests,
fresh seeds 2026091770..1785, injected 1024x1024 counts + temp roots only:
frozen K pins (6811/13636, both H spellings), matrix constants, P13-helper
identity (+ df=31 helper explicitly NOT shared), both-N grouping +
mis-grouping refusals, separation, order/allocation replay with closed-form
pooled means, DEV residual formula + df=15 stats, df=15 UCB literal with
df=31 factor absence asserted on module source, pure DEV residual,
checkpoint refusal, partial-failure preservation, injected accounting +
reopen guard, precondition BLOCKED stubs, MemoryError classification, CLI
parse refusal (subprocess), forbidden-access rule (functional tokens incl.
`bec_report_only`/`r_bec`/`allocate_layer_ks`/`analytic_order` absent).

## Items flagged for the independent Pre-EXECUTE reviewer

1. Confirm the frozen command (P15-06) is byte-identical to
   `FROZEN_COMMAND` in the runner and this freeze doc, incl. the export
   line, `ulimit -v 2097152`, and `timeout 2100`.
2. Recompute both K_total values from the literals (6811/13636) and the
   df=15 factor 1.753050356 against an independent t-table.
3. Confirm the absent root, the 25166822-byte stat expectation, and that
   `STATUS.yaml` still shows reads/attempts 0 with result null.
4. Confirm no decision-arm/BEC/tag/Toeplitz/FWHT/APP/SCL token reaches any
   runner code path (functional grep, not prose grep).
5. Confirm the per-N TRAIN-freeze-before-DEV ordering in code, and that
   the order-stability diagnostic cannot feed any gate or label.
6. Wall-margin check: 64 blocks at N=32768/65536 under 2 GiB/2100 s —
   the focused suite's real-transform faked runs average ~75 s per
   64-block pass on this machine, but the frozen run uses real genie
   rows; verify margin explicitly before authorization.

No OpenSpec box was checked by this session. No production behavior was
authorized by these docs.
