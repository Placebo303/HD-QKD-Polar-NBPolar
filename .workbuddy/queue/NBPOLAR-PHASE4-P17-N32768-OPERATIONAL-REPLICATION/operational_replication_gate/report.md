# NB-Polar Phase 4-P17 N=32768 operational replication of the P16 f=1.3 gate

- protocol: `nbpolar-p17-operational-replication-gate` (mode `operational-replication-gate`)
- source/target: `1M`; q=32, n=32768, K1=319, K2=6492, chunk_rows=512, tag_bits=64
- DEV streams x blocks: 16 each (128 blocks, fresh relative to P16)
- wall: 2031.385216 s; peak RSS: 569614336 bytes; resource stop fired: False

## Target population contract

- H1: 0.024280546818678802 (expected 0.02428054681872374)
- H2: 0.7767572780789994 (expected 0.7767572780789994)
- total: 0.8010378248976782 (expected 0.8010378248977232)
- floored-table total: 0.8010378249492791; floor-induced change: 5.1600945738528026e-11
- column deviation: 1.1357581541915351e-13; p_b sum: 1.0

## Predecessor construction identity (verified before any attempt)

- P16 file: `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
- canonical digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` (match: True)
- N=32768, K_total=6811, K1=319, K2=6492
- leakage bits: 34119; f: 1.2998502888172847 (<= 1.3 required)

## Predecessor context (report-only; never pooled into the decision)

- P16 DEV: 62/64 exact, Wilson LB 0.9098711859 (zero-count margin).
- These P16 observations contribute zero weight to the gates below; the decision uses exactly the 128 P17 blocks.

## DEV operational outcomes (128 P17 blocks)

| outcome | count |
|---|---|
| exact | 123 |
| undetected | 0 |
| verify_failed | 5 |
| decode_failed | 0 |
| nonfinite | 0 |
| resource_abort | 0 |

- exact fraction: 123/128 = 0.9609375
- one-sided 95% Wilson LB: 0.921934049951655 (>= 0.90 required; 121/128 boundary 0.902108476, 120/128 boundary 0.8924595822)

## Disclosure and verification accounting

- key-dependent bits: 4367232
- public control bits: 41951104
- tag invocations: 128
- transcript recount mismatches: []

## Integrity gates

| gate | result |
|---|---|
| predecessor_construction_identity | True |
| target_population_contract | True |
| construction_frozen_before_dev | True |
| dev_coverage_complete | True |
| streams_disjoint_frozen | True |
| orders_valid_k_replay_f_within_budget | True |
| buckets_disjoint_exhaustive | True |
| truth_isolation | True |
| undetected_zero | True |
| nonfinite_zero | True |
| no_unregistered_calls | True |
| disclosure_recount_exact | True |
| attempt_read_accounting_exact | True |
| resource_limits_met_and_no_abort | True |

- outcome label: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`

**Scope:** frozen V25 1M-population operational replication development signal at N=32768 only, sampled from the model; P16 blocks are report-only context and contribute zero observations to this decision; not held-out or real frame FER, efficiency, key rate, scaling superiority, qualification or promotion; planning f is not real-channel efficiency; undetected is never success.
