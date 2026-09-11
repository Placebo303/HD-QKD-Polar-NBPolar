# Proposed heavy task packet: Phase 3-R1 construction recovery

## State

`READY_FOR_AUTONOMOUS_EXECUTION_SESSION`. The user authorizes implementation
and TRAIN/DEV under this packet. One fresh synthetic EVAL is authorized only
after a real independent reviewer-go returns PASS on the final frozen EVAL
contract. Phase 4, Model-F, real data, promotion, commit, and push remain closed.

## Mission

Recover Phase 3 with a scientifically coherent construction gate and a valid
one-shot execution lifecycle. The predecessor artifacts stay immutable:

- never rerun or reuse EVAL seed 2026091203;
- never relabel the predecessor as PASS;
- preserve 299/300 exact and block 104 as procedure-invalid diagnostic evidence;
- do not use that EVAL to select a new K, threshold, order, or statistic.

The successor must resolve three independent defects before any new EVAL:

1. finite TRAIN produces a large zero tie, so full-vector Spearman is a poor
   unqualified statistic at 512 samples;
2. impossible disclosed values are legitimate decode failures after an earlier
   SC prefix error, not automatically numeric/implementation faults;
3. the pre-EVAL review and exact invocation must be real and replayable.

## Autonomous work allowed after authorization

The operator may compare and select among:

- more TRAIN samples with the original genie `(e,h)` estimator;
- analytic BEC order as the exact erasure construction baseline;
- hybrid analytic order plus genie calibration diagnostics;
- preregistered top-K overlap/risk-mass metrics that remain meaningful under
  finite-sample ties;
- an expanded DEV-only K grid;
- a dedicated executable synthetic-EVAL script with frozen arguments.

It must document at least three options, choose one using TRAIN/DEV only, and
explain why the chosen statistic measures construction quality. It may simplify
the predecessor code but must preserve the accepted Phase 1/2 behavior and all
45 predecessor tests.

## Frozen semantic corrections

For R1, an `ImpossibleDisclosedValueError` caused by a wrong earlier
undisclosed prefix counts as one failed decode and one non-exact block. It is
reported separately but is included in the same total failure count. It is not
a standalone zero-tolerance implementation gate unless a tiny oracle proves
the disclosed value has positive conditional support under the same prefix.

Numeric NaN, invalid posterior, truth leakage, stream leakage, or resource
abort remain hard failures.

This correction applies only prospectively to R1. It does not change the
predecessor's frozen zero-impossible rule or retroactively accept its EVAL.

## Required pre-EVAL construction gates

The operator must propose and freeze exact thresholds before fresh evaluation.
At minimum:

- analytic BEC recursion/orientation remains exact;
- genie conditionals still match the exhaustive oracle;
- construction ordering is deterministic and a full 256-permutation is
  persisted literally;
- construction quality is judged by preregistered metrics robust to ties, with
  full-vector results still reported;
- TRAIN, DEV and fresh EVAL streams are distinct;
- the fresh EVAL seed must differ from all predecessor seeds and is chosen in
  the freeze document before use;
- K selection uses only the new TRAIN/DEV data and a frozen deterministic rule.

The main thread recommends using analytic BEC order as the erasure-channel
ground truth and retaining genie estimates as calibration evidence. This is a
recommendation, not a forced implementation if the operator proves a better
tie-aware gate.

## Candidate DEV space

The successor may propose a bounded grid centered on the predecessor, such as
`epsilon=0.05`, `K in {45,53,61,69}`, plus at most one harder epsilon sanity
point. Exact grid, sample counts, selection rule, and budgets must be frozen
before running DEV. Do not use the predecessor EVAL to select among candidates;
it may be mentioned only as motivation for opening R1.

## Exact execution requirement

Before EVAL, create a dedicated checked-in-scope script or module entry point
whose command contains no placeholder. Persist:

- full 256-coordinate order;
- q/N/epsilon/K/alpha/poly;
- fresh seed and exactly one invocation;
- output schema and stop rules;
- statement that target artifact is absent and EVAL has not run.

Do not reconstruct the command after execution.

## Independent review requirement

A real reviewer-go subagent must review the frozen code, tests, full order,
stream separation, DEV selection, command, thresholds, and target absence.
If the execution environment cannot invoke reviewer-go, stop
`BLOCKED(INDEPENDENT_REVIEW_UNAVAILABLE)`. A separate operator process or
self-check is not authorization.

Save the actual reviewer verdict before EVAL. Only PASS authorizes one fresh
EVAL. Needs-changes may be repaired and re-reviewed without touching EVAL.

## Minimum validation

- all predecessor Phase 1-3 tests pass;
- new tests cover tie-heavy risk vectors and prospective impossible-as-failure
  accounting;
- analytic order and chosen construction metric agree under frozen criteria;
- no Alice truth reaches evaluation beyond disclosed U positions/values;
- no TRAIN/DEV/EVAL stream alias or data reuse;
- Model-F, real data, protocol, SCL and output roots remain absent;
- focused suite and TRAIN/DEV remain within a predeclared local budget.

The fresh EVAL success threshold must be selected before EVAL and count every
attempt, including impossible-disclosure, in the denominator. Do not require
whole-block MAP equality; exact U and X recovery remains the success event.

## Allowed scope after authorization

- Phase 3 `synthetic.py`, `construction.py`, their exports and focused tests;
- one dedicated Phase 3-R1 synthetic evaluation entry point;
- this packet's plan/freeze/review/return artifacts;
- minimal proven Phase 2 correction only if an accepted oracle test fails.

Forbidden: Model-F/CAL/VAL/TTBin, real data, protocol/leakage, method adapter,
SCL, rate adaptation, production benchmark roots, Phase 4, commit, push, or
scientific promotion.

## Return

After authorization, return either:

- `IMPLEMENTATION_CANDIDATE_SYNTHETIC_R1_GATE_PASS` with full tests, TRAIN/DEV
  table, real reviewer-go pre-EVAL PASS, exact command, single fresh EVAL and
  complete accounting; or
- `BLOCKED(<single earliest gate>)` with all later stages unattempted.

No Phase 4 transition occurs automatically. Main-thread independent result
review remains required.
