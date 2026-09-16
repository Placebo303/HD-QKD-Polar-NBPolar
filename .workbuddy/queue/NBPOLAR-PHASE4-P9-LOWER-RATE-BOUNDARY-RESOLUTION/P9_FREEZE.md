# P9 freeze — NB-Polar Phase 4-P9 lower-rate boundary resolution

Rev 1 (2026-09-14). Frozen by the Wave-A implementing session under the
exact user authorization in `AUTHORIZATION_PROMPT.md`; no semantics beyond
the packet `TASK_PACKET.md` were invented.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No gate run has been executed. The single artifact content read is **0
consumed** and the single scientific attempt is **0 consumed** at freeze;
both are consumed at the first NPZ content open
(`load_v25_channel_counts`). `STATUS.yaml` keeps `artifact_reads_used: 0`
and `attempts_used: 0`. The real output root is **ABSENT**.

## 1. Scope

One Tier-Y static lower-rate gate: over the exact 8x7 empirical-order
grid at `N=256` on the accepted V25 1M TRAIN model, including both zero
axes, select the lowest-disclosure point clearing the frozen SCREEN
reliability rule, then test that single selected point once on disjoint
CONFIRM streams with a paired BEC-order control. This resolves P8's
left-censored rate search and is the final N=256 static-rate localization
gate before a main-thread choice between adaptive target-rate work and
N-scaling/decoder acceleration. It is not held-out or real frame FER,
efficiency, leakage, key rate, scaling, qualification or promotion
evidence. No Model-F artifact, raw/held-out/real frame, EVAL stream,
`N>256`, APP/SCL/FWHT, production benchmark, old-root modification,
commit or push. No tuning, no rerun, no interpolation or unregistered
point.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core + CLI (delta-only) | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py` (adds `--gate-id`, P9 protocol/prefix/labels/grid/root; P8 path byte-for-byte) |
| tests (additions only) | `comparison_bench/tests/test_nbpolar_target_rate.py` (12 P8 preserved + 12 new P9 focused tests) |
| reused unchanged | `v35_algorithm_development.load_v25_channel_counts`; `target_construction` support/precondition/sampler/bucket helpers; `construction.analytic_order`; `prior.derive_p1/derive_p2` `build_p1_metrics/gather_p2_metrics/probs_to_symbol_metric/Provenance`; `sc.sc_decode`; `transform.polar_transform`; `algebra.make_gf32`; `two_layer.labels_to_bits/seed_bits_for/OUTCOMES/DISCLOSED_BITS_PER_COORDINATE/LABEL_SCALE/TAG_BITS`; `protocol.wilson_lower_bound/WILSON_Z`; `shared.toeplitz_tag/canonical_event` |
| changed accepted modules | **none** (`sc.py`, `prior.py`, `construction.py`, `protocol.py`, `two_layer.py`, `target_construction.py`, `empirical_channel.py`, `v35_algorithm_development.py` untouched) |
| package exports | **none added** (frozen command and tests import the module path directly, P7/P8 precedent) |
| benchmark adapter | **none added** |
| OpenSpec | `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p9/spec.md` + the P9 section of `tasks.md` (all P9 boxes unchecked) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (pinned; used for every focused command below) |
| untouched | frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, every existing evidence root |

## 3. Frozen inputs, orders identity and support rule

- Counts path:
  `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
- Stat-only pre-check (before any content open): the file exists and
  `st_size == 25166822`. Metadata-only verification performed at freeze:
  observed size `25166822` bytes (no content open).
- Orders path:
  `.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json`
- Orders identity (all BEFORE the NPZ content open; any failure is a
  fail-closed refusal consuming nothing): recorded `orders_sha256` equals
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`;
  recomputed canonical digest of the `layers` payload equals the recorded
  digest; both pooled empirical orders are valid 256-permutations; both
  BEC orders equal the recomputed H1/H2-surrogate `analytic_order` orders.
- Loader (single call, one artifact content read + one scientific attempt
  consumed at the first NPZ content open; no reopen, no retry):
  `comparison_bench.src.comparison_bench.formal_ir.v35_algorithm_development.load_v25_channel_counts`.
  Source selected: `1M`, `[Alice,Bob]` shape `[1024,1024]`.
- Support rule (the only one, exactly P7/P8): column-normalize the raw
  counts, replace every cell below `1e-15` by `1e-15`, renormalize each Bob
  column; `p_b` from the column totals over the total count; `P1`/`P2`
  from the accepted `derive_p1`/`derive_p2` of the floored table under
  `A = 32*U1 + U2`. No lambda, backoff, tuning, floor scan or held-out
  fitting.
- Preconditions (after the content open but before any SC call; failure
  raises `BLOCKED(target_population_contract)` with zero SC calls and no
  output root):
  1. no zero Bob column;
  2. `p_b` normalization and conditional-table column error `<= 1e-12`;
  3. raw-MLE in-sample population `H1` within `1e-12` of `0.02428054681872374`;
  4. `H2` within `1e-12` of `0.7767572780789994`;
  5. total within `1e-12` of `0.8010378248977232`;
  6. floor-induced total-entropy change relative to the raw MLE table `<= 1e-9`.

### 3.1 Refusal ordering (explicit Pre-EXECUTE review item)

Refusals fire in this order: (1) missing `--gate-id`; (2) existing
`--out-dir`; (3) frozen scalar/grid/seed-list validation (exact
`n`/`source`/`floor`/grids per gate, distinct and disjoint seed lists,
P9 prior-stream disjointness); (4) P7 orders identity/permutation/
surrogate refusal; (5) NPZ stat check; (6) single content open (read 1/1
+ attempt 1/1 consumed); (7) precondition refusal with no output root
and zero SC calls. Preconditions necessarily follow the content open
(they are functionals of the counts); "before the NPZ content open" in
the packet brief covers the absent-root, gate-id and orders-identity
refusals, while the packet proper requires preconditions only before SC.
The reviewer must confirm this reading.

## 4. Frozen SCREEN, selection and CONFIRM

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural order;
  `q=32`, `N=256`.
- Gate id: `--gate-id p9-lower-rate-boundary` (required closed-choice;
  first flag in the frozen command). It selects only the P9 protocol
  name `nbpolar-p9-lower-rate-boundary-screen-confirm`, the P9 tag-domain
  prefix `nbpolar-p9-lower-rate-boundary-seed` (differs from the P8 prefix
  `nbpolar-p8-target-rate-seed`), the P9 frame prefix
  `nbpolar-p9-lower-rate-boundary` and the P9 labels below. The P8 path
  (`p8-target-rate-screen-confirm`) preserves the P8 protocol/prefix/
  labels byte-for-byte; silent reuse of P8 identifiers in the P9 path is
  forbidden and refused by grid/prefix/protocol checks.
- SCREEN streams `2026091710, 2026091711, 2026091712`, 64 common blocks
  each = 192 shared blocks. Static grid `K1=[0,2,4,6,8,12,24,45]` by
  `K2=[0,20,40,50,60,70,80]` = exactly 56 configurations, including the
  global zero-disclosure corner `(0,0)` and the accepted P8 anchor
  `(8,80)`.
- Sampling: `B ~ p_b`, then `A ~ P_floor(A|B)` once per shared block
  (`high = A//32`, `low = A%32`); one explicit
  `np.random.default_rng(stream_seed)` per stream, no global RNG; every
  grid point uses the identical block object.
- Per configuration (empirical arm only): L1 SC on the P1 metric
  (`PRIOR_ONLY`) with the pooled empirical L1 order first `K1`; then L2
  SC on the candidate-conditioned P2 metric (`CANDIDATE_CONDITIONED`)
  with the pooled empirical L2 order first `K2`; each arm restarts SC by
  layer, rebuilds `label_hat = low_hat + 32*high_hat` and invokes one
  64-bit Toeplitz tag over the MSB-first 10-bit expansion with the P9
  phase/arm/block-domain seed (master `stream_seed + 10000`, 2623 public
  seed bits per tag).
- Zero-K by construction: `K1=0` and/or `K2=0` disclose nothing for that
  layer; `(0,0)` is the tag-only 64-bit arm (`5*(0+0)+64 = 64`
  key-dependent bits). No interpolation or unregistered point.
- Eligibility per point: 192/192 blocks accounted; undetected, nonfinite
  and resource_abort zero; one-sided 95% Wilson exact-recovery lower
  bound (`z = 1.6448536269514722`) `>= 0.95`. At this frozen shape this
  holds exactly for exact `>= 188/192`; both the bound and the count
  check are recorded with their agreement flag (equivalence verified over
  the full `0..192` range at freeze: `187 -> 0.94747… < 0.95`,
  `188 -> 0.95440… >= 0.95`; focused tests re-verify the full range).
- Selection: exactly one point, the lexicographic minimum of
  `(K1+K2, K1, K2)` over eligible points only. No DEV/CONFIRM outcome and
  no runtime enters the tiebreak. No eligible point stops without
  CONFIRM as `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` (valid
  negative, not BLOCKED).
- CONFIRM streams `2026091720..2026091724`, 128 common blocks each = 640,
  asserted disjoint from SCREEN and all prior official streams
  (`2026091650..1652`, `2026091660..1664`, `2026091680..1682`,
  `2026091690..1694`); the runner refuses any overlap. Only the selected
  empirical-order point plus a paired BEC-order control at the same
  selected K1/K2; BEC orders are the accepted P7 H1/H2 surrogates,
  report-only. No SCREEN block, outcome or tag seed enters CONFIRM.
- Confirm gates: empirical exact `>= 618/640`; Wilson lower bound
  `>= 0.95`; undetected, nonfinite and resource_abort zero. BEC exact and
  paired cells report-only; empirical need not beat BEC.
- Toeplitz master is `stream + 10000`, domain-separated by P9
  phase/arm/block.

## 5. Frozen accounting

- Fully invoked point: `5*(K1+K2)+64` key-dependent bits (L1 `5*K1` even
  when the L1 SC call fails, L2 `5*K2` only when invoked, tag `64` only
  when invoked); `2623` public control bits per invoked tag. Decode
  failure before tag counts only actually disclosed coordinate bits.
  Partial-call accounting preserved, including zero-K arms.
- Buckets `exact`/`verify_failed`/`decode_failed`/`undetected`/
  `resource_abort` are mutually exclusive; `undetected` is never merged
  into exact.
- Independent literal transcript recount of L1 disclosure, L2 disclosure
  and verification-tag events (phase and arm read literally from the
  event id) must equal the incremental totals per phase, per arm and in
  total with zero mismatch.
- Attempt/read accounting: `artifact_reads_allowed=1`,
  `attempts_allowed=1`, both consumed before this run `0`, consumed by
  this run `1`, `retries=0`, no reopen, no retry after open; the
  consumption point is the first NPZ content open.
- Budget: 2 GiB RSS peak and 3600 s total wall (`timeout 3600`,
  `ulimit -v 2097152`); a budget breach fills every remaining planned arm
  with `resource_abort`, skips CONFIRM, still writes the five files and
  returns `BLOCKED` (P7/P8 precedent).

## 6. Frozen gates and labels

Integrity gates (persisted booleans, frozen order):
`orders_identity_and_permutations`, `target_population_contract`,
`coverage_complete_and_disjoint`, `pairing_and_buckets`,
`truth_leak_zero` (global), `undetected_zero`, `nonfinite_zero`,
`resource_abort_zero` (the three zero gates cover the decision path:
eligible SCREEN points plus CONFIRM; rejected SCREEN configurations are
report-only), `disclosure_and_recount_exact`,
`attempt_read_accounting_exact`, `resource_limits_met`.

Scientific gates (frozen order): confirm empirical exact `>= 618/640`;
confirm empirical one-sided 95% Wilson lower bound `>= 0.95`.

Labels: no eligible SCREEN point (integrity pass) ->
`TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT`; point selected and every
CONFIRM/integrity gate true at the frozen shape ->
`TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE`; integrity true and any
CONFIRM gate false ->
`TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED`; integrity false ->
`BLOCKED` with the failing gate names in frozen order (operator maps to
`BLOCKED(<earliest gate>)`). Precondition failure ->
`BLOCKED(target_population_contract)` with no output root and zero SC
calls.

## 7. Frozen command (verbatim; the only authorized execution)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_rate --gate-id p9-lower-rate-boundary --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --orders .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json --n 256 --floor 1e-15 --screen-seeds 2026091710 2026091711 2026091712 --screen-blocks 64 --k1-grid 0 2 4 6 8 12 24 45 --k2-grid 0 20 40 50 60 70 80 --confirm-seeds 2026091720 2026091721 2026091722 2026091723 2026091724 --confirm-blocks 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm
```

Thirteen flags: `--gate-id` first, then `--counts`, `--source`,
`--orders`, `--n`, `--floor`, `--screen-seeds`, `--screen-blocks`,
`--k1-grid`, `--k2-grid`, `--confirm-seeds`, `--confirm-blocks`,
`--out-dir`. No rerun, seed/grid/order/floor/threshold change or partial
replacement after the content open. Stop and preserve the failure root
on precondition/entropy/orders mismatch, target presence, command/test
error, resource breach, truth leak or any integrity failure; do not fix
and rerun.

## 8. Frozen output root and five-file schema

Root:
`.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/`
(absent at freeze; must be absent before execution), containing exactly:

| file | contents |
|---|---|
| `frozen_plan.json` | gate id, protocol, point/constants, orders identity, support rule, entropy literals, streams/masters/grids, selection rule, accounting, gate orders, labels, budgets, frozen command, claim scope |
| `screen_records.json` | 56 configs: k1/k2, exact/192, Wilson bound + 188-count check + agreement, eligibility, outcome counts, scalar per-block empirical records |
| `selection_and_confirmation_records.json` | eligible points, selection rule, selected k1/k2 (or null), CONFIRM per-stream (5x128) and pooled outcomes, paired cells, Wilson values, scalar per-block paired records |
| `transcript_accounting.json` | incremental vs literal recount per phase/arm/total, mismatch count |
| `report.md` | human-readable rendering incl. all 56 SCREEN rows, selection, CONFIRM streams, leakage, planning-only f, wall/RSS |

Scalar/aggregate only: source/Bob/U/decoded/disclosed vectors, metric
arrays, labels, tags and raw seed material are never persisted.

## 9. Forbidden-path proof (what the frozen run may touch)

- Reads: the P7 `construction_orders.json` (identity/permutation checks
  only) plus exactly one content open of the registered
  `channel_counts.npz` through the accepted loader (plus its stat
  metadata). No read of the Model-F artifact (`model_f_input.npz`),
  `pairs.parquet`, TTBin, held-out/eval files, raw data or any other
  evidence root. The V25 NPZ was **not opened** in this wave (stat size
  `25166822` only).
- Writes: exactly the five files under the frozen root after the run
  completes. No write to `results/`,
  `comparison_bench/outputs_comparison/`, old evidence roots, sibling
  checkouts, OpenSpec or packet files during execution.
- Import safety: the focused suite includes an empty-cwd import
  subprocess that asserts no file creation, and the module contains no
  import-time I/O, no global RNG, and no `open(` call.
- Seed freshness: P9 SCREEN `2026091710..1712` and CONFIRM
  `2026091720..1724` appear only in P9 docs/code/tests (repo grep at
  freeze confirms zero hits elsewhere) and are disjoint from all prior
  official streams (`1650..52`, `1660..64`, `1680..82`, `1690..94`).
  Focused tests use fresh seeds `>= 2026091730` and never sample the
  frozen streams.
