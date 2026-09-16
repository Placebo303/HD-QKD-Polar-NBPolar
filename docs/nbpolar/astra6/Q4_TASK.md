# Q4 — scalable exact q-ary SC/SCL without semantic drift

## Question

Design a scalable decoder path for q=32 and large N with explicitly preserved
semantics. Accepted SC uses direct q-squared log-sum-exp with row chunking. A
tested FWHT shortcut changed exact support and near-tie decisions. Ordinary
q-ary SCL is missing.

## Required work

1. Decompose time/memory of SC recursion, metric construction, result
   retention, and prospective list decoding.
2. Separate allocation-only/algebraically exact optimizations from numerical
   approximations and new algorithms.
3. Decide whether transformed convolution can preserve zero support and stable
   log behavior; otherwise give an error model and decision-margin certificate.
4. Specify q-ary SCL for L={1,4,8}: path metric, branching/pruning, known
   coordinates, deterministic ties, memory layout, and L=1 equivalence.
5. Give a validation ladder from tiny exhaustive oracle and near-tie cases to
   N=256/1024 profiles and one bounded larger-N comparison.
6. Rank SCL, exact kernel acceleration, metric lifetime, and construction
   quality by expected scientific value.

## Constraints and return

Bitwise equivalence, bounded error, and a new decoder are different claims.
Do not inherit reference evidence for an approximate kernel. No tag-based path
selection. Preserve exact-zero support unless the statistical model explicitly
adds a floor. Return complexity, taxonomy, SCL pseudocode, stability argument,
validation matrix, priority, and stop conditions. No implementation.

