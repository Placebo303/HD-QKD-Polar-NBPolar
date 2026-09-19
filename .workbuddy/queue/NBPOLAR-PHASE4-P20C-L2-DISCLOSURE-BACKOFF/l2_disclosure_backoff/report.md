# NB-Polar Phase 4-P20C L2 disclosure backoff

- protocol: `nbpolar-p20c-l2-disclosure-backoff` (mode `dev-l2-disclosure-backoff`)
- source: `1M`; n=32768, k1=319, k2=6492, B1 K2=7516 (+1024 L2 order-prefix step)
- DEV blocks: [[0, 127], [128, 255], [256, 383]]; remainder [384, 1199] (never used)
- closed HOLD: [1600, 1983] (never selected); consumed VAL: [1200, 1599] (never selected)
- base cap: 34119 key bits/block; B1 cap: 39239 key bits/block (raw 327680 bits; ratios 0.104123 / 0.119748)
- wall: 92.906254 s; peak RSS: 579366912 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- B0_sc_base: 2/3 exact; key 102357 bits; public 983229 bits
- B1_L2plus: 3/3 exact; key 117717 bits; public 983229 bits
- B2_true_l1_diagnostic: 2/3 exact; key 97572 bits; public 983229 bits

## B1-vs-B0 disclosure comparison (descriptive)

- B1 restored a complete block where B0 failed on 1/3 blocks
- block 0: B0 exact (exact=True) vs B1 exact (exact=True, dK2=1024, restored=False)
- block 1: B0 verify_failed (exact=False) vs B1 exact (exact=True, dK2=1024, restored=True)
- block 2: B0 exact (exact=True) vs B1 exact (exact=True, dK2=1024, restored=False)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE`

descriptive single-factor L2-disclosure-backoff diagnostic on independent real development data (same-file TRAIN, N=32768, three DEV blocks); B2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
