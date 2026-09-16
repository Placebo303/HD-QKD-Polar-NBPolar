# NB-Polar Phase 4-P9 lower-rate boundary SCREEN -> CONFIRM gate

- protocol: `nbpolar-p9-lower-rate-boundary-screen-confirm` (mode `static-lower-rate-boundary-screen-confirm`)
- source/target: `1M`; q=32, N=256, floor=1e-15
- SCREEN: [2026091710, 2026091711, 2026091712] x 64 blocks = 192 shared blocks x 56 configs
- CONFIRM: [2026091720, 2026091721, 2026091722, 2026091723, 2026091724] x 128 blocks
- orders: `p7_file` sha `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`
- wall: 720.522313 s; peak RSS: 318406656 bytes; resource stop fired: False

## SCREEN grid (56 configurations)

| k1 | k2 | exact/192 | wilson_lb | count_188 | eligible |
|---|---|---|---|---|---|
| 0 | 0 | 0/192 | 0.0 | False | False |
| 0 | 20 | 0/192 | 0.0 | False | False |
| 0 | 40 | 0/192 | 0.0 | False | False |
| 0 | 50 | 11/192 | 0.03536607429071025 | False | False |
| 0 | 60 | 26/192 | 0.09983126360541061 | False | False |
| 0 | 70 | 29/192 | 0.1134016513968186 | False | False |
| 0 | 80 | 29/192 | 0.1134016513968186 | False | False |
| 2 | 0 | 0/192 | 0.0 | False | False |
| 2 | 20 | 0/192 | 0.0 | False | False |
| 2 | 40 | 3/192 | 0.006261330807758174 | False | False |
| 2 | 50 | 64/192 | 0.28003211627664304 | False | False |
| 2 | 60 | 136/192 | 0.6517805677306815 | False | False |
| 2 | 70 | 145/192 | 0.7008542842272918 | False | False |
| 2 | 80 | 145/192 | 0.7008542842272918 | False | False |
| 4 | 0 | 0/192 | 0.0 | False | False |
| 4 | 20 | 0/192 | 0.0 | False | False |
| 4 | 40 | 5/192 | 0.012732499159924415 | False | False |
| 4 | 50 | 80/192 | 0.35969774288673123 | False | False |
| 4 | 60 | 166/192 | 0.8188657477622883 | False | False |
| 4 | 70 | 176/192 | 0.8777862340385935 | False | False |
| 4 | 80 | 176/192 | 0.8777862340385935 | False | False |
| 6 | 0 | 0/192 | 0.0 | False | False |
| 6 | 20 | 0/192 | 0.0 | False | False |
| 6 | 40 | 5/192 | 0.012732499159924415 | False | False |
| 6 | 50 | 85/192 | 0.38494749509200016 | False | False |
| 6 | 60 | 176/192 | 0.8777862340385935 | False | False |
| 6 | 70 | 188/192 | 0.9544033287216636 | True | True |
| 6 | 80 | 188/192 | 0.9544033287216636 | True | True |
| 8 | 0 | 0/192 | 0.0 | False | False |
| 8 | 20 | 0/192 | 0.0 | False | False |
| 8 | 40 | 5/192 | 0.012732499159924415 | False | False |
| 8 | 50 | 86/192 | 0.39001684244089363 | False | False |
| 8 | 60 | 180/192 | 0.9022461940723889 | False | False |
| 8 | 70 | 192/192 | 0.9861044354151461 | True | True |
| 8 | 80 | 192/192 | 0.9861044354151461 | True | True |
| 12 | 0 | 0/192 | 0.0 | False | False |
| 12 | 20 | 0/192 | 0.0 | False | False |
| 12 | 40 | 5/192 | 0.012732499159924415 | False | False |
| 12 | 50 | 86/192 | 0.39001684244089363 | False | False |
| 12 | 60 | 180/192 | 0.9022461940723889 | False | False |
| 12 | 70 | 192/192 | 0.9861044354151461 | True | True |
| 12 | 80 | 192/192 | 0.9861044354151461 | True | True |
| 24 | 0 | 0/192 | 0.0 | False | False |
| 24 | 20 | 0/192 | 0.0 | False | False |
| 24 | 40 | 5/192 | 0.012732499159924415 | False | False |
| 24 | 50 | 86/192 | 0.39001684244089363 | False | False |
| 24 | 60 | 180/192 | 0.9022461940723889 | False | False |
| 24 | 70 | 192/192 | 0.9861044354151461 | True | True |
| 24 | 80 | 192/192 | 0.9861044354151461 | True | True |
| 45 | 0 | 0/192 | 0.0 | False | False |
| 45 | 20 | 0/192 | 0.0 | False | False |
| 45 | 40 | 5/192 | 0.012732499159924415 | False | False |
| 45 | 50 | 86/192 | 0.39001684244089363 | False | False |
| 45 | 60 | 180/192 | 0.9022461940723889 | False | False |
| 45 | 70 | 192/192 | 0.9861044354151461 | True | True |
| 45 | 80 | 192/192 | 0.9861044354151461 | True | True |

## Deterministic selection

- eligible points: [{'k1': 6, 'k2': 70, 'exact': 188}, {'k1': 6, 'k2': 80, 'exact': 188}, {'k1': 8, 'k2': 70, 'exact': 192}, {'k1': 8, 'k2': 80, 'exact': 192}, {'k1': 12, 'k2': 70, 'exact': 192}, {'k1': 12, 'k2': 80, 'exact': 192}, {'k1': 24, 'k2': 70, 'exact': 192}, {'k1': 24, 'k2': 80, 'exact': 192}, {'k1': 45, 'k2': 70, 'exact': 192}, {'k1': 45, 'k2': 80, 'exact': 192}]
- selected: `{'k1': 6, 'k2': 70}`
- rule: lexicographic minimum of (K1+K2, K1, K2) over eligible points only

## CONFIRM (selected point + paired BEC control)

- point: K1=6, K2=70
- empirical exact: 624/640; BEC exact: 520/640
- one-sided 95% Wilson lower bound: 0.9626753340557015; count rule 618/640: True
- paired cells: {'both_exact': 520, 'empirical_only': 104, 'bec_only': 0, 'neither': 16}

### CONFIRM per-stream (5x128)

| stream | records | empirical_exact | bec_exact |
|---|---|---|---|
| 2026091720 | 128 | 122 | 103 |
| 2026091721 | 128 | 123 | 102 |
| 2026091722 | 128 | 125 | 97 |
| 2026091723 | 128 | 127 | 108 |
| 2026091724 | 128 | 127 | 110 |

## Integrity gates

| gate | result |
|---|---|
| orders_identity_and_permutations | True |
| target_population_contract | True |
| coverage_complete_and_disjoint | True |
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
| confirm_empirical_exact_at_least_618_of_640 | True |
| confirm_empirical_wilson_lower_bound_at_least_0p95 | True |

## Disclosure accounting

- fully invoked point: `5*(K1+K2)+64 key-dependent bits per fully invoked point`; public control 2623 bits per tag
- selected-point leakage: 444 key-dependent bits
- key-dependent total: 4392768; public total: 31559936; tags: 12032
- recount mismatch count: 0

## Planning-only f

- mean key-dependent 444.0 bits / nH 205.0656831738056 = f 2.165159928897918 (planning-only; not real-channel efficiency)

- outcome label: `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE`

**Scope:** frozen V25 TRAIN target-population static rate development signal at N=256 only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; planning-only f is not real-channel efficiency; undetected is never success.
