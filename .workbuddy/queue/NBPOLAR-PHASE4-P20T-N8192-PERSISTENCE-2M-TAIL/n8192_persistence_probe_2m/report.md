# NB-Polar Phase 4-P20T N=8192 persistence probe on the single 2M HOLD-tail DEV block with N=8192-sized full-block IR-5

- protocol: `nbpolar-p20t-n8192-persistence-2m` (mode `n8192-tail-persistence-probe-2m`)
- source: `2M`; N=8192; K1=84 K2=1676 K_total=1760 (in-packet K-rule derivation from recomputed 2M H, TRAIN-residual split)
- alt-L2 construction: unit-pseudocount conditional alpha1 on all arms (recomputed from the worktree counts by the frozen rule); construction digest `d77466eca5b80840ba114ba76500d73d472a5f2818e1fc00b28abbd86d352bb6`
- fresh-A order digest: `66aefea8d88ef0160906ea37575aa4c4c0dbc0dda6fcd67513a61458198ade93` (first-84 / first-1676 prefixes on A/O); spike-B order digest: `355a32d3551c065088da6627dc1ad4ec07b004b73d322567eddaf8cadf03352a` (first-1676 prefix on B; formula `F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192`); set-delta |A-B|=963 |B-A|=963 (size-delta 0)
- single-segment DEV: HOLD [3595, 3626] (remainder [3627, 3644] never used; 1.5M stub/remainder counted never decoded)
- outcome: `TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE`; records 3/3
- operational exact (recorded, NOT a recovery rate): 0; per-arm rows {'A_anchor_frozen_order_equivalent': {'arm': 'A_anchor_frozen_order_equivalent', 'records': 1, 'exact_count': 0, 'outcomes': {'verify_failed': 1}, 'first_error_layers': ['L2']}, 'B_spike_local_order': {'arm': 'B_spike_local_order', 'records': 1, 'exact_count': 0, 'outcomes': {'verify_failed': 1}, 'first_error_layers': ['L2']}, 'O_true_l1_oracle': {'arm': 'O_true_l1_oracle', 'records': 1, 'exact_count': 0, 'outcomes': {'verify_failed': 1}, 'first_error_layers': ['L2']}}
- oracle exact (diagnostic only, never operational): 0
- undetected: 0; nonfinite: 0
- IR payload: rank-pct (all) {'count': 3, 'median': 0.400146484375, 'min': 0.050048828125, 'max': 0.400146484375}; IR-5 N=8192-sized=True (ir5full-v1)
- SC calls: 5/5 (Stage-B sampling 0); tags: 3/3
- key bits: 26172; public bits: 245949; recount mismatch: 0
- integrity: ALL PASS []

O is an oracle-labelled diagnostic control, never an operational protocol or deployable result. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success. This is a descriptive N=8192 persistence probe (n=1, within-N paired comparison only, Q-G1/Q-G2) of one spike-local L2-order position rule under the frozen alpha1 construction at in-packet disclosure with full-block hazard geometry recorded: no FER / reliability / efficiency / leakage / key-rate / recovery / scaling / promotion claim is made; no cross-N inference; no H2 input; the DEV block is consumed by this packet regardless of outcome.
