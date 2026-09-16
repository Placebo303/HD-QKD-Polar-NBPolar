# Implementation note — nbpolar-probe-tier-and-decision-gate-slimming

Workflow-change half (W-01/W-02/W-03) of packet
`NBPOLAR-X01-PROBE-TIER-BOOTSTRAP`. Documentation-only; no task box is checked
here.

## Where it landed

| Task | File | Anchor |
|---|---|---|
| W-01 | `AGENTS.md` | §10.4 "Two-tier execution (Tier X probes / Tier Y decision gates)" at line 365 |
| W-01 | `AGENTS.md` | §10.1 item 4 cross-reference to §10.4 at line 296 |
| W-02 | `docs/nbpolar/PROBE_TIER.md` | new file: "Two tiers" L6, "Tier-X template" L15, "Tier-Y threshold evidence" L32, "Delta-successor fast path" L38 |
| W-02 | `docs/nbpolar/WORKBUDDY_LIFECYCLE.md` | "Tier X / Tier Y" section at line 63 |
| W-02 | `docs/nbpolar/DOCUMENT_INDEX.md` | `PROBE_TIER.md` row at line 16 |
| W-03 | `workspace/probes/nbpolar_x01_20260913/prereg.md` | new file (three-line preregistration) |

## Scope

- Only W-01/W-02/W-03 were performed. W-04..W-07 (the probe run and review) were
  not run in this change.
- No code, results, old evidence roots, decision-log, index beyond the
  `PROBE_TIER.md` row, or project memory were touched.
- No task box in `tasks.md` was checked; no commit or push was made.

## Consistent with

`proposal.md`, `design.md` and the `nbpolar-research-lifecycle` delta spec
(exploratory probes, threshold calibration, delta successor).
