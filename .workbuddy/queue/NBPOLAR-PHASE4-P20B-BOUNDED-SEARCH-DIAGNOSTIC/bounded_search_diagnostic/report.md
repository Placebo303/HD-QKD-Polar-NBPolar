# NB-Polar Phase 4-P20B bounded-search diagnostic

- protocol: `nbpolar-p20b-bounded-search-diagnostic` (mode `dev-bounded-search-diagnostic`)
- source: `1M`; n=32768, k1=319, k2=6492, search bound M=8
- neighborhood: `P20B-NBHD-1-hamming1-u-domain-margin-ranked`
- DEV blocks: [[1200, 1327], [1328, 1455], [1456, 1583]]; remainder [1584, 1599] (unused)
- closed HOLD: [1600, 1983] (never selected)
- base cap: 34119 key bits/block (raw 327680 bits; ratio 0.104123)
- wall: 111.305401 s; peak RSS: 541188096 bytes; resource stop fired: False

## Per-arm outcomes (descriptive, no threshold)

- S0_sc_base: 0/3 exact; key 102357 bits; public 983229 bits
- S1_bounded_search: 0/3 exact; key 102357 bits; public 983229 bits
- S2_true_l1_diagnostic: 0/3 exact; key 97572 bits; public 983229 bits

## Search-vs-SC comparison (descriptive)

- S1 found a strictly better present candidate on 0/3 blocks
- block 0: S0 verify_failed (exact=False) vs S1 verify_failed (exact=False, selected=greedy, better=False, dNLL=0.0 bits)
- block 1: S0 verify_failed (exact=False) vs S1 verify_failed (exact=False, selected=greedy, better=False, dNLL=0.0 bits)
- block 2: S0 verify_failed (exact=False) vs S1 verify_failed (exact=False, selected=greedy, better=False, dNLL=0.0 bits)

## Integrity

- gates all pass: True
- failing: []
- label: `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE`

descriptive single-factor bounded-search diagnostic on independent real development data (VAL split, N=32768, three DEV blocks); S2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate; not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion evidence; the CE-normalized disclosure ratio is not qualification efficiency; undetected is never success
