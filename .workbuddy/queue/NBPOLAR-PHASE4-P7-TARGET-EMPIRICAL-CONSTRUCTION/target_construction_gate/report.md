# NB-Polar Phase 4-P7 target-population empirical construction gate

- protocol: `nbpolar-p7-target-empirical-construction-gate` (mode `paired-target-population-dev-gate`)
- source/target: `1M`; q=32, N=256, K1=45, K2=140, floor=1e-15
- TRAIN: [2026091650, 2026091651, 2026091652] x 256 blocks; DEV: [2026091660, 2026091661, 2026091662, 2026091663, 2026091664] x 128 = 640 paired blocks
- wall: 132.523651 s; peak RSS: 383832064 bytes; resource stop fired: False

## Target population contract

- H1: 0.024280546818678802 (expected 0.02428054681872374)
- H2: 0.7767572780789994 (expected 0.7767572780789994)
- total: 0.8010378248976782 (expected 0.8010378248977232)
- floored-table total: 0.8010378249492791; floor-induced change: 5.1600945738528026e-11
- column deviation: 1.1357581541915351e-13; p_b sum: 1.0
- BEC control epsilons: 0.00485610936373576 / 0.15535145561579988 (report-only)

## Construction stability (minimum pairwise TRAIN-order Spearman)

- L1: 0.9973291943236439; L2: 0.9950453479056992

## Paired DEV results

| cell | count |
|---|---|
| both_exact | 640 |
| empirical_only | 0 |
| bec_only | 0 |
| neither | 0 |

- empirical exact: 640/640; BEC exact: 640/640; one-sided 95% Wilson lower bound: 0.9957903841321254

## Integrity gates

| gate | result |
|---|---|
| target_population_contract | True |
| coverage_complete_and_disjoint | True |
| orders_frozen_permutations_provenance | True |
| pairing_and_buckets | True |
| truth_leak_zero | True |
| undetected_zero | True |
| nonfinite_zero | True |
| resource_abort_zero | True |
| disclosure_and_recount_exact | True |
| attempt_read_accounting_exact | True |
| resource_limits_met | True |

## Scientific gates

| gate | result |
|---|---|
| train_spearman_min_at_least_0p95 | True |
| empirical_exact_at_least_620_of_640 | True |
| empirical_wilson_lower_bound_at_least_0p95 | True |

## Disclosure accounting

- fully invoked arm: 989 key-dependent bits (L1 225 + L2 700 + tag 64); public control 2623 bits per tag
- key-dependent total: 1265920; public total: 3357440; tags: 1280
- recount mismatch count: 0

## Planning-only f

- leakage 989 bits / nH 205.0656831738056 = f 4.8228449767568495 (planning-only; not real-channel efficiency)

- outcome label: `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`

**Scope:** frozen V25 TRAIN target-population empirical construction development signal at N=256 only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; planning-only f is not real-channel efficiency; undetected is never success.
