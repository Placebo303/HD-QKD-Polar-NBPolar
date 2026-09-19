# AUTHORIZATION_PROMPT — NBPOLAR-X10-H2-SCALAR-ADJUDICATION (Tier-X probe)

Copy-paste authorization for the operator. Basis, scope, and limits frozen below.

## Authorization text

"Authorized: operator executes ONE frozen Tier-X probe
`NBPOLAR-X10-H2-SCALAR-ADJUDICATION` on branch `codex/nbpolar-phase0` in
`/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, per user decision 2026-09-19 to
adjudicate H2 (L2 order/metric non-generalization) from already-persisted
9-scalar instrumentation + coordinates.

Scope: one read-only worktree-artifact pass over the frozen inputs named in
`TASK_PACKET.md` §2 (P20N 16-record + P20O 20-record JSONL/summaries; optional
P20M 9-record baseline; orders/priors/runner code inventory-only, NPZ stat-only
never opened). ZERO protected-content opens (no V25 counts NPZ / pairs parquet /
1M/1.5M/2M content, not even stat). No decoder calls, no RNG calls, no tag
calls. Writes ONLY under `.workbuddy/queue/NBPOLAR-X10-H2-SCALAR-ADJUDICATION/`
(packet docs) and `workspace/probes/nbpolar_x10_h2_scalar_adjudication/`
(`prereg.md`, `body.py`, `results.json` — the last the only file `body.py`
writes). No claims beyond descriptive support labels. No commit. No push.

Execute exactly once with the frozen command in `TASK_PACKET.md` §4 (timeout
120s, single-thread env). One rerun permitted solely on execution error and
recorded. STOP with a specific status on missing/unreadable required file,
malformed JSONL/summary, required record-count mismatch, or nonfinite result —
no input repair."

## Gates confirmed at freeze
- Probe root absent (verified 2026-09-19, `PROBE_ROOT_ABSENT`).
- Packet root created fresh this probe; no overwrite of existing probe state.
- Concurrent milestone commit by user noted: new probe files land outside that
  commit if staged earlier — no interference expected, no action required.
- `prereg.md` (with byte-identical body block) is written BEFORE any frozen
  input content read; `body.py` runtime-asserts the identity.
