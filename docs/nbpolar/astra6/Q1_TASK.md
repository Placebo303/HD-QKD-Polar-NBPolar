# Q1 — explain the TRAIN-to-HOLD failure mechanism

## Question

Construct the strongest defensible causal diagnosis of why the frozen N=32768
point succeeds on TRAIN-model samples but fails on all three available
chronological HOLD blocks.

## Required work

1. Build a hypothesis table covering chance under a common distribution;
   covariate/conditional shift; support or prior calibration error;
   construction-order transfer failure; insufficient L1 or L2 backoff; hard
   L1 propagation; and interactions.
2. Predict the qualitative five-arm pattern for base, `l1_plus`, `l2_plus`,
   `both_plus`, and `true_l1_control` under each hypothesis.
3. State which patterns are identifiable with three paired blocks.
4. Recommend descriptive diagnostics that do not tune a new rate on them.
5. Design the smallest next independent-data experiment, including estimand,
   sampling unit, preregistered rule, and falsification outcomes.

## Constraints and return

Do not estimate HOLD FER, select a rate from the five arms, rerun historical
evidence, or assume TRAIN counts are the HOLD law. Separate model mismatch,
finite-length backoff, and decoder effects. Return a hypothesis matrix,
arm-pattern interpretations, ranked missing measurements, minimal independent
experiment, and forbidden conclusions. Stop at design.

