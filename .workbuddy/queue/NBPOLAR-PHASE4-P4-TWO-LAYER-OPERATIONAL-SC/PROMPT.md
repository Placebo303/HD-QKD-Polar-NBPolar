# Operator prompt — Phase 4-P4

Read AGENTS.md, project memory, the Phase4-P0 contract, this OpenSpec,
TASK_PACKET.md and STATUS.yaml. Implement P4-A01..A12 exactly. You are an
operator and may not redefine tables, thresholds, lifecycle or claims.

First implement/test the two-stage causal path with injected tables and tiny
independent oracles. Freeze the bounded N256 paired interface gate before any
claim-bearing SC call and obtain independent Pre-EXECUTE PASS. Consume the
single attempt at the first gate SC call; never rerun or tune. Obtain independent
Pre-RESULT recomputation before writing the return.

Return only `TWO_LAYER_OPERATIONAL_SC_CANDIDATE` or
`BLOCKED(<single earliest gate>)`, with attempt/seed usage, changed files,
tests, compact evidence list and unrun stages. Do not self-accept, commit/push.
