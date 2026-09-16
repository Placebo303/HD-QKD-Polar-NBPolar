# Operator return — NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION (CANDIDATE, pending main-thread acceptance)

Status: `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE_PENDING_MAIN_THREAD_ACCEPTANCE`.
This is a **candidate, not an acceptance**. The single authorized Tier-Y gate
executed exactly once (exit 0); independent Pre-EXECUTE and Pre-RESULT reviews
both PASS; the persisted label is `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`. No
rerun, retuning or seed/order/K/floor/threshold change occurred. The operator
reports evidence only; the main thread owns acceptance and scientific scope.

## 1. Mission

Implement and execute one target-population, model-sampled NB-Polar Tier-Y
development gate for the frozen V25 1M TRAIN count distribution at `N=256`,
testing whether pooled empirical genie construction orders support reliable
two-layer hard-candidate SC at a conservative fixed disclosure point
(`K1=45`, `K2=140`), with BEC analytic orders report-only.

## 2. Target population (X07 finding)

X07 (`NBPOLAR-X07-ENTROPY-CONTRACT-RECONCILIATION`, main-thread disposition)
established `POPULATION_SESSION_IDENTITY_1M`: the V49/X06 entropy literals and
the Model-F CAL artifact describe different sessions/populations. The accepted
target for P7 is therefore the V25 1M TRAIN population — the ~0.801-bit
near-neighbor channel — and the Model-F CAL artifact is rejected as the target
construction law for this purpose.

- Input: source `1M` from
  `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
  (25,166,822 B; `[Alice,Bob]` shape `[1024,1024]`), loaded once through the
  accepted `load_v25_channel_counts`.
- Model-F, raw/held-out/real frames, EVAL, parquet and TTBin were never read.

## 3. Support rule

Column-normalize the raw counts; replace every cell below `1e-15` by `1e-15`;
renormalize each Bob column; `p_b` from the column totals over the total count;
`P1`/`P2` from the accepted `derive_p1`/`derive_p2` under `A = 32*U1 + U2`. No
lambda, backoff, tuning, floor scan or held-out fitting.

## 4. Preconditions (all true; ratified entropy semantics)

Checked before any genie/SC call; failure would have raised
`BLOCKED(target_population_contract)` with no output root.

- no zero Bob column; `p_b` normalization and conditional-column error
  `1.1357581541915351e-13 <= 1e-12`;
- `H1 = 0.024280546818678802` vs literal `0.02428054681872374` (diff
  `-4.49e-14`), `H2 = 0.7767572780789994` vs literal `0.7767572780789994`
  (diff `0.0`), `total = 0.8010378248976782` vs literal `0.8010378248977232`
  (diff `-4.51e-14`), all within `1e-12`;
- floor guard: floor-induced total-entropy change `5.1600945738528026e-11 <=
  1e-9`.

These literals are the V49 1M/TRAIN `nll_*` columns, equal to the **raw-MLE
in-sample population conditional entropies** of the accepted V26/V49 chain
(`H1 = sum_b p_b H(P1_raw)`, `H2 = sum_b p_b sum_u1 P1_raw(u1|b) H(P2_raw)`).
The floored-table entropies are computed only for the `<=1e-9` guard and are
never gated against the literals. Independent Pre-EXECUTE review item #1
adjudicated this reading as the unique one jointly consistent with the packet's
two-tier thresholds and **ratified** it (see §8).

## 5. Construction, orders and stability

- GF32 polynomial 37, alpha 2, natural order, `N=256`; `q=32`, `K1=45`,
  `K2=140`, floor `1e-15`.
- TRAIN streams `2026091650..2026091652` × 256 blocks; DEV streams
  `2026091660..2026091664` × 128 common blocks = 640 paired blocks; disjoint,
  no EVAL. Per-DEV-stream public Toeplitz masters `stream+10000 = 2026101660..64`,
  domain-separated by arm/block.
- Per-layer (L1 and oracle-L2) per-stream and pooled worst-first orders via the
  accepted `genie_conditionals`; all 10/10 orders are permutations of `0..255`;
  orders frozen before the first DEV call; `orders_sha256`
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`.
- Minimum pairwise TRAIN-order Spearman: L1 `0.9973291943236439`, L2
  `0.9950453479056992` (both `>= 0.95`). BEC controls from `epsilon_l = H_l/5`
  (`0.00485610936373576` / `0.15535145561579988`), report-only.
- Sampling: `B ~ p_b`, then `A ~ P_floor(A|B)`; `high = A//32`, `low = A%32`;
  explicit per-stream `np.random.default_rng(seed)`, no global RNG.

## 6. DEV results (from the five persisted artifacts)

Both arms on the same sampled block, per-layer SC restart, candidate-conditioned
L2, `label_hat = low_hat + 32*high_hat`, one 64-bit Toeplitz tag per viable
candidate. `undetected` is never merged into success.

- Outcomes (both arms): `exact 640, undetected 0, verify_failed 0,
  decode_failed 0, resource_abort 0`; summed per-stream 128/128 each.
- Empirical exact **640/640**; BEC control exact **640/640** (report-only).
- Paired cells: `both_exact 640`, `empirical_only 0`, `bec_only 0`,
  `neither 0`.
- One-sided 95% Wilson exact-recovery lower bound `0.9957903841321254 >= 0.95`
  (`z = 1.6448536269514722`).
- Truth-leak / undetected / nonfinite / resource_abort all zero;
  `resource_stop_fired=false`.
- Disclosure: `5*(45+140)+64 = 989` key-dependent bits per fully invoked arm
  (L1 225 + L2 700 + tag 64); totals `1,265,920` key-dependent /
  `3,357,440` public / `1280` tags; independent literal transcript recount
  equals the incremental totals; recount mismatch count `0`.
- Resources: module wall `132.523651 s <= 3600 s`; peak RSS `383,832,064 B <=
  2,147,483,648 B`; no rerun.
- Planning-only `f = 4.8228449767568495` (leakage 989 / nH 205.0656831738056);
  not real-channel efficiency and no gate depends on it.
- All 11 integrity gates and 3 scientific gates true ->
  `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`.

## 7. Consumption accounting

- Artifact content reads: allowed 1, consumed before 0, **consumed by this run
  1**; `open_count 1`, `reopen_attempted false`, `retries 0`.
- Scientific attempts: allowed 1, consumed before 0, **consumed by this run 1**.
- Both were consumed at the **first NPZ content open**
  (`load_v25_channel_counts`); the recorded/observed size is `25,166,822 B`;
  the file was not reopened and no rerun or partial replacement occurred.
- Seeds `2026091650..52` (TRAIN), `2026091660..64` (DEV) and masters
  `2026101660..64` are spent (masters public control).

## 8. Reviewer verdicts and ratified semantics

- Independent Pre-EXECUTE (`PRE_EXECUTE_REVIEW.md`): **PASS**. Eight required
  checks pass; review item #1 adjudicated and **ratified**: preconditions 3–5
  compare the raw-MLE in-sample population conditional entropies against the
  literals at `1e-12`, precondition 6 compares `|floor_total - total| <= 1e-9`
  on the A-level floored/renormalized table, and the floored-table entropies are
  reported but never gated against the literals. Five non-blocking observations
  recorded; no blocking issues.
- Independent Pre-RESULT (`PRE_RESULT_REVIEW.md`): **PASS**. Every persisted
  value recomputed and reproduced; all 11 integrity and 3 scientific gates
  recomputed true; `orders_sha256`, Spearman, Wilson bound, cells, buckets and
  disclosure recount match; wording bounded. Non-blocking notes: STATUS pending
  (fixed in this closeout); frozen-before-DEV and attempt/read accounting are
  self-reported; raw-table precondition quantities are not independently
  recomputable without a second NPZ open (verified via recorded values, code and
  the Pre-EXECUTE estimate); both arms saturate at 640/640 so this gate carries
  no empirical-vs-BEC discrimination (interpretation only).
- Reviewer verdicts permit operator return but do not grant main-thread
  acceptance.

## 9. Five-file inventory (output root)

`.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`

| file | size (bytes) |
|---|---|
| `frozen_plan.json` | 6,301 |
| `construction_orders.json` | 43,137 |
| `per_block_paired_outcomes.json` | 925,631 |
| `aggregate_summary.json` | 11,389 |
| `report.md` | 2,554 |

Exactly these five files; single generation (all mtimes within a 25 ms window);
scalar/aggregate only — no symbols, labels, disclosed values, decoded keys or
raw seed bits persisted.

## 10. Bounded scope

Synthetic `N=256` V25-1M-TRAIN model-sampled **development signal only**. This
is **not** held-out or real frame FER, reconciliation efficiency, leakage,
key-rate, scaling, qualification or promotion evidence. `undetected` is never
success. `planning-only f` is not real-channel efficiency. No Model-F/raw/
held-out/EVAL artifact, no `N>256`, no APP/SCL/FWHT, no production benchmark, no
old-root modification, no commit or push.

## 11. Remaining stages

Unrun stages: **none** beyond main-thread acceptance. The main thread owns
adjudication of the `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` label; no further
scientific execution is requested or permitted in this packet.

No commit. No push.
