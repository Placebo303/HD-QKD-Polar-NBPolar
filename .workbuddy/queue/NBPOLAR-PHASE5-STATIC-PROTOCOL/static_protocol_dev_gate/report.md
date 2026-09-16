# NB-Polar Phase 5 static protocol — synthetic development gate

- protocol: `nbpolar-static-protocol` (mode `dev-gate`)
- run seed: `2026091317`; planned blocks: 300
- point: q=32, N=256, K=45, epsilon=0.05
- wall: 4.998916 s; peak RSS: 111190016 bytes

## Outcomes (disjoint, exhaustive)

| bucket | count |
|---|---|
| exact | 300 |
| undetected | 0 |
| verify_failed | 0 |
| decode_failed | 0 |
| resource_abort | 0 |

- attempted: 300 (coverage 1.0)
- verified union (exact + undetected): 300
- verification invocations: 300
- key-dependent bits total: 86700; public control bits total: 786900
- average key-dependent bits per attempted block: 289.0
- transcript recount mismatch count: 0
- truth-leak violations: 0; nonfinite: 0

## One-sided 95% Wilson lower bound (exact recovery)

- successes/denominator: 300/300
- z: 1.6448536269514722
- lower bound: 0.9910621278248719

## Hard gates

| gate | result |
|---|---|
| outcome_accounting_disjoint_exhaustive | True |
| coverage_complete | True |
| resource_stop_preregistered | True |
| per_block_disclosure_consistent | True |
| verification_universe_consistent | True |
| recount_zero_mismatch | True |
| undetected_zero | True |
| truth_leak_zero | True |
| nonfinite_zero | True |
| wilson_lower_ge_0_90 | True |
| avg_key_dependent_below_input_bits | True |

- candidate label: `STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE`

**Scope:** synthetic development signal only; this is not real-data FER, leakage efficiency, key rate, qualification or promotion evidence.
