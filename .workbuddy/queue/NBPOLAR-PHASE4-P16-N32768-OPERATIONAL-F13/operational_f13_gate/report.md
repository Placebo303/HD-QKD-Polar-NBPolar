# NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 gate

- protocol: `nbpolar-p16-operational-f13-gate` (mode `empirical-construction-operational-f13-gate`)
- source/target: `1M`; q=32, n=32768, target_f=1.3, chunk_rows=512, tag_bits=64
- TRAIN streams x blocks: 4 each (16 blocks); DEV: 8 each (64 blocks)
- wall: 1183.61887 s; peak RSS: 545861632 bytes; resource stop fired: False

## Target population contract

- H1: 0.024280546818678802 (expected 0.02428054681872374)
- H2: 0.7767572780789994 (expected 0.7767572780789994)
- total: 0.8010378248976782 (expected 0.8010378248977232)
- floored-table total: 0.8010378249492791; floor-induced change: 5.1600945738528026e-11
- column deviation: 1.1357581541915351e-13; p_b sum: 1.0

## Construction and allocation (frozen before DEV)

- K_total: 6811 (floor((1.3*N*H-64)/5) = floor(6811.785936024251) = 6811)
- split: K1=319, K2=6492; TRAIN residual: 5.87097048643237e-07
- leakage bits: 34119 (5*K_total+64); f: 1.2998502888173578 (<= 1.3 required)
- freeze digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`

## DEV operational outcomes (64 blocks)

| outcome | count |
|---|---|
| exact | 62 |
| undetected | 0 |
| verify_failed | 2 |
| decode_failed | 0 |
| nonfinite | 0 |
| resource_abort | 0 |

- exact fraction: 62/64 = 0.96875
- one-sided 95% Wilson LB: 0.9098711859061207 (>= 0.90 required; 62/64 boundary 0.9098711859, 61/64 boundary 0.8883797144)

## Disclosure and verification accounting

- key-dependent bits: 2183616
- public control bits: 20975552
- tag invocations: 64
- transcript recount mismatches: []

## Integrity gates

| gate | result |
|---|---|
| target_population_contract | True |
| construction_frozen_before_dev | True |
| train_dev_coverage_complete | True |
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

- outcome label: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE`

**Scope:** frozen V25 TRAIN target-population empirical-construction operational development signal at N=32768 only, sampled from the model; not held-out or real frame FER, efficiency, key rate, scaling superiority, qualification or promotion; planning f is not real-channel efficiency; undetected is never success.
