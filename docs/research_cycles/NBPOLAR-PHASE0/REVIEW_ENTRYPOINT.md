# NBPOLAR-PHASE0 review entrypoint

## Repository and branch

- Repository: current worktree root (`.`)
- Branch: `codex/nbpolar-phase0`
- Cycle: `NBPOLAR-PHASE0`
- Lifecycle: `FREEZE_ACCEPT`; Phase 1 packet may be issued separately, while
  decoder, Model-F, real-data, and formal execution remain unauthorized

## Read in this order

1. `openspec/changes/formal-ir-nbpolar-mvp/proposal.md`
2. `openspec/changes/formal-ir-nbpolar-mvp/design.md`
3. `openspec/changes/formal-ir-nbpolar-mvp/tasks.md`
4. `docs/nbpolar/ASSET_MAP.md`
5. `docs/nbpolar/ARCHITECTURE.md`
6. `docs/nbpolar/ROADMAP.md`
7. `EXECUTION_PACKET.md` and `PHASE0_PROMPT.md`

## Review questions

- Is GF32/poly37/alpha2 and transform orientation unambiguous?
- Are source disclosure and arbitrary known values, including zero, distinct
  from channel coding?
- Is the `(N,q)` metric and provenance contract sufficient to prevent the D7
  prior-only/APP confusion?
- Is the tiny oracle independent of the implementation under review?
- Are Model-F, Release, raw data, result roots, SCL and rate scans excluded?

An affirmative review freezes a plan only. It grants no decoder or real-data
execution authorization.
