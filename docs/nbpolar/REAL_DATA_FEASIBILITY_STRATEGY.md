# NB-Polar real-data correction feasibility strategy

## Project objective

This independent checkout develops NB-Polar itself. Its immediate objective is
not a cross-family winner, a repeated security proof, or `f <= 1.3` at any
cost. It is:

> Establish an operational, non-oracle and reproducible NB-Polar path that
> reconstructs complete real-data blocks under a preregistered disclosure
> budget that still has practical reconciliation meaning.

The sibling Comparison project owns NB-LDPC history and cross-method route
decisions. Security is an external contract here: preserve disclosure,
verification and data interfaces, but do not reopen the security proof.

## Three stages

1. **Real-data correction feasibility.** Demonstrate complete operational
   reconstruction under a nontrivial preregistered disclosure cap. The cap may
   exceed planning `f=1.3`, but it must not approach sending the raw input.
2. **Reproducible reliability.** Confirm the frozen candidate on new real
   blocks and independent sessions. Development blocks never become the
   confirmation sample.
3. **Efficiency optimization.** Only after reproducible recovery, reduce
   disclosure, wall time and memory and then revisit `f<=1.3`.

Planning `f`, sample-CE-normalized disclosure and qualification efficiency
remain distinct throughout.

## P19 disposition and mechanism result

P19 is accepted descriptively as
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`. Its finalized
worktree evidence, not the concurrent commit's 11/15 checkpoint, is
authoritative.

All 15 records on the same three HOLD blocks were `verify_failed`. The
registered outcomes were:

| Arm | K1 | K2 | Complete recovery | L1 correctness by block |
|---|---:|---:|---:|---|
| base | 319 | 6492 | 0/3 | true, false, false |
| l1_plus | 447 | 6492 | 0/3 | true, true, true |
| l2_plus | 319 | 7004 | 0/3 | true, false, false |
| both_plus | 447 | 7004 | 0/3 | true, true, true |
| true_l1_control | oracle | 6492 | 0/3 | true by diagnostic construction |

This establishes only a same-block mechanism observation:

- the registered +128 L1 disclosure repaired the two L1 errors;
- correct L1 did not produce complete recovery;
- the registered +512 L2 disclosure did not recover a block;
- true-L1-conditioned L2 also did not recover a block.

Therefore hard-L1 propagation is not a sufficient explanation for these
three failures, and L1 SCL is not the next default implementation. This does
not estimate FER, reject NB-Polar, or prove every moderate disclosure fails.

## Required measurement semantics

Every future mechanism or feasibility record separates:

- `l1_exact`;
- `hard_l2_exact`;
- `oracle_l2_exact`;
- `pair_exact`;
- first error coordinate and layer;
- raw TRAIN zero-count hits;
- fixed-floor (`1e-15`) hits and their log loss;
- true-H-conditioned L2 NLL;
- candidate-H-conditioned L2 NLL;
- `exact`, `verify_failed`, `undetected`, `decode_failed`, `nonfinite` and
  `resource_abort`.

The old 233/384 operational count is complete-pair exact. The 377/384 oracle
count uses true H in the final label. Their 144-cell difference is not, by
itself, the strict count of hard-L1-induced L2 errors.

## Immediate engineering prerequisite

Before another real-data execution, resource exceptions must be classified
correctly. `MemoryError` raised inside an L1 or L2 SC call must escape the
decode-failure catch and reach the frozen resource-stop path. The same audit
applies to all shared NB-Polar helpers with broad `except Exception` around SC.
Two injected tests per applicable helper cover L1 and L2 failure sites and
verify disclosure/call accounting at the stop.

This is implementation/accounting repair only. It reads no protected data,
reruns no historical gate and changes no scientific result.

## Next scientific question

After the prerequisite is independently accepted:

> With true L1 fixed for diagnosis, why does the current L2 fail on real data,
> and does one preregistered, practically meaningful L2 disclosure and
> construction candidate recover complete low layers on independent real
> development data without changing representation, kernel, prior and decoder
> simultaneously?

Only one factor changes at a time:

1. fixed order, preregistered L2 disclosure backoff;
2. fixed disclosure, one preregistered alternative L2 construction;
3. fixed prior/construction/disclosure, bounded search diagnostic to determine
   whether SC misses a present candidate.

The three P18/P19 HOLD blocks are closed diagnostic data. They must not select
K, floor, order, decoder or a successful point. A candidate is developed on a
separate declared population and confirmed on new real blocks/sessions.

## SCL entry gate

L1 SCL starts only if all of the following are shown:

- true-L1-conditioned L2 is recoverable at the frozen candidate;
- hard L1 is a material failure source;
- a small preregistered list contains true L1 often enough to matter;
- joint scoring uses one coherent probability model without evidence reuse;
- list width 1 is exactly the accepted SC behavior.

Otherwise effort remains on L2 model, construction, disclosure or search.

## Stop rules

- Do not tune on the three P18/P19 blocks.
- Do not add a third factor after an inconclusive two-factor experiment.
- Do not claim feasibility by disclosing all or nearly all raw information.
- Do not call an oracle control an operational correction result.
- Do not infer population reliability until an independent-session gate.
- If a preregistered meaningful disclosure cap cannot recover independent real
  development blocks, record the bounded negative and revisit the L2 model or
  representation before increasing N or list width.

