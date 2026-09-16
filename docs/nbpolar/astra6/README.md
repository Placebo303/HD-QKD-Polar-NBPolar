# NB-Polar x GPT-6 Astra reasoning pack

This is a compact, upload-friendly reasoning pack. It asks Astra to work on
the hardest open scientific questions without execution authority.

## Start here

Upload `PROJECT_BRIEF.md` and one selected `Q*_TASK.md`, then paste the
matching `Q*_PROMPT.md`. For a cross-cutting review, upload
`PROJECT_BRIEF.md`, `EXAMPLES.md`, and at most two task files, then use
`MASTER_PROMPT.md`.

## Priority

| Priority | Question | Why it matters now |
|---|---|---|
| 1 | Q1 HOLD generalization and backoff | The TRAIN-model point replicated, but three real HOLD blocks were 0/3. The mechanism must be located without overreading three blocks. |
| 2 | Q2 two-layer inference | Hard L1 conditioning produced a large oracle gap. A soft/list interface may retain useful uncertainty without truth leakage or double counting. |
| 3 | Q3 finite-length construction and rate | Model-sampled N=32768 approached `f=1.3`, while HOLD did not recover. A principled finite-length construction/backoff story is missing. |
| 4 | Q4 scalable exact decoder | Exact q-ary SC reaches large N, but direct arithmetic is costly; the tested FWHT shortcut changed support/decisions. SCL remains unimplemented. |

Q1 should be answered before choosing a new claim-bearing experiment. Q2-Q4
may be reasoned about in parallel, but must preserve Q1's population and
evidence conclusions.

## Authority boundary

This pack does not authorize artifact reads, TRAIN/HOLD/real-data access,
decoder execution, new result roots, tuning, code edits, commits, or pushes.
Astra should return analysis, derivations, falsifiable hypotheses, and a
minimal next-experiment design only.

Every answer must separate observed facts, mathematical deductions,
hypotheses, missing information, the smallest discriminating next experiment,
and claims that remain forbidden even if that experiment succeeds.

