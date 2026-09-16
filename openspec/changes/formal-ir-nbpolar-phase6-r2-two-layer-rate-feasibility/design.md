# Design: Phase 6-R2 two-layer rate feasibility

Implement one transparent BEC polarization recurrence (`z_minus=2z-z^2`,
`z_plus=z^2`) and an independent literal oracle for small powers of two. Use
the accepted per-source L1/L2 entropy inputs, converting layer entropy to the
explicit q=32 erasure surrogate `epsilon_l=H_l/5`.

For each registered N and each registered split of a whole-block FER budget,
select the minimum worst-channel disclosure count whose residual union bound
meets that layer budget. Account
`leakage_bits=5*(K1+K2)+64` and
`f=leakage_bits/(N*(H1+H2))`. Report tag-inclusive and tag-free values.

Mandatory sensitivity axes are N=2^8 through 2^18, equal versus
entropy-proportional FER allocation, and every accepted empirical source.
Reproduce the N=256 single-layer epsilon=.05 calibration K=43 before using the
model. Determine the first N meeting `f<=1.3` for each axis; do not call any
result a rigorous lower bound or transfer it to the empirical neighbor-shift
channel.

Separately trace the implemented protocol path and prove whether oracle-L2 and
candidate-conditioned L2 have ever entered SC execution. Specify, but do not
implement, the later empirical construction and scalable decoder prerequisites.
