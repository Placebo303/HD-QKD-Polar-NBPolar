# NB-Polar Phase 4-P20R single-factor L2-order-position on 1.5M VAL remainder with mandatory H2 IR-1..IR-5

- protocol: `nbpolar-p20r-order-position-1p5m` (mode `val-remainder-order-position-1p5m`)
- source: `1p5M`; N=32768; K1=331 K2=6689 K_total=7020 (1.5M-session-derived, S2-i literal replay)
- alt-L2 construction: unit-pseudocount conditional alpha1 on all arms; alt-table digest `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`
- frozen-A order digest: `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638` (first-331 / first-6689 prefixes on A/C); new-B order digest: `c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751` (first-6689 prefix on B/D); set-delta |A-B|=5476 |B-A|=5476 (size-delta 0)
- blocks: [[2044, 2171]] (remainder [2172, 2212] never used; 2M HOLD remainder counted never decoded)
- outcome: `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE`; records 4/4
- operational exact: 0 (A 0 / B 0); b_restored_count=0 (descriptive: A fail -> B exact); b_maintained_count=0 (A exact and B exact); A->B table {'a_exact_b_exact': 0, 'a_exact_b_fail': 0, 'a_fail_b_exact': 0, 'a_fail_b_fail': 1}
- oracle exact: 0 (C 0 / D 0); d_restored_count=0 (diagnostic only, never operational)
- undetected: 0; nonfinite: 0
- IR payload: rank-pct (all) {'count': 4, 'median': 0.6644287109375, 'min': 0.329193115234375, 'max': 0.999664306640625}; IR-5 truncated-all=True
- SC calls: 6/6 (Stage-B sampling 0); tags: 4/4
- key bits: 137346; public bits: 1310972; recount mismatch: 0
- integrity: ALL PASS []

C/D are oracle-labelled diagnostic controls, never an operational protocol or deployable result. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success. This is a descriptive VAL-remainder single-factor order-position reading on a FIRST-USE 1.5M VAL-remainder block: no recovery / FER / superiority / qualification / promotion / reliability claim is made, and the H2 decision stays main-thread analysis after acceptance.
