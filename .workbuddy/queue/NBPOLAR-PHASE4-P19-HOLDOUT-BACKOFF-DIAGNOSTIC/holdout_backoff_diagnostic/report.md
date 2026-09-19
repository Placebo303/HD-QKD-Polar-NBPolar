# NB-Polar Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic

- protocol: `nbpolar-p19-holdout-backoff-diagnostic` (mode `holdout-backoff-diagnostic`)
- source/target: `1M`; q=32, n=32768, base K1=319, base K2=6492, chunk_rows=512, tag_bits=64
- HOLD frames: [1600, 1999]; blocks: [[1600, 1727], [1728, 1855], [1856, 1983]]; unused remainder: {'frame_start': 1984, 'frame_end': 1999, 'frames': 16, 'symbols': 4096, 'used': False}
- records: 15/15; SC calls: 27/27; tags: 15/15
- wall: 186.421779 s; peak RSS: 615960576 bytes; resource stop fired: False

## Frozen arms (K, leakage, per-block SC calls; no threshold)

| arm | kind | K1 | K2 | leakage bits | SC/block | provenance | exact (of 3) |
|---|---|---|---|---|---|---|---|
| base | operational | 319 | 6492 | 34119 | 2 | OPERATIONAL | 0 |
| l1_plus | operational | 447 | 6492 | 34759 | 2 | OPERATIONAL | 0 |
| l2_plus | operational | 319 | 7004 | 36679 | 2 | OPERATIONAL | 0 |
| both_plus | operational | 447 | 7004 | 37319 | 2 | OPERATIONAL | 0 |
| true_l1_control | oracle_control | 0 | 6492 | 32524 | 1 | ORACLE_TRUE_L1_CONTROL | 0 |

## Descriptive recovery diagnostics (no threshold, no winner)

- ordered operational exact counts: [0, 0, 0, 0]
- first operational recovery arm: None
- ordered exact counts non-monotone: False (reported neutrally: no monotonicity, superiority, winner or threshold claim is made; exact counts are descriptive)

| arm | paired vs base | recovered vs base | lost vs base |
|---|---|---|---|
| l1_plus | {'verify_failed->verify_failed': 3} | 0 | 0 |
| l2_plus | {'verify_failed->verify_failed': 3} | 0 | 0 |
| both_plus | {'verify_failed->verify_failed': 3} | 0 | 0 |

## Oracle control (provenance-isolated; never an operational protocol)

- oracle-labelled true-L1 diagnostic control: never an operational protocol or deployable rate
- control records: 3 (excluded from every operational aggregate); deployable: False

## Disclosure and verification accounting

- operational key-dependent bits: 428628; control key-dependent bits (isolated): 97572
- public control bits: 4916145 (fixed per-tag value 327743)
- transcript recount: {'key_dependent_bits': 526200, 'public_control_bits': 4916145, 'tag_invocations': 15, 'event_types': {'l1_disclosure': 12, 'l2_disclosure': 15, 'verification_tag': 15}}
- transcript recount mismatches: []
- CE-normalized disclosure ratio note: sample cross-entropy-normalized descriptive disclosure ratios, explicitly NOT qualification reconciliation efficiency

## Integrity gates

| gate | result |
|---|---|
| predecessor_construction_identity | True |
| hold_split_manifest_identity | True |
| p18_block_range_identity | True |
| target_population_contract | True |
| hold_population_exact | True |
| blocks_exact_with_declared_remainder | True |
| fifteen_records_exact | True |
| sc_calls_exact | True |
| tags_exact | True |
| orders_valid_k_prefixes_within_registered_arms | True |
| oracle_isolation | True |
| buckets_disjoint_exhaustive | True |
| undetected_zero | True |
| nonfinite_zero | True |
| truth_isolation | True |
| disclosure_recount_exact | True |
| one_open_per_protected_input | True |
| input_stat_unchanged | True |
| no_unregistered_access | True |
| resource_limits_met_and_no_abort | True |

- outcome label: `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`
- recovery threshold: None (none; every 0/3..3/3 recovery pattern is a descriptive COMPLETE)

**Scope:** descriptive real-input layer/backoff diagnostic of the frozen V25 1M HOLD split at N=32768 only (three accepted P18 chronological blocks, frames 1600..1983); the true-L1 arm is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success.
