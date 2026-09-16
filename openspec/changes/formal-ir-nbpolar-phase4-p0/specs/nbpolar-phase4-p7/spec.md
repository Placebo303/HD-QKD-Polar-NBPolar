# NB-Polar Phase 4-P7 specification delta

Phase 4-P7 is the target-population empirical construction gate on the V25
1M TRAIN count matrix (not the Model-F CAL artifact rejected for this purpose
by X07).  One Tier-Y development gate asks whether pooled empirical genie
orders support reliable two-layer hard-candidate SC at a conservative fixed
disclosure point (`K1=45`, `K2=140`, `N=256`).  The claim scope is narrow: a
construction/protocol development signal for the frozen V25 TRAIN empirical
distribution at `N=256`; it is not held-out or real frame FER, efficiency, key
rate, scaling, qualification or promotion.  Implementation tasks live in the
companion P7 section of `tasks.md`; status, acceptance and route disposition
are owned by the main thread, never by the implementing session.

## Requirement: frozen target input and support rule

The gate SHALL load exactly source `1M` through the accepted
`load_v25_channel_counts(path)` from
`/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`,
after a stat-only size check of exactly `25,166,822` bytes and an absent-output
root check; one artifact content read and one scientific attempt SHALL be
consumed at the first NPZ content open, with no reopen and no Model-F,
held-out, raw-parquet or TTBin read.  The only support rule SHALL be:
column-normalize the raw counts, replace every cell below `1e-15` by `1e-15`,
renormalize each Bob column; `p_b` SHALL be the column totals over the total
count, and `P1`/`P2` SHALL be the accepted `derive_p1`/`derive_p2` tables under
the packing `A = 32*U1 + U2`.  No lambda, global backoff, tuning, floor scan or
held-out fitting is permitted.

## Requirement: preconditions and blocked target-population contract

Before any genie/SC call the gate SHALL require: no zero Bob column; `p_b`
normalization and conditional-table column error `<= 1e-12`; `H1` within
`1e-12` of `0.02428054681872374`; `H2` within `1e-12` of `0.7767572780789994`;
total within `1e-12` of `0.8010378248977232`; and the floor-induced total
entropy change relative to the raw MLE table `<= 1e-9`.  Any failure SHALL be
`BLOCKED(target_population_contract)` with no decoder/genie call and no output
root created.

## Requirement: frozen construction streams and orders

The gate SHALL use GF32 (primitive polynomial 37, alpha 2, natural order),
`N=256`; TRAIN streams `2026091650..2026091652` with 256 blocks each and DEV
streams `2026091660..2026091664` with 128 common blocks each (640 pairs);
per-DEV-stream public Toeplitz master `stream + 10000`, domain-separated by arm
and block.  Sampling SHALL be `B ~ p_b` then `A ~ P_floor(A|B)` with
`high = A//32`, `low = A%32`.  For L1 and oracle-conditioned L2 separately, the
gate SHALL accumulate `genie_conditionals` error/entropy sufficient statistics
per TRAIN stream and pooled across all three, freeze each pooled worst-first
order (and the three per-stream orders) before any DEV call, and require every
order to be a permutation and the minimum pairwise TRAIN-order Spearman rank
correlation to be `>= 0.95` for each layer.  BEC analytic control orders SHALL
be built from `epsilon_l = H_l/5` and are report-only; they SHALL never select
the empirical order.  TRAIN and DEV streams SHALL be disjoint and no EVAL
stream SHALL exist.

## Requirement: paired DEV arms, truth boundary and buckets

On every DEV block the gate SHALL run two paired protocol arms: (1) empirical:
pooled empirical L1 order `K1=45` then candidate-conditioned L2 via the pooled
empirical oracle-L2 order `K2=140`; (2) BEC control: BEC L1 order `K1=45` then
candidate-conditioned L2 via the BEC L2 order `K2=140`.  Each arm SHALL restart
SC by layer (no state, belief or partial sum crosses layers), rebuild the
10-bit label `low_hat + 32*high_hat` and invoke exactly one 64-bit Toeplitz
verification tag per viable candidate.  Alice truth SHALL enter only sampling,
disclosed values, tag construction and scoring; it SHALL NOT enter any
undisclosed operational metric, decision or candidate label.  Outcome buckets
SHALL be the accepted two-layer taxonomy: `exact` (tag pass AND label equal to
truth), `undetected` (tag pass and not exact; never merged with exact),
`verify_failed`, `decode_failed` (SC exception or nonfinite marginals; no tag)
and `resource_abort`.

## Requirement: frozen accounting and transcript recount

A fully invoked arm SHALL disclose exactly `5*(45+140)+64 = 989`
key-dependent bits (L1 `5*45`, L2 `5*140` when invoked, one `64`-bit tag when
invoked) and `2623` public control bits per invoked tag.  The gate SHALL
persist an independent literal transcript recount of the disclosure and tag
events per arm and in total and SHALL require zero mismatch against the
incremental totals.  Attempt/read accounting SHALL be exact (1 allowed/1
consumed at the NPZ content open in the frozen run; no retry, no reopen) and
the run SHALL stay within 2 GiB RSS and 3600 s wall.

## Requirement: integrity gates, scientific gates and outcome labels

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be: target input/support/entropy preconditions; 3x256
TRAIN and 5x128 DEV coverage complete and disjoint; orders frozen before DEV,
permutations valid and provenance correct; 640/640 arm pairing with mutually
exclusive and exhaustive buckets; truth-leak, `undetected`, nonfinite and
`resource_abort` all zero; disclosure exact (`989` per fully invoked arm,
`2623` public per tag) with zero recount mismatch; attempt/read accounting
exact; and resource limits met.  Scientific gates SHALL be: minimum pairwise
TRAIN-order Spearman `>= 0.95` for L1 and L2; empirical arm exact `>= 620/640`;
and the one-sided 95% Wilson exact-recovery lower bound `>= 0.95`
(`z = 1.6448536269514722`).  The gate SHALL return
`TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` iff every integrity and scientific
gate is true at the frozen 640-pair shape,
`TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED` iff integrity passes and any
scientific gate fails, and otherwise `BLOCKED` with
`integrity_all_pass=false` and the failing gate names in frozen order (the
operator maps this to `BLOCKED(<earliest gate>)`).  BEC-control exact counts,
paired cells, rank correlations and top-K overlaps are report-only; no gate
requires empirical to beat BEC.

## Requirement: frozen CLI, five-file output and bounded scope

The CLI SHALL require `--counts`, `--source`, `--n`, `--floor`,
`--train-seeds`, `--train-blocks`, `--dev-seeds`, `--dev-blocks`, `--k1`,
`--k2` and `--out-dir` with no production default; it SHALL refuse an existing
output root before the NPZ content open.  The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`
SHALL be absent before execution and SHALL contain exactly five compact
scalar-only files (`frozen_plan.json`, `construction_orders.json`,
`per_block_paired_outcomes.json`, `aggregate_summary.json`, `report.md`);
symbols, labels, disclosed values, decoded keys and raw seed bits SHALL NOT be
persisted.  No rerun, seed/order/K/floor/threshold change or partial
replacement is permitted after content open.  Forbidden: Model-F artifact,
raw/held-out/real frames, EVAL, `N>256`, adaptive schedule retuning,
APP/SCL/FWHT, production benchmark, efficiency/key-rate/qualification/promotion
claim, old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the two registered outcome labels and the
blocker return; a candidate means that at this single frozen V25 TRAIN
population point the pooled empirical construction supports `>= 620/640`
empirical exact recovery at `K1=45`/`K2=140` with a one-sided 95% Wilson lower
bound `>= 0.95`.  It SHALL NOT be described as held-out or real frame FER,
reconciliation efficiency, leakage, key rate, scaling, qualification or
promotion evidence; `undetected` frames SHALL never be merged with exact
frames, and planning-only `f` is not real-channel efficiency.  An independent
Pre-EXECUTE review SHALL pass before the single attempt, and an independent
Pre-RESULT review SHALL pass before any result or label is published; neither
the run nor the implementing session may accept its own work.
