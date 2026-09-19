# NB-Polar Phase 4-P20J l1 dose escalation 1p5m

- protocol: `nbpolar-p20j-l1-dose-escalation-1p5m` (mode `dev-l1-dose-escalation-1p5m`)
- source: `1p5M`; n=32768, k1=319, k2=6492, D1 K1=575 (+256 L1 order-prefix step)
- DEV blocks: [[768, 895], [896, 1023], [1024, 1151]]; remainder [1152, 1659] (never used)
- DEV source: `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` (size 1869178 B, sha `ca351e52...`; 1M full pool and reserved 2M refused by the cross-file gate); 1.5M VAL: [1660, 2212] (never selected); 1.5M HOLD: [2213, 2766] (never selected)
- base cap: 34119 key bits/block; D1 cap: 35399 key bits/block (raw 327680 bits; ratios 0.104123 / 0.108029)
- wall: 107.752468 s; peak RSS: 558669824 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- D0_sc_base: 0/3 exact; key 102357 bits; public 983229 bits
- D1_L1plus: 0/3 exact; key 106197 bits; public 983229 bits
- D2_true_l1_diagnostic: 3/3 exact; key 97572 bits; public 983229 bits

## D1-vs-D0 disclosure comparison (descriptive)

- D1 restored a complete block where D0 failed on 0/3 blocks
- block 0: D0 verify_failed (exact=False) vs D1 verify_failed (exact=False, dK1=256, restored=False)
- block 1: D0 verify_failed (exact=False) vs D1 verify_failed (exact=False, dK1=256, restored=False)
- block 2: D0 verify_failed (exact=False) vs D1 verify_failed (exact=False, dK1=256, restored=False)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_ESCALATION_1P5M_COMPLETE`

descriptive +256 L1-dose-escalation diagnostic on new-segment 1.5M TRAIN blocks (N=32768, three DEV blocks 768..1151) under the frozen per-session-calibrated prior; C2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
