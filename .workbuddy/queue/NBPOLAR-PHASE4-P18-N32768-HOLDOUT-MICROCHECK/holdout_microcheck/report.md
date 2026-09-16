# NB-Polar Phase 4-P18 N=32768 1M-HOLD operational microcheck

- protocol: `nbpolar-p18-holdout-microcheck` (mode `holdout-microcheck`)
- source/target: `1M`; q=32, n=32768, K1=319, K2=6492, chunk_rows=512, tag_bits=64
- HOLD frames: [1600, 1999]; blocks: [[1600, 1727], [1728, 1855], [1856, 1983]]; unused remainder: {'frame_start': 1984, 'frame_end': 1999, 'frames': 16, 'symbols': 4096, 'used': False}
- wall: 37.274417 s; peak RSS: 520798208 bytes; resource stop fired: False

## Predecessor and split identities (verified before the content opens)

- P16 construction digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` (match: True)
- split manifest: `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json` declares 400 HOLD frames / 102400 HOLD pairs (frozen 400/102400)

## Descriptive per-block scalars (no threshold, no recovery gate)

| block | frames | outcome | raw SER | total NLL bits | L1 correct | tag | disclosure CE ratio |
|---|---|---|---|---|---|---|---|
| 0 | 1600..1727 | verify_failed | 0.240936279296875 | 27589.350245339167 | True | False | 1.2366728355903898 |
| 1 | 1728..1855 | verify_failed | 0.23980712890625 | 27884.160498770143 | False | False | 1.2235978917674373 |
| 2 | 1856..1983 | verify_failed | 0.240264892578125 | 27688.088800952148 | False | False | 1.232262733815947 |

- total NLL bits: 83161.59954506146
- key-dependent bits: 102357 (fixed full-block value 34119)
- public control bits: 983229 (fixed per-tag value 327743)
- transcript recount mismatches: []
- sample CE-normalized disclosure ratio: 1.230820481567787 (descriptive only; NOT qualification efficiency)

## Integrity gates

| gate | result |
|---|---|
| predecessor_construction_identity | True |
| hold_split_manifest_identity | True |
| target_population_contract | True |
| hold_population_exact | True |
| blocks_exact_with_declared_remainder | True |
| orders_valid_k_replay_f_within_budget | True |
| sc_calls_exact | True |
| tags_exact | True |
| buckets_disjoint_exhaustive | True |
| truth_isolation | True |
| undetected_zero | True |
| nonfinite_zero | True |
| disclosure_recount_exact | True |
| one_open_per_protected_input | True |
| input_stat_unchanged | True |
| no_unregistered_access | True |
| resource_limits_met_and_no_abort | True |

- outcome label: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`
- recovery threshold: None (none; 0..3 exact outcomes are descriptive)

**Scope:** real-input operational microcheck of the frozen V25 1M HOLD split at N=32768 only (three registered chronological blocks, frames 1600..1983); descriptive loading/ordering/prior/decoder/accounting evidence, not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success.
