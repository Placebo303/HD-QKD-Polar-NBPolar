# NB-Polar Phase 4-P15 empirical-genie mid-N scaling gate

- protocol: `nbpolar-p15-empirical-genie-mid-n-scaling-gate` (mode `target-population-empirical-genie-mid-n-scaling-gate`)
- source/target: `1M`; q=32, target_f=1.3, chunk_rows=512
- N values: [32768, 65536]; TRAIN streams/blocks per stream: 4 each; DEV: 4 each
- genie calls: 128/128; wall: 1620.511243 s; peak RSS: 1033293824 bytes; resource stop fired: False

## Target population contract

- H1: 0.024280546818678802 (expected 0.02428054681872374)
- H2: 0.7767572780789994 (expected 0.7767572780789994)
- total: 0.8010378248976782 (expected 0.8010378248977232)
- floored-table total: 0.8010378249492791; floor-induced change: 5.1600945738528026e-11
- column deviation: 1.1357581541915351e-13; p_b sum: 1.0

## Per-N construction and DEV genie residuals (proxy, not FER)

| N | K_total | K1 | K2 | TRAIN residual | mean | std | min | max | UCB |
|---|---|---|---|---|---|---|---|---|---|
| 32768 | 6811 | 314 | 6497 | 1.1128237904570182e-06 | 0.019146193040229846 | 0.03822701382375279 | 4.452207734151337e-06 | 0.1247046397723417 | 0.035899663088366535 |
| 65536 | 13636 | 607 | 13029 | 1.1015630768662632e-10 | 0.028768524223564552 | 0.10806211430369776 | 2.4939197373896604e-09 | 0.43377941496412364 | 0.07612810621111707 |

## Per-N resources

| N | wall_s | rss_hwm | VmPeak_kB | VmSize_kB |
|---|---|---|---|---|
| 32768 | 569.717255 | 593866752 | 811928 | 693720 |
| 65536 | 1050.793743 | 1033293824 | 1241560 | 1025752 |

## Integrity gates

| gate | result |
|---|---|
| target_population_contract | True |
| two_n_cells_complete | True |
| streams_disjoint_frozen | True |
| orders_valid_frozen_before_dev | True |
| budget_allocation_reproduced | True |
| risks_finite | True |
| zero_genie_exceptions | True |
| truth_isolation | True |
| no_unregistered_calls | True |
| checkpoint_accounting_consistent | True |
| attempt_read_accounting_exact | True |
| resource_limits_met_and_no_abort | True |

- outcome label: `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED`
- smallest candidate N: None

**Scope:** frozen V25 TRAIN target-population empirical-genie mid-N construction/rate development signal only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; the UCB is a genie construction proxy, not an FER threshold or proof of any minimum N; undetected has no meaning in this tag-free gate and no success bucket exists.
