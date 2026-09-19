# NB-Polar Phase 4-P20H per-session TRAIN calibration

- protocol: `nbpolar-p20h-per-session-calibration` (mode `train-calibration-freeze`)
- source: `1p5M` (type2_1p5M_20260121_183806); counts [1024, 1024] sum 424960
- lambda: `137.3823795883264` (D4R2 nested-CV refit constant carried via formal_ir.nbpolar.prior_artifact.LAMBDA_STAR; frozen procedure output, no DEV influence, no per-session search, no floor search)
- floor: `1e-15`; packing `A = 32*U1 + U2 (low = s&31 = U2, high = (s>>5)&31 = U1)`; conditioning `FULL_BOB_ONLY`
- recalibrated literals: H1=2.006647056368773 H2=1.9017235959286112 TOTAL=3.908370652297384
- floor change vs unfloored smoothed: 4.440892098500626e-16; column dev 7.327471962526033e-15
- prior digest: `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
- input digest: `e5e99cc89a09ec913b82af7d061cc462af7bf57404c6d97c06537de9c3a2d59c` (npz 25166822 B)
- manifest cross-check: TRAIN 424960 pairs == counts total 424960: True
- counts content opens: 1 (single declared open)

Stage B loads `calibrated_prior.npz` read-only behind the calibration-identity digest gate and refuses on mismatch. No refit/resmoothing/relambda after any DEV contact.
