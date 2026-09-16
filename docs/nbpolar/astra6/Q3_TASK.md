# Q3 — finite-length construction, backoff, and f<=1.3

## Question

Formulate a defensible finite-length route from the V25 TRAIN conditional law
to a disclosure construction targeting a specified block failure probability
under population shift, rather than relying only on mean genie reliability or
a planning entropy ratio.

## Required work

1. Separate asymptotic polarization, finite-length source coding, empirical
   construction error, prior estimation error, decoder error, and shift.
2. Explain what current evidence establishes about `f<=1.3` at N=32768.
3. Propose coordinate-risk estimators/confidence bounds meaningful for block
   recovery, including correlated coordinate failures.
4. Derive a K1/K2 allocation with target block failure and explicit backoff.
5. Handle scarce HOLD data without repeated tuning.
6. Compare empirical genie order, analytic/BEC surrogate, cross-fitting or
   bootstrap stability, distributional robustness, and decoder-aware order.
7. Give the smallest experiment ladder separating construction failure from
   hard-decision decoder failure without turning HOLD into training data.

## Constraints and return

Planning `f`, sample-CE ratio, and qualified efficiency are distinct. Do not
infer a scaling law from non-monotone 16-block means or choose K/order on the
reported HOLD blocks. Return an error decomposition, estimators/bounds,
allocation rule, validation design, experiment ladder, assumptions, and
decisive failure criteria. No execution.

