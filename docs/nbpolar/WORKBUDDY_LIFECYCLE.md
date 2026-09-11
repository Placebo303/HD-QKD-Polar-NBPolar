# NB-Polar WorkBuddy lifecycle

## Ownership

The current main thread owns architecture, frozen requirements, authorization
boundaries, adjudication, scientific conclusions, durable status, and the next
task. An execution session owns implementation and bounded evidence collection.
A reviewer remains read-only and cannot authorize or accept its own work.

The main thread does not stop after saying that a future main thread should act.
After every return it either resolves the blocker, records a reviewed candidate,
accepts within evidence, or reports the one decision that truly requires the
user. It then prepares the next complete packet when a next stage exists.

## Required packet files

Every execution-ready queue directory contains:

1. `TASK_PACKET.md`: mission, source files, allowed/forbidden scope, stable
   acceptance IDs, commands, tests, budgets, stop rules, review gates and return
   conditions.
2. `PROMPT.md`: short operator entrypoint pointing to the packet.
3. `AUTHORIZATION_PROMPT.md`: exact user message that grants only this packet.
4. `STATUS.yaml`: machine-readable lifecycle and permission flags.

Planning may create all four files while every execution flag remains false.
This is preparation, not authorization.

## Normal sequence

```text
main thread freezes packet
  -> user copies AUTHORIZATION_PROMPT to execution session
  -> operator changes only the listed STATUS flags
  -> implementation / bounded evidence
  -> independent review
  -> operator returns COMPLETE or BLOCKED(single earliest gate)
  -> main thread verifies and adjudicates
  -> main thread updates acceptance, decision log and project memory
  -> main thread prepares the next four-file packet
```

At every user-authorization gate, the main-thread response includes the full
copyable authorization text. File links are provided for convenience but never
replace the text.

## Return and blocker handling

An operator returns only a reviewed candidate or one exact blocker. A genuine
frozen-requirement conflict is resolved by the main thread through the smallest
OpenSpec correction and regression, rather than by import spelling, weakened
tests, or repeated user handoffs. Historical BLOCKED reports remain immutable;
successor result files and `STATUS.yaml` carry the resolved state.

## Acceptance and next-stage discipline

Independent reviewer PASS makes a candidate eligible; the main thread records
the final accepted scope. Acceptance never opens the next packet implicitly.
The next packet remains all-false until its own authorization prompt is sent by
the user. Data, decoder, EVAL and scientific-promotion permissions stay
separate so a code task cannot silently become a result-producing run.

## Documentation updates

Each accepted milestone updates `CURRENT_TASK.md`, `docs/CURRENT_MAINLINE.md`,
`docs/decision-log.md`, `AGENT_PROJECT_MEMORY.md`, the NB-Polar document index,
and the relevant queue status. Reusable failures update
`docs/troubleshooting.md`. Candidate-only evidence is labelled as such.
