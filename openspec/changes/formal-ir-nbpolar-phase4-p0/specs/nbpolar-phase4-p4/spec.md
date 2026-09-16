# NB-Polar Phase 4-P4 specification delta

Phase 4-P4 restores the two-layer dependency omitted before the protocol
phases: the smallest two-stage SC closed loop on injected synthetic tables,
paired with a strictly isolated true-L1 oracle diagnostic. It is an interface
and cross-layer-propagation gate, not held-out real-data reconciliation.
Implementation tasks live in the companion P4 section of `tasks.md`; status and
acceptance are owned by the main thread, never by the implementing session.

## Requirement: causal candidate-conditioned operational path

The operational arm SHALL build the L1 metric from Bob and the injected
`P1 [U1,B]` table only, SHALL run exactly one `sc_decode` with
`known_positions = D1 = sorted(analytic_order(epsilon1, N)[:k1])` and the
actual `U1[D1]` GF32 values (zeros are values, never sentinels), and SHALL take
the source-domain hard candidate from that decode's re-encoded word
(`sc1.x_hat`). It SHALL build `P2_hat` by gathering the `[U1,B,U2]` table on
Bob and that candidate, SHALL mark it `CANDIDATE_CONDITIONED`, SHALL run
exactly one **fresh** `sc_decode` with `known_positions = D2 =
sorted(analytic_order(epsilon2, N)[:k2])` and the actual `U2[D2]`, and SHALL
form the full label `low_hat + 32*high_hat`. No decoder state, APP, soft
belief, partial sum or hard decision SHALL cross from L1 to L2; no warm start
and no reuse of L1 decoder objects is permitted. The arm SHALL invoke exactly
one final 64-bit Toeplitz tag over the MSB-first 10-bit label expansion using
the per-arm/per-block SHA-256 counter-stream seed derived from the frozen
public master with arm label `operational`, and SHALL disclose no further
coordinate after that tag.

## Requirement: isolated true-L1 oracle diagnostic

A labelled oracle arm SHALL condition its `P2_true` metric on the true high
layer only, SHALL mark it `ORACLE_CONDITIONED`, SHALL use the same block and
the same frozen `D2/U2[D2]` disclosures, and SHALL form
`label_oracle = low_hat_oracle + 32*high_true` with its own single final tag
under arm label `oracle`.  Alice truth, oracle values, APP or soft beliefs
SHALL NOT enter the operational metric, decoder arguments or tag; truth may
enter only the oracle arm, the disclosed-U map and scoring.  The oracle arm
SHALL run whenever true L1 is available, including blocks whose operational L1
decode failed.  A truth-isolation sentinel SHALL adversarially mutate truth
copies after the metrics and decisions exist and SHALL require the operational
metric and decisions to stay bitwise unchanged; violations SHALL be counted
and SHALL be zero.  A documented wrong-L1 assessment seam SHALL record the
per-block `oracle_candidate_divergence` (operational `P2_hat` differing from
`P2_true`) as report-only with no threshold.

## Requirement: disjoint outcome taxonomy, per-layer sub-buckets and accounting

Each arm SHALL classify every planned block into exactly one of `exact` (tag
pass and label equals the true label), `undetected` (tag pass and not exact;
never success), `verify_failed` (tag mismatch), `decode_failed` (L1 or L2 SC
exception or nonfinite decision marginals; no tag for that arm) or
`resource_abort` (block not executed because the preregistered budget stop
fired), and SHALL record per-layer sub-buckets (L1 executed/decode_failed, L2
invoked/skipped-by-L1-failure/decode_failed, tag invoked) that partition the
executed blocks.  Every block whose L1 stage returns a candidate SHALL invoke
both arms' L2.  Accounting SHALL be `5*k1` for the L1 disclosure, `5*k2` when
L2 is invoked and `64` when the one final tag is invoked, totalling
`5*(k1+k2) + 64` for a fully invoked arm; each tag invocation SHALL consume
2623 public seed bits at N=256, reported separately.  Canonical transcript
events (L1 disclosure, L2 disclosure, final tag per arm) SHALL be recounted by
an independent literal implementation whose totals equal the incremental
totals with zero mismatch.

## Requirement: frozen interface gate, five-file output and bounded scope

Exactly one bounded synthetic gate SHALL run on the frozen point (GF32/poly 37,
alpha 2, natural order, `N=256`, `epsilon1=0.05`, `epsilon2=0.20`, `k1=45`,
`k2=110`, 96 paired blocks, run seed `2026091360`, public Toeplitz master
`2026091361`, 2 GiB / 3600 s).  The CLI SHALL require `--n`, `--epsilon1`,
`--epsilon2`, `--k1`, `--k2`, `--blocks`, `--seed`, `--toeplitz-master` and
`--out-dir` with no production default, SHALL refuse an existing output root
before any decoder call, and SHALL refuse the consumed official seeds
`2026091200..2026091213`, `2026091314..2026091321`, `2026091330`,
`2026091340`, `2026091341`, `2026091350`, `2026091351` while accepting the
frozen pair.  The single attempt SHALL be consumed at the first gate SC call;
no rerun, seed change, table/K/threshold/set change or partial credit is
permitted.  The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`
SHALL be absent before execution and SHALL contain exactly five compact
scalar-only files (`frozen_plan.json`, `per_block_two_layer_outcomes.json`,
`transcript_accounting.json`, `aggregate_summary.json`, `report.md`); symbols,
labels, disclosed values, decoded keys and raw seed bits SHALL NOT be
persisted.  All hard gates (96/96 paired coverage; both arms' L2 invoked for
every L1 candidate; P1 `PRIOR_ONLY`, candidate `CANDIDATE_CONDITIONED` and
oracle `ORACLE_CONDITIONED` provenance; operational truth-leak zero; undetected
zero; nonfinite zero; resource-abort zero; disjoint/exhaustive buckets and
sub-buckets; exact disclosures; zero transcript recount mismatch; pre-run
injected wrong-L1 propagation passed) SHALL be persisted as booleans and SHALL
all pass before the candidate label is emitted.  `exact` and divergence counts
SHALL be report-only.  The scope is synthetic only: no Model-F stored file, no
columnar/TT-binary reader, no real data, no N>256, no FWHT/scalable decoder, no
SCL/Phase 7 and no benchmark adapter.

## Requirement: bounded claim

The only permitted candidate conclusion is
`TWO_LAYER_OPERATIONAL_SC_CANDIDATE`: the two-stage causal SC loop, its
isolation, provenance and accounting discipline are internally consistent on
injected synthetic tables.  It SHALL NOT be described as real-data FER,
reconciliation, leakage, key rate, `f<=1.3`, qualification or promotion
evidence.  An independent Pre-EXECUTE review SHALL pass before the single
claim-bearing run, and an independent Pre-RESULT review SHALL pass before any
result or candidate label is published; neither the run nor the implementing
session may accept its own work.
