# NB-Polar Phase 4-P20K l1 dose 512 1p5m

- protocol: `nbpolar-p20k-l1-dose-512-1p5m` (mode `dev-l1-dose-512-1p5m`)
- source: `1p5M`; n=32768, k1=319, k2=6492, E1 K1=831 (+512 L1 order-prefix step)
- DEV blocks: [[1152, 1279], [1280, 1407], [1408, 1535]]; remainder [1536, 1659] (never used)
- DEV source: `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` (size 1869178 B, sha `ca351e52...`; 1M full pool and reserved 2M refused by the cross-file gate); 1.5M VAL: [1660, 2212] (never selected); 1.5M HOLD: [2213, 2766] (never selected)
- base cap: 34119 key bits/block; E1 cap: 36679 key bits/block (raw 327680 bits; ratios 0.104123 / 0.111935)
- wall: 107.644398 s; peak RSS: 558936064 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- E0_sc_base: 0/3 exact; key 102357 bits; public 983229 bits
- E1_L1plus512: 0/3 exact; key 110037 bits; public 983229 bits
- E2_true_l1_diagnostic: 3/3 exact; key 97572 bits; public 983229 bits

## E1-vs-E0 disclosure comparison (descriptive)

- E1 restored a complete block where E0 failed on 0/3 blocks
- block 0: E0 verify_failed (exact=False) vs E1 verify_failed (exact=False, dK1=512, restored=False)
- block 1: E0 verify_failed (exact=False) vs E1 verify_failed (exact=False, dK1=512, restored=False)
- block 2: E0 verify_failed (exact=False) vs E1 verify_failed (exact=False, dK1=512, restored=False)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE`

descriptive +512 L1-dose-512 diagnostic on new-segment 1.5M TRAIN blocks (N=32768, three DEV blocks 1152..1535) under the frozen per-session-calibrated prior; E2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
