# P7 freeze — NB-Polar Phase 4-P7 target-population empirical construction

Rev 1 (2026-09-14). Frozen by the operator session under the exact user
authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond the packet
`TASK_PACKET.md` and the X07 main-thread disposition were invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No gate run has been executed. The single artifact content read is **0
consumed** and the single scientific attempt is **0 consumed** at freeze; both
are consumed at the first NPZ content open
(`load_v25_channel_counts`). `STATUS.yaml` keeps `artifact_reads_used: 0` and
`attempts_used: 0`. The real output root is **ABSENT**.

## 1. Scope

One Tier-Y target-population development gate: does the frozen V25 1M TRAIN
count population support pooled-empirical two-layer hard-candidate SC at
`N=256` with `K1=45` and `K2=140`, measured as empirical exact recovery over
640 paired DEV blocks against the frozen scientific gates? This is a
construction/protocol development signal for the frozen V25 TRAIN empirical
distribution only; it is not held-out or real frame FER, efficiency, leakage,
key rate, scaling, qualification or promotion evidence. No Model-F artifact,
raw/held-out/real frame, EVAL stream, `N>256`, APP/SCL/FWHT, production
benchmark, old-root modification, commit or push. No tuning, no rerun.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core + CLI | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_construction.py` |
| tests | `comparison_bench/tests/test_nbpolar_target_construction.py` (11 focused tests) |
| reused unchanged | `v35_algorithm_development.load_v25_channel_counts`; `construction.genie_conditionals/disclosure_order_from_stats/spearman_rank_corr/topk_overlap/analytic_order`; `prior.derive_p1/derive_p2/build_p1_metrics/gather_p2_metrics/probs_to_symbol_metric/Provenance`; `sc.sc_decode`; `transform.polar_transform`; `empirical_channel.sample_full_block`; `algebra.make_gf32`; `two_layer.labels_to_bits/seed_bits_for/OUTCOMES/DISCLOSED_BITS_PER_COORDINATE/LABEL_SCALE/TAG_BITS`; `protocol.wilson_lower_bound/WILSON_Z`; `shared.toeplitz_tag/canonical_event` |
| changed accepted modules | **none** (`sc.py`, `prior.py`, `construction.py`, `protocol.py`, `two_layer.py`, `penalty_gate.py`, `adaptive_l1.py`, `incremental.py`, `transform.py`, `algebra.py`, `empirical_channel.py`, `v35_algorithm_development.py` untouched) |
| benchmark adapter | **none added** (the frozen command imports the module path directly) |
| OpenSpec | `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p7/spec.md` + the P7 section of `tasks.md` (all P7 boxes unchecked) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3); interpreter used for every focused command below |
| untouched | frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, every existing evidence root |

## 3. Frozen input and support rule

- Counts path:
  `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
- Stat-only pre-check (before any content open): the file exists and
  `st_size == 25166822`. Metadata-only verification performed at freeze:
  observed size `25166822` bytes (no content open).
- Loader (single call, one artifact content read + one scientific attempt
  consumed at the first NPZ content open; no reopen, no retry):
  `comparison_bench.src.comparison_bench.formal_ir.v35_algorithm_development.load_v25_channel_counts`.
  Source selected: `1M`, `[Alice,Bob]` shape `[1024,1024]`.
- Support rule (the only one): column-normalize the raw counts, replace every
  cell below `1e-15` by `1e-15`, renormalize each Bob column; `p_b` from the
  column totals over the total count; `P1`/`P2` from the accepted
  `derive_p1`/`derive_p2` of the floored table under `A = 32*U1 + U2`. No
  lambda, backoff, tuning, floor scan or held-out fitting.
- Preconditions (all evaluated before any genie/SC call; failure raises
  `BLOCKED(target_population_contract)` and creates no output root):
  1. no zero Bob column;
  2. `p_b` normalization and conditional-table column error `<= 1e-12`;
  3. `H1` within `1e-12` of `0.02428054681872374`;
  4. `H2` within `1e-12` of `0.7767572780789994`;
  5. total within `1e-12` of `0.8010378248977232`;
  6. floor-induced total-entropy change relative to the raw MLE table
     `<= 1e-9`.

### 3.1 Entropy functional (explicit Pre-EXECUTE review item)

The checked `H1`/`H2`/total are the **raw-MLE in-sample population conditional
entropies** of the accepted V26/V49 chain:

```text
H1 = sum_b p_b H(P1_raw(:,b)),   P1_raw = derive_p1(counts / column totals)
H2 = sum_b p_b sum_u1 P1_raw(u1|b) H(P2_raw(u1,b,:)),  P2_raw = derive_p2(counts / column totals)
```

This is the functional behind `SOURCE_H`/V26 `adapter_H` for 1M
(`0.0242805468186788`, `0.7767572780789986`; `nbldpc_v26_20260818` m0 reports)
and the V27R/decision-log statement that recomputing `H` from
`channel_counts.npz` matches the frozen docs; it matches the packet literals
(V49 1M TRAIN `nll_u1`/`nll_u2`/`nll_total`) to `<= 5e-14`.

The floored protocol table's entropies are computed only for precondition 6.
On a V25-like sparse count matrix (~2-3 nonzero cells per Bob column, ~1020
floored cells per column) the `1e-15` floor adds a cell mass of
`~1e-12` per column; the floored-table functional therefore shifts H1 by
`~4.3e-11` and the total by `~5.1e-11` (literal-size arithmetic reproduced on
a synthetic sparse mimic), which exceeds the `1e-12` literal tolerance but
stays well inside the `1e-9` floor guard. The strict "entropy of the floored
table" reading of the packet would make precondition 3/4 unsatisfiable; the
population reading above is the accepted chain and the only reading consistent
with the packet's own thresholds. **The independent Pre-EXECUTE reviewer must
confirm this functional before the gate runs.**

## 4. Frozen construction

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural order;
  `q=32`, `N=256`.
- TRAIN streams `2026091650, 2026091651, 2026091652`, 256 blocks each.
- DEV streams `2026091660, 2026091661, 2026091662, 2026091663, 2026091664`,
  128 common blocks each = 640 paired blocks. TRAIN and DEV streams are
  disjoint; no EVAL stream exists.
- Per-DEV-stream public Toeplitz master `stream_seed + 10000`, domain-separated
  by arm (`empirical`/`bec`) and block index; 2623 public seed bits per tag.
- Sampling: `B ~ p_b` (256 `rng.random` draws against the cumulative `p_b`),
  then `A ~ P_floor(A|B)` (256 draws against the per-coordinate cumulative
  column); `high = A//32`, `low = A%32`; one explicit
  `np.random.default_rng(stream_seed)` per stream, no global RNG.
- TRAIN statistics per layer: L1 metric `build_p1_metrics(bob, P1)` with
  `u_true = polar_transform(high)`; oracle-L2 metric
  `gather_p2_metrics(bob, high, P2)` with `u_true = polar_transform(low)`;
  accepted `genie_conditionals` full-true accumulation
  (`h += -log2 p(u_true)`, `e += 1 - max p`); `ImpossibleDisclosedValueError`
  blocks are counted and skipped.
- Orders: per-stream and pooled worst-first
  `disclosure_order_from_stats(e/used, h/used)` for L1 and oracle-L2, all
  frozen (canonical SHA-256 digest of the layer payloads recorded) before the
  first DEV call; every order must be a permutation of `0..255`.
- BEC analytic controls: `epsilon_l = H_l/5` (population `H_l`),
  `analytic_order(epsilon_l, 256)`; report-only, never selects the empirical
  order.

## 5. Frozen DEV protocol

Every DEV block runs two paired arms on the same sampled block:

1. `empirical`: L1 SC on the P1 metric (`PRIOR_ONLY`) with the pooled
   empirical L1 order first `K1=45`; then L2 SC on the candidate-conditioned
   P2 metric (`CANDIDATE_CONDITIONED`, gathered from Bob and the hard L1
   candidate `high_hat = sc1.x_hat`) with the pooled empirical oracle-L2 order
   first `K2=140`;
2. `bec`: the same two fresh SC calls with the BEC L1/L2 orders.

Each arm restarts SC by layer (no state, belief or partial sum transfer),
rebuilds `label_hat = low_hat + 32*high_hat` and invokes one 64-bit Toeplitz
tag over the MSB-first 10-bit expansion, arm/block-domain-separated. Alice
truth enters only sampling, the disclosed `U` values, tag construction and
scoring; a per-block sentinel mutates internal truth copies after the metrics
and decisions exist and requires the protected metrics/decisions to stay
bitwise.

Outcome buckets (disjoint, exhaustive over planned blocks): `exact` (tag pass
AND label equal to truth), `undetected` (tag pass and not exact; never
success), `verify_failed`, `decode_failed` (SC exception or nonfinite
marginals; no tag), `resource_abort`. Paired cells:
`both_exact`/`empirical_only`/`bec_only`/`neither`.

## 6. Frozen accounting

- Fully invoked arm: `5*(45+140)+64 = 989` key-dependent bits (L1 `225`, L2
  `700`, tag `64`); `2623` public control bits per invoked tag. L1 disclosure
  counts even when the L1 SC call fails; L2/tag bits only when invoked.
- Independent literal transcript recount of L1 disclosure, L2 disclosure and
  verification-tag events (parsed from the arm-tagged event id) must equal the
  incremental totals and per-arm totals with zero mismatch.
- Attempt/read accounting: `artifact_reads_allowed=1`,
  `attempts_allowed=1`, both consumed before this run `0`, consumed by this run
  `1`, `retries=0`, no reopen, no retry after open; the consumption point is
  the first NPZ content open.
- Budget: 2 GiB RSS peak and 3600 s total wall (`timeout 3600`,
  `ulimit -v 2097152`); a budget breach before the order freeze raises and
  writes nothing; a DEV-phase breach fills the remaining planned blocks with
  `resource_abort` arms and returns `BLOCKED`.

## 7. Frozen gates and labels

Integrity gates (persisted booleans, frozen order): `target_population_contract`,
`coverage_complete_and_disjoint`, `orders_frozen_permutations_provenance`,
`pairing_and_buckets`, `truth_leak_zero`, `undetected_zero`,
`nonfinite_zero`, `resource_abort_zero`, `disclosure_and_recount_exact`,
`attempt_read_accounting_exact`, `resource_limits_met`.

Scientific gates (frozen order): minimum pairwise TRAIN-order Spearman
`>= 0.95` for L1 and L2 (the six pairwise correlations among the three
per-stream orders and the pooled order; BEC correlations are report-only);
empirical arm exact `>= 620/640`; empirical one-sided 95% Wilson exact-recovery
lower bound `>= 0.95` (`z = 1.6448536269514722`).

Labels: all integrity and scientific gates true at the frozen 640-pair shape
-> `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`; integrity true and any scientific
gate false -> `TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED`; integrity false ->
`BLOCKED` with the failing gate names in frozen order (operator maps to
`BLOCKED(<earliest gate>)`). Precondition failure ->
`BLOCKED(target_population_contract)` with no output root. BEC-control exact
counts, paired cells, rank correlations and top-K overlaps are report-only; no
gate requires empirical to beat BEC.

## 8. Frozen command (verbatim; the only authorized execution)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_construction --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --n 256 --floor 1e-15 --train-seeds 2026091650 2026091651 2026091652 --train-blocks 256 --dev-seeds 2026091660 2026091661 2026091662 2026091663 2026091664 --dev-blocks 128 --k1 45 --k2 140 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate
```

No rerun, seed/order/K/floor/threshold change or partial replacement after the
content open. Stop and preserve the failure root on precondition/entropy
mismatch, target presence, command/test error, resource breach, truth leak or
any integrity failure; do not fix and rerun.

## 9. Frozen output root and five-file schema

Root:
`.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`
(absent at freeze; must be absent before execution), containing exactly:

| file | contents |
|---|---|
| `frozen_plan.json` | protocol, point/constants, support rule, entropy literals/functional, streams/masters, accounting, gate orders, labels, budgets, frozen command, claim scope |
| `construction_orders.json` | per-stream/pooled/BEC L1 and L2 orders, per-stream/pooled sufficient-statistic scalars, provenance flags, `orders_sha256`, `frozen_before_dev`, `orders_unchanged_after_dev` |
| `per_block_paired_outcomes.json` | 640 records: stream seed, block index, paired cell, per-arm scalar buckets/accounting/error types |
| `aggregate_summary.json` | entropy checks, BEC epsilons, cells/marginals, per-stream results, construction stability, integrity/scientific gates, Wilson bound, disclosure recount, planning-only `f`, wall/RSS, accounting, label |
| `report.md` | human-readable rendering of the summary |

Scalar/aggregate only: symbols, labels, disclosed values, decoded keys and raw
seed bits are never persisted.

## 10. Forbidden-path proof (what the frozen run may touch)

- Reads: exactly one content open of the registered `channel_counts.npz`
  through the accepted loader (plus its stat metadata). No read of the Model-F
  artifact (`model_f_input.npz`), `pairs.parquet`, TTBin, held-out/eval files,
  raw data or any other evidence root.
- Writes: exactly the five files under the frozen root after the run completes.
  No write to `results/`, `comparison_bench/outputs_comparison/`, old evidence
  roots, sibling checkouts, OpenSpec or packet files during execution.
- Import safety: the focused suite includes an empty-cwd import subprocess that
  asserts no file creation, and the module contains no import-time I/O, no
  global RNG, and no `open(` call.
