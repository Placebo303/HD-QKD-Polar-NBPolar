# NB-Polar Phase 4-P20E plus1024 confirmation

- protocol: `nbpolar-p20e-plus1024-confirmation` (mode `dev-plus1024-confirmation`)
- source: `1M`; n=32768, k1=319, k2=6492, B1 K2=7516 (+1024 L2 order-prefix step)
- DEV blocks: [[384, 511], [512, 639], [640, 767]]; remainder [768, 1199] (never used)
- closed HOLD: [1600, 1983] (never selected); consumed VAL: [1200, 1599] (never selected); consumed P20C DEV: [0, 383] (never selected)
- base cap: 34119 key bits/block; B1 cap: 39239 key bits/block (raw 327680 bits; ratios 0.104123 / 0.119748)
- wall: 100.121085 s; peak RSS: 581156864 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- B0_sc_base: 3/3 exact; key 102357 bits; public 983229 bits
- B1_L2plus: 3/3 exact; key 117717 bits; public 983229 bits
- B2_true_l1_diagnostic: 3/3 exact; key 97572 bits; public 983229 bits

## B1-vs-B0 disclosure comparison (descriptive)

- B1 restored a complete block where B0 failed on 0/3 blocks
- block 0: B0 exact (exact=True) vs B1 exact (exact=True, dK2=1024, restored=False)
- block 1: B0 exact (exact=True) vs B1 exact (exact=True, dK2=1024, restored=False)
- block 2: B0 exact (exact=True) vs B1 exact (exact=True, dK2=1024, restored=False)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE`

descriptive zero-tuning +1024 confirmation on NEW real development blocks (same-file TRAIN subrange, N=32768, three new DEV blocks); B2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
