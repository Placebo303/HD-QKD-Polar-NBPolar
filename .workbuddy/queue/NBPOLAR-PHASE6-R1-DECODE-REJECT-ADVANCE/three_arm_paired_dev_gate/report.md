# NB-Polar Phase 6-R1 decode-reject-advance — three-arm synthetic development gate

- protocol: `nbpolar-decode-reject-advance-protocol` (mode `three-arm-paired-dev-gate`)
- run seed: `2026091350`; planned blocks: 300
- point: q=32, N=256, epsilon=0.05
- nested K: [29, 33, 37, 41, 45]; static comparator K: 45
- wall: 16.595318 s; peak RSS: 114622464 bytes

## Outcomes (disjoint, exhaustive; static | strict-stop | R1)

| bucket | static | strict-stop | r1 |
|---|---|---|---|
| exact | 298 | 280 | 298 |
| undetected | 0 | 0 | 0 |
| verify_failed | 0 | 0 | 0 |
| decode_failed | 2 | 20 | 2 |
| resource_abort | 0 | 0 | 0 |

- attempted: static 300 (coverage 1.0); strict-stop 300 (coverage 1.0); r1 300 (coverage 1.0)
- tag invocations: static 298; strict-stop 314; r1 333
- key-dependent bits total: static 86572; strict-stop 64276; r1 66152
- average key-dependent bits per attempted block: static 288.573333333; strict-stop 214.253333333; r1 220.506666667
- 5% integer rule vs static: 6615200 <= 8224340 (saving fraction 0.235873031)
- R1 rejections: 32 across 20 blocks; rejected-level histogram {'0': 20, '1': 7, '2': 3, '3': 2}
- paired identities vs strict-stop: rescued 18, persisted 282, regressed 0, other 0
- public control: 2478836 bits (static seed 781654; strict-stop seed 823622; r1 seed 873459; r1 feedback 67)
- verification union bound (total): 5.1228552649940085e-17 over 945 tag invocations
- transcript mismatch counts: static 0; strict-stop 0; r1 0
- truth-leak violations: {'static': 0, 'strict_stop': 0, 'r1': 0}; nonfinite: {'static': 0, 'strict_stop': 0, 'r1': 0}

## One-sided 95% Wilson lower bound (exact recovery)

- static: 298/300 -> 0.9800565738801275
- strict-stop: 280/300 -> 0.9055618244501542
- r1: 298/300 -> 0.9800565738801275

## Hard gates

| gate | result |
|---|---|
| frozen_plan_identity | True |
| three_arm_identical_blocks | True |
| outcome_buckets_disjoint_exhaustive_all_arms | True |
| coverage_complete_all_arms | True |
| r1_undetected_zero | True |
| r1_exact_ge_285 | True |
| r1_wilson_lower_ge_0_90 | True |
| r1_avg_key_dependent_le_95pct_static | True |
| frozen_order_nesting_and_schedule_consistency | True |
| invocation_universe_equals_recount_all_arms | True |
| union_bound_consistent | True |
| recount_zero_mismatch | True |
| truth_leak_zero | True |
| nonfinite_zero | True |
| resource_stop_preregistered | True |
| feedback_counted | True |
| public_control_counted | True |
| strict_arm_pinned_consistency | True |

- candidate label: `DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE`

**Scope:** synthetic paired development signal only; this is not real-data FER, leakage efficiency, key rate, qualification or promotion evidence.
