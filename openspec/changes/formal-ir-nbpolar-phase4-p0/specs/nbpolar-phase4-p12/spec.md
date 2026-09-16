# NB-Polar Phase 4-P12 specification delta

Phase 4-P12 is the target-population `f=1.3` N-scaling profile on the V25
1M TRAIN count matrix (not the Model-F CAL artifact rejected for this
purpose by X07). One Tier-Y development gate measures whether
target-model recovery improves with N when every point is held to the
actual leakage budget `f<=1.3`, using N-specific BEC-surrogate
construction and the accepted operational two-layer hard-L1 SC. This is a
development profile, not qualification or an empirical-order scaling
claim. The claim scope is narrow: a development signal for the frozen V25
TRAIN target population only; it is not held-out or real frame FER,
efficiency, key rate, scaling superiority, qualification or promotion.
Implementation tasks live in the companion P12 section of `tasks.md`;
status, acceptance and route disposition are owned by the main thread,
never by the implementing session. This document authorizes no production
behavior.

## Requirement: frozen target input, support rule and preconditions

The gate SHALL open exactly source `1M` through the accepted
`load_v25_channel_counts(path)` from
`/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`,
after a stat-only size check of exactly `25,166,822` bytes and an
absent-output root check; one artifact content read and one scientific
attempt SHALL be consumed at the first NPZ content open, with no reopen
and no Model-F, held-out, raw-parquet or TTBin read. The only support
rule SHALL be the exact P7 rule: column-normalize the raw counts, replace
every cell below `1e-15` by `1e-15`, renormalize each Bob column; `p_b`
SHALL be the column totals over the total count, and `P1`/`P2` SHALL be
the accepted `derive_p1`/`derive_p2` tables under the packing
`A = 32*U1 + U2`. No lambda, global backoff, tuning, floor scan or
held-out fitting is permitted. Before any SC call the gate SHALL recheck
the exact P7 entropy/support preconditions: no zero Bob column; `p_b`
normalization and conditional-table column error `<= 1e-12`; raw-MLE
in-sample population `H1` within `1e-12` of `0.02428054681872374`, `H2`
within `1e-12` of `0.7767572780789994`, total within `1e-12` of
`0.8010378248977232` (ratified P7 semantics); and the floor-induced total
entropy change relative to the raw MLE table `<= 1e-9`. Any failure SHALL
be `BLOCKED(target_population_contract)` with zero SC calls and no output
root created (consumption already spent: the refusal happens after the
content open, so it is recorded in the refusal message and freeze doc,
never in an output file).

## Requirement: frozen f budget, N-specific construction and allocation

For each N the gate SHALL set
`K_total = floor((1.3*N*(H1+H2)-64)/5)`, clipped to `[0, 2N]`, and SHALL
use the entire budget, so `leakage = 5*K_total + 64 <= 1.3*N*H` (asserted
at allocation time). For each layer the gate SHALL compute N-specific
analytic BEC reliabilities in float64 (`z- = 2z-z^2`, `z+ = z^2` from
`epsilon_l = H_l/5` via the accepted `analytic_erasure_probs`) with the
stable descending order and coordinate index tie-break of the accepted
`analytic_order`. The gate SHALL enumerate every feasible integer `K1`
(`K2 = K_total - K1`) and lexicographically minimize (sum of undisclosed
L1+L2 reliabilities, K1, K2). All K/order/residual values SHALL be frozen
before the first SC call. These are analytic BEC orders; the P7 N=256
empirical order SHALL NOT be reused or extrapolated.

## Requirement: frozen six-N execution matrix with single operational arm

The gate SHALL use GF32 (primitive polynomial 37, alpha 2, natural
order), the accepted chunked SC with `chunk_rows=512` for every SC call,
and exactly the N/seed/blocks matrix
256/2026091820/64, 4096/2026091821/32, 16384/2026091822/16,
65536/2026091823/8, 131072/2026091824/4, 262144/2026091825/4 (exactly 128
blocks). Master SHALL be `seed + 10000`, domain-separated by
P12/N/layer/block. Per block the gate SHALL sample `B ~ p_b` then
`A ~ P_floor(A|B)` once, run L1, build candidate-conditioned L2 metrics
from the hard L1 candidate only, run L2, rebuild the full label
`low_hat + 32*high_hat` and invoke exactly one domain-separated 64-bit
Toeplitz tag. No comparator, oracle, adaptive retry or repeated block is
permitted. Outcome buckets SHALL be the accepted two-layer taxonomy
(`exact`, `verify_failed`, `decode_failed`, `undetected`,
`resource_abort`), mutually exclusive and exhaustive, with `undetected`
never merged into success. Alice truth SHALL enter only sampling,
disclosed values, tag construction and scoring.

## Requirement: frozen accounting, intervals and transcript recount

A fully invoked block SHALL disclose exactly `5*(K1+K2)+64`
key-dependent bits (L1 `5*K1` even when the L1 SC call fails, L2 `5*K2`
only when invoked, one `64`-bit tag only when invoked) and
`seed_bits_for(N)` public control bits per invoked tag; decode failure
before tag counts only actually disclosed coordinate bits. The gate SHALL
persist an independent literal transcript recount of the disclosure and
tag events and SHALL require zero mismatch against the incremental
totals. Per N the gate SHALL report K/residual/leakage/f and tag-free f,
full bucket counts, the exact fraction and the two-sided 95%
Clopper-Pearson interval, wall/RSS, and key/public/tag accounting with
the literal recount. Attempt/read accounting SHALL be exact (1 allowed/1
consumed at the NPZ content open in the frozen run; no retry, no reopen)
and the run SHALL stay within 2 GiB RSS and 1800 s wall.

## Requirement: integrity-only gates, report-only recovery, outcome labels

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be: target input/support/entropy preconditions;
exactly the six registered N rows with 128 attempted blocks; exact
reproduction of budget/allocation/orders with `f<=1.3`; coverage
complete; mutually exclusive and exhaustive buckets with per-record
structural consistency; truth-leak zero globally; disclosure exact with
zero recount mismatch; attempt/read accounting exact; and resource limits
met with zero resource abort. There SHALL be no recovery threshold
because large-N samples are too small for qualification; recovery trend
and first observed success SHALL be report-only. The gate SHALL return
`TARGET_F13_N_SCALING_PROFILE_CANDIDATE` iff every integrity gate passes
and otherwise `BLOCKED` with the failing gate names in frozen order (the
operator maps this to `BLOCKED(<earliest gate>)`).

## Requirement: frozen CLI, five-file output and bounded scope

The CLI SHALL require every flag — `--counts`, `--source`, `--floor`,
`--target-f`, `--n-values`, `--stream-seeds`, `--blocks`, `--chunk-rows`
and `--out-dir` — with no production default; it SHALL refuse an
existing output root, a chunk-rows value other than 512 (with the
`_minus_block` default-512 contract check), and a CLI parse failure
before the NPZ content open. The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling/`
SHALL be absent before execution and SHALL contain exactly five compact
scalar-only files (`frozen_plan.json`, `allocation_and_orders.json`,
`per_block_outcomes.json`, `aggregate_summary.json`, `report.md`);
public orders and scalar outcomes only — sampled symbols, decoded keys,
metrics, raw counts and raw tag seeds SHALL NOT be persisted. The report
SHALL cover per-N K/residual/leakage/f and tag-free f, full bucket
counts, exact fractions with two-sided 95% Clopper-Pearson intervals,
wall/RSS, key/public/tag accounting with the literal recount, and the
report-only recovery trend. No rerun, seed/N/K/floor/order/threshold
change or partial replacement is permitted after content open.
Forbidden: Model-F artifact, raw/held-out/real frames, EVAL, other N in
the frozen run, empirical large-N learning, adaptive work, APP/SCL/FWHT,
production benchmark, FER/efficiency/key-rate/qualification/promotion
claim, old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered candidate label and
the blocker return; a candidate means that at the frozen V25 TRAIN
population point the six-N/128-block profile completed with every budget,
allocation, order, bucket, truth, accounting and resource gate true. It
SHALL NOT be described as held-out or real frame FER, reconciliation
efficiency, leakage, key rate, scaling superiority, qualification or
promotion evidence; `undetected` frames SHALL never be merged with exact
frames, and planning-only `f` is not real-channel efficiency. An
independent Pre-EXECUTE review SHALL pass before the single attempt, and
an independent Pre-RESULT review SHALL recompute all allocations,
outcomes, intervals, accounting and gates from the five artifacts before
any result or label is published; neither the run nor the implementing
session may accept its own work.
