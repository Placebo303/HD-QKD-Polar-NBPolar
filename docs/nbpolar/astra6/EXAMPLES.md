# Minimal examples for Astra

These are conceptual examples, not production code or execution inputs.

## 1. Hard-layer error propagation

Let `H` be the true high GF(32) layer, `L` the low layer, and `B` Bob's side
information:

```text
P(H,L|B) = P(H|B) P(L|H,B).
```

Current operational L2 uses `P(L|H=h_hat,B)`. If `h_hat != H`, a sharp L2
prior can exclude the true low symbol even when the joint posterior retains
substantial mass on compatible `(H,L)` pairs.

Observed synthetic table:

```text
                         oracle L2 exact   oracle L2 failed
operational L2 exact            233                  0
operational L2 failed           144                  7
```

A useful design compares:

```text
hard:       P(L | H=h_hat, B)
mixture:    sum_h w(h) P(L | H=h, B)
list:       retain (h,path_metric), decode L per h
joint:      decode the 1024-ary pair or equivalent factor graph
extrinsic:  pass only information not already in the L2 factor
```

It must define what `w(h)` means and not call an SC path score a calibrated
APP without justification.

## 2. TRAIN-model success versus HOLD failure

```text
same frozen N,K1,K2,construction,prior

TRAIN-model: 62/64 exact, then 123/128 on fresh model samples
HOLD:        0/3 exact; all verify_failed; no decoder/resource failures
             sample-CE-normalized disclosure ratio = 1.23082048
```

The correct inference is neither “FER is bad” nor “the failures are noise.”
The analysis should list hypotheses that predict different five-arm patterns
and safe descriptive statistics that do not tune on these three blocks.

## 3. Exact versus fast arithmetic

The accepted minus node reduces 32 terms for each of 32 outputs. Row chunking
changed allocation only and preserved bitwise results. A tested FWHT shortcut
created small finite perturbations and exact-support mismatches. A near-tie
flip early in SC changes the prefix, later plus recursions, and sometimes
whether a disclosed value appears impossible.

An optimization must claim exactly one of:

1. bitwise behavioral equivalence;
2. bounded posterior error with a certified decision margin;
3. a new decoder requiring new FER/leakage evidence.

## 4. Disclosure accounting

For N=32768, K1=319, K2=6492:

```text
key-dependent disclosure = 5*(K1+K2) + 64 = 34119 bits
```

The tag is counted once. Public control is separate. Adaptive/list proposals
must count each newly disclosed GF(32) coordinate once, every tag, and all
public feedback without merging public control into key-dependent leakage.

