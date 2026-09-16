# Main-thread acceptance — Phase 4-P9 lower-rate boundary resolution

Decision: **`TARGET_EMPIRICAL_LOWER_RATE_POINT_ACCEPTED`** within the frozen
synthetic V25-1M-TRAIN model-sampled N=256 development scope.

The main thread accepts K1=6/K2=70 as the deterministic minimum eligible point
of the complete registered grid, including both zero axes. Independent CONFIRM
returned 624/640 exact with one-sided 95% Wilson lower bound
0.9626753340557015; all integrity/scientific gates were true; both independent
reviews PASS; and the sole artifact read/attempt was consumed without rerun or
tuning. The Wave-C delivery failure did not cause a second execution.

This is a finite-grid development result, not a continuous optimum or a real
efficiency claim. BEC and P8-anchor comparisons remain report-only. The
planning-only f=2.165159928897918 remains materially above the project target
f<=1.3, so the next step is decoder scaling rather than another N=256 static or
adaptive disclosure gate.

Next gate: `NBPOLAR-PHASE4-P10-FWHT-KERNEL-SCALING-PROBE`, a non-claim Tier-X
probe frozen awaiting explicit authorization.
