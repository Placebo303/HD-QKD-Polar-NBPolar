# P3 Stage B empirical-prior SC interface diagnostic

- seed: 2026091316
- artifact attempt consumed at write: 1
- wall_s: 17.645

## B1 tiny oracle gates

| case | executed | exact | oracle rows | max prob err | max log err | support mismatch | numeric fail | truth leak | gates |
|---|---|---|---|---|---|---|---|---|---|
| B1_N2 | 64/64 | 8 | 128 | 1.110e-15 | 2.220e-15 | 0 | 0 | 0 | PASS |
| B1_N4 | 64/64 | 1 | 256 | 7.772e-16 | 5.329e-15 | 0 | 0 | 0 | PASS |

## B2/B3 disclosure-shape matrix

| case | mask | disclosed | planned | executed | exact | impossible | other | nonfinite | initial MAP err | wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| B2_N16_M1_all_but_one | M1_all_but_one | 15 | 16 | 16 | 15 | 0 | 1 | 0 | - | 0.080 |
| B2_N16_M2_prefix | M2_prefix | 8 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.080 |
| B2_N16_M3_suffix | M3_suffix | 8 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.081 |
| B2_N16_M4_alternating | M4_alternating | 8 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.079 |
| B2_N16_M5_construction_order | M5_construction_order | 8 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.080 |
| B2_N64_M1_all_but_one | M1_all_but_one | 63 | 16 | 16 | 16 | 0 | 0 | 0 | - | 0.257 |
| B2_N64_M2_prefix | M2_prefix | 32 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.261 |
| B2_N64_M3_suffix | M3_suffix | 32 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.271 |
| B2_N64_M4_alternating | M4_alternating | 32 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.267 |
| B2_N64_M5_construction_order | M5_construction_order | 32 | 16 | 16 | 0 | 0 | 16 | 0 | - | 0.263 |
| B3_N256_M1_all_but_one | M1_all_but_one | 255 | 8 | 8 | 8 | 0 | 0 | 0 | 8 | 0.572 |
| B3_N256_M2_prefix | M2_prefix | 128 | 8 | 8 | 0 | 0 | 8 | 0 | 8 | 0.578 |
| B3_N256_M3_suffix | M3_suffix | 128 | 8 | 8 | 0 | 0 | 8 | 0 | 8 | 0.592 |
| B3_N256_M4_alternating | M4_alternating | 128 | 8 | 8 | 0 | 0 | 8 | 0 | 8 | 0.572 |
| B3_N256_M5_construction_order | M5_construction_order | 128 | 8 | 8 | 0 | 0 | 8 | 0 | 8 | 0.575 |

B2 totals: exact=31 impossible=0 other=129 nonfinite=0 resource_abort=0
B3 totals: exact=8 impossible=0 other=32 nonfinite=0 initial_map_err=40 resource_abort=0

## B5 earliest-layer attribution (non-exact executed blocks)

| category | count |
|---|---|
| artifact_adapter_support | 0 |
| normalization | 0 |
| disclosure_contradiction | 0 |
| SC_numeric | 0 |
| SC_decision | 119 |
| expected_under_disclosure | 161 |
| unattributed | 0 |

## B4 resource profile (median of >=5 measured calls after warm-up)

| N | metric median s | decode median s | metric batch shape | metric shape | decision shape | peak RSS GiB | complete |
|---|---|---|---|---|---|---|---|
| 64 | 3.799899423029274e-05 | 0.007757172992569394 | [4, 64, 32] | [64, 32] | [64, 32] | 0.23288726806640625 | True |
| 256 | 4.309399810153991e-05 | 0.03448710800148547 | [4, 256, 32] | [256, 32] | [256, 32] | 0.23288726806640625 | True |
| 1024 | 0.00011792199802584946 | 0.16753002499171998 | [4, 1024, 32] | [1024, 32] | [1024, 32] | 0.23288726806640625 | True |

## Hard gates

- `hard_gates_pass`: True
- `truth_leak_violations`: 0
- `resource_abort_blocks`: 0
- `candidate_conclusion`: EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE

Candidate label only: acceptance is owned by the main thread and an independent Pre-RESULT review. This is not real-data FER, reconciliation, leakage, key rate or construction/K evidence.
