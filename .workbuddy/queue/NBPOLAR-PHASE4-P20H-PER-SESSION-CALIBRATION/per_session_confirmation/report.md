# NB-Polar Phase 4-P20H plus1024 per-session confirmation

- protocol: `nbpolar-p20h-per-session-calibration` (mode `dev-plus1024-per-session-calibration`)
- source: `1p5M`; n=32768, k1=319, k2=6492, B1 K2=7516 (+1024 L2 order-prefix step)
- DEV blocks: [[0, 127], [128, 255], [256, 383]]; remainder [384, 1659] (never used)
- DEV source: `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` (size 1869178 B, sha `ca351e52...`; 1M full pool and reserved 2M refused by the cross-file gate); 1.5M VAL: [1660, 2212] (never selected); 1.5M HOLD: [2213, 2766] (never selected)
- base cap: 34119 key bits/block; B1 cap: 39239 key bits/block (raw 327680 bits; ratios 0.104123 / 0.119748)
- wall: 114.272383 s; peak RSS: 558710784 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- B0_sc_base: 0/3 exact; key 102357 bits; public 983229 bits
- B1_L2plus: 0/3 exact; key 117717 bits; public 983229 bits
- B2_true_l1_diagnostic: 3/3 exact; key 97572 bits; public 983229 bits

## B1-vs-B0 disclosure comparison (descriptive)

- B1 restored a complete block where B0 failed on 0/3 blocks
- block 0: B0 verify_failed (exact=False) vs B1 verify_failed (exact=False, dK2=1024, restored=False)
- block 1: B0 verify_failed (exact=False) vs B1 verify_failed (exact=False, dK2=1024, restored=False)
- block 2: B0 verify_failed (exact=False) vs B1 verify_failed (exact=False, dK2=1024, restored=False)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE`

descriptive +1024 confirmation on per-session-calibrated 1.5M TRAIN blocks (N=32768, three DEV blocks); B2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
