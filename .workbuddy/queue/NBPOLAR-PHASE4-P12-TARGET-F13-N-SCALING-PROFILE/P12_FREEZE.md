# P12 freeze — target-population f=1.3 N-scaling profile (Wave-A implementation freeze)

Packet: `NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE` (Tier-Y).
Predecessor `EXACT_CHUNKED_SC_ACCEPTED` verified in the P11 STATUS.yaml.
This document freezes the implementation, tests, command, allocation,
output schema, target absence, budgets and attempt point for the Wave-C
gate execution. It authorizes nothing; an independent reviewer-go
Pre-EXECUTE PASS is required before the single NPZ content open. The gate
has NOT been run in this wave (artifact reads used: 0, attempts used: 0).

## 1. Mission and frozen execution matrix (P12-01/P12-03)

Measure whether target-model recovery improves with N when every point is
held to the actual leakage budget `f<=1.3`, using N-specific
BEC-surrogate construction and the accepted operational two-layer
hard-L1 SC. Development profile only: not qualification and not an
empirical-order scaling claim.

| N | stream seed | blocks | master (seed+10000) |
|---:|---:|---:|---:|
| 256 | 2026091820 | 64 | 2026091830+... (see note) |
| 4096 | 2026091821 | 32 | seed+10000 |
| 16384 | 2026091822 | 16 | seed+10000 |
| 65536 | 2026091823 | 8 | seed+10000 |
| 131072 | 2026091824 | 4 | seed+10000 |
| 262144 | 2026091825 | 4 | seed+10000 |

Exactly 128 blocks. Master = stream seed + 10000 per row
(2026091830..2026091835); the tag seed is domain-separated by
P12/N/layer/block with the literal layer token `verify` (exactly one
verification tag is invoked per block, so the layer dimension is the
constant verification-tag layer). Per block: `B ~ p_b` then
`A ~ P_floor(A|B)` sampled once; L1; candidate-conditioned L2; label
rebuild `low_hat + 32*high_hat`; exactly one 64-bit Toeplitz tag. No
comparator, oracle, adaptive retry or repeated block. Every SC call runs
through the accepted `sc_decode` with `_minus_block(chunk_rows=512)`
(the P11 default; verified by contract check, never changed).

## 2. Frozen f budget, construction and allocation (P12-02)

- Budget: `K_total = floor((1.3*N*(H1+H2)-64)/5)` with
  `H1 = 0.02428054681872374`, `H2 = 0.7767572780789994`
  (`H1+H2 = 0.8010378248977231` in float64; the `EXPECTED_TOTAL` literal
  `0.8010378248977232` differs by one ulp and every frozen floor is far
  from an integer boundary under either value, verified §8), clipped to
  `[0, 2N]`, entire budget used:
  `leakage = 5*K_total + 64 <= 1.3*N*H` (asserted at allocation time,
  fail-closed).
- Construction: N-specific analytic BEC reliabilities, float64
  `z- = 2z-z^2`, `z+ = z^2` from `epsilon_l = H_l/5` (accepted
  `analytic_erasure_probs`), stable descending orders with coordinate
  index tie-break (accepted `analytic_order`). Every feasible integer
  `K1` in `[max(0,K_total-N), min(N,K_total)]` with `K2 = K_total-K1`
  enumerated; lexicographic minimum of (sum of undisclosed L1+L2
  reliabilities, K1, K2). All K/order/residual values frozen before the
  first SC call. Analytic BEC orders only: the P7 N=256 empirical order
  is never reused or extrapolated.

Frozen six-N allocations, computed from the formulas and the H literals
alone (no NPZ opened; reproduced by
`test_frozen_six_allocations_pinned`):

| N | K_total | K1 | K2 | residual | leakage | f | f_no_tag |
|---:|---:|---:|---:|---|---|---|---|
| 256 | 40 | 1 | 39 | 6.151580025714424 | 264 | 1.2873923901554465 | 0.9752972652692777 |
| 4096 | 840 | 37 | 803 | 3.363831923437399 | 4264 | 1.2995836059713126 | 1.280077660665927 |
| 16384 | 3399 | 166 | 3233 | 1.2717801865443192 | 17059 | 1.29981219126786 | 1.2949357049415136 |
| 65536 | 13636 | 678 | 12958 | 0.12735089416941037 | 68244 | 1.2999645814655583 | 1.2987454598839718 |
| 131072 | 27285 | 1381 | 25904 | 0.017614350746612217 | 136489 | 1.2999741058529144 | 1.2993645450621212 |
| 262144 | 54583 | 2776 | 51807 | 0.0010478214685463172 | 272979 | 1.2999788680465925 | 1.2996740876511959 |

Arithmetic check (N=256): `1.3*256*0.8010378248977231 = 266.585...`;
`(266.585...-64)/5 = 40.517...`; floor 40; leakage `5*40+64 = 264`;
`264/(256*0.8010378248977231) = 1.28739... <= 1.3`. All six rows satisfy
`f <= 1.3`; all residuals are the minimized undisclosed-reliability sums.

## 3. Exact verbatim frozen command (P12-06)

Byte-equivalence with this file is a Pre-EXECUTE check:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 256 4096 16384 65536 131072 262144 --stream-seeds 2026091820 2026091821 2026091822 2026091823 2026091824 2026091825 --blocks 64 32 16 8 4 4 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling
```

Every flag is required; there is no production default. Pinned
interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(Python 3.12.3, NumPy 2.5.3 at freeze time; Pre-EXECUTE reconfirms).

## 4. Absent root and five-file schema (P12-04)

Root
`.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling/`
is ABSENT at freeze time (verified §8) and must remain absent until the
authorized execution. Exactly five compact scalar-only files:
`frozen_plan.json`, `allocation_and_orders.json`,
`per_block_outcomes.json`, `aggregate_summary.json`, `report.md`.
Public orders plus scalar outcomes only: never sampled symbols, decoded
keys, metrics, raw counts or raw tag seeds. Per N the report covers
K/residual/leakage/f and tag-free f; full bucket counts
(exact/verify_failed/decode_failed/undetected/resource_abort);
exact fraction with the two-sided 95% Clopper-Pearson interval;
wall/RSS; key/public/tag accounting with the independent literal
recount.

## 5. Gates, labels, no-threshold statement (P12-05)

Hard gates are integrity/completion only, in frozen order:
`target_population_contract`, `six_n_rows_and_128_blocks`,
`budget_allocation_orders_reproduced` (K_total/K1/K2/orders recomputed
from the literals, residual within 1e-9 float-noise bound, `f<=1.3`,
leakage inequality), `coverage_complete`,
`buckets_disjoint_exhaustive` (mutually exclusive exhaustive buckets,
undetected never success, per-record structural proof),
`truth_leak_zero`, `disclosure_and_recount_exact`,
`attempt_read_accounting_exact`, `resource_limits_met_and_no_abort`.
All true returns `TARGET_F13_N_SCALING_PROFILE_CANDIDATE`; otherwise the
earliest `BLOCKED(<gate>)`.

There is deliberately NO recovery threshold: large-N samples are too
small for qualification. Recovery trend and first observed success are
report-only and can never flip a gate.

## 6. Consumption point, refusal ordering, no-rerun rule

Artifact reads allowed 1, used 0 at freeze time; attempts allowed 1,
used 0. Read 1/1 and attempt 1/1 are consumed together at the first NPZ
content open (`load_v25_channel_counts`); a module-level reopen guard
refuses any second NPZ-mode call in-process. Refusal ordering: CLI-parse
failures, absent-root refusal (`FileExistsError`), frozen-scalar
mismatches (source/floor/target-f), the chunk-512 contract check, the
missing-file refusal and the stat-size mismatch ALL happen BEFORE the
content open and consume nothing. Precondition failures happen AFTER the
open: they raise `BLOCKED(target_population_contract)` with zero SC
calls and no output root, with consumption spent; the BLOCKED label is
recorded only in the refusal message (no file can record it). After
content open: no repair, rerun, tuning, frozen-value change, or partial
replacement; STOP and preserve evidence on any blocker or integrity
failure.

Exit codes: `0` if and only if the run completed and persisted one of
the frozen labels (`TARGET_F13_N_SCALING_PROFILE_CANDIDATE` or
`BLOCKED(<earliest gate>)`) with the five files; `2` on any
pre-completion refusal (parse/absent-root/contract/resource/shape).

## 7. Budgets and forbidden paths

`ulimit -v 2097152`; external `timeout 1800`; internal wall cap 1800 s;
RSS cap 2 GiB. Any breach fills the remaining blocks with
`resource_abort` records, which fail
`resource_limits_met_and_no_abort` by construction.

Forbidden: Model-F/raw/held-out/real/EVAL/tag/protocol paths; official
prior seeds (1650..52, 1660..64, 1680..82, 1690..94, 1710..12, 1720..24,
1800, probe seeds); N values other than the six frozen; empirical
large-N learning; adaptive work; FWHT/APP/SCL; FER/efficiency/key-rate
qualification or promotion; old-root modification; `results/`;
`comparison_bench/outputs_comparison/`; commit/push.

## 8. Freeze-time verification (2026-09-14, Wave-A)

- Gate root absent: `target_f13_n_scaling/` does not exist
  (`test ! -e ...` → `ROOT_ABSENT_OK`).
- NPZ stat metadata only, never opened: `stat` reports exactly
  `25166822` bytes for the frozen counts path. No process in this wave
  opened the NPZ content (reads used: 0; the loader cache was never
  populated: every test passes injected arrays or refuses before load).
- Frozen streams 2026091820..2026091825 fresh: repo-wide grep finds them
  only in the P12 packet docs (`TASK_PACKET.md`,
  `AUTHORIZATION_PROMPT.md`), the new P12 runner source, the new P12
  focused tests (docstring scope note only, never executed), and the P12
  OpenSpec delta; disjoint from every official prior seed and probe seed.
- Float-sum vs literal-total: `H1+H2 = 0.8010378248977231` vs literal
  `...232` differ by one ulp; all six floors are ≥0.27 from an integer
  boundary under either value, so `K_total` is identical.
- Allocation stability: the K1/K2 argmin is unchanged under relative
  entropy perturbations up to 1e-6 (≫ the 1e-12 precondition tolerance)
  at all six N; the best-vs-second-best residual gap is ≥7.8e-09 while
  the worst measured-vs-literal residual drift is 1.5e-10, inside the
  1e-9 reproduction tolerance.
- Pinned allocation table (§2) is asserted by
  `test_frozen_six_allocations_pinned`.
- Tests: focused file 23/23 green; complete accepted 262-test NB-Polar
  predecessor suite green; combined 285/285 with the pinned interpreter
  and fresh basetemps.
- HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged by this wave
  (same ID recorded in the P11 freeze); no commit was made. The worktree
  carries pre-existing unrelated modifications that this wave did not
  touch; the wave's complete diff is: new `target_n_scaling.py`, new
  `test_nbpolar_target_n_scaling.py`, new
  `specs/nbpolar-phase4-p12/spec.md`, P12 section appended to `tasks.md`,
  this freeze directory, and the `STATUS.yaml` accounting update.
