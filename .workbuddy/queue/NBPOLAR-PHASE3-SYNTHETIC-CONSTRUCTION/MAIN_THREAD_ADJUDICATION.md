# Main-thread adjudication: Phase 3 synthetic construction

Date: 2026-09-11  
Verdict: `BLOCKED(PHASE3_GATE_INVALID)`  
Disposition: retain all artifacts as diagnostic; no rerun; Phase 4 closed.

## Accepted implementation evidence

The reviewer-go test report of 45/45 is trusted. The synthetic generators,
analytic erasure recursion, genie/oracle agreement, construction data model,
and evaluation accounting are retained as an implementation candidate. This
does not accept the Phase 3 gate or its EVAL result.

## B1 — pre-EVAL review

Not ratified. The frozen packet required an independent reviewer-go and stated
that an unavailable reviewer must stop. The execution environment had no
subagent/reviewer-go tool; the operator performed a separate self-check and
used it to authorize EVAL. The self-check is useful audit evidence but is not
the required independent review. The EVAL is therefore procedure-invalid and
cannot satisfy P3-T1-08.

## B2 — exact invocation

Partially cured, still incomplete. The addendum names `evaluate_blocks` and all
scalar arguments, but supplies `disclosure_order` through a placeholder for a
full 256-coordinate permutation. The first 45 disclosed coordinates are
recorded and sufficient to understand the effective disclosure set, but the
literal function call requires a full permutation and is not exactly replayable
from the shown command alone.

## B3 — rank gate

Not ratified. P3-T1-05 froze Spearman correlation between the genie risk and
analytic erasure risk at >=0.90. It did not preregister filtering to coordinates
with observed `e>0`. The full-vector result is 0.7665 and therefore fails. The
resolvable-subset value 0.9959 and top-50 overlap 0.98 are retained as strong
diagnostics that finite TRAIN quantization and large zero ties dominate the
rank statistic; they cannot replace the frozen population after observation.
The consistent tie count is 187, not 190.

## EVAL diagnostic

Preserve the sole EVAL exactly as observed: seed 2026091203, q=32, N=256,
epsilon=0.05, K=45, 300 blocks, 299 exact, 300 initial-error blocks, one
impossible-disclosure at block 104, no rerun or replacement. This suggests
that K=45 has a small residual failure probability under the tested setup.
It does not prove that every 300-block sample must contain a failure or that
N/K is the unique cause.

## Gate ordering

The earliest substantive failure is P3-T1-05, observed before EVAL. The missing
independent review is an additional procedure failure, and P3-T1-08 also misses
its zero-impossible condition. For that reason the accepted terminal cannot be
described as a single proven N/K root cause.

## Next action

A Phase 3-R1 successor may redesign the construction-resolution gate and
propose a larger K grid, but it needs a new packet, real independent review,
and explicit authorization. It must not reuse or rerun EVAL seed 2026091203.
Relaxing the zero-impossible requirement after observing this result is not
accepted for the current run.
