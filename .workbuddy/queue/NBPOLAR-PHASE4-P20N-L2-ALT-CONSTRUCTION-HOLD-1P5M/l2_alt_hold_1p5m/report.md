# NB-Polar Phase 4-P20N fixed-disclosure ALT-L2 construction on 1.5M HOLD

- protocol: `nbpolar-p20n-l2-alt-hold-1p5m` (mode `hold-l2-alt-1p5m`)
- source: `1p5M`; N=32768; K1=331 K2=6689 K_total=7020 (carried literals, never recomputed)
- alt-L2 construction: unit-pseudocount conditional; alt-table digest `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`
- order file digest: `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638` (shared first-331 / first-6689 prefixes on all four arms)
- blocks: [[2213, 2340], [2341, 2468], [2469, 2596], [2597, 2724]] (remainder [2725, 2766] never used)
- outcome: `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`; records 16/16
- operational exact: 1 (A 0 / B 1); b_restored_count=1 (descriptive: A fail -> B exact); maintain=0
- oracle exact: 1 (C 0 / D 1); d_restored_count=1 (diagnostic only, never operational)
- undetected: 0; nonfinite: 0
- SC calls: 24/24 (Stage-B sampling 0); tags: 16/16
- key bits: 549384; public bits: 5243888; recount mismatch: 0
- integrity: ALL PASS []

C/D are oracle-labelled diagnostic controls, never an operational protocol or deployable result. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success. No recovery / FER / superiority / qualification claim is made; the B-vs-A and D-vs-C readings are descriptive only.
