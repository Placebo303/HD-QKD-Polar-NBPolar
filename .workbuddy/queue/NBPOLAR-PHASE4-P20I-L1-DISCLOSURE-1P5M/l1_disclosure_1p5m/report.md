# NB-Polar Phase 4-P20I l1 disclosure 1p5m

- protocol: `nbpolar-p20i-l1-disclosure-1p5m` (mode `dev-l1-disclosure-1p5m`)
- source: `1p5M`; n=32768, k1=319, k2=6492, C1 K1=447 (+128 L1 order-prefix step)
- DEV blocks: [[384, 511], [512, 639], [640, 767]]; remainder [768, 1659] (never used)
- DEV source: `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` (size 1869178 B, sha `ca351e52...`; 1M full pool and reserved 2M refused by the cross-file gate); 1.5M VAL: [1660, 2212] (never selected); 1.5M HOLD: [2213, 2766] (never selected)
- base cap: 34119 key bits/block; C1 cap: 34759 key bits/block (raw 327680 bits; ratios 0.104123 / 0.106076)
- wall: 110.575097 s; peak RSS: 559026176 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- C0_sc_base: 0/3 exact; key 102357 bits; public 983229 bits
- C1_L1plus: 0/3 exact; key 104277 bits; public 983229 bits
- C2_true_l1_diagnostic: 3/3 exact; key 97572 bits; public 983229 bits

## C1-vs-C0 disclosure comparison (descriptive)

- C1 restored a complete block where C0 failed on 0/3 blocks
- block 0: C0 verify_failed (exact=False) vs C1 verify_failed (exact=False, dK1=128, restored=False)
- block 1: C0 verify_failed (exact=False) vs C1 verify_failed (exact=False, dK1=128, restored=False)
- block 2: C0 verify_failed (exact=False) vs C1 verify_failed (exact=False, dK1=128, restored=False)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE`

descriptive +128 L1-disclosure diagnostic on new-segment 1.5M TRAIN blocks (N=32768, three DEV blocks 384..767) under the frozen per-session-calibrated prior; C2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
