# OpenSpec archive note — accepted P20R/P20S deltas (2026-09-20)

## Status

P20R (order-position 1.5M) and P20S (mechanism probe 2M merged) are Tier-Y
ACCEPTED. Their delta specs REMAIN under the active umbrella change:

- `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20r/spec.md`
- `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20s/spec.md`

No file moves were performed in this round.

## Why no merge was performed

Surveyed 2026-09-20 before acting:

- `openspec/specs/` contains only two legacy specs
  (`final-ir-method-selection`, `formal-ir-methods`); no NB-Polar delta has
  ever been merged there.
- `openspec/changes/archive/` contains only whole-change dirs from the
  2026-07/08 formal-nonbinary-ldpc era (each with proposal/design/tasks/specs);
  no per-delta archive precedent exists.
- The umbrella change `formal-ir-nbpolar-phase4-p0/` is still active.

Merging only the P20R/P20S deltas into `openspec/specs/` would invent a new
convention, so per the closeout instruction no new convention was created.

## Future `/opsx-archive` merge steps (when the umbrella change is archived)

1. Archive the whole umbrella change dir into `openspec/changes/archive/`
   following the existing whole-change precedent
   (proposal.md + design.md + tasks.md + specs/).
2. Merge accepted delta specs into `openspec/specs/` under the same
   relative paths, i.e. `openspec/specs/nbpolar-phase4-p20r/spec.md` and
   `openspec/specs/nbpolar-phase4-p20s/spec.md` (copy content verbatim from
   the umbrella delta dirs at archive time).
3. Resolve conflicts against already-merged NB-Polar specs at that time, if any.

## Explicitly untouched

- P20Q (`nbpolar-phase4-p20q`) stays as-is under the umbrella change.
- `nbpolar-reduced-n-persistence` stays as-is (unexecuted scoping; no
  execution authorized).
- `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` was not modified;
  no change dir was deleted or moved.
