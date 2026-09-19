# NB-Polar Phase 4-P20M raw-prior + session-budget operating-point swap

- protocol: `nbpolar-p20m-raw-prior-val-1p5m` (mode `dev-raw-prior-val-1p5m`)
- source: `1p5M`; N=32768; G1 K1=331 K2=6689 K_total=7020
- budget literal: `1.3*32768*0.8255660516732961-64 over 5, floored, clipped [0,65536] = 7020`
- blocks: [[1660, 1787], [1788, 1915], [1916, 2043]] (remainder [2044, 2212] never used)
- outcome: `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`; records 9/9
- operational exact: 0 (G0 0 / G1 0); g1_restored_count=0 (descriptive: G0 fail -> G1 exact); maintain=0
- oracle exact: 0 (diagnostic only, never operational)
- undetected: 0; nonfinite: 0
- SC calls: 15/15 (Stage-B sampling 0); tags: 9/9
- key bits: 308376; public bits: 2949687; recount mismatch: 0
- integrity: ALL PASS []

G2 is an oracle-labelled diagnostic control, never an operational protocol or deployable rate. The CE-normalized disclosure ratio is not qualification efficiency; undetected is never success.
