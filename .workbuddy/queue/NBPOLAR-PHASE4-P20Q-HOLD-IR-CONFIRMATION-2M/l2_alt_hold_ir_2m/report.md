# NB-Polar Phase 4-P20Q instrumented alpha1 confirmation on 2M HOLD with mandatory H2 IR-1..IR-5

- protocol: `nbpolar-p20q-hold-ir-confirmation-2m` (mode `hold-2m-ir-confirmation`)
- source: `2M`; N=32768; K1=334 K2=6746 K_total=7080 (2M-session-derived, S2-i literal replay)
- alt-L2 construction: unit-pseudocount conditional; alt-table digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
- order file digest: `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906` (shared first-334 / first-6746 prefixes on all four arms)
- blocks: [[2916, 3043], [3044, 3171], [3172, 3299], [3300, 3427], [3428, 3555]] (remainder [3556, 3644] never used)
- outcome: `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE`; records 20/20
- operational exact: 4 (A 0 / B 4); b_restored_count=4 (descriptive: A fail -> B exact); b_maintained_count=0 (A exact and B exact); A->B table {'a_exact_b_exact': 0, 'a_exact_b_fail': 0, 'a_fail_b_exact': 4, 'a_fail_b_fail': 1}
- oracle exact: 4 (C 0 / D 4); d_restored_count=4 (diagnostic only, never operational)
- undetected: 0; nonfinite: 0
- IR payload: rank-pct (all) {'count': 12, 'median': 0.8830413818359375, 'min': 0.3802490234375, 'max': 0.989410400390625}; IR-5 truncated-all=True
- SC calls: 30/30 (Stage-B sampling 0); tags: 20/20
- key bits: 692580; public bits: 6554860; recount mismatch: 0
- integrity: ALL PASS []

C/D are oracle-labelled diagnostic controls, never an operational protocol or deployable result. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success. This is a descriptive HOLD confirmation reading on FIRST-USE 2M HOLD: no recovery / FER / superiority / qualification / promotion / reliability claim is made, and the H2 decision stays main-thread analysis after acceptance.
