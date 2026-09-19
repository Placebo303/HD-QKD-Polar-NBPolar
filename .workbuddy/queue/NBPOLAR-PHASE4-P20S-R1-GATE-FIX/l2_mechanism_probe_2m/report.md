# NB-Polar Phase 4-P20S maximum-information mechanism probe on the merged final 2M block with uncapped full-block IR-5

- protocol: `nbpolar-p20s-mechanism-probe-2m` (mode `merged-mechanism-probe-2m`)
- source: `2M`; N=32768; K1=334 K2=6746 K_total=7080 (2M-session-derived, S2-i literal replay)
- alt-L2 construction: unit-pseudocount conditional alpha1 on all arms; alt-table digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
- frozen-A order digest: `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906` (first-334 / first-6746 prefixes on A/O); spike-B order digest: `139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864` (first-6746 prefix on B; formula `F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8`); set-delta |A-B|=1599 |B-A|=1599 (size-delta 0)
- merged block segments: [[2827, 2915], [3556, 3594]] (remainder [3595, 3644] never used; HOLD tail + 1.5M stub/remainder counted never decoded)
- outcome: `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE`; records 3/3
- operational exact (recorded, NOT a recovery rate): 1; per-arm rows {'A_anchor_frozen_order': {'arm': 'A_anchor_frozen_order', 'records': 1, 'exact_count': 1, 'outcomes': {'exact': 1}, 'first_error_layers': ['None']}, 'B_spike_local_order': {'arm': 'B_spike_local_order', 'records': 1, 'exact_count': 0, 'outcomes': {'verify_failed': 1}, 'first_error_layers': ['L2']}, 'O_true_l1_oracle': {'arm': 'O_true_l1_oracle', 'records': 1, 'exact_count': 1, 'outcomes': {'exact': 1}, 'first_error_layers': ['None']}}
- oracle exact (diagnostic only, never operational): 1
- undetected: 0; nonfinite: 0
- IR payload: rank-pct (all) {'count': 1, 'median': 0.432220458984375, 'min': 0.432220458984375, 'max': 0.432220458984375}; IR-5 uncapped=True (ir5full-v1)
- SC calls: 5/5 (Stage-B sampling 0); tags: 3/3
- key bits: 104722; public bits: 983229; recount mismatch: 0
- integrity: ALL PASS []

O is an oracle-labelled diagnostic control, never an operational protocol or deployable result. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success. This is a descriptive merged-block mechanism probe of one local-spike L2-order position rule under the frozen alpha1 construction at frozen disclosure with full-block hazard geometry recorded: no recovery / FER / superiority / qualification / promotion / reliability claim is made, and the H2 decision stays main-thread analysis after acceptance.
