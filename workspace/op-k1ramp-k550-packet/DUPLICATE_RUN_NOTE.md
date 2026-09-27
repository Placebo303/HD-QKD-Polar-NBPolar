# Duplicate-run note — 2026-09-27 (provenance incident, resolved as cross-check)

## What happened

The overnight plan assumed **one** execution of the operational k1 dose ramp. In the 02:50
automation tick and this working session, the same frozen configuration was prepared and
executed **twice**, in two independent probe roots:

| | root | packet | first byte of `results.json` | wall |
|---|---|---|---|---|
| A (this session) | `workspace/probes/op-k1ramp-k550-base/` | `workspace/op-k1ramp-k550-packet/` | 02:56:53 | 118.757 s |
| B (automation tick 1) | `workspace/probes/op-k1-ramp-k550/` | `workspace/op-k1-ramp-k550-packet/` | 03:03:06 | 118.96 s |

Root cause: the automation's first tick started at 02:50 reading
`workspace/overnight_state_20260927.md` **before** this session had written a heartbeat, so
the concurrency guard (heartbeat < 6 min ⇒ skip) could not exclude the parallel work. No
protected data was involved, no Tier-Y ran, and neither run was tuned after seeing the other.

## Why this is not contamination

Both roots use the identical frozen object: same grid `k1 ∈ {10,80,160,320,450}`, same
`k2=550`, same `d2=worst_k(H2,550)` (same `design_seed=2026092600`, `DESIGN_MC=128`), same
run seeds `2026092701..2026092702`, same channel, same prior, same toeplitz master, same
single arm, same `reruns=0`. Neither relies on the other's output.

## Outcome: treated as an independent one-shot cross-run

Verified identical derived quantities:

- `H` = 0.931830007484, `H_times_N` = 954.193927664 (both)
- design means `H1_mean` = 0.127262129, `H2_mean` = 1.269108966 (both)
- operational totals: `{exact 126, undetected 0, verify_failed 34, decode_failed 0, resource_abort 0}` (both)
- oracle totals: `{exact 160}` (both)
- `cells` = 10/10, `reruns` = 0 (both)

Therefore A and B are mutually corroborating executions of the same one-shot configuration,
not two conflicting results.

## Consequences / standing rule

1. **A is treated as the authoritative record** for the coarse ramp (it was written first and
   carries the freeze review + focused review + transcript in its packet). B is retained as an
   independent reproduction and is cited here, never as a separate scientific result.
2. No claim sentence may cite A and B as "two replicates" in a statistical sense (Tier-X is
   non-claim; no Wilson interval, no significance wording). The correct wording is
   "independently re-run once; totals match".
3. Future overnight ticks must treat the heartbeat as **mandatory before starting work**, and
   any session opening files under `workspace/probes/` must check
   `workspace/overnight_state_20260927.md` **first**.
