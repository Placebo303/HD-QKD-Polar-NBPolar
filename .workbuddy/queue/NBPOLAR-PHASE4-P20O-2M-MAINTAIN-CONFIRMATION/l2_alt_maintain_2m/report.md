# NB-Polar Phase 4-P20O maintain-confirmation of ALT-L2-LAPLACE-alpha1 at per-session disclosure on 2M VAL

- protocol: `nbpolar-p20o-2m-maintain-confirmation` (mode `val-2m-maintain-confirmation`)
- source: `2M`; N=32768; K1=334 K2=6746 K_total=7080 (2M-session-derived, S2-i literal recomputation)
- alt-L2 construction: unit-pseudocount conditional; alt-table digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
- order file digest: `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906` (shared first-334 / first-6746 prefixes on all four arms)
- blocks: [[2187, 2314], [2315, 2442], [2443, 2570], [2571, 2698], [2699, 2826]] (remainder [2827, 2915] never used)
- outcome: `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`; records 20/20
- operational exact: 2 (A 0 / B 2); b_restored_count=2 (descriptive: A fail -> B exact); b_maintained_count=0 (A exact and B exact); A->B table {'a_exact_b_exact': 0, 'a_exact_b_fail': 0, 'a_fail_b_exact': 2, 'a_fail_b_fail': 3}
- oracle exact: 3 (C 0 / D 3); d_restored_count=3 (diagnostic only, never operational)
- undetected: 0; nonfinite: 0
- SC calls: 30/30 (Stage-B sampling 0); tags: 20/20
- key bits: 692580; public bits: 6554860; recount mismatch: 0
- integrity: ALL PASS []

C/D are oracle-labelled diagnostic controls, never an operational protocol or deployable result. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success. This is a descriptive maintain-confirmation reading on FIRST-USE 2M VAL: no recovery / FER / superiority / qualification / promotion / reliability claim is made, and the positive/negative branch decision stays with the main thread after acceptance.
