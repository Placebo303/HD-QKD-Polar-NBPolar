# NB-Polar Phase 6 fixed incremental — paired synthetic development gate

- protocol: `nbpolar-incremental-protocol` (mode `paired-dev-gate`)
- run seed: `2026091340`; planned blocks: 300
- point: q=32, N=256, epsilon=0.05
- nested K: [29, 33, 37, 41, 45]; static comparator K: 45
- wall: 9.619874 s; peak RSS: 111816704 bytes

## Outcomes (disjoint, exhaustive; static | incremental)

| bucket | static | incremental |
|---|---|---|
| exact | 298 | 271 |
| undetected | 0 | 0 |
| verify_failed | 0 | 0 |
| decode_failed | 2 | 29 |
| resource_abort | 0 | 0 |

- attempted: static 300 (coverage 1.0); incremental 300 (coverage 1.0)
- tag invocations: static 298; incremental 287
- key-dependent bits total: static 86572; incremental 62188
- average key-dependent bits per attempted block: static 288.573333333; incremental 207.293333333
- 5% integer rule: 6218800 <= 8224340 (saving fraction 0.281661507)
- public control: 1534471 bits (static seed 781654; incremental seed 752801; feedback 16)
- verification union bound (total): 3.1712913545201005e-17 over 585 tag invocations
- transcript mismatch counts: static 0; incremental 0
- truth-leak violations: {'static': 0, 'incremental': 0}; nonfinite: {'static': 0, 'incremental': 0}

## One-sided 95% Wilson lower bound (exact recovery)

- static: 298/300 -> 0.9800565738801275
- incremental: 271/300 -> 0.8715597837542944

## Hard gates

| gate | result |
|---|---|
| frozen_plan_identity | True |
| paired_identical_blocks | True |
| outcome_buckets_disjoint_exhaustive_both_arms | True |
| paired_coverage_complete | True |
| incremental_undetected_zero | True |
| incremental_exact_ge_285 | False |
| incremental_wilson_lower_ge_0_90 | False |
| equal_attempted_denominators | True |
| incremental_avg_key_dependent_le_95pct_static | True |
| frozen_order_nesting_and_schedule_consistency | True |
| invocation_universe_equals_recount_both_arms | True |
| union_bound_consistent | True |
| recount_zero_mismatch | True |
| truth_leak_zero | True |
| nonfinite_zero | True |
| resource_stop_preregistered | True |
| feedback_control_counted | True |
| public_control_counted | True |

- candidate label: `None`

**Scope:** synthetic paired development signal only; this is not real-data FER, leakage efficiency, key rate, qualification or promotion evidence.
