# P14 IMPLEMENTATION NOTES (Wave-A)

## 1. Decisions

1. **Hard-freeze structural parameters in code.** `n` (16384),
   `prefix_blocks` (8/16/32/64/128), `train/dev_blocks_per_stream`
   (16/8) are validated for exact equality BEFORE the content open
   (ValueError refusal, no root created). Only the seed lists vary, so
   focused tests can run the full-shape 160-block matrix with injected
   counts + faked seams while the frozen-seed gates keep the candidate
   path exclusive to the frozen point. Rationale: smallest validation
   surface; "N other than 16384" is unrepresentable, not just gated.
2. **Single stream-major TRAIN pass with running sums.** Prefix-B means
   are `sums_B / B` at the moment `used == B`; no block is revisited.
   The no-repeated-calls property is enforced structurally (one loop)
   and counted exactly (320-call budget gate), and verified numerically
   by tests (closed-form prefix means from the fake's formula).
3. **Five-way DEV scoring from one decode.** Each DEV block's genie rows
   are scored against all five frozen `(order, k1, k2)` arms with the
   shared P13 `residual_for_orders`; DEV layer-calls stay 64 = 32x2
   (not 32x5x2). Tests assert the exact recomputation for all 160
   block-prefix pairs.
4. **Paired differences reuse the t-UCB helper.** `paired_diff_stats`
   is a thin alias of P13's `student_t_ucb_95` (32 paired differences
   carry the same df=31 factor 1.695518782). Non-32 inputs yield
   `ucb_95_t31 = None` (partial checkpoints only, never the final gate).
5. **Report-only top-K depth.** Overlap of prefix-B orders vs B=128 is
   measured at the frozen B=128 layer allocation (K1_128 for L1,
   K2_128 for L2): "how much of the final disclosed set was already
   top-ranked at prefix B". Depth 0 (possible only off the frozen
   point) records None. Interpretation, not selection.
6. **Checkpoint after every TRAIN and DEV block** (160 checkpoints of
   the same five files), per the packet's "after every block". Partial
   summaries carry `TRAIN(k)` / `RUNNING(k)` labels and live gates.
7. **No package-export change.** Like the P13 module, the runner is
   reached as a submodule (`...nbpolar.empirical_genie_learning_curve`)
   for both `python -m` CLI and test import; `__init__.py` needed no
   edit (minimal diff).
8. **No BEC arm.** P14 has no same-entropy BEC control (unlike P13):
   report-only diagnostics are Spearman/top-K overlap, allocation
   movement, and improved/tied/regressed counts. One fewer import,
   one fewer residual path, zero extra SC calls by construction.

## 2. P13 reuse map (read, not changed)

| P14 use | Accepted source | How |
|---|---|---|
| NPZ loader + one-open pattern + reopen guard | `v35_algorithm_development.load_v25_channel_counts` | same call shape, same accounting dict |
| floor/support rule + entropy/column preconditions + literals/tolerances | `target_construction.target_preconditions`, `TargetPopulationContractError`, `PRECONDITION_ORDER` | same call, same zero-genie fail-closed |
| per-block genie risks + calls counter + `(e,h,index)` orders + split rule + scalar residual + t-UCB | `empirical_genie_scaling.block_genie_risks`, `residual_for_orders`, `select_empirical_split`, `student_t_ucb_95` | imported (identity-pinned by test); sampling/oracle-genie exactly P13 |
| f-budget `floor((f*N*H-64)/5)` clip | `target_n_scaling.budget_k_total` | same call (3399 at frozen point) |
| sampler, metrics, provenance, transform, field | `empirical_channel.sample_full_block`, `prior.*`, `transform.polar_transform`, `algebra.make_gf32` | same call shapes as P13's loops |
| chunk contract (default-512, keyword-only, no sc_decode arg) | `sc._minus_block` introspection | verbatim check, same refusal |
| report-only rank stats | `construction.spearman_rank_corr`, `topk_overlap` | pure helpers |
| impossible-disclosure skip accounting | `sc.ImpossibleDisclosedValueError` | same TRAIN skip semantics |
| stub-before-open + per-block checkpoint + MemoryError finalize + resource error | P13 module structure | same ordering, P14 file names |

## 3. Test design (15 tests, injected + faked seams only)

- Fakes: deterministic `FakeGenie` (TRAIN formula over blocks 0..127,
  DEV formula over 128..159, exact +2 calls-counter per block call) and
  constant `fake_sample`; metrics/transform/orders/splits/stats/gates/
  checkpointing run for real. Fresh seeds 2026091741..1752 (census
  below); frozen streams 1930..1943 appear only as pinned constants.
- Full-shape runs (3 x 160 blocks, ~80 s each): nested/call-budget/
  stream-order test, order-K-replay test, five-way + paired-UCB +
  report-only recompute test.
- Pure/cheap tests: K pin (3399 both H spellings), matrix constants,
  helper-identity pins, paired-diff edges, six refusal tests (seed
  shape, disjointness, n, prefixes, chunk, bps, existing root, CLI
  parse exit 2), precondition-failure zero-genie BLOCKED stubs,
  MemoryError classification, injected accounting zeros, forbidden-token
  scan.
- Seed census (2026-09-15, repo-wide `202609[0-9]{4}` over
  py/md/yaml/json): 1930..1943 absent everywhere except frozen P14
  packet files + Wave-A additions; test seeds 1741..1752 absent
  everywhere before this wave (nearest used: 1740, 1760).

## 4. Errata found and fixed during Wave-A (all covered by tests)

1. **String-sorted prefix keys (runner bug, would have failed three
   final gates permanently).** `sorted()` over the `"8".."128"` dict
   keys yields `['128','16',...]`; three gate comparisons used it.
   Fixed to set equality (`nested_prefixes_exact`,
   `orders_valid_frozen_before_dev`, `budget_allocation_reproduced`).
   Found by `test_order_k_replay_per_prefix`.
2. **Run-K vs literal-K gate conjunct (runner, test-data only).** The
   replay gate additionally required the run's K to equal the literal
   3399, which fails on injected entropies by design. Replaced with
   run-self-consistency (`cell k_total == run k_total`); literal
   reproduction stays via `cell k_total == 3399`. Frozen run unaffected
   (floor stable, §3 of freeze doc).
3. **Test-side issues (no production impact).** Two tests read artifacts
   outside the `TemporaryDirectory` block (FileNotFoundError);
   RNG-seed logger also captured the `injected_counts` draw (precompute
   counts outside the patch; `full_run` now lazy-builds counts and
   forwards `expected_entropies`); RNG-per-stream (12 creations, not
   160) corrected the stream-major assertion; `sorted(prefixes)` in one
   test corrected to a set comparison.

## 5. Review items (for independent Pre-EXECUTE / Pre-RESULT)

1. Wall-budget headroom: ~1170 s projected (4x P13's accepted N=16384
   cell at ~7.3 s/block incl. two SC decodes) vs the 1800 s cap.
   Sampling dominates (accepted Python-loop sampler, unchanged).
2. The literal-K gate arm assumes the measured H reproduces 3399; raw
   is 3399.493 (0.007 from the boundary), so the 1e-12 literal
   tolerance cannot flip it — recomputation in Pre-RESULT will confirm.
3. On injected (non-frozen-seed) data the expected end-to-end label is
   `BLOCKED(streams_disjoint_frozen)` with all mechanical gates green;
   tests pin exactly this (mirrors P13's tiny-run BLOCKED pattern).
4. `test_no_production_raw_hold_access_rule` bans `analytic_order` /
   `allocate_layer_ks` tokens: P14 deliberately has no BEC arm, so a
   future BEC addition must update that test consciously.
5. Dirty-worktree note: the checkout was already dirty before Wave-A
   (prior-phase uncommitted docs/code, e.g. P3 STATUS, sc.py, registry
   files). Wave-A wrote only its six allowed files and ran no
   commit/push.
