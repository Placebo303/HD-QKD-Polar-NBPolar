# Focused Numerical Review — op-n32k-fine-f4 (A1) & op-n32k-matched (A2)

Verdict: A1 = PASS. A2 = PASS_WITH_COMMENTS.

1. Sign convention correct: prior_m2.py builds `n_plus`/`base` at `mat[(b+1)%N,b]=q_plus1`
   (Alice-Bob=+1 carries q+1). A2's `matched_pmf` assigns `p[(q-1)%q]=pm1=0.2419`, i.e.
   Bob=Alice-1 (delta=y-x=-1) carries 0.2419 -- matches the derivation exactly.
2. Deltas vs predecessor are only the ones authorized: A1 = grid/seeds/output-root/new
   design-sanity assertion; A2 = channel+design_seed+grid/seeds/output-root/wall budget.
   No unauthorized code deltas found in either run.py.
3. Prereg<->run: Q/P/C blocks match run.py constants (seeds, DESIGN_SEED, grid, budgets,
   interpreter/env) verbatim in both prereg.md files.
4. Independently recomputed: H(F4)=0.9318300074841255, H(matched)=0.8165136251021449;
   totals round(f*H*N/5) = 7328/7634 (A1), 6154/6421/6956 (A2); all 18 k1=round(share*total)
   values match exactly; disclosed=5*(k1+k2) and f_book values verified per point.
5. Per-point op/oracle exact counts recomputed from results.json match task figures exactly
   (A1: f1.20 2/1/0, f1.25 6/10/1, oracle 8/1/0,15/10/1; A2: f1.15 0/1/0/0, f1.20 0/10/0/0,
   f1.30 0/13/14/4, oracle 5/1/0/0,14/13/0/0,16/16/14/4).
6. Truth isolation: stop_rules_triggered=[] and undetected=0 in every per-point outcome and
   both global totals, both probes -- genuinely zero, not merged/omitted.
7. (e) decode_failed cause: sc.py/prior.py raise on NaN or all-(-inf) (zero-support) metric
   rows; two_layer.py catches this generically as decode_failed (L1 or L2). No floor is used
   anywhere in the runner path (apply_explicit_floor exists but is opt-in, unused here --
   confirmed by grep). The matched channel's 1021 exact-zero delta cells (vs F4's uniform
   nonzero residual) make this collapse reachable when L1/L2 candidate-conditioning lands on
   a low-probability branch. Per-point counts: T6154_k1_289=4 (L1-only, kdb=1445=5*289),
   T6421_k1_301=4 (L1-only, kdb=1505=5*301), T6956_k1_139=14 (post-L1 L2 failure,
   kdb=34780=5*6956 tag-excluded), T6956_k1_326=3 (kdb=1630=5*326); sum=25, matches. These are
   hard decoder aborts from genuine zero-likelihood conflicts (uncertain L1 candidate at small
   k1 shares), not silent near-misses; oracle (true high value) at T6956_k1_139 reaches
   exact=16/16, showing the failure is allocation-driven (too few L1 bits), not numerical noise
   that would flip to "exact." decode_failed is correctly isolated (never merged into
   exact/FER); reported exact counts are not artificially depressed by it -- a floor would most
   plausibly reclassify these as verify_failed, not exact.
8. Budgets/reruns/scope: A1 wall=2820.3s<4000s, RSS~1.19GiB; A2 wall=2520.4s<6000s,
   RSS~1.20GiB; both reruns=0, cells completed=expected (12/12, 24/24); writes confined to each
   probe's own workspace/probes/<id>/ directory.
9. (g) A1 launch incident confirmed in STATUS.yaml/EXECUTION_TRANSCRIPT: attempt 1 died (WSL
   VM teardown/mount race) before any process started -- no stdout, no results.json from
   attempt 1; correctly excluded from rerun count; attempt 2 is the sole measurement. A2 had one
   clean launch, gated on A1's completion.

Comment (non-blocking): decode_failed is a new outcome class vs the F4 predecessor (zero
occurrences there). For any future claim-bearing (Tier-Y) use of the matched channel, apply an
explicit documented floor (matching the real-data 1e-15 convention) so decode_failed does not
become load-bearing at small-k1 operating points.
