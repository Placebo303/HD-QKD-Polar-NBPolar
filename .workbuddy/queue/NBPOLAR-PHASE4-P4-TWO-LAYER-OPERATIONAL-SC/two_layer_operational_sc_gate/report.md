# NB-Polar Phase 4-P4 two-layer operational SC — synthetic development gate

- protocol: `nbpolar-two-layer-operational-sc` (mode `paired-two-layer-dev-gate`)
- run seed: `2026091360`; Toeplitz master: `2026091361`; planned blocks: 96
- point: q=32, N=256, epsilon1=0.05, epsilon2=0.2, k1=45, k2=110
- wall: 10.154709 s; peak RSS: 144609280 bytes

## Outcomes (per arm, disjoint and exhaustive)

| arm | exact | undetected | verify_failed | decode_failed | resource_abort |
|---|---|---|---|---|---|
| operational | 26 | 0 | 70 | 0 | 0 |
| oracle | 44 | 0 | 52 | 0 | 0 |

- attempt consumption point: first gate SC call; attempts consumed by this run: 1
- report-only exact: {'operational': 26, 'oracle': 44}; oracle/candidate divergence: 34 of 96 defined (no threshold)

## Accounting

- L1 disclosure per arm: 225 bits; L2 disclosure per arm: 550 bits; tag: 64 bits.
- fully invoked arm: 839 bits.
- key-dependent total: 161088; public control total: 503616 (2623 bits per tag invocation).
- transcript events: 576 {'l1_disclosure': 192, 'l2_disclosure': 192, 'verification_tag': 192}; recount mismatch count: 0.

## Hard gates

| gate | result |
|---|---|
| paired_coverage_complete | True |
| both_arms_l2_invoked_for_l1_candidates | True |
| p1_provenance_prior_only | True |
| candidate_provenance_candidate_conditioned | True |
| oracle_provenance_oracle_conditioned | True |
| operational_truth_leak_zero | True |
| undetected_zero | True |
| nonfinite_zero | True |
| resource_abort_zero | True |
| outcome_buckets_disjoint_exhaustive | True |
| disclosures_exact | True |
| transcript_recount_mismatch_zero | True |
| pre_run_injected_wrong_l1_propagation_passed | True |

- candidate label: `TWO_LAYER_OPERATIONAL_SC_CANDIDATE`

**Scope:** synthetic two-layer interface and cross-layer-propagation development signal only; this is not real-data FER, leakage efficiency, key rate, qualification, promotion or f<=1.3 evidence.
