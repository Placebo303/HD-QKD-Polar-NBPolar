# P12 implementation notes (Wave-A)

## Decisions

1. **Reuse, no new science.** The runner imports the accepted P7
   `build_target_conditional`/`target_preconditions`/`sample_target_block`/`classify_outcome`
   semantics, the accepted `analytic_erasure_probs`/`analytic_order`
   recurrence and order, the accepted `derive_p1`/`derive_p2`,
   `build_p1_metrics`/`gather_p2_metrics`/`probs_to_symbol_metric` with
   `PRIOR_ONLY` → `CANDIDATE_CONDITIONED` provenance, the accepted
   `sc_decode` (P11 chunked `_minus_block`, called not changed), and the
   P8 two-layer hard-candidate/Toeplitz/accounting pattern. No
   `sc.py`/`target_rate.py`/`target_construction.py`/loader/adapter edit.
2. **Frozen scalars enforced, N/shape variable.** The runner refuses
   `source != 1M`, `floor != 1e-15`, `target-f != 1.3` and
   `chunk-rows != 512` before any artifact access (mirroring the P7
   frozen-point style), while `n-values`/`stream-seeds`/`blocks` are
   variable-length lists so injected tests can use tiny shapes. The gates
   (not the parser) enforce the six-N/128-block frozen shape.
3. **Budget assert placement.** The `leakage <= 1.3*N*H` check runs at
   allocation time (before any SC) and raises the
   `budget_allocation_orders_reproduced` BLOCKED label on violation; for
   the frozen six points it holds with margin (worst `f = 1.29998`).
   Tiny-N injected shapes (e.g. N=8 with realistic H) correctly fail
   here because the 64-bit tag alone exceeds their budget; the focused
   end-to-end tests therefore use N=64/128.
4. **Exit codes.** `0` iff the run completed and persisted a frozen label
   (candidate or BLOCKED) with the five files; `2` on pre-completion
   refusals. This mirrors P7 (which exits 0 for NOT_CONFIRMED) rather
   than P11 (which exits 1 for non-candidate); both frozen labels are
   completed-run outcomes here.
5. **Reproduction tolerance.** `K_total`/`K1`/`K2`/orders reproduce
   exactly from the literals; the residual reproduces within `1e-9`
   (worst observed measured-vs-literal drift 1.5e-10). Exact float
   equality on the residual would be spurious, so the gate uses the
   bound; the argmin itself is stable to 1e-6 relative perturbations.
6. **Seed domain.** Tag seed prefix
   `nbpolar-p12-n-scaling-seed:<master>:<n>:verify:<block>` carries all
   four frozen dimensions; the layer token is the constant `verify`
   because exactly one verification tag is invoked per block.
7. **Clopper-Pearson from scratch.** Two-sided 95% intervals via a local
   continued-fraction incomplete beta plus bisection (no new
   dependency); the focused tests verify every reported bound against
   the independent `math.comb` binomial-tail identity, which caught and
   fixed a log-beta sign error during this wave.
8. **No package export change.** The CLI addresses the full dotted path,
   so `formal_ir/nbpolar/__init__.py` is untouched.

## Reuse map

| Need | Source (unchanged) |
|---|---|
| floor/support/preconditions/entropy | `target_construction.py` |
| chunked SC (`chunk_rows=512`) | `sc.py` via `sc_decode` |
| BEC recurrence/order | `synthetic.analytic_erasure_probs`, `construction.analytic_order` |
| P1/P2 tables, metrics, provenance | `prior.py` |
| block sampler | `target_construction.sample_target_block` → `empirical_channel` |
| outcome precedence | `target_construction.classify_outcome` |
| accounting constants/events/tag | `two_layer.py`, `shared.toeplitz_tag`/`canonical_event` |
| loader (single content open) | `v35_algorithm_development.load_v25_channel_counts` |

## Bugs found and fixed in-wave (with failing command + raw error)

1. `test_clopper_pearson_edges`: `_betai` log-beta sign error
   (`lgamma(a+b)-lgamma(a)-lgamma(b)` is −ln B; fix:
   `lgamma(a)+lgamma(b)-lgamma(a+b)`). Raw: `hi` for (0,4) returned
   `0.2857` vs closed form `0.602`.
2. `test_transcript_recount_literal`: `recount_events` seeded each
   per-N slot from the already-incremented running totals, double
   counting the first event per N (94 vs 84). Fix: zero-initialized
   slots before accumulation.
3. `test_l2_metric_uses_hard_candidate_not_truth`: test patched
   `prior.gather_p2_metrics`, but the runner holds its own imported
   reference; patch `target_n_scaling.gather_p2_metrics`. Test-side fix.
4. Tiny-N end-to-end (N=8): allocation correctly refused
   (`leakage 64 exceeds f-budget 12.09...`); tests moved to N=64/128.
   Behavior-as-designed, no code change.

## Review items for independent Pre-EXECUTE

- a. The `"13-flag"` wording in the wave brief vs the nine `--flags` in
  the P12-06 command (nine required flags; "13" appears to count
  otherwise). The implementation requires exactly the nine frozen flags.
- b. Exit-0-on-BLOCKED decision (§6 of the freeze): confirm the
  main thread wants completed `BLOCKED(<gate>)` runs (five files
  persisted) to exit 0 rather than P11-style 1.
- c. Residual reproduction uses the 1e-9 bound (§5/§8 of the freeze);
  confirm the bound is acceptable as "exact reproduction" evidence.
- d. Tag-seed layer token is the constant `verify` (one tag per block);
  confirm this satisfies "domain-separated by P12/N/layer/block".
- e. Test count note: this wave adds 23 focused tests, so the combined
  green run is 285 (262 predecessor + 23), not 272.
