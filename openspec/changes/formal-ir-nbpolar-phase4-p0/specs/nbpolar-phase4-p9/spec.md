# NB-Polar Phase 4-P9 specification delta

Phase 4-P9 is the lower-rate boundary resolution gate on the V25 1M TRAIN
count matrix. It reuses the accepted P8 static target-population protocol
and extends the SCREEN grid down to both zero axes, then confirms exactly
one deterministically selected point on disjoint streams. This resolves
P8's left-censored rate search at `N=256` and is the final N=256
static-rate localization gate before a main-thread choice between adaptive
target-rate work and N-scaling/decoder acceleration. The claim scope is
narrow: a static development signal for the frozen V25 TRAIN empirical
distribution at `N=256`; it is not held-out or real frame FER, efficiency,
key rate, scaling, qualification or promotion. Implementation tasks live
in the companion P9 section of `tasks.md`; status, acceptance and route
disposition are owned by the main thread, never by the implementing
session. This document authorizes no production behavior.

## Requirement: frozen target input, orders identity and support rule

The gate SHALL reuse the accepted P8 input contract unchanged: the P7
pooled empirical L1/L2 orders from the immutable P7
`construction_orders.json` with the frozen order identity
`8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`
(recomputed canonical digest equals the recorded digest) and the BEC
orders equal to the accepted `analytic_order` H1/H2-surrogate orders,
checked BEFORE opening the channel artifact; any mismatch SHALL be a
fail-closed refusal consuming no artifact read and no scientific attempt.
The gate SHALL then open exactly source `1M` through the accepted
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
held-out fitting is permitted.

## Requirement: preconditions and blocked target-population contract

Before any SC call the gate SHALL recheck the exact P7 entropy/support
preconditions: no zero Bob column; `p_b` normalization and
conditional-table column error `<= 1e-12`; raw-MLE in-sample population
`H1` within `1e-12` of `0.02428054681872374`, `H2` within `1e-12` of
`0.7767572780789994`, total within `1e-12` of `0.8010378248977232`; and
the floor-induced total entropy change relative to the raw MLE table
`<= 1e-9`. Any failure SHALL be `BLOCKED(target_population_contract)`
with zero SC calls and no output root created.

## Requirement: frozen shared-block SCREEN and deterministic selection

The gate SHALL use GF32 (primitive polynomial 37, alpha 2, natural
order), `N=256`; SCREEN streams `2026091710..2026091712` with 64 common
blocks each (192); the static empirical-order grid `K1 =
[0,2,4,6,8,12,24,45]` by `K2 = [0,20,40,50,60,70,80]` (exactly 56
configurations, including the global zero-disclosure corner `(0,0)` and
the accepted P8 anchor `(8,80)`). Sampling SHALL be `B ~ p_b` then `A ~
P_floor(A|B)` once per shared block (`high = A//32`, `low = A%32`); every
grid point SHALL use the identical block object. Each configuration SHALL
run L1 then candidate-conditioned L2 from scratch, rebuild the full label
`low_hat + 32*high_hat` and invoke exactly one P9-domain-separated 64-bit
Toeplitz tag per block (public master `stream + 10000`, domain-separated
by P9 phase/arm/block with a P9 tag-domain prefix that differs from the
P8 prefix). Zero-K behavior SHALL hold by construction: `K1=0` and/or
`K2=0` disclose nothing for that layer, and `(0,0)` is the tag-only
64-bit arm. A SCREEN point is eligible iff all 192 blocks are accounted
for, undetected/nonfinite/resource_abort are zero, and its one-sided 95%
Wilson exact-recovery lower bound (`z = 1.6448536269514722`) is `>= 0.95`
(equivalently at this frozen shape, exact `>= 188/192`; the
implementation SHALL record both the bound and the count check). The gate
SHALL select exactly one point by lexicographically minimizing
`(K1+K2, K1, K2)` over eligible points only, using no DEV/CONFIRM outcome
and no runtime to break ties. If no point is eligible the gate SHALL stop
without CONFIRM and return
`TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` (a valid scientific negative
result, not BLOCKED). No interpolation or unregistered point is allowed;
a selected grid boundary is not by itself a search-truncation ambiguity
because both axes include zero.

## Requirement: frozen disjoint CONFIRM with paired BEC control

CONFIRM streams SHALL be `2026091720..2026091724` with 128 common blocks
each (640), asserted disjoint from SCREEN and all prior official streams
(`1650..52`, `1660..64`, `1680..82`, `1690..94`); no SCREEN block,
outcome or tag seed may enter CONFIRM. CONFIRM SHALL run only the
selected empirical-order point plus a paired BEC-order control at the same
selected K1/K2; BEC orders use the accepted P7 H1/H2 surrogate and are
report-only. The Toeplitz public master SHALL be `stream + 10000`,
domain-separated by P9 phase/arm/block. The selected point confirms iff
empirical exact `>= 618/640`, the one-sided 95% Wilson exact-recovery
lower bound `>= 0.95`, and undetected, nonfinite and resource_abort are
zero. BEC exact and empirical-vs-BEC paired cells are report-only;
empirical is not required to beat BEC.

## Requirement: frozen accounting and transcript recount

A fully invoked point SHALL disclose exactly `5*(K1+K2)+64`
key-dependent bits (L1 `5*K1` even when the L1 SC call fails, L2 `5*K2`
only when invoked, one `64`-bit tag only when invoked) and `2623` public
control bits per invoked tag; decode failure before tag counts only
actually disclosed coordinate bits. Outcome buckets SHALL be the accepted
two-layer taxonomy (`exact`, `verify_failed`, `decode_failed`,
`undetected`, `resource_abort`), mutually exclusive with `undetected`
never merged into exact. The gate SHALL persist an independent literal
transcript recount of the disclosure and tag events per arm, per phase
and in total and SHALL require zero mismatch against the incremental
totals. Attempt/read accounting SHALL be exact (1 allowed/1 consumed at
the NPZ content open in the frozen run; no retry, no reopen) and the run
SHALL stay within 2 GiB RSS and 3600 s wall.

## Requirement: integrity gates, scientific gates and outcome labels

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be: P7 orders identity/permutations/surrogate
provenance; target input/support/entropy preconditions; SCREEN (3x64)
and, when executed, CONFIRM (5x128) coverage complete with disjoint
streams; arm pairing with mutually exclusive and exhaustive buckets;
truth-leak zero globally; `undetected`, nonfinite and `resource_abort`
zero over the decision path (eligible SCREEN points and CONFIRM);
disclosure exact with zero recount mismatch; attempt/read accounting
exact; and resource limits met. Confirm scientific gates SHALL be:
empirical exact `>= 618/640` and the one-sided 95% Wilson lower bound
`>= 0.95` at the frozen 640-block shape. The gate SHALL return
`TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` iff no SCREEN point is
eligible, `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` iff a point is
selected and every CONFIRM/integrity gate passes at the frozen shape,
`TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED` iff integrity passes
but CONFIRM fails, and otherwise `BLOCKED` with the failing gate names in
frozen order (the operator maps this to `BLOCKED(<earliest gate>)`).

## Requirement: frozen CLI, five-file output and bounded scope

The CLI SHALL require exactly thirteen flags — `--gate-id`,
`--counts`, `--source`, `--orders`, `--n`, `--floor`,
`--screen-seeds`, `--screen-blocks`, `--k1-grid`, `--k2-grid`,
`--confirm-seeds`, `--confirm-blocks` and `--out-dir` — with no
production default; `--gate-id` SHALL be the closed-choice
`p9-lower-rate-boundary` in the frozen command, selecting only the P9
protocol name, the P9 tag-domain prefix and the P9 result labels, while
the P8 path (P8 gate id) preserves the existing P8 protocol
name/prefix/labels byte-for-byte; silent reuse of P8 identifiers in the
P9 path is forbidden. The CLI SHALL refuse an existing output root and
an orders-identity mismatch before the NPZ content open. The only output
root
`.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/`
SHALL be absent before execution and SHALL contain exactly five compact
scalar-only files (`frozen_plan.json`, `screen_records.json`,
`selection_and_confirmation_records.json`, `transcript_accounting.json`,
`report.md`); source/Bob/U/decoded/disclosed vectors, metric arrays,
labels, tags and raw seed material SHALL NOT be persisted. The report
SHALL cover all 56 SCREEN configurations with eligibility and
deterministic selection, CONFIRM per-stream (5x128) and pooled outcomes
with paired cells and Wilson values, leakage totals, the planning-only
`f = mean_key_dependent/(256*0.8010378248977232)`, wall and RSS. No
rerun, seed/grid/floor/order/threshold change or partial replacement is
permitted after content open. Forbidden: Model-F artifact,
raw/held-out/real frames, EVAL, `N>256`, adaptive schedule, APP/SCL/FWHT,
production benchmark, efficiency/key-rate/qualification/promotion claim,
old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the three registered outcome labels
and the blocker return; a candidate means that at this single frozen V25
TRAIN population point the lowest-disclosure static grid point clearing
the frozen SCREEN rule also clears the disjoint 640-block CONFIRM. It
SHALL NOT be described as held-out or real frame FER, reconciliation
efficiency, leakage, key rate, scaling, qualification or promotion
evidence; `undetected` frames SHALL never be merged with exact frames,
and planning-only `f` is not real-channel efficiency. An independent
Pre-EXECUTE review SHALL pass before the single attempt, and an
independent Pre-RESULT review SHALL pass before any result or label is
published; neither the run nor the implementing session may accept its
own work.
