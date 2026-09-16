# NB-Polar Phase 4-P15 specification delta

Phase 4-P15 is the empirical-genie mid-N scaling gate at N=32768 and
N=65536 on the V25 1M TRAIN count matrix (not the Model-F CAL artifact
rejected for this purpose by X07). One Tier-Y development gate extends
the accepted P13/P14 empirical-genie residual curve with empirical
construction and independent DEV only, and determines whether either
registered N reaches the planning budget `f<=1.3` genie-residual UCB
target. It does not retry P12's operational/surrogate profile. This is
a model-sampled genie construction diagnostic, not operational FER or
real-data qualification. The claim scope is narrow: a mid-N
construction/rate development signal for the frozen V25 TRAIN target
population only; it is not held-out or real frame FER, efficiency, key
rate, scaling, qualification or promotion. Implementation tasks live in
the companion P15 section of `tasks.md`; status, acceptance and route
disposition are owned by the main thread, never by the implementing
session. This document authorizes no production behavior.

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
held-out fitting is permitted. Before any genie call the gate SHALL
recheck the exact P7 entropy/support preconditions: no zero Bob column;
`p_b` normalization and conditional-table column error `<= 1e-12`;
raw-MLE in-sample population `H1` within `1e-12` of
`0.02428054681872374`, `H2` within `1e-12` of `0.7767572780789994`,
total within `1e-12` of `0.8010378248977232` (ratified P7 semantics); and
the floor-induced total entropy change relative to the raw MLE table
`<= 1e-9`. Refusals (absent root, CLI parse, chunk contract, N-to-seed
grouping) SHALL happen before the content open with zero genie calls;
any post-open failure SHALL be `BLOCKED(<earliest gate>)` with
consumption already spent (recorded in the refusal message and freeze
doc, and best-effort in the pre-created stub files, never as a fresh
root).

## Requirement: frozen two-cell matrix with oracle-conditioned genie construction

The gate SHALL use GF32 (primitive polynomial 37, alpha 2, natural
order), the accepted P13 genie path (`block_genie_risks` with
`chunk_rows=512`) for every genie call, and exactly N=`32768, 65536`.
Per N the gate SHALL run TRAIN four fresh streams times four blocks
each (16 blocks) and DEV four disjoint fresh streams times four blocks
each (16 blocks), with each stream restarting its RNG:

| N | TRAIN streams | DEV streams |
|---:|---|---|
| 32768 | 2026091960..1963 | 2026091970..1973 |
| 65536 | 2026091980..1983 | 2026091990..1993 |

Per block the gate SHALL sample `B ~ p_b` then `A ~ P_floor(A|B)` once,
compute L1 genie conditionals with the true U1 prefix and L2 genie
conditionals with the true U1+U2 prefix (oracle-conditioned construction
only, L2 metrics `ORACLE_CONDITIONED` on the true high symbols). Each
block SHALL be sampled once and decoded once per layer (L1 true-prefix
genie, then oracle-conditioned L2 true-prefix genie). Planned genie
calls SHALL be exactly 128 (64 blocks x 2 layers). No decision arm, no
tag and no Toeplitz master SHALL exist in this gate.

## Requirement: frozen empirical construction, allocation and DEV residual

For each TRAIN block the gate SHALL accumulate coordinate risk
contributions `h_i = -log2 p_i[U_i]` and `e_i = 1 - max p_i`, pool TRAIN
risks per layer as means, and persist only the pooled coordinate risks,
never per-block metric/risk planes. Each layer SHALL be ordered
worst-first by the accepted `(e, h, index)` semantics. The gate SHALL set
`K_total = floor((1.3*N*(H1+H2)-64)/5)`, clipped to `[0, 2N]` (6811 at
N=32768, 13636 at N=65536), enumerate all feasible integer splits
`(K1, K2)` with `K1+K2 = K_total`, and select the lexicographic minimum
of `(TRAIN residual e sum, K1, K2)`. Orders, allocation and TRAIN
residual SHALL be frozen before that N's first DEV block; DEV SHALL
never change them. For every DEV block the gate SHALL persist the scalar
undisclosed-coordinate residual `R = sum(e1[undisclosed empirical
coords]) + sum(e2[undisclosed empirical coords])` for the frozen split.
DEV SHALL never be selected or tuned from. Per N the gate SHALL report
all 16 DEV `R` values, mean, sample standard deviation, range and
one-sided 95% Student-t upper confidence bound
`mean + 1.753050356*std/sqrt(16)` (df=15). The residual is a genie
union-bound construction proxy; it is not operational FER and not proof
of any minimum N. Report-only diagnostics SHALL be: order stability
across the four TRAIN streams (per-stream order Spearman against the
pooled order), allocation and resources.

## Requirement: frozen decision rule with the any-UCB candidate

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be: target input/support/entropy preconditions;
two complete N cells with 16 TRAIN + 16 DEV blocks per N; disjoint
frozen streams; valid permutation orders frozen before DEV with an
unchanged freeze digest; exact K budget/allocation replay from the
literals and pooled risks; finite risks; zero genie exceptions; truth
isolation (L1 `PRIOR_ONLY` / L2 `ORACLE_CONDITIONED` provenance with zero
violations and no truth arrays persisted); no unregistered calls (exactly
128 genie calls); checkpoint/file accounting consistency; exact
attempt/read accounting (1 allowed / 1 consumed at the NPZ content open
in the frozen run; no retry, no reopen); and resource limits met with no
abort. Scientific classification SHALL be:
`TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE` with the smallest
qualifying registered N if any DEV UCB `<= 0.01`;
`TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` if integrity
passes but neither UCB meets it; otherwise `BLOCKED` with the failing
gate names in frozen order (the operator maps this to
`BLOCKED(<earliest gate>)`). The gate SHALL describe the UCB as a genie
construction proxy only, never as an FER threshold, a real-channel
result or proof of any minimum N.

## Requirement: frozen CLI, five-file output, checkpointing and bounded scope

The CLI SHALL require every flag — `--counts`, `--source`, `--floor`,
`--target-f`, `--n-values`, `--train-seeds`, `--dev-seeds`,
`--train-blocks-per-stream`, `--dev-blocks-per-stream`, `--chunk-rows`
and `--out-dir` — with no production default; it SHALL refuse an
existing output root, a chunk-rows value other than 512 (with the
`_minus_block` default-512 contract check), N values other than
`32768 65536`, train/dev blocks-per-stream other than 4/4, a seed
grouping other than eight TRAIN plus eight DEV streams (four per N in N
order: TRAIN `1960..63, 1980..83` / DEV `1970..73, 1990..93`; distinct
within, disjoint across), and a CLI parse failure before the NPZ content
open. The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/`
SHALL be absent before execution and SHALL be created with exactly five
files before the content open (`frozen_plan.json`,
`construction_and_allocations.json`, `per_block_genie_residuals.jsonl`,
`aggregate_summary.json`, `report.md`), then checkpointed with the same
five files after every completed block; no sidecars SHALL be created.
Public orders/pooled risks and scalar block statistics only — counts,
sampled symbols, truth vectors, decoder outputs, metric planes and RNG
state SHALL NOT be persisted. The gate SHALL record wall, RSS HWM, Linux
`VmPeak` and `VmSize` per cell and per block record. The frozen
environment SHALL be `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2` with a 2 GiB virtual limit and
a 2100 s external timeout. On MemoryError/resource failure the gate
SHALL preserve checkpoints, finalize BLOCKED if possible, and never
rerun. No rerun, seed/N/K/floor/order/threshold change or partial
replacement is permitted after content open. Forbidden: Model-F artifact,
raw/held-out/real frames, EVAL, other N in the frozen run, any decision
arm, FWHT/APP/SCL, production benchmark, tag/Toeplitz, FER/efficiency/
key-rate/qualification/promotion claim, old-root modification, commit or
push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered candidate /
not-confirmed labels and the blocker return; a candidate means that at
the frozen V25 TRAIN population point the two-N/64-block gate completed
with every budget, allocation, order, risk, truth, call, checkpoint,
accounting and resource gate true, and at least one registered N has DEV
residual UCB `<= 0.01`. It SHALL NOT be described as held-out or real
frame FER, reconciliation efficiency, leakage, key rate, scaling
superiority, qualification or promotion evidence; planning `f` is not
real-channel efficiency. An independent Pre-EXECUTE review SHALL pass
before the single attempt, and an independent Pre-RESULT review SHALL
recompute the two allocations, per-block residual aggregates/UCBs,
classification, resource/accounting records and the five-file inventory
from the five artifacts before any result or label is published; neither
the run nor the implementing session may accept its own work.
