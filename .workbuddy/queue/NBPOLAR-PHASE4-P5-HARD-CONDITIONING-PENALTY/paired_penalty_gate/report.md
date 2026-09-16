# NB-Polar Phase 4-P5 hard-L1 conditioning penalty gate — synthetic statistic

- protocol: `nbpolar-p5-hard-conditioning-penalty-gate` (mode `paired-penalty-dev-gate`)
- seeds: [2026091470, 2026091471, 2026091472]; masters: [2026101470, 2026101471, 2026101472]; planned pairs: 384
- point: q=32, N=256, epsilon1=0.05, profile=strong, k1=45, k2=140
- p2_maxdiff: 0.34875000000000267 (floor 0.3)
- wall: 41.187262 s; peak RSS: 211537920 bytes

## Paired four-cell table

| cell | count |
|---|---|
| both_exact | 233 |
| oracle_only | 144 |
| operational_only | 0 |
| neither | 7 |

- X (oracle-only event count): 144; one-sided 95% exact lower bound L: 0.3338842736427746

## Integrity gates

| gate | result |
|---|---|
| pairing_coverage_complete | True |
| p2_maxdiff_at_least_0p30 | True |
| provenance_candidate_oracle_complete | True |
| operational_truth_leak_zero | True |
| undetected_zero | True |
| nonfinite_zero | True |
| resource_abort_zero | True |
| cells_disjoint_exhaustive | True |
| disclosures_exact_and_transcript_recount_zero | True |
| attempt_accounting_at_frozen_point | True |

## Discriminator

- oracle_exact_min_met: True
- operational_only_zero: True
- lower_bound_above_0p30: True
- passed: True

- outcome label: `HARD_L1_CONDITIONING_PENALTY_CANDIDATE`

**Scope:** synthetic single-point N=256 hard-conditioning penalty signal only; not real-data FER, efficiency, qualification or promotion; operational-arm numbers are interface diagnostics.
