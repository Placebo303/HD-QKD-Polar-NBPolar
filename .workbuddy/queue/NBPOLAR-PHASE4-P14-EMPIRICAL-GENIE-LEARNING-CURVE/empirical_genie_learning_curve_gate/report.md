# NB-Polar Phase 4-P14 empirical-genie learning curve gate

- protocol: `nbpolar-p14-empirical-genie-learning-curve-gate` (mode `target-population-empirical-genie-learning-curve-gate`)
- source/target: `1M`; q=32, n=16384, target_f=1.3, chunk_rows=512
- TRAIN streams x blocks: 8x16 = 128; DEV: 4x8 = 32; prefixes: [8, 16, 32, 64, 128]
- genie calls: 320/320; wall: 1110.16709 s; peak RSS: 283115520 bytes; resource stop fired: False

## Target population contract

- H1: 0.024280546818678802 (expected 0.02428054681872374)
- H2: 0.7767572780789994 (expected 0.7767572780789994)
- total: 0.8010378248976782 (expected 0.8010378248977232)
- floored-table total: 0.8010378249492791; floor-induced change: 5.1600945738528026e-11
- column deviation: 1.1357581541915351e-13; p_b sum: 1.0

## Per-prefix construction and DEV genie residuals (proxy, not FER)

| B | K1 | K2 | TRAIN residual | mean | std | min | max | UCB |
|---|---|---|---|---|---|---|---|---|
| 8 | 158 | 3241 | 5.3882981160102705e-05 | 0.1175773969604019 | 0.18328617696455765 | 0.00023161951066219544 | 0.6632266438755844 | 0.17251343416734777 |
| 16 | 161 | 3238 | 0.0002739494046524113 | 0.13176399133297984 | 0.18728900823240302 | 0.00015639852900284357 | 0.6981597350727797 | 0.18789978997914214 |
| 32 | 162 | 3237 | 0.0013067725980560572 | 0.1060391737357177 | 0.17563973337252425 | 0.0002421531531953125 | 0.6972184077530478 | 0.15868335611416776 |
| 64 | 162 | 3237 | 0.0036843863984939752 | 0.08983984405791562 | 0.16445710274458678 | 0.0004354717782820705 | 0.8070449161693778 | 0.13913227660764454 |
| 128 | 173 | 3226 | 0.013279461298516686 | 0.1419810706809162 | 0.19735260988460465 | 0.00017760231322272446 | 0.806151592316756 | 0.2011332146072146 |

## Paired differences (mean/std/UCB, report-only except the B=128 rule)

| contrast | mean | std | UCB |
|---|---|---|---|
| R_16_minus_R_8 | 0.014186594372577927 | 0.17294151558954643 | 0.06602204477258328 |
| R_32_minus_R_8 | -0.011538223224684209 | 0.1348726212270291 | 0.028886905721941962 |
| R_64_minus_R_8 | -0.02773755290248629 | 0.11712473187364603 | 0.0073680329885239225 |
| R_128_minus_R_8 | 0.024403673720514288 | 0.16989973009547454 | 0.07532741520801287 |
| R_16_minus_R_8_step | 0.014186594372577927 | 0.17294151558954643 | 0.06602204477258328 |
| R_32_minus_R_16_step | -0.025724817597262136 | 0.1031757123802204 | 0.005199853690245681 |
| R_64_minus_R_32_step | -0.01619932967780208 | 0.08917824709781177 | 0.010529906436730147 |
| R_128_minus_R_64_step | 0.05214122662300058 | 0.12867194063944914 | 0.09070783669434054 |

## Integrity gates

| gate | result |
|---|---|
| target_population_contract | True |
| one_n_cell_complete | True |
| nested_prefixes_exact | True |
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

- outcome label: `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`

**Scope:** frozen V25 TRAIN target-population empirical-genie learning-curve diagnostic at N=16384 only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; other prefixes diagnose learning only; P13 B=8 is a historical reference, never merged and never required equal; undetected has no meaning in this tag-free gate and no success bucket exists.
