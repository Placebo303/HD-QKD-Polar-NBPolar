# Main-thread disposition — X07

X07 is accepted as a descriptive provenance diagnosis, not as a scientific
candidate. The earliest established divergence is
`POPULATION_SESSION_IDENTITY_1M`: V49 describes the 2026-01-21 V25 TRAIN
population (MLE H=0.8010378248977232 bits/symbol), while X06 sampled the
2026-01-23 Model-F CAL population after concentration smoothing (model
H=7.5094403148357545). Axis, packing, Bob weights and normalization were
excluded as explanations.

The documented post-run correction touched auxiliary MI fields only. Those MI
fields are not accepted as evidence and must not be used downstream; the
required entropy/CE/provenance quantities were independently reproduced.

Disposition: use the V25 TRAIN counts with the V49 `1e-15` floor-only support
rule. Do not revise lambda or use the Model-F artifact for target-channel
construction. Next gate is Phase 4-P7 target-population empirical construction.

