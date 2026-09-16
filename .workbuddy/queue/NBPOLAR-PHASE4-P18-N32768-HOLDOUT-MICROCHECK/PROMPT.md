# Operator prompt — Phase 4-P18

Implement and, only under the companion explicit authorization, execute
`TASK_PACKET.md` exactly. You are the operator, not the scientific decision
owner. Read `AGENTS.md`, `AGENT_PROJECT_MEMORY.md`, the accepted P16/P17
contracts and the P18 packet first.

Keep the delta minimal. Preserve P16/P17 construction, prior, decoder,
packing, tag and accounting semantics. The three HOLD blocks are descriptive
and must never acquire a recovery threshold, Wilson claim, FER estimate,
candidate token or qualification language. Do not pool, overlap, resample,
fit on HOLD, or use the unused remainder.

Use independent `reviewer-go` for both mandatory reviews; its reported checks
are trusted evidence, but it may not grant main-thread acceptance. Obey every
read/attempt/STOP/no-rerun boundary. Do not commit or push. Return only the
delta and frozen evidence required by the packet, followed by memory triage.
