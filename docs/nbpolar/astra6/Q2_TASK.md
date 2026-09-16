# Q2 — preserve L1 uncertainty in the two-layer decoder

## Question

Design the smallest correct interface that retains L1 uncertainty when
decoding L2 while preventing Alice-truth leakage, posterior double counting,
and the false claim that an SC decision score is a calibrated APP.

## Required work

1. Derive target quantities for hard, mixture, list, joint, and
   extrinsic/cavity formulations.
2. State what current q-ary SC can and cannot supply.
3. Give a minimal algorithm, preferably q-ary SCL over L1 followed by
   conditional L2 evaluation, with explicit path-metric semantics.
4. Specify invariants: L=1 equivalence; oracle separation; normalization;
   known coordinates; no truth access; deterministic pruning/ties; accounting.
5. Analyze q=32 complexity for N=256, 1024, and 32768.
6. Give tiny exact-enumeration falsification examples.
7. Define one bounded paired synthetic experiment testing whether retained L1
   uncertainty closes the 233/384 versus 377/384 gap.

## Constraints and return

The final tag rejects but never selects a path. Do not reuse Bob evidence
twice or call a path list an APP without calibration. Preserve source
disclosure semantics. Return equations, pseudocode, invariants, complexity,
tiny oracles, paired experiment, failure modes, and a recommendation. No code
or execution.

