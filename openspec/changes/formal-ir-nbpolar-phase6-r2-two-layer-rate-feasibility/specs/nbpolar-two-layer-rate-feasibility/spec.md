# NB-Polar two-layer rate-feasibility requirements

## Requirement: explicit efficiency objective

The study SHALL compute `f=(5*(K1+K2)+64)/(N*(H1+H2))` and SHALL use
`f<=1.3` as the registered feasibility target.

## Requirement: sensitivity, not theorem

The study SHALL expose channel surrogate, FER allocation, entropy source and
tag accounting. It SHALL NOT describe BEC results as empirical-channel
performance, a universal lower bound, or decoder evidence.

## Requirement: operational-L2 gap

The study SHALL distinguish true-L1-conditioned oracle L2 from
candidate-L1-conditioned operational L2 and SHALL identify which paths have
actually executed.
