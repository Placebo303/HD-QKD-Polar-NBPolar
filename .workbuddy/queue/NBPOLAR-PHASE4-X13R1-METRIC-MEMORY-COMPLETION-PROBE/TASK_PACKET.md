# Phase 4-X13R1 Tier-X delta — metric-memory completion probe

## Mission

Complete the large-N evidence that X13 could not finish because its combined
400-second child budget was shorter than the observed 425.5-second workload.
This is a new probe, not a rerun or repair of X13. Keep X13 immutable.

## R1-01 — Inheritance and write boundary

Read only the two X13 probe files to verify their recorded identities and
inherit the independently reviewed 10/10 small-N parity and ownership evidence.
Do not modify or count X13's partial large-N values toward R1 completeness.

Write only:

- `workspace/probes/nbpolar_x13r1_metric_memory_completion/prereg.md`
- `workspace/probes/nbpolar_x13r1_metric_memory_completion/results.json`

Freeze exactly three top-level preregistration lines with the complete execution
body before any child launch. No production/test/OpenSpec/ledger/memory/index
edit; no artifact/evidence root/official seed/raw/held-out/real/EVAL/tag/FWHT/
APP/SCL/scientific gate. No attempt, threshold, winner, candidate or acceptance.

## R1-02 — Frozen semantics

Use the same deterministic injected P1/P2/p_b generation, probe seed
`2026091840`, GF(32) polynomial 37, alpha=2, chunk_rows=512 and the exact two
alternatives frozen in X13:

- `lifetime_only`: accepted builders/converter; release L1/L2 probability,
  metric and SCResult planes at last use; append scalar-only outcomes.
- `owned_log`: same releases/scalarization, plus owned float64 L2 gather,
  accepted validation, in-place `np.log` and accepted row normalization before
  direct `sc_decode`; never mutate caller-owned/view input.

No semantic or implementation change from X13 is allowed. Reconstruct and
compare the deterministic N=64 finite and X11-C3 controls once in the parent;
they must exactly match the inherited X13 parity record before child launch.

## R1-03 — Four isolated child cells

Launch exactly four fresh child processes in this order with
`ulimit -v 2097152` and the listed independent timeout:

1. lifetime_only, N=65536, 4 sequential blocks, 240 s;
2. lifetime_only, N=262144, 2 sequential blocks, 600 s;
3. owned_log, N=65536, 4 sequential blocks, 240 s;
4. owned_log, N=262144, 2 sequential blocks, 600 s.

Use deterministic domain separation by alternative/N/block while retaining the
same master probe seed. Each child reports every block's status, exact semantic
scalar outcome, wall, peak HWM, and stage/live-array ledger. The parent captures
stdout/stderr/exit and checkpoints the single results record after each block
message and child termination. Child MemoryError/timeout is descriptive and
does not authorize changes or rerun.

Each N=262144 child must reproduce X13's RNG stream position by consuming the
registered four N=65536 blocks' three generated arrays before generating its
two large blocks; record the stream-position check.

Completeness means 6/6 blocks for each alternative (12 total) with all expected
stage records. Do not merge X13's 5 partial blocks into these counts.

## R1-04 — Review, STOP and return

Independent reviewer-go, in the return message only, verifies X13 inheritance,
the parent parity reconstruction, deterministic input identity, four-child
split/budgets, 6/6 + 6/6 counts, scalar-only retention, live-array ledgers,
checkpoint completeness, resource records, two-file scope and forbidden access.
Its evidence is trusted by the main thread.

If a child resource-fails, finish recording that child then STOP without
launching later cells. A semantic/inheritance mismatch stops immediately.
Execution-code error may be rerun once only with unchanged freeze and full
recording; resource/semantic failures are never rerun. Parent timeout 1900 s,
2 GiB per child. No commit/push.

Return `X13R1 complete` or the blocker. Report two-file inventory, inheritance,
execution count, parent parity, all four cells, 6/6 counts, wall/RSS/ledger,
review and whether evidence supports exactly `lifetime_only`, `owned_log`, both,
or neither for a future P12-R1. This remains descriptive and creates no winner.
