# NB-Polar Phase 4-P14 specification delta

Phase 4-P14 is the empirical-genie construction learning curve gate at
P13's N=16384 point on the V25 1M TRAIN count matrix (not the Model-F
CAL artifact rejected for this purpose by X07). One Tier-Y development
gate determines whether failure to reach the planning budget `f<=1.3`
was materially caused by constructing from only eight TRAIN blocks. It
builds nested 8/16/32/64/128-block constructions from one 128-block
TRAIN sequence and evaluates all five on the same independent 32 DEV
blocks. This is a model-sampled genie construction diagnostic, not
operational FER or real-data qualification. The claim scope is narrow:
a learning-curve diagnostic for the frozen V25 TRAIN target population
only; it is not held-out or real frame FER, efficiency, key rate,
scaling, qualification or promotion. Implementation tasks live in the
companion P14 section of `tasks.md`; status, acceptance and route
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
`<= 1e-9`. Refusals (absent root, CLI parse, chunk/n/prefix/seed-shape
contract) SHALL happen before the content open with zero genie calls;
any post-open failure SHALL be `BLOCKED(<earliest gate>)` with
consumption already spent (recorded in the refusal message and freeze
doc, and best-effort in the pre-created stub files, never as a fresh
root).

## Requirement: frozen matrix with nested prefixes and shared decodes

The gate SHALL use GF32 (primitive polynomial 37, alpha 2, natural
order), the accepted P13 genie path (`block_genie_risks` with
`chunk_rows=512`) for every genie call, and exactly N=`16384`. The gate
SHALL run TRAIN streams `2026091930..2026091937` times 16 blocks each
(128 blocks) in stream-major order (seed ascending, then block index
ascending) and DEV streams `2026091940..2026091943` times 8 blocks each
(32 blocks), with each stream restarting its RNG. Nested prefix sizes
B=`8, 16, 32, 64, 128` SHALL come from that one TRAIN sequence. Each
TRAIN block SHALL be decoded once per layer; the accumulated risks
SHALL serve every applicable prefix with no repeated calls. Each DEV
block SHALL be decoded once per layer and its genie rows SHALL score
all five frozen constructions. Planned genie calls SHALL be exactly
320. Per block the gate SHALL sample `B ~ p_b` then `A ~ P_floor(A|B)`
once, compute L1 genie conditionals with the true U1 prefix and L2
genie conditionals with the true U1+U2 prefix (oracle-conditioned
construction only, L2 metrics `ORACLE_CONDITIONED` on the true high
symbols). No tag or Toeplitz master SHALL exist in this gate.

## Requirement: frozen nested construction and independent DEV evaluation

For each TRAIN block the gate SHALL accumulate coordinate risk
contributions `h_i = -log2 p_i[U_i]` and `e_i = 1 - max p_i` into
running sums; at each prefix boundary it SHALL pool means, order each
layer worst-first by the accepted `(e, h, index)` semantics, set
`K_total = floor((1.3*N*(H1+H2)-64)/5)` clipped to `[0, 2N]` (3399 at
the frozen point), enumerate all feasible integer splits `(K1, K2)`
with `K1+K2 = K_total`, and select the lexicographic minimum of
`(TRAIN residual e sum, K1, K2)`. All five orders, allocations and
TRAIN residuals SHALL be frozen before the first DEV block. For every
DEV block the gate SHALL persist the five scalar residuals `R_B =
sum(e1[undisclosed coords of prefix B]) + sum(e2[undisclosed coords of
prefix B])` from the one decode. DEV SHALL never be selected or tuned
from. Per prefix the gate SHALL report the 32 DEV `R_B` values, mean,
sample standard deviation, range and one-sided 95% Student-t upper
confidence bound `mean + 1.695518782*std/sqrt(32)` (df=31). It SHALL
also report paired `R_B - R_8` and adjacent differences with
mean/std/UCB. The residual is a genie union-bound construction proxy;
it is not operational FER. Report-only diagnostics SHALL be: pairwise
order Spearman/top-K overlap of each prefix against B=128, allocation
movement across prefixes, and per-block improved/tied/regressed counts
against R_8. P13's B=8 is a historical reference only: its
different-seed blocks SHALL NOT be merged and equality SHALL NOT be
required.

## Requirement: frozen decision rule on the B=128 prefix only

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be: target input/support/entropy preconditions;
one complete N cell with 128 TRAIN + 32 DEV blocks; exact nested
prefixes 8/16/32/64/128; disjoint frozen streams; five valid
permutation orders frozen before DEV with unchanged freeze digests;
exact K budget/allocation replay (K_total=3399) from the literals and
pooled risks; finite risks; zero genie exceptions; truth isolation (L1
`PRIOR_ONLY` / L2 `ORACLE_CONDITIONED` provenance with zero violations
and no truth arrays persisted); no unregistered calls (exactly 320
genie calls); checkpoint/file accounting consistency; exact
attempt/read accounting (1 allowed / 1 consumed at the NPZ content open
in the frozen run; no retry, no reopen); and resource limits met with no
abort. Scientific classification SHALL use only the B=128 prefix:
`TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE` if its frozen
one-sided DEV residual UCB `<= 0.01`;
`TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` if integrity
passes but it does not; otherwise `BLOCKED` with the failing gate names
in frozen order (the operator maps this to `BLOCKED(<earliest gate>)`).
Other prefixes diagnose learning only. The gate SHALL NOT describe this
as an FER threshold, a real-channel result or proof of any minimum N or
TRAIN size.

## Requirement: frozen CLI, five-file output, checkpointing and bounded scope

The CLI SHALL require every flag — `--counts`, `--source`, `--floor`,
`--target-f`, `--n`, `--train-seeds`, `--dev-seeds`,
`--train-blocks-per-stream`, `--dev-blocks-per-stream`,
`--prefix-blocks`, `--chunk-rows` and `--out-dir` — with no production
default; it SHALL refuse an existing output root, a chunk-rows value
other than 512 (with the `_minus_block` default-512 contract check), an
N other than 16384, prefix blocks other than `8 16 32 64 128`,
train/dev blocks-per-stream other than 16/8, a seed shape other than
eight TRAIN plus four DEV streams (distinct within, disjoint across),
and a CLI parse failure before the NPZ content open. The only output
root
`.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/`
SHALL be absent before execution and SHALL be created with exactly five
files before the content open (`frozen_plan.json`,
`learning_curve_constructions.json`, `per_block_genie_residuals.jsonl`,
`aggregate_summary.json`, `report.md`), then checkpointed with the same
five files after every completed TRAIN/DEV block; no sidecars SHALL be
created. Pooled risks/public orders and scalar block statistics only —
counts, sampled symbols, truth vectors, decoder outputs, metric planes
and RNG state SHALL NOT be persisted. The gate SHALL record wall, RSS
HWM, Linux `VmPeak` and `VmSize`. The frozen environment SHALL be
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`MALLOC_ARENA_MAX=2` with a 2 GiB virtual limit and an 1800 s external
timeout. On MemoryError/resource failure the gate SHALL preserve
checkpoints, finalize BLOCKED if possible, and never rerun. No rerun,
seed/prefix/order/allocation/threshold change or partial replacement is
permitted after content open. Forbidden: Model-F artifact,
raw/held-out/real frames, EVAL, other N in the frozen run, empirical
work outside the registered matrix, adaptive work, APP/SCL/FWHT,
production benchmark, FER/efficiency/key-rate/qualification/promotion
claim, old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered candidate /
not-confirmed labels and the blocker return; a candidate means that at
the frozen V25 TRAIN population point the 160-block gate completed with
every budget, allocation, order, risk, truth, call, checkpoint,
accounting and resource gate true, and the B=128 prefix has DEV
residual UCB `<= 0.01`. It SHALL NOT be described as held-out or real
frame FER, reconciliation efficiency, leakage, key rate, scaling
superiority, qualification or promotion evidence; planning `f` is not
real-channel efficiency. An independent Pre-EXECUTE review SHALL pass
before the single attempt, and an independent Pre-RESULT review SHALL
recompute the prefixes, constructions, statistics, classification,
accounting/resources and the five-file inventory from the five
artifacts before any result or label is published; neither the run nor
the implementing session may accept its own work.
