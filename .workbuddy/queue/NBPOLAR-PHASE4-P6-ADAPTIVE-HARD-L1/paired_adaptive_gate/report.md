# NB-Polar Phase 4-P6 adaptive hard-L1 disclosure gate — synthetic signal

- protocol: `nbpolar-p4p6-adaptive-hard-l1-gate` (mode `paired-adaptive-hard-l1-dev-gate`)
- seeds: [2026091550, 2026091551, 2026091552, 2026091553, 2026091554]; masters: [2026101550, 2026101551, 2026101552, 2026101553, 2026101554]; planned pairs: 640
- point: q=32, N=256, epsilon1=0.05, profile=strong, K1 levels=[45, 60, 72, 112], K2=140
- wall: 105.941485 s; peak RSS: 394567680 bytes

## Paired cells

| cell | count |
|---|---|
| both_exact | 632 |
| adaptive_only | 0 |
| static_only | 0 |
| neither | 8 |

## Disclosure

- static: 847360 key-dependent bits (mean 1324.000000)
- adaptive: 675783 key-dependent bits (mean 1055.910938)
- percentage saving: 20.248419%
- tag invocations (static/adaptive/total): 640/942/1582; feedback invocations: 302; union bound: 8.57603918436034e-17
- adaptive termination histogram: {'1': 403, '2': 185, '3': 39, '4': 13}

## Integrity gates

| gate | result |
|---|---|
| pairing_coverage_complete | True |
| stream_block_identity_exact | True |
| result_buckets_disjoint_exhaustive | True |
| d1_exactly_nested_and_d2_disclosed_once | False |
| provenance_and_truth_isolation_complete | True |
| undetected_zero | True |
| nonfinite_zero | True |
| resource_abort_zero | True |
| transcript_recount_mismatch_zero | True |
| tag_feedback_public_control_accounting_and_union_bound_exact | True |
| wall_rss_within_frozen_limits | True |
| attempt_seed_accounting_exact | True |

## Scientific gates

| gate | result |
|---|---|
| static_exact_at_least_620_of_640 | True |
| adaptive_exact_equals_static_exact | True |
| paired_adaptive_only_zero_and_static_only_zero | True |
| leakage_100_adaptive_le_85_static | True |

- outcome label: `BLOCKED`

**Scope:** synthetic N=256 development evidence only; this is not real-channel FER, reconciliation efficiency, key rate, qualification or promotion; undetected frames are never merged with exact frames and planning-only f is not real-channel efficiency.
