# Operator prompt — Phase 6-R2

Read AGENTS.md, AGENT_PROJECT_MEMORY.md, the R2 OpenSpec, TASK_PACKET.md and
STATUS.yaml. Implement exactly R2-A01..A10. This is decoder-free analysis:
do not call SC, read artifacts, sample blocks, or consume an attempt/seed.

Freeze inputs/formulas before producing the table. Use independent
implementations for recurrence/K selection, reproduce K43, run all registered
sensitivity axes, and have reviewer-go independently recompute the result.
Return either `TWO_LAYER_RATE_FEASIBILITY_CANDIDATE` with changed files and
exact test/result summary, or `BLOCKED(<earliest gate>)`. Do not self-accept,
commit or push.
