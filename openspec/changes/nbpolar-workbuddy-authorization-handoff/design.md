# Design: four-file handoff and main-thread continuation

Each executable queue item contains `TASK_PACKET.md`, `PROMPT.md`,
`AUTHORIZATION_PROMPT.md`, and `STATUS.yaml`. The authorization prompt names
the repository and packet, lists the exact status transition, enumerates every
true and false permission, and states the only allowed return conditions.

After a reviewed return, the main thread owns acceptance, durable status/docs,
and preparation of the next complete four-file packet. Preparing a packet is
not authorization. When authorization is next, the response includes the full
copyable text as well as links; a link alone is insufficient.
