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
