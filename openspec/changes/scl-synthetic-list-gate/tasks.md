# Tasks: SCL Synthetic List Gate (all NOT AUTHORIZED — scoping skeleton only)

Every box is unchecked. Every task carries `[GATE -- NOT AUTHORIZED]`.
No task may execute, freeze, or authorize anything under this scoping.

- [ ] S1 — Proposal review (this change). Confirm proposal/design/tasks encode the five
  recorded rules; confirm no L values, pruning thresholds, or working-point numbers are
  frozen; confirm `sc.py`-untouched + synthetic-only + no-claim scope. [GATE -- NOT AUTHORIZED]
- [ ] S2 — Freeze review. Independent review of the future frozen packet: working-point
  triple (N, K1/K2, channel strength) with the (a)-rule variance justification; list
  interface freeze (`scl_decode` shape, `list_width_L` slot, `prune_rule` placeholder with
  NO values); seed/tag grep proof; 3-line prereg text; stop-rule tokens. [GATE -- NOT AUTHORIZED]
- [ ] S3 — Implementation authorization. Explicit user authorization to create the NEW list
  module alongside frozen `sc.py` + the new probe body (new files only, zero edits to
  `formal_ir/nbpolar/` existing modules, zero protected opens). [GATE -- NOT AUTHORIZED]
- [ ] S4 — Focused tests. T0/T1 green (tie-break, diagonal-smoke, disclosure-smoke,
  order-identity, gate asserts) + full NB-Polar suite green; T2 at milestones only. Path-refusal
  asserts (no protected imports) verified. [GATE -- NOT AUTHORIZED]
- [ ] S5 — Single synthetic execution. One frozen-command run under single-thread pins;
  probe-root-only writes; `results.json` scalar-only (< 2 MB) with per-seed values +
  mean/sample-std/range; `decoder_calls`/`rng_calls`/`tag_calls: 0` recorded; zero protected
  opens; execution-error-only single recorded rerun. [GATE -- NOT AUTHORIZED]
- [ ] S6 — Focused numerical review. Independent reviewer-go Tier-X review (commands,
  completeness, arithmetic, truth isolation, write scope, H-localization carry-over,
  control-arm readings with X17 qualifications). No Pre-EXECUTE/Pre-RESULT (Tier-X rule).
  [GATE -- NOT AUTHORIZED]
- [ ] S7 — Acceptance + L-ladder derivation. Main-thread acceptance of descriptive results;
  derive the L-ladder FROM the working-point survival-vs-L curve per design (b) (survey
  L in {4,8,32} non-binding); record whether the X14-style survival gate (c) is met at the
  re-justified L values; decide whether any unlock-gate attempt is warranted. No
  FER/reliability/efficiency claims; no real-data follow-on; no production merge; SCL lock
  status explicitly re-stated. [GATE -- NOT AUTHORIZED]

Notes: S1 is this scoping. S2..S7 are placeholders for the separately-gated future track.
Small-task fast path is NOT claimed: a list decoder is a new module and needs the full gate
sequence above.
