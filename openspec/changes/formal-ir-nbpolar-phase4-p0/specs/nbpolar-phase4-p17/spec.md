# NB-Polar Phase 4-P17 specification delta

Phase 4-P17 is the N=32768 operational replication of the accepted P16
f=1.3 gate on the V25 1M count matrix (not the Model-F CAL artifact
rejected for this purpose by X07). One Tier-Y development gate repeats
the P16 operational measurement at exactly the same target model, N,
construction, disclosure and protocol with 128 fresh DEV blocks, to
resolve P16's zero-count margin. P16's 62/64 is report-only historical
context and contributes zero observations to the P17 decision. This is a
model-sampled operational development gate, not real-data qualification.
The claim scope is narrow: an operational replication development signal
for the frozen V25 1M population only; it is not held-out or real frame
FER, efficiency, key rate, scaling superiority, qualification or
promotion. Implementation tasks live in the companion P17 section of
`tasks.md`; status, acceptance and route disposition are owned by the
main thread, never by the implementing session. This document authorizes
no production behavior.

## Requirement: verified predecessor, frozen target input, support rule and preconditions

Before any output root exists and before the NPZ content open, the gate
SHALL read P16's accepted `construction_and_allocation.json` and verify:
N=`32768`, K_total=`6811`, K1=`319`, K2=`6492`, valid L1/L2 permutations
of length N, and the canonical construction digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
(recomputed with the exact P16 canonical recipe). P16 remains immutable.
Any mismatch SHALL stop before any attempt and consume nothing.

The gate SHALL then open exactly source `1M` through the accepted
`load_v25_channel_counts(path)` from
`/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`,
after a stat-only size check of exactly `25,166,822` bytes and an
absent-output root check; one artifact content read and one scientific
attempt SHALL be consumed together at the first NPZ content open, with
no reopen and no Model-F, held-out, raw-parquet or TTBin read. The only
support rule SHALL be the exact P7 rule: column-normalize the raw
counts, replace every cell below `1e-15` by `1e-15`, renormalize each
Bob column; `p_b` SHALL be the column totals over the total count, and
`P1`/`P2` SHALL be the accepted `derive_p1`/`derive_p2` tables under the
packing `A = 32*U1 + U2`. No lambda, global backoff, tuning, floor scan
or held-out fitting is permitted. Before any SC call the gate SHALL
recheck the exact P7 entropy/support preconditions: no zero Bob column;
`p_b` normalization and conditional-table column error `<= 1e-12`;
raw-MLE in-sample population `H1` within `1e-12` of
`0.02428054681872374`, `H2` within `1e-12` of `0.7767572780789994`,
total within `1e-12` of `0.8010378248977232` (ratified P7 semantics);
and the floor-induced total entropy change relative to the raw MLE
table `<= 1e-9`. Refusals (absent root, CLI parse, construction
identity, K flags, seed grouping, chunk/tag/N contracts) SHALL happen
before the content open with zero SC calls; any post-open failure SHALL
be `BLOCKED(<earliest gate>)` with consumption already spent (recorded
in the refusal message and freeze doc, and best-effort in the
pre-created stub files, never as a fresh root). Before the first DEV
block the gate SHALL additionally verify in code that the accepted
Wilson helper still reproduces the frozen boundary values (121/128
rounds to `0.9021084760`, 120/128 rounds to `0.8924595822`). No
construction, retraining or order computation of any kind exists in
this gate: orders and allocation arrive only through the verified P16
file.

## Requirement: frozen replication matrix with verified orders and operational DEV

The gate SHALL use GF32 (primitive polynomial 37, alpha 2, natural
order), N=`32768`, `chunk_rows=512`, planning `f=1.3` and tag-bits `64`,
with K1=`319`/K2=`6492` exactly as verified. DEV SHALL be the fresh
streams `2026092030..2026092037` times sixteen blocks each (128 blocks),
disjoint from every P16 stream; each stream SHALL restart its RNG. Per
block the gate SHALL sample `B ~ p_b` then `A ~ P_floor(A|B)` once.

For every DEV block the gate SHALL sample once and then: (1) disclose
true U1 at verified `order1[:K1]` and run operational L1 SC; (2) build
L2 metrics only from Bob and the hard L1 candidate (the true high layer
SHALL NOT enter this metric); (3) disclose true U2 at verified
`order2[:K2]` and restart operational L2 SC; (4) form
`label_hat = 32*high_hat + low_hat` and invoke exactly one 64-bit
Toeplitz tag in the P17/N/block seed domain (public master `DEV stream
seed + 10000`; the P17 seed prefix SHALL differ from P16's; raw seed
bits SHALL NOT be persisted); (5) classify exactly one of `exact`,
`undetected`, `verify_failed`, `decode_failed`, `nonfinite` (numeric SC
failure, outranking generic `decode_failed`) or `resource_abort`, with
undetected never success. Alice truth SHALL enter only sampling,
disclosed values, tag construction and scoring. No second arm, no
advancement and no repeated decode of any block is permitted.

## Requirement: frozen disclosure, verification and independent decision rule

A fully invoked block SHALL disclose exactly `5*(K1+K2)+64 = 34119`
key-dependent bits with `(5*K_total+64)/(N*H_total) <= 1.3` asserted from
the literals; partial failure SHALL count only actually disclosed bits.
Public Toeplitz control SHALL be `10*N+63 = 327743` bits per invoked
tag. The gate SHALL keep an independent literal recount of all
disclosure/tag/public-control events with zero mismatch.

Integrity gates (all persisted as booleans and all required before any
candidate label) SHALL be, in frozen order: predecessor construction
identity; target population contract; construction frozen before DEV;
128/128 DEV coverage with the exact frozen stream grouping; exact frozen
disjoint streams; valid verified orders with K replay and `f <= 1.3`;
mutually exclusive exhaustive outcome buckets; truth isolation (L1
`PRIOR_ONLY` / L2 `CANDIDATE_CONDITIONED` provenance with zero
violations); undetected zero; nonfinite zero; exact SC call accounting
(SC attempts exactly recomputed from the persisted records, with no
second counter of any kind); disclosure and literal-recount exactness;
exact attempt/read accounting (1 allowed / 1 consumed at the NPZ content
open in the frozen run; no retry, no reopen); and resource limits met
with no abort. Scientific classification over the 128 P17 blocks only
SHALL be:
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` iff all
integrity gates pass and exact `>= 121/128` with one-sided 95% Wilson
exact-recovery lower bound `>= 0.90`;
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_NOT_CONFIRMED` iff
integrity passes but either recovery gate fails; otherwise `BLOCKED`
with the failing gate names in frozen order (the operator maps this to
`BLOCKED(<earliest gate>)`). The 121/128 threshold has Wilson LB
`0.9021084760`; 120/128 has `0.8924595822`. The recovery total is pinned
to 128: P16's 62/64 is discussion-only context and SHALL NOT enter any
gate input.

## Requirement: frozen CLI, five-file output, checkpointing and bounded scope

The CLI SHALL require every flag — `--counts`, `--source`, `--floor`,
`--n`, `--k1`, `--k2`, `--construction`, `--construction-digest`,
`--dev-seeds`, `--dev-blocks-per-stream`, `--chunk-rows`, `--tag-bits`
and `--out-dir` — with no production default; it SHALL refuse an
existing output root, an N other than `32768`, K flags other than
`319`/`6492`, a chunk-rows value other than 512 (with the `_minus_block`
default-512 contract check), a tag-bits value other than 64,
dev-blocks-per-stream other than 16, a dev-seed count other than eight
streams, non-distinct or P16-overlapping streams, a construction digest
flag other than the frozen digest, and a CLI parse failure before the
NPZ content open. The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/`
SHALL be absent before execution and SHALL be created with exactly five
files before the content open (`frozen_plan.json`,
`predecessor_construction_identity.json`, `per_block_outcomes.jsonl`,
`aggregate_summary.json`, `report.md`), checkpointed after every
completed DEV block; no sidecars SHALL be created. Predecessor identity
and scalar block outcomes only — counts, sampled symbols, truth
vectors, decoded labels/keys, metric planes, tag seeds and RNG state
SHALL NOT be persisted. The gate SHALL record wall, RSS HWM, Linux
`VmPeak` and `VmSize` per record. The frozen environment SHALL be
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`MALLOC_ARENA_MAX=2` with a 2 GiB virtual limit and a 2400 s external
timeout. A wall/RSS breach during DEV SHALL abort-fill the remaining
blocks, preserve checkpoints and complete as BLOCKED. On MemoryError the
gate SHALL preserve checkpoints, finalize BLOCKED if possible, and never
rerun. No rerun, seed/N/K/floor/order/threshold change or partial
replacement is permitted after content open. Forbidden: Model-F
artifact, raw/held-out/real frames, EVAL, other N in the frozen run, any
construction path, any second or retry arm, transform/belief/list
decoders, production benchmark, FER/efficiency/key-rate/qualification/
promotion claim, old-root modification, commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered candidate /
not-confirmed labels and the blocker return; a candidate means that at
the frozen V25 1M population point the 128-block replication completed
with every identity, budget, allocation, order, outcome, truth, call,
checkpoint, accounting and resource gate true, and at least 121 of 128
fresh DEV blocks recovered exactly with Wilson LB `>= 0.90`. It SHALL
NOT be described as held-out or real frame FER, reconciliation
efficiency, leakage, key rate, scaling superiority, qualification or
promotion evidence; planning `f` is not real-channel efficiency; it is
model-sampled, not real-data evidence. An independent Pre-EXECUTE review
SHALL pass before the single attempt, and an independent Pre-RESULT
review SHALL recompute the 128 outcomes, Wilson, disclosure/public
accounting, predecessor identity, gates, resources and the five-file
inventory from the five artifacts before any result or label is
published; neither the run nor the implementing session may accept its
own work.
