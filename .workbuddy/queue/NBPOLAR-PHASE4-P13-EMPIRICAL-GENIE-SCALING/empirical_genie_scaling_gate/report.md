# NB-Polar Phase 4-P13 target empirical-genie f=1.3 scaling gate

- protocol: `nbpolar-p13-target-empirical-genie-scaling-gate` (mode `target-population-empirical-genie-scaling-gate`)
- source/target: `1M`; q=32, target_f=1.3, chunk_rows=512
- N values: [4096, 8192, 16384]; TRAIN streams/blocks per stream: 2 each; DEV: 8 each
- wall: 496.580679 s; peak RSS: 301961216 bytes; resource stop fired: False

## Target population contract

- H1: 0.024280546818678802 (expected 0.02428054681872374)
- H2: 0.7767572780789994 (expected 0.7767572780789994)
- total: 0.8010378248976782 (expected 0.8010378248977232)
- floored-table total: 0.8010378249492791; floor-induced change: 5.1600945738528026e-11
- column deviation: 1.1357581541915351e-13; p_b sum: 1.0

## Per-N construction and DEV genie residuals (proxy, not FER)

| N | K_total | K1 | K2 | TRAIN residual | emp mean | emp std | emp min | emp max | emp UCB | bec mean | bec UCB | emp-minus-bec mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4096 | 840 | 38 | 802 | 0.10927696273202786 | 0.827698743150655 | 0.4156658929058898 | 0.11514359942895647 | 1.7636954144631765 | 0.9522855359820204 | 18.631744135001654 | 19.650591422865244 | -17.804045391850998 |
| 8192 | 1693 | 78 | 1615 | 0.005622605905980432 | 0.39684042554673166 | 0.2972785735520714 | 0.003468452776927977 | 1.264753487350557 | 0.4859431994053538 | 33.207758990009765 | 34.646718795027105 | -32.81091856446303 |
| 16384 | 3399 | 152 | 3247 | 9.123285118244062e-05 | 0.1932197376646005 | 0.19774453910014764 | 0.004172203043802836 | 0.7382396685293214 | 0.2524893538319819 | 57.155382700913776 | 58.580859237207626 | -56.96216296324918 |

## Per-N resources

| N | wall_s | rss_hwm | VmPeak_kB | VmSize_kB |
|---|---|---|---|---|
| 4096 | 65.04243 | 244137984 | 470620 | 440156 |
| 8192 | 139.731162 | 244137984 | 470620 | 442716 |
| 16384 | 291.806806 | 301961216 | 525660 | 486108 |

## Integrity gates

| gate | result |
|---|---|
| target_population_contract | True |
| three_n_cells_complete | True |
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

- outcome label: `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED`
- smallest candidate N: None

**Scope:** frozen V25 TRAIN target-population empirical-genie construction/rate development signal only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; BEC results and empirical-minus-BEC differences are report-only; undetected has no meaning in this tag-free gate and no success bucket exists.
