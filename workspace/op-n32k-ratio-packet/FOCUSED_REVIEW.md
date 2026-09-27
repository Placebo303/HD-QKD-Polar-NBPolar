# Focused review — op-n32k-ratio (Tier-X, reviewer-go)

## Part 1 — verdict: PASS

Numbered findings (all checked against the actual files, not the packet's own prose):

1. **Diff vs op-peak-refine/run.py** (`workspace/probes/op-n32k-ratio/run.py` vs
   `workspace/probes/op-peak-refine/run.py`): every changed line maps to an authorized
   delta — `PROBE_ID`/`OUT` path, `Q/R/N/NLOG` (1024/10/32768/15), the `POINTS` grid
   (8 labeled points replacing the 3-point `K1_GRID`), `BASE_ID`, `SEEDS`
   (2026092801/02), `BLOCKS=8`, `DESIGN_SEED=2026092800`, `DESIGN_MC=64`,
   `WALL_LIMIT_S=5400`/`RSS_LIMIT=4GiB`, `NUMBA_CACHE_DIR`. Additions beyond the
   bare parameter swap are all benign: three `assert` grid-consistency checks
   (re-derive `total`/`k1`/`disclosed`/`f_book` from the frozen rule — guards
   transcription typos only, does not change semantics), two `print(..., flush=True)`
   progress lines, new `total`/`f_book_target`/`share_target`/`k1_share_actual`
   fields on each point record (additive), `block_wall_s` added to `records[]`
   (real field — see finding 2), and aggregation keyed by `f_label` instead of
   `k1` (finding 3). No frozen semantics (F4 model, M2 prior tables, two-layer
   GF32 SC/oracle logic, `toeplitz_master`, `worst_k` rule, undetected-STOP/
   isolation, RNG scheme) were touched, matching the prereg's stated inheritance.
2. `res.block_wall_s` (new field the runner reads) is a genuine attribute of
   `TwoLayerBlockResult` (`comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py:527,826`),
   not a fabricated placeholder.
3. Aggregating `points[].per_seed` by `f_label` (total,k1,k2) rather than `k1` alone
   correctly implements the prereg's explicit requirement ("aggregation keyed by
   unique point label ... never by k1 alone"); with 8 distinct k1 values in this
   grid the old `k1`-keyed filter would have given the same result here, so this
   is a robustness improvement, not a correctness fix forced by a collision.
4. `results.json` completeness and arithmetic verified directly: `cells
   {expected:16, completed:16}`, 8 points × 2 seeds × 8 blocks = 128 blocks,
   `design.a3_design_samples=64`, `a3_H1_mean=0.130552`, `a3_H2_mean=1.400117`
   (matches EXECUTION_TRANSCRIPT's H1=0.1306/H2=1.4001 exactly). Grid arithmetic
   recomputed independently: `H*N=30534.205685`, `T7939=round(1.30*HN/5)=7939`,
   `T9771=round(1.60*HN/5)=9771`, `disclosed=5*T` (39695/48855) and all 8
   `k1=round(share*total)` values match the prereg table exactly (319/6811, 0.09,
   0.14, 0.20 shares for both totals). `a3_key_dependent_bits_observed=[39759,
   48919]` = disclosed+64 in both cases, correct.
5. Truth isolation: `a3_outcomes_operational_total`/`_oracle_total` both show
   `{exact:0, undetected:0, verify_failed:128, decode_failed:0,
   resource_abort:0}` — `undetected` is genuinely 0 (not merged/hidden), and
   every per-point breakdown (`operational_totals`/`oracle_totals` on all 8
   points) shows the same isolated buckets (0/0/16/0/0). "Every point 0/16 in
   both arms" in the transcript is accurate.
6. Write scope: `git status` shows no changes under `results/`,
   `comparison_bench/outputs_comparison/` (other than a pre-existing, unrelated
   dirty file present at session start), or any other probe directory; the run
   only touched `workspace/probes/op-n32k-ratio/` and
   `workspace/op-n32k-ratio-packet/`. `workspace/probes/op-n32k-ratio/` and the
   packet dir are gitignored by the `workspace/*`/`workspace/probes/*` allowlist
   pattern (a pre-existing repo convention for probe scratch dirs, not a new
   issue).
7. `reruns=0`, `probe_runs=1`, no `execution_error_attempt1.json` present, stop
   list empty — matches the one-shot rerun policy. `wall_s=3649.563 ≤ 5400`;
   `peak_rss_bytes=1,210,146,816` (~1.13 GiB) `≤ 4 GiB`. `run_stdout.log` shows
   the design phase finishing at wall=901.6s and each of the 16 cells advancing
   in ~170–175s increments to the final 3649.6s, consistent with `within_budget:
   true`.
8. Minor pre-existing (not new) observation: `run.py` line 11
   (`sys.path.insert(0, "/mnt/d/Code/qkd-reconciliation-lab/src")`) reaches into
   a sibling checkout that is not one of the three sibling projects named in
   AGENTS.md §0; it is unchanged from `op-peak-refine` and is needed only for
   `qkd_recon.polar_core` (used by the never-invoked `a2_chain`/`a2_masks` dead
   code — A2 is not run in this probe). Not a defect introduced by this delta;
   flagging for awareness only.

No FAIL-level issues found.

## Part 2 — the 1.531 vs 0.932 gap

**What the design "entropy" measures.** `H1`/`H2` in `run.py` are genie-SC
per-coordinate entropies: `sc_decode` is called with `known_positions=allpos`
(every coordinate forced to its *true* transform-domain value), so the
recursive polar combine/split (`_minus_block`/`_plus_block` in
`comparison_bench/.../nbpolar/sc.py`) always propagates the true side
information. `decision_metrics[offset]` is nonetheless the full model
posterior over the 32-symbol alphabet at that coordinate (not collapsed to the
known value), and `H1`/`H2` average `-Σ p log2 p` over that posterior, over
positions and MC draws. `H1` uses `p1` under `Provenance.PRIOR_ONLY`
(marginalized over `low`); `H2` uses `p2` under `Provenance.ORACLE_CONDITIONED`
(conditioned on the *true* `high`). This is exactly the standard polar
synthetic-channel entropy construction — **provided** `p1`/`p2` (built via
`tl.layer_metric_tables(table)`, i.e. `derive_p1`/`derive_p2` in `prior.py`)
represent the *true* channel. `sc.py`'s own metric contract says
`logp_x[j,a] = ln P(X_j=a | Bob/context)`, i.e. the table must equal
`P(Alice=a|Bob=b)` (equivalently, under the uniform Alice/uniform-Bob
symmetry that holds here, `P(Bob=b|Alice=a)`).

**The bug.** `run.py` builds `table = pmf[(np.arange(Q)[:, None] -
np.arange(Q)[None, :]) % Q]`, i.e. `table[a,b] = pmf[(a-b) % Q]`. The true
generative model is `y = (x+delta) % Q` with `delta ~ pmf`, so the correct
value is `table[a,b] = P(Bob=b|Alice=a) = pmf[(b-a) % Q]`. Because `pmf` is
strongly asymmetric (`p(+1)=0.24` vs `p(-1)=0.005`), `pmf[(a-b)%Q] ≠
pmf[(b-a)%Q]`: the code feeds the decoder the *mirror-image* channel (as if
`delta` were negated). Both sign conventions happen to pass the module's own
`colsum==1` sanity check (the circulant is doubly stochastic either way), so
nothing in the pipeline catches it. This line is identical in
`op-peak-refine/run.py` and `op-n32k-ratio/run.py` — the bug is inherited, not
new to this probe, and it affects both the design-entropy diagnostic *and* the
actual per-block operational/oracle metrics (`p1_table`/`p2_table` passed into
`tl.run_two_layer_block` are the same buggy tables), so it is a possible
contributor to the poor decode results (0/16 exact everywhere), not just to
the entropy bookkeeping.

**Analytic/empirical check** (`workspace/probes/op-n32k-ratio/review_scratch/check_table_sign.py`,
run via the repo's own WSL venv, using the real `prior.py`/`sc.py`/`two_layer.py`
code, small N so it runs in seconds):

| quantity | value |
|---|---|
| `H_F4` (exact entropy of the true delta pmf) | 0.9318300074841255 (matches `frozen_params.H` exactly) |
| cross-entropy of true delta under the mirrored model, `H(true‖mirror)` | 2.2443 bits (whole-symbol, non-layered) |
| `H1+H2`, AS-CODED table, N=256 / N=1024 (48 MC samples) | 1.3357 / 1.3946 |
| `H1+H2`, CORRECTED table (`pmf[(b-a)%Q]`), N=256 / N=1024 | 0.9554 / 0.9356 |

The **N=1024 AS-CODED value (1.3946) reproduces op-peak-refine's actual
measured 1.3963 (H1=0.1273,H2=1.2691, DESIGN_MC=128) almost exactly** — the
tiny residual is Monte-Carlo noise from using a different design seed and
MC=48 vs 128. The corrected-table run at the same N lands at 0.9356,
i.e. essentially exactly `H=0.9318` (residual is finite-N + MC noise, both of
which shrink with more samples/larger N). The AS-CODED sum also grows with N
(1.336→1.395 for N=256→1024), consistent with the observed further increase
to 1.531 at N=32768 in the actual probe: unlike the true-channel case (where
the genie-SC chain rule is an *exact* invariant, sum/N·N = H(X|Y) for any N),
a mismatched-model genie-SC average is not entropy-conserving under
polarization — the average cross-entropy-like quantity drifts with N as the
mismatch interacts with polarization, rather than converging to a fixed value
at small N. I did not re-run the corrected table at the full N=32768 (would
take tens of minutes at this MC count and is outside this review's "seconds
only" analytic budget); the N=256/1024 trend and the exact match of the
AS-CODED N=1024 result to op-peak-refine's real measurement is strong enough
evidence for the diagnosis without it.

**Conclusion.** The 1.531 (N=32768) / 1.396 (N=1024) vs 0.932 gap is
overwhelmingly explained by a channel-direction (sign) bug in this probe
family's local `table` construction, not by a genuine two-layer disclosure
floor of the F4 channel. Fixing the one line (`table[a,b] = pmf[(b-a)%Q]`
instead of `pmf[(a-b)%Q]`) brings the design-entropy sum back down to ≈`H`
in the small-N check. This bug is local to these standalone Tier-X probe
scripts' own inline circulant construction (`op-peak-refine`/`op-n32k-ratio`
`run.py`); the real-data G1R2 CAL32 pipeline builds its prior from empirical
Alice|Bob counts directly (per `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md`,
q0/q+1/q−1/q_rest = 0.7562/0.2419/0.0018/0) and never reconstructs a synthetic
delta-circulant, so it is not exposed to this specific bug — the synthetic
testbed is mismatched in a way the real-data pipeline is not. The operator's
descriptive observation ("every point 0/16, both arms, isolated") is accurate
and correctly reported as non-claim; their *causal explanation* (a genuine
≈1.64-bit informational floor) is not supported — the floor is an artifact of
the sign bug, and it likely also degraded the actual per-block decode metrics
used in this run, not only the entropy bookkeeping. Recommended fix for any
successor probe: correct the `table` line and re-freeze a fresh Tier-X probe
(new prereg) before drawing any further allocation conclusions from this
family.
