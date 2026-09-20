# Design: SCL Synthetic List Gate (scoping only — nothing authorized)

All gates below are `NOT AUTHORIZED`. This design freezes a selection rule and an interface
shape; it freezes NO working-point numbers, NO L values, NO pruning thresholds.

## (a) Synthetic SC-vs-list distinguishing working point

### Channel construction (synthetic, in-body, no artifact reads)

- Family: diagonal/structured per-column model over Alice labels, X15-recipe shape kept as the
  structural template (diagonal pin + concentrated-neighbor share + planted rare-zero pin +
  diffuse rest), followed VERBATIM by the accepted pipeline: raw-count MLE + 1e-15 floor +
  column renormalize -> `derive_p1` / `derive_p2` (A = 32*U1 + U2, FULL_BOB_ONLY) ->
  `probs_to_symbol_metric`. Read-only reuse of `empirical_channel` (sampling recipes),
  `prior`, `algebra.make_gf32`, `transform.polar_transform`, `sc.sc_decode` (greedy L=1
  reference arm only).
- Parameterization uses ONLY recorded scalars as qualitative pins (never content opens):
  p_err ~0.25 context (P20J recorded raw SER ~0.2520/0.2526/0.2535, 1.5M population caveat);
  96/1024 = 9.375% rare-zero pin (vs recorded 3063/32768 = 9.3475% block-0 figure);
  X06 f_min 0.0002142 / f_max 0.3392 as qualitative sharpness context (different smoothing,
  no quantitative transfer). The working-point channel strength (diagonal mass) is NOT frozen
  here — it is the primary tuning axis of the selection rule below.
- No protected opens: pairs/V25/parquet/1M/1.5M/2M content, `raw_prior_*.npz` never imported
  or touched (path-refusal asserts in any future body).

### Scale / disclosure operating point (must differ from proven-pointless configs)

Proven-pointless triples (never to be re-asked):

| Probe | N | Disclosure passed to SC | Channel | Outcome |
|---|---|---|---|---|
| X14 | 256 | none (K2=52 for pm/K only) | flat Dirichlet | mismatch 0.96903 ~= chance; Q1 0.0 structural; Q2 void |
| X15 | 256 | none (prefix first 52) | 0.75 diagonal | mismatch 0.96863; G1 stop |
| X16/X17-C | 32768 | K1=334 + K2=6746 forced-correct | 0.75 diagonal (+H-a confound in X16; corrected in X17) | mismatch 0.76902 ~= 0.76931 ceiling; corrected C still at chance |

The new working point MUST differ on at least one operating-point axis, chosen by this rule:

1. Pick (N, K1, K2, channel-strength) such that greedy-SC mismatch sits in an INFORMATIVE
   variance band — strictly below the applicable no-information ceiling
   (undisclosed: 31/32 = 0.96875; disclosed: (1-K2/N)*31/32) by a preregistered margin, AND
   strictly above near-perfect decoding (so a list has room to add value). Exact band edges
   are frozen at freeze time, not here.
2. Candidate axes (one or more must move; freeze picks the minimal delta): (i) channel
   strength weaker than 0.75-diagonal (higher diagonal mass toward the P-control regime that
   decoded at 0.000); (ii) intermediate N with exact-ratio disclosure (same K/N ratios as
   2M literals 334/32768, 6746/32768, zero rounding analysis at freeze); (iii) disclosure
   placement variants (first-K vs hazard-ranked — placement is a caller-side truth-injection
   choice, never a `sc.py` change); (iv) the list-decoding question itself (per-position
   coverability vs path-survival — see gate (c)).
3. Why: X14/X15 prove undisclosed small-N points sit at the chance ceiling regardless of
   per-column sharpness; X16/X17 prove the full-scale 0.75-diagonal + full-disclosure point
   sits at its own ceiling even with corrected truth-side. Re-asking survival at any of those
   exact triples is proven pointless (decision-log closeout). The working point earns its name
   only by showing SC-vs-list separation.

### Discriminating measurement (what "distinguishes" means)

- Reference arm: frozen greedy `sc_decode` (L=1) per block (sole decoder use at this stage).
- List arm: the new list decoder (interface below) at the same block, same metrics, same
  disclosure — paired comparison, per-seed values + mean/sample-std/range.
- Primary signal: paired SC-vs-list gap (mismatch delta and/or exact-block delta,
  descriptive, no thresholds at this stage) PLUS X14-style top-L survival at frozen-hazard
  spikes (gate (c)). A working point qualifies as distinguishing only if BOTH the gap is
  non-degenerate (neither arm at ceiling nor at floor) AND spike strata are populated
  (spike-fraction band check carried from X16-G3 shape, edges frozen at freeze).
- Q2 (F-median8 vs mean-hazard coverage) may be re-asked only if mismatch variance exists;
  otherwise recorded null-with-reason per X14-review precedent.

### List decoder interface (new module alongside frozen sc.py — sc.py stays untouched)

- Location (placeholder, NOT created by this scoping): a NEW module under
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/` (e.g. `scl.py` — name frozen at
  freeze, not here). `sc.py` is read-only inventory: its `sc_decode(logp_x, *, field,
  alpha=2, known_positions=None, known_values=None) -> SCResult` signature, natural-order
  recursion, argmax-ties-to-smallest convention, `ImpossibleDisclosedValueError` /
  `NumericNonfiniteError` failure categories, and `chunk_rows=512` default are reused by
  reference, never edited.
- Interface shape (placeholders, NO frozen values yet):
  `scl_decode(logp_x, *, field, alpha, known_positions, known_values, list_width_L,
  prune_rule) -> SCLResult` where `list_width_L` is a caller-supplied positive integer
  (no default frozen here), `prune_rule` is an opaque callable/strategy slot (pruning
  criterion, reliability-gating hook, spike-local hook — mechanism UNFROZEN, values NONE),
  and `SCLResult` carries per-path survivors (u_hat candidates, path metrics, survivor flags,
  provenance). Metric contract identical to `sc.py` (float64 log-scores, symbol axis last,
  logsumexp-0 rows, exact-zero `-inf` preserved, NaN/+inf rejected).
- Extension point: the future body imports the frozen `sc.py` for the L=1 reference arm and
  the new module for list arms; shared minus/plus kernels reused by import where the freeze
  allows, never by editing `sc.py`.

## (b) L-ladder decision procedure (L from the working point, never inherited)

1. At the frozen working point, measure the survival-vs-L curve: per-position top-L survival
   fractions at frozen-hazard spikes (strata [2,4)/[4,8)/[8,inf) + nonspike_ref, margin
   2.0 bits, `sc.py` tie convention) over a SWEEP of L probed descriptively (sweep set frozen
   at freeze; NOT this survey's set).
2. Derive the ladder FROM the curve: pick the smallest L where marginal survival gain bends
   (knee), one L at saturation (plateau), and optionally one economy L below the knee — with
   the exact rule (e.g. gain-per-doubling thresholds) frozen at freeze time from pilot
   variance, never here.
3. The survey's L in {4, 8, 32} (Yuan/Abbasi/Falk context: GF256 L/4; N=8192 GF16/L=8 ~=
   GF4/L=32; short-block 32/100/625) is EXPLICITLY non-binding context — recorded for
   provenance, never auto-inherited (survey section 7 adjudication). A binary/CRC-SCL control
   at matched L is context for ladder resolution (Falk q-mismatch warning), not a frozen arm.
4. Output: a re-justified ladder (2-4 values) with the measured curve attached; any future
   SCL-unlock claim must cite survival at THOSE L values, not at survey values.

## (c) X14-style survival gate restated (the unlock criterion — unchanged semantics)

For any future SCL-unlock claim, ALL of the following hold (X14 section 2 / X15 section 2 /
X16 section 2 verbatim-compatible):

- Hazard atom (frozen recipe `l2_alt_hold_1p5m.py:1321`): h_j = -log2 p2[u1_cond_j, b_j,
  u2_true_j], bits base 2; exact-zero mass raises (synthetic construction guarantees positive
  arm-table mass).
- Spike: prefix-mean pm = mean(h_j) over the disclosed prefix (`l2_prefix_hazard_mean_bits`
  recipe); position j is a spike iff excess e_j = h_j - pm >= 2.0 bits; strata
  [2,4)/[4,8)/[8,inf) + nonspike_ref. Bins are recording buckets, never verdicts.
- Ranking: at each L2 position with conditioning (u1_cond_j, b_j) from the operational path,
  sort 32 u2 symbols by arm-table mass descending, ties to smallest index (`sc.py` argmax
  convention); r_j = 1-based rank of true u2_j; survives_j(L) iff r_j <= L; survival fraction
  = mean over spike positions per block, per-seed then pooled mean/sample-std/range,
  stratified by bin x L. Q1b symmetric with p1 columns and true u1.
- Gate: true-path top-L survival at frozen-hazard spike positions, at the re-justified L
  values from (b), measured at the distinguishing working point from (a). Coverability is a
  necessary-condition proxy, reported as such; path-survival (list decoder retaining the true
  path end-to-end) is the stronger successor question, separately gated.

## (d) Rebuild-vs-reuse split

- Reusable read-only (never edited): frozen SC path (`sc.py` incl. `chunk_rows=512`,
  failure categories, tie convention); prior recipes (`derive_p1`/`derive_p2`,
  `build_p1_metrics`/`gather_p2_metrics`, `probs_to_symbol_metric` incl. natural-log and
  FULL_BOB_ONLY semantics); metric definitions (hazard atom, prefix-mean, F-median8 R=8
  detector); transform/algebra (`polar_transform` natural order, involution, `make_gf32`
  poly 37, alpha=2); X14-X17 prereg/body/results pattern (3-line prereg, probe-root-only
  writes, per-seed + pooled stats, stop-payload discipline, evidence-size <= ~2 MB).
- New (this track only): list decoder module + its focused tests; working-point body (channel
  + disclosure + paired SC-vs-list comparison); L-ladder derivation record; survival-gate
  measurement at the new point. New files live in new probe roots + the new packet dir; no
  existing production, evidence, ledger, or sibling-checkout file is modified.

## (e) Gate sequence (every item NOT AUTHORIZED)

1. `G0 proposal` — this change (design + tasks + skeleton). [NOT AUTHORIZED beyond scoping]
2. `G1 freeze review` — independent review of the frozen working-point numbers, interface
   freeze, seed grep proof, and prereg text. [NOT AUTHORIZED]
3. `G2 implementation authorization` — explicit user authorization to create the new list
   module + probe body (new files only). [NOT AUTHORIZED]
4. `G3 focused tests` — T0/T1 green (self-tests: tie-break, diagonal-smoke, disclosure-smoke,
   order-identity, gate asserts) + full NB-Polar suite green; T2 only at milestones.
   [NOT AUTHORIZED]
5. `G4 single synthetic execution` — one frozen-command run, probe-root-only writes,
   `results.json` scalar-only (< 2 MB), zero protected opens. [NOT AUTHORIZED]
6. `G5 focused numerical review` — independent reviewer-go Tier-X review (commands,
   completeness, arithmetic, truth isolation, write scope). [NOT AUTHORIZED]
7. `G6 acceptance` — main-thread acceptance of descriptive results; decides ladder + whether
   any unlock-gate attempt is warranted. No FER/reliability/efficiency claim, no real-data
   follow-on, no production merge implied. [NOT AUTHORIZED]

Cross-cutting: SCL stays locked through G6; RN scope untouched; per-probe ledger/memory/index
updates milestone-batched per Tier-X rules.
