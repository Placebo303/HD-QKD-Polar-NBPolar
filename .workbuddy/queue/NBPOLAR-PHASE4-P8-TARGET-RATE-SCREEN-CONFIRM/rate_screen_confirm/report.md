# NB-Polar Phase 4-P8 target rate SCREEN -> CONFIRM gate

- protocol: `nbpolar-p8-target-rate-screen-confirm` (mode `static-target-rate-screen-confirm`)
- source/target: `1M`; q=32, N=256, floor=1e-15
- SCREEN: [2026091680, 2026091681, 2026091682] x 64 blocks = 192 shared blocks x 35 configs
- CONFIRM: [2026091690, 2026091691, 2026091692, 2026091693, 2026091694] x 128 blocks
- orders: `p7_file` sha `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`
- wall: 522.26697 s; peak RSS: 274264064 bytes; resource stop fired: False

## SCREEN grid (35 configurations)

| k1 | k2 | exact/192 | wilson_lb | count_188 | eligible |
|---|---|---|---|---|---|
| 8 | 80 | 189/192 | 0.9615500026161811 | True | True |
| 8 | 94 | 190/192 | 0.9690137061775033 | True | True |
| 8 | 110 | 190/192 | 0.9690137061775033 | True | True |
| 8 | 125 | 190/192 | 0.9690137061775033 | True | True |
| 8 | 140 | 190/192 | 0.9690137061775033 | True | True |
| 10 | 80 | 191/192 | 0.9769953117481123 | True | True |
| 10 | 94 | 192/192 | 0.9861044354151461 | True | True |
| 10 | 110 | 192/192 | 0.9861044354151461 | True | True |
| 10 | 125 | 192/192 | 0.9861044354151461 | True | True |
| 10 | 140 | 192/192 | 0.9861044354151461 | True | True |
| 12 | 80 | 191/192 | 0.9769953117481123 | True | True |
| 12 | 94 | 192/192 | 0.9861044354151461 | True | True |
| 12 | 110 | 192/192 | 0.9861044354151461 | True | True |
| 12 | 125 | 192/192 | 0.9861044354151461 | True | True |
| 12 | 140 | 192/192 | 0.9861044354151461 | True | True |
| 16 | 80 | 191/192 | 0.9769953117481123 | True | True |
| 16 | 94 | 192/192 | 0.9861044354151461 | True | True |
| 16 | 110 | 192/192 | 0.9861044354151461 | True | True |
| 16 | 125 | 192/192 | 0.9861044354151461 | True | True |
| 16 | 140 | 192/192 | 0.9861044354151461 | True | True |
| 24 | 80 | 191/192 | 0.9769953117481123 | True | True |
| 24 | 94 | 192/192 | 0.9861044354151461 | True | True |
| 24 | 110 | 192/192 | 0.9861044354151461 | True | True |
| 24 | 125 | 192/192 | 0.9861044354151461 | True | True |
| 24 | 140 | 192/192 | 0.9861044354151461 | True | True |
| 32 | 80 | 191/192 | 0.9769953117481123 | True | True |
| 32 | 94 | 192/192 | 0.9861044354151461 | True | True |
| 32 | 110 | 192/192 | 0.9861044354151461 | True | True |
| 32 | 125 | 192/192 | 0.9861044354151461 | True | True |
| 32 | 140 | 192/192 | 0.9861044354151461 | True | True |
| 45 | 80 | 191/192 | 0.9769953117481123 | True | True |
| 45 | 94 | 192/192 | 0.9861044354151461 | True | True |
| 45 | 110 | 192/192 | 0.9861044354151461 | True | True |
| 45 | 125 | 192/192 | 0.9861044354151461 | True | True |
| 45 | 140 | 192/192 | 0.9861044354151461 | True | True |

## Deterministic selection

- eligible points: [{'k1': 8, 'k2': 80, 'exact': 189}, {'k1': 8, 'k2': 94, 'exact': 190}, {'k1': 8, 'k2': 110, 'exact': 190}, {'k1': 8, 'k2': 125, 'exact': 190}, {'k1': 8, 'k2': 140, 'exact': 190}, {'k1': 10, 'k2': 80, 'exact': 191}, {'k1': 10, 'k2': 94, 'exact': 192}, {'k1': 10, 'k2': 110, 'exact': 192}, {'k1': 10, 'k2': 125, 'exact': 192}, {'k1': 10, 'k2': 140, 'exact': 192}, {'k1': 12, 'k2': 80, 'exact': 191}, {'k1': 12, 'k2': 94, 'exact': 192}, {'k1': 12, 'k2': 110, 'exact': 192}, {'k1': 12, 'k2': 125, 'exact': 192}, {'k1': 12, 'k2': 140, 'exact': 192}, {'k1': 16, 'k2': 80, 'exact': 191}, {'k1': 16, 'k2': 94, 'exact': 192}, {'k1': 16, 'k2': 110, 'exact': 192}, {'k1': 16, 'k2': 125, 'exact': 192}, {'k1': 16, 'k2': 140, 'exact': 192}, {'k1': 24, 'k2': 80, 'exact': 191}, {'k1': 24, 'k2': 94, 'exact': 192}, {'k1': 24, 'k2': 110, 'exact': 192}, {'k1': 24, 'k2': 125, 'exact': 192}, {'k1': 24, 'k2': 140, 'exact': 192}, {'k1': 32, 'k2': 80, 'exact': 191}, {'k1': 32, 'k2': 94, 'exact': 192}, {'k1': 32, 'k2': 110, 'exact': 192}, {'k1': 32, 'k2': 125, 'exact': 192}, {'k1': 32, 'k2': 140, 'exact': 192}, {'k1': 45, 'k2': 80, 'exact': 191}, {'k1': 45, 'k2': 94, 'exact': 192}, {'k1': 45, 'k2': 110, 'exact': 192}, {'k1': 45, 'k2': 125, 'exact': 192}, {'k1': 45, 'k2': 140, 'exact': 192}]
- selected: `{'k1': 8, 'k2': 80}`
- rule: lexicographic minimum of (K1+K2, K1, K2) over eligible points only

## CONFIRM (selected point + paired BEC control)

- point: K1=8, K2=80
- empirical exact: 638/640; BEC exact: 621/640
- one-sided 95% Wilson lower bound: 0.9906013676984646; count rule 618/640: True
- paired cells: {'both_exact': 621, 'empirical_only': 17, 'bec_only': 0, 'neither': 2}

### CONFIRM per-stream (5x128)

| stream | records | empirical_exact | bec_exact |
|---|---|---|---|
| 2026091690 | 128 | 127 | 124 |
| 2026091691 | 128 | 128 | 122 |
| 2026091692 | 128 | 128 | 123 |
| 2026091693 | 128 | 128 | 127 |
| 2026091694 | 128 | 127 | 125 |

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
- selected-point leakage: 504 key-dependent bits
- key-dependent total: 5470080; public total: 20984000; tags: 8000
- recount mismatch count: 0

## Planning-only f

- mean key-dependent 504.0 bits / nH 205.0656831738056 = f 2.457749108478718 (planning-only; not real-channel efficiency)

- outcome label: `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE`

**Scope:** frozen V25 TRAIN target-population static rate development signal at N=256 only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; planning-only f is not real-channel efficiency; undetected is never success.
