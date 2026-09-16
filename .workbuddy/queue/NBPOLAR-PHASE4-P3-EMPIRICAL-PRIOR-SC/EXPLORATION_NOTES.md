# P3 Stage A/A2 exploration notes (synthetic only, no artifact read)

Packet: `NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC`, Stage A + A2.
Artifact-content attempts consumed: **0**. No sibling read, no
`results/`/`outputs_comparison/` write. All tables below are
caller-injected (hand-built or frozen-seed RNG).

Frozen synthetic seeds (selected before sampling; disjoint from every
predecessor stream): unit `2026091314`, train `2026091315`, diagnostic
`2026091316` (`empirical_channel.P3_*_SEED`). Banned predecessor range
`2026091200..1213` is refused by `make_rng` (tested both boundaries).

## A13/A19 — dual-path P1 metric gather

- Hypothesis: a vectorized fancy-index gather and an independently
  written literal per-cell loop agree exactly on every injected shape.
- Tried: `build_p1_metrics` (operational, `mat[:, idx]` transpose) vs
  `build_p1_metrics_literal` (plain-Python per-cell copy, reference-only).
- Evidence: 100 injected cases x 2 shapes (dense/sparse/one-hot/mixed,
  1D+2D Bob) → max abs err `0.0`, support mismatches `0` (gate ≤1e-12).
  Production-shape parity vs accepted `prior.build_p1_metrics` on
  `(32,1024)` → bitwise `0.0`.
- Rejected: making the literal loop operational (10-80x slower, grows
  with N; measured below), and routing the operational path through
  `prior.build_p1_metrics` (keeps the channel import-free so truth
  isolation holds by construction; parity is tested, not inherited).
- Final: vectorized operational, literal test-reference only.

## A14 — representation study

- Hypothesis: probability rows (adapter-internal) vs natural-log rows
  (decoder-facing) need one canonical form with owned conversion.
- Tried: local generic `_to_log` (any q) vs accepted
  `prior.probs_to_symbol_metric` (pins q=32).
- Evidence: parity at q=32 → support equal, finite-entry max err ≤1e-15;
  `exp(log)` round-trips positive entries ≤1e-12; exact zeros stay
  `-inf`. SC public contract (`logp_x`, natural base) untouched.
- Rejected: converting inside the channel module (would duplicate the
  accepted converter) and canonical-probability (SC takes log).
- Final: canonical is normalized log; conversion owned by the adapter
  via the accepted helper at q=32.

## A15 — numerical stress

- Covered: likelihood rows down to `1e-300`, exact zeros, single
  surviving symbol, uniform, concentrated; GF32 N=2 SC smoke.
- Evidence: no NaN/`+Inf`; `-Inf` exactly equals the zero mask;
  per-row positive rescaling (prob or log domain) keeps `u_hat` bitwise.
- Rejected: direct probability-product oracle arithmetic — products of
  tiny rows underflow below ~1e-308 while the literal log-sum stays
  finite; `empirical_oracle` therefore scores `sum logp` with standalone
  logsumexp (same math, stable arithmetic).

## A16 — transform/interface metamorphism

- Covered: butterfly-vs-dense on GF4 N=2/4/8 + GF32 N=2 (0 mismatches);
  Bob-batch permutation equivariance of the gather; disclosed-coordinate
  input-order irrelevance on SC decisions.

## A17 — failure taxonomy

- Each forced case reaches its specified fail-loud category:
  impossible disclosure → `ImpossibleDisclosedValueError`; bad table
  normalization / bad symbol / wrong shape / nonfinite table →
  `channel contract` ValueError/TypeError; NaN log rows →
  `metric contract`; duplicate positions → `known-coordinate contract`.
  Nothing degrades into a decode count.

## A18 — complexity baseline (GF32 q=32, injected tables)

Median of 5 calls after 1 warm-up, metric vs decode separated, peak RSS
(`ru_maxrss`, GiB). No size skipped (stop rule: prior size >120 s or
RSS ≥1.5 GiB — never triggered).

| N | metric vec (s) | metric lit (s) | SC decode (s) | peak RSS (GiB) |
|---|---|---|---|---|
| 2 | 0.000009 | 0.000107 | 0.001085 | 0.091 |
| 4 | 0.000007 | 0.000110 | 0.001194 | 0.091 |
| 8 | 0.000006 | 0.000111 | 0.001447 | 0.092 |
| 16 | 0.000007 | 0.000130 | 0.002106 | 0.092 |
| 64 | 0.000007 | 0.000206 | 0.007093 | 0.092 |
| 256 | 0.000010 | 0.000518 | 0.032654 | 0.094 |
| 1024 | 0.000022 | 0.001797 | 0.155724 | 0.103 |

Scaling: gather ~flat (memory-bound micro-op); decode follows the
expected `N q^2 log N` reference curve. Shapes `(N,32)` verified at
every N. No performance claim; numbers are Stage B budget inputs only.

## Stage A gate status (synthetic)

P3-A01--A12 + packing/derivation parity: 23/23 pytest green
(`test_nbpolar_empirical_sc.py`); full predecessor suite
(transform/sc/construction/r1/prior/prior_artifact/p2r1 + new):
110 → 111 green, 0 failed. Pre-EXECUTE review (seeds, Stage B
masks/counts/command/target, attempt accounting) is the next gate and
is owned by the main thread + independent reviewer — not this operator.

# Stage B implementation notes (synthetic/injected only, artifact attempt 0)

Scope: make the frozen Stage B command executable (`--mode stageb`),
implement the vectorized exhaustive oracle backend, and add the Stage B
tests. The accepted artifact was **not** read: artifact-content attempts
consumed = **0**, target root still ABSENT. No real Stage B command ran.

## Alternatives compared

- **Literal oracle at GF32 N=4** (q^N = 1048576 candidates, per-candidate
  Python enumeration + dense reference transform): rejected as the B1
  backend — minutes-to-hours per prefix and refused above the unchanged
  4096 default cap. The literal function stays exactly as accepted for
  tiny domains; parity tests call it with an explicit test-only
  `max_candidates` opt-in at prefixes of length >= 2 (32 and 1 candidate
  suffixes).
- **Vectorized single-prefix backend** (recompute the 1M-candidate score
  vector per oracle call): works, but the frozen B1 compares all 4 nested
  prefixes per block, so it costs ~4x. A batch-prefix API
  (`empirical_oracle_conditionals_vectorized`) computes the joint scores
  once per block and evaluates each nested prefix as one contiguous
  mixed-radix slice logsumexp; the single-prefix function is now a thin
  wrapper over it. Measured chain cost 0.17-0.19 s per N=4 block → 64-block
  full-coordinate sweep ≈ 11-12 s (in-runner oracle wall 11.7 s; final
  standalone median 0.1724 s/block → 11.0 s), well under the 120 s
  per-case soft stop.
- **Batched butterfly transform instead of the dense batch transform**
  (42 ms vs 104 ms per N=4 call): rejected — the dense batch transform is
  validated row-wise against `polar_transform_reference`, and the chain
  design already brings the sweep far under budget; a second transform
  variant is duplicate surface without a gate it would change.
- **Stateful candidate/transform cache**: rejected (hidden state; no
  custom caching policy in this repo).
- **Per-case fresh RNG seeds**: rejected — one `make_rng(2026091316)`
  stream in frozen case order is the frozen contract.

## Measured cost (injected (32,8) tables, temp root; no artifact)

- Full frozen matrix (B1-B4 + B5 aggregation, default 120 s/3600 s caps):
  wall ≈ **18.1 s**, exactly 5 files, coverage complete, hard gates pass,
  truth-leak violations 0, resource aborts 0.
- B1 N=4: 64 blocks × 4 conditionals = 256 oracle rows, oracle wall
  **11.7 s**; max prob err 5.3e-16, finite max log err 5.3e-15, support
  mismatches 0 (gates 1e-12 / 1e-9).
- B4 medians (1 warm-up + 5 measured): metric 9.0e-6 / 1.9e-5 / 6.1e-5 s
  and decode 7.5e-3 / 3.4e-2 / 1.6e-1 s at N=64/256/1024; shapes
  (4,N,32)/(N,32)/(N,32); peak RSS ≈ 0.22 GiB.
- Tests: focused file 32 passed in 29.1 s; full predecessor suite
  (8 files) **120 passed** in 65.3 s.

## Rejected / corrected details

- **B4 disclosed values**: true U first (spec-aligned disclosure map); if a
  true value is impossible, fall back to the metric argmax at that
  position and record `disclosed_value_source`. Always-argmax and
  unguarded true-U were rejected (one impossible disclosure would abort a
  timing case).
- **Peak RSS unit fix**: `_peak_rss_gib` now scales `ru_maxrss` as KiB on
  Linux (bytes on macOS). The previous `/1024**3` under-reported by 1024x
  on this platform, which would have made the 2 GiB envelope evidence
  meaningless.
- **Alias keys**: `n_blocks` (= planned) and B3 `n_nan` (= `n_nonfinite`)
  are recorded so the compact JSON matches the frozen B2/B3 report
  wording exactly; B5 records `b4_scored_blocks = 0` because B4 is
  timing-only and never scored.
- **Full-matrix test seam**: `_run_stageb_from_tables` (keyword-only
  caps, optional `artifact_identity`) lets ordinary tests run the entire
  frozen matrix on injected tables and temp roots; artifact/root/seed
  refusal paths are tested with nonexistent temp paths only.
